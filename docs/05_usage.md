# 🖥️ Usage Guide — AI Security Alert Triage Assistant

> **Document:** `docs/05_usage.md`

---

## Table of Contents

- [Running Modes](#running-modes)
- [CLI Reference](#cli-reference)
- [Demo Mode (No Wazuh Required)](#demo-mode)
- [Live Mode](#live-mode)
- [Batch Mode](#batch-mode)
- [Understanding the Output](#understanding-the-output)
- [Reading Incident Reports](#reading-incident-reports)
- [Common Workflows](#common-workflows)

---

## Running Modes

The assistant supports three modes of operation:

| Mode | Wazuh Required | API Required | Use Case |
|------|---------------|-------------|---------|
| `demo` | ❌ | ✅ | Testing, learning, portfolio demos |
| `live` | ✅ | ✅ | Real SOC integration |
| `batch` | ✅ | ✅ | Processing historical alerts |

---

## CLI Reference

```
usage: python main.py [OPTIONS]

Options:
  --mode {demo,live,batch,single}   Operation mode (default: demo)
  --limit INT                        Max alerts to process (default: 10)
  --min-level INT                    Minimum Wazuh alert level 1-15 (default: 7)
  --alert-id TEXT                    Specific alert ID (for --mode single)
  --output {markdown,pdf,both}       Report output format (default: both)
  --no-color                         Disable colored output
  --debug                            Enable debug logging
  --version                          Show version and exit
  --help                             Show this help message

Examples:
  python main.py --mode demo                          # Run demo with sample alerts
  python main.py --mode live --limit 5               # Triage 5 live alerts
  python main.py --mode batch --min-level 10         # Batch process critical alerts
  python main.py --mode single --alert-id abc123     # Triage one specific alert
  python main.py --mode live --output markdown       # Markdown reports only
```

---

## Demo Mode

Demo mode uses pre-loaded sample alerts from `tests/fixtures/sample_alerts.json`. No Wazuh connection is needed — perfect for testing the AI pipeline and learning.

```bash
# Activate virtual environment
source venv/bin/activate

# Run in demo mode
python main.py --mode demo
```

### Sample Alert Types in Demo Mode

The demo includes these representative Wazuh alerts:

| Alert | Rule ID | Level | Type |
|-------|---------|-------|------|
| SSH Brute Force | 5710 | 10 | Authentication attack |
| SQL Injection | 31103 | 9 | Web application attack |
| File Integrity Violation | 550 | 7 | FIM alert |
| Privilege Escalation | 5501 | 12 | sudo misuse |
| Port Scan | 40101 | 8 | Reconnaissance |

---

## Live Mode

Live mode connects to your Wazuh instance and processes real alerts.

```bash
# Basic live mode (triage latest alerts above level 7)
python main.py --mode live

# Triage only high-severity alerts (level 10+)
python main.py --mode live --min-level 10

# Limit to 3 alerts per run
python main.py --mode live --limit 3

# Generate only Markdown (no PDF)
python main.py --mode live --output markdown
```

---

## Understanding the Output

### Terminal Display

Each triaged alert produces a structured panel in the terminal:

```
╔══════════════════════════════════════════════════════════════════╗
║  🚨 ALERT TRIAGE RESULT                                          ║
║  Alert ID: 5710_web-server-01_20241201143022                     ║
║  Wazuh Rule: 5710 │ Level: 10/15 │ Agent: web-server-01         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📝 SUMMARY (Plain English)                                      ║
║  ─────────────────────────────────────────────────────────────  ║
║  Multiple failed SSH login attempts were detected originating    ║
║  from external IP 203.0.113.45, targeting the web-server-01     ║
║  agent. Over 47 failed attempts in a 5-minute window indicates  ║
║  an automated brute force tool. No successful login was         ║
║  detected, but the attack is ongoing.                           ║
║                                                                  ║
║  🗺️  MITRE ATT&CK                                                ║
║  ─────────────────────────────────────────────────────────────  ║
║  Tactic:        Credential Access (TA0006)                      ║
║  Technique:     Brute Force (T1110)                             ║
║  Sub-technique: Password Guessing (T1110.001)                   ║
║                                                                  ║
║  ⚠️  SEVERITY SCORE: 8/10  [HIGH]                                ║
║  ─────────────────────────────────────────────────────────────  ║
║  High volume (47 attempts/5 min) from external IP targeting     ║
║  a production web server. No successful auth detected, but      ║
║  persistence of attack warrants immediate response.             ║
║                                                                  ║
║  🔍 INVESTIGATION STEPS                                          ║
║  ─────────────────────────────────────────────────────────────  ║
║  1. Review /var/log/auth.log for full timeline of SSH attempts  ║
║     grep "Failed password" /var/log/auth.log | tail -100        ║
║  2. Check if any authentication succeeded after failures         ║
║     grep "Accepted password" /var/log/auth.log                  ║
║  3. Geolocate source IP 203.0.113.45                            ║
║     curl ipinfo.io/203.0.113.45                                 ║
║  4. Identify if other agents are being targeted by same IP      ║
║     (Check Wazuh dashboard for same source IP)                  ║
║  5. Review currently connected SSH sessions                      ║
║     who && last -n 20                                           ║
║                                                                  ║
║  🛠️  REMEDIATION STEPS                                           ║
║  ─────────────────────────────────────────────────────────────  ║
║  1. Block source IP immediately:                                 ║
║     sudo ufw deny from 203.0.113.45 to any port 22             ║
║  2. Install and enable fail2ban:                                 ║
║     sudo apt install fail2ban && sudo systemctl enable fail2ban ║
║  3. Disable SSH password authentication:                         ║
║     Edit /etc/ssh/sshd_config: PasswordAuthentication no        ║
║     sudo systemctl restart sshd                                 ║
║  4. Consider changing SSH port:                                  ║
║     Edit Port 22 → Port 2222 in /etc/ssh/sshd_config           ║
║  5. Enable SSH key-only authentication:                          ║
║     Generate: ssh-keygen -t ed25519 -C "admin"                 ║
║                                                                  ║
║  📄 Reports saved:                                               ║
║     📝 reports/alert_5710_web-server-01_20241201143022.md       ║
║     📋 reports/alert_5710_web-server-01_20241201143022.pdf      ║
╚══════════════════════════════════════════════════════════════════╝
```

### Severity Score Color Coding

| Score | Color | Label | Typical Response |
|-------|-------|-------|-----------------|
| 9–10 | 🔴 Bold Red | CRITICAL | Immediate human escalation |
| 7–8 | 🟠 Red | HIGH | Investigate within 1 hour |
| 4–6 | 🟡 Yellow | MEDIUM | Investigate within 24 hours |
| 1–3 | 🟢 Green | LOW | Review at end of shift |

---

## Reading Incident Reports

Each generated Markdown report follows this structure:

```markdown
# Incident Triage Report
**Report ID:** TRP-20241201-5710
**Generated:** 2024-12-01 14:30:22 UTC
**AI Model:** claude-sonnet-4-6

## Alert Details
| Field | Value |
|-------|-------|
| Rule ID | 5710 |
| Rule Level | 10/15 |
| Agent | web-server-01 (10.0.0.5) |
| Timestamp | 2024-12-01T14:30:22Z |
| Source IP | 203.0.113.45 |

## AI Analysis Summary
[Plain English summary here]

## MITRE ATT&CK Classification
- **Tactic:** Credential Access (TA0006)
- **Technique:** Brute Force (T1110)
- **Sub-technique:** Password Guessing (T1110.001)

## Severity Assessment
**Score: 8/10 — HIGH**

[Detailed justification]

## Investigation Steps
1. [Step with commands]
2. [Step with commands]
...

## Remediation Steps
1. [Step with commands]
...

## Raw Alert Data
[JSON of original Wazuh alert]

## Audit Trail
- Alert Received: 2024-12-01 14:30:22
- AI Analysis Started: 2024-12-01 14:30:23
- Analysis Complete: 2024-12-01 14:30:25
- Report Generated: 2024-12-01 14:30:25
- Model Used: claude-sonnet-4-6
- Tokens Used: 1,847
```

---

## Common Workflows

### Workflow 1: Morning Alert Review
```bash
# Check overnight alerts (level 8+), last 8 hours
python main.py --mode batch --min-level 8 --hours-back 8

# Review generated reports
ls -la reports/ | sort -k6,7
```

### Workflow 2: Critical Alert Deep Dive
```bash
# Triage only critical alerts (level 12+)
python main.py --mode live --min-level 12 --limit 5

# Get specific alert
python main.py --mode single --alert-id "1701438622_5710"
```

### Workflow 3: Portfolio Demo
```bash
# Demo mode — no Wazuh needed
python main.py --mode demo --limit 5

# Show all generated reports
cat reports/*.md
```

---

> **Previous:** [Configuration ←](04_configuration.md) | **Next:** [Testing →](06_testing.md)
