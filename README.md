# IronWatch

Factory walk-through gate: ferrous-theft detection (Proteus + Arduino) plus a facial-recognition attendance companion.

## The problem this repo just closed

**A0 = 0 and the alarm would not fire.**

Arduino A0 is wired to CD4046 **DEMOD (pin 10)**. That pin is a source-follower of **VCOIN (pin 9)**. VCOIN was left floating, so DEMOD sat at 0 V and `analogRead(A0)` returned **0**. The sketch then required `sensorValue > 600`. Zero cannot satisfy that. The gate was mute by construction.

**What you asked for:** A0 = 0 must **trigger**.

New firmware treats a collapsed demod voltage as metal:

```cpp
metalDetected = (sensorValue <= 40);   // A0 = 0 TRIGGERS
```

Wiring that lets A0 actually *move* (otherwise it stays 0 and the alarm just stays on):

```
RV1 wiper  →  4046 pin 9 (VCOIN)
4046 pin 10 (DEMOD)  →  Arduino A0
```

Fast Proteus bypass: RV1 wiper straight to A0.

## Where to look

| Path | What |
|---|---|
| [docs/A0-TRIGGER-DIAGNOSIS.md](docs/A0-TRIGGER-DIAGNOSIS.md) | Full diagnosis + Proteus click-by-click |
| [firmware/metal_gate_detector.ino](firmware/metal_gate_detector.ino) | Arduino sketch, MODE LOW default |
| [simulator/index.html](simulator/index.html) | Live A0=0 diagnostic console (open in a browser) |

## Pin map (unchanged from the Proteus sheet)

| Pin | Net | Role |
|---|---|---|
| A0 | 4046 DEMOD | ferrous signature voltage |
| D0 / D1 | Virtual Terminal | badge ID, 9600 baud |
| D2 | LED-RED | alarm |
| D3 | LED-GREEN | clear |
| D4 | BUZ1 | buzzer |

Authorized badge string: `A1B2C3` (5 second window).

## Proteus load

1. Arduino IDE → board Uno → Verify → Sketch → Export Compiled Binary.
2. Double-click the Uno in Proteus → Program File → the `.hex`.
3. Play. Virtual Terminal should print `A0=0 … [A0=0 TRIGGER]` if the pin is still sitting at zero.
