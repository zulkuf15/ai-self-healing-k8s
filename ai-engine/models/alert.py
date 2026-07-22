"""
Alertmanager webhook payload'inin (basitlestirilmis) veri modeli.
Referans: https://prometheus.io/docs/alerting/latest/configuration/#webhook_config
"""
from pydantic import BaseModel
from typing import Optional


class AlertItem(BaseModel):
    status: str  # "firing" | "resolved"
    labels: dict
    annotations: dict
    startsAt: Optional[str] = None

    @property
    def alertname(self) -> str:
        return self.labels.get("alertname", "unknown")

    @property
    def namespace(self) -> str:
        return self.labels.get("namespace", "unknown")

    @property
    def pod(self) -> Optional[str]:
        return self.labels.get("pod")

    @property
    def deployment(self) -> Optional[str]:
        return self.labels.get("deployment") or self.labels.get("workload")


class AlertmanagerWebhook(BaseModel):
    receiver: str
    status: str
    alerts: list[AlertItem]
