#!/usr/bin/env bash
# Ollama pod'unun icine girip modeli indirir (image icine gomulu degil,
# ilk calistirmada indirilir -- boylece image kucuk kalir).
set -euo pipefail

MODEL="${1:-llama3.2:3b}"
POD=$(kubectl get pod -n ai-engine -l app=ollama -o jsonpath='{.items[0].metadata.name}')

echo ">> Model indiriliyor: ${MODEL} (pod: ${POD})"
kubectl exec -n ai-engine "${POD}" -- ollama pull "${MODEL}"

echo ">> Tamam. Test icin:"
echo "   kubectl exec -n ai-engine ${POD} -- ollama list"
