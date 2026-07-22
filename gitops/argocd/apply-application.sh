#!/usr/bin/env bash
# gitops/argocd/application.yaml'i cluster'a uygular.
# ONCE application.yaml icindeki repoURL'i kendi GitHub repo'nla
# degistirdiginden emin ol.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if grep -q "KULLANICI_ADIN" "${SCRIPT_DIR}/application.yaml"; then
  echo "!! HATA: application.yaml icindeki repoURL hala placeholder."
  echo "   Once su satiri kendi GitHub repo url'inle degistir:"
  grep "repoURL" "${SCRIPT_DIR}/application.yaml"
  exit 1
fi

kubectl apply -f "${SCRIPT_DIR}/application.yaml"
echo ">> Application uygulandi. Durumu kontrol icin:"
echo "   kubectl get application -n argocd"
