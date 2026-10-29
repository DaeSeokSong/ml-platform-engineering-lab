# Gitea runner

compose.yaml은 같은 폴더의 registration-token을 읽습니다. Gitea에서 본인 저장소의 등록 토큰을 발급받아 별도 파일에 저장하고 권한을 제한합니다. 토큰을 README나 Git에 적지 않습니다.

runner label lab은 ml-platform-ci:py311-docker29 이미지를 사용합니다. 3장의 .gitea/Dockerfile.ci로 해당 이미지를 먼저 만들어야 합니다. Docker 소켓은 사용자의 로컬 실습 Docker에 연결됩니다.
