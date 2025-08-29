"""Reliable serial device interface with safe open/close and background reading."""

from __future__ import annotations

import glob
import threading
import time
from dataclasses import dataclass

import serial  # pyserial
from loguru import logger

from monocular_path_prediction.config.definitions import (
    SERIAL_DEVICE_PREFIX,
    SerialConfig,
)
from monocular_path_prediction.sensors.device.device_info import DeviceInfo

# How long to wait in total when trying to open initially
INITIAL_CONNECT_TIMEOUT_S = 3.0
# Backoff when open fails or device disconnects
RETRY_BACKOFF_S = 0.25
# Number of open retries before giving up during initial connect
OPEN_RETRIES = int(INITIAL_CONNECT_TIMEOUT_S / RETRY_BACKOFF_S)


def find_serial_devices() -> list[DeviceInfo]:
    """Find all serial devices with a given prefix."""
    devices: list[DeviceInfo] = []
    for idx, path in enumerate(sorted(glob.glob(f"{SERIAL_DEVICE_PREFIX}*"))):
        devices.append(DeviceInfo(name=path, index=idx))
    return devices


@dataclass
class _State:
    """Internal mutable state kept together for clarity."""

    running: bool = False
    latest_line: str | None = None
    thread: threading.Thread | None = None


class SerialDevice:
    """Manage a serial connection with resilient background reading and reconnection.

    Features:
      * Safe open/close with retries and (when available) POSIX exclusive open
      * Reader thread created per-open (no reuse of a joined Thread)
      * Auto-reconnect on transient SerialException / device disappear
      * Thread-safe 'latest line' handoff
      * Optional auto-discovery of port if config.port is empty
    """

    def __init__(self, config: SerialConfig | None = None):
        if config is None:
            config = SerialConfig()
        self.config = config

        self._serial: serial.Serial | None = None
        self._lock = threading.Lock()
        self._state = _State()
        self.is_connected = False

        # Initial connection attempt (bounded)
        if not self._initial_connect():
            msg = (
                f"Timeout: serial port '{self.config.port or SERIAL_DEVICE_PREFIX}*' "
                f"did not connect within {INITIAL_CONNECT_TIMEOUT_S:.2f}s."
            )
            logger.error(msg)
            raise SystemExit(msg)

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def open(self) -> bool:
        """Open the serial connection and start background reading."""
        # If already open and healthy, do nothing
        if self._serial and getattr(self._serial, "is_open", False):
            logger.debug(f"Serial already open: '{self._serial.port}'")
            self.is_connected = True
            return True

        # Build serial object and try to open with retries
        ser = serial.Serial()
        ser.port = self.config.port
        ser.baudrate = self.config.baud_rate
        ser.timeout = self.config.timeout
        ser.write_timeout = self.config.timeout

        # Prefer POSIX exclusive open if supported (avoids 'already open' races)
        if hasattr(ser, "exclusive"):
            try:
                ser.exclusive = True  # type: ignore[attr-defined]
            except Exception as err:
                logger.error(err)
                pass

        for attempt in range(OPEN_RETRIES):
            try:
                ser.open()
                # Clear any stale bytes
                try:
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                except Exception as err:
                    logger.error(err)
                    pass
                self._serial = ser
                self.is_connected = True
                logger.success(
                    f"Opened serial port: {self.config.port} @ {self.config.baud_rate}"
                )
                # Start background reader
                self._start_reader()
                return True
            except (serial.SerialException, OSError) as err:
                logger.warning(f"[open attempt {attempt + 1}/{OPEN_RETRIES}] {err}")
                time.sleep(RETRY_BACKOFF_S)

        self.is_connected = False
        return False

    def close(self) -> None:
        """Stop the background thread and close the serial connection."""
        self._stop_reader()
        if self._serial and getattr(self._serial, "is_open", False):
            try:
                self._serial.close()
                logger.success(f"Closed serial port: {self._serial.port}")
            except Exception as err:
                logger.warning(f"Error while closing serial: {err}")
        self._serial = None
        self.is_connected = False

    def read_line(self) -> str | None:
        """Read one line synchronously (blocking up to timeout)."""
        ser = self._serial
        if not (ser and ser.is_open):
            return None
        try:
            raw = ser.readline()
            if not raw:
                return None
            line = raw.decode(self.config.encoder, errors="replace").strip()
            with self._lock:
                self._state.latest_line = line
            return line
        except (serial.SerialException, OSError, UnicodeDecodeError) as err:
            logger.warning(f"Serial read error (sync): {err}")
            self._handle_disconnect()
            return None

    def latest_line(self) -> str | None:
        """Return the most recent line the background thread has seen (non-blocking)."""
        with self._lock:
            return self._state.latest_line

    # Context manager sugar
    def __enter__(self) -> SerialDevice:
        """Context manager entry."""
        if not self.open():
            raise RuntimeError("Failed to open serial device in context manager.")
        return self

    def stop(self) -> None:
        """Stop the parser thread and close serial."""
        self._state.running = False
        if self._state.thread and self._state.thread.is_alive():
            self._state.thread.join(timeout=2.0)
        self.close()

    # Context manager override (optional sugar)
    def __exit__(self, exc_type, exc, tb) -> None:
        """Close the parser thread."""
        self.stop()

    # --------------------------------------------------------------------- #
    # Internals
    # --------------------------------------------------------------------- #
    def _initial_connect(self) -> bool:
        """Try to connect once during __init__, bounded by OPEN_RETRIES."""
        if self.open():
            return True
        return False

    def _start_reader(self) -> None:
        """Start the background reader thread (one per-open)."""
        # Stop any previous reader just in case
        self._stop_reader()

        self._state.running = True

        def _target() -> None:
            logger.info("Serial reader thread started.")
            while self._state.running:
                ser = self._serial
                if not (ser and ser.is_open):
                    # Try to reconnect
                    if self._try_reconnect():
                        continue
                    time.sleep(RETRY_BACKOFF_S)
                    continue

                try:
                    # Prefer non-blocking check when available
                    if getattr(ser, "in_waiting", 0) > 0:
                        raw = ser.readline()
                        if raw:
                            line = raw.decode(
                                self.config.encoder, errors="replace"
                            ).strip()
                            with self._lock:
                                self._state.latest_line = line
                    else:  # fallback to readline timeout
                        # Small sleep to avoid busy wait when no data pending
                        time.sleep(self.config.loop_delay)
                except (serial.SerialException, OSError, UnicodeDecodeError) as err:
                    logger.warning(f"Serial read error (async): {err}")
                    self._handle_disconnect()
                    time.sleep(RETRY_BACKOFF_S)

            logger.info("Serial reader thread exiting.")

        t = threading.Thread(target=_target, name="SerialReader", daemon=True)
        self._state.thread = t
        t.start()

    def _stop_reader(self) -> None:
        """Stop the background reader thread if running."""
        if self._state.thread and self._state.thread.is_alive():
            self._state.running = False
            self._state.thread.join(timeout=2.0)
        self._state.thread = None
        self._state.running = False

    def _handle_disconnect(self) -> None:
        """Mark connection down and close handle; reader will try to reconnect."""
        self.is_connected = False
        if self._serial and getattr(self._serial, "is_open", False):
            try:
                self._serial.close()
            except Exception as err:
                logger.error(err)
                pass

    def _try_reconnect(self) -> bool:
        """Attempt a single reconnect step; return True if successful."""
        try:
            if self.open():
                logger.success("Serial reconnected.")
                return True
        except Exception as err:
            logger.debug(f"Reconnect attempt failed: {err}")
        return False
