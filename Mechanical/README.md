# Mechanical design (SolidWorks)

Boom-gate drive: 24 V DC motor → 3-stage spur gearbox (70 : 1) → 90 mm output shaft → 1.0 m / 13.5 kg arm.

| File | Part |
|---|---|
| `pinion 1 (motor).SLDPRT` | Stage 1 pinion, 17 T, m = 3 |
| `gear 1.SLDPRT` | Stage 1 gear, 68 T, m = 3 |
| `Pinion 2.SLDPRT` / `Gear 2.SLDPRT` | Stage 2, 16 T / 70 T, m = 4 |
| `Pinion 3.SLDPRT` / `Gear 3 (Arm).SLDPRT` | Stage 3, 16 T / 64 T, m = 5 (arm gear) |
| `20mm shaft`, `27mm shaft`, `30mm shaft`, `90mm shaft`, `minishaft.SLDPRT` | Shafts |
| `casing for gear box.SLDPRT` | Gearbox housing |
| `Structural_gate_design.SLDPRT`, `handle.SLDPRT`, `grip.SLDPRT` | Gate frame and manual release |
| `assembly/Gearbox_Design.SLDASM` | Gearbox assembly (exported to `../Gearbox_Design.xml` for Simscape Multibody) |
| `assembly/Overall_metal_detecting_gate_design.SLDASM` | Full gate assembly |

Ratios: 4.000 × 4.375 × 4.000 = 70.0. Inertia and motor sizing derived from these parts are in `../matlab/gate_params.m`; see report Section 3.1.
