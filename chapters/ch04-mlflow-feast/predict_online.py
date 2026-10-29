from pathlib import Path
import pandas as pd
import mlflow
import mlflow.sklearn
from feast_setup import store, root, groups

mlflow.set_tracking_uri("sqlite:///mlflow.db")
model_uri = Path("registered_model_uri.txt").read_text().strip()
model = mlflow.sklearn.load_model(model_uri)

sample = pd.read_parquet(
    root / "feast" / "feature_data" / "demographic_features.parquet"
).iloc[0]

features = [
    f"{view}:{column}"
    for view, _, columns in groups
    for column in columns
]
online = store.get_online_features(
    features=features,
    entity_rows=[{"user_id": sample["user_id"]}],
    full_feature_names=False,
).to_df()

inputs = online.loc[:, list(model.feature_names_in_)]
encoder = model.named_steps["encoder"]
unknown = []

for column, categories in zip(inputs.columns, encoder.categories_):
    value = inputs.iloc[0][column]
    known = value in categories
    print(column, repr(value), "일치" if known else "훈련 범주에 없음")

    if not known:
        unknown.append(column)
        matches = [
            repr(category) for category in categories
            if str(category).strip() == str(value).strip()
        ]
        print("  공백을 제외하면 같은 훈련 범주:", matches)

if unknown:
    raise ValueError(f"입력 범주 불일치로 예측 중단: {unknown}")

prediction = int(model.predict(inputs)[0])
probability = float(model.predict_proba(inputs)[0, 1])

print("\n사용한 모델:", model_uri)
print("예측 소득:", ">50K" if prediction == 1 else "<=50K")
print("고소득 확률:", round(probability, 4))
