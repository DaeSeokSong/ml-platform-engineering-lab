import hashlib
import io
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError

BUCKET = 'storage-lab'
CONFIG = Config(signature_version='s3v4', s3={'addressing_style': 'path'}, connect_timeout=3, read_timeout=15, retries={'max_attempts': 2})

def client(prefix, endpoint, region):
    return boto3.client('s3', endpoint_url=endpoint, region_name=region,
        aws_access_key_id=os.environ[f'{prefix}_ACCESS_KEY'],
        aws_secret_access_key=os.environ[f'{prefix}_SECRET_KEY'], config=CONFIG)

def read(s3, bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    try:
        return response['Body'].read()
    finally:
        response['Body'].close()

clients = {
    'SeaweedFS': client('SEAWEED', 'http://ml-platform-seaweedfs:8333', 'us-east-1'),
    'Garage': client('GARAGE', 'http://ml-platform-garage:3900', 'garage'),
    'VersityGW': client('VERSITY', 'http://ml-platform-versitygw:7070', 'us-east-1'),
}
for name, s3 in clients.items():
    for attempt in range(30):
        try:
            s3.list_buckets()
            break
        except (EndpointConnectionError, ClientError):
            if attempt == 29:
                raise
            time.sleep(1)
    try:
        s3.head_bucket(Bucket=BUCKET)
    except ClientError as exc:
        if exc.response['ResponseMetadata']['HTTPStatusCode'] != 404:
            raise
        s3.create_bucket(Bucket=BUCKET)

source = clients['SeaweedFS']
payloads = {
    'roundtrip/check.json': json.dumps({'study': 'week02', 'message': '같은 클라이언트로 저장소 비교'}, ensure_ascii=False).encode(),
    'roundtrip/demographic_features.parquet': read(source, 'feature-data-sets', 'demographic_features.parquet'),
    'roundtrip/model.pkl': read(source, 'feature-data-sets', 'models/income-classifier-tree/1/model.pkl'),
}
records = []
for name, s3 in clients.items():
    for key, payload in payloads.items():
        s3.put_object(Bucket=BUCKET, Key=key, Body=payload)
        restored = read(s3, BUCKET, key)
        info = s3.head_object(Bucket=BUCKET, Key=key)
        keys = [obj['Key'] for obj in s3.list_objects_v2(Bucket=BUCKET, Prefix=key).get('Contents', [])]
        assert restored == payload and info['ContentLength'] == len(payload) and key in keys
        records.append({'backend': name, 'key': key, 'bytes': len(payload), 'sha256': hashlib.sha256(restored).hexdigest(), 'put_get_head_list': True})
        print(f'{name}: {key}, {len(payload)}바이트, 일치 확인')

posix = Path('/posix')
assert read(clients['VersityGW'], 'existing-bucket', 'from-filesystem.txt') == (posix / 'existing-bucket/from-filesystem.txt').read_bytes()
assert (posix / BUCKET / 'roundtrip/check.json').read_bytes() == payloads['roundtrip/check.json']
print('VersityGW: 기존 파일 → S3 조회, S3 업로드 → 실제 파일 일치 확인')
result = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'operator': 'agent',
    'versions': {'Garage': '2.5.0', 'VersityGW': '1.8.0', 'SeaweedFS': '4.51'},
    'cases': records, 'posix_to_s3': True, 's3_to_posix': True,
    'limits': ['단일 노드 실습', '성능·고가용성·S3 전체 API 검증 아님']}
Path('/out/comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('3개 저장소 × 3개 파일 검증: 성공')
