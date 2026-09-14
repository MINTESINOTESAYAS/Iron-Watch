"""Train the LBPH model from data/faces/*  and register workers in the DB.

    python train.py
"""
import cv2
import numpy as np
import config
import db
from face_utils import new_recogniser, save_labels


def main():
    people = sorted(p for p in config.FACES_DIR.glob("*") if p.is_dir())
    if not people:
        raise SystemExit(f"No enrolled workers in {config.FACES_DIR}. Run enroll.py first.")

    images, labels, table = [], [], {}
    for label, folder in enumerate(people):
        emp_id, _, name = folder.name.partition("_")
        name = name.replace("_", " ")
        files = list(folder.glob("*.png"))
        for f in files:
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            if img.shape != config.FACE_SIZE[::-1]:
                img = cv2.resize(img, config.FACE_SIZE)
            images.append(img)
            labels.append(label)
        table[label] = {"emp_id": emp_id, "name": name}
        db.upsert_worker(emp_id, name, label)
        print(f"  label {label:2d}  {emp_id:8s} {name:25s} {len(files)} samples")

    rec = new_recogniser()
    rec.train(images, np.array(labels))
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    rec.write(str(config.MODEL_FILE))
    save_labels(table)
    print(f"Trained on {len(images)} images / {len(table)} workers -> {config.MODEL_FILE}")


if __name__ == "__main__":
    main()
