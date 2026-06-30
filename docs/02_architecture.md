# 🏗️ Architecture — AI Security Alert Triage Assistant

> **Document:** `docs/02_architecture.md`
> **Purpose:** Explain every architectural component, design decision, and data flow

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Component Breakdown](#component-breakdown)
- [Data Flow](#data-flow)
- [Directory Architecture](#directory-architecture)
- [Module Design](#module-design)
- [AI Pipeline Architecture](#ai-pipeline-architecture)
- [Security Architecture](#security-architecture)
- [Design Decisions](#design-decisions)

---

## Architecture Overview

The AI Security Alert Triage Assistant follows a **pipeline architecture** — data flows linearly from source (Wazuh) through processing stages to output (reports). Each stage is a separate, testable module.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYSTEM OVERVIEW                             │
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │  Wazuh   │───▶│  Alert   │───▶│  AI      │───▶│   Report     │  │
│  │  SIEM    │    │  Parser  │    │  Engine  │    │  Generator   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────┘  │
│       │                │               │                │           │
│  REST API          Normalize      Claude API         Markdown       │
│  :55000           + Enrich        Analysis           + PDF          │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    SUPPORTING SYSTEMS                        │   │
│  │   Config Manager │ Audit Logger │ CLI Interface │ Tests     │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. 📡 Alert Poller (`scripts/poller.py`)

**What it does:** Connects to the Wazuh REST API at regular intervals and retrieves new security alerts.

**How it works:**
```python
# Simplified logic
class AlertPoller:
    def __init__(self, config):
        self.wazuh_url = config.WAZUH_HOST
        self.credentials = (config.WAZUH_USER, config.WAZUH_PASSWORD)
        self.interval = config.POLL_INTERVAL

    def get_token(self):
        """Authenticate with Wazuh API and get JWT token"""
        response = requests.post(
            f"{self.wazuh_url}/security/user/authenticate",
            auth=self.credentials, verify=False
        )
        return response.json()['data']['token']

    def fetch_alerts(self, min_level=7, limit=10):
        """Fetch alerts above minimum severity level"""
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "level": min_level,
            "limit": limit,
            "sort": "-timestamp"
        }
        response = requests.get(
            f"{self.wazuh_url}/security/events",
            headers=headers, params=params, verify=False
        )
        return response.json()['data']['affected_items']
```

**Key design choices:**
- Uses JWT token authentication (tokens expire, so we refresh per poll cycle)
- Configurable minimum alert level (default: 7 out of 15 — moderate and above)
- `verify=False` for lab environments (set to `True` with proper certificates in production)

---

### 2. 🔍 Alert Parser (`scripts/parser.py`)

**What it does:** Normalizes raw Wazuh alert JSON into a consistent internal format.

**Why this matters:** Wazuh alerts can have varying structures depending on the rule group. The parser ensures the AI engine always receives a predictable data structure.

```python
# Example normalization
raw_alert = {
    "_source": {
        "rule": {"id": "5710", "level": 10, "description": "SSH brute force..."},
        "agent": {"name": "web-server-01", "ip": "10.0.0.5"},
        "data": {"srcip": "192.168.1.105"},
        "timestamp": "2024-12-01T14:30:22.000Z"
    }
}

normalized_alert = {
    "alert_id": "1701438622_5710_web-server-01",
    "rule_id": "5710",
    "rule_level": 10,
    "rule_description": "SSH brute force attempt",
    "rule_groups": ["authentication_failed", "ssh"],
    "agent_name": "web-server-01",
    "agent_ip": "10.0.0.5",
    "source_ip": "192.168.1.105",
    "destination_ip": None,
    "timestamp": "2024-12-01T14:30:22Z",
    "raw_data": {...}  # Preserved for reference
}
```

---

### 3. 🧠 AI Engine (`scripts/ai_engine.py`)

**What it does:** The core of the project. Takes normalized alert data, constructs a structured prompt, calls the Claude API, and parses the structured JSON response.

**Prompt Architecture:**

The AI engine uses a **system + user** prompt pattern:

```
System Prompt (constant):
"You are a senior SOC analyst with 10+ years of experience.
 Analyze security alerts and respond ONLY with valid JSON.
 Always map to MITRE ATT&CK. Be specific and actionable."

User Prompt (per alert):
"Analyze this Wazuh security alert:
 Rule: {rule_id} | Level: {level}/15 | {description}
 Agent: {agent_name} ({agent_ip})
 Source IP: {source_ip}
 Timestamp: {timestamp}

 Return JSON with these exact fields:
 - summary (string): Plain-English explanation
 - mitre_tactic (string): e.g., 'Credential Access (TA0006)'
 - mitre_technique (string): e.g., 'Brute Force (T1110)'
 - mitre_subtechnique (string): e.g., 'Password Guessing (T1110.001)'
 - severity_score (int): 1-10
 - severity_justification (string): Why this score
 - investigation_steps (list): 5 specific steps
 - remediation_steps (list): 5 specific steps with commands"
```

**Response Validation:**
```python
REQUIRED_FIELDS = [
    "summary", "mitre_tactic", "mitre_technique",
    "severity_score", "investigation_steps", "remediation_steps"
]

def validate_response(response_dict):
    for field in REQUIRED_FIELDS:
        if field not in response_dict:
            raise ValueError(f"Missing required field: {field}")
    if not 1 <= response_dict["severity_score"] <= 10:
        raise ValueError("Severity score must be 1-10")
    return True
```

---

### 4. 📊 Report Generator (`scripts/reporter.py`)

**What it does:** Takes the alert + AI analysis and produces formatted outputs.

**Output formats:**

```
Alert + Analysis
     │
     ├──▶ Rich Terminal Output (real-time display)
     ├──▶ Markdown Report (reports/alert_{id}_{timestamp}.md)
     └──▶ PDF Report (reports/alert_{id}_{timestamp}.pdf)
         (Markdown → Jinja2 HTML Template → WeasyPrint PDF)
```

---

### 5. 📋 Config Manager (`scripts/utils.py`)

**What it does:** Loads and validates configuration from `.env` and `configs/config.yaml`.

```python
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    # Wazuh
    wazuh_host: str
    wazuh_port: int
    wazuh_user: str
    wazuh_password: str
    # AI
    anthropic_api_key: str
    ai_model: str
    # Application
    poll_interval: int
    min_alert_level: int

    @classmethod
    def from_env(cls):
        load_dotenv()
        return cls(
            wazuh_host=os.getenv("WAZUH_HOST"),
            wazuh_port=int(os.getenv("WAZUH_PORT", 55000)),
            # ... etc
        )
```

---

## Data Flow

### Complete Data Flow (Step-by-Step)

```
Step 1: AUTHENTICATION
  Client → POST /security/user/authenticate → Wazuh API
  Response: JWT Token (valid 900 seconds)

Step 2: ALERT RETRIEVAL
  Client → GET /security/events?level=7&limit=10 → Wazuh API
  Response: Array of raw alert JSON objects

Step 3: PARSING
  Raw JSON → parser.py → Normalized Alert Dict
  (Field extraction, type casting, null handling)

Step 4: ENRICHMENT (optional)
  Normalized Alert → enricher.py
  - GeoIP lookup for source IPs (ip-api.com)
  - Basic reputation check
  → Enriched Alert Dict

Step 5: AI ANALYSIS
  Enriched Alert → ai_engine.py
  → Prompt construction
  → POST /v1/messages → Claude API
  → Response parsing and validation
  → Analysis Dict (summary, MITRE, severity, steps)

Step 6: OUTPUT
  Alert + Analysis → reporter.py
  ├── Rich terminal display (immediate)
  ├── Markdown file (reports/)
  └── PDF file (reports/)

Step 7: LOGGING
  Every triage decision → audit logger
  Format: {timestamp} | {alert_id} | {severity_score} | {mitre_technique}
```

---

## AI Pipeline Architecture

### Prompt Engineering Strategy

The quality of AI output depends entirely on the quality of prompts. This project uses several prompt engineering techniques:

#### 1. Role Assignment
```
"You are a senior SOC analyst with 10 years of experience
 specializing in incident triage and threat analysis."
```
*Why:* LLMs perform better when given a specific, expert persona.

#### 2. Output Format Specification
```
"Respond ONLY with valid JSON. Do not include any prose,
 markdown code fences, or explanatory text outside the JSON object."
```
*Why:* Ensures machine-parseable, structured output every time.

#### 3. Few-Shot Examples (in system prompt)
```json
{
  "example_input": "SSH brute force, 47 attempts, level 10",
  "example_output": {
    "severity_score": 8,
    "mitre_tactic": "Credential Access (TA0006)"
  }
}
```
*Why:* Shows the model the expected output style.

#### 4. Chain of Thought (embedded in field descriptions)
```
"severity_justification: Explain step by step why you assigned
 this score, considering: source IP type, frequency, target criticality"
```
*Why:* Forces the model to reason before scoring.

#### 5. Temperature = 0.1
*Why:* Security analysis requires factual, consistent, deterministic output — not creative variation. Low temperature anchors responses to training knowledge.

---

## Security Architecture

### Credential Management

```
❌ NEVER:
   ANTHROPIC_API_KEY = "sk-ant-xxx"  # hardcoded in code

✅ ALWAYS:
   # In .env file (gitignored)
   ANTHROPIC_API_KEY=sk-ant-xxx

   # In code
   api_key = os.getenv("ANTHROPIC_API_KEY")
```

### API Security

| API | Authentication | Transport | Verification |
|-----|---------------|-----------|-------------|
| Wazuh REST API | JWT (Basic Auth for token) | HTTPS | Configurable (False for lab) |
| Claude API | API Key (Bearer Token) | HTTPS | Always verified |

### Principle of Least Privilege

The Wazuh API user created for this project should have **read-only** access:

```bash
# Create read-only API user in Wazuh
# Only needs: events:read, security:read
# Does NOT need: agents:write, rules:write, etc.
```

### Audit Trail

Every triage decision is logged:
```
2024-12-01 14:30:22 | INFO | TRIAGE | alert_id=5710_web-server-01 | \
  score=8 | technique=T1110.001 | analyst_action=auto
```

This creates an immutable record of all AI triage decisions for compliance and review.

---

## Design Decisions

### Why Wazuh?
- **Open source** — No licensing cost, ideal for portfolio projects
- **Feature-rich** — Agents, rules, FIM, compliance modules
- **REST API** — Well-documented, easy to integrate
- **Industry-relevant** — Used in real SOC environments

### Why Claude (Anthropic)?
- **Instruction following** — Excellent at structured JSON output
- **Security knowledge** — Strong foundational understanding of security concepts
- **Safety** — Less prone to generating harmful outputs
- **API quality** — Clean, well-documented Python SDK

### Why Pipeline Architecture?
- **Testability** — Each module can be unit-tested independently
- **Replaceability** — Can swap Wazuh for Splunk, Claude for GPT-4
- **Debuggability** — Easy to trace issues to a specific stage
- **Extensibility** — Add enrichment or output stages without refactoring

### Why Not a Web App (Yet)?
This v1.0 focuses on the **core logic** — the AI triage pipeline. A web UI would add complexity that could obscure the security concepts being demonstrated. A React frontend is planned for v2.0.

---

> **Previous:** [Introduction ←](01_introduction.md) | **Next:** [Installation →](03_installation.md)
