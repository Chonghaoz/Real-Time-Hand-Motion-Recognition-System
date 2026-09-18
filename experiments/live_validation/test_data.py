import time
import serial
import pandas as pd
import os

PORT = "COM3"          # Change this to your serial port
BAUD = 115200
SECONDS = 20
OUTPUT_FILE = "esp32_live_features_translate_2.csv"

columns = [
    "gx", "gy", "gz",
    "lin_acc_mag",
    "gyro_mag",
    "gyro_diff",
    "lin_acc_diff",
    "gyro_avg",
    "gyro_var",
    "lin_acc_avg",
    "lin_acc_var",
    "lin_ax_avg",
    "lin_ay_avg",
    "lin_az_avg"
]

rows = []

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print(f"Collecting data for {SECONDS} seconds...")

start_time = time.time()

while time.time() - start_time < SECONDS:
    line = ser.readline().decode(errors="ignore").strip()

    if not line:
        continue

    # Skip header row
    if line.startswith("gx,gy,gz"):
        continue

    parts = line.split(",")

    if len(parts) != 14:
        continue

    try:
        values = list(map(float, parts))
        rows.append(values)
    except ValueError:
        continue

ser.close()

df = pd.DataFrame(rows, columns=columns)
df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {len(df)} rows to {os.path.abspath(OUTPUT_FILE)}")
print(df.head())