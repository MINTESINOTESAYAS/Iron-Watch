# Iron-Watch

Metal-detecting access gate with face-recognition attendance logging for a
metal factory. AASTU Electromechanical Engineering internship project.

| Folder | Contents |
|---|---|
| `docs/` | Final report: `Project_Report.pdf`, `Project_Report.docx`, `Project_Report.md` (source), `figures/`, `build_report.py` |
| `matlab/` | Gate drive model: `gate_params.m`, `gate_sim.m`, `gate_analysis.m`, `build_gate_simulink.m` |
| `software/attendance/` | OpenCV face-recognition attendance system (Python) - see its README |
| `software/esp32_gate/` | ESP32 gate-controller firmware + Wokwi diagram |
| `Mechanical/` | SolidWorks gearbox, shafts, arm, structure (see its README) |
| `electrical/` | Proteus schematic (see its README) |
| `Internship_*_Guideline_*.pdf` | AASTU department templates the report follows |

## Quick start

```bash
# MATLAB
cd matlab; gate_sim            % simulation + plots
gate_analysis                  % poles, controllability, sizing
build_gate_simulink            % creates gate_pid.slx (needs Simulink)

# Attendance software
cd software/attendance
pip install -r requirements.txt
python enroll.py --id E001 --name "Worker Name"
python train.py
python attendance.py
python dashboard.py            # http://localhost:5000
```

## Rebuild the report

```bash
pip install python-docx reportlab
python docs/build_report.py     # regenerates Project_Report.pdf and .docx from the .md
```
