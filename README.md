# Iron-Watch

Metal-detecting access gate with face-recognition attendance logging for a
metal factory. AASTU Electromechanical Engineering internship project.

| Folder | Contents |
|---|---|
| `Report/` | Final report: `Iron-Watch_Project_Report.pdf` / `.docx` / `.md` (source), `figures/`, `data/`, `tools/` (regeneration scripts) |
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
pip install numpy scipy matplotlib markdown xhtml2pdf python-docx pypandoc-binary
cd Report/tools
python run_sim.py        # re-runs the drive simulation, writes figures + data
python make_diagrams.py  # architecture / gearbox / electrical / control diagrams
python build_pdf.py      # Iron-Watch_Project_Report.pdf
python build_docx.py     # Iron-Watch_Project_Report.docx
```
