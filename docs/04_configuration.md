# ⚙️ Configuration Reference — AI Security Alert Triage Assistant

> **Document:** `docs/04_configuration.md`

---

## Table of Contents

- [Environment Variables](#environment-variables)
- [Application Config (YAML)](#application-config-yaml)
- [MITRE Mapping Config](#mitre-mapping-config)
- [Severity Rules Config](#severity-rules-config)
- [Logging Configuration](#logging-configuration)
- [Configuration Best Practices](#configuration-best-practices)

---

## Environment Variables

All sensitive configuration lives in `.env`. **Never commit this file to Git.**

### Complete `.env` Reference

```env
# ============================================================
# AI Security Alert Triage Assistant — .env Configuration
# ============================================================

# ─── ANTHROPIC AI SETTINGS ─────────────────────────────────
# Your Claude API key from console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Model to use for analysis — claude-sonnet-4-6 recommended
# Options: claude-haiku-4-5-20251001 (faster/cheaper), claude-sonnet-4-6 (balanced)
AI_MODEL=claude-sonnet-4-6

# Max tokens in AI response (2048 is sufficient for triage)
AI_MAX_TOKENS=2048

# Temperature: 0.0=deterministic, 1.0=creative. Use low for security.
AI_TEMPERATURE=0.1

# ─── WAZUH API SETTINGS ────────────────────────────────────
# Full URL of your Wazuh manager (include https://)
WAZUH_HOST=https://192.168.1.100

# Wazuh API port (default: 55000)
WAZUH_PORT=55000

# Wazuh API username (create a read-only user for this)
WAZUH_USER=triage-reader

# Wazuh API password
WAZUH_PASSWORD=SecurePassword123!

# SSL certificate verification
# false = skip verification (OK for home lab with self-signed cert)
# true  = verify certificate (required in production)
WAZUH_VERIFY_SSL=false

# ─── POLLING SETTINGS ──────────────────────────────────────
# How often to check for new alerts (seconds)
POLL_INTERVAL=60

# Maximum alerts to retrieve per poll cycle
ALERT_LIMIT=10

# Minimum Wazuh rule level to process (1-15, Wazuh scale)
# 7 = moderate | 10 = high | 12 = critical
# Lower = more alerts | Higher = only severe
MIN_ALERT_LEVEL=7

# ─── OUTPUT SETTINGS ───────────────────────────────────────
# Directory to save generated reports
REPORT_OUTPUT_DIR=reports/

# Generate PDF copies of reports (requires WeasyPrint)
GENERATE_PDF=true

# ─── LOGGING ────────────────────────────────────────────────
# Log verbosity: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Path to audit log file
LOG_FILE=logs/triage.log
```

---

## Application Config (YAML)

The file `configs/config.yaml` controls application behavior (non-sensitive settings):

```yaml
# ============================================================
# AI Security Alert Triage Assistant — Application Config
# ============================================================

application:
  name: "AI Security Alert Triage Assistant"
  version: "1.0.0"
  description: "AI-powered Wazuh alert triage"

# Alert fields to extract from Wazuh API response
# Only listed fields are passed to AI (keeps prompts focused)
wazuh:
  api_timeout_seconds: 30
  token_refresh_interval: 800    # JWT expires at 900s, refresh at 800s
  extracted_fields:
    - id
    - rule.id
    - rule.level
    - rule.description
    - rule.groups
    - rule.mitre.id
    - rule.mitre.tactic
    - agent.id
    - agent.name
    - agent.ip
    - data.srcip
    - data.dstip
    - data.protocol
    - timestamp

# AI analysis configuration
ai_analysis:
  include_mitre_mapping: true
  include_investigation_steps: true
  include_remediation_steps: true
  investigation_step_count: 5
  remediation_step_count: 5
  severity_scale_max: 10
  retry_on_invalid_json: true
  max_retries: 3

# Report generation settings
reporting:
  output_formats:
    - markdown
    - pdf
  filename_pattern: "alert_{rule_id}_{timestamp}"
  include_raw_alert_json: true
  include_ai_prompt: false        # Set true for debugging
  include_audit_info: true
  markdown_template: "configs/report_template.md"
  html_template: "configs/report_template.html"

# Display settings for CLI
display:
  use_color: true
  show_progress_bars: true
  panel_width: 80                 # Characters wide
  severity_colors:                # Rich color names
    critical: "bold red"          # 9-10
    high: "red"                   # 7-8
    medium: "yellow"              # 4-6
    low: "green"                  # 1-3
```

---

## MITRE Mapping Config

The file `configs/mitre_mapping.json` provides a local lookup table mapping Wazuh rule groups to MITRE techniques. This supplements (and can correct) the AI's MITRE mapping:

```json
{
  "_comment": "Maps Wazuh rule groups to MITRE ATT&CK",
  "_version": "ATT&CK v14",
  "rule_group_mappings": {
    "authentication_failed": {
      "tactic": "Credential Access",
      "tactic_id": "TA0006",
      "technique": "Brute Force",
      "technique_id": "T1110"
    },
    "web": {
      "tactic": "Initial Access",
      "tactic_id": "TA0001",
      "technique": "Exploit Public-Facing Application",
      "technique_id": "T1190"
    },
    "rootkit": {
      "tactic": "Defense Evasion",
      "tactic_id": "TA0005",
      "technique": "Rootkit",
      "technique_id": "T1014"
    },
    "malware": {
      "tactic": "Execution",
      "tactic_id": "TA0002",
      "technique": "User Execution",
      "technique_id": "T1204"
    },
    "syscheck": {
      "tactic": "Defense Evasion",
      "tactic_id": "TA0005",
      "technique": "Indicator Removal",
      "technique_id": "T1070"
    },
    "firewall": {
      "tactic": "Discovery",
      "tactic_id": "TA0007",
      "technique": "Network Service Discovery",
      "technique_id": "T1046"
    }
  }
}
```

---

## Severity Rules Config

The file `configs/severity_rules.json` defines factors that adjust the AI severity score:

```json
{
  "_comment": "Additional scoring factors beyond AI base score",
  "wazuh_level_weight": {
    "description": "Add to score based on Wazuh rule level",
    "7":  0,
    "8":  0,
    "9":  1,
    "10": 2,
    "11": 2,
    "12": 3,
    "13": 3,
    "14": 4,
    "15": 5
  },
  "agent_criticality": {
    "description": "Agents tagged as critical add to score",
    "critical_agents": ["db-server", "dc-01", "finance-server"],
    "bonus_score": 2
  },
  "source_ip_factors": {
    "external_ip_bonus": 1,
    "known_bad_ip_bonus": 3,
    "internal_ip_penalty": -1
  },
  "time_of_day_factors": {
    "after_hours_bonus": 1,
    "business_hours_penalty": 0
  }
}
```

---

## Logging Configuration

The application uses Python's built-in `logging` module:

```python
# Generated log format:
# 2024-12-01 14:30:22,123 | INFO | triage | ALERT_RECEIVED | rule=5710 level=10
# 2024-12-01 14:30:23,456 | INFO | ai_engine | ANALYSIS_COMPLETE | score=8 technique=T1110.001
# 2024-12-01 14:30:23,789 | INFO | reporter | REPORT_SAVED | path=reports/alert_5710_...md

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
```

**Log levels:**

| Level | Use Case |
|-------|---------|
| `DEBUG` | Verbose output including full prompts and API responses |
| `INFO` | Normal operation — alert received, analysis complete, report saved |
| `WARNING` | Non-critical issues — retry needed, field missing |
| `ERROR` | Failures — API unreachable, JSON parse error |

---

## Configuration Best Practices

### Security
- ✅ Always use `.env` for secrets — never hardcode API keys
- ✅ Confirm `.env` is in `.gitignore` before every push
- ✅ Use a read-only Wazuh API user with minimal permissions
- ✅ Set `WAZUH_VERIFY_SSL=true` in any non-lab environment
- ✅ Rotate the Wazuh API password regularly

### Performance
- ✅ Start with `MIN_ALERT_LEVEL=10` to reduce noise during initial testing
- ✅ Set `POLL_INTERVAL=120` to avoid rate limits during development
- ✅ Set `AI_MAX_TOKENS=2048` — sufficient for triage, avoids excess cost
- ✅ Set `GENERATE_PDF=false` during development (PDF is slow)

### Cost Management (Claude API)
- Each alert analysis uses approximately 1,500–2,500 tokens
- At current Claude Sonnet pricing, processing 100 alerts ≈ $0.05–$0.15
- Use `claude-haiku-4-5-20251001` for higher-volume, lower-cost use cases

---

> **Previous:** [Installation ←](03_installation.md) | **Next:** [Usage →](05_usage.md)
