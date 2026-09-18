# Dataset

This directory contains the motion dataset used by the selected four-class pipeline.

Classes: `STILL`, `TRANSLATE`, `ROTATE`, and `SHAKE`.

Each CSV contains the 14 features emitted by the ESP32 data-collection firmware:

`gx`, `gy`, `gz`, `lin_acc_mag`, `gyro_mag`, `gyro_diff`, `lin_acc_diff`, `gyro_avg`, `gyro_var`, `lin_acc_avg`, `lin_acc_var`, `lin_ax_avg`, `lin_ay_avg`, `lin_az_avg`.

The training pipeline cleans each recording independently with basic NaN/duplicate removal followed by Isolation Forest (`contamination=0.03`). The dataset was collected for this project and is primarily single-user data, so the reported offline metrics should not be interpreted as broad user-independent performance.
