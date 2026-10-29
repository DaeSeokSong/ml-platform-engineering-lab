# KFP 설치와 외부 S3 연결

KFP는 2.16.1 태그의 cluster-scoped-resources와 env/platform-agnostic을 사용합니다. 전체 KCD 대신 KFP 단독 설치입니다. 기존 kind 컨텍스트와 메모리를 먼저 확인하고 실행합니다.

```bash
bash infra/kfp/install.sh
python3 infra/kfp/connect_storage.py
```

설치 스크립트는 공식 upstream을 고정 버전으로 내려받아 kustomize하고 적용합니다. connect_storage.py는 외부 SeaweedFS의 현재 kind IP로 Service·EndpointSlice를 구성하고 기존 이름을 위한 ExternalName 별칭과 본인의 S3 Secret을 만듭니다. 인증값을 출력하지 않습니다.

EndpointSlice는 Service가 보낼 실제 서버의 IP·포트 목록입니다. 컨테이너 재생성으로 IP가 바뀌면 연결 스크립트를 다시 실행합니다. KFP 내부 산출물 저장소와 외부 피처용 SeaweedFS는 별개입니다.

첫 이미지 준비에 10분 이상 걸렸던 실제 사례가 있어 준비 대기는 900초로 뒀습니다. 시간이 초과되면 Pod 이벤트와 이전 로그를 먼저 보고 PVC 삭제·MySQL 인증 변경을 임의로 하지 않습니다. 새 PC 설치 스크립트 전체 재실행은 추가 검증 범위이며 기존 환경의 KFP 실행 성공과 구분합니다.

수동 구성 참고는 external-seaweedfs.yaml.example을 사용합니다. ${SEAWEED_KIND_IP}를 그대로 apply하지 않습니다.
