"""
Kubernetes API'sine (in-cluster ServiceAccount uzerinden) aksiyon uygular.
Sadece decision_engine tarafindan zaten dogrulanmis, whitelist'teki
aksiyonlar buraya ulasir -- burasi 'son kapi' degil, ikinci savunma katmani.
"""
from kubernetes import client, config as k8s_config
from utils.logger import logger

try:
    k8s_config.load_incluster_config()
except k8s_config.ConfigException:
    # Pod disinda (lokal test) calisirken kubeconfig'e dus
    k8s_config.load_kube_config()

core_v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()


def restart_pod(namespace: str, deployment_name: str) -> dict:
    """
    LLM'e tam pod adini (rastgele son ekli, orn. crashloop-demo-6bdb9d8787-ggdrw)
    tahmin ettirmek yerine, deployment_name'i 'app' etiketiyle eslestirip
    o deployment'a ait pod(lar)i buluyoruz ve siliyoruz -- sahibi bir
    Deployment/ReplicaSet ise otomatik yeniden olusturulur.
    """
    try:
        pods = core_v1.list_namespaced_pod(namespace, label_selector=f"app={deployment_name}")
        if not pods.items:
            msg = f"'{deployment_name}' etiketine sahip pod bulunamadi (namespace: {namespace})"
            logger.warning(msg)
            return {"success": False, "detail": msg}

        deleted = []
        for pod in pods.items:
            core_v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
            deleted.append(pod.metadata.name)

        logger.success(f"Pod(lar) silindi (restart): {namespace}/{deleted}")
        return {"success": True, "detail": f"{deleted} silindi, yeniden olusturulacak"}
    except client.ApiException as e:
        logger.error(f"Pod silinemedi: {e}")
        return {"success": False, "detail": str(e)}


def scale_deployment(namespace: str, deployment_name: str, replicas: int = 2) -> dict:
    try:
        apps_v1.patch_namespaced_deployment_scale(
            name=deployment_name, namespace=namespace, body={"spec": {"replicas": replicas}}
        )
        logger.success(f"Deployment scale edildi: {namespace}/{deployment_name} -> {replicas} replika")
        return {"success": True, "detail": f"{replicas} replikaya scale edildi"}
    except client.ApiException as e:
        logger.error(f"Scale basarisiz: {e}")
        return {"success": False, "detail": str(e)}


def get_previous_revision(namespace: str, deployment_name: str):
    """
    Onceki (mevcuttan farkli, daha kucuk revizyon numarali) bir ReplicaSet
    var mi diye BAKAR, hicbir sey DEGISTIRMEZ. Prompt'a "rollback mumkun mu"
    bilgisini vermek icin kullanilir.
    """
    try:
        deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
        current_rev = int(deployment.metadata.annotations.get("deployment.kubernetes.io/revision", "0"))
        rs_list = apps_v1.list_namespaced_replica_set(namespace, label_selector=f"app={deployment_name}")

        prev_revs = []
        for rs in rs_list.items:
            owner_match = any(o.kind == "Deployment" and o.name == deployment_name for o in (rs.metadata.owner_references or []))
            rev = rs.metadata.annotations.get("deployment.kubernetes.io/revision") if rs.metadata.annotations else None
            if owner_match and rev is not None and int(rev) < current_rev:
                prev_revs.append(int(rev))

        return max(prev_revs) if prev_revs else None
    except client.ApiException as e:
        logger.warning(f"Revizyon gecmisi okunamadi: {e}")
        return None


def rollback_deployment(namespace: str, deployment_name: str) -> dict:
    """
    Deployment'i, bir onceki (saglikli) ReplicaSet revizyonunun pod template'ine
    geri dondurur -- 'kubectl rollout undo' ile ayni mantik.
    """
    try:
        deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
        current_rev = int(deployment.metadata.annotations.get("deployment.kubernetes.io/revision", "0"))

        rs_list = apps_v1.list_namespaced_replica_set(
            namespace,
            label_selector=f"app={deployment_name}",
        )

        candidates = []
        for rs in rs_list.items:
            owner_match = any(o.kind == "Deployment" and o.name == deployment_name for o in (rs.metadata.owner_references or []))
            rev = rs.metadata.annotations.get("deployment.kubernetes.io/revision") if rs.metadata.annotations else None
            if owner_match and rev is not None:
                candidates.append((int(rev), rs))

        previous = [rs for rev, rs in candidates if rev < current_rev]
        if not previous:
            msg = f"'{deployment_name}' icin geri donulecek onceki bir revizyon bulunamadi"
            logger.warning(msg)
            return {"success": False, "detail": msg}

        # en yuksek revizyon numarali (yani bir onceki) ReplicaSet'i sec
        previous.sort(key=lambda rs: int(rs.metadata.annotations["deployment.kubernetes.io/revision"]))
        target_rs = previous[-1]

        deployment.spec.template = target_rs.spec.template
        apps_v1.patch_namespaced_deployment(deployment_name, namespace, deployment)

        target_rev = target_rs.metadata.annotations["deployment.kubernetes.io/revision"]
        logger.success(f"Deployment rollback edildi: {namespace}/{deployment_name} -> revizyon {target_rev}")
        return {"success": True, "detail": f"revizyon {target_rev}'e geri donuldu"}
    except client.ApiException as e:
        logger.error(f"Rollback basarisiz: {e}")
        return {"success": False, "detail": str(e)}
