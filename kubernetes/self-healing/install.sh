#!/usr/bin/env bash
# 2. Asama: Ollama + AI Engine'i cluster'a kurar (bu sirayla).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ">> ServiceAccount ve RBAC uygulaniyor..."
kubectl apply -f "${SCRIPT_DIR}/serviceaccount.yaml"
kubectl apply -f "${SCRIPT_DIR}/rbac.yaml"

echo ">> Ollama deploy ediliyor..."
kubectl apply -f "${SCRIPT_DIR}/ollama-deployment.yaml"

echo ">> Ollama pod'unun hazir olmasi bekleniyor (model indirmeden once)..."
kubectl rollout status deployment/ollama -n ai-engine --timeout=180s

echo ">> AI Engine deploy ediliyor..."
kubectl apply -f "${SCRIPT_DIR}/ai-engine-deployment.yaml"

echo ""
echo ">> Sira geldi model indirmeye. Su komutu calistir (birkac dakika surebilir):"
echo "   bash scripts/pull-ollama-model.sh"
