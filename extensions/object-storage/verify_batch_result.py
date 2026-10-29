import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
import pandas as pd
from botocore.config import Config

prefix = Path('/batch-prefix').read_text().strip()
s3 = boto3.client('s3', endpoint_url='http://ml-platform-seaweedfs:8333', region_name='us-east-1',
    aws_access_key_id=os.environ['SEAWEED_ACCESS_KEY'], aws_secret_access_key=os.environ['SEAWEED_SECRET_KEY'],
    config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}))
response = s3.get_object(Bucket='feature-data-sets', Key=f'{prefix}/results/predictions.csv')
try:
    payload = response['Body'].read()
finally:
    response['Body'].close()
df = pd.read_csv(io.BytesIO(payload))
assert len(df) == 3
assert df['prediction'].isin([0, 1]).all()
assert df['probability_gt_50k'].between(0, 1).all()
sanitized = df[['prediction', 'probability_gt_50k', 'model_uri']].to_dict(orient='records')
report = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'operator': 'agent',
          'rows': len(df), 'predictions': sanitized, 'note': '개인 ID·실행별 경로를 제외한 실제 저장 결과'}
Path('/out/batch-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('실제 S3 예측 결과 3행 확인: 성공')
print(df[['prediction', 'probability_gt_50k']].to_string(index=False))
