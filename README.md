# ML Platform Engineering Lab

『머신러닝 플랫폼 엔지니어링』을 바탕으로 환경 구축, 챕터별 실습, 에이전트 학습 하네스를 정리하는 저장소입니다.

## 시작하기

1. [공통 학습 하네스](docs/study-harness.md)와 [재현용 첫 입력 프롬프트](docs/study-start-prompt.md)를 읽습니다.
2. [환경 구성과 경로](docs/environment/README.md)에서 Windows 저장소와 WSL 실행 폴더의 역할을 확인합니다.
3. [챕터별 실습](chapters/README.md)에서 필요한 데이터·서비스를 확인한 뒤 진행합니다.
4. [검증 범위](docs/verification.md)에서 실제 확인한 결과와 추가 정리가 필요한 범위를 구분합니다.

## 구성

```text
chapters/       챕터별 작업 코드와 실행 README
infra/          Gitea·runner·모니터링 설정 및 KFP 연결 템플릿
scripts/        작업 폴더 준비 도구
artifacts/      인터랙티브 설명 아티팩트 안내
docs/          학습 하네스·환경·진행·출처·검증 기록
```

| 실습 | 현재 상태 |
|---|---|
| [3장 API·컨테이너·Helm·CI·모니터링](chapters/ch03-hello-joker/README.md) | 기존 WSL 실습에서 확인한 작업본 이관 |
| [4장 모델 비교·MLflow·Feast·Redis·S3](chapters/ch04-mlflow-feast/README.md) | 공개 데이터 생성·독립 모델/피처 재현 확인 |
| [5장 KFP 배치 추론](chapters/ch05-kfp/README.md) | 기존 환경의 통합 DAG SUCCEEDED 확인 |
| [Garage·VersityGW](extensions/object-storage/README.md) | 동일 파일 왕복·파일/S3 양방향 확인 |
| [인터랙티브 설명](artifacts/README.md) | 조작·모바일·어두운 테마 검사 완료 |

공개 데이터 준비부터 모델·Feast 흐름을 새 작업 폴더에서 재현했고 저장소 확장을 추가했습니다. 기존 Docker 서비스·이미지를 공유한 검사이며 빈 PC의 전체 설치 검증은 아닙니다. 데이터·모델·인증정보는 Git에 넣지 않고 준비 코드와 출처를 제공합니다.

[실제 확인한 환경과 결과](docs/verification.md) · [자료 출처](docs/sources.md) · [공개 전 점검](docs/publication-checklist.md)
