# System Architecture

```text
QMI8658 IMU
    |
    v
Accelerometer + Gyroscope
    |
    v
Low-pass filtering
    |
    +-------------------+
    |                   |
    v                   v
Gravity estimation   Gyroscope signal
    |
    v
Linear acceleration
    |                   |
    +---------+---------+
              v
      Sliding window (5)
              |
              v
       14 motion features
              |
              v
       StandardScaler
              |
              v
  Stationary safeguard / Decision Tree
              |
              v
       Majority vote (3)
              |
              v
  State-change confirmation
              |
              v
        TFT visualization
```

The same feature ordering is used by the data-collection firmware, Python preprocessing/training code, and deployed classifier. This consistency is essential because the exported tree thresholds operate on standardized features.


## Training-to-firmware boundary

`training/export_tree.py` retrains the selected deterministic Decision Tree configuration and writes `firmware/motion_classifier/model_data.h`. The generated header contains the tree structure, class decisions, and StandardScaler parameters. Keeping these generated values outside the main `.ino` file makes the deployment path easier to audit and update without changing the runtime logic.
