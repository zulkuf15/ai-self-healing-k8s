#!/usr/bin/env bash
# ai-engine Docker image'ini yerel olarak build eder ve Kind cluster'ina yukler.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="self-healing-k8s"
IMAGE="ai-engine:local"

echo ">> Image build ediliyor: ${IMAGE}"
docker build -t "${IMAGE}" "${ROOT_DIR}/ai-engine"

echo ">> Image Kind cluster'ina yukleniyor..."
kind load docker-image "${IMAGE}" --name "${CLUSTER_NAME}"

echo ">> Tamam. 'kubectl apply -f kubernetes/self-healing/' ile deploy edebilirsin."
