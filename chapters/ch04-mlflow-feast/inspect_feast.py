import os
from pathlib import Path
import pandas as pd
import redis

client = redis.Redis(
    host="ml-platform-feast-redis",
    port=6379,
    password=os.environ["FEAST_REDIS_PASSWORD"],
    socket_connect_timeout=5,
    socket_timeout=5,
)
print("Python에서 Redis 연결:", client.ping())

files = sorted(Path("feast/feature_data").glob("*.parquet"))
if not files:
    raise FileNotFoundError("피처 Parquet 파일을 찾지 못했습니다.")

for path in files:
    df = pd.read_parquet(path)
    print(f"\n파일: {path.name}")
    print("행·열:", df.shape)
    print("컬럼과 자료형:")
    print(df.dtypes.to_string())
    print("첫 번째 행:")
    print(df.head(1).to_string(index=False))

    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            print(f"시간 범위 [{column}]:",
                  df[column].min(), "~", df[column].max())
