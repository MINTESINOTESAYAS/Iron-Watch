# IronWatch

Factory walk-through security gate for ferrous-metal theft prevention
with facial-recognition attendance — AASTU Department of
Electromechanical Engineering internship project.

## Report

The polished internship project report (39 pages, PDF) is here:

👉 [`report/IronWatch_Internship_Project_Report_AASTU.pdf`](report/IronWatch_Internship_Project_Report_AASTU.pdf)

It follows the AASTU outline: cover → abstract → introduction →
literature review → system design (mechanical, mathematical modeling,
PID controller, electrical/electronics) → simulation/results/discussion →
conclusion/recommendations → appendices (mechanical/BOM, Arduino
firmware, company attendance log system) → references (APA 7th).

## Key design facts

- Gantry 900 × 2000 × 350 mm; LC coil in one upright; **single
  pedestrian swing-arm boom** (the only moving part).
- Ferrous discrimination via CD4046 phase channel (DEMOD → A0);
  firmware rule `metalDetected = (analogRead(A0) <= 40)` — A0 = 0
  is the low-side trigger. VCOIN (4046 pin 9) must be biased (~2.5 V)
  or DEMOD parks at 0 V (permanent false alarm).
- Pins: A0 sensor, D2 red, D3 green, D4 buzzer, Serial 9600,
  badge `A1B2C3`; boom drive on D7/D8 + PWM D9 (L298N).
- PID (Kp=18, Ki=12, Kd=5) controls **only the boom-arm angle**;
  detection logic is the trigger, not the PID plant.

## Rebuilding the report

```bash
cd report
pip install reportlab matplotlib numpy
python3 make_figures.py   # diagrams, PID simulation, metrics.json
python3 make_report.py    # builds the PDF
```
