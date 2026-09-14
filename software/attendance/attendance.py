"""Live attendance logging: camera -> face recognition -> SQLite (+ gate).

    python attendance.py            # window with boxes + names
    python attendance.py --headless # no window (Raspberry Pi / server)

Press q to quit. Each worker toggles IN / OUT on successive recognitions,
with a lockout so one person walking past is logged only once.
"""
import argparse
import time
from collections import deque
import cv2
import config
import db
from face_utils import detect_faces, preprocess, load_recogniser
from gate_link import GateLink


class Recogniser:
    """Wraps LBPH + the 'confirm over N frames' + lockout logic."""

    def __init__(self):
        self.model, self.labels = load_recogniser()
        self.history = deque(maxlen=config.CONFIRM_FRAMES)
        self.last_logged = {}                       # emp_id -> unix time

    def identify(self, face):
        label, dist = self.model.predict(face)
        if dist > config.LBPH_THRESHOLD or label not in self.labels:
            return None, dist
        return self.labels[label], dist

    def should_log(self, emp_id):
        self.history.append(emp_id)
        if len(self.history) < config.CONFIRM_FRAMES or len(set(self.history)) != 1:
            return False
        if time.time() - self.last_logged.get(emp_id, 0) < config.REPEAT_LOCKOUT_S:
            return False
        self.last_logged[emp_id] = time.time()
        self.history.clear()
        return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()

    rec = Recogniser()
    gate = GateLink()
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not cap.isOpened():
        raise SystemExit("Camera not found - check config.CAMERA_INDEX")
    print("Attendance running. Press q to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray)

        for (x, y, w, h) in faces:
            who, dist = rec.identify(preprocess(gray, (x, y, w, h)))
            if who is None:
                colour, text = (0, 0, 255), f"UNKNOWN ({dist:.0f})"
                rec.history.append(None)
            else:
                colour, text = (0, 255, 0), f"{who['name']} ({dist:.0f})"
                if rec.should_log(who["emp_id"]):
                    ev = db.log_event(who["emp_id"], who["name"], dist, gate.metal_detected)
                    gate.send("OPEN")
                    flag = "  [METAL ALERT]" if gate.metal_detected else ""
                    print(f"{time.strftime('%H:%M:%S')}  {ev:3s}  {who['emp_id']}  {who['name']}{flag}")
            if not a.headless:
                cv2.rectangle(frame, (x, y), (x + w, y + h), colour, 2)
                cv2.putText(frame, text, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)

        if not a.headless:
            if gate.metal_detected:
                cv2.putText(frame, "METAL DETECTED", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            cv2.imshow("Iron-Watch attendance", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
