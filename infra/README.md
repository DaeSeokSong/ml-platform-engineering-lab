# 인프라 설정

현재 WSL에서 사용한 비밀정보 없는 설정을 보존합니다. 전체 신규 설치 자동화는 아직 포함하지 않습니다.

| 폴더 | 역할 |
|---|---|
| gitea | Gitea 28.2.0 Compose 설정 |
| runner | Gitea runner 설정, 등록 토큰은 별도 파일 |
| monitoring | Prometheus·Grafana Helm values |
| kfp | KFP 고정 버전 설치 위치와 외부 S3 연결 템플릿 |

## 로컬 레지스트리

기존 kind Docker 네트워크가 준비된 환경에서 사용했던 실행 형식입니다. 같은 이름의 컨테이너가 있으면 새로 만들지 않습니다.

```bash
docker run -d --name ml-platform-registry --restart unless-stopped --network kind -p 127.0.0.1:5001:5000 -v ml-platform-registry-data:/var/lib/registry -e OTEL_TRACES_EXPORTER=none registry:3
```

kind 노드의 /etc/containerd/certs.d/localhost:5001/hosts.toml에는 http://ml-platform-registry:5000을 pull·resolve 대상으로 지정합니다. 이 설정 없이 노드 안의 localhost:5001이 호스트 레지스트리로 자동 연결되지는 않습니다.

## 외부 S3·Redis

SeaweedFS 4.51의 weed mini를 ml-platform-feast 네트워크에서 사용했고 feature-data-sets·feature-registry 두 버킷을 만들었습니다. Redis는 같은 네트워크의 ml-platform-feast-redis이며 인증값은 .redis-password에서 주입했습니다. 해당 설치의 공개 템플릿·버킷 초기화 명령은 추가 정리 예정입니다.

실제 .s3.env·.redis-password·registration-token 파일은 복사하지 않습니다. Gitea·runner Compose는 kind 네트워크가 먼저 있어야 실행됩니다.
