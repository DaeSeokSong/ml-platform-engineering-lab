import os
from datetime import timedelta
import boto3
from botocore.config import Config
from feast import Entity, FeatureStore, FeatureView, Field, FileSource, ValueType
from feast.types import String
from feast.repo_config import RepoConfig

endpoint = os.environ["FEAST_S3_ENDPOINT_URL"]
registry_bucket = os.environ.get("S3_REGISTRY_BUCKET", "feature-registry")
project = os.environ.get("FEAST_S3_PROJECT", "income_s3")
feature_bucket = os.environ.get("S3_FEATURE_BUCKET", "feature-data-sets")
registry_uri = f"s3://{registry_bucket}/{project}/registry.db"

config = RepoConfig(
    project=project,
    provider="local",
    registry=registry_uri,
    offline_store={"type": "file"},
    online_store={
        "type": "redis",
        "connection_string": (
            "ml-platform-feast-redis:6379,password="
            + os.environ["FEAST_REDIS_PASSWORD"]
        ),
    },
    entity_key_serialization_version=2,
)
store = FeatureStore(config=config)

user = Entity(
    name="user",
    join_keys=["user_id"],
    value_type=ValueType.STRING,
)

groups = [
    ("demographic", "demographic_features.parquet",
     ["Sex", "Native_country", "Race"]),
    ("occupation", "occupational_features.parquet",
     ["Workclass", "Education", "Occupation"]),
    ("relationship", "relationship_features.parquet",
     ["Relationship", "Marital-Status"]),
]

definitions = [user]
for name, filename, columns in groups:
    source = FileSource(
        path=f"s3://{feature_bucket}/{filename}",
        timestamp_field="feature_timestamp",
        s3_endpoint_override=endpoint,
    )
    definitions.append(FeatureView(
        name=name,
        entities=[user],
        ttl=timedelta(days=365),
        schema=[Field(name=column, dtype=String) for column in columns],
        source=source,
    ))

if __name__ == "__main__":
    store.apply(definitions)
    print("프로젝트:", store.project)
    print("등록된 피처 뷰:",
          sorted(view.name for view in store.list_batch_feature_views()))

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        config=Config(s3={"addressing_style": "path"}),
    )
    metadata = s3.head_object(
        Bucket=registry_bucket,
        Key=f"{project}/registry.db",
    )
    print("레지스트리 주소:", registry_uri)
    print("S3 레지스트리 크기:", metadata["ContentLength"], "bytes")
