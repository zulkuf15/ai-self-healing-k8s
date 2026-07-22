#!/usr/bin/env bash
# Prometheus + Grafana + Alertmanager'i kube-prometheus-stack ile kurar.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACE="monitoring"
RELEASE="kube-prometheus-stack"

echo ">> Helm repo ekleniyor..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo update >/dev/null

echo ">> ${RELEASE} kuruluyor / guncelleniyor (namespace: ${NAMESPACE})..."
helm upgrade --install "${RELEASE}" prometheus-community/kube-prometheus-stack \
  --namespace "${NAMESPACE}" \
  --values "${SCRIPT_DIR}/values-kube-prometheus-stack.yaml" \
  --wait --timeout 5m

echo ""
echo ">> Pod'lar:"
kubectl get pods -n "${NAMESPACE}"

echo ""
echo ">> Kurulum tamam. Erisim:"
echo "   Grafana:    http://localhost:3000  (kullanici: admin / sifre: admin123)"
echo "   Prometheus: http://localhost:9090"
