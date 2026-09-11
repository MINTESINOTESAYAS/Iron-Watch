"""Generate all figures + computed metrics for the IronWatch AASTU report."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon

NAVY = "#0B2C4A"
GOLD = "#C9A227"
RED = "#C0392B"
GREEN = "#1E8449"
GREY = "#5D6D7E"
LIGHT = "#EAF0F6"

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.labelsize": 10,
})

A = "assets"
import os
os.makedirs(A, exist_ok=True)

# ---------------------------------------------------------------- mechanics ---
m_arm, L_arm = 1.2, 0.85          # kg, m
m_tip = 0.3                       # paddle / end-stop mass
lc = 0.42                         # centre of mass radius (m)
J_arm_only = (1/3)*m_arm*L_arm**2 + m_tip*L_arm**2 + 0.02   # + hub/shaft
J_tot = J_arm_only + 0.064        # + reflected rotor inertia (40:1 gearbox)
b = 1.20                          # viscous damping @ output (bearings+gearbox+back-EMF)
tau_c = 0.25                      # coulomb friction N m
alpha_req, omega_req = 2.5, 1.8   # rad/s^2, rad/s (S-curve profile peaks)
tau_req = J_tot*alpha_req + b*omega_req + tau_c
T_motor = 6.0                     # rated continuous output torque N m (12 V 80 W 40:1)
T_stall = 7.8                     # stall torque N m
SF = T_motor / tau_req
d_shaft = 0.020
tau_shaft = 16*T_stall/(np.pi*d_shaft**3)/1e6  # MPa (worst case: stalled motor)
tau_allow = 55.0
C_bearing, P_bearing = 9400.0, 60.0
L10 = (C_bearing/P_bearing)**3 * 1e6  # revolutions
rpm_out = 25.0
L10h = L10/(60*rpm_out)
P_mech = T_motor*omega_req/0.70  # / gearbox efficiency

mech = dict(J=float(J_tot), tau_req=float(tau_req), SF=float(SF),
            tau_shaft_MPa=float(tau_shaft), L10_rev=float(L10),
            L10h=float(L10h), P_W=float(P_mech))

# ------------------------------------------------------------- PID sim -------
J, bb, Km = J_tot, b, 0.65        # plant: J th''+b th'+tc*tanh(w)=Km*u, |u|<=12 V
Kp, Ki, Kd, N = 18.0, 12.0, 5.0, 30.0
EZONE, IMAX = 0.25, 0.5           # integrator engages |e|<0.25 rad, clamped
dt, T = 0.001, 6.0
n = int(T/dt)
PLOT_T = 3.0   # display window for plots (metrics use the full run)
SP = np.pi/2                      # 90 deg

def simulate(Kp, Ki, Kd, ref, Nloc=N, ez=EZONE, imax=IMAX):
    th, w = 0.0, 0.0
    integ, d_filt = 0.0, 0.0
    TH, U, E = np.zeros(n), np.zeros(n), np.zeros(n)
    umax = 12.0
    for k in range(n):
        r = ref[k]
        e = r - th
        # filtered derivative on MEASUREMENT (no setpoint kick)
        d_filt = d_filt + (dt*Nloc)*((-w) - d_filt)/(1+dt*Nloc) if Nloc > 0 else -w
        # integrator: engage-zone + clamp (anti-windup)
        if abs(e) < ez:
            integ = max(-imax, min(imax, integ + e*dt))
        u = max(-umax, min(umax, Kp*e + Ki*integ + Kd*d_filt))
        acc = (Km*u - bb*w - tau_c*np.tanh(w/0.05))/J
        w += acc*dt
        th += w*dt
        TH[k], U[k], E[k] = th, u, e
    return TH, U, E

t = np.arange(n)*dt
ref_step = np.full(n, SP)
TH_pid, U_pid, E_pid = simulate(Kp, Ki, Kd, ref_step)
TH_p, _, _ = simulate(8.0, 0.0, 0.0, ref_step, Nloc=0, ez=9, imax=0)
TH_pd, _, _ = simulate(14.0, 0.0, 4.0, ref_step, Nloc=25, ez=0, imax=0)

def metrics(TH):
    y = TH/SP
    try: tr = t[np.where(y >= 0.9)[0][0]] - t[np.where(y >= 0.1)[0][0]]
    except Exception: tr = float("nan")
    try:
        band = np.where(np.abs(y-1.0) > 0.02)[0]
        ts = t[band[-1]] if len(band) else 0.0
        # settling = last exit time
        ts = t[band[-1]] if len(band) else 0.0
    except Exception: ts = float("nan")
    os_ = (np.max(y)-1.0)*100
    sse = abs(y[-1]-1.0)*100
    return dict(rise=float(tr), settle=float(ts), overshoot=float(os_),
                sse=float(sse), peak_effort=float(np.max(np.abs(U_pid))))

M = metrics(TH_pid)
pid = dict(Kp=Kp, Ki=Ki, Kd=Kd, N=N, ezone=EZONE, imax=IMAX, **M)

# S-curve reference (smooth open in 1.2 s, hold, smooth close)
def scurve(Tm, dt, n, dwell_start=1.4, close_dur=1.2):
    r = np.zeros(n); tt = np.arange(n)*dt
    for k, tk in enumerate(tt):
        if tk < Tm:  # quintic 0->SP
            s = tk/Tm; r[k] = SP*(10*s**3-15*s**4+6*s**5)
        elif tk < dwell_start: r[k] = SP
        elif tk < dwell_start+close_dur:
            s = (tk-dwell_start)/close_dur; r[k] = SP*(1-(10*s**3-15*s**4+6*s**5))
        else: r[k] = 0.0
    return r
ref_s = scurve(1.2, dt, n)
TH_s, U_s, _ = simulate(Kp, Ki, Kd, ref_s)

with open("metrics.json", "w") as f:
    json.dump({"mech": mech, "pid": pid}, f, indent=1)
print("metrics:", json.dumps({"mech": mech, "pid": pid}, indent=1))

# ------------------------------------------------------------- helpers -------
def box(ax, xy, w, h, text, fc="white", ec=NAVY, fs=9, style="round,pad=0.02"):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle=style, fc=fc, ec=ec, lw=1.4))
    ax.text(xy[0]+w/2, xy[1]+h/2, text, ha="center", va="center", fontsize=fs,
            color=NAVY, weight="bold", linespacing=1.4)

def arrow(ax, p1, p2, c=NAVY, w=1.6, style="-|>"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, color=c,
                 linewidth=w, mutation_scale=12, shrinkA=0, shrinkB=2))

def eq_image(tex, fname, fs=17, pad=0.15):
    fig = plt.figure(figsize=(8, 1.1))
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.5, tex, fontsize=fs, ha="center", va="center", color="black")
    fig.savefig(f"{A}/{fname}", bbox_inches="tight", pad_inches=pad,
                facecolor="white")
    plt.close(fig)

# equations
eq_image(r"$J\,\ddot{\theta}+b\,\dot{\theta}+m\,g\,l_c\sin\theta+\tau_c\,\mathrm{sgn}(\dot{\theta})=\tau_m$".replace(r"\,", " "),
         "eq_rotor.png")
eq_image(r"$\tau_{req}=J\,\alpha+b\,\omega+\tau_c,\qquad P_{mech}=\dfrac{\tau\,\omega}{\eta}$".replace(r"\,", " ").replace(r"\dfrac", r"\frac").replace(r"\qquad", "    "),
         "eq_torque.png")
eq_image(r"$L\,\dfrac{di}{dt}+R\,i+K_b\,\omega_m=v,\qquad \tau_m=N\,K_t\,i$".replace(r"\,", " ").replace(r"\dfrac", r"\frac").replace(r"\qquad", "    "),
         "eq_motor.png")
eq_image("$tau_max = 16 T / (pi d^3)  <=  tau_allow$",
         "eq_shaft.png")
eq_image("$L_{10}=(C/P)^3 \\times 10^6$ rev",
         "eq_bearing.png")
eq_image("$A=df/dx|_{x0,u0}, \\quad B=df/du|_{x0,u0}$",
         "eq_jac.png")
eq_image("$u(t)=K_p e(t)+K_i \\int_0^t e(s) ds+K_d def(t)/dt, \\quad |u| \\leq 12V$",
         "eq_pid.png")
eq_image("$metalDetected = (analogRead(A0) \\leq 40)$",
         "eq_thresh.png")
eq_image("$ADC = round(V_{DEMOD}/5.0 \\times 1023)$",
         "eq_adc.png")

# ---------------------------------------------------- F1 architecture --------
fig, ax = plt.subplots(figsize=(15, 6.6))
ax.set_xlim(0, 15); ax.set_ylim(0, 6.6); ax.axis("off")
ax.set_title("IronWatch system architecture — detection, identity, and boom control", color=NAVY, pad=12)
# lane labels
for y, lab in [(5.35, "FERROUS DETECTION"), (3.35, "IDENTITY + ATTENDANCE"), (1.15, "BOOM CONTROL + ALARMS")]:
    ax.text(0.15, y+0.55, lab, fontsize=9, weight="bold", color="white",
            bbox=dict(boxstyle="round,pad=0.25", fc=NAVY, ec=NAVY))
# detection lane
box(ax, (0.3, 4.6), 2.0, 0.9, "LC search coil\n(in gantry\nupright)")
box(ax, (2.7, 4.6), 2.0, 0.9, "LM358\nsignal\nconditioning")
box(ax, (5.1, 4.6), 2.0, 0.9, "CD4046 PLL\nphase compare\nDEMOD \u2192 A0")
box(ax, (7.5, 4.6), 2.2, 0.9, "Threshold\nA0 \u2264 40\n= METAL", fc="#FDEDEC", ec=RED)
for x in [2.3, 4.7, 7.1]: arrow(ax, (x, 5.05), (x+0.4, 5.05))
arrow(ax, (9.7, 5.05), (10.4, 5.05))
# arduino core
box(ax, (10.4, 3.9), 2.4, 2.0, "Arduino Uno\ndecision logic\nSerial 9600", fc="#FEF9E7", ec=GOLD)
# identity lane
box(ax, (0.3, 2.6), 2.0, 0.9, "Badge / RFID\n(Virtual Terminal\nin simulation)")
box(ax, (2.7, 2.6), 2.2, 0.9, "Valid badge?\nA1B2C3")
box(ax, (5.3, 2.6), 2.0, 0.9, "Face camera\nattendance\npipeline")
box(ax, (7.7, 2.6), 2.0, 0.9, "Attendance log\nCSV + register", fc="#EAFAF1", ec=GREEN)
for x in [2.3, 4.9]: arrow(ax, (x, 3.05), (x+0.4, 3.05))
arrow(ax, (7.3, 3.05), (7.7, 3.05)); arrow(ax, (9.7, 3.05), (10.4, 4.4))
arrow(ax, (4.9, 3.5), (10.4, 4.9))
ax.text(7.0, 3.75, "badge string", fontsize=8, style="italic", color=GREY)
# control lane
box(ax, (0.3, 0.5), 1.9, 0.9, "D2 red LED\nD3 green LED\nD4 buzzer")
box(ax, (2.6, 0.5), 2.1, 0.9, "L298N driver\n+ 12 V geared\nmotor")
box(ax, (5.1, 0.5), 2.1, 0.9, "Swing-arm\nboom (only\nmoving part)")
box(ax, (7.6, 0.5), 2.1, 0.9, "Angle sensor\nPID feedback\nKp/Ki/Kd")
for x in [2.2, 4.7, 7.2]: arrow(ax, (x, 0.95), (x+0.4, 0.95))
arrow(ax, (11.6, 3.9), (11.6, 0.95)); arrow(ax, (11.6, 0.95), (9.7, 0.95))
ax.text(11.75, 2.4, "commands", fontsize=8, style="italic", color=GREY, rotation=90, va="center")
arrow(ax, (10.4, 1.6), (2.2, 1.6)); arrow(ax, (2.2, 1.6), (2.2, 1.4))
ax.text(6.0, 1.75, "alarm / grant signals", fontsize=8, style="italic", color=GREY)
arrow(ax, (9.7, 4.4), (9.7, 3.5))
fig.tight_layout(); fig.savefig(f"{A}/fig_architecture.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F2 gantry -------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.4))
for ax in (ax1, ax2):
    ax.set_aspect("equal"); ax.axis("off")
fig.suptitle("Gantry frame — 900 mm walk-through × 2000 mm high × 350 mm deep (SHS 40×40×2)", color=NAVY, fontweight="bold")
# front view
ax1.set_xlim(0, 14); ax1.set_ylim(0, 22); ax1.set_title("Front view (walk-through)", color=NAVY)
ax1.add_patch(Rectangle((2, 1), 1, 19, fc=LIGHT, ec=NAVY, lw=2))      # left upright
ax1.add_patch(Rectangle((11, 1), 1, 19, fc=LIGHT, ec=NAVY, lw=2))     # right upright
ax1.add_patch(Rectangle((2, 19), 10, 1.2, fc=NAVY, ec=NAVY))          # header
ax1.add_patch(Rectangle((8.6, 2.2), 2.0, 15.6, fc="none", ec=RED, lw=1.6, ls="--"))  # coil zone
ax1.text(9.6, 10, "LC\nCOIL\nZONE", ha="center", va="center", fontsize=9, weight="bold", color=RED, linespacing=1.5)
ax1.add_patch(Rectangle((1.2, 0.4), 2.6, 0.6, fc=GREY, ec=NAVY))      # feet
ax1.add_patch(Rectangle((10.2, 0.4), 2.6, 0.6, fc=GREY, ec=NAVY))
ax1.annotate("", xy=(3, 18.4), xytext=(11, 18.4), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.5))
ax1.text(7, 18.7, "900 mm clear opening", ha="center", fontsize=10, weight="bold", color=NAVY)
ax1.annotate("", xy=(12.8, 1), xytext=(12.8, 20.2), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.5))
ax1.text(13.4, 10.5, "2000 mm", rotation=90, va="center", fontsize=10, weight="bold", color=NAVY)
ax1.text(2.5, 0.05, "anchor feet", ha="center", fontsize=8, color=GREY)
# side view
ax2.set_xlim(0, 10); ax2.set_ylim(0, 22); ax2.set_title("Side view (one upright + boom)", color=NAVY)
ax2.add_patch(Rectangle((3, 1), 1.6, 19, fc=LIGHT, ec=NAVY, lw=2))
ax2.add_patch(Rectangle((2.2, 0.4), 3.2, 0.6, fc=GREY, ec=NAVY))
ax2.add_patch(Rectangle((3, 19), 4.5, 1.2, fc=NAVY, ec=NAVY))
ax2.add_patch(Rectangle((4.6, 9.4), 3.4, 0.5, fc=GOLD, ec=NAVY, lw=1.6))  # boom arm at 1000mm height
ax2.add_patch(Circle((4.6, 9.65), 0.35, fc=NAVY, ec=NAVY))
ax2.text(6.4, 10.2, "swing-arm boom @ ~1000 mm", fontsize=9, weight="bold", color=NAVY)
ax2.text(3.8, 5, "coil faces\npassage", fontsize=8, ha="center", color=RED, weight="bold")
ax2.annotate("", xy=(2.2, 0.1), xytext=(5.4, 0.1), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.5))
ax2.text(3.8, -0.5, "350 mm footprint", ha="center", fontsize=10, weight="bold", color=NAVY)
fig.tight_layout(); fig.savefig(f"{A}/fig_gantry.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F3 boom ---------------
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.set_xlim(0, 11); ax.set_ylim(0, 5.6); ax.axis("off")
fig.suptitle("Swing-arm boom — plan view, 90° travel (the single moving part)", color=NAVY, fontweight="bold")
# pivot housing
ax.add_patch(Rectangle((1.2, 2.0), 1.6, 1.6, fc=NAVY, ec=NAVY))
ax.text(2.0, 2.8, "drive\npost", color="white", ha="center", va="center", fontsize=9, weight="bold")
# closed arm (blocking passage)
ax.add_patch(Rectangle((2.8, 2.62), 5.6, 0.36, fc=GOLD, ec=NAVY, lw=1.6))
ax.text(5.6, 3.25, "CLOSED — arm blocks 900 mm passage", fontsize=10, weight="bold", color=NAVY, ha="center")
# open arm (dashed, swung 90 deg)
ax.add_patch(Rectangle((2.62, 0.4), 0.36, 0, fc="none", ec="none"))
open_arm = Polygon([[2.62, 2.62], [2.98, 2.62], [2.98, -0.4], [2.62, -0.4]], closed=True,
                   fc="none", ec=GREEN, lw=2, ls="--")
ax.add_patch(open_arm)
ax.set_ylim(-0.6, 5.6)
ax.text(3.3, 0.6, "OPEN (90°)", fontsize=10, weight="bold", color=GREEN)
# arc
arc = matplotlib.patches.Arc((2.8, 2.8), 3.4, 3.4, theta1=265, theta2=355, color=NAVY, lw=2)
ax.add_patch(arc)
ax.annotate("", xy=(4.35, 2.35), xytext=(3.4, 1.35), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2))
ax.text(4.6, 1.5, r"$\theta: 0 \rightarrow 90^{\circ}$", fontsize=12, color=NAVY)
# dims + FBD note
ax.annotate("", xy=(2.8, 4.3), xytext=(8.4, 4.3), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.4))
ax.text(5.6, 4.5, "L = 0.85 m,  m = 1.2 kg + 0.3 kg paddle", ha="center", fontsize=10, color=NAVY)
ax.text(8.9, 2.8, "pivot FBD:\nJ·θ̈ + b·θ̇\n+ τc·sgn(θ̇)\n= τm (gearbox)",
       fontsize=9, color=NAVY, va="center",
       bbox=dict(boxstyle="round,pad=0.3", fc=LIGHT, ec=NAVY))
fig.tight_layout(); fig.savefig(f"{A}/fig_boom.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F4 simulink -----------
fig, ax = plt.subplots(figsize=(15, 4.6))
ax.set_xlim(0, 15); ax.set_ylim(0, 4.2); ax.axis("off")
fig.suptitle("MATLAB/Simulink PID loop — boom-arm angle servo (detection logic is the trigger, not the plant)",
             color=NAVY, fontweight="bold")
box(ax, (0.3, 1.7), 1.5, 0.9, "θ ref\n0 / 90°")
ax.add_patch(Circle((2.45, 2.15), 0.35, fc="white", ec=NAVY, lw=1.6))
ax.text(2.45, 2.15, "Σ", ha="center", va="center", fontsize=12, weight="bold", color=NAVY)
ax.text(2.45, 2.62, "+", ha="center", fontsize=10, color=NAVY); ax.text(2.05, 1.85, "−", ha="center", fontsize=12, color=NAVY)
box(ax, (3.2, 1.7), 2.2, 0.9, "PID + filter\n+ anti-windup", fc="#FEF9E7", ec=GOLD)
box(ax, (5.9, 1.7), 1.7, 0.9, "Saturation\n±12 V")
box(ax, (8.1, 1.7), 2.6, 0.9, "DC geared motor\n+ swing arm\nJ θ̈+b θ̇=Km·u")
box(ax, (11.2, 1.7), 1.3, 0.9, "θ\n(deg)")
box(ax, (12.9, 1.7), 1.5, 0.9, "Scope\n+ metrics")
arrow(ax, (1.8, 2.15), (2.1, 2.15)); arrow(ax, (2.8, 2.15), (3.2, 2.15))
arrow(ax, (5.4, 2.15), (5.9, 2.15)); arrow(ax, (7.6, 2.15), (8.1, 2.15))
arrow(ax, (10.7, 2.15), (11.2, 2.15)); arrow(ax, (12.5, 2.15), (12.9, 2.15))
arrow(ax, (11.85, 1.7), (11.85, 0.7)); arrow(ax, (11.85, 0.7), (2.45, 0.7)); arrow(ax, (2.45, 0.7), (2.45, 1.8))
ax.text(7.0, 0.35, "angle-sensor feedback (potentiometer / encoder)", ha="center", fontsize=9, style="italic", color=GREY)
ax.text(4.3, 1.15, "e", ha="center", fontsize=10, color=NAVY); ax.text(6.75, 2.7, "u", ha="center", fontsize=10, color=NAVY)
fig.tight_layout(); fig.savefig(f"{A}/fig_simulink.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F5 pid step -----------
fig, ax = plt.subplots(figsize=(11, 6.2))
ax.plot(t, np.rad2deg(ref_step), "k--", lw=1.6, label="Reference 90°")
ax.plot(t, np.rad2deg(TH_p), color=GREY, lw=1.8, label="P only (Kp=8) — oscillatory")
ax.plot(t, np.rad2deg(TH_pd), color=GOLD, lw=1.8, label="PD (Kp=14, Kd=4) — small SSE")
ax.plot(t, np.rad2deg(TH_pid), color=NAVY, lw=2.4, label=f"PID tuned (Kp={Kp}, Ki={Ki}, Kd={Kd})")
ax.fill_between(t, 88.2, 91.8, color=GREEN, alpha=0.08, label="±2% band")
ax.set_xlim(0, 3); ax.set_ylim(0, 105)
ax.set_xlabel("Time (s)"); ax.set_ylabel("Boom angle (deg)")
ax.set_title("Closed-loop step response — boom angle 0 → 90°", color=NAVY)
ax.grid(True, alpha=0.3); ax.legend(loc="lower right", fontsize=9)
txt = (f"PID metrics:  rise {M['rise']:.2f} s   settling(2%) {M['settle']:.2f} s\n"
       f"overshoot {M['overshoot']:.1f}%   steady-state err {M['sse']:.2f}%   peak |u| {M['peak_effort']:.1f} V")
ax.text(0.98, 0.30, txt, transform=ax.transAxes, ha="right", va="top", fontsize=9,
        color=NAVY, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=NAVY))
fig.tight_layout(); fig.savefig(f"{A}/fig_pid_step.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F6 scurve -------------
fig, axs = plt.subplots(3, 1, figsize=(11, 7.2), sharex=True)
axs[0].plot(t, np.rad2deg(ref_s), "k--", lw=1.4, label="S-curve profile (open–hold–close)")
axs[0].plot(t, np.rad2deg(TH_s), color=NAVY, lw=2, label="PID tracking")
axs[0].set_ylabel("Angle (deg)"); axs[0].legend(fontsize=9); axs[0].grid(True, alpha=0.3)
axs[0].set_title("Operational profile tracking — smooth open (1.2 s), hold, smooth close", color=NAVY)
w_s = np.gradient(TH_s, dt)
axs[1].plot(t, np.rad2deg(w_s), color=GREEN, lw=1.8)
axs[1].set_ylabel("Speed (deg/s)"); axs[1].grid(True, alpha=0.3)
axs[2].plot(t, U_s, color=RED, lw=1.6)
axs[2].axhline(12, color="k", ls=":", lw=1); axs[2].axhline(-12, color="k", ls=":", lw=1)
axs[2].set_ylabel("Effort u (V)"); axs[2].set_xlabel("Time (s)"); axs[2].grid(True, alpha=0.3)
axs[2].set_xlim(0, PLOT_T)
axs[2].text(0.99, 0.88, "saturation ±12 V never hit — smooth, unstressed drive", transform=axs[2].transAxes,
            ha="right", fontsize=9, color=NAVY, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=NAVY))
fig.tight_layout(); fig.savefig(f"{A}/fig_pid_scurve.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F7 demod --------------
fig, ax = plt.subplots(figsize=(11, 5.8))
phase = np.linspace(0, 90, 400)
v_demod = 4.8*np.exp(-phase/22) + 0.05
adc = np.round(v_demod/5.0*1023)
ax.plot(phase, v_demod, color=NAVY, lw=2.4, label="DEMOD voltage vs phase shift (illustrative)")
ax.axhline(0.2, color=RED, ls="--", lw=1.8, label="Threshold ADC=40 (≈0.20 V)")
ax.axhspan(0, 0.2, color=RED, alpha=0.08)
ax.text(62, 0.55, "ALARM ZONE\nA0 ≤ 40 → METAL", color=RED, weight="bold", ha="center", fontsize=10)
ax.set_xlabel("Phase shift caused by target (deg)"); ax.set_ylabel("DEMOD (V)")
ax2 = ax.twinx(); ax2.plot(phase, adc, color=GOLD, lw=1.4, ls=":", label="ADC counts")
ax2.set_ylabel("Arduino A0 counts (0–1023)")
for x, v, lab, c in [(4, 4.6, "air ≈ 940", GREY), (28, 1.2, "keys/buckle ≈ 245", GOLD), (70, 0.1, "iron bar ≈ 20", RED)]:
    ax.plot(x, v, "o", color=c, ms=8); ax.text(x+2.5, v+0.35, lab, fontsize=9, weight="bold", color=c)
ax.set_xlim(0, 90); ax.set_ylim(0, 5.2)
ax.set_title("Ferrous discrimination — pure iron/steel collapses DEMOD toward 0 V; small items stay above threshold", color=NAVY)
ax.grid(True, alpha=0.3)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc="upper right", fontsize=9)
fig.tight_layout(); fig.savefig(f"{A}/fig_demod.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F8 proteus ------------
fig, ax = plt.subplots(figsize=(15, 8.2))
ax.set_xlim(0, 15); ax.set_ylim(0, 8.4); ax.axis("off")
fig.suptitle("Proteus firmware-in-the-loop bench — concept (what was simulated vs substituted)", color=NAVY, fontweight="bold")
# arduino
box(ax, (6.0, 3.1), 3.0, 2.6, "Arduino Uno\n(ATmega328P)\nA0 D2 D3 D4\nSerial 9600", fc="#FEF9E7", ec=GOLD)
# left chain
box(ax, (0.3, 5.3), 2.3, 1.2, "LC coil +\noscillator")
box(ax, (3.0, 5.3), 2.1, 1.2, "LM358\nconditioning")
box(ax, (0.3, 3.6), 2.3, 1.2, "CD4046\nDEMOD out")
box(ax, (3.0, 3.6), 2.1, 1.2, "10 k pot\n⇄ DEMOD\n(substitute!)", fc="#FDEDEC", ec=RED)
arrow(ax, (2.6, 5.9), (3.0, 5.9)); arrow(ax, (1.45, 5.3), (1.45, 4.8))
ax.text(1.6, 5.0, "phase", fontsize=8, style="italic", color=GREY)
arrow(ax, (2.6, 4.2), (3.0, 4.2)); arrow(ax, (5.1, 4.2), (6.0, 4.4))
ax.text(5.15, 4.55, "→ A0", fontsize=9, weight="bold", color=NAVY)
ax.text(0.3, 3.15, "VCOIN pin 9 biased ≈2.5 V — else DEMOD stuck at 0 V", fontsize=8, color=RED, weight="bold")
# top terminal
box(ax, (6.0, 6.3), 3.0, 1.2, "Virtual Terminal\n9600-8-N-1 ⇄ RFID\nbadge A1B2C3", fc="#EAF2F8", ec=NAVY)
arrow(ax, (7.0, 6.3), (7.0, 5.7)); arrow(ax, (8.0, 5.7), (8.0, 6.3))
ax.text(8.2, 6.0, "TX/RX", fontsize=8, style="italic", color=GREY)
# right: outputs
box(ax, (9.9, 5.5), 2.0, 1.0, "D2 RED\n(alarm)")
box(ax, (12.3, 5.5), 2.0, 1.0, "D3 GREEN\n(granted)")
box(ax, (9.9, 4.0), 2.0, 1.0, "D4 BUZZER\n(via NPN)")
box(ax, (12.3, 4.0), 2.0, 1.0, "LCD 16×2\n(status)")
for xa, ya, xb, yb in [(9.0, 5.0, 9.9, 6.0), (9.0, 4.8, 12.3, 6.0), (9.0, 4.0, 9.9, 4.5), (9.0, 3.8, 12.3, 4.5)]:
    arrow(ax, (xa, ya), (xb, yb))
# bottom: boom drive
box(ax, (6.0, 0.6), 3.0, 1.5, "L298N + 12 V\ngeared motor\n⇄ boom arm", fc="#EAFAF1", ec=GREEN)
arrow(ax, (7.5, 3.1), (7.5, 2.1))
ax.text(7.7, 2.6, "D7/D8 + PWM D9", fontsize=8, style="italic", color=GREY)
box(ax, (9.9, 0.6), 4.4, 1.5, "Angle feedback\npot on shaft ⇄ encoder\n(PID loop in Simulink)", fc="white", ec=GREY)
arrow(ax, (9.0, 1.35), (9.9, 1.35))
# substitution banner
ax.text(7.5, 7.85, "Honest substitutions: pot ⇄ DEMOD volts  •  Virtual Terminal ⇄ RFID reader  •  ideal motor ⇄ geared boom (friction in MATLAB)  •  serial events ⇄ face pipeline",
        ha="center", fontsize=8.5, color=RED, weight="bold",
        bbox=dict(boxstyle="round,pad=0.35", fc="#FDEDEC", ec=RED))
fig.tight_layout(); fig.savefig(f"{A}/fig_proteus.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F9 flowchart ----------
fig, ax = plt.subplots(figsize=(9, 11))
ax.set_xlim(0, 9); ax.set_ylim(0, 11.4); ax.axis("off")
fig.suptitle("Firmware decision flow — detect → identify → grant/deny → boom PID → log", color=NAVY, fontweight="bold")

def rbox(y, text, fc="white", ec=NAVY, h=0.75):
    ax.add_patch(FancyBboxPatch((2.4, y), 4.2, h, boxstyle="round,pad=0.05", fc=fc, ec=ec, lw=1.5))
    ax.text(4.5, y+h/2, text, ha="center", va="center", fontsize=9, weight="bold", color=NAVY)
    return y
def dia(yc, text, fc="white", ec=NAVY):
    p = Polygon([[4.5, yc+0.75], [6.9, yc], [4.5, yc-0.75], [2.1, yc]], closed=True, fc=fc, ec=ec, lw=1.5)
    ax.add_patch(p)
    ax.text(4.5, yc, text, ha="center", va="center", fontsize=9, weight="bold", color=NAVY)
    return yc
def varrow(y1, y2, x=4.5):
    arrow(ax, (x, y1), (x, y2))
rbox(10.3, "START — init pins, Serial 9600")
rbox(9.35, "Read sensor:  A0 = analogRead(A0)")
dia(8.0, "A0 ≤ 40 ?\n(METAL)")
arrow(ax, (4.5, 10.3), (4.5, 10.1)); arrow(ax, (4.5, 9.35), (4.5, 8.78))
# YES branch (left): route left then down into alarm box
ax.add_patch(FancyBboxPatch((0.15, 6.55), 3.0, 1.15, boxstyle="round,pad=0.05", fc="#FDEDEC", ec=RED, lw=1.5))
ax.text(1.65, 7.12, "ALARM: D2 RED on\nD4 buzzer, boom LOCKED", ha="center", va="center", fontsize=9, weight="bold", color=RED)
ax.plot([2.1, 1.65], [8.0, 8.0], color=RED, lw=1.6)
arrow(ax, (1.65, 8.0), (1.65, 7.72), c=RED)
ax.text(1.9, 8.18, "YES", fontsize=9, weight="bold", color=RED)
# NO branch (right): route right then down into badge box
ax.add_patch(FancyBboxPatch((5.85, 6.55), 3.0, 1.15, boxstyle="round,pad=0.05", fc="white", ec=NAVY, lw=1.5))
ax.text(7.35, 7.12, "Read badge from Serial\n(Virtual Terminal)", ha="center", va="center", fontsize=9, weight="bold", color=NAVY)
ax.plot([6.9, 7.35], [8.0, 8.0], color=NAVY, lw=1.6)
arrow(ax, (7.35, 8.0), (7.35, 7.72))
ax.text(7.05, 8.18, "NO", fontsize=9, weight="bold", color=GREEN)
# badge decision diamond
dia(5.5, "badge ==\n\"A1B2C3\" ?")
ax.plot([7.35, 7.35, 4.5], [6.55, 6.25, 6.25], color=NAVY, lw=1.6)
arrow(ax, (4.5, 6.25), (4.5, 6.28))
ax.text(5.9, 6.42, "badge string", fontsize=7.5, style="italic", color=GREY, ha="center")
ax.text(7.5, 5.5, "NO → deny:\nRED blink,\nboom locked", fontsize=8.5, color=RED, weight="bold",
        bbox=dict(boxstyle="round,pad=0.25", fc="#FDEDEC", ec=RED))
ax.plot([6.9, 7.0], [5.5, 5.5], color=RED, lw=1.6)
arrow(ax, (7.5, 4.95), (7.5, 1.52), c=RED)   # deny returns to scan via loop line

# grant chain
rbox(4.0, "GRANT: D3 GREEN on — log attendance", fc="#EAFAF1", ec=GREEN)
rbox(3.05, "PID servo boom 0° → 90° (open)")
rbox(2.1, "Hold 3 s → PID servo 90° → 0° (close)")
rbox(1.15, "Write event log (time, badge, A0, result)")
arrow(ax, (4.5, 6.25-0.75), (4.5, 4.78))
arrow(ax, (4.5, 4.0), (4.5, 3.82)); arrow(ax, (4.5, 3.05), (4.5, 2.87))
arrow(ax, (4.5, 2.1), (4.5, 1.92))
# alarm return path (left)
arrow(ax, (1.65, 6.55), (1.65, 1.52)); arrow(ax, (1.65, 1.52), (2.38, 1.52))
ax.text(1.0, 4.0, "return\nto scan", fontsize=8, style="italic", color=GREY, ha="center")
# main loop-back (right)
arrow(ax, (6.62, 1.52), (8.45, 1.52)); arrow(ax, (8.45, 1.52), (8.45, 10.67)); arrow(ax, (8.45, 10.67), (6.62, 10.67))
ax.text(8.55, 6.0, "loop", fontsize=8, style="italic", color=GREY, ha="left")
fig.tight_layout(); fig.savefig(f"{A}/fig_flowchart.png", bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------- F10 face pipe ---------
fig, ax = plt.subplots(figsize=(15, 4.4))
ax.set_xlim(0, 15); ax.set_ylim(0, 3.6); ax.axis("off")
fig.suptitle("Facial-recognition attendance pipeline — enrolled faces linked to gate events", color=NAVY, fontweight="bold")
steps = ["Enroll\n(HR office)", "Face\nembeddings DB", "Gate camera\ncapture", "Detect +\nmatch", "Liveness\ncheck*", "Grant +\nwrite log", "Daily CSV +\nmonthly sheet"]
x = 0.2
for i, s in enumerate(steps):
    fc = "#EAFAF1" if i in (1, 5, 6) else "white"
    ec = GREEN if i in (1, 5, 6) else NAVY
    box(ax, (x, 1.2), 1.7, 1.2, s, fc=fc, ec=ec, fs=8.5)
    if i < len(steps)-1: arrow(ax, (x+1.7, 1.8), (x+2.05, 1.8))
    x += 2.05
ax.text(7.5, 0.45, "* Liveness / anti-spoof note: deployment recommendation — see §5.2.  Prototype represents this stage with badge + serial attendance events.",
        ha="center", fontsize=8.5, style="italic", color=GREY)
fig.tight_layout(); fig.savefig(f"{A}/fig_facepipe.png", bbox_inches="tight"); plt.close(fig)

print("figures done")
