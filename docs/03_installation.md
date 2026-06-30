# 🚀 Installation Guide — AI Security Alert Triage Assistant

> **Document:** `docs/03_installation.md`
> **Audience:** Beginners — every step is explained with purpose and theory
> **Time Required:** ~30–60 minutes

---

## Table of Contents

- [Before You Begin](#before-you-begin)
- [Phase 1: System Preparation](#phase-1-system-preparation)
- [Phase 2: Python Environment Setup](#phase-2-python-environment-setup)
- [Phase 3: Project Installation](#phase-3-project-installation)
- [Phase 4: Wazuh API Setup](#phase-4-wazuh-api-setup)
- [Phase 5: AI API Setup](#phase-5-ai-api-setup)
- [Phase 6: Verification](#phase-6-verification)
- [Installation Checklist](#installation-checklist)

---

## Before You Begin

### What You Need

| Requirement | Why | Where to Get |
|-------------|-----|-------------|
| Linux system (Ubuntu/Pop!_OS recommended) | Best Python and security tooling support | — |
| Python 3.10+ | Required for modern type hints used in codebase | [python.org](https://python.org) |
| Git | To clone this repository | `sudo apt install git` |
| Wazuh Manager (v4.x) | Source of security alerts | [wazuh.com/install](https://documentation.wazuh.com/current/installation-guide/index.html) |
| Anthropic API Key | Powers the AI analysis engine | [console.anthropic.com](https://console.anthropic.com) |
| Internet connection | For Claude API calls | — |

> **💡 No Wazuh?** You can still run this project in **demo mode** using sample alerts stored in `tests/fixtures/sample_alerts.json`. Wazuh is only needed for live mode.

---

## Phase 1: System Preparation

### Step 1.1: Update System Packages

**Purpose:** Ensure your system has the latest security patches and package metadata.

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

**Expected Output:**
```
Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
...
0 upgraded, 0 newly installed, 0 to remove and 0 not changed.
```

---

### Step 1.2: Install System Dependencies

**Purpose:** Install required system libraries for PDF generation and SSL support.

```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libssl-dev \
    build-essential
```

**What each package does:**
- `python3, python3-pip, python3-venv` — Python runtime and package manager
- `git` — Version control
- `curl` — Command-line HTTP tool (for API testing)
- `libpango*` — Text rendering library required by WeasyPrint (PDF generation)
- `libffi-dev, libssl-dev` — SSL and foreign function interface libraries
- `build-essential` — Compiler tools needed for some Python packages

---

### Step 1.3: Verify Python Version

**Purpose:** Confirm Python 3.10+ is installed (required for this project).

```bash
python3 --version
```

**Expected Output:**
```
Python 3.10.12
```

> **If you see Python 3.8 or lower:** Install Python 3.10:
> ```bash
> sudo apt install python3.10 python3.10-venv python3.10-pip
> ```

---

## Phase 2: Python Environment Setup

### Step 2.1: Clone the Repository

**Purpose:** Download the project source code to your machine.

```bash
# Navigate to your projects directory
cd ~/projects  # or wherever you keep your projects
mkdir -p ~/projects && cd ~/projects

# Clone the repository
git clone https://github.com/kshitiz/ai-security-triage.git

# Enter the project directory
cd ai-security-triage
```

**Expected Output:**
```
Cloning into 'ai-security-triage'...
remote: Enumerating objects: 150, done.
remote: Counting objects: 100% (150/150), done.
Receiving objects: 100% (150/150), 45.23 KiB | 2.31 MiB/s, done.
```

---

### Step 2.2: Create a Virtual Environment

**Purpose:** Isolate project dependencies from your system Python installation.

**Theory:** A virtual environment creates a self-contained Python installation. This prevents dependency conflicts between projects. Think of it as a sandbox for your project's packages.

```bash
# Create the virtual environment
python3 -m venv venv

# Verify it was created
ls -la venv/
```

**Expected Output:**
```
total 24
drwxrwxr-x 5 user user 4096 Dec  1 14:30 .
drwxrwxr-x 8 user user 4096 Dec  1 14:30 ..
drwxrwxr-x 2 user user 4096 Dec  1 14:30 bin
drwxrwxr-x 2 user user 4096 Dec  1 14:30 include
drwxrwxr-x 3 user user 4096 Dec  1 14:30 lib
```

---

### Step 2.3: Activate the Virtual Environment

**Purpose:** Switch your terminal session to use the virtual environment's Python.

```bash
source venv/bin/activate
```

**How to know it worked:** Your terminal prompt will change:
```
# Before activation:
user@machine:~/projects/ai-security-triage$

# After activation:
(venv) user@machine:~/projects/ai-security-triage$
```

> **Important:** You must activate the virtual environment every time you open a new terminal to work on this project.

**To deactivate** (when done working):
```bash
deactivate
```

---

### Step 2.4: Upgrade pip

**Purpose:** Ensure you have the latest package installer to avoid compatibility issues.

```bash
pip install --upgrade pip
```

---

### Step 2.5: Install Python Dependencies

**Purpose:** Install all required Python libraries listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

**What's being installed (key packages):**
```
anthropic          - Claude AI API client
requests           - HTTP library for Wazuh API calls
rich               - Beautiful terminal output and formatting
python-dotenv      - Load configuration from .env file
pyyaml             - Parse YAML config files
jinja2             - HTML templating for reports
weasyprint         - Convert HTML to PDF
pandas             - Data processing and analysis
pytest             - Testing framework
```

**Expected Output:**
```
Successfully installed anthropic-0.25.0 requests-2.31.0 rich-13.7.0 ...
```

> **If WeasyPrint fails:** This is common — it has system dependencies:
> ```bash
> sudo apt-get install -y python3-cffi python3-brotli libpango-1.0-0
> pip install weasyprint
> ```

---

## Phase 3: Project Installation

### Step 3.1: Set Up Environment Variables

**Purpose:** Provide sensitive configuration (API keys, passwords) without hardcoding them.

**Theory:** Environment variables store configuration outside of code. This is a security best practice — your API keys never enter version control.

```bash
# Copy the example environment file
cp .env.example .env

# Open it for editing
nano .env
```

**You will see:**
```env
# ============================================================
# AI Security Alert Triage Assistant — Configuration
# ============================================================

ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_MODEL=claude-sonnet-4-6

WAZUH_HOST=https://your-wazuh-ip
WAZUH_PORT=55000
WAZUH_USER=wazuh-api-user
WAZUH_PASSWORD=your-password
WAZUH_VERIFY_SSL=false

POLL_INTERVAL=60
ALERT_LIMIT=10
MIN_ALERT_LEVEL=7
LOG_LEVEL=INFO

REPORT_OUTPUT_DIR=reports/
GENERATE_PDF=true
```

**Fill in:**
1. `ANTHROPIC_API_KEY` — Your Claude API key (see Phase 5)
2. `WAZUH_HOST` — Your Wazuh manager IP or hostname
3. `WAZUH_USER` and `WAZUH_PASSWORD` — Wazuh API credentials

**Save and exit nano:** `Ctrl+X → Y → Enter`

---

### Step 3.2: Verify .gitignore

**Purpose:** Make absolutely sure your `.env` file with API keys is never committed to Git.

```bash
cat .gitignore | grep ".env"
```

**Expected Output:**
```
.env
*.env
```

> **If `.env` is NOT in .gitignore:** Add it immediately:
> ```bash
> echo ".env" >> .gitignore
> ```

---

### Step 3.3: Create Required Directories

**Purpose:** Ensure output directories exist before running the application.

```bash
mkdir -p reports logs
```

---

## Phase 4: Wazuh API Setup

> **Skip this phase if using demo mode.**

### Step 4.1: Verify Wazuh is Running

On your Wazuh Manager host:

```bash
sudo systemctl status wazuh-manager
```

**Expected Output:**
```
● wazuh-manager.service - Wazuh manager
   Loaded: loaded (/lib/systemd/system/wazuh-manager.service)
   Active: active (running) since Thu 2024-12-01 10:00:00 UTC; 4h ago
```

### Step 4.2: Verify Wazuh API is Accessible

From your project machine:

```bash
# Replace YOUR_WAZUH_IP with your actual Wazuh manager IP
curl -k -u wazuh:wazuh https://YOUR_WAZUH_IP:55000/ 2>/dev/null | python3 -m json.tool
```

**Expected Output:**
```json
{
    "data": {
        "title": "Wazuh API",
        "api_version": "4.7.0",
        "revision": 40714,
        ...
    }
}
```

**If this fails:** Check firewall rules — port 55000 must be open:
```bash
# On Wazuh manager:
sudo ufw allow 55000/tcp
sudo systemctl restart wazuh-manager
```

### Step 4.3: Create a Read-Only API User (Best Practice)

On your Wazuh Manager, create a dedicated API user with minimal permissions:

```bash
# Access Wazuh API to create user
curl -k -u admin:admin -X POST \
  "https://localhost:55000/security/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "triage-reader", "password": "SecurePass123!"}'
```

---

## Phase 5: AI API Setup

### Step 5.1: Create an Anthropic Account

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up for an account
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Name it: `ai-security-triage-project`
6. Copy the key — **you will only see it once!**

### Step 5.2: Add Key to Environment

```bash
# Edit your .env file
nano .env

# Set the API key:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Step 5.3: Test the API Key

```bash
python3 -c "
import anthropic
import os
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
message = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=50,
    messages=[{'role': 'user', 'content': 'Say OK'}]
)
print('Claude API test:', message.content[0].text)
"
```

**Expected Output:**
```
Claude API test: OK
```

---

## Phase 6: Verification

### Step 6.1: Run the Full Test Suite

```bash
pytest tests/ -v
```

**Expected Output:**
```
tests/test_parser.py::test_normalize_ssh_alert PASSED
tests/test_parser.py::test_handle_missing_fields PASSED
tests/test_ai_engine.py::test_prompt_construction PASSED
tests/test_reporter.py::test_markdown_generation PASSED
...
======================== 12 passed in 3.45s ========================
```

### Step 6.2: Run Demo Mode

```bash
python main.py --mode demo
```

This runs the assistant with sample alerts from `tests/fixtures/sample_alerts.json` — no Wazuh or API calls required.

### Step 6.3: Run Connectivity Tests

```bash
python scripts/utils.py --test-all
```

**Expected Output:**
```
✅ Python version: 3.11.4 (OK)
✅ All dependencies installed
✅ .env file found and loaded
✅ Claude API: Connected (claude-sonnet-4-6)
✅ Wazuh API: Connected (v4.7.0) [SKIP if demo mode]
✅ Reports directory: exists
✅ Logs directory: exists

All checks passed! Run: python main.py --mode demo
```

---

## Installation Checklist

Use this checklist to confirm everything is set up correctly:

- [ ] System updated (`sudo apt-get update`)
- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] Repository cloned (`git clone ...`)
- [ ] Virtual environment created and activated (`source venv/bin/activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from template (`cp .env.example .env`)
- [ ] `.env` is in `.gitignore`
- [ ] Anthropic API key added to `.env`
- [ ] Wazuh credentials added to `.env` (or using demo mode)
- [ ] `reports/` and `logs/` directories exist
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Demo mode works (`python main.py --mode demo`)

---

> **Previous:** [Architecture ←](02_architecture.md) | **Next:** [Configuration →](04_configuration.md)
