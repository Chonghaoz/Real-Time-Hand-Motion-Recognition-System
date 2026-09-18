# ESP32-S3 Real-Time Hand Motion Recognition

A real-time embedded motion-recognition system built on an ESP32-S3 with a QMI8658 six-axis IMU. The project covers the complete pipeline from sensor acquisition and signal processing to machine-learning training, manual model export, on-device inference, and TFT visualization.

## What it recognizes

The selected system classifies four motion states:

- `STILL` — stationary regardless of device orientation
- `TRANSLATE` — controlled linear movement
- `ROTATE` — rotational movement
- `SHAKE` — vigorous, irregular movement

## End-to-end pipeline

```text
QMI8658 IMU
  -> low-pass filtering
  -> gravity estimation / linear acceleration
  -> 5-sample sliding window
  -> 14 engineered motion features
  -> per-recording outlier removal
  -> StandardScaler
  -> Decision Tree
  -> C++ tree export
  -> ESP32-S3 inference
  -> majority voting + state-change confirmation
  -> TFT display
```

The deployed firmware also uses a lightweight stationary safeguard before Decision Tree inference to improve stability for clearly motionless inputs.

## Feature engineering

The final selected pipeline uses 14 features:

`gx`, `gy`, `gz`, `lin_acc_mag`, `gyro_mag`, `gyro_diff`, `lin_acc_diff`, `gyro_avg`, `gyro_var`, `lin_acc_avg`, `lin_acc_var`, `lin_ax_avg`, `lin_ay_avg`, `lin_az_avg`.

Gravity is estimated with a low-pass component and removed from filtered acceleration so the classifier can focus more directly on device motion rather than orientation alone. Windowed mean and variance features capture short-term temporal behavior while remaining inexpensive enough for embedded inference.

## Model and evaluation

The selected held-out Decision Tree configuration uses `max_depth=10` and `min_samples_leaf=10`. In the recorded final ML workspace it achieved approximately **98.13% held-out test accuracy**. A separate 5-fold cross-validation pipeline produced approximately **97.16% mean accuracy** with **0.70% standard deviation**.

The strongest Decision Tree features in that experiment were `lin_acc_avg`, `lin_acc_var`, and `gyro_avg`. See [`results/`](results/) for the recorded figures and details.

These are offline dataset results, not a claim of equivalent accuracy for arbitrary users or all real-world conditions. Live deployment exposed class overlap and motivated additional temporal stabilization.

## Embedded deployment

Instead of running a Python model on a host computer, the trained scikit-learn Decision Tree is exported into C++ arrays containing feature indices, thresholds, child-node indices, leaf flags, and predicted classes. StandardScaler mean/scale parameters are exported alongside the tree, allowing the ESP32-S3 to reproduce the preprocessing and tree traversal locally without cloud inference.

The runtime then applies a 3-prediction majority vote and requires repeated confirmation before changing the stable displayed state. The round TFT shows an animated visual for the current action.

## Repository structure

```text
firmware/
  data_collection/       ESP32 feature-streaming firmware
  motion_classifier/     on-device Decision Tree + TFT application
    model_data.h          generated tree/scaler parameters
training/
  collect_data.py        serial data capture
  data_processing.py     cleaning, splitting and scaling
  model_training.py      training and evaluation
  export_tree.py         export tree/scaler parameters to C++
data/raw/                 selected four-class recordings
results/                  metrics notes and figures
docs/                     hardware, architecture and development history
experiments/live_validation/  deployment debugging artifacts
```

## Setup

Python dependencies:

```bash
pip install -r requirements.txt
```

For data collection, flash `firmware/data_collection/data_collection.ino`, then run the collector with explicit command-line arguments. For example:

```bash
python training/collect_data.py --port COM3 --label TRANSLATE --session 3 --seconds 60
```

Valid labels are `STILL`, `TRANSLATE`, `ROTATE`, and `SHAKE`. The optional session suffix keeps repeated recordings separate (for example, `--session 3` creates `translate3.csv`).

To reproduce training from the repository root:

```bash
python training/model_training.py
```

To regenerate the evaluation figures as well:

```bash
python training/model_training.py --save-plots
```

To regenerate the C++ model header used by the firmware:

```bash
python training/export_tree.py
```

This writes `firmware/motion_classifier/model_data.h`, keeping generated model parameters separate from the application logic.

Arduino-side dependencies include `Wire`, `SPI`, and `TFT_eSPI`. The QMI8658 registers are accessed directly in the selected firmware.

## Project status and provenance

This repository documents a previously completed teaching/research project and was organized for publication after the original development work. The repository therefore does **not** fabricate historical Git commits. [`docs/development.md`](docs/development.md) records the real development stages based on the surviving project files and experiments.

A later 17-feature configuration was explored while investigating real-time generalization, but it is not used as the main version here because later does not necessarily mean better validated.
