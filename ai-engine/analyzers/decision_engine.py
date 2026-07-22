"""
Alarm + log verisini TEK bir LLM cagrisinda hem kok neden analizine hem de
yapilandirilmis (JSON) bir remediation kararina donusturur. Iki ayri cagri
yerine tek cagri kullanmak, CPU uzerinde calisan yerel modellerde toplam
gecikmeyi onemli olcude azaltir.

Gecersiz/parse edilemeyen/whitelist disi HER cevap guvenli varsayilana
(no_action) duser -- bu, sistemin "emin degilsem hicbir sey yapma" ilkesi.
"""
from pathlib import Path
from config import Config
from services.ollama_service import ask_ollama
from utils.helpers import extract_json
from utils.logger import logger

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "combined_analysis.txt"

SAFE_DEFAULT_DECISION = {
    "action": "no_action",
    "target": None,
    "namespace": Config.TARGET_NAMESPACE,
    "confidence": 0.0,
    "reasoning": "Karar dogrulanamadi (LLM cevap vermedi veya gecersizdi), guvenli varsayilan uygulandi.",
}
SAFE_DEFAULT_ROOT_CAUSE = "Kok neden analizi alinamadi (LLM zaman asimina ugradi ya da gecersiz cevap dondu)."


def analyze_and_decide(alert_context: dict, logs: str) -> tuple[str, dict]:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(
        alertname=alert_context["alertname"],
        namespace=alert_context["namespace"],
        pod=alert_context.get("pod") or "bilinmiyor",
        deployment=alert_context.get("deployment") or alert_context.get("pod") or "bilinmiyor",
        summary=alert_context.get("summary", ""),
        description=alert_context.get("description", ""),
        logs=logs or "(log bulunamadi)",
        rollback_available=alert_context.get("rollback_available", False),
    )

    raw = ask_ollama(prompt)
    parsed = extract_json(raw)

    if parsed is None:
        logger.warning("LLM cevabi JSON olarak parse edilemedi, guvenli varsayilana duşuluyor.")
        return SAFE_DEFAULT_ROOT_CAUSE, SAFE_DEFAULT_DECISION

    root_cause = parsed.get("root_cause", SAFE_DEFAULT_ROOT_CAUSE)
    target = parsed.get("target")
    if isinstance(target, dict):
        # LLM bazen talimata ragmen {"kind":..,"name":..} gibi bir nesne
        # donebiliyor -- name alanini cikararak duz string'e ceviriyoruz.
        target = target.get("name")
    decision = {
        "action": parsed.get("action"),
        "target": target,
        "namespace": parsed.get("namespace", Config.TARGET_NAMESPACE),
        "confidence": parsed.get("confidence", 0.0),
        "reasoning": parsed.get("reasoning", ""),
    }

    if not _is_valid(decision):
        logger.warning(f"LLM karari semaya/whitelist'e uymuyor: {decision} -> no_action")
        return root_cause, SAFE_DEFAULT_DECISION

    if decision["action"] == "rollback_deployment" and not alert_context.get("rollback_available", False):
        logger.warning("LLM rollback onerdi ama geri donulecek revizyon yok -> no_action")
        return root_cause, SAFE_DEFAULT_DECISION

    logger.info(f"Karar: {decision['action']} | hedef={decision.get('target')} | guven={decision.get('confidence')}")
    return root_cause, decision


def _is_valid(decision: dict) -> bool:
    if decision.get("action") not in Config.ALLOWED_ACTIONS:
        return False
    if decision.get("action") != "no_action" and not decision.get("target"):
        return False
    # AI, TARGET_NAMESPACE disinda bir namespace'e aksiyon oneremez (defense in depth)
    if decision.get("namespace", Config.TARGET_NAMESPACE) != Config.TARGET_NAMESPACE:
        return False
    return True
