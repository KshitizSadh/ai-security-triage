# tests/test_reporter.py
"""
Unit tests for ReportGenerator.
These require NO external services — no Ollama, no Wazuh.
Run anytime with: pytest tests/test_reporter.py -v
"""

import tempfile
from pathlib import Path

from scripts.reporter import ReportGenerator
from scripts.parser import AlertParser


# A fake but schema-valid AI analysis — stands in for a real Ollama response
SAMPLE_ANALYSIS = {
    "summary": "Test summary of a brute force attack.",
    "mitre_tactic": "Credential Access (TA0006)",
    "mitre_technique": "Brute Force (T1110)",
    "mitre_subtechnique": "Password Guessing (T1110.001)",
    "severity_score": 8,
    "severity_justification": "High because external IP and production target.",
    "investigation_steps": [
        "Check auth.log", "Check for success", "Geolocate IP",
        "Check other agents", "Review sessions"
    ],
    "remediation_steps": [
        "Block IP", "Install fail2ban", "Disable password auth",
        "Change SSH port", "Enable key auth"
    ],
    "false_positive_indicators": "Known scanner IP would be a false positive.",
    "escalation_needed": False,
    "_ai_model": "llama3.1:8b",
    "_analysis_tier": "fast",
    "_alert_id": "5710_web-server-01_20241201"
}


class TestReportGenerator:
    def test_generate_creates_markdown_file(self, sample_ssh_alert):
        """generate() should create a .md file in the output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            alert = AlertParser().normalize(sample_ssh_alert)
            reporter = ReportGenerator(output_dir=tmpdir, generate_pdf=False)

            paths = reporter.generate(alert, SAMPLE_ANALYSIS)

            assert "markdown" in paths
            md_path = Path(paths["markdown"])
            assert md_path.exists()
            assert md_path.suffix == ".md"

    def test_markdown_content_includes_key_fields(self, sample_ssh_alert):
        """Generated report should contain the rule ID, severity, and MITRE mapping."""
        with tempfile.TemporaryDirectory() as tmpdir:
            alert = AlertParser().normalize(sample_ssh_alert)
            reporter = ReportGenerator(output_dir=tmpdir, generate_pdf=False)

            paths = reporter.generate(alert, SAMPLE_ANALYSIS)
            content = Path(paths["markdown"]).read_text(encoding="utf-8")

            assert "5710" in content
            assert "8/10" in content
            assert "T1110" in content
            assert "HIGH" in content

    def test_severity_label_critical(self):
        reporter = ReportGenerator(output_dir=tempfile.mkdtemp(), generate_pdf=False)
        label, icon = reporter._get_severity_label(10)
        assert label == "CRITICAL"

    def test_severity_label_low(self):
        reporter = ReportGenerator(output_dir=tempfile.mkdtemp(), generate_pdf=False)
        label, icon = reporter._get_severity_label(2)
        assert label == "LOW"

    def test_report_id_contains_rule_id(self, sample_ssh_alert):
        alert = AlertParser().normalize(sample_ssh_alert)
        reporter = ReportGenerator(output_dir=tempfile.mkdtemp(), generate_pdf=False)
        report_id = reporter._generate_report_id(alert)
        assert "5710" in report_id

    def test_no_pdf_when_disabled(self, sample_ssh_alert):
        """When generate_pdf=False, no PDF key should appear in the output paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            alert = AlertParser().normalize(sample_ssh_alert)
            reporter = ReportGenerator(output_dir=tmpdir, generate_pdf=False)
            paths = reporter.generate(alert, SAMPLE_ANALYSIS)
            assert "pdf" not in paths

    def test_output_directory_created_if_missing(self):
        """ReportGenerator should create the output dir if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "nested" / "reports"
            assert not target.exists()
            ReportGenerator(output_dir=str(target), generate_pdf=False)
            assert target.exists()
