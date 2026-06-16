from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "placement_data.csv"
MODEL_PATH = ROOT / "models" / "placement_model.joblib"
METRICS_PATH = ROOT / "models" / "model_metrics.txt"

FEATURES = [
    "gender",
    "branch",
    "graduation_year",
    "cgpa",
    "tenth_percent",
    "twelfth_percent",
    "internships",
    "projects",
    "certifications",
    "aptitude_score",
    "communication_score",
]

TARGET = "placed"


def build_pipeline() -> Pipeline:
    numeric_features = [
        "graduation_year",
        "cgpa",
        "tenth_percent",
        "twelfth_percent",
        "internships",
        "projects",
        "certifications",
        "aptitude_score",
        "communication_score",
    ]
    categorical_features = ["gender", "branch"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric_features),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=250,
                    max_depth=6,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    x = df[FEATURES]
    y = df[TARGET]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, zero_division=0)

    joblib.dump(pipeline, MODEL_PATH)
    METRICS_PATH.write_text(
        f"Accuracy: {accuracy:.2f}\n\nClassification Report:\n{report}",
        encoding="utf-8",
    )

    print(f"Saved model: {MODEL_PATH}")
    print(f"Accuracy: {accuracy:.2f}")


if __name__ == "__main__":
    main()
