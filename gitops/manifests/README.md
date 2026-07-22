# GitOps Kaynak Klasoru

Bu klasor, ArgoCD'nin izledigi ve cluster'a otomatik senkronize ettigi
SAF Kubernetes manifestlerini icerir (Helm values dosyalari DAHIL DEGIL --
ArgoCD bunlari gecerli bir K8s kaynagi olarak parse edemeyip hata verir).

Buradaki dosyalar, projenin diger yerlerindeki (kubernetes/, monitoring/)
orijinal dosyalarin bir KOPYASIDIR. Ileride bir degisiklik yaparsan, bu
klasordeki kopyayi da guncelleyip push etmeyi unutma -- ArgoCD SADECE
buradaki hali dikkate alir.

(Daha ileri bir versiyonda, bu duplikasyonu kaldirmak icin Kustomize ile
tum manifestleri tek bir yerden referanslamak iyi bir sonraki adim olur.)
