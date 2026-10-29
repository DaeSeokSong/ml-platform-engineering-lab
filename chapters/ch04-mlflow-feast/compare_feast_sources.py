from pathlib import Path
import pandas as pd
from feast_setup import store as local_store, root, groups
from feast_s3_setup import store as s3_store

data = pd.read_parquet(
    root / "feast" / "feature_data" / "demographic_features.parquet"
)
sample = data.head(3).reset_index(drop=True)

entity_df = pd.DataFrame({
    "user_id": sample["user_id"],
    "event_timestamp": (
        pd.to_datetime(sample["feature_timestamp"], utc=True)
        + pd.Timedelta(seconds=1)
    ),
})

features = [
    f"{view}:{column}"
    for view, _, columns in groups
    for column in columns
]
feature_columns = [name.replace(":", "__") for name in features]

def retrieve(store):
    result = store.get_historical_features(
        entity_df=entity_df,
        features=features,
        full_feature_names=True,
    ).to_df()

    if len(result) != len(entity_df):
        raise ValueError(
            f"{store.project}: 요청 {len(entity_df)}행, 반환 {len(result)}행"
        )

    columns = ["user_id", "event_timestamp"] + feature_columns
    return (
        result[columns]
        .sort_values(["user_id", "event_timestamp"])
        .reset_index(drop=True)
    )

local = retrieve(local_store)
remote = retrieve(s3_store)

assert remote[feature_columns].notna().all().all(), "결측 피처가 있습니다."
pd.testing.assert_frame_equal(local, remote)

out = Path("artifacts/feast")
out.mkdir(parents=True, exist_ok=True)
remote.to_csv(out / "s3_historical.csv", index=False)

print("로컬 조회 행 수:", len(local))
print("S3 조회 행 수:", len(remote))
print("비교한 피처 수:", len(feature_columns))
print("로컬·S3 Feast 조회 결과 일치: 성공")
print("저장 위치:", out / "s3_historical.csv")
