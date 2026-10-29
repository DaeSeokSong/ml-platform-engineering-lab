import os
import pandas as pd
from feast import FeatureStore
from feast.repo_config import RepoConfig

endpoint = "http://external-seaweedfs:8333"
os.environ["FEAST_S3_ENDPOINT_URL"] = endpoint
os.environ["AWS_ENDPOINT_URL"] = endpoint

store = FeatureStore(config=RepoConfig(
    project="income_s3",
    provider="local",
    registry="s3://feature-registry/income_s3/registry.db",
    offline_store={"type": "file"},
    online_store={"type": "sqlite", "path": "/tmp/unused-online.db"},
    entity_key_serialization_version=2,
))

print("Feast 프로젝트:", store.project)
print("등록된 피처 뷰:",
      sorted(view.name for view in store.list_batch_feature_views()))

source = pd.read_parquet(
    "s3://feature-data-sets/demographic_features.parquet",
    storage_options={
        "client_kwargs": {"endpoint_url": endpoint},
        "config_kwargs": {"s3": {"addressing_style": "path"}},
    },
)

requests = source[["user_id", "feature_timestamp"]].head(3).copy()
requests["event_timestamp"] = (
    pd.to_datetime(requests["feature_timestamp"], utc=True)
    + pd.Timedelta(seconds=1)
)
requests = requests[["user_id", "event_timestamp"]]

features = [
    "demographic:Sex",
    "demographic:Native_country",
    "demographic:Race",
    "occupation:Workclass",
    "occupation:Education",
    "occupation:Occupation",
    "relationship:Relationship",
    "relationship:Marital-Status",
]

result = store.get_historical_features(
    entity_df=requests,
    features=features,
    full_feature_names=True,
).to_df()

columns = [feature.replace(":", "__") for feature in features]

assert len(result) == len(requests), "요청과 반환 행 수가 다릅니다."
assert not result[columns].isna().any().any(), "조회되지 않은 피처가 있습니다."

print("조회한 사용자 수:", len(result))
print("사용자별 피처 수:", len(columns))
print("Pod에서 Feast S3 과거 조회: 성공")
