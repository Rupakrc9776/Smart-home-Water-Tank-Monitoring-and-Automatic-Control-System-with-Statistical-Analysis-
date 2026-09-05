"""Headless append-only serial logger for the smart water tank."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import serial
from serial.tools import list_ports
from dashboard import BAUD_RATE, CSV_PATH, parse_reading


def find_port() -> str | None:
    ports = list(list_ports.comports())
    preferred = ("arduino", "wch", "usb serial", "ch340", "usb")
    for port in ports:
        description = f"{port.description} {port.manufacturer or ''}".lower()
        if any(marker in description for marker in preferred):
            return port.device
    return ports[0].device if ports else None


def main() -> None:
    requested_port = input("Arduino port [auto]: ").strip()
    port = requested_port or find_port()
    if not port:
        print("No serial port detected.")
        return
    path = Path(CSV_PATH)
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(("Time", "Distance_cm", "Water_Percent", "Pump"))
    print(f"Logging {port} at {BAUD_RATE} baud. Press Ctrl+C to stop.")
    connection = None
    try:
        connection = serial.Serial(port, BAUD_RATE, timeout=1)
        while True:
            reading = parse_reading(connection.readline().decode("utf-8", errors="ignore").strip())
            if reading is None:
                continue
            distance, level, pump = reading
            stamp = datetime.now().strftime("%H:%M:%S")
            with path.open("a", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow((stamp, f"{distance:g}", f"{level:g}", pump))
            print(f"{stamp} | {level:.0f}% | Pump {pump} | Distance {distance:.1f} cm")
    except serial.SerialException as error:
        print(f"Serial connection failed: {error}")
    except KeyboardInterrupt:
        print("\nLogging stopped.")
    finally:
        if connection is not None and connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
