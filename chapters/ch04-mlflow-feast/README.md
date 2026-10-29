# 4장: MLflow·Feast·Redis·S3

MLflow는 실험·모델 버전을 기록하고, Feast는 같은 정의와 시점 기준으로 피처를 조회합니다. Redis는 온라인 조회용 피처를 보관하며 SeaweedFS는 S3 API로 파일을 제공합니다.

## 선행 조건

- WSL Bash 작업 위치: ~/ml-platform-lab/ch04-mlflow-feast
- [공개 데이터 준비](data/README.md): prepare_data.py로 CSV·피처 파일 생성
- ml-platform-feast Docker 네트워크, Redis, 외부 SeaweedFS
- .redis-password와 .s3.env를 본인 값으로 준비하며 Git에 추가하지 않습니다.

## Python 환경

```bash
cd ~/ml-platform-lab/ch04-mlflow-feast
pwd
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/workspace" -w /workspace python:3.11-bookworm bash -ec 'python -m venv .venv; .venv/bin/python -m pip install -r requirements.lock.txt; .venv/bin/python -m pip check'
```

requirements.txt는 장의 직접 의존성을, requirements.lock.txt는 성공한 배치 이미지에서 보존한 전체 설치 버전을 담습니다. SQLAlchemy는 MLflow 3.0.0 호환성을 위해 2.0 계열을 사용합니다. 작업 중 ch04 requirements가 KFP 목록으로 덮어써진 것을 발견해 공개본에는 장의 원래 직접 의존성을 복구했습니다. KFP SDK는 ch05에서 별도로 설치합니다.

## 공개 데이터 생성

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/workspace" -w /workspace python:3.11-bookworm .venv/bin/python prepare_data.py
```

기존 데이터가 있으면 덮어쓰지 않습니다. 공개 UCI 원본과 합성 ID·시각을 사용하며, 입력의 선행 공백을 보존합니다.

## 실행 순서

| 순서 | 코드 | 확인할 것 |
|---|---|---|
| 1 | train_baseline.py, eda_income.py | 모델 비교·데이터 분포 |
| 2 | track_tree.py | MLflow 실험·파라미터·지표 |
| 3 | save_reload_model.py | 저장 전후 예측·확률 일치 |
| 4 | register_model.py | income-classifier-tree 버전 등록 |
| 5 | inspect_feast.py, feast_setup.py | Redis 연결·엔티티·뷰 등록 |
| 6 | query_historical_checked.py | 요청 시점 이전의 값만 사용 |
| 7 | materialize_features.py, predict_online.py | Redis 적재·온라인 피처 추론 |
| 8 | test_s3.py, upload_features.py, feast_s3_setup.py | S3 파일·레지스트리 등록 |
| 9 | compare_feast_sources.py, materialize_s3.py | 로컬/S3 과거·온라인 조회 비교 |

## 실행 명령 형식

```bash
docker run --rm --network ml-platform-feast --user "$(id -u):$(id -g)" -e USER="$(id -un)" -e HOME=/tmp --env-file .s3.env -e AWS_ENDPOINT_URL=http://ml-platform-seaweedfs:8333 -e FEAST_S3_ENDPOINT_URL=http://ml-platform-seaweedfs:8333 -e AWS_EC2_METADATA_DISABLED=true -e FEAST_REDIS_PASSWORD="$(cat .redis-password)" -v "$PWD:/workspace" -w /workspace python:3.11-bookworm .venv/bin/python compare_feast_sources.py
```

위 명령은 S3·Redis가 필요한 단계의 실행 형식입니다.

실행 대상 파일은 표의 순서에 맞춰 바꿉니다. 로컬 학습 단계에는 S3·Redis 환경변수가 필요하지 않습니다. feast_setup.py의 등록은 main 실행 진입점 여부를 확인하며, 현재 파일에 없다면 Python에서 store.apply(definitions)를 명시적으로 실행합니다.

## 확인한 결과

검증 Accuracy/ROC AUC는 트리 0.8178/0.8442, 랜덤 포레스트 0.8250/0.8747, XGBoost 0.8308/0.8814였습니다. 트리 모델 저장 전후 6,033행의 예측이 같았고, 표본 3명에 대한 로컬/S3 조회 일치를 확인했습니다. 이 결과를 다른 데이터의 일반적인 성능 우열로 확대하지 않습니다.


## 독립 재현의 설정 분리

FEAST_PROJECT, FEAST_S3_PROJECT, S3_FEATURE_BUCKET, S3_REGISTRY_BUCKET 환경변수로 기존 온라인 피처와 S3 버킷을 덮어쓰지 않고 검증할 수 있습니다. 설정하지 않으면 원래 실습 이름을 사용합니다. 신규 작업 폴더에서 모델 비교·저장·등록·Feast 과거 조회·Redis 적재·S3 비교를 실제 실행했습니다. [검증 결과](../../docs/evidence/reproduction.json)를 확인합니다.
