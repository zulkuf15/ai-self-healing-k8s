#!/usr/bin/env bash
# Kind cluster'i olusturur, context'i ayarlar ve node'lari dogrular.
set -euo pipefail

CLUSTER_NAME="self-healing-k8s"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ">> Kind cluster olusturuluyor: ${CLUSTER_NAME}"

if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
  echo "!! '${CLUSTER_NAME}' isimli cluster zaten var. Once 'kind delete cluster --name ${CLUSTER_NAME}' calistir."
  exit 1
fi

kind create cluster --config "${SCRIPT_DIR}/cluster.yaml"

echo ">> kubectl context kontrol ediliyor..."
kubectl cluster-info --context "kind-${CLUSTER_NAME}"

echo ""
echo ">> Node'lar:"
kubectl get nodes -o wide

echo ""
echo ">> Cluster hazir. Sirada: kubernetes/namespace.yaml uygulanmasi."
echo "   kubectl apply -f ../kubernetes/namespace.yaml"
