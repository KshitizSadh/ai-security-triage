# 🧪 Testing Guide — AI Security Alert Triage Assistant

> **Document:** `docs/06_testing.md`

---

## Overview

The test suite uses **pytest** and covers three levels:

| Level | Type | Files | Wazuh? | AI API? |
|-------|------|-------|--------|---------|
| Unit | Parser, utils | `test_parser.py` | ❌ | ❌ |
| Integration | AI engine | `test_ai_engine.py` | ❌ | ✅ |
| End-to-End | Full pipeline | `test_e2e.py` | ❌ (fixtures) | ✅ |

---

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run only unit tests (no API needed)
pytest tests/test_parser.py -v

# Run with coverage report
pytest tests/ -v --cov=scripts --cov-report=term-missing

# Run a specific test
pytest tests/test_parser.py::test_normalize_ssh_alert -v
```

---

## Test Structure

### Unit Tests: Alert Parser (`tests/test_parser.py`)

```python
import pytest
from scripts.parser import AlertParser

class TestAlertParser:
    def test_normalize_ssh_alert(self, sample_ssh_alert):
        """Parser extracts all required fields from SSH brute force alert."""
        parser = AlertParser()
        result = parser.normalize(sample_ssh_alert)

        assert result["rule_id"] == "5710"
        assert result["rule_level"] == 10
        assert result["agent_name"] == "web-server-01"
        assert result["source_ip"] == "203.0.113.45"
        assert result["rule_groups"] == ["authentication_failed", "ssh"]

    def test_handle_missing_source_ip(self, sample_alert_no_srcip):
        """Parser handles alerts without source IP gracefully."""
        parser = AlertParser()
        result = parser.normalize(sample_alert_no_srcip)
        assert result["source_ip"] is None   # Not a crash

    def test_alert_id_generation(self, sample_ssh_alert):
        """Parser generates unique, deterministic alert IDs."""
        parser = AlertParser()
        result = parser.normalize(sample_ssh_alert)
        assert "alert_id" in result
        assert "5710" in result["alert_id"]
```

### Integration Tests: AI Engine (`tests/test_ai_engine.py`)

```python
import pytest
from scripts.ai_engine import AIEngine
from scripts.parser import AlertParser

@pytest.mark.integration
class TestAIEngine:
    def test_analysis_returns_required_fields(self, normalized_ssh_alert):
        """AI analysis response includes all required triage fields."""
        engine = AIEngine()
        result = engine.analyze(normalized_ssh_alert)

        required_fields = [
            "summary", "mitre_tactic", "mitre_technique",
            "severity_score", "investigation_steps", "remediation_steps"
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_severity_score_in_range(self, normalized_ssh_alert):
        """Severity score is always between 1 and 10."""
        engine = AIEngine()
        result = engine.analyze(normalized_ssh_alert)
        assert 1 <= result["severity_score"] <= 10

    def test_mitre_technique_format(self, normalized_ssh_alert):
        """MITRE technique ID follows T#### format."""
        engine = AIEngine()
        result = engine.analyze(normalized_ssh_alert)
        # Should contain a pattern like T1110 or T1110.001
        import re
        assert re.search(r'T\d{4}(\.\d{3})?', result["mitre_technique"])
```

---

## Test Fixtures (`tests/fixtures/sample_alerts.json`)

```json
{
  "alerts": [
    {
      "id": "1701438622.123456",
      "_source": {
        "rule": {
          "id": "5710",
          "level": 10,
          "description": "sshd: brute force trying to get access to the system.",
          "groups": ["authentication_failed", "ssh"]
        },
        "agent": {
          "id": "001",
          "name": "web-server-01",
          "ip": "10.0.0.5"
        },
        "data": {
          "srcip": "203.0.113.45",
          "dstuser": "root"
        },
        "timestamp": "2024-12-01T14:30:22.000Z"
      }
    }
  ]
}
```

---

## Manual Testing Checklist

Before each commit, manually verify:

- [ ] `python main.py --mode demo` runs without errors
- [ ] At least one complete alert is triaged and displayed
- [ ] A `.md` report is created in `reports/`
- [ ] A `.pdf` report is created in `reports/` (if `GENERATE_PDF=true`)
- [ ] `pytest tests/ -v` passes all tests
- [ ] No API keys appear in output or logs

---

> **Previous:** [Usage ←](05_usage.md) | **Next:** [Troubleshooting →](07_troubleshooting.md)
