"""
Gelen Alertmanager alarmini isleyip, sonraki adimlar (log cekme, LLM analizi)
icin gerekli baglami (context) hazirlar.
"""
from models.alert import AlertItem
from services.kubernetes_service import get_previous_revision
from utils.logger import logger


def build_alert_context(alert: AlertItem) -> dict:
    deployment = alert.deployment or alert.pod
    previous_rev = None
    if deployment:
        previous_rev = get_previous_revision(alert.namespace, deployment)

    context = {
        "alertname": alert.alertname,
        "namespace": alert.namespace,
        "pod": alert.pod,
        "deployment": deployment,
        "status": alert.status,
        "summary": alert.annotations.get("summary", ""),
        "description": alert.annotations.get("description", ""),
        "rollback_available": previous_rev is not None,
    }
    logger.info(f"Alarm alindi: {context['alertname']} | ns={context['namespace']} | pod={context['pod']} | rollback_var_mi={context['rollback_available']}")
    return context
