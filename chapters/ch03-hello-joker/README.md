# 3장: API에서 CI·GitOps·모니터링까지

FastAPI로 농담 API를 만들고 Docker·Helm·Gitea Actions·Argo CD·Prometheus·Grafana로 연결한 작업본입니다. 원본 예제 압축 파일은 포함하지 않습니다.

## 입력과 실행 위치

WSL Bash의 ~/ml-platform-lab/ch03-hello-joker에서 실행합니다. [작업 폴더 준비](../../docs/environment/README.md)를 먼저 완료합니다.

## API 테스트와 이미지

```bash
cd ~/ml-platform-lab/ch03-hello-joker
pwd
docker run --rm -v "$PWD:/workspace" -w /workspace python:3.11-bookworm bash -ec 'python -m pip install -r requirements.txt -c constraints.local.txt; python -m pytest -q'
docker build -f Dockerfile.practice -t hello-joker:ch03-v2 .
```

## 이어지는 실습

1. charts/hello-joker를 Helm으로 배포하고 rollout을 확인합니다.
2. [로컬 레지스트리](../../infra/README.md)를 준비해 localhost:5001 이미지를 노드에서 읽게 합니다.
3. .gitea의 Dockerfile.ci로 CI 이미지를 만들고 Gitea 저장소에 이 챕터 내용을 별도 루트로 올려 runner label lab으로 실행합니다.
4. Argo CD에 개인 Gitea 저장소를 연결하고 values-gitops.yaml로 ml-platform-gitops에 배포합니다.
5. [모니터링 설정](../../infra/monitoring/README.md)으로 /metrics를 수집합니다.

charts의 기존 Secret 참조에 맞는 hello-joker-secret은 각 네임스페이스에 직접 준비해야 합니다. 값은 이 저장소에 넣지 않습니다. Gitea CI는 GitHub Actions용이 아니며 이 저장소의 하위 폴더 상태로 자동 실행되지 않습니다.

기존 환경에서 API·테스트·CI 이미지 업로드·GitOps 배포·Prometheus 타깃과 Grafana 지표를 확인했습니다. 새 환경 전체 재현 안내는 보완 중입니다.
