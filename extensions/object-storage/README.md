# 객체 저장소 확장: SeaweedFS·Garage·VersityGW

Garage는 자체 운영용 객체 저장소이고, VersityGW는 기존 파일 디렉터리 앞에 S3 API를 붙이는 게이트웨이입니다. 기존 SeaweedFS와 같은 클라이언트·파일을 사용해 역할 차이를 확인합니다.

## 실행 위치와 선행 조건

WSL Bash에서 clone한 저장소 루트로 이동해 실행합니다. 4·5장의 SeaweedFS 피처·모델 저장과 배치 런타임 이미지가 준비돼 있어야 합니다. 실제 실행 폴더는 ~/ml-platform-lab/infra/storage-lab이며 서비스 계정과 테스트 파일은 Git 밖에 보관합니다.

```bash
python3 extensions/object-storage/start_services.py
python3 extensions/object-storage/run_checks.py
python3 extensions/object-storage/run_checks.py --batch-result
```

첫 명령은 Garage 2.5.0과 VersityGW 1.8.0을 생성·기동합니다. 같은 이름의 기존 컨테이너는 이미지가 같은지 확인하고 유지합니다. 개인 파일 서버 대신 전용 테스트 디렉터리를 사용합니다. 두 번째 명령은 세 저장소의 PUT·GET·HEAD·LIST와 파일 내용을 비교하고, 마지막은 기존 KFP의 실제 결과 CSV를 읽어 개인 ID를 제외한 증거를 남깁니다.

## 실제 확인한 결과

| 항목 | 결과 |
|---|---|
| JSON 76바이트·Parquet 1,440,643바이트·모델 8,291바이트 | 세 저장소 모두 내용·크기·목록 일치 |
| 기존 POSIX 파일을 S3로 조회 | 성공 |
| S3 업로드를 실제 POSIX 파일로 읽기 | 성공 |
| KFP 최종 예측 CSV | 3행·클래스·확률 범위 확인 |

결과는 [비교 증거](../../docs/evidence/comparison.json), [실제 배치 결과](../../docs/evidence/batch-result.json)에 있습니다. 에이전트가 직접 실행한 검사이며 단일 노드의 기능 확인입니다. 속도 순위·고가용성·S3 전체 API 호환성을 검증한 것은 아닙니다.

## 선택 기준

| 도구 | 이번 실습에서 드러난 역할 | 검토할 점 |
|---|---|---|
| SeaweedFS | 피처·모델·레지스트리를 S3로 보관 | 파일·객체 구성과 운영 범위 |
| Garage | 독립 객체 저장소에 같은 S3 객체를 보관 | 운영 시 복제·노드 배치와 API 지원 범위 |
| VersityGW | 기존 파일을 이동하지 않고 S3 API로 접근 | 실제 파일시스템의 권한·메타데이터·동시 접근 조건 |

[Garage 공식 시작 안내](https://garagehq.deuxfleurs.fr/documentation/quick-start/) · [VersityGW Docker 안내](https://github.com/versity/versitygw/wiki/Docker)
