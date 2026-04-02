"""
train_model.py — Train a TinyML car-detection model for XIAO ESP32S3
=====================================================================
Trains a small CNN on parking slot images, quantizes to TFLite int8,
and writes the model bytes as a C array to model.h.

Dataset source
--------------
This script can download directly from Roboflow:
  Workspace : dataworld
  Project   : carparking-6tcct

Usage
-----
  # Download dataset from Roboflow + train:
  python train_model.py --api-key YOUR_ROBOFLOW_KEY

  # Use local images only (no Roboflow):
  python train_model.py

  # Get your API key: https://app.roboflow.com → Settings → API Keys

Local data layout (used when --api-key is not provided, OR combined with downloaded data)
  data/available/  →  images of empty parking slots
  data/occupied/   →  images of slots with a car

How Roboflow data is mapped to classes
---------------------------------------
The carparking-6tcct dataset is an object-detection dataset where
bounding boxes mark cars in parking slots.

  Image has ≥ 1 bounding box  →  occupied
  Image has 0 bounding boxes  →  available

Downloaded images are auto-sorted into data/available/ and data/occupied/
so you can inspect or add to them before training.

Output
------
  model.tflite  — quantized TFLite model (~50-150 KB)
  model.h       — C array for Arduino sketch
"""

import os
import sys
import shutil
import pathlib
import argparse
import numpy as np

# ── dependency check ─────────────────────────────────────────────────────────
try:
    import tensorflow as tf
except ImportError:
    sys.exit("TensorFlow not found.\n  pip install -r requirements.txt")

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow not found.\n  pip install -r requirements.txt")

# ── config ────────────────────────────────────────────────────────────────────
IMG_WIDTH  = 96
IMG_HEIGHT = 96
CHANNELS   = 1          # grayscale — matches PIXFORMAT_GRAYSCALE on ESP32
BATCH_SIZE = 16
EPOCHS     = 30

ROBOFLOW_WORKSPACE = "dataworld"
ROBOFLOW_PROJECT   = "carparking-6tcct"
ROBOFLOW_VERSION   = 1              # bump if the dataset has multiple versions

DATA_DIR   = pathlib.Path("data")
# Write outputs to /training/out when inside Docker, else current directory
_out_dir   = pathlib.Path("/training/out") if pathlib.Path("/training/out").exists() else pathlib.Path(".")
OUT_TFLITE = _out_dir / "model.tflite"
OUT_HEADER = _out_dir / "model.h"

CLASSES = ["available", "occupied"]  # index 0 = available, 1 = occupied

# ── Roboflow download ─────────────────────────────────────────────────────────
def download_roboflow(api_key: str, version: int = ROBOFLOW_VERSION):
    """
    Downloads the carparking-6tcct dataset from Roboflow in YOLOv5 format,
    then sorts images into data/available/ and data/occupied/ based on whether
    annotation files contain bounding boxes.
    """
    try:
        from roboflow import Roboflow
    except ImportError:
        sys.exit("roboflow package not found.\n  pip install roboflow")

    print(f"Roboflow: connecting to {ROBOFLOW_WORKSPACE}/{ROBOFLOW_PROJECT} v{version}...")
    rf       = Roboflow(api_key=api_key)
    project  = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)
    rf_ver   = project.version(version)

    # Download as YOLOv5 PyTorch format — gives us images + per-image .txt annotations
    dl_path = pathlib.Path("roboflow_download")
    rf_ver.download("yolov5pytorch", location=str(dl_path))
    print(f"Roboflow: downloaded to {dl_path}")

    # Sort images into classification folders
    avail_dir = DATA_DIR / "available"
    occ_dir   = DATA_DIR / "occupied"
    avail_dir.mkdir(parents=True, exist_ok=True)
    occ_dir.mkdir(parents=True, exist_ok=True)

    n_avail = n_occ = 0
    img_exts = {".jpg", ".jpeg", ".png", ".bmp"}

    # Walk all train/valid/test splits
    for split in ("train", "valid", "test"):
        img_folder   = dl_path / split / "images"
        label_folder = dl_path / split / "labels"
        if not img_folder.exists():
            continue

        for img_path in img_folder.iterdir():
            if img_path.suffix.lower() not in img_exts:
                continue

            label_path = label_folder / (img_path.stem + ".txt")

            # Occupied = annotation file exists AND is non-empty
            is_occupied = (label_path.exists() and
                           label_path.stat().st_size > 0 and
                           label_path.read_text().strip() != "")

            dest_dir = occ_dir if is_occupied else avail_dir
            dest     = dest_dir / img_path.name
            # Avoid overwriting if same name exists from another split
            if dest.exists():
                dest = dest_dir / f"{split}_{img_path.name}"
            shutil.copy2(img_path, dest)

            if is_occupied:
                n_occ += 1
            else:
                n_avail += 1

    print(f"Roboflow: sorted {n_occ} occupied, {n_avail} available images into {DATA_DIR}/")

    if n_avail == 0:
        print("WARNING: 0 available (empty slot) images found in dataset.")
        print("  The Roboflow dataset may only contain images with cars.")
        print("  Add your own empty-slot photos to data/available/ before training.")

    return n_occ + n_avail

# ── load images ───────────────────────────────────────────────────────────────
def load_dataset():
    images, labels = [], []
    for label_idx, class_name in enumerate(CLASSES):
        folder = DATA_DIR / class_name
        if not folder.exists():
            print(f"WARNING: {folder} not found — skipping class '{class_name}'")
            continue

        img_files = [f for f in folder.iterdir()
                     if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}]

        if len(img_files) < 10:
            print(f"WARNING: only {len(img_files)} images in {folder} (recommend ≥ 50)")

        for img_path in img_files:
            try:
                img = Image.open(img_path).convert("L")           # → grayscale
                img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.LANCZOS)
                arr = np.array(img, dtype=np.float32) / 255.0    # → [0, 1]
                images.append(arr)
                labels.append(label_idx)
            except Exception as e:
                print(f"  Skipped {img_path.name}: {e}")

    if len(images) == 0:
        sys.exit(
            "No images found.\n"
            "  Option A: python train_model.py --api-key YOUR_KEY  (download from Roboflow)\n"
            "  Option B: add images to data/available/ and data/occupied/"
        )

    counts = [labels.count(i) for i in range(len(CLASSES))]
    print(f"Loaded {len(images)} images — " +
          ", ".join(f"{CLASSES[i]}: {counts[i]}" for i in range(len(CLASSES))))

    X = np.array(images)[..., np.newaxis]                         # [N, 96, 96, 1]
    y = tf.keras.utils.to_categorical(labels, num_classes=len(CLASSES))
    return X, y

# ── model architecture ────────────────────────────────────────────────────────
# Small CNN designed to fit in ~100 KB on ESP32S3 after int8 quantization.
# Fast inference (~80-120 ms on ESP32S3 at 240 MHz).
def build_model():
    return tf.keras.Sequential([
        tf.keras.layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, CHANNELS)),

        tf.keras.layers.Conv2D(16, 3, padding="same", activation="relu"),
        tf.keras.layers.MaxPooling2D(),      # 96 → 48

        tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu"),
        tf.keras.layers.MaxPooling2D(),      # 48 → 24

        tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu"),
        tf.keras.layers.MaxPooling2D(),      # 24 → 12

        tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu"),
        tf.keras.layers.GlobalAveragePooling2D(),

        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(len(CLASSES), activation="softmax"),
    ])

# ── TFLite conversion (int8 quantized) ───────────────────────────────────────
def convert_to_tflite(keras_model, X_rep):
    def representative_dataset():
        for i in range(min(200, len(X_rep))):
            yield [X_rep[i : i + 1].astype(np.float32)]

    converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type  = tf.int8
    converter.inference_output_type = tf.int8

    tflite_bytes = converter.convert()
    OUT_TFLITE.write_bytes(tflite_bytes)
    print(f"Saved: {OUT_TFLITE}  ({len(tflite_bytes) / 1024:.1f} KB)")
    return tflite_bytes

# ── write C header ────────────────────────────────────────────────────────────
def write_header(model_bytes):
    lines = [
        "// model.h — auto-generated by train_model.py",
        "// DO NOT EDIT — regenerate with: python train_model.py",
        "//",
        f"// Source    : roboflow.com/{ROBOFLOW_WORKSPACE}/{ROBOFLOW_PROJECT}",
        f"// Model size: {len(model_bytes)} bytes ({len(model_bytes) / 1024:.1f} KB)",
        f"// Input     : [1, {IMG_HEIGHT}, {IMG_WIDTH}, {CHANNELS}]  int8",
        f"// Output    : [1, {len(CLASSES)}]  classes: {CLASSES}",
        "",
        "const unsigned char g_model[] = {",
    ]

    row = []
    for i, byte in enumerate(model_bytes):
        row.append(f"0x{byte:02x}")
        if len(row) == 12 or i == len(model_bytes) - 1:
            lines.append("  " + ", ".join(row) + ",")
            row = []

    lines += [
        "};",
        f"const unsigned int g_model_len = {len(model_bytes)};",
        "",
    ]

    OUT_HEADER.write_text("\n".join(lines))
    print(f"Saved: {OUT_HEADER}")

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Train TinyML parking detector")
    parser.add_argument(
        "--api-key", metavar="KEY",
        help="Roboflow API key (get from app.roboflow.com → Settings → API Keys)"
    )
    parser.add_argument(
        "--version", type=int, default=ROBOFLOW_VERSION,
        help=f"Roboflow dataset version (default: {ROBOFLOW_VERSION})"
    )
    args = parser.parse_args()

    print("=" * 56)
    print("  TinyML Parking Detector — Model Training")
    print(f"  Dataset : {ROBOFLOW_WORKSPACE}/{ROBOFLOW_PROJECT}")
    print(f"  Input   : {IMG_WIDTH}×{IMG_HEIGHT} grayscale")
    print(f"  Classes : {CLASSES}")
    print("=" * 56)

    # Download from Roboflow if key provided
    if args.api_key:
        download_roboflow(args.api_key, version=args.version)
    else:
        print("No --api-key provided — using local data/ directory only.")
        print(f"  To download from Roboflow: python train_model.py --api-key YOUR_KEY\n")

    X, y = load_dataset()

    # Train/val split (80/20, stratified-ish)
    idx   = np.random.permutation(len(X))
    split = int(0.8 * len(X))
    X_train, y_train = X[idx[:split]], y[idx[:split]]
    X_val,   y_val   = X[idx[split:]], y[idx[split:]]
    print(f"Split — train: {len(X_train)}  val: {len(X_val)}")

    # Augmentation — critical when dataset is small
    augment = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomBrightness(0.15),
        tf.keras.layers.RandomContrast(0.15),
    ])

    train_ds = (
        tf.data.Dataset.from_tensor_slices((X_train, y_train))
        .shuffle(1000)
        .map(lambda x, y: (augment(x, training=True), y),
             num_parallel_calls=tf.data.AUTOTUNE)
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )
    val_ds = (
        tf.data.Dataset.from_tensor_slices((X_val, y_val))
        .batch(BATCH_SIZE)
        .prefetch(tf.data.AUTOTUNE)
    )

    model = build_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    print(f"\nTraining for up to {EPOCHS} epochs...")
    model.fit(
        train_ds, validation_data=val_ds, epochs=EPOCHS,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_accuracy", patience=8, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=4, min_lr=1e-5),
        ]
    )

    loss, acc = model.evaluate(val_ds, verbose=0)
    print(f"\nVal accuracy: {acc * 100:.1f}%")
    if acc < 0.80:
        print("WARNING: accuracy below 80%.")
        print("  → Add more training images (especially empty slots)")
        print("  → Make sure images match your actual camera angle/lighting")

    tflite_bytes = convert_to_tflite(model, X_train)
    write_header(tflite_bytes)

    print()
    print("Next steps:")
    print(f"  1. cp {OUT_HEADER} ../parking_sensor/model.h")
    print("  2. Re-upload the Arduino sketch")


if __name__ == "__main__":
    main()
