# 📘 Complete Implementation Guide — AI Security Alert Triage Assistant

> **Document:** `docs/implementation_guide.md`
> **Audience:** Beginners — every step includes purpose, theory, commands, expected output, and troubleshooting
> **Time to Complete:** 4–6 hours (including Wazuh setup)

---

## Table of Contents

- [Phase 1: Environment Preparation](#phase-1-environment-preparation)
- [Phase 2: Wazuh SIEM Setup](#phase-2-wazuh-siem-setup)
- [Phase 3: Core Application Development](#phase-3-core-application-development)
- [Phase 4: AI Engine Development](#phase-4-ai-engine-development)
- [Phase 5: Report Generation](#phase-5-report-generation)
- [Phase 6: CLI Interface](#phase-6-cli-interface)
- [Phase 7: Testing](#phase-7-testing)
- [Phase 8: Documentation & Portfolio](#phase-8-documentation--portfolio)

---

## Phase 1: Environment Preparation

### Step 1.1 — System Update and Base Dependencies

**Purpose:** Ensure a clean, updated system with all required system-level libraries before installing Python packages.

**Theory:** Python packages like WeasyPrint (PDF generation) depend on shared system libraries (libpango, libffi) that must be installed at the OS level before pip can install the Python bindings. Skipping this step is the #1 cause of installation failures.

**Commands:**
```bash
# Update package lists
sudo apt-get update

# Upgrade existing packages
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    nano \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libssl-dev \
    build-essential \
    python3-cffi \
    python3-brotli
```

**Expected Output:**
```
Reading package lists... Done
Building dependency tree... Done
...
0 newly installed, 0 to remove and 0 not changed.
```

**Verification:**
```bash
python3 --version     # Should show 3.10.x or higher
git --version         # Should show git version 2.x.x
curl --version        # Should show curl 7.x or higher
```

**Common Errors:**
- `E: Unable to locate package python3.10` → Run `sudo add-apt-repository ppa:deadsnakes/ppa` first
- `E: dpkg was interrupted` → Run `sudo dpkg --configure -a` then retry

**Security Best Practice:** Always update the system before installing project dependencies. Outdated system packages can contain known vulnerabilities that undermine the security of your tools.

---

### Step 1.2 — Python Virtual Environment

**Purpose:** Create an isolated Python environment to prevent dependency conflicts between this project and other Python projects on your system.

**Theory:** Python's global site-packages directory is shared across all projects. If Project A needs `requests==2.28.0` and Project B needs `requests==2.31.0`, they conflict. A virtual environment creates a completely isolated Python installation in a local directory — the `venv/` folder — that is used only for this project.

**Commands:**
```bash
# Navigate to projects directory
cd ~/projects

# Clone repository
git clone https://github.com/kshitiz/ai-security-triage.git
cd ai-security-triage

# Create virtual environment
python3 -m venv venv

# Verify creation
ls venv/bin/
# You should see: python, python3, pip, activate, etc.
```

**Activate the environment:**
```bash
source venv/bin/activate
```

**How to confirm activation:**
```bash
# Your prompt changes:
# Before: user@machine:~/projects/ai-security-triage$
# After:  (venv) user@machine:~/projects/ai-security-triage$

# Also:
which python   # Should show: ~/projects/ai-security-triage/venv/bin/python
```

**Install dependencies:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all project dependencies
pip install -r requirements.txt

# Verify key packages
pip list | grep -E "anthropic|requests|rich|weasyprint"
```

**Expected Output:**
```
anthropic          0.25.0
requests           2.31.0
rich               13.7.0
weasyprint         60.2
```

**Common Errors:**
- `error: Microsoft Visual C++ 14.0 or greater is required` (Windows) → Install Build Tools for VS
- `Failed building wheel for weasyprint` → Ensure `libpango-1.0-0` is installed (Step 1.1)
- `pip: command not found` → Use `pip3` instead of `pip`

---

### Step 1.3 — Environment Variable Configuration

**Purpose:** Securely configure application secrets (API keys, passwords) without hardcoding them in source code.

**Theory:** **Hardcoding secrets in code is one of the most common and dangerous security mistakes.** When you push code to GitHub with a hardcoded API key, that key is permanently in the Git history — even if you delete it later. Environment variables store secrets separately from code. The `.env` file lives only on your machine and is excluded from version control via `.gitignore`.

**Commands:**
```bash
# Copy the template
cp .env.example .env

# Open for editing
nano .env
```

**`.env` file contents to fill in:**
```env
# ─── AI CONFIGURATION ─────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
AI_MODEL=claude-sonnet-4-6
AI_MAX_TOKENS=2048
AI_TEMPERATURE=0.1

# ─── WAZUH CONFIGURATION ──────────────────────────────────
WAZUH_HOST=https://192.168.1.100
WAZUH_PORT=55000
WAZUH_USER=triage-reader
WAZUH_PASSWORD=YourSecurePassword123!
WAZUH_VERIFY_SSL=false

# ─── APPLICATION SETTINGS ─────────────────────────────────
POLL_INTERVAL=60
ALERT_LIMIT=10
MIN_ALERT_LEVEL=7
LOG_LEVEL=INFO
REPORT_OUTPUT_DIR=reports/
GENERATE_PDF=true
LOG_FILE=logs/triage.log
```

**Save and verify .gitignore:**
```bash
# Ensure .env is excluded from git
cat .gitignore | grep "\.env"

# Expected output:
# .env
# *.env

# Double-check: this command should produce output showing .env is ignored
git check-ignore -v .env
# Expected: .gitignore:1:.env    .env
```

**Security Best Practice:**
- **Never** use `git add .env` or `git add -A` without first checking `git status`
- **Always** run `git status` before committing to verify .env is not staged
- Consider adding a pre-commit hook: `pip install pre-commit && pre-commit install`

---

## Phase 2: Wazuh SIEM Setup

> **Skip to Phase 3 if using demo mode.**

### Step 2.1 — Verify Wazuh Manager is Running

**Purpose:** Confirm the Wazuh SIEM is operational before attempting API integration.

**Theory:** The Wazuh Manager is the central component that receives, processes, and stores security events from Wazuh Agents. It also runs the REST API server on port 55000. If the manager is down, no alerts will be generated and the API will be unreachable.

**Commands (run on Wazuh Manager host):**
```bash
# Check manager service status
sudo systemctl status wazuh-manager

# Check Wazuh API service status  
sudo systemctl status wazuh-api

# Check if port 55000 is listening
sudo ss -tlnp | grep 55000
```

**Expected Output:**
```
● wazuh-manager.service - Wazuh manager
   Active: active (running) since Thu 2024-12-01 10:00:00 UTC; 4h 30min ago
   ...
tcp   LISTEN  0  128  0.0.0.0:55000  0.0.0.0:*  users:(("wazuh-apid",pid=1234))
```

**If Wazuh is not running:**
```bash
sudo systemctl start wazuh-manager
sudo systemctl start wazuh-api
sudo systemctl enable wazuh-manager  # Start on boot
sudo systemctl enable wazuh-api
```

---

### Step 2.2 — Test Wazuh API Connectivity

**Purpose:** Verify the Wazuh REST API is accessible from your project machine before writing code.

**Theory:** The Wazuh REST API uses **HTTPS** (TLS-encrypted HTTP) with **JWT (JSON Web Token)** authentication. To interact with the API:
1. First, call the authentication endpoint with username/password
2. The API returns a short-lived JWT token
3. Include the JWT in the `Authorization: Bearer <token>` header for all subsequent requests

**Commands (run from project machine):**
```bash
# Replace values with your actual Wazuh details
WAZUH_IP="192.168.1.100"
WAZUH_USER="wazuh"
WAZUH_PASS="wazuh"

# Step 1: Get a JWT token
TOKEN=$(curl -s -k -u "${WAZUH_USER}:${WAZUH_PASS}" \
  "https://${WAZUH_IP}:55000/security/user/authenticate" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

echo "Token received: ${TOKEN:0:30}..."

# Step 2: Use token to list recent alerts
curl -s -k -H "Authorization: Bearer $TOKEN" \
  "https://${WAZUH_IP}:55000/security/events?limit=2&sort=-timestamp" \
  | python3 -m json.tool | head -50
```

**Expected Output:**
```json
{
    "data": {
        "affected_items": [
            {
                "_index": "wazuh-alerts-4.x-2024.12.01",
                "_source": {
                    "timestamp": "2024-12-01T14:30:22.000Z",
                    "rule": {
                        "level": 3,
                        "description": "PAM: Login session opened.",
                        "id": "5501"
                    },
                    "agent": {
                        "id": "001",
                        "name": "ubuntu-agent",
                        "ip": "10.0.0.5"
                    }
                }
            }
        ],
        "total_affected_items": 1250
    }
}
```

**Common Errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| `curl: (7) Failed to connect` | Wrong IP or port | Verify WAZUH_IP and port 55000 |
| `SSL certificate problem` | Self-signed cert | Add `-k` flag to curl (disables verification) |
| `{"error":6,"message":"Not authorized"}` | Wrong credentials | Check username/password |
| `{"error":1,"message":"No authorization header"}` | Missing token | Ensure Bearer token is in header |

---

### Step 2.3 — Create a Dedicated Read-Only API User

**Purpose:** Follow the principle of least privilege by creating an API user with only the permissions needed.

**Theory:** The default Wazuh `wazuh` user has full administrative access. If this credential is compromised (e.g., through the application), an attacker could modify detection rules, disable agents, or delete alerts. A read-only user limits the blast radius of a credential compromise.

**Commands:**

First, get a token with admin credentials:
```bash
# Authenticate with admin (wazuh) user
ADMIN_TOKEN=$(curl -s -k \
  -u "wazuh:wazuh" \
  "https://WAZUH_IP:55000/security/user/authenticate" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# Create a new user with read-only role
curl -s -k \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  "https://WAZUH_IP:55000/security/users" \
  -d '{"username": "triage-reader", "password": "TRiage@2024!SecurePass"}'
```

**Update your `.env` file with the new user:**
```env
WAZUH_USER=triage-reader
WAZUH_PASSWORD=TRiage@2024!SecurePass
```

---

## Phase 3: Core Application Development

### Step 3.1 — Alert Poller (`scripts/poller.py`)

**Purpose:** Implement the component that connects to Wazuh and retrieves alerts on a schedule.

**Theory:** API polling is a design pattern where the client repeatedly asks the server "do you have new data?" at regular intervals. An alternative is webhooks (server pushes data when available), but Wazuh's REST API uses polling. The poller handles:
- Authentication (token acquisition and refresh)
- Pagination (retrieving alerts in batches)
- Filtering (by alert level and time window)
- Error handling and retry logic

**Implementation:**
```python
# scripts/poller.py
"""
Wazuh Alert Poller
Handles authentication and alert retrieval from Wazuh REST API.
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings in lab environments
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)


class WazuhPoller:
    """
    Polls the Wazuh REST API for security alerts.
    
    Handles JWT authentication with automatic token refresh,
    configurable alert level filtering, and pagination.
    """
    
    # Wazuh JWT tokens expire at 900 seconds; refresh at 800 to be safe
    TOKEN_REFRESH_INTERVAL = 800

    def __init__(self, host: str, port: int, username: str, 
                 password: str, verify_ssl: bool = False):
        """
        Initialize the poller with Wazuh connection details.
        
        Args:
            host: Full URL of Wazuh manager (e.g., https://192.168.1.100)
            port: API port (default: 55000)
            username: Wazuh API username
            password: Wazuh API password
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = f"{host}:{port}"
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        
        self._token: Optional[str] = None
        self._token_acquired_at: Optional[float] = None
        
        logger.info(f"WazuhPoller initialized for {self.base_url}")

    def _get_token(self) -> str:
        """
        Acquire a JWT token from Wazuh API using Basic Auth.
        
        Returns:
            JWT token string
            
        Raises:
            ConnectionError: If Wazuh API is unreachable
            AuthenticationError: If credentials are invalid
        """
        auth_url = f"{self.base_url}/security/user/authenticate"
        
        try:
            response = requests.post(
                auth_url,
                auth=(self.username, self.password),
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            
            token = response.json()["data"]["token"]
            self._token_acquired_at = time.time()
            logger.debug("Wazuh API token acquired successfully")
            return token
            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot connect to Wazuh API at {self.base_url}. "
                f"Is Wazuh running? Error: {e}"
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise PermissionError(
                    "Wazuh API authentication failed. "
                    "Check WAZUH_USER and WAZUH_PASSWORD in .env"
                )
            raise

    def _get_valid_token(self) -> str:
        """Return a valid token, refreshing if approaching expiry."""
        if (self._token is None or 
            self._token_acquired_at is None or
            time.time() - self._token_acquired_at > self.TOKEN_REFRESH_INTERVAL):
            self._token = self._get_token()
        return self._token

    def fetch_alerts(self, 
                     min_level: int = 7,
                     limit: int = 10,
                     hours_back: int = 1) -> List[Dict]:
        """
        Retrieve security alerts from Wazuh API.
        
        Args:
            min_level: Minimum Wazuh rule level (1-15)
            limit: Maximum number of alerts to return
            hours_back: How far back to look for alerts (hours)
            
        Returns:
            List of normalized alert dictionaries
        """
        token = self._get_valid_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Calculate time window
        since = (datetime.utcnow() - timedelta(hours=hours_back)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        
        params = {
            "level": min_level,
            "limit": limit,
            "sort": "-timestamp",
            "timestamp": f">{since}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/security/events",
                headers=headers,
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            
            alerts = response.json().get("data", {}).get("affected_items", [])
            logger.info(f"Retrieved {len(alerts)} alerts (level>={min_level})")
            return alerts
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                # Token might have expired despite our refresh logic; retry once
                self._token = None
                return self.fetch_alerts(min_level, limit, hours_back)
            logger.error(f"Wazuh API error: {e}")
            return []

    def test_connection(self) -> Dict:
        """
        Test Wazuh API connectivity and return version info.
        
        Returns:
            Dict with connection status and Wazuh version
        """
        try:
            response = requests.get(
                f"{self.base_url}/",
                verify=self.verify_ssl,
                timeout=10
            )
            data = response.json().get("data", {})
            return {
                "connected": True,
                "version": data.get("api_version", "unknown"),
                "title": data.get("title", "Wazuh API")
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
```

**Expected Output (test_connection):**
```python
{
    "connected": True,
    "version": "4.7.0",
    "title": "Wazuh API"
}
```

---

### Step 3.2 — Alert Parser (`scripts/parser.py`)

**Purpose:** Normalize the raw, variable-structure Wazuh alert JSON into a consistent internal format.

**Theory:** Wazuh alerts have different structures depending on the rule group. For example:
- SSH alerts have `data.srcip` for the attacker IP
- Web alerts have `data.srcip` AND `data.id` (HTTP request ID)
- FIM alerts have `syscheck.path` for the changed file
- Windows alerts have `data.win.eventdata.*` fields

The parser handles this variability with safe field extraction (never raises KeyError on missing fields) and produces a flat, consistent dictionary that the rest of the pipeline can rely on.

**Implementation:**
```python
# scripts/parser.py
"""
Alert Parser
Normalizes raw Wazuh alert JSON into a consistent internal format.
"""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertParser:
    """
    Parses and normalizes raw Wazuh alert JSON.
    
    Handles the variable structure of different Wazuh rule groups
    and produces a consistent AlertDict for downstream processing.
    """
    
    def normalize(self, raw_alert: Dict) -> Dict:
        """
        Normalize a raw Wazuh alert into a consistent format.
        
        Args:
            raw_alert: Raw alert dict from Wazuh API
            
        Returns:
            Normalized alert dictionary with consistent fields
        """
        # Wazuh alerts have _source nested structure
        source = raw_alert.get("_source", raw_alert)
        
        rule = source.get("rule", {})
        agent = source.get("agent", {})
        data = source.get("data", {})
        
        # Extract core fields safely (no KeyError on missing fields)
        rule_id = str(rule.get("id", "unknown"))
        rule_level = int(rule.get("level", 0))
        rule_description = rule.get("description", "No description available")
        rule_groups = rule.get("groups", [])
        
        agent_name = agent.get("name", "unknown-agent")
        agent_id = agent.get("id", "000")
        agent_ip = agent.get("ip", None)
        
        # Source IP can be in different locations depending on rule type
        source_ip = self._extract_source_ip(data, source)
        dest_ip = data.get("dstip", None)
        
        # MITRE info (may be pre-populated by Wazuh if rule has MITRE mapping)
        mitre = rule.get("mitre", {})
        existing_mitre_ids = mitre.get("id", [])
        existing_mitre_tactics = mitre.get("tactic", [])
        
        timestamp_raw = source.get("timestamp", "")
        timestamp = self._normalize_timestamp(timestamp_raw)
        
        # Generate a deterministic unique ID for this alert
        alert_id = self._generate_alert_id(rule_id, agent_name, timestamp)
        
        normalized = {
            # Core identifiers
            "alert_id": alert_id,
            "wazuh_id": raw_alert.get("_id", ""),
            
            # Rule information
            "rule_id": rule_id,
            "rule_level": rule_level,
            "rule_description": rule_description,
            "rule_groups": rule_groups,
            "rule_groups_str": ", ".join(rule_groups) if rule_groups else "unknown",
            
            # Agent information
            "agent_id": agent_id,
            "agent_name": agent_name,
            "agent_ip": agent_ip,
            
            # Network information
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            
            # Timing
            "timestamp": timestamp,
            "timestamp_raw": timestamp_raw,
            
            # Existing MITRE data (from Wazuh rules, if available)
            "existing_mitre_ids": existing_mitre_ids,
            "existing_mitre_tactics": existing_mitre_tactics,
            
            # Extra context fields for specific rule types
            "extra_context": self._extract_extra_context(source, rule_groups),
            
            # Preserve original for reference
            "raw_alert": raw_alert
        }
        
        logger.debug(f"Parsed alert: rule={rule_id} level={rule_level} agent={agent_name}")
        return normalized

    def _extract_source_ip(self, data: Dict, source: Dict) -> Optional[str]:
        """Extract source IP from various possible locations in alert data."""
        # Common locations for source IP in Wazuh alerts
        candidates = [
            data.get("srcip"),
            data.get("src_ip"),
            source.get("srcip"),
            data.get("win", {}).get("eventdata", {}).get("ipAddress"),
        ]
        for ip in candidates:
            if ip and ip != "0.0.0.0":
                return ip
        return None

    def _extract_extra_context(self, source: Dict, groups: List[str]) -> Dict:
        """Extract rule-type-specific additional context fields."""
        context = {}
        data = source.get("data", {})
        
        # FIM (File Integrity Monitoring) context
        if "syscheck" in groups or any("syscheck" in g for g in groups):
            syscheck = source.get("syscheck", {})
            context["changed_file"] = syscheck.get("path", "")
            context["change_type"] = syscheck.get("event", "modified")
            context["md5_before"] = syscheck.get("md5_before", "")
            context["md5_after"] = syscheck.get("md5_after", "")
        
        # Web attack context
        if any("web" in g for g in groups):
            context["url"] = data.get("url", "")
            context["http_method"] = data.get("method", "")
            context["http_status"] = data.get("id", "")
        
        # Authentication context
        if any("auth" in g for g in groups):
            context["target_user"] = data.get("dstuser", data.get("user", ""))
            context["auth_method"] = data.get("type", "")
        
        # Process context
        if "process" in groups:
            context["process_name"] = data.get("command", "")
            context["process_pid"] = data.get("pid", "")
        
        return context

    def _normalize_timestamp(self, raw_ts: str) -> str:
        """Normalize various timestamp formats to ISO 8601 UTC."""
        if not raw_ts:
            return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        # Wazuh uses ISO 8601; just ensure consistent format
        return raw_ts.replace(".000Z", "Z").replace("+0000", "Z")

    def _generate_alert_id(self, rule_id: str, 
                            agent_name: str, timestamp: str) -> str:
        """Generate a unique, human-readable alert ID."""
        # Format: rule_agentname_YYYYMMDDHHMMSS
        ts_compact = timestamp.replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
        return f"{rule_id}_{agent_name}_{ts_compact}"

    def normalize_batch(self, raw_alerts: List[Dict]) -> List[Dict]:
        """Normalize a list of raw alerts, skipping any that fail parsing."""
        normalized = []
        for raw in raw_alerts:
            try:
                normalized.append(self.normalize(raw))
            except Exception as e:
                logger.warning(f"Failed to parse alert: {e}. Skipping.")
        return normalized
```

---

### Step 3.3 — Context Enricher (`scripts/enricher.py`)

**Purpose:** Add contextual information (like IP geolocation) to alerts before AI analysis.

**Theory:** Raw Wazuh alerts contain technical data but lack context. Knowing that a source IP is in Romania when your organization is in India makes a big difference to severity scoring. The enricher adds this context so the AI has more information to work with.

**Implementation:**
```python
# scripts/enricher.py
"""
Alert Context Enricher
Adds contextual information to normalized alerts before AI analysis.
Uses free public APIs (no key required) for demonstration purposes.
"""

import logging
import requests
from typing import Dict

logger = logging.getLogger(__name__)


class AlertEnricher:
    """Enriches alerts with contextual information."""

    GEOIP_API = "http://ip-api.com/json/{ip}?fields=status,country,city,org,threat"
    
    # Known internal/reserved IP ranges (very simplified)
    PRIVATE_RANGES = ["10.", "172.16.", "172.17.", "172.18.", 
                      "192.168.", "127.", "::1"]

    def enrich(self, alert: Dict) -> Dict:
        """
        Enrich an alert with additional context.
        
        Adds GeoIP information for external source IPs.
        Does not block on failure — enrichment is best-effort.
        
        Args:
            alert: Normalized alert dict from AlertParser
            
        Returns:
            Alert dict with 'enrichment' key added
        """
        enrichment = {
            "source_ip_type": "unknown",
            "geoip": None,
            "is_internal": False,
        }
        
        source_ip = alert.get("source_ip")
        
        if source_ip:
            # Determine if internal or external
            is_internal = any(source_ip.startswith(r) for r in self.PRIVATE_RANGES)
            enrichment["is_internal"] = is_internal
            enrichment["source_ip_type"] = "internal" if is_internal else "external"
            
            # GeoIP lookup for external IPs only
            if not is_internal:
                enrichment["geoip"] = self._geoip_lookup(source_ip)
        
        alert["enrichment"] = enrichment
        return alert

    def _geoip_lookup(self, ip: str) -> Dict:
        """
        Look up geographic information for an IP address.
        
        Uses ip-api.com free tier (45 req/min, no API key needed).
        Returns empty dict on failure — enrichment is non-critical.
        """
        try:
            response = requests.get(
                self.GEOIP_API.format(ip=ip),
                timeout=3  # Short timeout — enrichment shouldn't block triage
            )
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "country": data.get("country", ""),
                    "city": data.get("city", ""),
                    "org": data.get("org", "")
                }
        except Exception as e:
            logger.debug(f"GeoIP lookup failed for {ip}: {e}")
        
        return {}
```

---

## Phase 4: AI Engine Development

### Step 4.1 — Prompt Engineering

**Purpose:** Design the system and user prompts that produce reliable, structured security analysis from Claude.

**Theory — Why Prompt Engineering is Critical:**

Large language models like Claude are highly capable but require precise instructions to produce reliable, structured outputs. Without careful prompting:
- The model might explain rather than respond with JSON
- Field names might vary ("severity" vs "severity_score" vs "risk_score")
- Values might be out of expected ranges
- Analysis quality might vary wildly between runs

Good prompt engineering uses these techniques:

**1. System Prompt (Sets Context):**
The system prompt tells the model who it is and how it should behave throughout the conversation. It is sent once and persists.

**2. Explicit Format Instructions:**
"Return ONLY valid JSON" is critical. Without it, Claude might wrap JSON in explanatory prose or markdown code fences.

**3. Schema Definition:**
Providing the exact JSON schema prevents field name ambiguity and missing fields.

**4. Examples (Few-Shot Prompting):**
A minimal example response helps the model understand the expected output style.

**5. Low Temperature (0.1):**
Temperature controls randomness. For factual security analysis, we want highly deterministic, consistent outputs — not creative variation.

**Final Prompt Design:**

```python
SYSTEM_PROMPT = """You are a senior Security Operations Center (SOC) analyst 
with 10+ years of experience in incident response, threat analysis, and 
MITRE ATT&CK framework application.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a valid JSON object
2. Do NOT include any text before or after the JSON
3. Do NOT wrap the JSON in markdown code fences (no ```json)
4. Do NOT add explanations outside the JSON object
5. All fields in the schema are REQUIRED — never omit any field

You will analyze Wazuh SIEM security alerts and produce structured triage analysis.
Your analysis must be:
- Accurate and based on established security knowledge
- Actionable (specific commands for investigation and remediation)
- MITRE ATT&CK mapped to the most specific applicable technique
- Severity-scored considering full context, not just raw rule level"""

USER_PROMPT_TEMPLATE = """Analyze this Wazuh SIEM security alert and return ONLY a JSON object:

ALERT DETAILS:
- Rule ID: {rule_id}
- Rule Level: {rule_level}/15 (Wazuh severity scale)
- Rule Description: {rule_description}
- Rule Groups: {rule_groups}
- Agent (Target): {agent_name} (IP: {agent_ip})
- Source IP (Attacker): {source_ip}
- Timestamp: {timestamp}
- IP Context: {ip_context}
{extra_context}

Return this EXACT JSON schema (all fields required):
{{
  "summary": "2-4 sentence plain-English explanation of what happened, why it matters, and immediate risk",
  "mitre_tactic": "Full tactic name with ID, e.g., 'Credential Access (TA0006)'",
  "mitre_technique": "Full technique name with ID, e.g., 'Brute Force (T1110)'",
  "mitre_subtechnique": "Sub-technique if applicable, e.g., 'Password Guessing (T1110.001)' or null",
  "severity_score": <integer 1-10>,
  "severity_justification": "2-3 sentence explanation of why this score considering: asset criticality, source IP type, attack frequency, potential impact",
  "investigation_steps": [
    "Step 1: Specific action with exact command if applicable",
    "Step 2: ...",
    "Step 3: ...",
    "Step 4: ...",
    "Step 5: ..."
  ],
  "remediation_steps": [
    "Step 1: Specific action with exact command if applicable",
    "Step 2: ...",
    "Step 3: ...",
    "Step 4: ...",
    "Step 5: ..."
  ],
  "false_positive_indicators": "What would indicate this is a false positive",
  "escalation_needed": <true or false>
}}"""
```

---

### Step 4.2 — AI Engine Implementation (`scripts/ai_engine.py`)

**Implementation:**
```python
# scripts/ai_engine.py
"""
AI Analysis Engine
Sends normalized alerts to Claude API and returns structured triage analysis.
"""

import json
import logging
import re
import time
from typing import Dict, Optional

import anthropic

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior SOC analyst with 10+ years of experience.
Analyze security alerts and respond ONLY with valid JSON.
No prose. No markdown fences. Only the JSON object."""

USER_PROMPT_TEMPLATE = """Analyze this Wazuh security alert and return ONLY JSON:

Rule ID: {rule_id} | Level: {rule_level}/15 | Groups: {rule_groups}
Description: {rule_description}
Agent: {agent_name} (IP: {agent_ip})
Source IP: {source_ip} | Context: {ip_context}
Timestamp: {timestamp}
{extra_context_str}

Return this exact schema:
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
    """Performs AI-powered security alert analysis using Claude."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6",
                 max_tokens: int = 2048, temperature: float = 0.1,
                 max_retries: int = 3):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_retries = max_retries
        logger.info(f"AIEngine initialized with model: {model}")

    def analyze(self, alert: Dict) -> Dict:
        """
        Analyze a normalized alert using Claude AI.
        
        Args:
            alert: Normalized alert dict from AlertParser (+ enrichment)
            
        Returns:
            Analysis dict with summary, MITRE mapping, severity, steps
            
        Raises:
            ValueError: If valid analysis cannot be obtained after retries
        """
        prompt = self._build_prompt(alert)
        
        for attempt in range(1, self.max_retries + 1):
            logger.debug(f"AI analysis attempt {attempt}/{self.max_retries}")
            
            try:
                raw_response = self._call_claude(prompt)
                analysis = self._parse_response(raw_response)
                self._validate_response(analysis)
                
                # Add metadata
                analysis["_ai_model"] = self.model
                analysis["_alert_id"] = alert.get("alert_id", "")
                
                logger.info(
                    f"Analysis complete: score={analysis['severity_score']} "
                    f"technique={analysis['mitre_technique'][:30]}"
                )
                return analysis
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    raise ValueError(
                        f"AI analysis failed after {self.max_retries} attempts. "
                        f"Last error: {e}"
                    )
                time.sleep(1)  # Brief pause before retry

    def _call_claude(self, prompt: str) -> str:
        """Make the API call to Claude and return raw text response."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _parse_response(self, raw: str) -> Dict:
        """Parse Claude's response, handling common formatting issues."""
        cleaned = raw.strip()
        
        # Remove markdown code fences if present (```json ... ```)
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\n?', '', cleaned)
            cleaned = re.sub(r'\n?```$', '', cleaned)
            cleaned = cleaned.strip()
        
        # Find JSON object if surrounded by other text
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group()
        
        return json.loads(cleaned)

    def _validate_response(self, analysis: Dict) -> None:
        """Validate that the AI response contains all required fields."""
        for field in REQUIRED_FIELDS:
            if field not in analysis:
                raise ValueError(f"Missing required field: '{field}'")
        
        score = analysis.get("severity_score")
        if not isinstance(score, int) or not 1 <= score <= 10:
            raise ValueError(
                f"Invalid severity_score: {score!r}. Must be integer 1-10."
            )
        
        for list_field in ["investigation_steps", "remediation_steps"]:
            if not isinstance(analysis.get(list_field), list):
                raise ValueError(f"'{list_field}' must be a list")
            if len(analysis[list_field]) < 3:
                raise ValueError(f"'{list_field}' must have at least 3 items")

    def _build_prompt(self, alert: Dict) -> str:
        """Construct the analysis prompt from alert data."""
        enrichment = alert.get("enrichment", {})
        geoip = enrichment.get("geoip", {})
        
        ip_context = "internal network IP" if enrichment.get("is_internal") else (
            f"external IP from {geoip.get('country', 'unknown country')}, "
            f"org: {geoip.get('org', 'unknown')}"
            if geoip else "external IP (no geo data)"
        )
        
        # Build extra context string from rule-specific fields
        extra = alert.get("extra_context", {})
        extra_lines = []
        if extra.get("changed_file"):
            extra_lines.append(f"Changed File: {extra['changed_file']}")
        if extra.get("target_user"):
            extra_lines.append(f"Target User: {extra['target_user']}")
        if extra.get("url"):
            extra_lines.append(f"URL: {extra['url']}")
        extra_context_str = "\n".join(extra_lines)
        
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
            extra_context_str=extra_context_str
        )

    def test_connection(self) -> bool:
        """Test Claude API connectivity with a minimal request."""
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Reply with: OK"}]
            )
            return "OK" in resp.content[0].text
        except Exception as e:
            logger.error(f"Claude API test failed: {e}")
            return False
```

**Expected AI Response (example):**
```json
{
  "summary": "Multiple failed SSH login attempts detected from external IP 203.0.113.45 targeting the web-server-01 agent. 47 failed attempts in a 5-minute window is consistent with an automated brute force tool attempting to guess credentials. No successful authentication was detected, but the attack is ongoing and the source IP is from an unusual geographic location.",
  "mitre_tactic": "Credential Access (TA0006)",
  "mitre_technique": "Brute Force (T1110)",
  "mitre_subtechnique": "Password Guessing (T1110.001)",
  "severity_score": 8,
  "severity_justification": "High score due to: (1) external source IP from unusual location, (2) very high attempt frequency (47 in 5 minutes) indicating automation, (3) target is a production web server. Reduced from maximum because no successful authentication yet occurred.",
  "investigation_steps": [
    "Review auth log for full attack timeline: grep 'Failed password' /var/log/auth.log | grep '203.0.113.45'",
    "Check for any successful logins after failures: grep 'Accepted' /var/log/auth.log | tail -20",
    "GeoIP lookup the source IP: curl ipinfo.io/203.0.113.45",
    "Check if other agents are being targeted: Search Wazuh for same source IP in last hour",
    "Review current active SSH sessions: who && ss -tnp | grep :22"
  ],
  "remediation_steps": [
    "Block source IP immediately: sudo ufw deny from 203.0.113.45 to any port 22",
    "Install and enable fail2ban: sudo apt install fail2ban -y && sudo systemctl enable --now fail2ban",
    "Disable SSH password authentication in /etc/ssh/sshd_config: set PasswordAuthentication no, then: sudo systemctl restart sshd",
    "Consider moving SSH to non-standard port: Change 'Port 22' to 'Port 2222' in /etc/ssh/sshd_config",
    "Enable SSH key-based auth only: ssh-keygen -t ed25519 -C 'admin@$(hostname)' and add to authorized_keys"
  ],
  "false_positive_indicators": "Alert would be false positive if 203.0.113.45 is a known authorized IP (e.g., monitoring system, authorized pen test) or if the agent is a honeypot intentionally exposed.",
  "escalation_needed": false
}
```

---

## Phase 5: Report Generation

### Step 5.1 — Report Generator (`scripts/reporter.py`)

**Purpose:** Produce professional, formatted incident reports in Markdown and PDF formats.

**Theory:** Documentation is a core responsibility in incident response. The report serves multiple purposes:
- **Analyst reference** — Structured summary for immediate action
- **Ticket creation** — Can be copy-pasted into a ticket system
- **Audit trail** — Permanent record of the triage decision
- **Management reporting** — Professional format for non-technical stakeholders
- **Post-incident review** — Historical record for lessons learned

**Implementation:**
```python
# scripts/reporter.py
"""
Report Generator
Produces Markdown and PDF incident reports from alert + analysis data.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates formatted incident reports from triage analysis."""

    SEVERITY_LABELS = {
        (9, 10): ("CRITICAL", "🔴"),
        (7, 8):  ("HIGH",     "🟠"),
        (4, 6):  ("MEDIUM",   "🟡"),
        (1, 3):  ("LOW",      "🟢"),
    }

    def __init__(self, output_dir: str = "reports/", generate_pdf: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generate_pdf = generate_pdf

    def generate(self, alert: Dict, analysis: Dict) -> Dict[str, str]:
        """
        Generate all report formats for a triaged alert.
        
        Args:
            alert: Normalized alert dict
            analysis: AI analysis dict
            
        Returns:
            Dict with paths to generated report files
        """
        report_id = self._generate_report_id(alert)
        severity_label, severity_icon = self._get_severity_label(
            analysis.get("severity_score", 0)
        )
        
        context = {
            "report_id": report_id,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "alert": alert,
            "analysis": analysis,
            "severity_label": severity_label,
            "severity_icon": severity_icon,
        }
        
        output_paths = {}
        
        # Generate Markdown report
        md_path = self.output_dir / f"{report_id}.md"
        md_content = self._render_markdown(context)
        md_path.write_text(md_content, encoding="utf-8")
        output_paths["markdown"] = str(md_path)
        logger.info(f"Markdown report saved: {md_path}")
        
        # Generate PDF report (optional)
        if self.generate_pdf:
            try:
                pdf_path = self.output_dir / f"{report_id}.pdf"
                self._render_pdf(context, pdf_path)
                output_paths["pdf"] = str(pdf_path)
                logger.info(f"PDF report saved: {pdf_path}")
            except Exception as e:
                logger.warning(f"PDF generation failed: {e}. Markdown still saved.")
        
        return output_paths

    def _render_markdown(self, ctx: Dict) -> str:
        """Render the Markdown report template."""
        a = ctx["alert"]
        an = ctx["analysis"]
        score = an.get("severity_score", 0)
        
        steps_to_md = lambda steps: "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(steps)
        )
        
        return f"""# 🛡️ Incident Triage Report

**Report ID:** {ctx["report_id"]}  
**Generated:** {ctx["generated_at"]}  
**AI Model:** {an.get("_ai_model", "claude-sonnet-4-6")}  
**Severity:** {ctx["severity_icon"]} **{score}/10 — {ctx["severity_label"]}**

---

## Alert Details

| Field | Value |
|-------|-------|
| Rule ID | {a.get("rule_id", "N/A")} |
| Rule Level | {a.get("rule_level", "N/A")}/15 |
| Rule Description | {a.get("rule_description", "N/A")} |
| Rule Groups | {a.get("rule_groups_str", "N/A")} |
| Agent Name | {a.get("agent_name", "N/A")} |
| Agent IP | {a.get("agent_ip", "N/A")} |
| Source IP | {a.get("source_ip", "N/A")} |
| Timestamp | {a.get("timestamp", "N/A")} |

---

## AI Analysis Summary

{an.get("summary", "No summary available.")}

---

## MITRE ATT&CK Classification

| Field | Value |
|-------|-------|
| Tactic | {an.get("mitre_tactic", "N/A")} |
| Technique | {an.get("mitre_technique", "N/A")} |
| Sub-technique | {an.get("mitre_subtechnique") or "N/A"} |

---

## Severity Assessment

**Score: {score}/10 — {ctx["severity_label"]}**

{an.get("severity_justification", "No justification provided.")}

**Escalation Required:** {"✅ YES — Escalate to senior analyst" if an.get("escalation_needed") else "❌ No — Standard investigation"}

---

## Investigation Steps

{steps_to_md(an.get("investigation_steps", ["No steps available."]))}

---

## Remediation Steps

{steps_to_md(an.get("remediation_steps", ["No steps available."]))}

---

## False Positive Indicators

{an.get("false_positive_indicators", "No indicators specified.")}

---

## Audit Trail

| Event | Timestamp |
|-------|-----------|
| Alert Timestamp | {a.get("timestamp", "N/A")} |
| Report Generated | {ctx["generated_at"]} |
| Wazuh Alert ID | {a.get("wazuh_id", "N/A")} |
| Internal Alert ID | {a.get("alert_id", "N/A")} |
| AI Model Used | {an.get("_ai_model", "N/A")} |

---

*Report generated by AI Security Alert Triage Assistant v1.0.0*  
*This report is AI-generated. Human analyst review is required for all HIGH and CRITICAL alerts.*
"""

    def _render_pdf(self, ctx: Dict, output_path: Path) -> None:
        """Render a PDF from the Markdown report using WeasyPrint."""
        from weasyprint import HTML
        
        md_content = self._render_markdown(ctx)
        
        # Simple HTML wrapper for WeasyPrint
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; 
         color: #333; line-height: 1.6; }}
  h1 {{ color: #1a1a2e; border-bottom: 2px solid #e63946; padding-bottom: 10px; }}
  h2 {{ color: #16213e; border-left: 4px solid #e63946; padding-left: 10px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
  th {{ background-color: #16213e; color: white; padding: 8px 12px; text-align: left; }}
  td {{ border: 1px solid #ddd; padding: 8px 12px; }}
  tr:nth-child(even) {{ background-color: #f5f5f5; }}
  code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; 
         font-family: monospace; }}
  .severity-critical {{ color: #dc2626; font-weight: bold; }}
  .severity-high {{ color: #ea580c; font-weight: bold; }}
  .severity-medium {{ color: #ca8a04; font-weight: bold; }}
  .severity-low {{ color: #16a34a; font-weight: bold; }}
</style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: Arial;">{md_content}</pre>
</body>
</html>"""
        
        HTML(string=html_content).write_pdf(str(output_path))

    def _get_severity_label(self, score: int):
        """Get severity label and icon for a numeric score."""
        for (low, high), (label, icon) in self.SEVERITY_LABELS.items():
            if low <= score <= high:
                return label, icon
        return "UNKNOWN", "⚪"

    def _generate_report_id(self, alert: Dict) -> str:
        """Generate a human-readable report ID."""
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        rule_id = alert.get("rule_id", "unknown")
        agent = alert.get("agent_name", "unknown").replace("-", "_")
        return f"TRP_{ts}_{rule_id}_{agent}"
```

---

## Phase 6: CLI Interface

### Step 6.1 — Main Application Entry Point (`main.py`)

**Implementation:**
```python
# main.py
"""
AI Security Alert Triage Assistant
Main application entry point and CLI interface.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from scripts.poller import WazuhPoller
from scripts.parser import AlertParser
from scripts.enricher import AlertEnricher
from scripts.ai_engine import AIEngine
from scripts.reporter import ReportGenerator

# Load environment variables from .env file
load_dotenv()

console = Console()

BANNER = """
[bold blue]╔══════════════════════════════════════════════════════════════════╗[/]
[bold blue]║[/]    [bold white]🛡️  AI Security Alert Triage Assistant  v1.0.0[/]           [bold blue]║[/]
[bold blue]║[/]    [dim]Wazuh SIEM + Claude AI | SOC Automation Tool[/]                [bold blue]║[/]
[bold blue]╚══════════════════════════════════════════════════════════════════╝[/]
"""


def setup_logging(level: str = "INFO", log_file: str = "logs/triage.log"):
    """Configure application logging."""
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() if level == "DEBUG" else logging.NullHandler()
        ]
    )


def build_components():
    """Build and return all application components from environment config."""
    poller = WazuhPoller(
        host=os.getenv("WAZUH_HOST", "https://localhost"),
        port=int(os.getenv("WAZUH_PORT", 55000)),
        username=os.getenv("WAZUH_USER", ""),
        password=os.getenv("WAZUH_PASSWORD", ""),
        verify_ssl=os.getenv("WAZUH_VERIFY_SSL", "false").lower() == "true"
    )
    parser = AlertParser()
    enricher = AlertEnricher()
    ai_engine = AIEngine(
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        model=os.getenv("AI_MODEL", "claude-sonnet-4-6"),
        max_tokens=int(os.getenv("AI_MAX_TOKENS", 2048)),
        temperature=float(os.getenv("AI_TEMPERATURE", 0.1))
    )
    reporter = ReportGenerator(
        output_dir=os.getenv("REPORT_OUTPUT_DIR", "reports/"),
        generate_pdf=os.getenv("GENERATE_PDF", "true").lower() == "true"
    )
    return poller, parser, enricher, ai_engine, reporter


def process_alert(alert_raw, parser, enricher, ai_engine, reporter):
    """Run a single alert through the complete triage pipeline."""
    # Parse and normalize
    alert = parser.normalize(alert_raw)
    
    # Enrich with context
    alert = enricher.enrich(alert)
    
    # AI Analysis
    with console.status("[bold yellow]🤖 Analyzing with Claude AI...[/]"):
        analysis = ai_engine.analyze(alert)
    
    # Display results in CLI
    display_triage_result(alert, analysis)
    
    # Generate reports
    paths = reporter.generate(alert, analysis)
    
    # Show report paths
    if paths.get("markdown"):
        console.print(f"  📝 [green]{paths['markdown']}[/]")
    if paths.get("pdf"):
        console.print(f"  📋 [green]{paths['pdf']}[/]")
    
    return alert, analysis, paths


def display_triage_result(alert: dict, analysis: dict):
    """Display a formatted triage result in the terminal."""
    score = analysis.get("severity_score", 0)
    
    # Color based on severity
    if score >= 9:
        color = "bold red"
    elif score >= 7:
        color = "red"
    elif score >= 4:
        color = "yellow"
    else:
        color = "green"
    
    console.print()
    console.rule(
        f"[{color}]🚨 ALERT — Rule {alert['rule_id']} | "
        f"Level {alert['rule_level']}/15 | "
        f"Agent: {alert['agent_name']}[/]"
    )
    
    # Summary
    console.print(Panel(
        analysis.get("summary", "N/A"),
        title="[bold]📝 Summary[/]",
        border_style="blue"
    ))
    
    # MITRE + Severity table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="dim", width=20)
    table.add_column("Value")
    table.add_row("Tactic", analysis.get("mitre_tactic", "N/A"))
    table.add_row("Technique", analysis.get("mitre_technique", "N/A"))
    table.add_row("Sub-technique", analysis.get("mitre_subtechnique") or "N/A")
    table.add_row(f"[{color}]Severity Score[/]", 
                  f"[{color}]{score}/10[/]")
    table.add_row("Escalate", 
                  "✅ YES" if analysis.get("escalation_needed") else "❌ No")
    console.print(table)
    
    # Investigation steps
    console.print("\n[bold cyan]🔍 Investigation Steps:[/]")
    for i, step in enumerate(analysis.get("investigation_steps", []), 1):
        console.print(f"  {i}. {step}")
    
    # Remediation steps
    console.print("\n[bold green]🛠️  Remediation Steps:[/]")
    for i, step in enumerate(analysis.get("remediation_steps", []), 1):
        console.print(f"  {i}. {step}")
    
    console.print("\n[bold]📄 Reports saved:[/]")


def run_demo_mode(parser, enricher, ai_engine, reporter, limit: int):
    """Run in demo mode using fixture alerts."""
    import json
    fixtures_path = Path("tests/fixtures/sample_alerts.json")
    
    if not fixtures_path.exists():
        console.print("[red]ERROR: tests/fixtures/sample_alerts.json not found.[/]")
        console.print("Run: python scripts/utils.py --create-fixtures")
        sys.exit(1)
    
    alerts = json.loads(fixtures_path.read_text())["alerts"][:limit]
    console.print(f"[dim]📁 Demo mode: loaded {len(alerts)} sample alerts[/]\n")
    
    for i, raw_alert in enumerate(alerts, 1):
        console.print(f"\n[bold]Processing alert {i}/{len(alerts)}...[/]")
        process_alert(raw_alert, parser, enricher, ai_engine, reporter)


def main():
    """Main application entry point."""
    parser_cli = argparse.ArgumentParser(
        description="AI Security Alert Triage Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser_cli.add_argument("--mode", choices=["demo", "live", "batch", "single"],
                            default="demo", help="Operation mode")
    parser_cli.add_argument("--limit", type=int, default=10)
    parser_cli.add_argument("--min-level", type=int, default=7)
    parser_cli.add_argument("--alert-id", type=str, help="Specific alert ID")
    parser_cli.add_argument("--output", choices=["markdown", "pdf", "both"],
                            default="both")
    parser_cli.add_argument("--debug", action="store_true")
    args = parser_cli.parse_args()
    
    setup_logging(
        level="DEBUG" if args.debug else os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE", "logs/triage.log")
    )
    
    console.print(BANNER)
    
    poller, alert_parser, enricher, ai_engine, reporter = build_components()
    
    # Validate API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]ERROR: ANTHROPIC_API_KEY not set in .env[/]")
        sys.exit(1)
    
    if args.mode == "demo":
        run_demo_mode(alert_parser, enricher, ai_engine, reporter, args.limit)
    elif args.mode == "live":
        with console.status("[cyan]Connecting to Wazuh...[/]"):
            conn = poller.test_connection()
        if not conn["connected"]:
            console.print(f"[red]Cannot connect to Wazuh: {conn.get('error')}[/]")
            sys.exit(1)
        console.print(f"[green]✅ Wazuh connected (v{conn['version']})[/]")
        
        with console.status("[cyan]Fetching alerts...[/]"):
            raw_alerts = poller.fetch_alerts(
                min_level=args.min_level, limit=args.limit
            )
        
        if not raw_alerts:
            console.print(f"[yellow]No alerts found above level {args.min_level}.[/]")
            return
        
        console.print(f"[green]Found {len(raw_alerts)} alerts to triage.[/]")
        for raw in raw_alerts:
            process_alert(raw, alert_parser, enricher, ai_engine, reporter)
    
    console.print("\n[bold green]✅ Triage session complete.[/]")


if __name__ == "__main__":
    main()
```

---

## Phase 7: Testing

### Step 7.1 — Create Sample Alert Fixtures

```bash
mkdir -p tests/fixtures
```

Create `tests/fixtures/sample_alerts.json` with representative Wazuh alerts (SSH brute force, port scan, file integrity violation, privilege escalation, web attack).

### Step 7.2 — Run the Test Suite

```bash
# All tests
pytest tests/ -v --tb=short

# With coverage
pytest tests/ -v --cov=scripts --cov-report=term-missing --cov-report=html

# Open coverage report
firefox htmlcov/index.html
```

---

## Phase 8: Documentation & Portfolio

### Step 8.1 — Final Checklist Before Publishing

```bash
# 1. Verify .env is gitignored
git check-ignore -v .env

# 2. Check for any hardcoded secrets
grep -r "sk-ant" scripts/ main.py configs/   # Should return nothing
grep -r "password" scripts/ --include="*.py" # Should show only env var reads

# 3. Run all tests
pytest tests/ -v

# 4. Run demo mode
python main.py --mode demo --limit 2

# 5. Check generated files
ls -la reports/
ls -la logs/

# 6. Final git push
git add .
git commit -m "feat: complete AI Security Alert Triage Assistant v1.0.0"
git push origin main
```

### Step 8.2 — GitHub Release

```bash
# Tag the release
git tag -a v1.0.0 -m "Initial release: AI Security Alert Triage Assistant"
git push origin v1.0.0
```

---

> **Implementation complete.** Return to [README](../README.md) or see [Usage Guide](05_usage.md) for operating instructions.
