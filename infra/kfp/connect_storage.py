import json
import os
import shutil
import subprocess
from pathlib import Path

docker = shutil.which('docker') or '/snap/bin/docker'
kubectl = shutil.which('kubectl')
if not kubectl:
    raise SystemExit('kubectl을 PATH에 추가한 WSL Bash에서 실행하세요.')
lab = Path(os.environ.get('ML_PLATFORM_LAB_ROOT', str(Path.home() / 'ml-platform-lab')))
info = json.loads(subprocess.check_output([docker, 'inspect', 'ml-platform-seaweedfs']))[0]
if 'kind' not in info['NetworkSettings']['Networks']:
    subprocess.run([docker, 'network', 'connect', 'kind', 'ml-platform-seaweedfs'], check=True)
    info = json.loads(subprocess.check_output([docker, 'inspect', 'ml-platform-seaweedfs']))[0]
ip = info['NetworkSettings']['Networks']['kind']['IPAddress']
items = [
    {'apiVersion': 'v1', 'kind': 'Service', 'metadata': {'name': 'external-seaweedfs', 'namespace': 'kubeflow'},
     'spec': {'ports': [{'name': 's3', 'port': 8333, 'targetPort': 8333}]}},
    {'apiVersion': 'discovery.k8s.io/v1', 'kind': 'EndpointSlice',
     'metadata': {'name': 'external-seaweedfs-manual', 'namespace': 'kubeflow', 'labels': {'kubernetes.io/service-name': 'external-seaweedfs', 'endpointslice.kubernetes.io/managed-by': 'study-manual'}},
     'addressType': 'IPv4', 'ports': [{'name': 's3', 'protocol': 'TCP', 'port': 8333}],
     'endpoints': [{'addresses': [ip], 'conditions': {'ready': True}}]},
    {'apiVersion': 'v1', 'kind': 'Service', 'metadata': {'name': 'ml-platform-seaweedfs', 'namespace': 'kubeflow'},
     'spec': {'type': 'ExternalName', 'externalName': 'external-seaweedfs.kubeflow.svc.cluster.local'}},
]
base = [kubectl, '--context', 'kind-ml-platform']
subprocess.run(base + ['apply', '-f', '-'], input=json.dumps({'apiVersion': 'v1', 'kind': 'List', 'items': items}), text=True, check=True)
secret = subprocess.check_output(base + ['-n', 'kubeflow', 'create', 'secret', 'generic', 'feature-s3-credentials', '--from-env-file=' + str(lab / 'ch04-mlflow-feast/.s3.env'), '--dry-run=client', '-o', 'json'])
subprocess.run(base + ['apply', '--server-side', '-f', '-'], input=secret, check=True)
print('외부 S3 Service·EndpointSlice·Secret 구성 완료')
