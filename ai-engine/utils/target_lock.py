"""
Ayni deployment/pod icin AYNI ANDA birden fazla analiz+aksiyon calismasini
engeller. Onceki 'dedup' modulu SADECE ayni alarm ADI icin zaman bazli bir
bekleme uyguluyordu -- ama Kubernetes'in kendi varsayilan kurallari (orn.
KubePodCrashLooping) ile bizim ozel kuralimiz (PodCrashLooping) FARKLI
isimlerde oldugu icin AYNI pod icin ES ZAMANLI iki ayri analiz tetiklenebiliyor.
Bu da bir "race condition"a yol aciyor: biri rollback yaparken digeri farkli
(hatta cakisan) bir aksiyon uygulayabiliyor.

Bu modul, hedef (namespace/deployment) bazinda gercek bir mutex (kilit)
saglayarak ayni hedefe yonelik islemlerin SIRAYLA calismasini garanti eder.
"""
from threading import Lock

_locks: dict[str, Lock] = {}
_meta_lock = Lock()


def get_lock(key: str) -> Lock:
    with _meta_lock:
        if key not in _locks:
            _locks[key] = Lock()
        return _locks[key]
