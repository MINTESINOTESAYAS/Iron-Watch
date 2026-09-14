"""Serial link to the ESP32 gate controller (metal detector + gate motor).

Protocol (one line per message, 115200 baud):
    ESP32 -> PC :  METAL:1   (detector tripped)   METAL:0  (clear)
    PC -> ESP32 :  OPEN      (worker recognised, open gate)
                   DENY      (unknown face, keep closed + buzzer)
If config.SERIAL_PORT is None everything here is a harmless no-op, so the
face system runs stand-alone on a laptop.
"""
import threading
import time
import config


class GateLink:
    def __init__(self):
        self._ser = None
        self._metal_until = 0.0
        if config.SERIAL_PORT:
            import serial                      # pyserial
            self._ser = serial.Serial(config.SERIAL_PORT, config.SERIAL_BAUD, timeout=0.2)
            threading.Thread(target=self._reader, daemon=True).start()
            print(f"Gate link on {config.SERIAL_PORT}")

    def _reader(self):
        while True:
            try:
                line = self._ser.readline().decode(errors="ignore").strip()
            except Exception:
                time.sleep(0.5)
                continue
            if line == "METAL:1":
                self._metal_until = time.time() + config.METAL_HOLD_S
            elif line == "METAL:0":
                self._metal_until = 0.0

    @property
    def metal_detected(self) -> bool:
        return time.time() < self._metal_until

    def send(self, cmd: str):
        if self._ser:
            self._ser.write((cmd + "\n").encode())
