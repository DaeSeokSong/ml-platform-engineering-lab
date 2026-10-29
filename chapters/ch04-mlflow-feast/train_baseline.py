import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

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
model.fit(X_train, y_train)

print("훈련/검증 행 수:", len(X_train), len(X_valid))
print("다수 클래스 기준 정확도:", round(1 - y_valid.mean(), 4))
for name, features, target in [
    ("훈련", X_train, y_train),
    ("검증", X_valid, y_valid),
]:
    prediction = model.predict(features)
    score = model.predict_proba(features)[:, 1]
    print(
        f"{name}: Accuracy={accuracy_score(target, prediction):.4f}, "
        f"ROC AUC={roc_auc_score(target, score):.4f}"
    )

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

candidates = {
    "RandomForest": RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=2
    ),
    "XGBoost": XGBClassifier(
        n_estimators=100, max_depth=5, learning_rate=0.1,
        objective="binary:logistic", eval_metric="logloss",
        random_state=42, n_jobs=2
    ),
}

for name, classifier in candidates.items():
    candidate = Pipeline([
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ("classifier", classifier),
    ])
    candidate.fit(X_train, y_train)

    print(f"\n{name}")
    for split, features, target in [
        ("훈련", X_train, y_train),
        ("검증", X_valid, y_valid),
    ]:
        prediction = candidate.predict(features)
        score = candidate.predict_proba(features)[:, 1]
        print(
            f"{split}: Accuracy={accuracy_score(target, prediction):.4f}, "
            f"ROC AUC={roc_auc_score(target, score):.4f}"
        )
