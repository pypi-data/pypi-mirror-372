from typing import Dict, Optional

# Prometheus
try:
    from prometheus_client import Gauge, CollectorRegistry, push_to_gateway
except Exception:
    Gauge = None
    CollectorRegistry = None
    push_to_gateway = None

# StatsD
try:
    import statsd
except Exception:
    statsd = None


class MetricsExporters:
    def __init__(self, prometheus_gateway: Optional[str] = None, statsd_addr: Optional[str] = None, job: str = "blazemetrics"):
        self.prom_registry = CollectorRegistry() if CollectorRegistry is not None else None
        self.prom_gauges: Dict[str, "Gauge"] = {}
        self.prom_gateway = prometheus_gateway
        self.prom_job = job
        self.statsd_client = statsd.StatsClient(*(statsd_addr.split(":"))) if (statsd and statsd_addr) else None

    def export(self, metrics: Dict[str, float], labels: Optional[Dict[str, str]] = None):
        labels = labels or {}
        # Prometheus
        if self.prom_registry is not None and Gauge is not None:
            for k, v in metrics.items():
                if k not in self.prom_gauges:
                    g = Gauge(f"blazemetrics_{k}", f"BlazeMetrics metric {k}", list(labels.keys()), registry=self.prom_registry)
                    self.prom_gauges[k] = g
                self.prom_gauges[k].labels(**labels).set(v)
            if self.prom_gateway:
                try:
                    push_to_gateway(self.prom_gateway, job=self.prom_job, registry=self.prom_registry)
                except Exception:
                    pass
        # StatsD
        if self.statsd_client is not None:
            for k, v in metrics.items():
                try:
                    self.statsd_client.gauge(f"blazemetrics.{k}", v)
                except Exception:
                    pass 