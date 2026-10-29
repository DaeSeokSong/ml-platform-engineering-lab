# 작업 도구

prepare-workdirs.sh는 챕터 코드를 WSL 실행 폴더에 복사합니다. 기존 파일을 덮어쓰거나 서비스를 설치하지 않습니다.

```bash
bash scripts/prepare-workdirs.sh
```

별도 작업 폴더를 선택하려면 ML_PLATFORM_LAB_ROOT 환경변수를 지정합니다. 셸 문법과 임시 폴더 복사 동작은 정리 과정에서 검사하며, 실제 운영 중인 WSL 작업 폴더에 자동 실행하지 않습니다.
