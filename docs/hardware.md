# Hardware

The system runs on an ESP32-S3 development board with a QMI8658 six-axis IMU and a 1.28-inch round TFT display.

The firmware communicates with the QMI8658 over I2C at address `0x6B`, using SDA/SCL pins 6 and 7 in the project configuration. Accelerometer and gyroscope samples are filtered on-device before feature extraction.

The display is driven with `TFT_eSPI`. The third-party library itself is intentionally not vendored in this repository; install it separately in the Arduino environment and configure it for the target board/display.
