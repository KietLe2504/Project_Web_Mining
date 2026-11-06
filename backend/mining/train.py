import argparse
import warnings

import pandas as pd
import xgboost as xgb
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

from .config import ARTIFACT_DIR, RANDOM_STATE, RESULTS_PATH, TARGET, TEST_SIZE
from .data import (
    apply_encoders,
    compute_defaults,
    expand_dates,
    fill_missing,
    fit_encoders,
    load_training_frame,
    select_feature_columns,
)
from .model_store import save_bundle

warnings.filterwarnings("ignore")


def build_models():
    return {
        "logistic_regression": ("Logistic Regression", LogisticRegression(max_iter=300, C=0.001, penalty="l2")),
        "naive_bayes": ("Naive Bayes", GaussianNB(var_smoothing=0.01)),
        "decision_tree": (
            "Decision Trees",
            DecisionTreeClassifier(max_depth=None, min_samples_leaf=1, min_samples_split=5),
        ),
        "gradient_boosting": (
            "Gradient Boosting",
            GradientBoostingClassifier(learning_rate=0.1, max_depth=4, n_estimators=50),
        ),
        "xgboost": (
            "XGBoost",
            xgb.XGBClassifier(random_state=0, learning_rate=0.01, max_depth=3, n_estimators=50),
        ),
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nrows", type=int, default=500000)
    parser.add_argument("--serve-model", choices=list(build_models()), default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    nrows = args.nrows if args.nrows > 0 else None

    frame = fill_missing(load_training_frame(nrows))
    defaults = compute_defaults(frame)
    frame = expand_dates(frame)
    feature_columns = select_feature_columns(frame)
    encoders = fit_encoders(frame, feature_columns)
    x = apply_encoders(frame[feature_columns], encoders)
    y = frame[TARGET]
    print("Feature matrix:", x.shape)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print("Training set:", x_train.shape, "Test set:", x_test.shape)

    rows = []
    fitted = {}
    for key, (label, model) in build_models().items():
        print(f"\n=== {label} ===")
        model.fit(x_train, y_train)
        train_acc = accuracy_score(y_train, model.predict(x_train))
        test_pred = model.predict(x_test)
        test_acc = accuracy_score(y_test, test_pred)
        print(f"Training accuracy: {train_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        print(classification_report(y_test, test_pred))
        rows.append({"key": key, "Model": label, "Training Accuracy": train_acc, "Test Accuracy": test_acc})
        fitted[key] = model

    results = pd.DataFrame(rows).sort_values(by="Test Accuracy", ascending=False)
    print("\n=== Model comparison ===")
    print(results.drop(columns="key").to_string(index=False))

    serve_key = args.serve_model or results.iloc[0]["key"]
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_PATH, index=False)
    save_bundle(
        {
            "model": fitted[serve_key],
            "model_name": serve_key,
            "feature_columns": feature_columns,
            "encoders": encoders,
            "defaults": defaults,
        }
    )
    print(f"\nSaved model '{serve_key}' to {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
