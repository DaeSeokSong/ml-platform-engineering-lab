import json
import os
import shutil
import subprocess
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
lab = Path(os.environ.get('ML_PLATFORM_LAB_ROOT', str(Path.home() / 'ml-platform-lab')))
private = lab / 'infra/storage-lab'
output = repo / 'docs/evidence'
output.mkdir(parents=True, exist_ok=True)
docker = shutil.which('docker') or '/snap/bin/docker'
script = 'verify_batch_result.py' if '--batch-result' in __import__('sys').argv else 'compare_stores.py'
args = [docker, 'run', '--rm', '--network', 'ml-platform-feast', '--env-file', str(private / '.comparison.env'),
    '-v', f'{repo}:/repo:ro', '-v', f'{output}:/out', '-v', f'{private}/versity/files:/posix:ro']
if script == 'verify_batch_result.py':
    args += ['-v', f'{lab}/ch05-kfp/latest_batch_prefix.txt:/batch-prefix:ro']
args += ['localhost:5001/ml-platform-batch:week02-v1', 'python', f'/repo/extensions/object-storage/{script}']
subprocess.run(args, check=True)
