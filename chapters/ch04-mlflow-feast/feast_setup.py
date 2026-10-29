import os
from pathlib import Path
from datetime import timedelta
from feast import Entity, FeatureStore, FeatureView, Field, FileSource, ValueType
from feast.types import String
from feast.repo_config import RepoConfig

root = Path(__file__).resolve().parent
registry_dir = root / "feast-local"
registry_dir.mkdir(exist_ok=True)

config = RepoConfig(
    project=os.environ.get("FEAST_PROJECT", "income_features"),
    provider="local",
    registry=str(registry_dir / "registry.db"),
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
        path=str(root / "feast" / "feature_data" / filename),
        timestamp_field="feature_timestamp",
    )
    view = FeatureView(
        name=name,
        entities=[user],
        ttl=timedelta(days=365),
        schema=[Field(name=column, dtype=String) for column in columns],
        source=source,
    )
    definitions.append(view)
