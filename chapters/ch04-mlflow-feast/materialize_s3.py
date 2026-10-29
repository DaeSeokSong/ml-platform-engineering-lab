from pathlib import Path
import pandas as pd
from feast_setup import store as local_store
from feast_s3_setup import store as s3_store, groups

entity_rows = (
    pd.read_csv("artifacts/feast/s3_historical.csv")[["user_id"]]
    .to_dict("records")
)

features = [
    f"{view}:{column}"
    for view, _, columns in groups
    for column in columns
]
feature_columns = [name.replace(":", "__") for name in features]

def online(store):
    result = store.get_online_features(
        features=features,
        entity_rows=entity_rows,
        full_feature_names=True,
    ).to_df()
    return (
        result[["user_id"] + feature_columns]
        .sort_values("user_id")
        .reset_index(drop=True)
    )

before = online(s3_store)
print("적재 전 조회된 피처 값 수:",
      int(before[feature_columns].notna().sum().sum()))

s3_store.materialize(
    start_date=pd.Timestamp("2022-09-16T08:24:02Z").to_pydatetime(),
    end_date=pd.Timestamp("2023-09-16T13:47:28Z").to_pydatetime(),
)

local = online(local_store)
remote = online(s3_store)

assert remote[feature_columns].notna().all().all(), "결측 피처가 있습니다."
pd.testing.assert_frame_equal(local, remote)

out = Path("artifacts/feast")
out.mkdir(parents=True, exist_ok=True)
remote.to_csv(out / "s3_online.csv", index=False)

print("\n적재 후 조회된 피처 값 수:",
      int(remote[feature_columns].notna().sum().sum()))
print("비교 사용자 수:", len(remote))
print("사용자별 피처 수:", len(feature_columns))
print("로컬·S3 프로젝트 온라인 조회 결과 일치: 성공")
