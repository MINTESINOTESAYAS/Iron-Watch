# Iron-Watch — 90° Gate Gearbox: PID Control, Simulink & Simscape Twin

3-stage **70:1** spur gearbox (17→68, 16→70, 16→64) driving a **1.0 m / 13.5 kg**
boom arm 0° (closed) → 90° (open) → 0° on a trapezoidal profile, under
**PID + gravity/inertia/friction feedforward**, with a **24 V 500 W DC motor**.

## Repository map

| Path | What |
|---|---|
| `matlab/gate_params.m` | **Single source of truth** — every parameter, edit only here |
| `matlab/gate_gearbox_pid_sim.m` | Main simulation — press F5, no toolboxes needed |
| `matlab/build_gate_simulink.m` | Auto-builds the 56-block Simulink twin (`gate_gearbox_pid.slx`) |
| `docs/HOW_TO_RUN.md` | **Start here** — isolated step-by-step PC instructions |
| `docs/MOTOR_SELECTION.md` | Sizing record, purchase list, wiring, shaft-adapter note |
| `docs/SIMULINK_GUIDE.md` | Auto-build + full click-by-click manual build |
| `docs/SIMSCAPE_SOLIDWORKS_GUIDE.md` | SolidWorks → Simscape Multibody export & integration |
| `verification/` | Independent Python mirror + expected console output + static checks |

## Quickstart

1. Copy the 3 `matlab/*.m` files into one folder (e.g. `C:\gate_project\`).
2. MATLAB → `cd` there → open `gate_gearbox_pid_sim.m` → **F5**.
3. Confirm the console ends with `RESULT: ALL CHECKS PASSED`.

Details + acceptance numbers: [`docs/HOW_TO_RUN.md`](docs/HOW_TO_RUN.md).

## Verified results (nominal → worst-case detuned plant)

Overshoot 0.005° → 0.06° · RMS error 0.004° → 0.07° · steady error < 0.03° ·
peak torque 1.20 → 1.54 N·m (limit 3.04) · peak current 15.7 → 20.2 A (limit 40 A) ·
peak voltage 4.2 → 4.8 V (supply 24 V). Full trace: `verification/expected_results.txt`
(formatted exactly as this script prints it — diff your run against it).

**Verification status:** independent numeric replica ✓ · static analysis
(bracket/param/`fprintf`-arity/Simulink wiring, 56 blocks / 75 lines) ✓ ·
MATLAB grammar parse of all 3 files ✓ — details in
[`verification/README.md`](verification/README.md).
