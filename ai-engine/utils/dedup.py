"""
Ayni alarmi (namespace+pod+alertname) kisa bir sure icinde tekrar tekrar
islemeyi engeller. CrashLoopBackOff gibi durumlar Prometheus metriginde
"titreyebilir" (flapping) ve ayni alarm arka arkaya birkac kez firing
olarak gelebilir -- bu da yavas calisan LLM'i gereksiz yere kuyruga sokar.

Not: Bu basit bir in-memory cozum (pod yeniden baslarsa sifirlanir).
Production'da Redis gibi paylasimli bir store tercih edilir.
"""
import time
from threading import Lock

_last_seen: dict[str, float] = {}
_lock = Lock()

COOLDOWN_SECONDS = 180  # ayni alarm icin 3 dakika bekleme suresi


def should_process(key: str) -> bool:
    now = time.time()
    with _lock:
        last = _last_seen.get(key)
        if last is not None and (now - last) < COOLDOWN_SECONDS:
            return False
        _last_seen[key] = now
        return True
