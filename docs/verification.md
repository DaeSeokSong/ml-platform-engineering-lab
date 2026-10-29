# 검증 범위

## 사용자가 기존 WSL에서 확인한 결과

- Python 3.11.17, MLflow 3.0.0, Feast 0.40.1, scikit-learn 1.9.1.
- 모델 저장 전후 검증 6,033행 예측 동일, 최대 확률 차이 0.0.
- 로컬/S3 Feast 과거 조회와 Redis 온라인 값 비교.
- Pod의 S3 인증·모델 파일 8개 해시 검사·Pipeline 로드·Feast 조회.
- KFP 통합 배치 DAG 실행 상태 SUCCEEDED.

## 에이전트가 추가 실행한 결과

- 새 작업 폴더의 UCI 데이터 준비·세 모델 학습·MLflow 기록·저장·등록 재현.
- 별도 프로젝트·버킷에서 과거 조회·Redis 적재·온라인 추론·S3 업로드·조회·materialization 비교.
- [재현 증거](evidence/reproduction.json): 트리 검증 0.8178/0.8442, RF 0.8250/0.8747, XGBoost 0.8308/0.8814.
- [저장소 비교](evidence/comparison.json): 3개 저장소 × 3개 파일, PUT·GET·HEAD·LIST와 내용 일치.
- VersityGW의 파일→S3, S3→실제 파일 확인.
- [실제 배치 결과](evidence/batch-result.json): S3 결과 CSV 3행 확인, 개인 ID 제외.
- [인터랙티브 설명](../artifacts/README.md): 주요 조작·390px 모바일·어두운 테마·페이지 오류 검사.

## 한계

독립 재현은 기존 Docker 서비스·실행 이미지를 공유했습니다. 빈 PC의 설치부터 전체 환경을 새로 올린 검사는 아닙니다. 저장소의 성능 순위·고가용성·S3 전체 API와 전 사용자 값 대조도 검사하지 않았습니다. 설명 화면의 가상 이력은 실제 데이터의 관측 기록이 아닙니다.
