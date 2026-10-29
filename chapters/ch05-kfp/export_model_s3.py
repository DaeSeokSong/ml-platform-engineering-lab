import hashlib
import json
import tempfile
from pathlib import Path

import boto3
import mlflow
from botocore.config import Config

mlflow.set_tracking_uri("sqlite:////workspace/mlflow.db")
mlflow.set_registry_uri("sqlite:////workspace/mlflow.db")

model_uri = Path("registered_model_uri.txt").read_text().strip()
model_dir = Path(mlflow.artifacts.download_artifacts(
    artifact_uri=model_uri,
    dst_path=tempfile.mkdtemp(prefix="model-export-"),
))

assert (model_dir / "MLmodel").is_file(), "MLflow 모델 설명 파일이 없습니다."
print("원본 모델:", model_uri)

s3 = boto3.client(
    "s3",
    endpoint_url="http://ml-platform-seaweedfs:8333",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        connect_timeout=5,
        read_timeout=30,
    ),
)

bucket = "feature-data-sets"
prefix = "models/income-classifier-tree/1"
files = {}

for path in sorted(model_dir.rglob("*")):
    if not path.is_file():
        continue

    relative = path.relative_to(model_dir).as_posix()
    key = f"{prefix}/{relative}"
    original_hash = hashlib.sha256(path.read_bytes()).hexdigest()

    s3.upload_file(str(path), bucket, key)
    response = s3.get_object(Bucket=bucket, Key=key)
    try:
        downloaded_hash = hashlib.sha256(response["Body"].read()).hexdigest()
    finally:
        response["Body"].close()

    assert original_hash == downloaded_hash, f"파일 불일치: {relative}"
    files[relative] = original_hash
    print("복사·일치 확인:", relative)

manifest = {
    "source_model_uri": model_uri,
    "files": files,
}
s3.put_object(
    Bucket=bucket,
    Key=f"{prefix}/manifest.json",
    Body=json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"),
    ContentType="application/json",
)

print("모델 저장 위치:", f"s3://{bucket}/{prefix}/")
print("검증한 모델 파일 수:", len(files))
print("모델 S3 복사·무결성 확인: 성공")
