# How to Run — Isolated Step-by-Step PC Instructions

Follow these steps exactly, in order. No step depends on Simulink or any toolbox.

## What you need

| Item | Requirement |
|---|---|
| PC | Windows / macOS / Linux |
| MATLAB | R2016b or newer, **no toolboxes needed** (base MATLAB only) — or **GNU Octave** (free, from octave.org) |
| Files | The 3 files in the `matlab/` folder of this repo, kept together in ONE folder |

## Step 1 — Put the files in one folder

1. Create a folder, e.g. `C:\gate_project\` (Windows) or `~/gate_project/` (macOS/Linux).
2. Copy these 3 files into it (all from this repo's `matlab/` folder):
   - `gate_params.m`
   - `gate_gearbox_pid_sim.m`
   - `build_gate_simulink.m` (only needed later for Simulink)

## Step 2 — Open MATLAB and go to that folder

1. Start MATLAB.
2. In the **Current Folder** panel, navigate to your folder (`C:\gate_project\`),
   or type in the Command Window:
   ```matlab
   cd C:\gate_project\
   ```
3. Confirm: type `dir` — you must see the 3 `.m` files listed.

## Step 3 — Run the simulation

1. Double-click `gate_gearbox_pid_sim.m` to open it in the Editor (optional, for reading).
2. Press **F5** (or click **Run**). If MATLAB asks about "Change Folder" / "Add to Path",
   choose **Change Folder** (or add the folder to the path — either works).
3. Wait ~5–20 seconds. The Command Window prints the design report, then the results.

> Octave users: open a terminal in the folder and run `octave gate_gearbox_pid_sim.m`.

## Step 4 — Verify your output (acceptance check)

Your console output must contain these lines (numbers must match to the decimals shown):

```
Ratios: i1=4.0000 i2=4.3750 i3=4.0000 N_total=70.0000
J_eff @ output = 21.1302 kg m^2
Holding torque @ motor = 1.069 N m = 56.0% of rated
Gains (wn=8, zeta=1.0): Kp=2253.9 Ki=3606.2 Kd=394.4
```

and the test section must end with:

```
RESULT: ALL CHECKS PASSED
```

with (nominal plant) approximately:

| Metric | OPEN | CLOSE |
|---|---|---|
| Overshoot | 0.005° | 0.005° |
| Settling (0.5° band) | 0.00 s (never leaves band) | 0.00 s |
| RMS tracking error | 0.004° | 0.004° |
| Peak motor torque | 1.20 N·m (39% of limit) | — |
| Peak current | 15.7 A (limit 40 A) | — |
| Peak voltage | 4.2 V (supply 24 V) | — |

Two figures also open:
- **Figure 1** — nominal response: angle ref-vs-actual, error, speed, torque, current, voltage.
- **Figure 2** — robustness run (plant detuned +15% mass / +20% inertia / 2× friction,
  same controller): still tracks within 0.16°.

A file `gate_tuning.mat` is written next to the scripts — it carries the gains
into Simulink/hardware (see `SIMULINK_GUIDE.md`).

If anything differs, see **Troubleshooting** below before changing any code.

## Step 5 — Put in YOUR measured numbers (only 2–4 lines)

All editable parameters live in **`gate_params.m`** — never edit the other files
for tuning. Open `gate_params.m` and find the `[GIVEN]` / `[EST]` flags:

1. **Arm mass & balance point** (the two numbers the whole sizing rests on):
   - `P.m_arm = 13.5` — weigh arm + shaft together on a scale.
   - `P.Lc = 0.5` — currently assumes a uniform rod (balance point at L/2).
     To measure exactly: rest the arm (without shaft) across a round bar, slide it
     until it balances, measure pivot→balance distance. Type that value in.
2. **Motor electrics** (only if you change motor or can measure):
   - `P.motor.R` — lock the shaft, apply ~2 V, measure current: R = V/I.
   - `P.motor.J_rotor`, `P.motor.L` — take from the datasheet if given,
     otherwise leave the estimates (the design is insensitive to them — proven
     by the robustness run, which changes far bigger things).
3. Press **F5** again and confirm `ALL CHECKS PASSED` still prints.

## Step 6 — Retune only if you must (one knob)

The gains are computed from `P.ctrl.wn` (loop bandwidth, default `8.0`):
- Response too aggressive / noisy on real hardware → lower to `6.0`, re-run.
- Too sluggish → raise to `10.0`, re-run, and check the torque plot stays
  clear of the red limit lines.

Do not hand-edit Kp/Ki/Kd — they are derived from `wn` by pole placement.

## Step 7 — Next stages (in this order)

1. `docs/MOTOR_SELECTION.md` — why the 24 V 500 W motor was chosen, what to buy,
   wiring/fuse/supply sizing, and the shaft-adapter note for your 28 mm pinion bore.
2. `docs/SIMULINK_GUIDE.md` — build the Simulink twin (auto-build script + full
   click-by-click), press Run, compare with Step 4 numbers.
3. `docs/SIMSCAPE_SOLIDWORKS_GUIDE.md` — export your SolidWorks assembly into
   Simscape Multibody and drive it with the same controller.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Undefined function 'gate_params'` | MATLAB is in the wrong folder | Step 2: `cd` to the folder with the 3 files |
| `Not enough input arguments` opening a function file | You pressed Run on `gate_params.m` | Run `gate_gearbox_pid_sim.m` instead (F5) |
| No figures appear | Figure window behind others / Octave headless | Check taskbar; in Octave use GUI mode |
| Numbers differ slightly (last decimal) | Different MATLAB/BLAS version | Normal — round-off only; PASS/FAIL must still pass |
| `ALL CHECKS PASSED` missing after editing params | Real parameter change | Read the `[FAIL]` line: it names the violated spec; see Step 6, or check the motor can hold the load (report line `Holding torque ... % of rated` should stay < 70%) |
| Simulation is slow (> 60 s) | Very old PC | Normal on first run; close other apps. The loop is 32k RK4 steps by design (deterministic, matches Simulink fixed-step) |
