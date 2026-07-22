#!/usr/bin/env bash
# Loki + Promtail'i kurar ve mevcut Grafana'ya datasource olarak baglar.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACE="monitoring"
RELEASE="loki"

echo ">> Helm repo ekleniyor..."
helm repo add grafana https://grafana.github.io/helm-charts >/dev/null
helm repo update >/dev/null

echo ">> ${RELEASE} (Loki + Promtail) kuruluyor..."
helm upgrade --install "${RELEASE}" grafana/loki-stack \
  --namespace "${NAMESPACE}" \
  --values "${SCRIPT_DIR}/values-loki-stack.yaml" \
  --wait --timeout 5m

echo ">> Loki datasource ConfigMap'i uygulaniyor..."
kubectl apply -f "${SCRIPT_DIR}/grafana-datasource-loki.yaml"

echo ""
echo ">> Pod'lar:"
kubectl get pods -n "${NAMESPACE}" -l app.kubernetes.io/instance="${RELEASE}"

echo ""
echo ">> Kurulum tamam."
echo "   Grafana'yi actiginda (http://localhost:3000) Explore sekmesinden"
echo "   'Loki' datasource'unu secip pod loglarini sorgulayabilirsin."
echo "   Ornek sorgu: {namespace=\"test-app\"}"
