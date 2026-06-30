# scripts/ai_engine.py
"""
AI Analysis Engine — Ollama (local LLM) version.
No API key required. Talks to a locally-running Ollama server.
Implements tiered routing: a fast model triages every alert, and a
deep model re-analyzes anything that crosses the severity threshold.
"""

import json
import logging
import re
import time
from typing import Dict

import requests

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior SOC analyst with 10+ years of experience.
Analyze security alerts and respond ONLY with valid JSON.
No prose. No markdown fences. No <think> tags. Only the raw JSON object."""

USER_PROMPT_TEMPLATE = """Analyze this Wazuh security alert and return ONLY JSON:

Rule ID: {rule_id} | Level: {rule_level}/15 | Groups: {rule_groups}
Description: {rule_description}
Agent: {agent_name} (IP: {agent_ip})
Source IP: {source_ip} | Context: {ip_context}
Timestamp: {timestamp}
{extra_context_str}

Return this exact schema, nothing else:
{{
  "summary": "2-4 sentences: what happened, why it matters, immediate risk",
  "mitre_tactic": "Name (ID) e.g. Credential Access (TA0006)",
  "mitre_technique": "Name (ID) e.g. Brute Force (T1110)",
  "mitre_subtechnique": "Name (ID) or null",
  "severity_score": <1-10 integer>,
  "severity_justification": "Why this score: consider asset, IP type, frequency, impact",
  "investigation_steps": ["Step 1 with command", "Step 2", "Step 3", "Step 4", "Step 5"],
  "remediation_steps": ["Step 1 with command", "Step 2", "Step 3", "Step 4", "Step 5"],
  "false_positive_indicators": "What would indicate false positive",
  "escalation_needed": true or false
}}"""

REQUIRED_FIELDS = [
    "summary", "mitre_tactic", "mitre_technique", "severity_score",
    "severity_justification", "investigation_steps", "remediation_steps",
    "false_positive_indicators", "escalation_needed"
]


class AIEngine:
    """
    Performs AI-powered security alert analysis using local Ollama models,
    with tiered routing: a fast model triages every alert, and a deep
    model re-analyzes anything that crosses the severity threshold.
    """

    def __init__(self, model_fast: str = "llama3.1:8b",
                 model_deep: str = "deepseek-r1:14b",
                 deep_threshold: int = 7,
                 host: str = "http://localhost:11434",
                 max_tokens: int = 2048, temperature: float = 0.1,
                 max_retries: int = 3):
        self.model_fast = model_fast
        self.model_deep = model_deep
        self.deep_threshold = deep_threshold
        self.host = host.rstrip("/")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_retries = max_retries
        logger.info(
            f"AIEngine initialized — fast: {model_fast}, "
            f"deep: {model_deep} (threshold: {deep_threshold}+)"
        )

    def analyze(self, alert: Dict) -> Dict:
        """
        Two-pass analysis pipeline:
        1. Fast model performs initial triage on every alert
        2. If severity_score >= threshold, deep model re-analyzes for higher confidence
        """
        prompt = self._build_prompt(alert)

        # Pass 1 — fast model, every alert
        analysis = self._run_analysis(prompt, self.model_fast)
        analysis["_analysis_tier"] = "fast"

        # Pass 2 — conditional escalation
        if analysis["severity_score"] >= self.deep_threshold:
            logger.info(
                f"Severity {analysis['severity_score']} >= {self.deep_threshold} "
                f"— escalating to deep model ({self.model_deep})"
            )
            try:
                deep_analysis = self._run_analysis(prompt, self.model_deep)
                deep_analysis["_analysis_tier"] = "deep"
                deep_analysis["_fast_pass_score"] = analysis["severity_score"]
                analysis = deep_analysis
            except Exception as e:
                logger.warning(f"Deep analysis failed, keeping fast-pass result: {e}")

        analysis["_alert_id"] = alert.get("alert_id", "")
        return analysis

    def _run_analysis(self, prompt: str, model: str) -> Dict:
        """Run analysis with retry logic against a specific model."""
        for attempt in range(1, self.max_retries + 1):
            logger.debug(f"[{model}] attempt {attempt}/{self.max_retries}")
            try:
                raw_response = self._call_ollama(prompt, model)
                analysis = self._parse_response(raw_response)
                self._validate_response(analysis)
                analysis["_ai_model"] = model
                return analysis
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"[{model}] attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    raise ValueError(
                        f"Analysis failed after {self.max_retries} attempts "
                        f"with model {model}: {e}"
                    )
                time.sleep(1)

    def _call_ollama(self, prompt: str, model: str) -> str:
        """Call the local Ollama /api/chat endpoint."""
        response = requests.post(
            f"{self.host}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            },
            timeout=120  # Local inference can be slower than cloud, especially on CPU
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def _parse_response(self, raw: str) -> Dict:
        """
        Parse the model's response, handling common local-LLM formatting issues:
        - <think>...</think> reasoning blocks (DeepSeek-R1 and similar models)
        - Markdown code fences around JSON
        - Trailing prose before/after the JSON object
        """
        cleaned = raw.strip()

        # Strip reasoning model "thinking" traces
        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()

        # Strip markdown code fences
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\n?', '', cleaned)
            cleaned = re.sub(r'\n?```$', '', cleaned)
            cleaned = cleaned.strip()

        # Extract the JSON object if surrounded by other text
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group()

        return json.loads(cleaned)

    def _validate_response(self, analysis: Dict) -> None:
        """Validate schema compliance — treat AI output as untrusted input."""
        for field in REQUIRED_FIELDS:
            if field not in analysis:
                raise ValueError(f"Missing required field: '{field}'")

        score = analysis.get("severity_score")
        if not isinstance(score, int) or not 1 <= score <= 10:
            raise ValueError(f"Invalid severity_score: {score!r}. Must be integer 1-10.")

        for list_field in ["investigation_steps", "remediation_steps"]:
            if not isinstance(analysis.get(list_field), list):
                raise ValueError(f"'{list_field}' must be a list")
            if len(analysis[list_field]) < 3:
                raise ValueError(f"'{list_field}' must have at least 3 items")

    def _build_prompt(self, alert: Dict) -> str:
        enrichment = alert.get("enrichment", {})
        geoip = enrichment.get("geoip", {})
        ip_context = "internal network IP" if enrichment.get("is_internal") else (
            f"external IP from {geoip.get('country', 'unknown country')}, "
            f"org: {geoip.get('org', 'unknown')}" if geoip else "external IP (no geo data)"
        )

        extra = alert.get("extra_context", {})
        extra_lines = []
        if extra.get("changed_file"):
            extra_lines.append(f"Changed File: {extra['changed_file']}")
        if extra.get("target_user"):
            extra_lines.append(f"Target User: {extra['target_user']}")
        if extra.get("url"):
            extra_lines.append(f"URL: {extra['url']}")

        return USER_PROMPT_TEMPLATE.format(
            rule_id=alert.get("rule_id", "unknown"),
            rule_level=alert.get("rule_level", 0),
            rule_groups=alert.get("rule_groups_str", "unknown"),
            rule_description=alert.get("rule_description", "No description"),
            agent_name=alert.get("agent_name", "unknown"),
            agent_ip=alert.get("agent_ip") or "unknown",
            source_ip=alert.get("source_ip") or "N/A",
            ip_context=ip_context,
            timestamp=alert.get("timestamp", "unknown"),
            extra_context_str="\n".join(extra_lines)
        )

    def test_connection(self) -> Dict:
        """Verify Ollama is reachable and both configured models are pulled."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=10)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            fast_ok = any(self.model_fast in m for m in models)
            deep_ok = any(self.model_deep in m for m in models)
            return {
                "connected": True,
                "fast_model_available": fast_ok,
                "deep_model_available": deep_ok,
                "models_found": models
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
