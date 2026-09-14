# Iron-Watch attendance logging (OpenCV + SQLite + Flask)

Camera at the gate -> face recognised -> IN/OUT written to `data/attendance.db`
-> shown on a web dashboard. Optional ESP32 link adds the metal-detector flag.

## 1. Install (Python 3.9+)

```bash
cd software/attendance
python -m venv .venv
# Windows: .venv\Scripts\activate     Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```
`opencv-contrib-python` is required (plain `opencv-python` has no `cv2.face`).
If both are installed, uninstall `opencv-python`.

## 2. Enrol workers  (30 face samples each from the webcam)

```bash
python enroll.py --id E001 --name "Abebe Kebede"
python enroll.py --id E002 --name "Sara Tesfaye"
# or from existing photos:
python enroll.py --id E003 --name "Dawit Alemu" --from-folder C:\photos\dawit
```
Samples go to `data/faces/<id>_<name>/`. Enrol under the SAME lighting as the gate.

## 3. Train

```bash
python train.py
```
Writes `data/lbph_model.yml` + `data/labels.json` and registers workers in the DB.
Re-run every time you enrol someone.

## 4. Run attendance

```bash
python attendance.py            # window with boxes;  q = quit
python attendance.py --headless # on a Pi / server
```
Green box = known worker (name + LBPH distance). Red = UNKNOWN.
A worker is logged after 5 consecutive matching frames, toggling IN -> OUT -> IN,
and ignored for 60 s afterwards so they are not double-counted.

## 5. Dashboard

```bash
python dashboard.py     # open http://localhost:5000
```
Daily hours per worker, latest events, metal alerts highlighted. JSON at
`/api/events` and `/api/summary?day=YYYY-MM-DD`.

## 6. Connect the ESP32 gate (optional)

Flash `../esp32_gate/esp32_gate.ino`, then in `config.py` set
`SERIAL_PORT = "COM5"` (or `/dev/ttyUSB0`). The PC sends `OPEN` on a
recognised face and `DENY` on unknown; the ESP32 sends `METAL:1/0`, which is
stored with the next attendance record.

## Tuning (config.py)

| Setting | Effect |
|---|---|
| `LBPH_THRESHOLD` (70) | lower = stricter; raise if real workers show as UNKNOWN |
| `CONFIRM_FRAMES` (5) | more = fewer false logs, slower response |
| `REPEAT_LOCKOUT_S` (60) | min. seconds between two logs of the same worker |
| `CAMERA_INDEX` | `0`, `1`… or an RTSP URL for an IP camera |

## Troubleshooting

* `cv2.face missing` -> `pip uninstall opencv-python opencv-python-headless && pip install opencv-contrib-python`
* Everyone is UNKNOWN -> enrol more samples in gate lighting, raise threshold to 80.
* Wrong person matched -> lower threshold to 55-60, add more samples for both people.
* Camera not found -> change `CAMERA_INDEX`, close other apps using the webcam.
