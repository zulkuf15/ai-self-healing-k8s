"""
decision_engine'den gelen dogrulanmis karari alip, ilgili kubernetes_service
fonksiyonunu cagirarak gercek aksiyonu uygular.
"""
from services import kubernetes_service as k8s
from utils.logger import logger


def apply_remediation(decision: dict) -> dict:
    action = decision["action"]
    namespace = decision["namespace"]
    target = decision.get("target")

    if action == "no_action":
        logger.info("Aksiyon: no_action -- hicbir sey yapilmiyor.")
        return {"applied": False, "action": "no_action"}

    if action == "restart_pod":
        result = k8s.restart_pod(namespace, target)
    elif action == "scale_deployment":
        result = k8s.scale_deployment(namespace, target)
    elif action == "rollback_deployment":
        result = k8s.rollback_deployment(namespace, target)
    else:
        logger.error(f"Bilinmeyen aksiyon (buraya hic gelmemeliydi): {action}")
        return {"applied": False, "action": action, "error": "unknown_action"}

    return {"applied": result["success"], "action": action, "target": target, "detail": result["detail"]}
