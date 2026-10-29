# 환경 구성과 실행 경로

## 실행 공간

Git 저장소에는 코드·설정·README·하네스를 보관하고, WSL의 ~/ml-platform-lab에는 실제 데이터·가상환경·DB를 둡니다. 인증 파일은 WSL 작업 폴더에서만 생성합니다.

| 항목 | 확인한 환경 |
|---|---|
| 실행 | Windows·WSL Ubuntu·Docker |
| Python | python:3.11-bookworm, 3.11.17 |
| 클러스터 | kind ml-platform, Kubernetes v1.37.0 |
| MLflow·Feast·scikit-learn | 3.0.0·0.40.1·1.9.1 |
| KFP 서버·SDK | 2.16.1 |
| SeaweedFS·Redis | 4.51·7.4.12-bookworm |
| Garage·VersityGW | 2.5.0·1.8.0 |

## 1. 필수 도구와 클러스터

Docker·kind·kubectl·Helm·Git·Python 3이 필요합니다. 설치는 각 공식 배포 안내를 따릅니다. Docker Snap을 쓰면 /snap/bin이 PATH에 포함돼야 합니다.

```bash
docker --version
kind version
kubectl version --client
helm version --short
```

클러스터가 없는 새 실습 환경에서만 생성합니다. 기존 ml-platform 클러스터는 삭제·재생성하지 않습니다.

```bash
kind create cluster --name ml-platform --image kindest/node:v1.37.0
```

## 2. 저장소와 작업 코드

```bash
mkdir -p ~/src
cd ~/src
git clone https://github.com/DaeSeokSong/ml-platform-engineering-lab.git
cd ml-platform-engineering-lab
bash scripts/prepare-workdirs.sh
python3 scripts/bootstrap_infra.py
python3 scripts/configure_registry.py
```

복사 도구는 기존 파일을 덮어쓰지 않습니다. bootstrap은 기존 서비스를 유지하고 없을 때 로컬 registry·Redis·SeaweedFS를 만듭니다. 인증정보는 무작위 생성해 작업 폴더의 비공개 파일로 저장합니다. 전용 단일 노드 학습 환경용입니다.

## 3. 챕터 순서

1. [3장](../../chapters/ch03-hello-joker/README.md): API·컨테이너·Helm·CI·GitOps·모니터링.
2. [4장](../../chapters/ch04-mlflow-feast/README.md): 공개 데이터 생성·모델 학습·MLflow·Feast·Redis·S3.
3. [5장](../../chapters/ch05-kfp/README.md): KFP 설치·연결·배치 추론.
4. [저장소 확장](../../extensions/object-storage/README.md): Garage·VersityGW 비교.

3장의 Gitea 계정·runner 토큰·Argo CD 저장소 연결은 각자의 계정으로 준비해야 하며 자동 가입·인증을 제공하지 않습니다.

## 4. 재부팅 후

Pod와 컨테이너 준비 상태를 확인하고 port-forward를 다시 엽니다. 이 터미널을 켜 두고 별도 터미널에서 SDK 코드를 실행합니다.

```bash
kubectl --context kind-ml-platform -n kubeflow get pods
kubectl --context kind-ml-platform -n kubeflow port-forward --address 127.0.0.1 service/ml-pipeline-ui 8088:80
```

## 검증 범위

새 작업 폴더에서 공개 데이터 준비→모델 학습·저장·등록→Feast 과거·온라인 조회→S3 비교까지 재현했습니다. 이 검사는 기존 Docker 서비스와 검증된 실행 이미지를 공유했습니다. 빈 PC의 도구 설치·클러스터 생성부터 전 과정을 다시 검증한 것은 아닙니다. [증거](../evidence/reproduction.json)를 확인합니다.
