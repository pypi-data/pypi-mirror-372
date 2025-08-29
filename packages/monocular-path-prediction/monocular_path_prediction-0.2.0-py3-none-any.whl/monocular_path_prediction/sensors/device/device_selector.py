"""Camera tools for the monocular path prediction pipeline."""

from __future__ import annotations

import curses
import sys
from typing import Callable

from loguru import logger

from monocular_path_prediction.config.definitions import ESCAPE_KEY
from monocular_path_prediction.sensors.device.device_info import DeviceInfo


class Selector:  # pragma: no cover
    """Interactive serial port picker with a curses TUI."""

    def __init__(self) -> None:
        """Initialize the camera picker."""

    # ---------- TUI ----------

    @staticmethod
    def _draw_menu(terminal_screen, title: str, items: list[str], cursor: int) -> None:
        """Draw the selection menu.

        :param terminal_screen: Curses screen/window object.
        :param str title: Header/title line.
        :param list[str] items: Items to list.
        :param int cursor: Current cursor position.
        """
        terminal_screen.clear()
        height, width = terminal_screen.getmaxyx()
        terminal_screen.addnstr(0, 0, title, width - 1, curses.A_BOLD)
        terminal_screen.addnstr(
            1, 0, "↑/↓ or j/k to move • Enter to select • q to quit", width - 1
        )

        top = 0
        visible_rows = height - 3
        if cursor >= visible_rows:
            top = cursor - visible_rows + 1

        for i, text in enumerate(items[top : top + visible_rows]):
            y = i + 3
            attr = curses.A_REVERSE if (top + i) == cursor else curses.A_NORMAL
            terminal_screen.addnstr(y, 0, text, width - 1, attr)

        terminal_screen.refresh()

    @classmethod
    def _pick(cls, terminal_screen, entries: list[DeviceInfo]) -> DeviceInfo | None:
        """Run the curses loop to pick an entry.

        :param terminal_screen: Curses screen/window object.
        :param list[str] entries: Available imu entries.
        :return: Selected str or None if canceled.
        :rtype: Str | None
        """
        curses.curs_set(0)
        terminal_screen.nodelay(False)
        terminal_screen.keypad(True)

        labels = [f"[{entry.index}] {entry.name}" for entry in entries]
        cursor = 0 if labels else -1

        while True:
            if not labels:
                msg = "No serial ports found."
                logger.warning(msg)

                cls._draw_menu(terminal_screen, "No devices found.", [], -1)
                ch = terminal_screen.getch()
                if ch in (ord("q"), ESCAPE_KEY):  # q or ESC
                    return None
                continue

            cls._draw_menu(terminal_screen, "Select a device:", labels, cursor)
            ch = terminal_screen.getch()

            if ch in (curses.KEY_UP, ord("k")):
                cursor = max(0, cursor - 1)
            elif ch in (curses.KEY_DOWN, ord("j")):
                cursor = min(len(labels) - 1, cursor + 1)
            elif ch in (curses.KEY_ENTER, 10, 13):
                return entries[cursor]
            elif ch in (ord("q"), ESCAPE_KEY):  # q or ESC
                return None

    # ---------- Public API ----------

    def select_interactive(self, device_finder: Callable) -> DeviceInfo:
        """Open the curses TUI to select a camera.

        :return: Selected CameraInfo, or None if the user canceled.
        :rtype: CameraInfo | None
        """
        entries = device_finder()
        if len(entries) == 1:
            logger.info("Only one device found.")
            return entries[0]
        device_info = curses.wrapper(self._pick, entries)
        if device_info is None:
            logger.error("No device selected. Exiting.")
            sys.exit(1)
        logger.info(f"Selected device: {device_info})")
        return device_info
