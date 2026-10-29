#!/usr/bin/env bash
set -euo pipefail
LAB_ROOT="${ML_PLATFORM_LAB_ROOT:-$HOME/ml-platform-lab}"
KFP_ROOT="$LAB_ROOT/infra/kfp"
mkdir -p "$KFP_ROOT"
if [ ! -d "$KFP_ROOT/upstream/.git" ]; then
  git clone --depth 1 --branch 2.16.1 --filter=blob:none --sparse https://github.com/kubeflow/pipelines.git "$KFP_ROOT/upstream"
fi
if [ "$(git -C "$KFP_ROOT/upstream" describe --tags --exact-match)" != '2.16.1' ]; then
  printf '기존 upstream 버전이 2.16.1이 아니므로 변경하지 않습니다.\n' >&2
  exit 1
fi
git -C "$KFP_ROOT/upstream" sparse-checkout set manifests/kustomize
kubectl --context kind-ml-platform get nodes
kubectl kustomize "$KFP_ROOT/upstream/manifests/kustomize/cluster-scoped-resources" > "$KFP_ROOT/cluster-scoped.yaml"
kubectl kustomize "$KFP_ROOT/upstream/manifests/kustomize/env/platform-agnostic" > "$KFP_ROOT/platform-agnostic.yaml"
kubectl --context kind-ml-platform create namespace kubeflow --dry-run=client -o yaml | kubectl --context kind-ml-platform apply --server-side -f -
kubectl --context kind-ml-platform apply --server-side -f "$KFP_ROOT/cluster-scoped.yaml"
kubectl --context kind-ml-platform wait --for=condition=Established crd/applications.app.k8s.io --timeout=120s
kubectl --context kind-ml-platform apply --server-side -f "$KFP_ROOT/platform-agnostic.yaml"
kubectl --context kind-ml-platform -n kubeflow wait --for=condition=Available deployment --all --timeout=900s
kubectl --context kind-ml-platform -n kubeflow get pods
