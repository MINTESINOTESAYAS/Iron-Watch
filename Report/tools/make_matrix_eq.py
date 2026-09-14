#!/usr/bin/env python3
"""Render the state-space matrix equation (mathtext has no bmatrix) as a
crisp, large equation image used by both the PDF and DOCX builds."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")

fig, ax = plt.subplots(figsize=(11.6, 2.5), dpi=300)
ax.set_xlim(0, 11.6); ax.set_ylim(0, 2.5); ax.axis("off")
fs = 20
ys = [1.95, 1.25, 0.55]

def lbracket(xc, yt, yb, w=0.09, lw=2.0):
    ax.plot([xc, xc], [yb, yt], color="k", lw=lw)
    ax.plot([xc, xc+w], [yt, yt], color="k", lw=lw)
    ax.plot([xc, xc+w], [yb, yb], color="k", lw=lw)

def rbracket(xc, yt, yb, w=0.09, lw=2.0):
    ax.plot([xc, xc], [yb, yt], color="k", lw=lw)
    ax.plot([xc, xc-w], [yt, yt], color="k", lw=lw)
    ax.plot([xc, xc-w], [yb, yb], color="k", lw=lw)

ax.text(0.05, 1.25, r"$\dot{\mathbf{x}}=$", fontsize=fs+3, va="center")
# matrix A
xA0, xA1 = 1.05, 4.55
lbracket(xA0, 2.30, 0.20); rbracket(xA1, 2.30, 0.20)
Ac = [1.40, 2.45, 3.85]
Agrid = [["0", "1", "0"],
         ["0", r"$-b/J_{eff}$", r"$N\eta K_t/J_{eff}$"],
         ["0", r"$-K_e N/L$", r"$-R/L$"]]
for y, row in zip(ys, Agrid):
    for xc, t in zip(Ac, row):
        ax.text(xc, y, t, fontsize=fs-2.5, va="center", ha="center")
ax.text(4.80, 1.25, r"$\mathbf{x}$", fontsize=fs+2, va="center")
ax.text(5.45, 1.25, r"$+$", fontsize=fs+2, va="center")
# vector B
xB0, xB1 = 5.95, 6.75
lbracket(xB0, 2.30, 0.20); rbracket(xB1, 2.30, 0.20)
for y, t in zip(ys, ["$0$", "$0$", "$1/L$"]):
    ax.text((xB0+xB1)/2, y, t, fontsize=fs-2, va="center", ha="center")
ax.text(7.00, 1.25, r"$V$", fontsize=fs+2, va="center")
ax.text(7.55, 1.25, r"$+$", fontsize=fs+2, va="center")
# disturbance vector
xD0, xD1 = 8.05, 8.85
lbracket(xD0, 2.30, 0.20); rbracket(xD1, 2.30, 0.20)
for y, t in zip(ys, ["$0$", "$1/J_{eff}$", "$0$"]):
    ax.text((xD0+xD1)/2, y, t, fontsize=fs-3, va="center", ha="center")
ax.text(9.15, 1.25, r"$d,\qquad d=-mgL_c\cos\theta$,", fontsize=fs-1, va="center")
# output + state definition
ax.text(0.05, -0.32, r"$y=[\,1\ \ 0\ \ 0\,]\,\mathbf{x},$"
                     r"$\qquad \mathbf{x}=[\,\theta,\ \omega,\ i\,]^T$,",
        fontsize=fs-1, va="center")
ax.set_ylim(-0.7, 2.6)
fig.savefig(os.path.join(FIG, "eq_state_space.png"), dpi=300, bbox_inches="tight",
            facecolor="white", pad_inches=0.10)
print("state-space equation image saved")
