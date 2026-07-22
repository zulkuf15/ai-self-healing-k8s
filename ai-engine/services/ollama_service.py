"""
Yerel Ollama LLM servisine prompt gonderip cevap alan ince (thin) katman.
"""
import requests
from config import Config
from utils.logger import logger


def ask_ollama(prompt: str, temperature: float = 0.2) -> str:
    try:
        resp = requests.post(
            f"{Config.OLLAMA_URL}/api/generate",
            json={
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                # num_predict: modelin uretecegi maksimum token sayisi.
                # Sinirlamazsak CPU'da model gereksiz uzun cevaplar yazip
                # yavaslayabiliyor -- kisa ve net JSON/aciklama icin yeterli.
                "options": {"temperature": temperature, "num_predict": 350},
            },
            timeout=240,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except requests.RequestException as e:
        logger.error(f"Ollama isteği basarisiz: {e}")
        return ""
