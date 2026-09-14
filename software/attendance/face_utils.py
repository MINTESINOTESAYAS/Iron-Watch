"""Face detection (Haar cascade, ships inside OpenCV) + LBPH recogniser wrapper."""
import json
import cv2
import numpy as np
import config

_CASCADE_NAME = "haarcascade_frontalface_default.xml"
_cascade_path = config.BASE_DIR / _CASCADE_NAME            # local copy wins
if not _cascade_path.exists():
    _cascade_path = cv2.data.haarcascades + _CASCADE_NAME  # copy shipped with OpenCV
_cascade = cv2.CascadeClassifier(str(_cascade_path))
if _cascade.empty():
    raise SystemExit(
        f"Could not load {_CASCADE_NAME}. Download it from\n"
        "https://github.com/opencv/opencv/raw/4.x/data/haarcascades/"
        f"{_CASCADE_NAME}\nand place it next to face_utils.py")


def detect_faces(gray):
    """Return list of (x, y, w, h) for faces in a grayscale frame."""
    return _cascade.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))


def preprocess(gray, box):
    """Crop, resize and equalise a face so lighting changes matter less."""
    x, y, w, h = box
    face = gray[y:y + h, x:x + w]
    face = cv2.resize(face, config.FACE_SIZE)
    return cv2.equalizeHist(face)


def new_recogniser():
    if not hasattr(cv2, "face"):
        raise SystemExit(
            "cv2.face missing -> run:  pip uninstall opencv-python && "
            "pip install opencv-contrib-python")
    return cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)


def save_labels(labels: dict):
    config.LABELS_FILE.write_text(json.dumps(labels, indent=2))


def load_labels() -> dict:
    """{label(int): {"emp_id":..., "name":...}}"""
    raw = json.loads(config.LABELS_FILE.read_text())
    return {int(k): v for k, v in raw.items()}


def load_recogniser():
    rec = new_recogniser()
    rec.read(str(config.MODEL_FILE))
    return rec, load_labels()
