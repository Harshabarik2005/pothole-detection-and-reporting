# save as final_dataset/split_dataset.py
import os, shutil, random, pathlib

# auto-locate script folder so relative paths always work
HERE = pathlib.Path(__file__).resolve().parent
DATASET_ROOT = HERE
TRAIN_RATIO = 0.8
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

images_dir = DATASET_ROOT / "images"
labels_dir = DATASET_ROOT / "labels"

train_img = DATASET_ROOT / "train" / "images"
train_lbl = DATASET_ROOT / "train" / "labels"
val_img   = DATASET_ROOT / "val" / "images"
val_lbl   = DATASET_ROOT / "val" / "labels"

for d in [train_img, train_lbl, val_img, val_lbl]:
    d.mkdir(parents=True, exist_ok=True)

pairs = []
for p in images_dir.glob("*"):
    if p.suffix.lower() in IMG_EXTS:
        lbl = labels_dir / (p.stem + ".txt")
        if lbl.exists():
            pairs.append((p, lbl))

if not pairs:
    raise SystemExit("No matched image/label pairs found. Check filenames and extensions.")

random.shuffle(pairs)
k = int(len(pairs)*TRAIN_RATIO)
train_pairs, val_pairs = pairs[:k], pairs[k:]

def copy_pairs(items, di, dl):
    for img, lbl in items:
        shutil.copy2(img, di / img.name)
        shutil.copy2(lbl, dl / lbl.name)

copy_pairs(train_pairs, train_img, train_lbl)
copy_pairs(val_pairs,   val_img,   val_lbl)

print(f"Total: {len(pairs)} | Train: {len(train_pairs)} | Val: {len(val_pairs)}")
print("Done. Folders created under:", DATASET_ROOT)
