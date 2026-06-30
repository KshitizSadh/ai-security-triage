# scripts/enricher.py
"""Adds GeoIP and internal/external context to alerts before AI analysis."""

import logging
import requests
from typing import Dict

logger = logging.getLogger(__name__)


class AlertEnricher:
    GEOIP_API = "http://ip-api.com/json/{ip}?fields=status,country,city,org"
    PRIVATE_RANGES = ["10.", "172.16.", "192.168.", "127."]

    def enrich(self, alert: Dict) -> Dict:
        enrichment = {"source_ip_type": "unknown", "geoip": None, "is_internal": False}
        source_ip = alert.get("source_ip")

        if source_ip:
            is_internal = any(source_ip.startswith(r) for r in self.PRIVATE_RANGES)
            enrichment["is_internal"] = is_internal
            enrichment["source_ip_type"] = "internal" if is_internal else "external"
            if not is_internal:
                enrichment["geoip"] = self._geoip_lookup(source_ip)

        alert["enrichment"] = enrichment
        return alert

    def _geoip_lookup(self, ip: str) -> Dict:
        try:
            r = requests.get(self.GEOIP_API.format(ip=ip), timeout=3)
            d = r.json()
            if d.get("status") == "success":
                return {"country": d.get("country", ""), "org": d.get("org", "")}
        except Exception as e:
            logger.debug(f"GeoIP lookup failed: {e}")
        return {}
