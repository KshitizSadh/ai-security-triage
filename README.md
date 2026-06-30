# 🛡️ AI Security Alert Triage Assistant

<div align="center">

![GitHub last commit](https://img.shields.io/github/last-commit/kshitiz/ai-security-triage?style=for-the-badge&color=blue)
![GitHub repo size](https://img.shields.io/github/repo-size/kshitiz/ai-security-triage?style=for-the-badge&color=green)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Wazuh](https://img.shields.io/badge/Wazuh-4.x-00C3E3?style=for-the-badge&logo=security&logoColor=white)
![MITRE ATT&CK](https://img.shields.io/badge/MITRE-ATT%26CK-red?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![SOC](https://img.shields.io/badge/Type-SOC%20%7C%20SIEM%20%7C%20AI-blueviolet?style=for-the-badge)

**An AI-powered Security Alert Triage Assistant that integrates with Wazuh SIEM to automate the initial analysis of security alerts — reducing analyst workload, improving consistency, and accelerating incident response.**

[📖 Documentation](#documentation) • [🚀 Quick Start](#quick-start) • [🏗️ Architecture](#architecture) • [📊 Features](#features) • [🤝 Contributing](#contributing)

</div>

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Objectives](#objectives)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Step-by-Step Setup](#step-by-step-setup)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Verification Steps](#verification-steps)
- [Troubleshooting](#troubleshooting)
- [Security Concepts Learned](#security-concepts-learned)
- [Skills Demonstrated](#skills-demonstrated)
- [Lessons Learned](#lessons-learned)
- [Future Improvements](#future-improvements)
- [References](#references)
- [Author](#author)

---

## 🔍 Project Overview

The **AI Security Alert Triage Assistant** is a Python-based tool that bridges the gap between raw SIEM alerts and actionable security intelligence. It connects to a **Wazuh** SIEM deployment, retrieves security alerts via the REST API, and passes them through an **AI pipeline** (using Claude/OpenAI) to produce:

- **Plain-English explanations** of technical alerts
- **MITRE ATT&CK framework** mappings (Tactic + Technique + Sub-technique)
- **Contextual severity scores** (1–10 scale with justification)
- **Investigation checklists** tailored to each alert type
- **Remediation recommendations** with specific commands
- **Automated incident reports** in Markdown and PDF format

> **Who is this for?** SOC analysts, cybersecurity students, security engineers, and anyone building automated detection workflows. This project demonstrates how AI augments — not replaces — human security analysts.

---

## 🎯 Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Connect to Wazuh REST API and retrieve live alerts | ✅ Complete |
| 2 | Parse and normalize alert fields (rule ID, description, agent, level) | ✅ Complete |
| 3 | Generate plain-English alert summaries using AI | ✅ Complete |
| 4 | Map alerts to MITRE ATT&CK Tactics and Techniques | ✅ Complete |
| 5 | Assign contextual severity scores (1–10) | ✅ Complete |
| 6 | Generate investigation and remediation checklists | ✅ Complete |
| 7 | Produce automated incident reports (Markdown + PDF) | ✅ Complete |
| 8 | Build a CLI interface for analyst interaction | ✅ Complete |
| 9 | Log all triage decisions for audit trails | ✅ Complete |
| 10 | Demonstrate SOC workflow automation with AI | ✅ Complete |

---

## ✨ Features

```
┌─────────────────────────────────────────────────────────────┐
│               AI SECURITY ALERT TRIAGE ASSISTANT            │
├────────────────────────┬────────────────────────────────────┤
│  📡 WAZUH INTEGRATION  │  🤖 AI ANALYSIS ENGINE             │
│  • REST API polling    │  • Plain-English summaries         │
│  • Alert normalization │  • MITRE ATT&CK mapping            │
│  • Field extraction    │  • Severity scoring (1-10)         │
├────────────────────────┼────────────────────────────────────┤
│  🔍 INVESTIGATION      │  📄 REPORTING                      │
│  • Step-by-step guide  │  • Markdown incident reports       │
│  • IOC extraction      │  • PDF export                      │
│  • Timeline building   │  • Audit trail logging             │
├────────────────────────┼────────────────────────────────────┤
│  🛠️  REMEDIATION        │  🖥️  INTERFACE                     │
│  • Actionable steps    │  • CLI interactive mode            │
│  • Commands provided   │  • Batch processing mode           │
│  • Priority ranking    │  • Config file support             │
└────────────────────────┴────────────────────────────────────┘
```

---

## 🛠️ Technologies Used

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **SIEM** | Wazuh | 4.x | Security alert source and rule engine |
| **AI/LLM** | Anthropic Claude API | claude-sonnet-4-6 | Alert analysis and natural language generation |
| **Language** | Python | 3.10+ | Core application logic |
| **HTTP Client** | Requests | 2.31+ | Wazuh REST API communication |
| **CLI** | Rich | 13.x | Beautiful terminal output |
| **Config** | python-dotenv | 1.0+ | Environment variable management |
| **Reporting** | Jinja2 | 3.x | Report templating |
| **PDF** | WeasyPrint | 60.x | PDF generation from HTML |
| **Data** | Pandas | 2.x | Alert data processing |
| **Logging** | Python logging | stdlib | Audit trail generation |
| **Testing** | pytest | 7.x | Unit and integration tests |

---

## 🏗️ Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph SIEM["🔒 Wazuh SIEM Environment"]
        WM[Wazuh Manager] --> WA[Wazuh Agents]
        WA --> |"Security Events"| WM
        WM --> API[Wazuh REST API<br/>:55000]
    end

    subgraph APP["🤖 AI Triage Assistant"]
        direction TB
        POLL[Alert Poller<br/>scripts/poller.py] --> PARSE[Alert Parser<br/>scripts/parser.py]
        PARSE --> ENRICH[Context Enricher<br/>scripts/enricher.py]
        ENRICH --> AI[AI Analysis Engine<br/>scripts/ai_engine.py]
        AI --> REPORT[Report Generator<br/>scripts/reporter.py]
        AI --> LOG[Audit Logger<br/>logs/triage.log]
    end

    subgraph AI_SVC["☁️ AI Service"]
        CLAUDE[LLM API<br/>ANY MODEL]
    end

    subgraph OUTPUT["📊 Outputs"]
        MD[Markdown Reports<br/>reports/*.md]
        PDF[PDF Reports<br/>reports/*.pdf]
        CONSOLE[Rich CLI Output<br/>Terminal]
    end

    API --> |"JSON Alerts"| POLL
    AI --> |"Analysis Request"| CLAUDE
    CLAUDE --> |"Structured Response"| AI
    REPORT --> MD
    REPORT --> PDF
    REPORT --> CONSOLE
```

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant W as Wazuh API
    participant P as Alert Poller
    participant AI as AI Engine
    participant C as Claude API
    participant R as Report Generator
    participant A as Analyst

    P->>W: GET /security/events (every 60s)
    W-->>P: JSON Alert Array
    P->>P: Parse & Normalize Fields
    P->>AI: Enriched Alert Object
    AI->>C: Structured Triage Prompt
    C-->>AI: Analysis JSON Response
    AI->>AI: Validate & Score Response
    AI->>R: Alert + Analysis Object
    R->>A: Rich CLI Output
    R->>R: Write Markdown Report
    R->>R: Generate PDF
    Note over A,R: Analyst reviews and takes action
```

---

## 📁 Folder Structure

```
ai-security-triage/
│
├── 📄 README.md                    # This file — project overview
├── 📄 LICENSE                      # MIT License
├── 📄 .env.example                 # Environment variable template
├── 📄 requirements.txt             # Python dependencies
├── 📄 main.py                      # Application entry point
│
├── 📂 scripts/                     # Core application scripts
│   ├── poller.py                   # Wazuh API polling and alert retrieval
│   ├── parser.py                   # Alert field parsing and normalization
│   ├── enricher.py                 # Context enrichment (GeoIP, threat intel)
│   ├── ai_engine.py                # AI prompt engineering and API calls
│   ├── reporter.py                 # Report generation (Markdown + PDF)
│   └── utils.py                    # Shared utility functions
│
├── 📂 configs/                     # Configuration files
│   ├── config.yaml                 # Main application configuration
│   ├── mitre_mapping.json          # MITRE ATT&CK technique reference
│   ├── severity_rules.json         # Severity scoring configuration
│   └── report_template.html        # HTML template for PDF reports
│
├── 📂 docs/                        # Project documentation
│   ├── 01_introduction.md          # Project introduction
│   ├── 02_architecture.md          # Detailed architecture guide
│   ├── 03_installation.md          # Step-by-step installation
│   ├── 04_configuration.md         # Configuration reference
│   ├── 05_usage.md                 # Usage guide with examples
│   ├── 06_testing.md               # Testing procedures
│   ├── 07_troubleshooting.md       # Common issues and fixes
│   ├── 08_faq.md                   # Frequently asked questions
│   ├── 09_references.md            # External references
│   ├── 10_security_notes.md        # Security considerations
│   └── 11_lessons_learned.md       # Lessons learned
│
├── 📂 reports/                     # Generated incident reports
│   ├── sample_report.md            # Sample triage report
│   └── .gitkeep
│
├── 📂 screenshots/                 # Project screenshots
│   ├── 01_wazuh_dashboard.png      # Wazuh alert dashboard
│   ├── 02_cli_output.png           # CLI triage output
│   ├── 03_ai_analysis.png          # AI analysis panel
│   ├── 04_incident_report.png      # Generated report preview
│   └── README.md                   # Screenshot descriptions
│
├── 📂 diagrams/                    # Architecture diagrams
│   ├── system_architecture.png     # High-level architecture
│   ├── data_flow.png               # Data flow diagram
│   └── mitre_mapping.png           # MITRE ATT&CK heatmap
│
├── 📂 logs/                        # Application and audit logs
│   ├── triage.log                  # Triage decision audit log
│   └── .gitkeep
│
├── 📂 references/                  # Research and reference materials
│   ├── wazuh_rules_reference.md    # Wazuh rule ID reference
│   ├── mitre_attack_summary.md     # MITRE ATT&CK quick reference
│   └── ai_prompt_templates.md      # Prompt engineering templates
│
└── 📂 tests/                       # Test suite
    ├── test_parser.py              # Alert parser unit tests
    ├── test_ai_engine.py           # AI engine integration tests
    ├── test_reporter.py            # Report generator tests
    └── fixtures/                   # Test alert fixtures
        └── sample_alerts.json      # Sample Wazuh alert data
```

---

## ✅ Prerequisites

Before starting, ensure you have the following:

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Ubuntu 20.04 / Pop!_OS 22.04 | Ubuntu 22.04 LTS |
| RAM | 4 GB | 8 GB |
| CPU | 2 cores | 4 cores |
| Storage | 20 GB | 50 GB |
| Python | 3.10 | 3.11+ |

### Required Services

- [ ] **Wazuh Manager** running (v4.x) with REST API enabled on port 55000
- [ ] **Wazuh API credentials** (username and password)
- [ ] **Anthropic API key** (Claude API access) — [Get one here](https://console.anthropic.com)
- [ ] **Python 3.10+** installed
- [ ] **pip** package manager
- [ ] **Git** for cloning the repository

> **💡 Tip:** If you don't have a live Wazuh instance, you can use the sample alert fixtures in `tests/fixtures/sample_alerts.json` to run the assistant in demo mode.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/kshitiz/ai-security-triage.git
cd ai-security-triage

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env                          # Add your API keys

# 5. Run the assistant
python main.py --mode demo         # Demo mode (no Wazuh required)
python main.py --mode live         # Live mode (requires Wazuh)
```

---

## ⚙️ Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/kshitiz/ai-security-triage.git
cd ai-security-triage
```

### Step 2: Create a Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
# Verify activation — you should see (venv) in your prompt
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import anthropic, requests, rich; print('All dependencies installed successfully ✅')"
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# ============================================================
# AI Security Alert Triage Assistant — Configuration
# ============================================================

# --- Anthropic Claude API ---
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_MODEL=claude-sonnet-4-6
AI_MAX_TOKENS=2048

# --- Wazuh API ---
WAZUH_HOST=https://your-wazuh-manager-ip
WAZUH_PORT=55000
WAZUH_USER=wazuh-api-user
WAZUH_PASSWORD=your-secure-password
WAZUH_VERIFY_SSL=false          # Set true in production

# --- Application Settings ---
POLL_INTERVAL=60                # Seconds between alert polls
ALERT_LIMIT=10                  # Max alerts per poll cycle
MIN_ALERT_LEVEL=7               # Minimum Wazuh rule level to process
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR

# --- Report Settings ---
REPORT_OUTPUT_DIR=reports/
GENERATE_PDF=true
```

### Application Config (`configs/config.yaml`)

```yaml
application:
  name: "AI Security Alert Triage Assistant"
  version: "1.0.0"
  author: "Kshitiz"

wazuh:
  api_timeout: 30
  alert_fields:
    - id
    - rule.id
    - rule.level
    - rule.description
    - rule.groups
    - agent.name
    - agent.ip
    - data.srcip
    - data.dstip
    - timestamp

ai_analysis:
  temperature: 0.1              # Low temp for consistent, factual responses
  include_mitre: true
  include_remediation: true
  severity_scale: 10            # Score out of 10

reporting:
  formats:
    - markdown
    - pdf
  include_raw_alert: true
  include_audit_trail: true
```

---

## 📋 Step-by-Step Setup

### Phase 1: Environment Setup

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.10+ if not present
sudo apt-get install python3 python3-pip python3-venv -y

# Verify Python version
python3 --version  # Should show 3.10.x or higher
```

### Phase 2: Wazuh API Verification

```bash
# Test Wazuh API connectivity (replace with your Wazuh IP)
curl -k -u wazuh-user:password https://YOUR_WAZUH_IP:55000/

# Expected response:
# {"data":{"title":"Wazuh API","api_version":"4.x.x","revision":...}}
```

### Phase 3: Application Setup

```bash
# Clone and set up
git clone https://github.com/kshitiz/ai-security-triage.git
cd ai-security-triage
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Phase 4: Run the Assistant

```bash
# Demo mode (uses sample alerts from fixtures)
python main.py --mode demo

# Live mode (connects to Wazuh)
python main.py --mode live

# Process a specific alert by ID
python main.py --mode single --alert-id "1234567890"

# Batch process recent alerts
python main.py --mode batch --limit 20 --min-level 7
```

---

## 🖥️ Usage

### Interactive CLI Mode

```
╔══════════════════════════════════════════════════════════════╗
║         🛡️  AI Security Alert Triage Assistant v1.0.0        ║
║              Connected to Wazuh │ Claude AI Active           ║
╠══════════════════════════════════════════════════════════════╣
║  [1] Fetch and Triage Latest Alerts                          ║
║  [2] Triage Single Alert by ID                               ║
║  [3] Batch Process Alerts (Last 24h)                         ║
║  [4] Generate Summary Report                                  ║
║  [5] View Triage History                                      ║
║  [6] Settings                                                 ║
║  [Q] Quit                                                     ║
╚══════════════════════════════════════════════════════════════╝

Enter choice: 1

🔍 Fetching alerts from Wazuh... Found 3 alerts above threshold.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ALERT #1  │  Rule 5710  │  Level 10  │  SSH Brute Force
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 AI SUMMARY
Multiple failed SSH login attempts detected from IP 192.168.1.105
targeting agent 'web-server-01'. This pattern is consistent with
an automated brute force attack attempting to guess credentials.

🗺️  MITRE ATT&CK MAPPING
  Tactic    : Credential Access (TA0006)
  Technique : Brute Force (T1110)
  Sub-tech  : Password Guessing (T1110.001)

⚠️  SEVERITY SCORE: 8/10
  Justification: High volume of attempts (47 in 5 minutes),
  external source IP, targeting production server.

🔍 INVESTIGATION STEPS
  1. Check /var/log/auth.log for full timeline of attempts
  2. Identify if any login succeeded after the failures
  3. Geolocate source IP 192.168.1.105
  4. Check if other hosts are targeted by same IP
  5. Review firewall rules for SSH access restrictions

🛠️  REMEDIATION
  1. Block source IP immediately:
     sudo ufw deny from 192.168.1.105 to any port 22
  2. Enable fail2ban for SSH:
     sudo apt install fail2ban && sudo systemctl enable fail2ban
  3. Disable password authentication, enforce SSH keys:
     Edit /etc/ssh/sshd_config → PasswordAuthentication no
  4. Consider changing SSH port from default 22

📄 Report saved: reports/alert_5710_20241201_143022.md
```

---

## 📸 Screenshots

> **Note:** Screenshots will be added upon deployment. The `screenshots/` directory contains placeholder descriptions.

| Screenshot | Description |
|------------|-------------|
| `01_wazuh_dashboard.png` | Wazuh security alerts dashboard showing active alerts |
| `02_cli_output.png` | AI triage assistant CLI output with rich formatting |
| `03_ai_analysis.png` | Detailed AI analysis panel with MITRE mapping |
| `04_incident_report.png` | Generated Markdown incident report preview |
| `05_pdf_report.png` | PDF incident report opened in browser |

---

## ✔️ Verification Steps

Run these checks to verify the setup is working correctly:

```bash
# 1. Verify Python and dependencies
python -c "import anthropic; print('Claude API library:', anthropic.__version__)"
python -c "import requests; print('Requests library:', requests.__version__)"

# 2. Test Wazuh API connection
python scripts/utils.py --test-wazuh

# 3. Test Claude API connection
python scripts/utils.py --test-ai

# 4. Run unit tests
pytest tests/ -v

# 5. Run demo mode
python main.py --mode demo --limit 1

# Expected output:
# ✅ Wazuh API: Connected (v4.x.x)
# ✅ Claude API: Connected (claude-sonnet-4-6)
# ✅ All systems operational
```

---

## 🔧 Troubleshooting

| Issue | Likely Cause | Solution |
|-------|-------------|---------|
| `ConnectionError: Wazuh API unreachable` | Wrong IP or port | Verify WAZUH_HOST and WAZUH_PORT in `.env` |
| `SSL Certificate Error` | Self-signed cert | Set `WAZUH_VERIFY_SSL=false` in `.env` |
| `AuthenticationError: 401` | Wrong credentials | Verify WAZUH_USER and WAZUH_PASSWORD |
| `anthropic.AuthenticationError` | Invalid API key | Check ANTHROPIC_API_KEY in `.env` |
| `RateLimitError` | Too many API calls | Increase POLL_INTERVAL in `.env` |
| `No alerts returned` | Level threshold too high | Lower MIN_ALERT_LEVEL in `.env` |
| `PDF generation failed` | WeasyPrint not installed | `pip install weasyprint` |

See [docs/07_troubleshooting.md](docs/07_troubleshooting.md) for detailed troubleshooting.

---

## 📚 Security Concepts Learned

| Concept | Application in This Project |
|---------|---------------------------|
| **SIEM** | Wazuh collects and correlates security events across agents |
| **Alert Triage** | Prioritizing alerts by severity to reduce analyst fatigue |
| **MITRE ATT&CK** | Mapping raw alerts to standardized adversary tactics/techniques |
| **Incident Response** | Structured process from detection → analysis → remediation |
| **Threat Intelligence** | Enriching alerts with context (IP reputation, GeoIP) |
| **Defense in Depth** | Multiple detection layers: agent → manager → AI analysis |
| **Least Privilege** | API credentials scoped to read-only Wazuh access |
| **Audit Trails** | All triage decisions logged with timestamps |
| **AI in Security** | LLMs as force multipliers for analyst workflows |
| **SOC Automation** | Reducing MTTR (Mean Time to Respond) through automation |

---

## 💼 Skills Demonstrated

```
┌─────────────────────────────────────────────────────────────┐
│                    SKILLS DEMONSTRATED                      │
├─────────────────────────────────────────────────────────────┤
│  🔵 Security          │  🟢 Development                     │
│  • SIEM (Wazuh)       │  • Python scripting                 │
│  • Alert analysis     │  • REST API integration             │
│  • MITRE ATT&CK       │  • Prompt engineering               │
│  • Incident response  │  • CLI development (Rich)           │
│  • SOC workflows      │  • Configuration management         │
├─────────────────────────────────────────────────────────────┤
│  🟡 AI/ML             │  🔴 Documentation                   │
│  • LLM API usage      │  • Technical writing                │
│  • Prompt design      │  • GitHub documentation             │
│  • AI for security    │  • Markdown proficiency             │
│  • Structured outputs │  • Mermaid diagrams                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔮 Future Improvements

- [ ] **Web Dashboard** — React-based frontend for alert visualization
- [ ] **Multi-SIEM Support** — Add Splunk, Elastic SIEM, Microsoft Sentinel connectors
- [ ] **Threat Intelligence Integration** — VirusTotal, AbuseIPDB, MISP API enrichment
- [ ] **Slack/Teams Notifications** — Real-time alert notifications to collaboration tools
- [ ] **Automated Playbook Execution** — Trigger SOAR-like responses based on alert type
- [ ] **ML Severity Scoring** — Train a model on historical triage decisions
- [ ] **Multi-Agent Support** — Parallel processing of alerts from multiple Wazuh agents
- [ ] **False Positive Tuning** — Track analyst feedback to reduce noise over time
- [ ] **Docker Deployment** — Containerize for easy deployment in any environment

---

## 📖 References

- [Wazuh Documentation](https://documentation.wazuh.com/)
- [Wazuh REST API Reference](https://documentation.wazuh.com/current/user-manual/api/index.html)
- [Anthropic Claude API Documentation](https://docs.anthropic.com/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [SANS SOC Analyst Handbook](https://www.sans.org/reading-room/)
- [Python Rich Library](https://rich.readthedocs.io/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## 👤 Author

<div align="center">

**Kshitiz**
*Final-year B.Sc. (Hons) Computer Science | Ramanujan College, University of Delhi*
*Cybersecurity Enthusiast | CRTA Certified | Top 3% TryHackMe*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/kshitiz)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/kshitiz)
[![TryHackMe](https://img.shields.io/badge/TryHackMe-Top_3%25-1db954?style=for-the-badge)](https://tryhackme.com/p/kshitiz)

*"Security is not a product, but a process." — Bruce Schneier*

</div>

---

<div align="center">

⭐ **If this project helped you learn, please star it!** ⭐

*Built with 🛡️ and ☕ as part of a personal cybersecurity portfolio*

</div>
