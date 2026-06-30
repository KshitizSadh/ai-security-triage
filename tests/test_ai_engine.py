# tests/test_ai_engine.py
"""
Integration tests for AIEngine.
These REQUIRE Ollama running locally with llama3.1:8b pulled.
If Ollama isn't reachable, these tests are SKIPPED automatically
rather than failing — so `pytest tests/` is always safe to run.

Run only these with: pytest tests/test_ai_engine.py -v
"""

import re

import pytest
import requests

from scripts.ai_engine import AIEngine


def ollama_is_available(host="http://localhost:11434", model="llama3.1:8b"):
    """Check if Ollama is running and the fast model is pulled."""
    try:
        resp = requests.get(f"{host}/api/tags", timeout=3)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        return any(model in m for m in models)
    except Exception:
        return False


requires_ollama = pytest.mark.skipif(
    not ollama_is_available(),
    reason="Ollama not running or llama3.1:8b not pulled — run: ollama pull llama3.1:8b"
)


@requires_ollama
class TestAIEngine:
    def test_analysis_returns_required_fields(self, normalized_ssh_alert):
        """AI analysis response includes all required triage fields."""
        engine = AIEngine(model_fast="llama3.1:8b", model_deep="llama3.1:8b")
        result = engine.analyze(normalized_ssh_alert)

        required_fields = [
            "summary", "mitre_tactic", "mitre_technique",
            "severity_score", "investigation_steps", "remediation_steps"
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_severity_score_in_range(self, normalized_ssh_alert):
        """Severity score is always between 1 and 10."""
        engine = AIEngine(model_fast="llama3.1:8b", model_deep="llama3.1:8b")
        result = engine.analyze(normalized_ssh_alert)
        assert 1 <= result["severity_score"] <= 10

    def test_mitre_technique_format(self, normalized_ssh_alert):
        """MITRE technique ID follows T#### format."""
        engine = AIEngine(model_fast="llama3.1:8b", model_deep="llama3.1:8b")
        result = engine.analyze(normalized_ssh_alert)
        assert re.search(r'T\d{4}(\.\d{3})?', result["mitre_technique"])

    def test_investigation_steps_is_nonempty_list(self, normalized_ssh_alert):
        engine = AIEngine(model_fast="llama3.1:8b", model_deep="llama3.1:8b")
        result = engine.analyze(normalized_ssh_alert)
        assert isinstance(result["investigation_steps"], list)
        assert len(result["investigation_steps"]) >= 3

    def test_connection_check_works(self):
        """test_connection() correctly reports Ollama and model availability."""
        engine = AIEngine(model_fast="llama3.1:8b", model_deep="llama3.1:8b")
        status = engine.test_connection()
        assert status["connected"] is True
        assert status["fast_model_available"] is True


class TestAIEngineParsing:
    """
    These tests do NOT require Ollama — they test the response parser directly
    against pre-recorded model output, including the messy formatting real
    local models sometimes produce.
    """

    def test_strips_think_tags(self):
        engine = AIEngine.__new__(AIEngine)  # bypass __init__, no host needed
        raw = '<think>Let me consider this...</think>{"summary": "test"}'
        result = engine._parse_response(raw)
        assert result == {"summary": "test"}

    def test_strips_markdown_fences(self):
        engine = AIEngine.__new__(AIEngine)
        raw = '```json\n{"summary": "test"}\n```'
        result = engine._parse_response(raw)
        assert result == {"summary": "test"}

    def test_extracts_json_from_surrounding_prose(self):
        engine = AIEngine.__new__(AIEngine)
        raw = 'Here is my analysis: {"summary": "test"} Hope that helps!'
        result = engine._parse_response(raw)
        assert result == {"summary": "test"}

    def test_validate_response_rejects_missing_field(self):
        engine = AIEngine.__new__(AIEngine)
        incomplete = {"summary": "test"}  # missing everything else
        with pytest.raises(ValueError, match="Missing required field"):
            engine._validate_response(incomplete)

    def test_validate_response_rejects_bad_severity(self):
        engine = AIEngine.__new__(AIEngine)
        bad = {
            "summary": "x", "mitre_tactic": "x", "mitre_technique": "x",
            "severity_score": 15,  # out of range
            "severity_justification": "x",
            "investigation_steps": ["a", "b", "c"],
            "remediation_steps": ["a", "b", "c"],
            "false_positive_indicators": "x", "escalation_needed": False
        }
        with pytest.raises(ValueError, match="severity_score"):
            engine._validate_response(bad)
