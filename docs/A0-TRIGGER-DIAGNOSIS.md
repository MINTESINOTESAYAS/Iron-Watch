# A0 = 0 — why the alarm never fired, and how to trigger it

You asked to continue the Proteus / Arduino session and diagnose **A0 = 0, I want to trigger**.

This is not a random ADC glitch. It is two stacked faults: a **hardware net that cannot produce a voltage**, and **firmware that refuses to treat 0 as metal**.

---

## What you are seeing

| Symptom | Meaning |
|---|---|
| Virtual Terminal prints `Sensor=0` or nothing useful | `analogRead(A0)` is returning **0** |
| Red LED / buzzer never start | old sketch requires `sensorValue > 600` |
| Turning RV1 does nothing to A0 | A0 is **not** listening to the pot |
| ERC still lists `UNDRIVEN: U1,VCOIN` | that unused pin is the analog input of DEMOD |

Arduino A0 is wired to **4046 pin 10 (DEMOD)**. On a CD4046, pin 10 is not a magic “metal detected” flag. It is an **internal source-follower of pin 9 (VCOIN)**.

```
VCOIN (pin 9)  ──source follower──►  DEMOD (pin 10)  ──wire──►  Arduino A0
     ▲
     └── left FLOATING in your schematic
```

Floating VCOIN ⇒ DEMOD ≈ 0 V ⇒ `analogRead(A0) = 0` forever.

The previous sketch then did:

```cpp
bool metalDetected = (sensorValue > METAL_THRESHOLD);  // THRESHOLD = 600
```

**0 is never greater than 600.** The alarm is electrically impossible.

The earlier advice that “VCOIN and ZENER can stay floating” was wrong for this topology. ZENER can stay open. **VCOIN cannot**, not if A0 is reading DEMOD.

---

## What “A0 = 0” should mean in this gate

A collapsed demod voltage is a legitimate ferrous-detect signature:

- Idle coil / PLL locked → DEMOD sits at some mid/high DC
- Ferrous mass in the field → inductance jumps, loop unlocks, **DEMOD dumps toward 0 V**
- Firmware should fire when A0 is **at or near 0**, not when it crosses 600

That is what you asked for. The new firmware does exactly that.

---

## Fix 1 — firmware (already written)

File: `firmware/metal_gate_detector.ino`

```cpp
// A0 near 0  =  metal  =  TRIGGER
metalDetected = (sensorValue <= 40);
```

Default polarity is **MODE LOW**. Live serial looks like:

```
A0=0  V=0.00  METAL=YES  AUTH=no   ALARM=ON ***  [A0=0 TRIGGER]
```

If A0 is stuck at 0 when you load this hex, **the alarm will come on immediately**. That is the proof the logic is now the right way around. To also be able to *clear* the alarm, A0 has to be able to rise — which is Fix 2.

### Load it into Proteus (click by click)

1. Open the sketch in Arduino IDE, board = **Arduino Uno**.
2. **Sketch → Verify/Compile**.
3. **Sketch → Export Compiled Binary**.
4. In the sketch folder find `metal_gate_detector.ino.hex` (or `*.ino.standard.hex`).
5. Proteus: double-click the Uno → **Program File** → browse to that `.hex` → **OK**.
6. Click **Play**.
7. Double-click the Virtual Terminal. You should see `ALARM=ON ***  [A0=0 TRIGGER]` if A0 is still 0.

Virtual Terminal commands (9600 baud, type then Enter):

| Type | Effect |
|---|---|
| `A1B2C3` | authorized 5 s (alarm suppresses even if metal) |
| `MODE LOW` | A0=0 triggers (default) |
| `MODE HIGH` | old behaviour, A0 high triggers |
| `TH 40` | set ADC threshold |
| `HELP` | list commands |

---

## Fix 2 — give VCOIN a real voltage so A0 can move

Stop the simulation first.

### Preferred (keeps the 4046 in the analog path)

1. Identify **RV1** middle pin (wiper).
2. Draw a wire from that wiper to **U1 pin 9 (VCOIN)**.
3. Confirm pin 10 (DEMOD) still goes to Arduino **A0**.
4. Play. Sweep RV1. Virtual Terminal `A0=` numbers must change.
5. Turn RV1 fully toward ground until `A0=0` → red LED + buzzer.

### Fastest Proteus demo (bypass DEMOD)

If the 4046 model still holds DEMOD at 0 V after wiring VCOIN:

1. Delete the DEMOD → A0 wire.
2. Wire **RV1 wiper directly to Arduino A0**.
3. Play. Pot = 0 % → A0 = 0 → **TRIGGER**. Pot up → CLEAR.

This is legitimate for the simulation: RV1 already stands in for “ferrous object walked through the coil.” You are just letting the Arduino see that stand-in.

---

## Prove it with a voltmeter (2 minutes)

1. **P** → search `VOLTMETER` → place it.
2. Voltmeter **+** to the A0 net, **−** to ground.
3. Play.
4. If the meter reads **0.00 V** and RV1 does nothing, A0 is not connected to a driven analog source (VCOIN still open, or DEMOD dead in the model).
5. After the VCOIN (or direct-pot) wire, the meter must swing as you turn RV1.

---

## Why turning RV1 never changed A0 before

Signal path that was *drawn* on the sheet:

```
L1/C1  →  LM358  →  4046 analog  →  DEMOD  →  A0
                ↗
              RV1
```

Signal path that A0 actually had:

```
(floating VCOIN)  →  DEMOD  →  A0  =  0 V
```

RV1 and the LM358 can be switching all day. None of that voltage reaches pin 10 unless it is fed into **VCOIN**.

---

## Expected demo sequence (for your supervisor)

1. Simulation running, no badge typed.
2. RV1 at ground → terminal shows `A0=0 … ALARM=ON ***` → red LED + buzzer.
3. Raise RV1 → `ALARM=off`, green LED.
4. Drop RV1 to 0 again → alarm returns. **That is the A0=0 trigger.**
5. Type `A1B2C3` while A0 is still 0 → `AUTH=YES  ALARM=off` for 5 s (authorized tool checkout).
6. After 5 s, alarm returns if A0 is still 0.

A browser console that behaves the same way lives in `simulator/index.html` — use it if you want to show the logic without waiting on Proteus.

---

## What not to “fix”

- ERC warnings on Arduino RXD and A0 connected to outputs — informational, leave them.
- `UNDRIVEN: U1,ZENER` — unused, leave open.
- `UNDRIVEN: Virtual Terminal,CTS` — unused, leave open.
- Do **not** raise `METAL_THRESHOLD` to 0 with the old `>` comparison. `sensorValue > 0` still misses a stuck-at-zero pin. Use `<=`.
