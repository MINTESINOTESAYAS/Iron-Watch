# Verification — what was checked, how, and how to re-run it

The deliverable in `matlab/` is plain MATLAB/Octave with **no toolbox
dependencies**, so it self-verifies on your PC (`gate_gearbox_pid_sim.m`
prints `RESULT: ALL CHECKS PASSED` only if every acceptance test passes).
This folder holds the independent checks performed **before delivery**.

## Files

| File | What it is |
|---|---|
| `replica_sim.py` | Independent pure-Python (numpy) mirror of the exact algorithm — written separately from the MATLAB, used to prove the physics/control design before transcription |
| `replica_output.txt` | Raw console output of `replica_sim.py` (design-approval run) |
| `expected_results.txt` | **Exact expected console output of `matlab/gate_gearbox_pid_sim.m`** — same numbers as the replica, formatted with the MATLAB file's own `fprintf` format strings, so you can diff your MATLAB/Octave run line-by-line |
| `matlab_static_check.py` | Automated static analysis of the three `.m` files (see below) |

## Checks performed (2026-09-13)

1. **Independent numeric replica** — `replica_sim.py` re-implements the model
   (gear inertias → reflected inertia, trapezoidal profile, PID + feedforward
   with anti-windup, driver lag, RK4 @ 1 kHz, both plants) and asserts
   hand-computed values (`J_eff`, gains, ratios, holding torque) before
   simulating. Result: **ALL CHECKS PASSED** (Python 3.11, numpy 2.4.6).
   Re-run: `python3 verification/replica_sim.py`

2. **Static analysis of the actual `.m` files** — bracket/end balance, every
   `P.*` field read is assigned in `gate_params.m`, every local function
   defined and used, `fprintf` format-string arity (30 + 3 calls), and the
   full Simulink wiring graph (56 blocks / 75 lines: every inport driven
   exactly once, all port numbers valid, Sum/Mux/Demux widths consistent).
   Result: **PASSED**.
   Re-run: `python3 verification/matlab_static_check.py`

3. **MATLAB grammar parse** of all three `.m` files with an independent
   MATLAB parser (parso/smop-based `matlab2python`). Both core files
   (`gate_params.m`, `gate_gearbox_pid_sim.m`) parse with zero errors.
   `build_gate_simulink.m` parses cleanly once 5 lines are masked; each of
   those 5 lines was individually confirmed **valid MATLAB** that the old
   smop grammar simply does not model:
   - `clearvars -except gate_prof;` (standard MATLAB command)
   - `L = { % {from, to}` (inline comment inside a cell-array opening — legal)
   - `    };` (cell close; cascades from the previous line)
   - the two-line `fprintf([...  ...])` string concatenation with `...`
     continuation (legal MATLAB; the same construct parses fine elsewhere)

4. **Manual line-by-line semantic audit** of `gate_gearbox_pid_sim.m`
   against the approved replica: identical state vector
   `[theta, omega, tau_drv, int_e, ed_filt]`, identical profile equations,
   RK4 loop, controller + feedforward + anti-windup logic, metric
   definitions and acceptance thresholds.

> Note: the `done in 3.8 s.` line in `expected_results.txt` is machine speed
> dependent — it will differ on your PC. Everything else must match to the
> printed decimals.

> Note: the delivery sandbox could not install GNU Octave (all package
> mirrors blocked), so checks 1–4 were used instead of a live Octave run.
> On your PC, `gate_gearbox_pid_sim.m` verifies itself — if the console ends
> with `RESULT: ALL CHECKS PASSED` and matches `expected_results.txt`, the
> deliverable is confirmed on your machine.
