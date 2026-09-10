"""
Read IronWatch Arduino serial and treat A0=0 as metal_detected.

Usage:
    python a0_serial_bridge.py --port COM3
    python a0_serial_bridge.py --port /dev/ttyUSB0

The firmware already prints lines like:
    A0=0  V=0.00  METAL=YES  AUTH=no   ALARM=ON ***  [A0=0 TRIGGER]

This script just parses them so exit_scanner.py can drop the fake 'm' key later.
"""
from __future__ import annotations

import argparse
import re
import sys
import time

LINE = re.compile(
    r"A0=(?P<adc>\d+)\s+V=(?P<volts>[\d.]+)\s+METAL=(?P<metal>\S+)\s+"
    r"AUTH=(?P<auth>\S+)\s+ALARM=(?P<alarm>\S+)"
)


def parse_line(text: str) -> dict | None:
    m = LINE.search(text)
    if not m:
        return None
    d = m.groupdict()
    return {
        "adc": int(d["adc"]),
        "volts": float(d["volts"]),
        "metal": d["metal"].startswith("Y"),
        "authorized": d["auth"].startswith("Y"),
        "alarm": d["alarm"].startswith("ON"),
        "a0_zero_trigger": d["adc"] == "0" or int(d["adc"]) == 0,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="IronWatch A0 serial bridge")
    p.add_argument("--port", required=True)
    p.add_argument("--baud", type=int, default=9600)
    args = p.parse_args()

    try:
        import serial  # type: ignore
    except ImportError:
        print("Install pyserial:  pip install pyserial", file=sys.stderr)
        return 1

    ser = serial.Serial(args.port, args.baud, timeout=1)
    print(f"Listening on {args.port} @ {args.baud}. Ctrl+C to stop.")
    try:
        while True:
            raw = ser.readline().decode("utf-8", errors="replace").strip()
            if not raw:
                time.sleep(0.02)
                continue
            parsed = parse_line(raw)
            if parsed:
                flag = "TRIGGER" if parsed["alarm"] else "clear"
                print(
                    f"[{flag:7}] A0={parsed['adc']:4d}  "
                    f"metal={parsed['metal']} auth={parsed['authorized']}"
                )
            else:
                print(raw)
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        ser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
