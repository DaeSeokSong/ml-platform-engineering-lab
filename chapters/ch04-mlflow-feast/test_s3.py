import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://ml-platform-seaweedfs:8333",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        retries={"mode": "standard", "max_attempts": 5},
        connect_timeout=3,
        read_timeout=10,
    ),
)

print("버킷:", [item["Name"] for item in s3.list_buckets()["Buckets"]])

bucket = "feature-data-sets"
key = "checks/connection.txt"
original = b"ml-platform-s3-check"

s3.put_object(Bucket=bucket, Key=key, Body=original)
downloaded = s3.get_object(Bucket=bucket, Key=key)["Body"].read()

assert downloaded == original, "업로드한 내용과 다운로드한 내용이 다릅니다."
print("객체 경로:", f"s3://{bucket}/{key}")
print("업로드·다운로드 내용 일치: 성공")
