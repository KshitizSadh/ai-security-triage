# tests/test_parser.py
"""
Unit tests for AlertParser.
These require NO external services — no Ollama, no Wazuh.
Run anytime with: pytest tests/test_parser.py -v
"""

from scripts.parser import AlertParser


class TestAlertParser:
    def test_normalize_ssh_alert(self, sample_ssh_alert):
        """Parser extracts all required fields from the SSH brute force alert."""
        parser = AlertParser()
        result = parser.normalize(sample_ssh_alert)

        assert result["rule_id"] == "5710"
        assert result["rule_level"] == 10
        assert result["agent_name"] == "web-server-01"
        assert result["source_ip"] == "203.0.113.45"
        assert "authentication_failed" in result["rule_groups"]

    def test_normalize_sql_injection_alert(self, sample_sql_injection_alert):
        """Parser correctly extracts web-attack-specific context (URL)."""
        parser = AlertParser()
        result = parser.normalize(sample_sql_injection_alert)

        assert result["rule_id"] == "31103"
        assert result["source_ip"] == "198.51.100.22"
        assert "url" in result["extra_context"]
        assert "OR" in result["extra_context"]["url"]

    def test_handle_missing_source_ip(self, sample_alert_no_srcip):
        """Parser handles FIM alerts (which have no srcip) without crashing."""
        parser = AlertParser()
        result = parser.normalize(sample_alert_no_srcip)
        assert result["source_ip"] is None
        assert result["rule_id"] == "550"

    def test_fim_extra_context_has_changed_file(self, sample_fim_alert):
        """Parser extracts the changed file path for syscheck (FIM) alerts."""
        parser = AlertParser()
        result = parser.normalize(sample_fim_alert)
        assert result["extra_context"].get("changed_file") == "/etc/passwd"

    def test_alert_id_generation_is_deterministic(self, sample_ssh_alert):
        """Same input alert always produces the same alert_id."""
        parser = AlertParser()
        result1 = parser.normalize(sample_ssh_alert)
        result2 = parser.normalize(sample_ssh_alert)
        assert result1["alert_id"] == result2["alert_id"]
        assert "5710" in result1["alert_id"]

    def test_rule_groups_str_is_comma_joined(self, sample_ssh_alert):
        """rule_groups_str should be a human-readable joined string."""
        parser = AlertParser()
        result = parser.normalize(sample_ssh_alert)
        assert isinstance(result["rule_groups_str"], str)
        assert "," in result["rule_groups_str"] or len(result["rule_groups"]) == 1

    def test_normalize_batch_skips_bad_alerts(self, sample_alerts):
        """normalize_batch should not crash on a malformed entry — just skip it."""
        parser = AlertParser()
        broken_alert = {"_source": {}}  # missing everything
        batch = sample_alerts[:2] + [broken_alert]
        results = parser.normalize_batch(batch)
        # Should still get results for the 2 valid alerts at minimum
        assert len(results) >= 2

    def test_agent_fields_present(self, sample_ssh_alert):
        """Agent name, ID, and IP should all be extracted correctly."""
        parser = AlertParser()
        result = parser.normalize(sample_ssh_alert)
        assert result["agent_id"] == "001"
        assert result["agent_ip"] == "10.0.0.5"
