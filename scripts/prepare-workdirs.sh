#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
LAB_ROOT="${ML_PLATFORM_LAB_ROOT:-$HOME/ml-platform-lab}"
for chapter in ch03-hello-joker ch04-mlflow-feast ch05-kfp; do
  mkdir -p "$LAB_ROOT/$chapter"
  cp -a --update=none "$REPO_ROOT/chapters/$chapter/." "$LAB_ROOT/$chapter/"
  printf '작업 코드 준비: %s
' "$LAB_ROOT/$chapter"
done
printf '데이터·인증정보·가상환경·서비스는 별도로 준비해야 합니다.
'
