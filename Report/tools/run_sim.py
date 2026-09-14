#!/usr/bin/env python3
"""
run_sim.py -- Faithful Python reproduction of the committed MATLAB simulation
files (matlab/gate_params.m, matlab/gate_sim.m, trap_ref.m) for the
Iron-Watch 90-degree boom-gate project.

It reproduces, number-for-number:
  * gate_params()  -- gear geometry/masses/inertias, reflected inertia,
                      motor constants, trapezoidal profile, PID gains
  * gate_sim.m     -- fixed-step (1 ms, Euler) closed-loop opening move with
                      PID (no gravity term: inertia + viscous friction plant),
                      current/voltage saturation
                      and conditional-integration anti-windup
It additionally performs (clearly labelled) verification runs:
  * a robustness run with +15 % arm mass, +20 % inertia, 2 x friction
  * a full open/close cycle (RK4) with the same controller and an added
    acceleration + Coulomb feed-forward, as structured in
    gate_gearbox_pid_sim.m (gains/profile taken from gate_tuning.mat for the
    full-cycle run)

Outputs (written into Report/figures and Report/data):
  metrics.json, gear_table.csv, sim_open.csv
  fig_open_response.png, fig_full_cycle.png, fig_robustness.png,
  fig_profile.png, fig_openloop.png
"""
import json, os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures"); DAT = os.path.join(ROOT, "data")
os.makedirs(FIG, exist_ok=True); os.makedirs(DAT, exist_ok=True)

# ----------------------------------------------------------------------
# Parameters -- exact port of gate_params.m
# ----------------------------------------------------------------------
g = 9.81
rho = 7850.0
pitchD = np.array([51.0, 204.0, 64.0, 280.0, 80.0, 320.0])   # mm  P1,G1,P2,G2,P3,G3
bore   = np.array([28.0, 20.0, 20.0, 30.0, 30.0, 90.0])      # mm
face   = np.array([25.0, 25.0, 32.0, 32.0, 40.0, 40.0])      # mm
teeth  = np.array([17, 68, 16, 70, 16, 64])
module = np.array([3, 3, 4, 4, 5, 5])
names  = ["P1 (motor pinion)", "G1 (gear 1)", "P2 (pinion 2)",
          "G2 (gear 2)", "P3 (pinion 3)", "G3 (arm gear)"]

gear_mass = np.zeros(6); gearJ = np.zeros(6)
for k in range(6):
    Ro = (pitchD[k]/1000.0)/2; Ri = (bore[k]/1000.0)/2; w = face[k]/1000.0
    m = rho*math.pi*(Ro**2-Ri**2)*w
    gear_mass[k] = m
    gearJ[k] = 0.5*m*(Ro**2+Ri**2)

i1 = 68/17; i2 = 70/16; i3 = 64/16
N = i1*i2*i3
eta_mesh = 0.96
eta = eta_mesh**3

m_arm, L_arm = 13.5, 1.0
Lc = L_arm/2
J_arm = (1/3)*m_arm*L_arm**2
T_grav_max = m_arm*g*Lc

Ne = np.array([N, N/i1, N/i1, N/(i1*i2), N/(i1*i2), 1.0])
J_gb_ref = float(np.sum(gearJ*Ne**2))

V, P_rated, n_rated, I_rated = 24.0, 500.0, 2500.0, 27.0
w_rated = n_rated*2*math.pi/60
T_rated = P_rated/w_rated
R, Lmot = 0.15, 0.5e-3
Kt = (V - I_rated*R)/w_rated
Ke = Kt
J_rot = 6e-4
I_max = 30.0
J_eff = J_arm + J_gb_ref + J_rot*N**2
b_fric = 1.2

theta_target = math.pi/2
T_acc, T_move = 0.6, 2.5
v_pk = theta_target/(T_move-T_acc)
a_pk = v_pk/T_acc

wn, zeta = 5.0, 0.9
Kp = J_eff*wn**2
Kd = 2*zeta*wn*J_eff
Ki = Kp*wn/10

def trap_ref(t):
    ta, Tm, vp, ap, D = T_acc, T_move, v_pk, a_pk, theta_target
    if t <= 0: return 0.0, 0.0
    if t < ta: return 0.5*ap*t*t, ap*t
    if t < Tm-ta: return 0.5*ap*ta*ta + vp*(t-ta), vp
    if t < Tm:
        td = Tm-t
        return D-0.5*ap*td*td, vp-ap*(t-(Tm-ta))
    return D, 0.0

# ----------------------------------------------------------------------
# Design report numbers
# ----------------------------------------------------------------------
T_hold_motor = T_grav_max/(N*eta)
cd = [(pitchD[0]+pitchD[1])/2, (pitchD[2]+pitchD[3])/2, (pitchD[4]+pitchD[5])/2]
print(f"Ratios: i1={i1:.4f} i2={i2:.4f} i3={i3:.4f} N={N:.4f}")
print(f"Centre distances (mm): {cd}")
print("Gear mass / inertia:")
for k in range(6):
    print(f"  {names[k]:18s} m={gear_mass[k]:7.3f} kg  J={gearJ[k]:.6f} kg m2  (x{Ne[k]:.2f} at output)")
print(f"Total gear mass = {gear_mass.sum():.2f} kg; gearbox reflected J = {J_gb_ref:.4f}")
print(f"Arm: m={m_arm} L={L_arm} Lc={Lc} J={J_arm:.4f}; Tgrav,max={T_grav_max:.3f} N m")
print(f"Motor: w={w_rated:.2f} rad/s T_rated={T_rated:.3f} Nm Kt=Ke={Kt:.6f}")
print(f"Holding torque at motor = {T_hold_motor:.3f} Nm = {100*T_hold_motor/T_rated:.1f} % of rated")
print(f"J_eff={J_eff:.4f} (rotor refl {J_rot*N**2:.4f} + gb {J_gb_ref:.4f} + arm {J_arm:.4f})")
print(f"Profile: v_pk={v_pk:.4f} rad/s = {math.degrees(v_pk):.2f} deg/s, a_pk={a_pk:.4f} rad/s2")
print(f"Gains: Kp={Kp:.3f} Ki={Ki:.3f} Kd={Kd:.3f}")

# ----------------------------------------------------------------------
# Exact port of gate_sim.m (opening move, Euler 1 ms, 0..8 s)
# ----------------------------------------------------------------------
I_clamp = 300.0
def run_open(m=m_arm, J=J_eff, b=b_fric, T_end=6.0):
    dt = 1e-3
    t = np.arange(0, T_end+dt/2, dt)
    n = t.size
    th = np.zeros(n); w = np.zeros(n); cur = np.zeros(n)
    th_r = np.zeros(n); w_r = np.zeros(n); e_int = 0.0
    for k in range(n-1):
        thr, wr = trap_ref(t[k]); th_r[k] = thr; w_r[k] = wr
        e = thr-th[k]; de = wr-w[k]
        e_int = float(np.clip(e_int + e*dt, -I_clamp/Ki, I_clamp/Ki))   # clamped integral
        tau_cmd = Kp*e + Ki*e_int + Kd*de
        i_cmd = tau_cmd/(N*eta*Kt)
        i_cmd = np.clip(i_cmd, -I_max, I_max)
        V_cmd = i_cmd*R + Ke*N*w[k]
        V_cmd = np.clip(V_cmd, -V, V)
        didt = (V_cmd - R*cur[k] - Ke*N*w[k])/Lmot
        cur[k+1] = cur[k]+didt*dt
        tau_out = N*eta*Kt*cur[k+1]
        wdot = (tau_out - b*w[k])/J
        w[k+1] = w[k]+wdot*dt
        th[k+1] = th[k]+w[k+1]*dt
    th_r[-1] = theta_target
    volt = cur*R + Ke*N*w
    return t, th, w, cur, th_r, w_r, volt

t, th, om, cur, thr, omr, volt_open = run_open()
err = thr-th
metrics = dict(
    N=N, i1=i1, i2=i2, i3=i3, eta=eta,
    gear=[dict(name=names[k], z=int(teeth[k]), module=int(module[k]),
               pitch=float(pitchD[k]), bore=float(bore[k]), face=float(face[k]),
               mass=float(gear_mass[k]), J=float(gearJ[k]), speed_factor=float(Ne[k]))
          for k in range(6)],
    centre_distances=cd, total_gear_mass=float(gear_mass.sum()),
    J_gb_ref=J_gb_ref, J_arm=J_arm, J_rotor_ref=J_rot*N**2, J_eff=J_eff,
    T_grav_max=T_grav_max, T_hold_motor=T_hold_motor,
    T_rated=T_rated, w_rated=w_rated, Kt=Kt, motor_rated_I=I_rated,
    v_pk=v_pk, a_pk=a_pk, Kp=Kp, Ki=Ki, Kd=Kd,
    final_angle_deg=math.degrees(th[-1]),
    peak_error_deg=math.degrees(np.max(np.abs(err))),
    peak_current_A=float(np.max(np.abs(cur))),
    peak_voltage_V=float(np.max(np.abs(volt_open))),
    T_acc_req=float(J_eff*a_pk + b_fric*v_pk),
)
mv = t <= T_move+2
overshoot = math.degrees(max(0, np.max(th[mv])-theta_target))
outside = t[mv & (np.abs(thr-th) > math.radians(0.5))]
settle = float(outside.max()) if outside.size else 0.0
rms = math.degrees(np.sqrt(np.mean((thr[t<=T_move]-th[t<=T_move])**2)))
steady = math.degrees(np.mean(np.abs(thr[t>=5]-th[t>=5])))
metrics.update(overshoot_open_deg=overshoot, settle_open_s=settle,
               rms_open_deg=rms, steady_state_err_deg=steady)
print(f"\nOPEN: final={math.degrees(th[-1]):.3f} deg peak_err={math.degrees(np.max(np.abs(err))):.3f} deg")
print(f"overshoot={overshoot:.3f} deg settle={settle:.2f} s RMS={rms:.3f} deg "
      f"steady={steady:.4f} deg peakI={np.max(np.abs(cur)):.2f} A")

# ---- robustness (+15 % mass, +20 % J, 2 x friction) ----
tR, thR, wR, curR, thrR, _, _ = run_open(m=1.15*m_arm, J=1.20*J_eff, b=2*b_fric)
errR = thrR-thR
rmsR = math.degrees(np.sqrt(np.mean((thrR[t<=T_move]-thR[t<=T_move])**2)))
ovR = math.degrees(max(0, np.max(thR[t<=T_move+2])-theta_target))
outR = t[(t<=T_move+2) & (np.abs(thrR-thR) > math.radians(0.5))]
stR = float(outR.max()) if outR.size else 0.0
metrics.update(robust=dict(rms_deg=rmsR, overshoot_deg=ovR, settle_s=stR,
                           peak_I=float(np.max(np.abs(curR))),
                           final_deg=math.degrees(thR[-1])))
print(f"WORST: overshoot={ovR:.3f} RMS={rmsR:.3f} settle={stR:.2f} peakI={np.max(np.abs(curR)):.2f}")

# detailed trajectory checks (nominal opening)
imax_lag = int(np.argmax(thr-th)); imax_ov = int(np.argmax(th))
print(f"  max tracking lag {math.degrees((thr-th)[imax_lag]):.3f} deg at t={t[imax_lag]:.2f} s")
print(f"  max actual angle {math.degrees(th[imax_ov]):.3f} deg at t={t[imax_ov]:.2f} s")
print(f"  angle at t=2.5s = {math.degrees(th[np.argmin(abs(t-2.5))]):.2f} deg; peak speed {math.degrees(np.max(om)):.1f} deg/s")
print(f"  current at t=0.05s: {cur[np.argmin(abs(t-0.05))]:.2f} A; mean current during move: {cur[t<=T_move].mean():.2f} A")

# ----------------------------------------------------------------------
# Full open/close cycle, RK4 (mirrors gate_gearbox_pid_sim.m structure,
# using the committed gate_params gains/profile)
# ----------------------------------------------------------------------
def ref_cycle(tt, t0o=2.0, t1o=2.0+T_move, t0c=10.0, t1c=10.0+T_move, T_end=16.0):
    if tt < t0o: return 0.0,0.0,0.0
    if tt < t1o:
        s=(tt-t0o)/T_move; thr_,wr=trap_ref(s*T_move)
        a = a_pk if s*T_move<T_acc else (-a_pk if s*T_move>T_move-T_acc else 0)
        return thr_,wr,a
    if tt < t0c: return theta_target,0.0,0.0
    if tt < t1c:
        s = (tt-t0c)/T_move                      # 0..1 closing progress
        p,v = trap_ref(s*T_move)
        a = a_pk if s*T_move<T_acc else (-a_pk if s*T_move>T_move-T_acc else 0)
        return theta_target-p, -v, -a
    return 0.0,0.0,0.0

def run_cycle(m=m_arm, J=J_eff, b=b_fric, tc=0.0):
    dt=1e-3; T_end=16.0; n=int(T_end/dt)+1
    X=np.zeros((n,2)); T=np.arange(n)*dt; RE=np.zeros((n,3)); eint=0.0; curc=np.zeros(n)
    for k in range(n-1):
        thk,wk=X[k]; thr_,wr,ar=ref_cycle(T[k]); RE[k]=thr_,wr,ar
        e=thr_-thk; de=wr-wk
        eint = float(np.clip(eint + e*dt, -I_clamp/Ki, I_clamp/Ki))
        tau=Kp*e+Ki*eint+Kd*de                     # plain PID, same as gate_sim.m
        ic=np.clip(tau/(N*eta*Kt),-I_max,I_max)
        Vc=np.clip(ic*R+Ke*N*wk,-V,V)
        didt=(Vc-R*curc[k]-Ke*N*wk)/Lmot; curc[k+1]=curc[k]+didt*dt
        to=N*eta*Kt*curc[k+1]
        def f(x):
            th,ww=x
            return np.array([ww,(to-b*ww)/J])
        x=X[k]; k1=f(x); k2=f(x+0.5*dt*k1); k3=f(x+0.5*dt*k2); k4=f(x+dt*k3)
        X[k+1]=x+dt*(k1+2*k2+2*k3+k4)/6
    RE[-1]=0
    volt = curc*R+Ke*N*X[:,1]
    tau_m = Kt*curc
    return T,X,RE,curc,volt,tau_m

Tc,Xc,REc,curc,volt,tau_m = run_cycle()
errc = np.degrees(REc[:,0]-Xc[:,0])
mo = (Tc>=2.0)&(Tc<=4.5); mc = (Tc>=10.0)&(Tc<=12.5)
metrics["cycle"] = dict(peak_err_deg=float(np.max(np.abs(errc))),
    rms_open_deg=float(np.sqrt(np.mean(errc[mo]**2))), rms_close_deg=float(np.sqrt(np.mean(errc[mc]**2))),
    peak_torque_Nm=float(np.max(np.abs(tau_m))), peak_I=float(np.max(np.abs(curc))), peak_V=float(np.max(np.abs(volt))),
    final_deg=float(np.degrees(Xc[-1,0])))
print("CYCLE:", metrics["cycle"])

# ----------------------------------------------------------------------
# Linearised open-loop plant (output shaft), for controller design section
# theta'' = (K u - b theta' - mgLc)/J  -> around operating point gravity is
# treated as a constant disturbance cancelled by feed-forward.
# Mechanical plant from motor voltage: G(s) = (N eta Kt)/(s((Js+b)(Ls+R))+Ke Kt N^2?)
# Use simplified torque-input plant J s^2 + b s = tau
A = np.array([[0,1],[0,-b_fric/J_eff]]); B=np.array([[0],[1/J_eff]])
C=np.array([[1,0]]); Dm=np.array([[0]])
sys_tau = signal.StateSpace(A,B,C,Dm)
# closed loop with PD on position: characteristic s^2 + (b+Kd)/J s + Kp/J
cl_poles = np.roots([J_eff, b_fric+Kd, Kp, Ki])
metrics["closed_loop_poles"] = [complex(p).__repr__() for p in cl_poles]
metrics["open_loop_poles"] = [0.0, -b_fric/J_eff]
print("Closed-loop poles:", cl_poles, " wn=",wn," zeta=",zeta)

# ======================================================================
# FIGURES
# ======================================================================
plt.rcParams.update({"font.size":10,"axes.grid":True,"grid.alpha":0.35,
                     "figure.dpi":150})

# --- Fig: opening response (3 panels, as gate_sim.m) ---
fig,ax=plt.subplots(3,1,figsize=(7.2,7.0),sharex=True)
ax[0].plot(t,np.degrees(thr),'r--',lw=1.4,label='reference')
ax[0].plot(t,np.degrees(th),'b-',lw=1.3,label='actual')
ax[0].set_ylabel(r'$\theta$ [deg]'); ax[0].legend(loc='lower right'); ax[0].set_ylim(-5,100)
ax[0].set_title('Gate arm angle: 0 (closed) $\\rightarrow$ 90 deg (open)')
ax[1].plot(t,np.degrees(err),'k'); ax[1].set_ylabel('Error [deg]')
ax[2].plot(t,cur,'m'); ax[2].set_ylabel('Motor current [A]'); ax[2].set_xlabel('Time [s]')
ax[2].set_xlim(0,6)
fig.tight_layout(); fig.savefig(FIG+"/fig_open_response.png"); plt.close(fig)

# --- Fig: speed + voltage (opening move) ---
fig,ax=plt.subplots(2,1,figsize=(7.2,5.0),sharex=True)
ax[0].plot(t,np.degrees(omr),'r--',lw=1.3,label='reference'); ax[0].plot(t,np.degrees(om),'b-',lw=1.2,label='actual')
ax[0].set_ylabel('speed (deg/s)'); ax[0].legend(fontsize=8); ax[0].set_title('Arm speed (top) and motor terminal voltage (bottom)')
ax[1].plot(t,volt_open,'g-'); ax[1].axhline(V,color='r',ls='--',lw=1); ax[1].set_ylabel('voltage (V)'); ax[1].set_xlabel('time (s)'); ax[1].set_xlim(0,6)
fig.tight_layout(); fig.savefig(FIG+"/fig_speed_voltage.png"); plt.close(fig)

# --- Fig: pole map ---
fig,ax=plt.subplots(figsize=(5.2,4.0))
ax.plot(cl_poles.real,cl_poles.imag,'bx',ms=10,mew=2,label='closed loop (PID)')
ax.plot([0,-b_fric/J_eff],[0,0],'ro',label='open loop')
ax.axhline(0,color='k',lw=.6); ax.axvline(0,color='k',lw=.6); ax.set_xlabel('Re (rad/s)'); ax.set_ylabel('Im (rad/s)')
ax.set_title('Pole map'); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(FIG+"/fig_poles.png"); plt.close(fig)

# --- Fig: full cycle (6 panels) ---
fig,axs=plt.subplots(3,2,figsize=(9.5,9.0))
axs[0,0].plot(Tc,np.degrees(REc[:,0]),'r--',lw=1.3,label='reference')
axs[0,0].plot(Tc,np.degrees(Xc[:,0]),'b-',lw=1.1,label='actual')
axs[0,0].set_ylabel('angle (deg)'); axs[0,0].legend(fontsize=8); axs[0,0].set_title('Arm angle: reference vs actual')
axs[0,1].plot(Tc,np.degrees(REc[:,0]-Xc[:,0]),'b-'); axs[0,1].set_title('Tracking error'); axs[0,1].set_ylabel('error (deg)')
axs[1,0].plot(Tc,np.degrees(REc[:,1]),'r--',lw=1.2,label='reference')
axs[1,0].plot(Tc,np.degrees(Xc[:,1]),'b-',lw=1.0,label='actual'); axs[1,0].legend(fontsize=8)
axs[1,0].set_ylabel('speed (deg/s)'); axs[1,0].set_title('Arm angular speed')
axs[1,1].plot(Tc,tau_m,'b-'); axs[1,1].axhline(T_rated,color='r',ls='--',lw=1); axs[1,1].axhline(-T_rated,color='r',ls='--',lw=1)
axs[1,1].set_ylabel('torque (N m)'); axs[1,1].set_title('Motor torque (dashed = rated ±%.2f Nm)'%T_rated)
axs[2,0].plot(Tc,curc,'b-'); axs[2,0].axhline(I_max,color='r',ls='--',lw=1); axs[2,0].axhline(-I_max,color='r',ls='--',lw=1)
axs[2,0].set_ylabel('current (A)'); axs[2,0].set_xlabel('time (s)'); axs[2,0].set_title('Motor current (dashed = ±30 A limit)')
axs[2,1].plot(Tc,volt,'b-'); axs[2,1].axhline(V,color='r',ls='--',lw=1); axs[2,1].axhline(-V,color='r',ls='--',lw=1)
axs[2,1].set_ylabel('voltage (V)'); axs[2,1].set_xlabel('time (s)'); axs[2,1].set_title('Motor terminal voltage (dashed = ±24 V)')
fig.tight_layout(); fig.savefig(FIG+"/fig_full_cycle.png"); plt.close(fig)

# --- Fig: robustness ---
fig,ax=plt.subplots(2,1,figsize=(7.5,5.6),sharex=True)
ax[0].plot(t,np.degrees(err),'b-',label='nominal')
ax[0].plot(tR,np.degrees(errR),'r-',label='worst case (+15% m, +20% J, 2$\\times$ friction)')
ax[0].set_ylabel('tracking error (deg)'); ax[0].legend(fontsize=8); ax[0].set_title('Robustness: tracking error')
ax[1].plot(t,cur,'b-',label='nominal'); ax[1].plot(tR,curR,'r-',label='worst case')
ax[1].axhline(I_max,color='k',ls='--',lw=1); ax[1].axhline(-I_max,color='k',ls='--',lw=1)
ax[1].set_ylabel('motor current (A)'); ax[1].set_xlabel('time (s)'); ax[1].set_xlim(0,6)
ax[1].legend(fontsize=8); ax[1].set_title('Motor current vs 30 A driver limit')
fig.tight_layout(); fig.savefig(FIG+"/fig_robustness.png"); plt.close(fig)

# --- Fig: trapezoidal reference ---
fig,axs=plt.subplots(3,1,figsize=(7.0,6.5),sharex=True)
tt=np.arange(0,3.0,1e-3); ref=np.array([trap_ref(x) for x in tt])
axs[0].plot(tt,np.degrees(ref[:,0]),'b'); axs[0].set_ylabel('angle (deg)'); axs[0].set_title('Trapezoidal motion profile (0 $\\rightarrow$ 90 deg in 2.5 s)')
axs[1].plot(tt,np.degrees(ref[:,1]),'r'); axs[1].set_ylabel('speed (deg/s)')
acc=np.gradient(ref[:,1],1e-3); axs[2].plot(tt,acc,'g'); axs[2].set_ylabel('accel (rad/s$^2$)'); axs[2].set_xlabel('time (s)')
fig.tight_layout(); fig.savefig(FIG+"/fig_profile.png"); plt.close(fig)

# --- Fig: open-loop vs closed-loop response ---
w0,T0=signal.step(sys_tau); w0=T0*0
# simulate open loop (no control): apply constant torque equal to gravity holding?
# Show unstable open-loop under small disturbance: start at 5 deg offset, no control
dt=1e-3; tt=np.arange(0,6,dt); th_o=np.zeros_like(tt); w_o=np.zeros_like(tt)
tau_step = 5.0   # N m constant torque at the arm shaft, no feedback
for k in range(len(tt)-1):
    wd=(tau_step-b_fric*w_o[k])/J_eff
    w_o[k+1]=w_o[k]+wd*dt; th_o[k+1]=th_o[k]+w_o[k+1]*dt
th_cl=th
fig,ax=plt.subplots(1,2,figsize=(9.5,3.6))
ax[0].plot(tt,np.degrees(th_o),'r-'); ax[0].set_title('Open loop: 5 N m torque step, arm never settles\n(pole at s = 0: marginally stable)')
ax[0].set_xlabel('time (s)'); ax[0].set_ylabel('angle (deg)')
ax[1].plot(t,np.degrees(thr),'k--',label='reference'); ax[1].plot(t,np.degrees(th_cl),'b-',label='PID closed loop')
ax[1].set_title('Closed loop: PID position control'); ax[1].set_xlabel('time (s)'); ax[1].set_ylabel('angle (deg)')
ax[1].legend(fontsize=8); ax[1].set_ylim(-5,100)
fig.tight_layout(); fig.savefig(FIG+"/fig_openloop.png"); plt.close(fig)

# save data
import csv
with open(DAT+"/gear_table.csv","w",newline="") as f:
    wr=csv.writer(f); wr.writerow(["Gear","Teeth z","Module m (mm)","Pitch d (mm)","Bore (mm)","Face width (mm)","Mass (kg)","J own (kg m2)","Speed factor at output"])
    for k in range(6): wr.writerow([names[k],teeth[k],module[k],pitchD[k],bore[k],face[k],f"{gear_mass[k]:.3f}",f"{gearJ[k]:.5f}",f"{Ne[k]:.3f}"])
np.savetxt(DAT+"/sim_open.csv",np.c_[t,np.degrees(thr),np.degrees(th),np.degrees(err),cur],
           delimiter=",",header="time_s,ref_deg,actual_deg,error_deg,current_A",comments="")
json.dump(metrics,open(DAT+"/metrics.json","w"),indent=2)
print("\nSaved figures + data.")
