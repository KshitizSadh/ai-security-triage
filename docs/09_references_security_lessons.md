# 📚 References — AI Security Alert Triage Assistant

> **Document:** `docs/09_references.md`

---

## Official Documentation

| Resource | URL | Purpose |
|----------|-----|---------|
| Wazuh Documentation | https://documentation.wazuh.com | Complete Wazuh reference |
| Wazuh REST API | https://documentation.wazuh.com/current/user-manual/api/index.html | API endpoints used in this project |
| Anthropic Claude API | https://docs.anthropic.com | Claude API reference and pricing |
| MITRE ATT&CK | https://attack.mitre.org | Threat framework used for mapping |
| Python Rich | https://rich.readthedocs.io | CLI formatting library |

## Security Standards & Frameworks

| Framework | URL | Application |
|-----------|-----|------------|
| NIST CSF | https://www.nist.gov/cyberframework | Overall security framework |
| NIST SP 800-61 | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf | Incident Response guidance |
| MITRE ATT&CK Navigator | https://mitre-attack.github.io/attack-navigator | ATT&CK visualization tool |
| CIS Controls | https://www.cisecurity.org/controls | Security best practices |

## Learning Resources

| Resource | Topic |
|----------|-------|
| TryHackMe SOC Level 1 Path | SOC fundamentals, Wazuh, alert triage |
| SANS SOC Analyst Handbook | Professional SOC workflows |
| Anthropic Prompt Engineering Guide | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview |
| Wazuh Training | https://wazuh.com/services/training |
| Blue Team Labs Online | Hands-on incident response practice |

## Research Papers (Relevant)

- Sommer & Paxson (2010). "Outside the Closed World: On Using Machine Learning for Network Intrusion Detection." IEEE S&P.
- Apruzzese et al. (2022). "The Role of Machine Learning in Cybersecurity." Digital Threats: Research and Practice.
- Stojanović et al. (2020). "Towards Optimal Detection of MITRE ATT&CK Techniques." Applied Sciences.

---

# 🔒 Security Notes — AI Security Alert Triage Assistant

> **Document:** `docs/10_security_notes.md`

---

## Data Privacy

### What Data is Sent to Claude API?

The following Wazuh alert fields are included in prompts sent to Anthropic:
- Rule ID, level, description, and groups
- Agent name and internal IP address
- Source IP address (attacker IP)
- Timestamp

**What is NOT sent:**
- Full raw log entries (configurable — off by default)
- User credentials or passwords
- File contents from FIM alerts
- Configuration details

### Handling Sensitive Environments

For environments where sending alert data to an external API is prohibited:

**Option 1: Self-Hosted LLM (Recommended)**
```python
# Modify ai_engine.py to use Ollama (local LLM)
import requests

def analyze_with_ollama(alert_data):
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3",
        "prompt": build_prompt(alert_data),
        "stream": False
    })
    return response.json()["response"]
```

**Option 2: Data Minimization**
Configure the system to send only rule IDs (not descriptions) and anonymized IPs.

---

## Credential Security

### API Key Protection

```bash
# ✅ CORRECT: Keys in .env file
echo "ANTHROPIC_API_KEY=sk-ant-xxx" >> .env
echo ".env" >> .gitignore

# ❌ WRONG: Keys in code
api_key = "sk-ant-xxx"  # Never do this

# ✅ Verify .env is gitignored
git check-ignore -v .env  # Should output: .gitignore:.env
```

### Pre-commit Hook (Prevent Accidental Key Commits)

```bash
# Install git-secrets to prevent accidental key commits
brew install git-secrets  # macOS
# or: pip install detect-secrets

# Configure to scan for API key patterns
git secrets --add 'sk-ant-[a-zA-Z0-9-_]+'
git secrets --install
```

---

## Network Security

### Wazuh API Access Control

```bash
# Firewall rule: Only allow the triage assistant's IP to reach Wazuh API
# On Wazuh Manager:
sudo ufw allow from TRIAGE_ASSISTANT_IP to any port 55000
sudo ufw deny 55000  # Block all other access
```

### SSL in Production

```python
# NEVER use verify=False in production
# Always provide proper certificates:
requests.get(url, verify="/path/to/wazuh-ca.pem")

# Or set as environment variable:
os.environ["REQUESTS_CA_BUNDLE"] = "/path/to/ca-bundle.crt"
```

---

## Least Privilege

The Wazuh API user for this project should have **read-only permissions** only:

```bash
# Minimum required permissions:
# - security:events:read    (fetch alerts)
# - security:agents:read    (agent information)
# - security:rules:read     (rule details)

# Does NOT need:
# - agents:write            (deploy agents)
# - rules:write             (modify rules)
# - manager:write           (configure manager)
```

---

# 📝 Lessons Learned — AI Security Alert Triage Assistant

> **Document:** `docs/11_lessons_learned.md`

---

## Technical Lessons

### 1. Prompt Engineering is Critical

**Challenge:** Early versions produced inconsistent JSON output or included preamble text before the JSON.

**Solution:** The prompt must explicitly state "Return ONLY valid JSON with no other text" AND provide a schema. Adding a few-shot example in the system prompt improved consistency from ~70% to ~98%.

**Takeaway:** For LLM-powered security tools, the quality of the prompt determines the quality of the output. Invest time in prompt design, testing, and iteration.

---

### 2. Validation is Non-Negotiable

**Challenge:** When the AI occasionally returned a severity score of 11/10 or omitted a required field, the entire pipeline crashed.

**Solution:** Added a dedicated response validation layer that checks every required field exists, types are correct, and values are in expected ranges. Added retry logic (3 attempts) for invalid responses.

**Takeaway:** Never trust AI output without validation. Treat LLM responses as untrusted external input, the same as user input in a web application.

---

### 3. Wazuh JWT Tokens Expire

**Challenge:** Long-running batch jobs would fail after 15 minutes because the Wazuh JWT token (valid for 900 seconds) expired mid-run.

**Solution:** Implemented token refresh logic in the poller — the token is refreshed every 800 seconds proactively.

**Takeaway:** When working with time-limited API tokens, always implement proactive refresh logic rather than reactive error handling.

---

### 4. Alert Volume vs. Quality

**Challenge:** Setting `MIN_ALERT_LEVEL=3` during early testing flooded the system with thousands of low-level alerts (like informational DNS queries), consuming API quota rapidly.

**Solution:** Set minimum level to 7 (moderate) for development and 10 (high) for production. Added configurable thresholds.

**Takeaway:** In security automation, more alerts ≠ more security. Effective triage requires good filtering upstream before AI analysis.

---

### 5. Structure Documentation Early

**Challenge:** Early in the project, scripts had no docstrings, `.env` variables were undocumented, and there was no README. When returning to the project after a week, it took an hour to remember how to run it.

**Solution:** Adopted documentation-first development — write the README before writing code. Every function has a docstring. The `.env.example` is always synchronized with `.env`.

**Takeaway:** Good documentation is a security practice too. Undocumented security tools become shelfware. Your future self (and employers reviewing your GitHub) will thank you.

---

## Security Concept Lessons

### 6. MITRE ATT&CK is a Language, Not a Checklist

Initially approached MITRE ATT&CK as a checklist to "cover all techniques." The real insight: it's a **shared vocabulary** for describing attacker behavior. A single alert maps to one tactic/technique — the goal is precise classification, not broad coverage.

### 7. Alert Level vs. Severity Score

Wazuh's rule level (1–15) is a technical score about rule confidence/prevalence. The AI's contextual severity score (1–10) considers: is the target critical? Is the source external? Is it part of a chain of events? A level-7 alert on a payment server is far more critical than a level-10 alert on a test VM. Context is everything.

### 8. SOC Automation Augments, Not Replaces

The most important lesson: AI triage handles the **mechanical** parts of analysis (explanation, classification, basic recommendations) but **cannot** replace the analyst's:
- Knowledge of the specific organization's environment
- Understanding of business context
- Pattern recognition across multiple incidents
- Judgment calls in novel situations

AI tools are **force multipliers**, not analyst replacements.

---

## What I Would Do Differently

1. **Start with fixtures** — Build and test against sample alerts before touching the live Wazuh API
2. **Validate the schema first** — Define the expected JSON response schema before writing prompts
3. **Add cost tracking early** — Log token usage per alert from day one
4. **Write tests alongside code** — Not after

---

> **Previous:** [References ←](09_references.md)
