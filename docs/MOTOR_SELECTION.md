# Motor Selection & Sizing — Calculation Record

## 1. What the load actually demands

From your data (arm 13.5 kg @ 1.0 m, 70:1 gearbox, 0.96 efficiency per mesh):

| Quantity | Value | How |
|---|---|---|
| Worst-case gravity torque (arm horizontal) | **66.2 N·m** | m·g·Lc = 13.5 × 9.81 × 0.5 |
| Motor torque to hold it | **1.07 N·m** | 66.2 / (70 × 0.8847) |
| Peak output speed (90° in 6 s trapezoid) | 0.349 rad/s (20°/s) | profile math |
| Peak motor speed | **262 rpm** | 0.349 × 70 |
| Peak mechanical power | **≈ 30 W** | 66.2 × 0.349 + losses |
| Reflected inertia @ output | **21.13 kg·m²** | gear-by-gear computation in code |

So the motor must **hold 1.07 N·m continuously** (worst case), deliver ~1.2 N·m
peak during moves, spin only a few hundred rpm, and output tens of watts.

## 2. Why the IEC 100L (3 kW) motor is unsuitable

| Issue | Number |
|---|---|
| Rated power vs needed | 3000 W vs ~30 W → **100× oversized** |
| Rated torque vs needed | 19.6 N·m vs 1.07 N·m → motor idles at 5% load (poor efficiency, hunting) |
| Rotor inertia reflected to arm | 0.0154 × 70² ≈ **75 kg·m²** — it would *dominate* the whole mechanism and make the response sluggish |
| Supply | Needs 400 V 3-phase + VFD in vector mode — expensive, dangerous to wire, total overkill for a 1 m gate |
| Frame/shaft | 100L frame + 28 mm shaft dwarfs the gearbox input stage |

Verdict: keep the IEC 100L for a conveyor or pump. The gate needs a small motor.

## 3. Selected motor (primary): 24 V 500 W brushed DC, MY1020 class

Standard e-bike/scooter motor, stocked worldwide, driven by a single H-bridge.

| Spec | Value | Source |
|---|---|---|
| Voltage / power | 24 V / 500 W | nameplate |
| Rated speed | 2500 rpm | nameplate |
| Rated torque | **1.91 N·m** | 500 W @ 2500 rpm |
| Rated current | 27.4 A | datasheet (typical) |
| Winding resistance | 0.15 Ω | estimate (measure: locked-rotor V/I) |
| Winding inductance | 0.35 mH | estimate |
| Ke = Kt | 0.07597 (SI) | derived from rated point |
| Rotor inertia | 0.0006 kg·m² | estimate (contributes only 3.5 of 21.1 kg·m²) |
| Driver current limit | 40 A → 3.04 N·m peak | BTS7960-class H-bridge setting |

**Margins (the reason this size, not 250 W or 350 W):**

| Check | Value | Rule |
|---|---|---|
| Holding / rated | 1.07 / 1.91 = **56%** | must be < 70% for cool continuous holding ✓ |
| Peak move / rated | ~1.20 / 1.91 = **63%** | comfortable ✓ |
| Peak move / driver limit | 1.20 / 3.04 = **39%** | transients never clip ✓ |
| Voltage headroom | 4.2 V used of 24 V | huge margin; even a sagging battery works ✓ |

A 250 W motor (rated ~0.9 N·m) **cannot** hold the arm — it would stall/overheat.
A 350 W motor (≈1.2 N·m rated) holds at ~90% — workable but hot. 500 W is the
smallest standard size with proper margin.

## 4. Alternative (drop-in): 24 V 500 W BLDC + BLD-750-class driver

Same power class, brushless (longer life, quieter), needs its electronic driver
in torque/current mode. Parameters are pre-loaded as a commented block in
`gate_params.m` (section 4) — uncomment to switch. All simulation results are
practically identical (rated 1.59 N·m, holding at 67%).

## 5. Mechanical interface — read before ordering!

- Your **Pinion 1 bore is Ø28 mm** (it matches an IEC 100L shaft).
  Small DC/BLDC motors have shafts around **12–14 mm** (measure yours!).
- You need a **reducing sleeve + stepped key** (28 mm OD / motor-shaft ID,
  length ≥ 25 mm face width) with a set screw, **or** have a new Pinion 1 cut
  with the correct bore. Do not run a loose pinion on the shaft.
- Verify shaft rotation direction vs your opening direction before final
  assembly (swap motor leads to reverse a brushed DC motor).

## 6. Purchase & wiring list

| Item | Spec |
|---|---|
| Motor | 24 V 500 W brushed DC (MY1020/Unite class), with mounting bracket |
| Driver | Dual BTS7960 H-bridge module (43 A), heatsink + fan |
| Power supply | 24 V DC, **≥ 30 A (720 W)** regulated, **or** 2× 12 V 20 Ah batteries in series |
| Fuse | 50 A slow-blow in the battery/supply + lead |
| Wire motor↔driver | ≥ 4 mm² copper (peaks 40 A); keep short |
| Angle sensor | Incremental encoder ≥ 1000 CPR on arm shaft, or 10-turn pot + ADC (you need θ feedback for the PID) |
| Safety | Mushroom E-stop cutting driver power; mechanical end-stops at 0° and 90°; arm pinch guards |

## 7. What mass figures the equations want (your question, answered)

The gravity term is `m·g·Lc·cos(θ)` and the inertia term uses `(1/3)·m·L²`.
I used **m = 13.5 kg (arm + shaft weighed together)** and **Lc = 0.5 m**
(uniform-rod assumption). To make it exact:

1. Weigh the arm **without** the shaft → `m_rod`.
2. Balance the bare arm on a pipe to find its balance point → measure
   pivot-to-balance distance → `Lc`.
3. Set `P.m_arm`/`P.Lc` in `gate_params.m`
   (shaft mass on the pivot axis adds inertia ≈ 0.005 kg·m² — negligible — and
   zero gravity moment, so it is correctly ignored).
4. Re-run: the report, gains and plots all update automatically.
