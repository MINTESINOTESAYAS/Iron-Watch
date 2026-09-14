# Electrical design (Proteus)

`electrical system.pdsprj` — schematic of the gate controller:

- ESP32 DevKit (controller), 5 V buck from 24 V supply
- BTS7960 H-bridge → 24 V 500 W DC motor (RPWM GPIO 18, LPWM GPIO 19)
- Metal-detector relay contact → GPIO 34 (pull-up, active LOW)
- Limit switches: open GPIO 32, closed GPIO 33
- Buzzer GPIO 25, alert LED GPIO 26, OK LED GPIO 27
- Serial (USB) link to the PC running `software/attendance/`

The same circuit is reproduced for browser simulation in `software/esp32_gate/diagram.json` (Wokwi). Pin map and rationale: report Sections 3.3.5 and 3.4.
