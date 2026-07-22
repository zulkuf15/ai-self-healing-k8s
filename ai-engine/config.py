"""
Ortam degiskenlerinden konfigurasyon okur. Kubernetes Deployment'ta
bunlar env: alaninda tanimlanir (bkz. ai-engine-deployment.yaml).
"""
import os


class Config:
    # Ollama servisinin cluster-ici adresi (Service DNS)
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama.ai-engine.svc.cluster.local:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    # Loki'nin cluster-ici adresi
    LOKI_URL = os.getenv("LOKI_URL", "http://loki.monitoring.svc.cluster.local:3100")

    # AI'in aksiyon alabilecegi TEK namespace. Guvenlik siniri burada da
    # ikinci kez uygulanir (RBAC yetmezmis gibi savunma katmani -- defense in depth).
    TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE", "test-app")

    # LLM'in onerebilecegi, sistemin gercekten calistirmasina izin verilen
    # aksiyonlar. Whitelist disinda bir aksiyon gelirse calistirilmaz.
    ALLOWED_ACTIONS = {"restart_pod", "scale_deployment", "rollback_deployment", "no_action"}

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    PORT = int(os.getenv("PORT", "8000"))
