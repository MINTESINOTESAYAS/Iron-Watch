"""Central settings for the Iron-Watch attendance system. Edit here only."""
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent
DATA_DIR   = BASE_DIR / "data"
FACES_DIR  = DATA_DIR / "faces"          # data/faces/<emp_id>_<name>/*.png
MODEL_FILE = DATA_DIR / "lbph_model.yml"
LABELS_FILE= DATA_DIR / "labels.json"
DB_FILE    = DATA_DIR / "attendance.db"

CAMERA_INDEX      = 0        # 0 = first webcam; or an RTSP URL string for an IP camera
FRAME_WIDTH       = 640
FRAME_HEIGHT      = 480
FACE_SIZE         = (200, 200)   # all faces are resized to this before training

ENROL_SAMPLES     = 30       # images captured per worker during enrolment
LBPH_THRESHOLD    = 70.0     # LBPH distance: lower = stricter. 50-80 typical.
CONFIRM_FRAMES    = 5        # consecutive frames the same ID must be seen before logging
REPEAT_LOCKOUT_S  = 60       # ignore the same worker for this many seconds after a log

# Metal-detector gate controller (ESP32 over USB serial). Set PORT=None to disable.
SERIAL_PORT       = None     # e.g. "COM5" on Windows, "/dev/ttyUSB0" on Linux
SERIAL_BAUD       = 115200
METAL_HOLD_S      = 5.0      # a METAL:1 message stays valid for this long

DASHBOARD_HOST    = "0.0.0.0"
DASHBOARD_PORT    = 5000
