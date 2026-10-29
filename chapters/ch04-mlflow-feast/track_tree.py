import pandas as pd
import mlflow
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("income-classification")

df = pd.read_csv("data/income_data.csv")
X = df.drop(columns="Target")
y = df["Target"].str.strip().eq(">50K").astype(int)

X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

model = Pipeline([
    ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ("classifier", DecisionTreeClassifier(max_depth=5, random_state=42)),
])

with mlflow.start_run(run_name="decision-tree-depth5") as run:
    mlflow.log_params({
        "model_type": "DecisionTreeClassifier",
        "max_depth": 5,
        "random_state": 42,
        "validation_fraction": 0.2,
        "stratified_split": True,
        "train_rows": len(X_train),
        "validation_rows": len(X_valid),
    })

    model.fit(X_train, y_train)

    for split, features, target in [
        ("train", X_train, y_train),
        ("valid", X_valid, y_valid),
    ]:
        mlflow.log_metrics({
            f"{split}_accuracy": accuracy_score(
                target, model.predict(features)
            ),
            f"{split}_auc": roc_auc_score(
                target, model.predict_proba(features)[:, 1]
            ),
        })

    mlflow.log_artifact("track_tree.py", artifact_path="code")
    mlflow.log_artifact("requirements.txt", artifact_path="environment")
    mlflow.log_artifact("constraints.local.txt", artifact_path="environment")
    mlflow.log_artifact("data/income_data.csv", artifact_path="data")
    run_id = run.info.run_id

saved = mlflow.get_run(run_id)
print("\nRun ID:", run_id)
print("상태:", saved.info.status)
print("기록된 모델:", saved.data.params["model_type"])
for name, value in sorted(saved.data.metrics.items()):
    print(f"{name}: {value:.4f}")
