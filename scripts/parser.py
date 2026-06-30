# scripts/parser.py
"""Alert Parser — normalizes raw Wazuh alert JSON into a consistent format."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertParser:
    def normalize(self, raw_alert: Dict) -> Dict:
        source = raw_alert.get("_source", raw_alert)
        rule = source.get("rule", {})
        agent = source.get("agent", {})
        data = source.get("data", {})

        rule_id = str(rule.get("id", "unknown"))
        rule_level = int(rule.get("level", 0))
        rule_groups = rule.get("groups", [])

        source_ip = self._extract_source_ip(data, source)
        timestamp = source.get("timestamp", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        alert_id = self._generate_alert_id(rule_id, agent.get("name", "unknown"), timestamp)

        return {
            "alert_id": alert_id,
            "wazuh_id": raw_alert.get("_id", ""),
            "rule_id": rule_id,
            "rule_level": rule_level,
            "rule_description": rule.get("description", "No description"),
            "rule_groups": rule_groups,
            "rule_groups_str": ", ".join(rule_groups) if rule_groups else "unknown",
            "agent_id": agent.get("id", "000"),
            "agent_name": agent.get("name", "unknown-agent"),
            "agent_ip": agent.get("ip"),
            "source_ip": source_ip,
            "dest_ip": data.get("dstip"),
            "timestamp": timestamp,
            "extra_context": self._extract_extra_context(source, rule_groups),
            "raw_alert": raw_alert
        }

    def _extract_source_ip(self, data: Dict, source: Dict) -> Optional[str]:
        for ip in [data.get("srcip"), data.get("src_ip"), source.get("srcip")]:
            if ip and ip != "0.0.0.0":
                return ip
        return None

    def _extract_extra_context(self, source: Dict, groups: List[str]) -> Dict:
        context = {}
        data = source.get("data", {})
        if any("syscheck" in g for g in groups):
            sc = source.get("syscheck", {})
            context["changed_file"] = sc.get("path", "")
        if any("web" in g for g in groups):
            context["url"] = data.get("url", "")
        if any("auth" in g for g in groups):
            context["target_user"] = data.get("dstuser", "")
        return context

    def _generate_alert_id(self, rule_id: str, agent_name: str, timestamp: str) -> str:
        ts = timestamp.replace("-", "").replace(":", "").replace("T", "_").replace("Z", "").replace(".000", "")
        return f"{rule_id}_{agent_name}_{ts}"

    def normalize_batch(self, raw_alerts: List[Dict]) -> List[Dict]:
        out = []
        for raw in raw_alerts:
            try:
                out.append(self.normalize(raw))
            except Exception as e:
                logger.warning(f"Failed to parse alert: {e}")
        return out
