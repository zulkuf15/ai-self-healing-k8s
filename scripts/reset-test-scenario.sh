#!/usr/bin/env bash
# test-app namespace'indeki tum test kaynaklarini temizler.
set -euo pipefail

echo ">> test-app namespace'i temizleniyor..."
kubectl delete deployment --all -n test-app --ignore-not-found
kubectl delete pod --all -n test-app --ignore-not-found --force --grace-period=0
kubectl delete pvc --all -n test-app --ignore-not-found

echo ">> Tamam. Namespace bos duruma getirildi."
