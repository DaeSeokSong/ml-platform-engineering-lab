from pathlib import Path
import pandas as pd
from feast_setup import store, root

data = pd.read_parquet(
    root / "feast" / "feature_data" / "demographic_features.parquet"
)
sample = data.sort_values("feature_timestamp").iloc[0]
timestamp = pd.to_datetime(sample["feature_timestamp"], utc=True)
before = timestamp - pd.Timedelta(seconds=1)
after = timestamp + pd.Timedelta(seconds=1)

entity_df = pd.DataFrame({
    "user_id": [sample["user_id"], sample["user_id"]],
    "event_timestamp": [before, after],
})

features = [
    "demographic:Sex",
    "demographic:Native_country",
    "demographic:Race",
]
columns = [feature.replace(":", "__") for feature in features]

returned = store.get_historical_features(
    entity_df=entity_df,
    features=features,
    full_feature_names=True,
).to_df()

result = entity_df.merge(
    returned,
    on=["user_id", "event_timestamp"],
    how="left",
    validate="one_to_one",
    indicator="return_status",
).sort_values("event_timestamp")

print("피처 발생 시점:", timestamp)
print("요청 행 수:", len(entity_df))
print("Feast 반환 행 수:", len(returned))
print(result.to_string(index=False))

before_values = result.loc[result["event_timestamp"].eq(before), columns]
after_values = result.loc[result["event_timestamp"].eq(after), columns]

assert before_values.isna().all().all(), "직전 요청에 피처 값이 반환됐습니다."
assert after_values.notna().all().all(), "직후 요청의 피처 값이 없습니다."

out = Path("artifacts/feast")
out.mkdir(parents=True, exist_ok=True)
returned.to_csv(out / "historical_raw.csv", index=False)
result.to_csv(out / "historical_check.csv", index=False)
print("\n직전 값 없음·직후 값 존재 확인: 성공")
