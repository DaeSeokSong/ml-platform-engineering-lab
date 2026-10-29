# 5장: KFP 배치 추론

KFP는 작업을 DAG로 연결해 실행·기록하는 도구입니다. 여기서는 Feast 조회 → MLflow 추론 → S3 저장·재읽기 검증을 연결합니다.

## 선행 조건

4장의 MLflow 모델 등록·S3 피처와 레지스트리 준비를 완료해야 합니다. kind-ml-platform의 kubeflow 네임스페이스에 KFP 2.16.1이 설치되고 외부 SeaweedFS에 접근할 수 있어야 합니다. [인프라 안내](../../infra/README.md)를 확인합니다.

## SDK 환경

```bash
cd ~/ml-platform-lab/ch05-kfp
pwd
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/workspace" -w /workspace python:3.11-bookworm bash -ec 'python -m venv .venv; .venv/bin/python -m pip install -r requirements.txt; .venv/bin/python -m pip check'
```

SDK 가상환경과 ch04의 모델·피처 가상환경을 분리합니다. 실제 작업 이미지는 runtime/requirements.lock.txt를 사용합니다.

## 연결 확인과 준비 순서

1. 별도 터미널에서 ml-pipeline-ui 8088:80 port-forward를 유지합니다.
2. check_connection.py로 서버 목록을 조회하고 first_pipeline.py로 작은 DAG를 실행합니다.
3. [S3 연결 템플릿](../../infra/kfp/README.md)과 feature-s3-credentials Secret을 준비합니다.
4. ConfigMap s3-check-code에 check_s3_from_pod.py를 넣고 s3-auth-check.yaml을 실행합니다.
5. export_model_s3.py를 ch04 가상환경·/workspace 마운트로 실행해 등록 모델 파일과 manifest를 S3에 올립니다.
6. runtime Dockerfile로 localhost:5001/ml-platform-batch:week02-v1 이미지를 빌드·push합니다.
7. ConfigMap model-check-code와 feast-check-code를 각각 해당 확인용 Python 파일로 생성하고 확인 Pod를 실행합니다.

export_model_s3.py는 ch04의 mlflow.db와 registered_model_uri.txt를 읽습니다. ch05에서 ch04 폴더를 /workspace에, ch05 폴더를 /pipeline-work에 마운트하고 /pipeline-work/export_model_s3.py를 실행해야 합니다.

## 실제 통합 실행

```bash
docker run --rm --network host --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/workspace" -w /workspace python:3.11-bookworm .venv/bin/python batch_pipeline.py
```

batch_pipeline.py는 같은 폴더의 check_feast_from_pod.py와 check_model_from_pod.py를 읽습니다. ch04에서 실행하면 상대 경로 오류가 납니다. 실행마다 새로운 S3 경로와 Run을 만들므로 상태 확인을 위해 반복 제출하지 않습니다.

```bash
docker run --rm --network host --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/workspace" -w /workspace python:3.11-bookworm .venv/bin/python -c 'from pathlib import Path; import kfp; run_id=Path("latest_batch_run_id.txt").read_text().strip(); print(kfp.Client(host="http://127.0.0.1:8088").get_run(run_id).state)'
```

기존 환경에서 통합 Run의 SUCCEEDED를 확인했습니다. 현재 작업본은 사용자 3명 선택과 Feast 조회를 첫 단계에 묶은 3단계 변형이며, 노션의 별도 사용자 ID 파일 읽기 컴포넌트와 완전히 같은 구성은 아닙니다. 최종 경로는 s3://feature-data-sets/week02-batch/<실행별 값>/results/predictions.csv입니다.

전체 새 환경 재현·개별 README 명령의 재실행은 공개 전 추가 검증 대상입니다.
