import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://external-seaweedfs:8333",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        connect_timeout=5,
        read_timeout=10,
        retries={"max_attempts": 2},
    ),
)

buckets = [item["Name"] for item in s3.list_buckets()["Buckets"]]
print("버킷:", buckets)

response = s3.get_object(
    Bucket="feature-data-sets",
    Key="demographic_features.parquet",
)
body = response["Body"]
try:
    header = body.read(4)
finally:
    body.close()

assert header == b"PAR1", f"예상과 다른 파일 헤더: {header!r}"
print("Pod → S3 인증·피처 파일 읽기: 성공")
