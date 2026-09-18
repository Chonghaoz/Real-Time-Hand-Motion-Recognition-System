# Development History

This repository was assembled after the original project work. The stages below document the actual development process rather than pretending that the current Git history is the original development history.

1. **IMU bring-up** — established QMI8658 I2C communication and verified accelerometer/gyroscope readings.
2. **Rule-based prototype** — explored motion thresholds using acceleration tilt and gyroscope magnitude.
3. **Early ML experiments** — collected labeled serial data and evaluated KNN and Decision Tree classifiers.
4. **Class redesign** — moved from an orientation-oriented `TILT` class to the motion classes `STILL`, `TRANSLATE`, `ROTATE`, and `SHAKE`.
5. **Linear-acceleration pipeline** — estimated gravity, derived linear acceleration, and built a 14-feature sliding-window representation.
6. **Data cleaning and training** — applied per-recording Isolation Forest cleaning, StandardScaler, train/test evaluation, and cross-validation.
7. **Embedded deployment** — exported the Decision Tree and scaler parameters as C++ arrays and reproduced inference directly on the ESP32-S3.
8. **Real-time stabilization** — added a stationary safeguard, majority voting, and state-change confirmation after live testing exposed differences between offline and deployed behavior.
9. **Later experiments** — additional feature configurations were explored after the selected version.
