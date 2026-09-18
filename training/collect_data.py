"""Capture 14-feature motion samples streamed by the ESP32-S3 over serial."""

import argparse
import time
from pathlib import Path

import pandas as pd
import serial

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "raw"
FEATURE_COLUMNS = [
    "gx", "gy", "gz", "lin_acc_mag", "gyro_mag", "gyro_diff",
    "lin_acc_diff", "gyro_avg", "gyro_var", "lin_acc_avg",
    "lin_acc_var", "lin_ax_avg", "lin_ay_avg", "lin_az_avg",
]
VALID_LABELS = ("STILL", "TRANSLATE", "ROTATE", "SHAKE")


def parse_args():
    parser = argparse.ArgumentParser(description="Collect motion features from ESP32 serial output.")
    parser.add_argument("--port", required=True, help="Serial port, e.g. COM3 or /dev/ttyUSB0")
    parser.add_argument("--label", required=True, type=str.upper, choices=VALID_LABELS)
    parser.add_argument("--seconds", type=float, default=60.0, help="Recording duration (default: 60)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--session", default="", help="Optional session suffix, e.g. 1 -> translate1.csv")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DATA_DIR)
    return parser.parse_args()


def collect(port, baud, label, seconds):
    rows = []
    with serial.Serial(port, baud, timeout=1) as ser:
        time.sleep(2)  # Allow the board to reset after opening the serial port.
        print(f"Collecting {label} for {seconds:g} seconds from {port} @ {baud} baud...")
        start = time.time()
        while time.time() - start < seconds:
            line = ser.readline().decode(errors="ignore").strip()
            if not line or line.startswith("gx,gy,gz"):
                continue
            parts = line.split(",")
            if len(parts) != len(FEATURE_COLUMNS):
                continue
            try:
                rows.append([*map(float, parts), label])
            except ValueError:
                continue
    return rows


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    suffix = str(args.session).strip()
    filename = f"{args.label.lower()}{suffix}.csv"
    output = args.output_dir / filename

    rows = collect(args.port, args.baud, args.label, args.seconds)
    df = pd.DataFrame(rows, columns=FEATURE_COLUMNS + ["label"])
    df.to_csv(output, index=False)
    print(f"Saved {len(df)} rows to {output.resolve()}")


if __name__ == "__main__":
    main()
