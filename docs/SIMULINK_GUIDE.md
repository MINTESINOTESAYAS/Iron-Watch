# Simulink Guide — Auto-Build + Click-by-Click Manual Build

You have two ways to get the identical model. **Do Option A.** Option B exists so
you (and your examiner) can see and defend every single block.

Block diagram (signal flow — left to right):

```
gate_prof ──►[From Workspace]──►[Demux]─┬─th_d─┬───────────────────────────►(Mux/Scope angle)
                                         │      ├─►[ErrSum +-]─e─┬─►[Kp]────►[PIDSum]─►[OutTauSum]─►[ToMotor 1/(N·η)]
                                         │      │                ├─►anti-windup gate─►[Ki]─►[IntE limited]─┘        │
                                         │      │                └─(D path below)                              [CurLim ±Tpeak]
                                         ├─w_d──┼─►[VelErrSum +-]─ed─►[Dfilt λ/(s+λ)]─►[Kd]──────────────────────►┘        │
                                         │      ├─►[ViscFF b]───────────────────────────────────►[FFSum]────────┘        │
                                         │      └─►[CoulNorm 20]─►[tanh]─►[CoulFF tc]─────────────►┘                     ▼
                                         └─a_d──►[InertFF J]─────────────────────────────────────►┘              [Driver 1/(τs+1)]
                                         ─th (feedback)─┬─► ErrSum(-), CosTh ─►[GravFF mgLc]─┬─► FFSum(FF)              │
                                                        │                                    └─► PlantSum(-)          ▼
                                         ─w (feedback)─┴─► VelErrSum(-), ViscPlant, tanh path ──► PlantSum(-)   [ToOutput N·η]
                                                                                                   │
                                          Plant: PlantSum(+---)─►[InvJ 1/J]─►[W ∫]─► w ─►[TH ∫]─► th ─┘ (feedback up)
                                          Monitor: τ─►[1/Kt]─► i ; v = i·R + Ke·N·w ; Scopes + To Workspace logs
```

Numbers (from `gate_params.m` — do not retype blindly, copy from your console report):

| Gain | Value | Gain | Value |
|---|---|---|---|
| Kp / Ki / Kd | 2253.9 / 3606.2 / 394.4 | ToMotor 1/(N·η) | 0.016146 |
| Dfilt λ | 188.496 (num `[188.496]`, den `[1 188.496]`) | CurLim | ±3.039 |
| IntE limits | ±25 (output = I-term) | Driver | num `[1]`, den `[0.004 1]` |
| GravFF mgLc | 66.2175 | ToOutput N·η | 61.9315 |
| InertFF J | 21.1302 | InvJ | 0.047326 |
| ViscFF / CoulFF | 1.5 / 2.5 | ToCurrent 1/Kt | 13.1623 |
| CoulNorm / CoulNormP | 20 / 50 | Rdrop / EMF | 0.15 / 5.31818 |

---

## Option A — Auto-build (3 clicks, recommended)

1. In MATLAB, `cd` to the folder with the 3 `.m` files.
2. Command Window, type:
   ```matlab
   build_gate_simulink
   ```
   and press Enter. The model `gate_gearbox_pid.slx` is created, saved and opened.
3. Press **Run** (or Ctrl+T). Double-click **ScopeAngle**: the two traces must lie
   on top of each other, matching Figure 1 of the `.m` sim. Acceptance:
   overshoot < 2°, steady error < 0.3°, peak torque ≈ 1.2 N·m (ScopeTorque).
4. (Optional) Compare numerically in the Command Window:
   ```matlab
   err = th_d_log(:,2) - th_log(:,2);
   fprintf('max|err| = %.4f deg\n', max(abs(err))*180/pi);
   ```
   Expect ≈ 0.015° (nominal). If you see this, the Simulink twin is verified
   against the proven `.m` simulation.

> If `build_gate_simulink` errors with "Could not create a Simulink model",
> Simulink is not installed/licensed — the `.m` simulation already gives you
> all results; use Option B on a licensed machine later.

## Option B — Click-by-click manual build

Create the same model by hand (verify at the end with step 4 above).

### B.0 — New model + solver (do first)

1. MATLAB Home → **Simulink** → **Blank Model**. Save as `gate_gearbox_pid`.
2. Open **Modeling → Model Settings** (Ctrl+E):
   - Solver: Type = `Fixed-step`, Solver = `ode4 (Runge-Kutta)`, Fixed-step size = `0.001`.
   - Stop time = `16`. → OK.
3. Open the **Library Browser** (View → Library Browser). All blocks below are
   added by drag-and-drop from the path shown, then double-clicked to set parameters.

### B.1 — Reference profile (needs base-workspace data)

4. Command Window — build the profile table once (paste):
   ```matlab
   P = gate_params(); dt = 0.001; tv = (0:dt:16)';
   warning('off'); % (nothing to warn about; keeps output clean)
   ```
   Then generate it with the sim's own equations — simplest: run
   `gate_gearbox_pid_sim` once (it also saves `gate_tuning.mat`), then paste:
   ```matlab
   load gate_tuning.mat
   ```
   The auto-build script normally makes `gate_prof` for you; for the manual build,
   run these lines to create it identically:
   ```matlab
   P = gate_params(); dt = P.sim.dt; T = P.prof; t = (0:dt:T.T_end)';
   th = zeros(size(t)); w = th; a = th;
   for k = 1:numel(t)
     tk = t(k);
     if tk < T.t0_open, p=0;v=0;ac=0;
     elseif tk < T.t1_open, [p,v,ac] = profseg((tk-T.t0_open)/T.T_move,T);
     elseif tk < T.t0_close, p=T.move;v=0;ac=0;
     elseif tk < T.t1_close, [p,v,ac] = profseg((tk-T.t0_close)/T.T_move,T); p=T.move-p; v=-v; ac=-ac;
     else, p=0;v=0;ac=0; end
     th(k)=p; w(k)=v; a(k)=ac;
   end
   gate_prof = [t th w a];
   function [p,v,ac] = profseg(s,T)
     D=T.move;Ta=T.T_acc;vv=T.v_pk;aa=T.a_pk;tt=s*T.T_move;
     if tt<=0, p=0;v=0;ac=0; elseif tt<Ta, p=.5*aa*tt^2;v=aa*tt;ac=aa;
     elseif tt<T.T_move-Ta, p=.5*aa*Ta^2+vv*(tt-Ta);v=vv;ac=0;
     elseif tt<T.T_move, td=T.T_move-tt; p=D-.5*aa*td^2; v=vv-aa*(tt-(T.T_move-Ta)); ac=-aa;
     else, p=D;v=0;ac=0; end
   end
   ```
   (Paste the whole block at once — MATLAB accepts local functions in scripts.)
   Verify: `size(gate_prof)` → `16001  4`.
5. Drag **Sources → From Workspace**, name it `Profile`, set Variable name =
   `gate_prof`. Drag **Signal Routing → Demux**, Number of outputs = `3`.
   Connect Profile → Demux. (Outputs top→bottom: th_d, w_d, a_d.)

### B.2 — Errors, P, I (with anti-windup), D

6. **Math Operations → Sum** `ErrSum`, List of signs = `+-`. Wire Demux/1 → ErrSum/+.
7. **Math Operations → Sum** `VelErrSum`, signs `+-`. Wire Demux/2 → VelErrSum/+.
8. **Math Operations → Gain** `Kp` = `2253.9` (your exact value from the report).
   Wire ErrSum → Kp.
9. Integrator + anti-windup gate (the only "clever" part — it freezes the
   integrator exactly when the driver saturates):
   - **Sources → Constant** `Tpeak_pos` = `3.039`, `Tpeak_neg` = `-3.039`,
     `Zero` = `0`, `Zero2` = `0`.
   - **Logic and Bit Operations → Relational Operator** `GT_hi` (`>`),
     `LT_lo` (`<`), `E_pos` (`>`), `E_neg` (`<`).
   - **Logic and Bit Operations → Logical Operator** `AND_hi` (AND, 2 inputs),
     `AND_lo` (AND), `OR_fr` (OR, 2 inputs).
   - **Signal Routing → Switch** `IntGate`: Criteria `u2 >= Threshold`, Threshold `0.5`.
   - **Math Operations → Gain** `Ki` = `3606.2`.
   - **Continuous → Integrator** `IntE`: Initial condition `0`, check
     **Limit output**, Upper `25`, Lower `-25`.
   - Wire: ToMotor(output, step B.4) → GT_hi/1 and LT_lo/1; Tpeak_pos → GT_hi/2
     and later MuxTau/2; Tpeak_neg → LT_lo/2 and MuxTau/3; ErrSum → E_pos/1,
     E_neg/1 and IntGate/3; Zero → E_pos/2, E_neg/2; GT_hi+E_pos → AND_hi;
     LT_lo+E_neg → AND_lo; ANDs → OR_fr; OR_fr → IntGate/2; Zero2 → IntGate/1;
     IntGate → Ki → IntE.
10. **Continuous → Transfer Fcn** `Dfilt`: Numerator `[188.496]`,
    Denominator `[1 188.496]`. Wire VelErrSum → Dfilt.
11. **Gain** `Kd` = `394.4`. Wire Dfilt → Kd.
12. **Sum** `PIDSum`, signs `+++`. Wire Kp → 1, IntE → 2, Kd → 3.

### B.3 — Feedforward

13. **Trigonometric Function** `CosTh`, Function `cos`; **Gain** `GravFF` =
    `66.2175`. (Input `th` wired in step B.5.)
14. **Gain** `InertFF` = `21.1302` ← Demux/3 (a_d).
15. **Gain** `ViscFF` = `1.5` ← Demux/2 (w_d).
16. **Gain** `CoulNorm` = `20` ← Demux/2; **Trigonometric Function** `TanhWd`
    (`tanh`); **Gain** `CoulFF` = `2.5`. Chain them.
17. **Sum** `FFSum`, signs `++++`: GravFF → 1, InertFF → 2, ViscFF → 3, CoulFF → 4.
18. **Sum** `OutTauSum`, signs `++`: PIDSum → 1, FFSum → 2.

### B.4 — Motor interface

19. **Gain** `ToMotor` = `0.016146` (= 1/(70×0.8847)) ← OutTauSum.
20. **Discontinuities → Saturation** `CurLim`, Upper `3.039`, Lower `-3.039` ← ToMotor.
21. **Transfer Fcn** `Driver`, Numerator `[1]`, Denominator `[0.004 1]` ← CurLim.

### B.5 — Plant + feedback

22. **Gain** `ToOutput` = `61.9315` (= 70×0.8847) ← Driver.
23. **Sum** `PlantSum`, signs `+---` ← ToOutput/1.
24. **Gain** `InvJ` = `0.047326` (= 1/21.1302) ← PlantSum.
25. **Integrator** `W` (IC 0) ← InvJ; **Integrator** `TH` (IC 0) ← W.
26. Feedback/th wiring: TH → ErrSum/−, CosTh, MuxAngle/2 (step B.6), TW_th.
    GravFF ← CosTh; GravFF → PlantSum/2.
27. W → VelErrSum/−; W → **Gain** `ViscPlant` = `1.5` → PlantSum/3;
    W → **Gain** `CoulNormP` = `50` → **Trig** `TanhW` (`tanh`) →
    **Gain** `CoulPlant` = `2.5` → PlantSum/4; W → EMF (step B.6).

### B.6 — Monitor + scopes + logging

28. Driver → **Gain** `ToCurrent` = `13.1623` (= 1/0.075974) → To Workspace `i_log`
    (SaveFormat Array) and → **Gain** `Rdrop` = `0.15` → **Sum** `VoltSum` (`++`)/1.
29. W → **Gain** `EMF` = `5.31818` (= 0.075974×70) → VoltSum/2 → To Workspace `v_log`.
30. **Mux** `MuxAngle` (2 in): Demux/1 → 1, TH → 2 → **Scope** `ScopeAngle`.
31. **Mux** `MuxTau` (3 in): Driver → 1, Tpeak_pos → 2, Tpeak_neg → 3 →
    **Scope** `ScopeTorque`.
32. **To Workspace** blocks (SaveFormat **Array**): `th_d_log` ← Demux/1,
    `th_log` ← TH, `tau_log` ← Driver.

### B.7 — Run + accept

33. Save, press **Run**. Open scopes; run the 4-line check from Option A step 4.
    Pass criteria are identical to the `.m` sim (overshoot < 2°, etc.).
    If a wire is missing, Simulink tells you the exact block — fix and re-run.
