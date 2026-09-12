"""
Independent verification mirror for gate_gearbox_pid_sim.m
-----------------------------------------------------------
Pure-numpy replica of the EXACT algorithm that will ship in the MATLAB file.
Purpose: prove all physics, sizing, gains and metrics BEFORE delivering MATLAB.
If this script prints ALL CHECKS PASSED, the MATLAB transcription is approved.

Conventions (identical in MATLAB):
  theta = 0      -> CLOSED (arm horizontal, max gravity torque)
  theta = +90deg -> OPEN (arm vertical, zero gravity torque)
  All angles in radians internally, degrees only for display.
"""
import math
import numpy as np

g = 9.81

# =====================================================================
# 1. GEAR DATA (user BOM, mm)  [pitch_od, root_od, bore, face]
# =====================================================================
GEARS = {
    "P1": dict(stage=1, teeth=17, module=3, pitch=51.0,  od=57.0,  root=43.5,  bore=28.0, face=25.0),
    "G1": dict(stage=1, teeth=68, module=3, pitch=204.0, od=210.0, root=196.5, bore=20.0, face=25.0),
    "P2": dict(stage=2, teeth=16, module=4, pitch=64.0,  od=72.0,  root=54.0,  bore=20.0, face=32.0),
    "G2": dict(stage=2, teeth=70, module=4, pitch=280.0, od=288.0, root=270.0, bore=30.0, face=32.0),
    "P3": dict(stage=3, teeth=16, module=5, pitch=80.0,  od=90.0,  root=67.5,  bore=30.0, face=40.0),
    "G3": dict(stage=3, teeth=64, module=5, pitch=320.0, od=330.0, root=307.5, bore=90.0, face=40.0),
}
RHO_STEEL = 7850.0

def gear_mass_inertia(row):
    """Hollow-cylinder approximation, outer radius = PITCH radius (teeth cancel)."""
    Ro = (row["pitch"] / 1000.0) / 2.0
    Ri = (row["bore"] / 1000.0) / 2.0
    w = row["face"] / 1000.0
    m = RHO_STEEL * math.pi * (Ro**2 - Ri**2) * w
    J = 0.5 * m * (Ro**2 + Ri**2)
    return m, J

print("=" * 72)
print("GEAR GEOMETRY CROSS-CHECK (standard full-depth teeth: OD=m(z+2), Root=m(z-2.5))")
print("=" * 72)
for k, r in GEARS.items():
    od_t = r["module"] * (r["teeth"] + 2)
    rt_t = r["module"] * (r["teeth"] - 2.5)
    p_t = r["module"] * r["teeth"]
    ok = (abs(od_t - r["od"]) < 1e-9 and abs(rt_t - r["root"]) < 1e-9 and abs(p_t - r["pitch"]) < 1e-9)
    print(f"  {k}: pitch {r['pitch']:6.1f} (theory {p_t:6.1f})  "
          f"OD {r['od']:6.1f} (th {od_t:6.1f})  root {r['root']:6.1f} (th {rt_t:6.1f})  -> {'OK' if ok else 'MISMATCH!!'}")
    assert ok, f"gear geometry mismatch on {k}"

print()
print("=" * 72)
print("GEAR MASS / INERTIA (hollow cylinder @ pitch radius, steel 7850 kg/m^3)")
print("=" * 72)
JM = {}
mass_tot = 0.0
for k, r in GEARS.items():
    m, J = gear_mass_inertia(r)
    JM[k] = J
    mass_tot += m
    print(f"  {k}:  mass = {m:7.3f} kg   J = {J:.6f} kg m^2")
print(f"  TOTAL gear mass = {mass_tot:.2f} kg")

# Ratios
i1 = GEARS["G1"]["teeth"] / GEARS["P1"]["teeth"]
i2 = GEARS["G2"]["teeth"] / GEARS["P2"]["teeth"]
i3 = GEARS["G3"]["teeth"] / GEARS["P3"]["teeth"]
N = i1 * i2 * i3
print()
print(f"Ratios: i1={i1:.4f}  i2={i2:.4f}  i3={i3:.4f}  N_total={N:.4f}")
assert abs(i1 - 4.0) < 1e-12 and abs(i2 - 4.375) < 1e-12 and abs(i3 - 4.0) < 1e-12 and abs(N - 70.0) < 1e-12

# Center distances (SolidWorks verification values)
cd1 = GEARS["P1"]["module"] * (GEARS["P1"]["teeth"] + GEARS["G1"]["teeth"]) / 2
cd2 = GEARS["P2"]["module"] * (GEARS["P2"]["teeth"] + GEARS["G2"]["teeth"]) / 2
cd3 = GEARS["P3"]["module"] * (GEARS["P3"]["teeth"] + GEARS["G3"]["teeth"]) / 2
print(f"Center distances (check in SolidWorks sketch): {cd1:.1f} / {cd2:.1f} / {cd3:.1f} mm")
assert abs(cd1 - 127.5) < 1e-9 and abs(cd2 - 172.0) < 1e-9 and abs(cd3 - 200.0) < 1e-9

# =====================================================================
# 2. ARM + LOAD
# =====================================================================
m_arm, L_arm, Lc = 13.5, 1.0, 0.5   # uniform-rod assumption (documented)
J_arm = (1.0 / 3.0) * m_arm * L_arm**2
T_grav_max = m_arm * g * Lc
print()
print(f"Arm: m={m_arm} kg L={L_arm} m Lc={Lc} m -> J_arm={J_arm:.4f} kg m^2, T_grav_max={T_grav_max:.2f} N m")

# =====================================================================
# 3. EFFICIENCY + REFLECTED INERTIA (to OUTPUT shaft)
# =====================================================================
eta = 0.96 ** 3
J_rotor = 0.0006
J_shaftA = JM["G1"] + JM["P2"]      # spins i2*i3 = 17.5x output
J_shaftB = JM["G2"] + JM["P3"]      # spins i3 = 4x output
J_mshaft = JM["P1"] + J_rotor       # spins N = 70x output
J_eff = J_arm + JM["G3"] + J_shaftB * i3**2 + J_shaftA * (i2 * i3)**2 + J_mshaft * N**2
print(f"eta_total = 0.96^3 = {eta:.5f}")
print(f"J_eff @ output = {J_eff:.4f} kg m^2  (arm {J_arm:.3f} + G3 {JM['G3']:.4f} + "
      f"shaftB {J_shaftB*i3**2:.4f} + shaftA {J_shaftA*(i2*i3)**2:.4f} + motor {J_mshaft*N**2:.4f})")
# Independent hand-check (separately computed): must match ~21.13
assert abs(J_eff - 21.13) < 0.5, f"J_eff {J_eff} disagrees with hand calc!"

# =====================================================================
# 4. MOTOR (primary: 24 V 500 W brushed DC, MY1020 class)
# =====================================================================
V_sup = 24.0
P_rated = 500.0
n_rated = 2500.0
w_rated = n_rated * 2 * math.pi / 60.0
T_rated = P_rated / w_rated
I_rated = 27.4
R_est, L_est = 0.15, 0.00035
Ke = (V_sup - I_rated * R_est) / w_rated
Kt = Ke
I_peak = 40.0
T_peak_m = Kt * I_peak
T_hold_m = T_grav_max / (N * eta)
print()
print(f"Motor: {V_sup:.0f} V {P_rated:.0f} W, n_rated={n_rated:.0f} rpm, T_rated={T_rated:.3f} N m")
print(f"  R={R_est} ohm(est) L={L_est*1000} mH(est) Ke=Kt={Ke:.6f} (SI)  J_rotor={J_rotor} (est)")
print(f"  Holding torque needed @ motor = {T_hold_m:.3f} N m = {100*T_hold_m/T_rated:.1f}% of rated  "
      f"(peak avail {T_peak_m:.2f} N m)")
assert T_hold_m / T_rated < 0.70, "motor too small for continuous holding!"
assert Kt * I_rated > T_rated, "Kt inconsistent with nameplate!"

# =====================================================================
# 5. MOTION PROFILE (trapezoidal, analytic)
# =====================================================================
MOVE = math.pi / 2
T_MOVE, T_ACC = 6.0, 1.5
V_PK = MOVE / (T_MOVE - T_ACC)
A_PK = V_PK / T_ACC
print()
print(f"Profile: 90 deg in {T_MOVE} s, t_acc={T_ACC} s -> v_pk={V_PK:.4f} rad/s ({math.degrees(V_PK):.2f} deg/s), "
      f"a_pk={A_PK:.4f} rad/s^2")
# Timeline: dwell 1 | open 6 | dwell 2 | close 6 | dwell 1  (16 s)
T0_OPEN, T1_OPEN = 1.0, 1.0 + T_MOVE
T0_CLOSE, T1_CLOSE = 9.0, 9.0 + T_MOVE
T_END = 16.0

def trap(s):
    """Scalar trapezoid ref (pos, vel, acc) for move progress s in [0,1]."""
    D, T, ta = MOVE, T_MOVE, T_ACC
    v, a = V_PK, A_PK
    t = s * T
    if t <= 0:   return 0.0, 0.0, 0.0
    if t < ta:   return 0.5*a*t*t, a*t, a
    if t < T-ta: return 0.5*a*ta*ta + v*(t-ta), v, 0.0
    if t < T:
        td = T - t
        return D - 0.5*a*td*td, v - a*(t-(T-ta)), -a
    return D, 0.0, 0.0

def ref_at(t):
    if t < T0_OPEN:  return 0.0, 0.0, 0.0
    if t < T1_OPEN:
        p, v, a = trap((t - T0_OPEN) / T_MOVE); return p, v, a
    if t < T0_CLOSE: return MOVE, 0.0, 0.0
    if t < T1_CLOSE:
        p, v, a = trap((t - T0_CLOSE) / T_MOVE); return MOVE - p, -v, -a
    return 0.0, 0.0, 0.0

# profile self-test: continuity + endpoint correctness + peak values
ts = np.linspace(0, T_END, 16001)
P = np.array([ref_at(t)[0] for t in ts])
V = np.array([ref_at(t)[1] for t in ts])
assert abs(P[0]) < 1e-12 and abs(P[-1]) < 1e-9
assert abs(max(P) - MOVE) < 1e-9 and min(P) > -1e-9
assert abs(max(abs(V)) - V_PK) < 1e-9
assert max(abs(np.diff(P) / (ts[1]-ts[0])) ) < V_PK * 1.01  # numerical vel matches
print("Profile self-test: endpoints, peaks, continuity -> OK")

# =====================================================================
# 6. CONTROLLER GAINS (3rd-order pole placement on J_eff)
# =====================================================================
WN, ZETA = 8.0, 1.0
P3 = WN / 3.0
Kp = J_eff * (WN**2 + 2*ZETA*WN*P3)
Kd = J_eff * (2*ZETA*WN + P3)
Ki = J_eff * (WN**2 * P3)
LAM_D = 2*math.pi*30.0       # D-term filter bandwidth
TAU_DRV = 0.004              # driver current-loop lag
INT_MAX = 25.0               # integrator authority (N m @ output)
B_VISC, T_COUL = 1.5, 2.5    # plant friction (est)
print()
print(f"Gains (pole place wn={WN}, zeta={ZETA}, p3={P3:.3f}): Kp={Kp:.1f} Ki={Ki:.1f} Kd={Kd:.1f}")
# hand-check
assert abs(Kp - 2253.7) < 60 and abs(Ki - 3606.0) < 120 and abs(Kd - 394.4) < 12

# =====================================================================
# 7. SIMULATION (fixed-step RK4 @ 1 kHz, full state)
#    x = [th, w, tau_drv, int_e, ed_f]
# =====================================================================
DT = 0.001
def ctrl_out(th, w, int_e, ed_f, t):
    th_d, w_d, a_d = ref_at(t)
    e, ed_raw = th_d - th, w_d - w
    ed = ed_f
    tau_pid_unsat = Kp*e + Ki*int_e + Kd*ed
    ff = m_arm*g*Lc*math.cos(th) + J_eff*a_d + B_VISC*w_d + T_COUL*math.tanh(w_d/0.05)
    tau_out_unsat = tau_pid_unsat + ff
    tau_m_cmd = tau_out_unsat / (N*eta)
    sat = max(-T_peak_m, min(T_peak_m, tau_m_cmd))
    return e, ed_raw, tau_pid_unsat, ff, tau_out_unsat, tau_m_cmd, sat, th_d, w_d, a_d

# Plant parameters (nominally = model; robustness run detunes these)
PLANT_NOM = dict(m=m_arm, Lc=Lc, J=J_eff, b=B_VISC, tc=T_COUL)
PLANT_WORST = dict(m=15.5, Lc=0.55, J=J_eff*1.2, b=B_VISC*2.0, tc=T_COUL*2.0)

def make_xdot(P):
    def xdot(x, t):
        th, w, tau_drv, int_e, ed_f = x
        e, ed_raw, _, _, _, tau_m_cmd, sat, _, _, _ = ctrl_out(th, w, int_e, ed_f, t)
        frozen = (tau_m_cmd > T_peak_m and e > 0) or (tau_m_cmd < -T_peak_m and e < 0)
        int_dot = 0.0 if frozen else e
        if Ki*int_e > INT_MAX and int_dot > 0: int_dot = 0.0
        if Ki*int_e < -INT_MAX and int_dot < 0: int_dot = 0.0
        tau_out = tau_drv * N * eta
        w_dot = (tau_out - P["m"]*g*P["Lc"]*math.cos(th) - P["b"]*w
                 - P["tc"]*math.tanh(w/0.02)) / P["J"]
        return np.array([w, w_dot, (sat - tau_drv)/TAU_DRV, int_dot, LAM_D*(ed_raw - ed_f)])
    return xdot

def run_sim(P):
    xdot = make_xdot(P)
    n = int(T_END/DT) + 1
    X = np.zeros((n, 5)); T = np.zeros(n)
    REF = np.zeros((n, 3)); TAU_M = np.zeros(n); CUR = np.zeros(n); VOLT = np.zeros(n)
    for k in range(n-1):
        t = k*DT
        T[k] = t
        x = X[k]
        k1 = xdot(x, t); k2 = xdot(x + 0.5*DT*k1, t + 0.5*DT)
        k3 = xdot(x + 0.5*DT*k2, t + 0.5*DT); k4 = xdot(x + DT*k3, t + DT)
        X[k+1] = x + DT*(k1 + 2*k2 + 2*k3 + k4)/6
    T[n-1] = T_END
    for k in range(n):
        th, w, tau_drv, int_e, ed_f = X[k]
        _, _, _, _, _, _, _, th_d, w_d, a_d = ctrl_out(th, w, int_e, ed_f, T[k])
        REF[k] = [th_d, w_d, a_d]
        TAU_M[k] = tau_drv
        CUR[k] = tau_drv / Kt
        VOLT[k] = CUR[k]*R_est + Ke*N*w
    return T, X, REF, TAU_M, CUR, VOLT

def move_metrics(T, X, REF, t0, t1, target, label):
    TH = X[:, 0]
    m = (T >= t0) & (T <= t1 + 2.0)
    me = (T >= t0) & (T <= t1)
    err = REF[m, 0] - TH[m]
    over = max(0.0, (max(TH[m]) - target)) if target > 0 else max(0.0, (target - min(TH[m])))
    band = math.radians(0.5)
    outs = T[m][np.abs(err) > band]
    settle = (max(outs) - t0) if len(outs) else 0.0
    rms = float(np.sqrt(np.mean((REF[me, 0]-TH[me])**2)))
    mx = float(max(abs(REF[me, 0]-TH[me])))
    print(f"  {label}: overshoot={math.degrees(over):.3f} deg  settle(0.5deg)={settle:.2f} s  "
          f"RMS track err={math.degrees(rms):.3f} deg  max err={math.degrees(mx):.3f} deg")
    return over, settle, rms, mx

def summarize(T, X, REF, TAU_M, CUR, VOLT, title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)
    TH = X[:, 0]; ERR = REF[:, 0] - TH
    o1, s1, r1, m1 = move_metrics(T, X, REF, T0_OPEN, T1_OPEN, MOVE, "OPEN ")
    o2, s2, r2, m2 = move_metrics(T, X, REF, T0_CLOSE, T1_CLOSE, 0.0, "CLOSE")
    steady = float(np.mean(np.abs(ERR[T >= T_END-1.0])))
    pk_tq, pk_i, pk_v = max(abs(TAU_M)), max(abs(CUR)), max(abs(VOLT))
    print(f"  steady-state err (last 1 s) = {math.degrees(steady):.3f} deg")
    print(f"  peak motor torque = {pk_tq:.3f} N m ({100*pk_tq/T_peak_m:.1f}% of driver limit)")
    print(f"  peak current      = {pk_i:.2f} A (limit {I_peak:.0f} A)")
    print(f"  peak voltage      = {pk_v:.2f} V (supply {V_sup:.0f} V)")
    print(f"  final angle = {math.degrees(TH[-1]):.3f} deg (target 0)")
    return dict(o1=o1, s1=s1, r1=r1, m1=m1, o2=o2, s2=s2, r2=r2, m2=m2,
                steady=steady, pk_tq=pk_tq, pk_i=pk_i, pk_v=pk_v)

T, X, REF, TAU_M, CUR, VOLT = run_sim(PLANT_NOM)
res_nom = summarize(T, X, REF, TAU_M, CUR, VOLT, "CLOSED-LOOP RESULTS (nominal plant)")

Tw, Xw, REFw, TAU_Mw, CURw, VOLTw = run_sim(PLANT_WORST)
res_w = summarize(Tw, Xw, REFw, TAU_Mw, CURw, VOLTw,
                  "ROBUSTNESS RUN (plant: mass 15.5kg, Lc 0.55, J +20%, friction 2x; controller nominal)")

def build_checks(r, tag, relaxed=False):
    ov_lim = 2.0
    st_lim = 0.3 if not relaxed else 0.5
    return [
        (f"[{tag}] overshoot OPEN  <= 2.0 deg", math.degrees(r["o1"]) <= ov_lim),
        (f"[{tag}] overshoot CLOSE <= 2.0 deg", math.degrees(r["o2"]) <= ov_lim),
        (f"[{tag}] settle OPEN  <= move+2 s", r["s1"] <= T_MOVE + 2.0),
        (f"[{tag}] settle CLOSE <= move+2 s", r["s2"] <= T_MOVE + 2.0),
        (f"[{tag}] steady err <= {st_lim} deg", math.degrees(r["steady"]) <= st_lim),
        (f"[{tag}] peak torque < 90% limit", r["pk_tq"] < 0.9*T_peak_m),
        (f"[{tag}] peak current < limit", r["pk_i"] < I_peak),
        (f"[{tag}] peak voltage headroom (24V)", r["pk_v"] < 20.0),
        (f"[{tag}] RMS track err < 1.0 deg", max(math.degrees(r["r1"]), math.degrees(r["r2"])) < 1.0),
    ]

print()
print("=" * 72)
print("ACCEPTANCE CHECKS")
print("=" * 72)
checks = build_checks(res_nom, "nominal") + build_checks(res_w, "worst-case", relaxed=True)
allok = True
for name, ok in checks:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    allok &= ok
print("=" * 72)
print("ALL CHECKS PASSED - MATLAB transcription approved" if allok else "FAILURES PRESENT - DO NOT SHIP")
print("=" * 72)
assert allok
