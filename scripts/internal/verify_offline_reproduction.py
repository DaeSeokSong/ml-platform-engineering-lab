import json
import os
import shutil
import subprocess
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
root = Path.home() / 'ml-platform-lab-repro-20261029'
if root.exists():
    raise SystemExit('독립 검증 폴더가 이미 있습니다. 기존 결과를 덮어쓰지 않습니다.')
root.mkdir()
for path in (repo / 'chapters/ch04-mlflow-feast').glob('*.py'):
    shutil.copy2(path, root / path.name)
for name in ['requirements.txt', 'constraints.local.txt']:
    shutil.copy2(repo / 'chapters/ch04-mlflow-feast' / name, root / name)
args = ['/snap/bin/docker', 'run', '--rm', '--user', f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp', '-e', 'USER=lab', '-e', 'OPENBLAS_NUM_THREADS=1', '-e', 'MLFLOW_ENABLE_ARTIFACTS_PROGRESS_BAR=false', '-v', f'{root}:/workspace', '-w', '/workspace', 'localhost:5001/ml-platform-batch:week02-v1']
logs = []
for script in ['prepare_data.py', 'train_baseline.py', 'track_tree.py', 'save_reload_model.py', 'register_model.py']:
    result = subprocess.run(args + ['python', script], check=True, capture_output=True, text=True)
    print(f'{script}: 성공')
    logs.append({'script': script, 'stdout': result.stdout})
(root / 'verification.json').write_text(json.dumps(logs, ensure_ascii=False, indent=2))
print('기존 작업 폴더를 변경하지 않은 독립 데이터·학습·모델 등록 검증 완료')
