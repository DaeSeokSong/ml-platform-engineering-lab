import json
import os
import secrets
import shutil
import subprocess
import time
from pathlib import Path

DOCKER = shutil.which('docker') or '/snap/bin/docker'
LAB = Path(os.environ.get('ML_PLATFORM_LAB_ROOT', str(Path.home() / 'ml-platform-lab')))
WORK = LAB / 'infra/storage-lab'
WORK.mkdir(parents=True, exist_ok=True)
os.chmod(WORK, 0o700)

def run(*args, capture=False):
    return subprocess.run([DOCKER, *args], check=True, text=True, capture_output=capture)

def save_private(path, values):
    if not path.exists():
        path.write_text(''.join(f'{key}={value}\n' for key, value in values.items()))
        os.chmod(path, 0o600)
    return dict(line.split('=', 1) for line in path.read_text().splitlines() if '=' in line)

def start(name, image, args):
    existing = subprocess.run([DOCKER, 'inspect', name], capture_output=True, text=True)
    if existing.returncode == 0:
        info = json.loads(existing.stdout)[0]
        if info['Config']['Image'] != image:
            raise RuntimeError(f'기존 컨테이너의 이미지가 다릅니다: {name}')
        if not info['State']['Running']:
            run('start', name)
        print('기존 실습 컨테이너 유지:', name)
        return
    run('pull', image)
    run('run', '-d', '--name', name, '--restart', 'unless-stopped',
        '--network', 'ml-platform-feast', *args, image, *(
            ['server', '--single-node', '--default-bucket'] if name.endswith('garage') else []))

run('network', 'inspect', 'ml-platform-feast', capture=True)
garage = save_private(WORK / '.garage.env', {
    'GARAGE_RPC_SECRET': secrets.token_hex(32),
    'GARAGE_DEFAULT_ACCESS_KEY': 'GK' + secrets.token_hex(16),
    'GARAGE_DEFAULT_SECRET_KEY': secrets.token_hex(32),
    'GARAGE_DEFAULT_BUCKET': 'storage-lab',
})
config = WORK / 'garage.toml'
config.write_text('''metadata_dir = "/var/lib/garage/meta"
data_dir = "/var/lib/garage/data"
db_engine = "sqlite"
replication_factor = 1
rpc_bind_addr = "[::]:3901"
rpc_public_addr = "127.0.0.1:3901"
[s3_api]
s3_region = "garage"
api_bind_addr = "[::]:3900"
''')
start('ml-platform-garage', 'dxflrs/garage:v2.5.0', [
    '--memory', '512m', '-p', '127.0.0.1:3900:3900',
    '--env-file', str(WORK / '.garage.env'), '--entrypoint', '/garage',
    '-v', f'{config}:/etc/garage.toml:ro',
    '-v', 'ml-platform-garage-meta:/var/lib/garage/meta',
    '-v', 'ml-platform-garage-data:/var/lib/garage/data',
])
versity = save_private(WORK / '.versity.env', {
    'ROOT_ACCESS_KEY': 'lab' + secrets.token_hex(12),
    'ROOT_SECRET_KEY': secrets.token_hex(32),
    'VGW_BACKEND': 'posix', 'VGW_BACKEND_ARGS': '/data/s3',
    'VGW_PORT': ':7070', 'VGW_IAM_DIR': '/data/iam',
})
files = WORK / 'versity/files'
iam = WORK / 'versity/iam'
(files / 'existing-bucket').mkdir(parents=True, exist_ok=True)
iam.mkdir(parents=True, exist_ok=True)
(files / 'existing-bucket/from-filesystem.txt').write_text('파일 서버에서 먼저 만든 예시\n', encoding='utf-8')
start('ml-platform-versitygw', 'ghcr.io/versity/versitygw:v1.8.0', [
    '--memory', '256m', '--user', f'{os.getuid()}:{os.getgid()}',
    '-p', '127.0.0.1:7070:7070', '--env-file', str(WORK / '.versity.env'),
    '-v', f'{files}:/data/s3', '-v', f'{iam}:/data/iam',
])
seaweed = dict(line.split('=', 1) for line in (LAB / 'ch04-mlflow-feast/.s3.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
save_private(WORK / '.comparison.env', {
    'SEAWEED_ACCESS_KEY': seaweed['AWS_ACCESS_KEY_ID'],
    'SEAWEED_SECRET_KEY': seaweed['AWS_SECRET_ACCESS_KEY'],
    'GARAGE_ACCESS_KEY': garage['GARAGE_DEFAULT_ACCESS_KEY'],
    'GARAGE_SECRET_KEY': garage['GARAGE_DEFAULT_SECRET_KEY'],
    'VERSITY_ACCESS_KEY': versity['ROOT_ACCESS_KEY'],
    'VERSITY_SECRET_KEY': versity['ROOT_SECRET_KEY'],
    'AWS_EC2_METADATA_DISABLED': 'true',
})
print('저장소 실습 준비: Garage 2.5.0 / VersityGW 1.8.0')
print('인증정보는 WSL 작업 폴더에만 보관했습니다.')
