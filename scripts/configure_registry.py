import argparse
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--node', default='ml-platform-control-plane')
args = parser.parse_args()
docker = shutil.which('docker') or '/snap/bin/docker'
subprocess.run([docker, 'inspect', args.node], check=True, stdout=subprocess.DEVNULL)
directory = '/etc/containerd/certs.d/localhost:5001'
subprocess.run([docker, 'exec', args.node, 'mkdir', '-p', directory], check=True)
content = '[host."http://ml-platform-registry:5000"]\n  capabilities = ["pull", "resolve"]\n'
subprocess.run([docker, 'exec', '-i', args.node, 'cp', '/dev/stdin', directory + '/hosts.toml'], input=content, text=True, check=True)
print('kind 노드의 로컬 레지스트리 pull 경로 구성 완료')
