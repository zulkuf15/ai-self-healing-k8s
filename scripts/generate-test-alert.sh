#!/usr/bin/env bash
# "Kotu deploy" senaryosu:
#  1) Once saglikli versiyonu (v1) deploy eder, calisir hale gelmesini bekler.
#  2) Sonra kasten bozuk bir versiyonu (v2) deploy eder -- bu, kubelet'in
#     kendi ic retry'inin COZEMEYECEGI kalici bir hata (config bozuk).
#  3) Prometheus ~30-60 saniye icinde CrashLoopBackOff'u tespit edip
#     Alertmanager uzerinden AI Engine'e haber verir. Dogru cozum: rollback.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCENARIO_DIR="${ROOT_DIR}/test-scenarios/crashloop"

echo ">> 1/2: Saglikli versiyon (v1) deploy ediliyor..."
kubectl apply -f "${SCENARIO_DIR}/deployment-v1-healthy.yaml"
kubectl rollout status deployment/crashloop-demo -n test-app --timeout=60s

echo ""
echo ">> 2/2: 5 saniye sonra 'kotu deploy' (v2) uygulanacak..."
sleep 5
kubectl apply -f "${SCENARIO_DIR}/deployment-v2-bad.yaml"

echo ""
echo ">> Tamam. Simdi izle:"
echo "   kubectl get pods -n test-app -w"
echo "   kubectl logs -n ai-engine -l app=ai-engine -f"
echo "   http://localhost:9090/alerts"
