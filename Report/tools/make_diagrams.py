#!/usr/bin/env python3
"""Generate publication-quality engineering diagrams for the Iron-Watch report.
All values are taken from the project repository (gate_params.m, the Simulink
model gate_gearbox_pid.slx and the Proteus project electrical system.pdsprj)."""
import os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch, Arc
from matplotlib.lines import Line2D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures"); os.makedirs(FIG, exist_ok=True)

BLUE="#1f4e79"; LBLUE="#dae6f2"; GREEN="#2e6b3e"; LGREEN="#dcefe0"
RED="#a6272c"; LRED="#f3dede"; GREY="#555"; LGREY="#eeeeee"; ORANGE="#b5651d"; LOR="#fbe7d3"

def box(ax,x,y,w,h,text,fc=LBLUE,ec=BLUE,fs=8.5,bold=True):
    p=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.012,rounding_size=0.02",
                     fc=fc,ec=ec,lw=1.3); ax.add_patch(p)
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,
            weight="bold" if bold else "normal")
    return (x+w/2,y+h/2)

def arrow(ax,p1,p2,color="black",lw=1.3,style="-|>"):
    ax.add_patch(FancyArrowPatch(p1,p2,arrowstyle=style,mutation_scale=11,
                                 lw=lw,color=color,shrinkA=0,shrinkB=0))

def line(ax,xs,ys,color="black",lw=1.2,ls="-"):
    ax.add_line(Line2D(xs,ys,color=color,lw=lw,ls=ls,solid_capstyle="round"))

def sumcirc(ax,c,r=0.15):
    ax.add_patch(Circle(c,r,fc="white",ec="black",lw=1.3,zorder=6))
    ax.text(*c,"$\\Sigma$",ha="center",va="center",fontsize=11,zorder=7)

# =====================================================================
# 1. CONTROL ARCHITECTURE BLOCK DIAGRAM (mirrors gate_gearbox_pid.slx)
# =====================================================================
fig,ax=plt.subplots(figsize=(12.4,7.0)); ax.set_xlim(0,12.4); ax.set_ylim(0,7.0); ax.axis("off")
def section(x,w,label,color):
    ax.add_patch(Rectangle((x,0.95),w,5.35,fill=False,ec=color,lw=1.4,ls="--",alpha=.7))
    ax.text(x+0.1,6.12,label,color=color,fontsize=9.5,weight="bold")
section(0.2,1.75,"1 REFERENCE",GREY)
section(2.15,3.35,"2 CONTROLLER (PID)",BLUE)
section(5.7,2.15,"3 MOTOR (electrical)",ORANGE)
section(8.05,4.15,"4 MECHANICAL PLANT",GREEN)

box(ax,0.35,3.55,1.45,1.0,"Trapezoidal\nprofile\n$\\theta_{ref},\\,\\omega_{ref}$\n0$\\rightarrow$90° in 2.5 s",LGREY,GREY,8)
# error sums
S1=(2.55,4.05); sumcirc(ax,S1)
ax.text(S1[0]-0.30,S1[1]+0.13,"+",fontsize=11); ax.text(S1[0]+0.14,S1[1]-0.32,"$-$",fontsize=12)
# P, I, D branches
box(ax,3.0,5.15,1.85,0.62,"$K_p$ = 528.3 N m/rad",LBLUE,BLUE,8.2)
box(ax,3.0,4.27,1.85,0.62,"$K_i$ = 264.1 + integrator\n(clamped $\\pm$300 N m)",LBLUE,BLUE,7.8)
box(ax,3.0,3.40,1.85,0.62,"$K_d$ = 190.2\n(speed error)",LBLUE,BLUE,8)
SPID=(5.15,4.05); sumcirc(ax,SPID,0.14)
box(ax,2.55,2.35,2.55,0.78,"Integral clamp $\\pm$300 N m\n= anti-windup (no extra logic)",LGREY,GREY,8,False)
# motor section
box(ax,5.82,3.55,1.9,0.95,"$i_{cmd}=\\tau_{cmd}/(N\\eta K_t)$\nDriver current limit\n$\\pm$30 A",LOR,ORANGE,8)
box(ax,5.82,2.25,1.9,0.95,"Voltage $V=iR+K_e N\\omega$\nSupply limit $\\pm$24 V",LOR,ORANGE,8.2)
box(ax,5.82,1.15,1.9,0.85,"$L\\,di/dt=V-Ri-K_eN\\omega$\n$R$=0.15 $\\Omega$, $L$=0.5 mH",LOR,ORANGE,7.8)
# mechanical
box(ax,8.25,3.55,1.75,0.95,"Gearbox\n$\\tau_{out}=N\\eta K_t i$\nN=70, $\\eta$=0.885",LGREEN,GREEN,8.2)
S4=(10.55,2.9); sumcirc(ax,S4)
ax.text(S4[0]+0.20,S4[0]*0+S4[1]+0.15,"+",fontsize=11); ax.text(S4[0]+0.20,S4[1]-0.30,"$-$",fontsize=12)
box(ax,10.85,1.95,1.25,1.05,"$\\dfrac{1}{J_{eff}s^2+b\\,s}$\n$J_{eff}$=21.13 kg m$^2$\n$b$=1.2 N m s/rad",LGREEN,GREEN,8)
box(ax,10.85,4.65,1.25,0.7,"$\\theta$ arm\nangle",LGREEN,GREEN,8.5)

# wiring: ref -> S1
arrow(ax,(1.80,4.05),(2.39,4.05))
# S1 -> three gains
line(ax,[2.70,2.85,2.85],[4.05,4.05,5.46]); arrow(ax,(2.85,5.46),(3.0,5.46))
line(ax,[2.70,2.85],[4.05,4.58]); arrow(ax,(2.85,4.58),(3.0,4.58))
line(ax,[2.70,2.85,2.85],[4.05,4.05,3.71]); arrow(ax,(2.85,3.71),(3.0,3.71))
# gains -> SPID
arrow(ax,(4.85,5.46),(5.05,4.20))
arrow(ax,(4.85,4.58),(5.03,4.12))
arrow(ax,(4.85,3.71),(5.05,3.90))
# SPID -> icmd -> voltage -> electrical
arrow(ax,(5.29,4.05),(5.82,4.05))
arrow(ax,(6.77,3.55),(6.77,3.20))
arrow(ax,(6.77,2.25),(6.77,2.00))
# electrical -> gearbox (current output routed out of the block's right edge)
line(ax,[7.72,8.12,8.12],[1.58,1.58,3.75]); arrow(ax,(8.12,3.75),(8.25,3.95))
# back-EMF feedback from internal speed into voltage block
line(ax,[12.10,12.10,7.55,7.55],[2.40,0.78,0.78,2.45],color=ORANGE,lw=1.0,ls=":")
arrow(ax,(7.55,2.45),(7.55,2.62),color=ORANGE)
ax.text(9.7,0.58,"back-EMF $K_e N\\omega$ feedback into voltage command",fontsize=7.6,color=ORANGE,ha="center")
# gearbox -> S4 -> inertia -> theta
arrow(ax,(10.00,3.95),(10.40,3.05))
ax.text(10.05,3.40,"viscous friction $b\\omega$",fontsize=7.4,color=GREEN,ha="center")
arrow(ax,(10.70,2.9),(10.85,2.55))
line(ax,[11.48,11.48],[3.00,4.65]); arrow(ax,(11.48,4.60),(11.48,4.66))
# outer feedback theta -> S1 (bottom route, tapped at the arm-angle line)
line(ax,[11.48,12.05,12.05,2.55,2.55],[3.85,3.85,0.32,0.32,3.85],color=BLUE,lw=1.2,ls="-.")
arrow(ax,(2.55,3.85),(2.55,3.92),color=BLUE)
ax.text(7.1,0.10,"Position feedback $\\theta$ (and speed $\\omega$) to PID  - - -  plant = inertia + viscous friction (arm counter-balanced, no gravity term)",
        ha="center",fontsize=8,color=BLUE)
fig.tight_layout(); fig.savefig(FIG+"/fig_control_architecture.png",bbox_inches="tight"); plt.close(fig)

# =====================================================================
# 2. THREE-STAGE GEARBOX KINEMATIC LAYOUT
# =====================================================================
fig,ax=plt.subplots(figsize=(11.6,5.2)); ax.set_aspect("equal"); ax.axis("off")
s=0.0082
rP1,rG1=25.5*s,102*s; rP2,rG2=32*s,140*s; rP3,rG3=40*s,160*s
y=2.6
cP1=(1.3,y); cG1=(cP1[0]+rP1+rG1,y)
cP2=(cG1[0]+1.7,y); cG2=(cP2[0]+rP2+rG2,y)
cP3=(cG2[0]+2.2,y); cG3=(cP3[0]+rP3+rG3,y)
def gear(c,rr,label_inside,col,sub):
    ax.add_patch(Circle(c,rr,fc=col,ec="black",lw=1.4,zorder=2))
    ax.add_patch(Circle(c,rr*0.92,fill=False,ec="black",lw=0.5,ls=":",zorder=3))
    ax.add_patch(Circle(c,rr*0.13,fc="white",ec="black",lw=1.2,zorder=4))
    ax.text(c[0],c[1],label_inside,ha="center",va="center",fontsize=9,weight="bold",zorder=5)
    ax.text(c[0],c[1]-rr-0.26,sub,ha="center",fontsize=8.3)
gear(cP1,rP1,"P1",LBLUE,"P1 — 17T, module 3\nØ51 / bore Ø28 / 25 mm")
gear(cG1,rG1,"G1",LGREEN,"G1 — 68T, module 3\nØ204 / bore Ø20 / 25 mm")
gear(cP2,rP2,"P2",LBLUE,"P2 — 16T, module 4\nØ64 / bore Ø20 / 32 mm")
gear(cG2,rG2,"G2",LGREEN,"G2 — 70T, module 4\nØ280 / bore Ø30 / 32 mm")
gear(cP3,rP3,"P3",LBLUE,"P3 — 16T, module 5\nØ80 / bore Ø30 / 40 mm")
gear(cG3,rG3,"G3",LGREEN,"G3 — 64T, module 5 (arm)\nØ320 / bore Ø90 / 40 mm")
# common shafts
for (ca,cb) in ((cG1,cP2),(cG2,cP3)):
    ax.annotate("",xy=(cb[0]-rP2*0.5,4.55),xytext=(ca[0]+rG1*0.35,4.55),
                arrowprops=dict(arrowstyle="<->",color=GREY,lw=1.1))
ax.text((cG1[0]+cP2[0])/2,4.75,"common shaft B",ha="center",fontsize=8,color=GREY)
ax.text((cG2[0]+cP3[0])/2,4.75,"common shaft C",ha="center",fontsize=8,color=GREY)
ax.annotate("motor shaft A\n24 V, 500 W, 2500 rpm",xy=cP1,xytext=(cP1[0],5.6),
            ha="center",fontsize=8.4,arrowprops=dict(arrowstyle="-",color=GREY))
ax.annotate("output shaft D → 1.0 m boom arm",xy=(cG3[0],y+rG3*0.5),xytext=(cG3[0],5.6),
            ha="center",fontsize=8.4,arrowprops=dict(arrowstyle="-",color=GREY))
for cx,txt in [((cP1[0]+cG1[0])/2,"$i_1=68/17=4.00$"),
               ((cP2[0]+cG2[0])/2,"$i_2=70/16=4.375$"),
               ((cP3[0]+cG3[0])/2,"$i_3=64/16=4.00$")]:
    ax.text(cx,0.75,txt,ha="center",fontsize=10,color=BLUE,weight="bold")
ax.text(0.1,0.20,"Centre distances:  $a_1=(51+204)/2=127.5$ mm  ·  $a_2=(64+280)/2=172$ mm  ·  $a_3=(80+320)/2=200$ mm      "
        "Total ratio $N=i_1 i_2 i_3 = 4.00\\times4.375\\times4.00 = 70:1$",fontsize=9)
ax.set_xlim(0,cG3[0]+rG3+0.6); ax.set_ylim(0.1,6.0)
ax.set_title("Three-stage compound spur-gear train (pitch circles to scale, steel gears)",fontsize=11)
fig.tight_layout(); fig.savefig(FIG+"/fig_gearbox.png",bbox_inches="tight"); plt.close(fig)

# =====================================================================
# 3. ELECTRICAL / CONTROL SCHEMATIC (functional, from Proteus BOM)
# =====================================================================
fig,ax=plt.subplots(figsize=(12,6.8)); ax.set_xlim(0,12); ax.set_ylim(0,6.8); ax.axis("off")
ax.text(2.4,6.45,"INDUCTIVE METAL-DETECTOR SENSOR FRONT-END",ha="center",fontsize=9.5,weight="bold",color=RED)
# LC tank
cx=1.0
for k in range(4):
    th=np.linspace(math.pi,0,24)
    xx=cx-0.20+k*0.13+0.20*np.cos(th); yy=5.15+0.20*np.sin(th)
    ax.plot(xx,yy,color="black",lw=1.3)
ax.text(cx+0.05,5.55,"L1 = 3.9 µH",fontsize=8.5)
ax.plot([cx,cx],[4.20,4.60],color="k"); ax.plot([cx-0.20,cx+0.20],[4.60,4.60],color="k",lw=2)
ax.plot([cx-0.20,cx+0.20],[4.72,4.72],color="k",lw=2); ax.plot([cx,cx],[4.72,5.0],color="k")
ax.text(cx+0.32,4.62,"C1 = 22 nF",fontsize=8.5)
ax.text(cx,3.85,"LC tank, $f_0\\approx$543 kHz\n(metal detunes the tank)",ha="center",fontsize=8)
ax.plot([cx,cx],[3.65,3.4],color="k")
box(ax,2.35,4.55,1.85,1.05,"U2: LM358\ncomparator /\nbuffer (DIL08)",LRED,RED,8.5)
box(ax,2.45,3.15,1.65,0.95,"RV1: 1 kΩ pot\nsensitivity\nthreshold dial",LGREY,GREY,8)
arrow(ax,(1.55,4.85),(2.35,5.05)); arrow(ax,(3.28,4.10),(3.28,4.55))
# Arduino
box(ax,5.0,1.85,2.35,3.9,"",LBLUE,BLUE,9)
ax.text(6.175,5.30,"ARD1: ARDUINO UNO R3",ha="center",fontsize=9.5,weight="bold",color=BLUE)
ax.text(6.175,4.92,"ATmega328P · 16 MHz",ha="center",fontsize=8.2)
for i,t in enumerate(["analog sensing input","detection / timing logic","gate-motor sequencing","status indicators + alarm"]):
    ax.text(6.175,4.42-i*0.42,t,ha="center",fontsize=8.4)
arrow(ax,(4.20,5.0),(5.0,4.6))
# outputs on right (short labels, wide boxes, font 7.8)
outs=[("D1 red LED + R3 220 Ω  →  METAL / ALARM",LRED,RED,5.35),
      ("D2 green LED + R4 220 Ω  →  READY / CLEAR",LGREEN,GREEN,4.55),
      ("BUZ1 piezo buzzer — 5 V, 500 Hz",LOR,ORANGE,3.75)]
for txt,fc,ec,yv in outs:
    box(ax,8.15,yv,3.45,0.6,txt,fc,ec,8.0,bold=False)
    arrow(ax,(7.35,4.2),(8.15,yv+0.30))
box(ax,8.15,2.30,3.45,1.10,"Gate actuator: 24 V / 500 W brushed-DC gearmotor\nH-bridge driver (BTS7960-class, ±30 A)\n3-stage 70:1 gearbox → boom arm 0–90°",
    LGREEN,GREEN,8.0,bold=False)
arrow(ax,(7.35,3.3),(8.15,2.95))
# serial below
box(ax,5.2,0.55,1.95,0.8,"P1: COMPIM serial\n9600 baud, 8N1\ntelemetry / event log",LGREY,GREY,7.8,bold=False)
arrow(ax,(6.175,1.85),(6.175,1.35))
ax.text(0.2,0.18,"Power rails (from Proteus PWRRAILS.DAT): +5 V / GND / VCC for logic, sensing and indicators; separate 24 V rail for the gate motor.   "
        "Designators, values and the LC coil values are read directly from the project netlist (ROOT.CDB).",fontsize=7.8,color=GREY)
ax.set_title("Electrical and electronic system — functional reconstruction of ‘electrical system.pdsprj’",fontsize=10.5)
fig.tight_layout(); fig.savefig(FIG+"/fig_electrical.png",bbox_inches="tight"); plt.close(fig)

# =====================================================================
# 4. GATE STRUCTURE / GRAVITY LOAD
# =====================================================================
fig,axs2=plt.subplots(1,2,figsize=(11.5,4.8),gridspec_kw={"width_ratios":[1,1.25]})
ax=axs2[0]; ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-0.6,2.3); ax.set_ylim(-0.45,3.45)
# base + post
ax.add_patch(Rectangle((-0.45,-0.30),0.95,0.20,fc="#555",ec="black"))
ax.add_patch(Rectangle((-0.18,-0.10),0.36,1.65,fc="#8a8f98",ec="black"))
ax.add_patch(Rectangle((-0.42,1.40),0.84,0.42,fc="#c9d6ea",ec=BLUE,lw=1.4))
ax.text(0.0,1.61,"gearbox +\nmotor",ha="center",va="center",fontsize=7.6)
P=(0.0,1.55)
# open position (faint vertical)
ax.add_patch(Rectangle((P[0]-0.04,P[1]),0.08,1.55,fc="#d9a441",ec="black",alpha=0.30,zorder=2))
ax.text(0.32,2.85,"open position\n(vertical, 90°)",fontsize=8,color=GREY)
# closed arm horizontal
armL=1.70
ax.add_patch(Rectangle((P[0],P[1]-0.04),armL,0.08,fc="#d9a441",ec="black",zorder=3))
ax.add_patch(Circle(P,0.08,fc="white",ec="black",zorder=5))
# COM
gx=P[0]+armL*0.5
ax.add_patch(Circle((gx,P[1]),0.045,fc=RED,ec="black",zorder=6))
ax.annotate("",xy=(gx,P[1]-0.50),xytext=(gx,P[1]-0.03),arrowprops=dict(arrowstyle="->",color=RED,lw=2))
ax.text(gx+0.09,P[1]-0.30,"$mg$",color=RED,fontsize=12)
ax.text(gx+0.05,P[1]+0.20,"COM, $L_c$ = 0.5 m",fontsize=8)
# 90 deg arc
ax.add_patch(Arc(P,1.0,1.0,theta1=90,theta2=0,color=BLUE,lw=1.5))
ax.annotate("",xy=(P[0]+0.52,P[1]+0.03),xytext=(P[0]+0.38,P[1]+0.38),
            arrowprops=dict(arrowstyle="->",color=BLUE,lw=1.4))
ax.text(P[0]+0.60,P[1]+0.34,"90°",color=BLUE,fontsize=11,weight="bold")
ax.text(1.05,0.55,"boom arm: 1.0 m, 13.5 kg; closed = horizontal\nWorst-case gravity torque $T_{grav,max}=mgL_c=66.22$ N m",
        ha="center",fontsize=8.2)
ax.set_title("Boom-gate geometry and worst-case gravity load",fontsize=10)
# right plot
th=np.linspace(0,math.pi/2,200); Tg=13.5*9.81*0.5*np.cos(th)
ax=axs2[1]
ax.plot(np.degrees(th),Tg,color=RED,lw=2.2)
ax.fill_between(np.degrees(th),Tg,alpha=0.12,color=RED)
ax.axhline(66.22,ls=":",color=GREY,lw=1.2)
ax.annotate("66.22 N m at 0° (arm horizontal)",xy=(8,66.22),xytext=(26,60),fontsize=8.4,
            arrowprops=dict(arrowstyle="->",color=GREY))
ax.set_xlabel("arm angle $\\theta$  [0° = closed/horizontal, 90° = open/vertical]",fontsize=9.5)
ax.set_ylabel("gravity torque $m g L_c \\cos\\theta$ (N m)",fontsize=9.5)
ax.set_title("Static gravity load (unbalanced arm) - removed by counterbalance",fontsize=9.5); ax.grid(alpha=.35); ax.set_xlim(0,90); ax.set_ylim(0,72)
fig.tight_layout(); fig.savefig(FIG+"/fig_gate_concept.png",bbox_inches="tight"); plt.close(fig)
print("Diagrams regenerated.")
