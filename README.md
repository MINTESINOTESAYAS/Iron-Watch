# Iron-Watch

Metal-detecting access gate with face-recognition attendance logging for a
metal factory. AASTU Electromechanical Engineering internship project.

| Folder | Contents |
|---|---|
| `docs/Project_Report.md` | Full project report |
| `matlab/` | Gate drive model: `gate_params.m`, `gate_sim.m`, `gate_analysis.m`, `build_gate_simulink.m` |
| `software/attendance/` | OpenCV face-recognition attendance system (Python) - see its README |
| `software/esp32_gate/` | ESP32 gate-controller firmware + Wokwi diagram |
| `Mechanical/` | SolidWorks gearbox, shafts, arm, structure |
| `electrical/` | Proteus schematic |

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
