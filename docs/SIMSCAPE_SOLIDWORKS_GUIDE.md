# Simscape + SolidWorks Guide — Drive YOUR Assembly with the PID Controller

Goal: your real SolidWorks gearbox + arm assembly, moving 0°→90°→0° in MATLAB,
driven by the verified PID controller. The idealized equation in the `.m` sim is
replaced by your true multibody geometry — the controller stays the same.

> Time estimate: 1–2 hours first time (mostly install + export).
> Requires: SolidWorks 2018+ on Windows, MATLAB with **Simscape Multibody**
> (same release year as the Multibody Link add-in), and the model built in
> `SIMULINK_GUIDE.md`.

---

## Part 0 — Prepare the SolidWorks assembly (30 min — do not skip)

Your export is only as good as your mates. Audit them now:

1. Open your gate assembly. Open **Evaluate → Mass Properties** for each gear
   (click the part in the tree, not the assembly). Compare with the computed table:

   | Gear | Predicted mass | Your SolidWorks value |
   |---|---|---|
   | P1 | 0.28 kg | ___ |
   | G1 | 6.35 kg | ___ |
   | P2 | 0.73 kg | ___ |
   | G2 | 15.29 kg | ___ |
   | P3 | 1.36 kg | ___ |
   | G3 | 23.26 kg | ___ |

   Within ±10% → your density/material and bores are right (teeth add/remove a
   little vs the cylinder approximation — expected). Off by 2×+ → check material
   (must be steel, not default "plain carbon steel" with wrong density, and check
   the bore cuts actually exist).
2. Check the three shaft **centre distances**: 127.5 / 172.0 / 200.0 mm
   (Measure tool, axis to axis). If they differ, your gears were placed visually —
   fix with distance mates or the teeth will mesh wrong in reality.
3. Mates audit (each shaft needs exactly: 1 Concentric to its housing bore +
   1 Coincident/Distance along the axis; each gear: Concentric + Coincident to its
   shaft shoulder):
   - Motor shaft + P1; Shaft A + G1 + P2; Shaft B + G2 + P3; Output shaft + G3 + arm.
   - No redundant/conflicting mates (FeatureManager shows no red/yellow).
4. Arm pivot: add a **LimitAngle mate** 0°–90° between arm and frame as a
   mechanical sanity reference (it exports as documentation; limits are enforced
   by the controller + physical end-stops, not the mate).
5. **Save everything.** Note the assembly's units (Tools → Options → Units —
   use MMGS) and which plane is "up" (gravity direction).

## Part 1 — Install Simscape Multibody Link (one time)

6. In MATLAB: check your release, e.g. `ver` → note `R2024a` (any year works,
   but Link version should match).
7. Download **Simscape Multibody Link** for your release from mathworks.com
   (search "Simscape Multibody Link SolidWorks", free, needs login).
8. Close SolidWorks. Run the installer as Administrator (it registers `smlink`).
9. Open SolidWorks → **Tools → Add-Ins** → tick **Simscape Multibody Link** → OK.
   Verify: the **Tools** menu now shows **Simscape Multibody Link → Export**.

## Part 2 — Export the assembly

10. Open the assembly (all parts resolved, no lightweight mode: right-click top
    assembly → Set Lightweight to Resolved).
11. **Tools → Simscape Multibody Link → Export → Simscape Multibody…**
12. In the dialog: select the assembly (default), output folder e.g.
    `C:\gate_project\sm_export\`. Keep defaults (STEP visuals ON). → **Export**.
13. Result: one `.xml` file (e.g. `gate_asm.xml`) + a folder of `.step` visuals.
    Errors here are 95% mate problems — go back to Part 0.

## Part 3 — Import into Simscape

14. In MATLAB: `cd` to the export folder.
15. Command Window:
    ```matlab
    smimport('gate_asm.xml')   % use YOUR xml name
    ```
    A model `gate_asm.slx` is generated and opened: one **Solid** block per part,
    **Rigid Transform** blocks, and **Revolute Joint** blocks where mates allowed
    rotation (4 shaft joints + arm pivot — count them!).
16. Add the two blocks every Simscape model needs (Library Browser → Simscape):
    - **Utilities → Solver Configuration**: connect to any frame line (it has no
      position — wire it to the World Frame's assembly side). Leave defaults,
      but set Solver Type `Backwards Euler`, tolerance `1e-4` for speed.
    - **Utilities → Mechanism Configuration**: set **Gravity** to your "down"
      (if SolidWorks up is +Y, gravity vector = `[0 -9.81 0]`).
17. Save. Press Run — the **Mechanics Explorer** window should show your gate
    (it will just sit/dangle — no actuation yet). If parts explode/fly: a joint
    lost its mate reference — re-export after fixing mates.

## Part 4 — Add the 3 gear meshes (critical — export does NOT do this)

Mates only say "these spin"; they don't say "teeth mesh at ratio i". Add:

18. Library → **Simscape → Multibody → Gears and Constraints → Gear Constraint**.
    Place 3 copies: `Mesh1`, `Mesh2`, `Mesh3`.
19. Each Gear Constraint has Base Follower ports (B, F) + two frame ports.
    Connect B/F across the mating pair's carrier frames:
    - `Mesh1`: between motor-shaft joint frame and Shaft-A joint frame.
      Base Gear Pitch Radius = `25.5 mm`, Follower = `102.0 mm`
      (pitch radii: 51/2 and 204/2).
    - `Mesh2`: Shaft A ↔ Shaft B: `32.0 mm` / `140.0 mm`.
    - `Mesh3`: Shaft B ↔ Output: `40.0 mm` / `160.0 mm`.
    (Units: open each block, set Pitch Radius units to `mm`.)
    > Which side is Base vs Follower only flips the sign convention — pick the
    > pinion as Base in all three, then verify direction in Part 6 (if the arm
    > opens when it should close, swap two motor leads / invert the torque sign).
20. Save, Run — shafts now turn together at 70:1. Test: temporarily actuate the
    motor joint (step 21) with a tiny constant torque and watch all shafts spin
    in Mechanics Explorer.

## Part 5 — Actuate + connect YOUR controller

21. Open the **arm pivot Revolute Joint** block → **Actuation**: check
    **Torque → Provided by Input** (Mode automatically becomes torque-driven).
    → **Sensing**: check **Position** and **Velocity** (these output θ and ω).
    The block gains ports T (torque in), q (position out), w (velocity out).
22. Copy the controller from your verified model: open `gate_gearbox_pid.slx`
    (built in `SIMULINK_GUIDE.md`), select everything EXCEPT the plant blocks
    (`ToOutput…TH`, `ViscPlant`, `Coul…`, `CosTh`-plant branch, monitor, scopes),
    copy, and paste into `gate_asm.slx`. (Simpler alternative: rebuild per the
    click-by-click — same blocks, 30 min.)
23. Wire across the Simulink↔Simscape boundary (needs converters):
    - Joint `q` → **Simscape → Utilities → PS-Simulink Converter** → controller's
      `th` feedback (where `TH` used to feed). Set converter units `rad`.
    - Joint `w` → **PS-Simulink Converter** (units `rad/s`) → controller's `w`.
    - Controller torque output: IMPORTANT — the controller computes torque at the
      **arm/output shaft** (`OutTauSum`), while the joint expects torque at the
      **joint it's attached to**. Since you actuate the ARM joint directly, wire
      `OutTauSum` (output-side torque, N·m) → **Simulink-PS Converter**
      (units `N*m`) → joint `T`. (Do NOT use the motor-side signal — the gearbox
      is now real geometry, not the `N·η` gain. Delete/bypass `ToMotor…Driver…
      ToOutput` for the Simscape run — or keep them as a live "what the motor
      sees" monitor by feeding them from the same signals. Cleanest: keep
      `ToMotor→CurLim→Driver→ToCurrent/Rdrop/EMF/VoltSum` wired as a monitor
      chain driven by `OutTauSum`, so current/voltage plots stay valid.)
    - Current-limit saturation `CurLim` stays (it protects the virtual motor):
      chain is OutTauSum → ToMotor → CurLim → Driver → ToOutput → joint T.
      This preserves EXACTLY the `.m` behavior including limits.
24. Set the profile source: `gate_prof` + From Workspace block came along with
    the paste (or re-add per guide). Ensure `gate_prof` is in the base workspace
    (re-run its generation lines if you restarted MATLAB).
25. Solver for multibody: Model Settings → Solver `ode15s (stiff/NDF)`,
    Max step `0.01`, Relative tolerance `1e-4`. (Multibody + contacts need a
    stiff solver; the controller still samples every 1 ms via a Rate Transition
    if you want strict parity — for this slow gate, direct connection is fine.)

## Part 6 — Run, verify, iterate

26. Set the arm's initial angle to closed: arm Revolute Joint → **State Targets →
    Position Priority High, Value 0**. Press **Run**.
27. Watch Mechanics Explorer: dwell → smooth OPEN (6 s) → dwell → CLOSE → dwell.
    Open your pasted ScopeAngle: it must closely match Figure 1 of the `.m` sim.
    Small differences (< 1–2°) vs the `.m` sim are EXPECTED and GOOD — they are
    your real inertias/geometry talking instead of the cylinder approximation.
28. Direction check: if the arm moves opposite (tries to go below 0°), either
    swap Base/Follower on all three Gear Constraints, or put a **Gain −1**
    before the joint torque (document which you chose).
29. Torque sanity: the monitor chain's peak current must still be < 40 A and
    voltage < 24 V. If the real-geometry gravity torque exceeds the estimate
    (arm CoM further out than L/2), update `P.Lc` in `gate_params.m` from the
    SolidWorks Mass Properties (Center of Mass relative to pivot!) and re-run
    everything — that closes the loop between CAD and control.
30. Save the final `gate_asm.slx` next to your other models.

## Quick alternative (no Simscape license): SolidWorks Motion check

If you only need a kinematic/interference check: SolidWorks **Motion Study** →
**Motor** → Rotary Motor on the arm pivot → Motion: **Distance**, 90°, 6 s,
**Linear** profile → Calculate. Use **Results → Trace Path / Interference
Detection** and plot motor torque to cross-check the 66 N·m figure. Note: Motion
cannot run your PID — control validation stays in MATLAB/Simulink/Simscape.
