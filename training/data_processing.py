"""Dataset loading, per-recording outlier removal, splitting, and scaling."""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw"

FEATURE_COLUMNS = [
    "gx", "gy", "gz", "lin_acc_mag", "gyro_mag", "gyro_diff",
    "lin_acc_diff", "gyro_avg", "gyro_var", "lin_acc_avg",
    "lin_acc_var", "lin_ax_avg", "lin_ay_avg", "lin_az_avg",
]
LABEL_FILES = {
    "STILL": ["still.csv", "still1.csv", "still2.csv"],
    "SHAKE": ["shake.csv", "shake1.csv", "shake2.csv"],
    "ROTATE": ["rotate.csv", "rotate1.csv", "rotate2.csv"],
    "TRANSLATE": ["translate.csv", "translate1.csv", "translate2.csv"],
}


def clean_single_file(file_path, label, contamination=0.03, n_estimators=200,
                      random_state=42, min_rows_for_iforest=50, verbose=True):
    file_path = Path(file_path)
    df = pd.read_csv(file_path)
    missing = [column for column in FEATURE_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"{file_path} is missing required columns: {missing}")

    df = df[FEATURE_COLUMNS].dropna().drop_duplicates().copy()
    after_basic = len(df)

    if len(df) >= min_rows_for_iforest:
        detector = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
        )
        mask = detector.fit_predict(df[FEATURE_COLUMNS]) == 1
        df = df.loc[mask].copy()

    if verbose:
        print(
            f"{file_path.name:<15} label={label:<9} "
            f"after_basic={after_basic:>5} after_iforest={len(df):>5} "
            f"removed={after_basic - len(df):>4}"
        )
    df["label"] = label
    return df


def load_dataset(data_dir=DATA_DIR, verbose=True):
    data_dir = Path(data_dir)
    groups = []
    for label, filenames in LABEL_FILES.items():
        parts = [clean_single_file(data_dir / name, label, verbose=verbose) for name in filenames]
        groups.append(pd.concat(parts, ignore_index=True))
    dataset = pd.concat(groups, ignore_index=True)
    if verbose:
        print("\n===== Final merged dataset =====")
        print("Dataset size:", dataset.shape)
        print(dataset["label"].value_counts())
    return dataset


def prepare_train_test(dataset, test_size=0.2, random_state=42, verbose=True):
    X = dataset[FEATURE_COLUMNS]
    y = dataset["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    if verbose:
        print("\nTraining set size:", X_train.shape)
        print("Test set size:", X_test.shape)
    return X, y, X_train_scaled, X_test_scaled, y_train, y_test, scaler
