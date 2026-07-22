"""
Loki'den, alarmi tetikleyen pod/namespace'e ait son loglari ceker.
Bu loglar, LLM'e "kok neden ne?" diye sorarken kanit olarak kullanilir.
"""
import time
import requests
from config import Config
from utils.logger import logger


def fetch_recent_logs(namespace: str, pod: str | None = None, minutes: int = 10, limit: int = 100) -> str:
    end = int(time.time() * 1e9)
    start = end - (minutes * 60 * int(1e9))

    query = f'{{namespace="{namespace}"}}'
    if pod:
        query = f'{{namespace="{namespace}", pod=~"{pod}.*"}}'

    try:
        resp = requests.get(
            f"{Config.LOKI_URL}/loki/api/v1/query_range",
            params={"query": query, "start": start, "end": end, "limit": limit, "direction": "backward"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error(f"Loki sorgusu basarisiz: {e}")
        return ""

    lines = []
    for stream in data.get("data", {}).get("result", []):
        for _, line in stream.get("values", []):
            lines.append(line)

    # en yeni loglar basta geldigi icin kronolojik siraya cevir
    lines.reverse()
    return "\n".join(lines[-limit:])
