"""
Alarm + log verisini alip LLM'den kok neden analizi (insan-okunur metin) ister.
"""
from pathlib import Path
from services.ollama_service import ask_ollama
from utils.logger import logger

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "root_cause.txt"


def analyze_root_cause(alert_context: dict, logs: str) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(
        alertname=alert_context["alertname"],
        namespace=alert_context["namespace"],
        pod=alert_context.get("pod") or "bilinmiyor",
        summary=alert_context.get("summary", ""),
        description=alert_context.get("description", ""),
        logs=logs or "(log bulunamadi)",
    )
    result = ask_ollama(prompt)
    logger.info(f"Kok neden analizi tamamlandi ({len(result)} karakter)")
    return result.strip()
