"""Enrol a worker: capture face samples from the camera.

    python enroll.py --id E001 --name "Abebe Kebede"
    python enroll.py --id E001 --name "Abebe Kebede" --from-folder path/to/photos

Then run  python train.py  to rebuild the model.
"""
import argparse
import re
import cv2
import config
from face_utils import detect_faces, preprocess


def safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="employee ID, e.g. E001")
    ap.add_argument("--name", required=True)
    ap.add_argument("--from-folder", help="use existing photos instead of the camera")
    ap.add_argument("--samples", type=int, default=config.ENROL_SAMPLES)
    a = ap.parse_args()

    out = config.FACES_DIR / f"{safe(a.id)}_{safe(a.name)}"
    out.mkdir(parents=True, exist_ok=True)
    n = 0

    if a.from_folder:
        from pathlib import Path
        for p in sorted(Path(a.from_folder).glob("*")):
            img = cv2.imread(str(p))
            if img is None:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            for box in detect_faces(gray):
                cv2.imwrite(str(out / f"{n:03d}.png"), preprocess(gray, box))
                n += 1
                break
        print(f"Saved {n} face samples to {out}")
        return

    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not cap.isOpened():
        raise SystemExit("Camera not found - check config.CAMERA_INDEX")
    print("Look at the camera. Move your head slightly. Press q to abort.")

    while n < a.samples:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray)
        for (x, y, w, h) in faces[:1]:              # largest/first face only
            cv2.imwrite(str(out / f"{n:03d}.png"), preprocess(gray, (x, y, w, h)))
            n += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{a.name}: {n}/{a.samples}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.imshow("Enrol - Iron-Watch", frame)
        if cv2.waitKey(100) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    print(f"Saved {n} face samples to {out}. Now run:  python train.py")


if __name__ == "__main__":
    main()
