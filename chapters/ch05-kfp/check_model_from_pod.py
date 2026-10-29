import hashlib
import json
import tempfile
from pathlib import Path

import boto3
import mlflow.sklearn
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://external-seaweedfs:8333",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        connect_timeout=5,
        read_timeout=30,
    ),
)

bucket = "feature-data-sets"
prefix = "models/income-classifier-tree/1"

response = s3.get_object(Bucket=bucket, Key=f"{prefix}/manifest.json")
try:
    manifest = json.loads(response["Body"].read())
finally:
    response["Body"].close()

model_dir = Path(tempfile.mkdtemp(prefix="model-"))

for relative, expected_hash in manifest["files"].items():
    path = model_dir / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, f"{prefix}/{relative}", str(path))

    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual_hash == expected_hash, f"파일 불일치: {relative}"

print("검증한 모델 파일 수:", len(manifest["files"]))

model = mlflow.sklearn.load_model(str(model_dir))

print("원본 모델:", manifest["source_model_uri"])
print("로드한 객체:", type(model).__name__)
print("입력 피처 수:", len(model.feature_names_in_))
print("Pod에서 S3 모델 로드: 성공")
