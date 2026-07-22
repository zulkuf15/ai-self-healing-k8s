#!/usr/bin/env bash
# Ozel "Sistem Sagligi" dashboard'unu Grafana'ya ekler (sidecar uzerinden).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ">> Dashboard ConfigMap'i uygulaniyor..."
kubectl apply -f "${SCRIPT_DIR}/dashboards/configmap.yaml"

echo ""
echo ">> Tamam. Grafana sidecar'i birkac saniye icinde dashboard'u algilayacak."
echo "   Grafana > Dashboards > 'Sistem Sagligi - AI Self-Healing K8s' altinda gorebilirsin."
echo "   Eger gorunmuyorsa: kubectl logs -n monitoring -l app.kubernetes.io/name=grafana -c grafana-sc-dashboard"
