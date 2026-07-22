from flask import Blueprint, request, jsonify
from models.alert import AlertmanagerWebhook
from services.alert_service import build_alert_context
from services.loki_service import fetch_recent_logs
from analyzers.decision_engine import analyze_and_decide
from services.remediation_service import apply_remediation
from config import Config
from utils.logger import logger
from utils.dedup import should_process
from utils.target_lock import get_lock

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook/alert", methods=["POST"])
def handle_alert():
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "gecersiz JSON"}), 400

    try:
        webhook = AlertmanagerWebhook(**payload)
    except Exception as e:
        logger.error(f"Payload parse edilemedi: {e}")
        return jsonify({"error": "payload semaya uymuyor"}), 400

    results = []
    for alert in webhook.alerts:
        if alert.status != "firing":
            continue  # sadece aktif alarmlarla ilgileniyoruz, 'resolved' olanlari atla
        if alert.alertname in ("InfoInhibitor", "Watchdog", "DeadMansSwitch"):
            continue  # Alertmanager/Prometheus'un kendi ic meta-alarmlari, gercek bir pod sorunu degil
        if not alert.pod:
            continue  # hedef bir pod belirtmeyen alarmlarla ilgilenmiyoruz
        if alert.namespace != Config.TARGET_NAMESPACE:
            logger.info(f"Alarm {alert.namespace} namespace'inde, hedef disinda -- atlaniyor.")
            continue

        # Dedup/kilit ANAHTARI kasitli olarak alertname'i icermez: farkli
        # alarm kurallari (bizim ozel kuralimiz + Kubernetes'in varsayilani)
        # AYNI pod/deployment icin ayri ayri tetiklenebiliyor. Hedefi esas
        # aliyoruz ki cakisan/es zamanli islemler engellensin.
        target_key = f"{alert.namespace}/{alert.deployment or alert.pod}"

        with get_lock(target_key):
            if not should_process(target_key):
                logger.info(f"Hedef son 3 dakikada zaten islendi, atlaniyor: {target_key}")
                continue

            context = build_alert_context(alert)
            logs = fetch_recent_logs(context["namespace"], context.get("pod"))
            root_cause, decision = analyze_and_decide(context, logs)
            outcome = apply_remediation(decision)

        results.append({
            "alert": context["alertname"],
            "root_cause": root_cause,
            "decision": decision,
            "outcome": outcome,
        })

    return jsonify({"processed": len(results), "results": results}), 200
