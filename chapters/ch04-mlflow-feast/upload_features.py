import os
from pathlib import Path
import boto3
import pandas as pd
from botocore.config import Config

endpoint = "http://ml-platform-seaweedfs:8333"
bucket = os.environ.get("S3_FEATURE_BUCKET", "feature-data-sets")

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint,
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
    ),
)

storage_options = {
    "client_kwargs": {"endpoint_url": endpoint},
    "config_kwargs": {"s3": {"addressing_style": "path"}},
}

files = sorted(Path("feast/feature_data").glob("*.parquet"))
if len(files) != 3:
    raise ValueError(f"피처 파일 3개를 예상했지만 {len(files)}개입니다.")

for path in files:
    uri = f"s3://{bucket}/{path.name}"
    s3.upload_file(str(path), bucket, path.name)

    local = pd.read_parquet(path)
    remote = pd.read_parquet(
        uri,
        engine="pyarrow",
        storage_options=storage_options,
    )
    pd.testing.assert_frame_equal(local, remote)
    print(f"{path.name}: {remote.shape}, 원본과 일치")

print("\n피처 파일 3개 S3 업로드·읽기 검증: 성공")
