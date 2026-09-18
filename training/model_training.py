"""Train and evaluate the selected Decision Tree motion classifier."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from data_processing import FEATURE_COLUMNS, ROOT, load_dataset, prepare_train_test

RESULTS_DIR = ROOT / "results" / "figures"


def train_selected_model(verbose=True):
    dataset = load_dataset(verbose=verbose)
    X, y, X_train, X_test, y_train, y_test, scaler = prepare_train_test(dataset, verbose=verbose)
    tree = DecisionTreeClassifier(max_depth=10, min_samples_leaf=10, random_state=42)
    tree.fit(X_train, y_train)
    return tree, scaler, X, y, X_test, y_test


def evaluate(tree, X_test, y_test):
    y_pred = tree.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("\n===== Decision Tree =====")
    print("Accuracy:", accuracy)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    return y_pred


def run_cross_validation(X, y):
    # This preserves the cross-validation configuration used in the original project.
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("tree", DecisionTreeClassifier(
            random_state=42, max_depth=6, min_samples_leaf=8, min_samples_split=20
        )),
    ])
    scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
    print("\n===== 5-Fold Cross Validation =====")
    print("Fold accuracies:", scores)
    print("Mean accuracy:", scores.mean())
    print("Std accuracy:", scores.std())


def save_figures(tree, X_test, y_test, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    y_pred = tree.predict(X_test)
    cm = confusion_matrix(y_test, y_pred, labels=tree.classes_)
    fig, ax = plt.subplots(figsize=(7, 7))
    ConfusionMatrixDisplay(cm, display_labels=tree.classes_).plot(ax=ax, colorbar=False)
    ax.set_title("Decision Tree Confusion Matrix")
    fig.tight_layout()
    fig.savefig(output_dir / "confusion_matrix.png", dpi=180)
    plt.close(fig)

    importance = pd.DataFrame({"feature": FEATURE_COLUMNS, "importance": tree.feature_importances_})
    importance = importance.sort_values("importance", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(importance["feature"], importance["importance"])
    ax.invert_yaxis()
    ax.set_xlabel("Importance")
    ax.set_title("Decision Tree Feature Importance")
    fig.tight_layout()
    fig.savefig(output_dir / "feature_importance.png", dpi=180)
    plt.close(fig)
    return importance


def main():
    parser = argparse.ArgumentParser(description="Train and evaluate the motion classifier.")
    parser.add_argument("--save-plots", action="store_true", help="Regenerate figures under results/figures")
    args = parser.parse_args()

    tree, scaler, X, y, X_test, y_test = train_selected_model()
    evaluate(tree, X_test, y_test)
    run_cross_validation(X, y)

    importance = pd.DataFrame({"feature": FEATURE_COLUMNS, "importance": tree.feature_importances_})
    print("\nDecision Tree feature_importances_:")
    print(importance.sort_values("importance", ascending=False).to_string(index=False))
    if args.save_plots:
        save_figures(tree, X_test, y_test, RESULTS_DIR)
        print(f"\nSaved plots to {RESULTS_DIR}")

    print("\n===== Tree Complexity =====")
    print("Tree depth:", tree.get_depth())
    print("Number of nodes:", tree.tree_.node_count)
    print("Number of leaves:", tree.get_n_leaves())


if __name__ == "__main__":
    main()
