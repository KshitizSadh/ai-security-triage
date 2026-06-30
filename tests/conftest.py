# tests/conftest.py
"""Shared pytest fixtures for the test suite."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_alerts(fixtures_dir):
    """Load all sample alerts from the fixture file."""
    data = json.loads((fixtures_dir / "sample_alerts.json").read_text())
    return data["alerts"]


@pytest.fixture
def sample_ssh_alert(sample_alerts):
    """The SSH brute force alert (rule 5710) from fixtures."""
    for alert in sample_alerts:
        if alert["_source"]["rule"]["id"] == "5710":
            return alert
    raise ValueError("SSH brute force fixture (rule 5710) not found")


@pytest.fixture
def sample_sql_injection_alert(sample_alerts):
    """The SQL injection alert (rule 31103) from fixtures."""
    for alert in sample_alerts:
        if alert["_source"]["rule"]["id"] == "31103":
            return alert
    raise ValueError("SQL injection fixture (rule 31103) not found")


@pytest.fixture
def sample_fim_alert(sample_alerts):
    """The file integrity monitoring alert (rule 550) from fixtures."""
    for alert in sample_alerts:
        if alert["_source"]["rule"]["id"] == "550":
            return alert
    raise ValueError("FIM fixture (rule 550) not found")


@pytest.fixture
def sample_alert_no_srcip(sample_fim_alert):
    """FIM alerts have no srcip — reuse it to test missing-field handling."""
    return sample_fim_alert


@pytest.fixture
def normalized_ssh_alert(sample_ssh_alert):
    """A pre-normalized SSH alert, ready to pass into AlertEnricher / AIEngine."""
    from scripts.parser import AlertParser
    return AlertParser().normalize(sample_ssh_alert)
