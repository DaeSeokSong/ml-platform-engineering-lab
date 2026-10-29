from pathlib import Path
import pandas as pd
from feast_setup import store, root, groups

tables = [
    pd.read_parquet(root / "feast" / "feature_data" / filename)
    for _, filename, _ in groups
]

timestamps = pd.concat([
    pd.to_datetime(table["feature_timestamp"], utc=True)
    for table in tables
], ignore_index=True)

start = timestamps.min() - pd.Timedelta(seconds=1)
end = timestamps.max() + pd.Timedelta(seconds=1)

entity_rows = [{"user_id": tables[0].iloc[0]["user_id"]}]
features = [
    f"{view}:{column}"
    for view, _, columns in groups
    for column in columns
]

before = store.get_online_features(
    features=features,
    entity_rows=entity_rows,
    full_feature_names=True,
).to_df()

print("적재 전 온라인 조회:")
print(before.T.to_string())
print("\n적재 기간:", start, "~", end)

store.materialize(
    start_date=start.to_pydatetime(),
    end_date=end.to_pydatetime(),
)

after = store.get_online_features(
    features=features,
    entity_rows=entity_rows,
    full_feature_names=True,
).to_df()

print("\n적재 후 온라인 조회:")
print(after.T.to_string())

feature_columns = [name.replace(":", "__") for name in features]
assert after[feature_columns].notna().all().all(), "일부 피처 값이 없습니다."

out = Path("artifacts/feast")
out.mkdir(parents=True, exist_ok=True)
before.to_csv(out / "online_before.csv", index=False)
after.to_csv(out / "online_after.csv", index=False)
print("\n피처 8개 온라인 조회: 성공")
