"""Send messages to Arduino over serial."""

import argparse
import struct
import time

import serial
from loguru import logger

# Change this to match your Arduino's serial port
BAUD_RATE = 9600  # Match this with your Arduino sketch

FREQUENCY_HZ = 5
PERIOD = 1.0 / FREQUENCY_HZ


class Arduino:
    """Class for sending messages to Arduino over serial."""

    def __init__(self, serial_port: str, baud_rate: int = 9600) -> None:
        """Initialize the Arduino class."""
        self.serial_port = serial.Serial(serial_port, baud_rate, timeout=1)
        self.baud_rate = baud_rate

        logger.info(f"Opened serial port: {serial_port} at {baud_rate} baud.")

    def send(self, value: float) -> None:
        """Send data to serial at a given frequency."""
        try:
            # Example data: comma-separated string
            data = struct.pack("<f", value)  # Little-endian 32-bit float
            self.serial_port.write(data)
            logger.info(f"Sent: '{value}'")

        except Exception as err:
            logger.error(f"Sending to serial port failed: {err}")
            self.serial_port.close()

    def send_loop(self, value: float, period: float = 1.0) -> None:
        """Send data to serial at a given frequency in a loop."""
        while True:
            try:
                self.send(value)
                time.sleep(period)
            except KeyboardInterrupt:
                logger.info("Stopping...")
                self.serial_port.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send messages to Arduino.")
    parser.add_argument("--port", type=str, help="Serial port.")
    parser.add_argument("--baud_rate", type=int, default=9600, help="Baud rate.")
    parser.add_argument("--period", type=float, default=1.0, help="Period.")
    parser.add_argument("--value", type=float, default=1.00, help="Value.")
    parser.add_argument("--loop", action="store_true", help="Send in a loop.")

    args = parser.parse_args()
    arduino = Arduino(serial_port=args.port, baud_rate=args.baud_rate)

    if args.loop:
        arduino.send_loop(value=args.value, period=args.period)
    else:
        arduino.send(value=args.value)
