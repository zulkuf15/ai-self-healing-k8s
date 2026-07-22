#!/usr/bin/env bash
# ArgoCD'yi cluster'a kurar (resmi kurulum manifestleriyle).
set -euo pipefail

echo ">> argocd namespace'i olusturuluyor..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

echo ">> ArgoCD kuruluyor (resmi manifestler)..."
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo ">> Pod'larin hazir olmasi bekleniyor (birkac dakika surebilir)..."
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd
kubectl wait --for=condition=available --timeout=300s deployment/argocd-repo-server -n argocd

echo ""
echo ">> ArgoCD kuruldu. Admin sifresini almak icin:"
echo "   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
echo ""
echo ">> ArgoCD UI'a erismek icin (ayri bir terminalde):"
echo "   kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "   Sonra tarayicidan: https://localhost:8080 (kullanici: admin)"
