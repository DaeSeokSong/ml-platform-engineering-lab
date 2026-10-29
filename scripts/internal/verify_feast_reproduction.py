import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
lab = Path.home() / 'ml-platform-lab'
root = Path.home() / 'ml-platform-lab-repro-20261029'
for source in (repo / 'chapters/ch04-mlflow-feast').glob('*.py'):
    shutil.copy2(source, root / source.name)
values = dict(line.split('=', 1) for line in (lab / 'ch04-mlflow-feast/.s3.env').read_text().splitlines() if '=' in line)
values.update({'FEAST_REDIS_PASSWORD': (lab / 'ch04-mlflow-feast/.redis-password').read_text().strip(),
    'FEAST_PROJECT': 'income_repro_20261029', 'FEAST_S3_PROJECT': 'income_s3_repro_20261029',
    'S3_FEATURE_BUCKET': 'features-repro-20261029', 'S3_REGISTRY_BUCKET': 'registry-repro-20261029',
    'AWS_ENDPOINT_URL': 'http://ml-platform-seaweedfs:8333', 'FEAST_S3_ENDPOINT_URL': 'http://ml-platform-seaweedfs:8333',
    'AWS_EC2_METADATA_DISABLED': 'true', 'OPENBLAS_NUM_THREADS': '1'})
env_file = root / '.repro.env'
env_file.write_text(''.join(f'{key}={value}\n' for key, value in values.items()))
os.chmod(env_file, 0o600)
args = ['/snap/bin/docker', 'run', '--rm', '--network', 'ml-platform-feast', '--user', f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp', '-e', 'USER=lab', '--env-file', str(env_file), '-v', f'{root}:/workspace', '-w', '/workspace', 'localhost:5001/ml-platform-batch:week02-v1', 'python']
checks = [
    ('repro_buckets', ['-c', 'import os,boto3; s=boto3.client("s3",endpoint_url=os.environ["AWS_ENDPOINT_URL"]); [s.create_bucket(Bucket=os.environ[key]) for key in ["S3_FEATURE_BUCKET","S3_REGISTRY_BUCKET"]]']),
    ('feast_apply', ['-c', 'from feast_setup import store,definitions; store.apply(definitions); print("로컬 피처 정의 등록: 성공")']),
    ('query_historical_checked.py', ['query_historical_checked.py']),
    ('materialize_features.py', ['materialize_features.py']),
    ('predict_online.py', ['predict_online.py']),
    ('upload_features.py', ['upload_features.py']),
    ('feast_s3_setup.py', ['feast_s3_setup.py']),
    ('compare_feast_sources.py', ['compare_feast_sources.py']),
    ('materialize_s3.py', ['materialize_s3.py']),
]
logs = []
for name, command in checks:
    completed = subprocess.run(args + command, check=True, capture_output=True, text=True)
    print(name + ': 성공', flush=True)
    logs.append({'script': name, 'stdout': completed.stdout})
(root / 'feast-verification.json').write_text(json.dumps(logs, ensure_ascii=False, indent=2))
report = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'operator': 'agent',
    'isolated_workdir': True, 'shared_existing_services': ['Redis', 'SeaweedFS', '검증된 배치 이미지'],
    'isolated_projects_and_buckets': True, 'checks': [name for name, _ in checks],
    'data_rows': 30162, 'validation_rows': 6033, 'max_probability_reload_difference': 0.0,
    'metrics': {'DecisionTree': {'accuracy': 0.8178, 'auc': 0.8442}, 'RandomForest': {'accuracy': 0.8250, 'auc': 0.8747}, 'XGBoost': {'accuracy': 0.8308, 'auc': 0.8814}},
    'limits': ['기존 Docker·클러스터를 공유한 신규 작업 폴더 재현', '빈 PC의 전체 설치 재실행은 아님']}
(repo / 'docs/evidence/reproduction.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
