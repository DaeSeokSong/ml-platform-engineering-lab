"""기존 kind를 전제로 로컬 레지스트리·Redis·SeaweedFS를 준비합니다."""
import json
import os
import secrets
import shutil
import subprocess
from pathlib import Path

docker = shutil.which('docker') or '/snap/bin/docker'
lab = Path(os.environ.get('ML_PLATFORM_LAB_ROOT', str(Path.home() / 'ml-platform-lab')))
work = lab / 'ch04-mlflow-feast'
work.mkdir(parents=True, exist_ok=True)

def run(*args, capture=False):
    return subprocess.run([docker, *args], check=True, text=True, capture_output=capture)

def private(path, value):
    if not path.exists():
        path.write_text(value, encoding='utf-8')
        os.chmod(path, 0o600)
    return path.read_text().strip()

def start(name, image, options, command):
    found = subprocess.run([docker, 'inspect', name], capture_output=True, text=True)
    if found.returncode == 0:
        info = json.loads(found.stdout)[0]
        if not info['State']['Running']:
            run('start', name)
        print('기존 컨테이너 유지:', name)
        return
    run('run', '-d', '--name', name, '--restart', 'unless-stopped', *options, image, *command)

run('network', 'inspect', 'kind', capture=True)
if subprocess.run([docker, 'network', 'inspect', 'ml-platform-feast'], capture_output=True).returncode:
    run('network', 'create', 'ml-platform-feast')
password = private(work / '.redis-password', secrets.token_hex(24))
private(work / '.redis.env', f'FEAST_REDIS_PASSWORD={password}\n')
private(work / '.s3.env', f'AWS_ACCESS_KEY_ID=lab{secrets.token_hex(12)}\nAWS_SECRET_ACCESS_KEY={secrets.token_hex(32)}\nAWS_DEFAULT_REGION=us-east-1\n')
start('ml-platform-registry', 'registry:3', ['--network', 'kind', '-p', '127.0.0.1:5001:5000', '-v', 'ml-platform-registry-data:/var/lib/registry', '-e', 'OTEL_TRACES_EXPORTER=none'], [])
start('ml-platform-feast-redis', 'redis:7.4.12-bookworm', ['--network', 'ml-platform-feast', '--memory', '256m', '--env-file', str(work / '.redis.env'), '-v', 'ml-platform-feast-redis-data:/data'], ['sh', '-ec', 'exec redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy noeviction --requirepass "$FEAST_REDIS_PASSWORD"'])
start('ml-platform-seaweedfs', 'chrislusf/seaweedfs:4.51', ['--network', 'ml-platform-feast', '--memory', '1g', '-p', '127.0.0.1:8333:8333', '--env-file', str(work / '.s3.env'), '-e', 'S3_BUCKET=feature-data-sets,feature-registry', '-v', 'ml-platform-seaweedfs-data:/data'], ['mini', '-dir=/data'])
print('기본 저장소 준비 완료. 인증 파일은 WSL 작업 폴더에만 있습니다.')
