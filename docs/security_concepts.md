# 🔐 Security Concepts — AI Security Alert Triage Assistant

> **Document:** `docs/security_concepts.md`
> **Purpose:** Deep explanations of every security concept involved in this project

---

## 1. CIA Triad

The **CIA Triad** is the foundational model of information security. Every security decision — including alert triage priority — relates back to these three properties:

```
         Confidentiality
              /\
             /  \
            /    \
           /      \
          /________\
   Integrity    Availability
```

### Confidentiality
**Definition:** Only authorized parties can access information.
**In this project:** SSH brute force attacks (Rule 5710) directly threaten confidentiality — if successful, the attacker gains unauthorized access to the system. This is why we score such alerts highly.

### Integrity
**Definition:** Information is accurate and has not been tampered with.
**In this project:** File Integrity Monitoring (FIM) alerts from Wazuh (Rule 550) detect when files are modified unexpectedly — a direct integrity violation. An attacker modifying `/etc/passwd` or a web shell being written to `/var/www/html/` are integrity violations.

### Availability
**Definition:** Systems and data are accessible when needed by authorized users.
**In this project:** A successful SSH brute force leading to ransomware deployment would destroy availability. Port scanning alerts can precede DDoS infrastructure reconnaissance.

### Using the CIA Triad for Triage Priority

```
Alert: SSH Brute Force from External IP targeting DB Server
├── Confidentiality: HIGH risk (unauthorized access attempt to production DB)
├── Integrity: MEDIUM risk (if successful, could modify database)
└── Availability: MEDIUM risk (if successful, could drop tables)
→ Severity: 9/10 — All three pillars threatened on critical asset
```

---

## 2. SIEM (Security Information and Event Management)

### What is a SIEM?

A SIEM is a centralized platform that:

1. **Collects** logs from diverse sources (servers, firewalls, endpoints, applications)
2. **Normalizes** different log formats into a common schema
3. **Correlates** events across sources to detect patterns
4. **Alerts** when correlation rules match suspicious patterns
5. **Stores** logs for forensic investigation and compliance

### SIEM Architecture

```
Log Sources                  SIEM                    Outputs
──────────              ──────────────            ──────────────
Linux servers ─────────► Log Collection ────────► Alerts
Windows hosts ─────────► Normalization  ────────► Dashboards
Firewalls     ─────────► Correlation    ────────► Reports
Web servers   ─────────► Rule Engine    ────────► Compliance
Cloud services ────────► Storage        ────────► Forensics
```

### Wazuh vs. Commercial SIEMs

| Feature | Wazuh (Open Source) | Splunk (Commercial) | Microsoft Sentinel |
|---------|--------------------|--------------------|-------------------|
| Cost | Free | High (licensed) | Usage-based |
| Scalability | Medium | Very High | Very High (cloud) |
| Rule library | 3000+ built-in | Extensive | Extensive |
| API | REST API | REST + SDK | REST API |
| Best for | Home lab, SME | Enterprise | Azure environments |

---

## 3. Alert Triage

### Why Triage Matters

```
Without Triage:
10,000 alerts → random processing → high-severity alerts buried
                                  → MTTR = 277 days

With Triage:
10,000 alerts → prioritized queue → critical alerts first
                                  → MTTR reduced significantly
```

### The Triage Decision Matrix

| Severity | Wazuh Level | Response Time | Action |
|----------|------------|--------------|--------|
| Critical (9-10) | 12-15 | Immediate (<15 min) | Escalate + contain |
| High (7-8) | 9-11 | <1 hour | Investigate now |
| Medium (4-6) | 6-8 | <24 hours | Schedule investigation |
| Low (1-3) | 1-5 | End of shift | Review when possible |

### Factors in Contextual Severity (Beyond Raw Alert Level)

Good triage considers these factors that raw log levels miss:

1. **Asset criticality** — Level-7 alert on payment server > Level-12 alert on test box
2. **Source IP type** — External IP > Internal IP (external = more suspicious)
3. **Attack frequency** — 1 failed login vs. 47 in 5 minutes (brute force vs. typo)
4. **Time of day** — 3 AM failed login from overseas is more suspicious than 9 AM internal
5. **Historical context** — Same source IP seen in previous alerts = higher score
6. **Attack chain potential** — Port scan followed by exploit attempt = escalating threat

This is exactly why the AI engine's contextual scoring outperforms pure rule-level assessment.

---

## 4. MITRE ATT&CK Framework

### What is MITRE ATT&CK?

MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge) is a globally-accessible knowledge base of adversary behaviors, built from real-world observations of attacks. It provides a common taxonomy for discussing how attackers operate.

### The Three Levels

```
Tactic (The WHY — what the adversary is trying to achieve)
    └── Technique (The HOW — the general method used)
            └── Sub-technique (The SPECIFIC VARIANT of the method)

Example:
TA0006 — Credential Access (Tactic: gain credentials)
    └── T1110 — Brute Force (Technique: guess passwords)
            └── T1110.001 — Password Guessing (Sub-technique: guess one user's password)
            └── T1110.003 — Password Spraying (Sub-technique: one password against many users)
            └── T1110.004 — Credential Stuffing (Sub-technique: use breach data)
```

### The 14 MITRE Tactics

| ID | Tactic | Description | Example |
|----|--------|-------------|---------|
| TA0043 | Reconnaissance | Gather info before attack | Port scanning |
| TA0042 | Resource Development | Build attack infrastructure | Creating malware |
| TA0001 | Initial Access | Get into the network | Phishing, exploits |
| TA0002 | Execution | Run malicious code | PowerShell scripts |
| TA0003 | Persistence | Maintain foothold | Cron jobs, backdoors |
| TA0004 | Privilege Escalation | Gain higher permissions | sudo exploitation |
| TA0005 | Defense Evasion | Avoid detection | Log deletion |
| TA0006 | Credential Access | Steal credentials | Brute force, keylogging |
| TA0007 | Discovery | Understand the environment | Network scanning |
| TA0008 | Lateral Movement | Move through network | RDP, SSH pivoting |
| TA0009 | Collection | Gather target data | File collection |
| TA0011 | Command & Control | Communicate with implants | C2 beaconing |
| TA0010 | Exfiltration | Steal data | Data transfer |
| TA0040 | Impact | Disrupt/destroy | Ransomware |

### Why MITRE ATT&CK Matters in This Project

Mapping every alert to MITRE ATT&CK:
1. **Standardizes communication** — Any security professional worldwide understands T1110
2. **Identifies attack phase** — Is this reconnaissance or active exploitation?
3. **Informs response** — Different tactics require different response playbooks
4. **Enables threat hunting** — If you see TA0001, look for TA0002 and TA0003 activity
5. **Tracks adversary behavior** — Build a profile of what techniques attackers use in your environment

---

## 5. Incident Response (IR) Lifecycle

This project automates the **Identification** phase of the IR lifecycle:

```
┌─────────────────────────────────────────────────────────────┐
│                   INCIDENT RESPONSE LIFECYCLE               │
│                                                             │
│  ┌──────────────┐                                           │
│  │ Preparation  │  Policies, playbooks, tools, training    │
│  └──────┬───────┘                                           │
│         │                                                   │
│  ┌──────▼───────┐                                           │
│  │Identification│ ◄── THIS PROJECT AUTOMATES THIS PHASE    │
│  │  (Triage)    │  Detect, classify, score, document       │
│  └──────┬───────┘                                           │
│         │                                                   │
│  ┌──────▼───────┐                                           │
│  │ Containment  │  Stop the spread (block IP, isolate host)│
│  └──────┬───────┘                                           │
│         │                                                   │
│  ┌──────▼───────┐                                           │
│  │ Eradication  │  Remove malware, close vulnerabilities   │
│  └──────┬───────┘                                           │
│         │                                                   │
│  ┌──────▼───────┐                                           │
│  │  Recovery    │  Restore systems to normal operation     │
│  └──────┬───────┘                                           │
│         │                                                   │
│  ┌──────▼───────┐                                           │
│  │Lessons Learned│ Document, improve, update playbooks     │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Defense in Depth

**Defense in Depth** means using multiple, layered security controls so that if one fails, others still protect the asset.

### Layers in This Project's Environment

```
Layer 1: Network Perimeter
  └── Firewall blocking unknown external traffic

Layer 2: System Hardening
  └── SSH key-only auth, minimal open ports

Layer 3: Monitoring & Detection
  └── Wazuh agents detecting suspicious activity

Layer 4: Alert Analysis
  └── This project — AI-assisted triage of Wazuh alerts

Layer 5: Incident Response
  └── Human analyst takes action on triaged alerts

Layer 6: Recovery
  └── Backups, restore procedures
```

---

## 7. Least Privilege

**Principle of Least Privilege:** Every user, process, and system should have only the minimum permissions necessary to perform its function.

### Applied in This Project

| Component | What Access Needed | What We Grant |
|-----------|------------------|--------------|
| Wazuh API user | Read security alerts | `events:read`, `agents:read` only |
| Claude API key | Send text messages | Standard API access |
| Application process | Read .env, write reports/ | No root, no system-wide access |
| Wazuh agent | Report logs | Agent permissions only |

### Why It Matters

If this project's API key is compromised:
- With full permissions: attacker could modify Wazuh rules, delete alerts, deploy agents
- With least privilege: attacker can only read alerts they could already see

---

## 8. Zero Trust

**Zero Trust** — "Never trust, always verify." Assume every request could be malicious.

### Applied in This Project

| Principle | Implementation |
|-----------|---------------|
| Verify identity | Wazuh JWT token authentication on every request |
| Least privilege | Read-only API credentials |
| Assume breach | Audit log every action, even internal ones |
| Validate input | Parse and validate every field from Wazuh API response |
| Validate AI output | Validate schema and value ranges of every Claude response |

---

## 9. Audit Trails & Logging

**Audit trails** are immutable, timestamped records of who did what, when.

### Why Audit Trails Matter in Security Tools

1. **Accountability** — Who triaged what alert, and what did they decide?
2. **Forensics** — If an incident escalates, what was the timeline?
3. **Compliance** — PCI-DSS, SOC2, ISO 27001 all require audit logs
4. **AI Transparency** — What did the AI recommend, and was it acted upon?

### This Project's Audit Log Format

```
2024-12-01 14:30:22,123 | INFO | poller    | ALERT_RECEIVED    | rule=5710 agent=web-01 level=10
2024-12-01 14:30:22,456 | INFO | parser    | PARSE_COMPLETE     | alert_id=5710_web-01_20241201
2024-12-01 14:30:22,789 | INFO | ai_engine | ANALYSIS_START     | alert_id=5710_web-01_20241201
2024-12-01 14:30:25,234 | INFO | ai_engine | ANALYSIS_COMPLETE  | score=8 technique=T1110.001
2024-12-01 14:30:25,567 | INFO | reporter  | REPORT_SAVED       | path=reports/alert_5710_...md
2024-12-01 14:30:26,890 | INFO | reporter  | PDF_SAVED          | path=reports/alert_5710_...pdf
```

---

## 10. AI in Security (Key Considerations)

### Strengths of AI in Alert Triage

| Strength | Why It Matters |
|----------|---------------|
| Speed | 4 seconds vs. 15-30 minutes per alert |
| Consistency | Same quality analysis at 3 AM as 3 PM |
| Scalability | Process 1000 alerts as easily as 10 |
| Knowledge depth | Trained on security literature, frameworks, CVEs |
| Documentation | Generates reports automatically |

### Limitations of AI in Alert Triage

| Limitation | Risk | Mitigation |
|-----------|------|-----------|
| No organizational context | Misses "this is our scanner, not an attacker" | Pass agent tags and context in prompt |
| Hallucination | Invents CVEs or techniques | Validate all AI claims |
| Prompt injection | Malicious log content manipulates AI | Only pass structured fields, not raw logs |
| Training data cutoff | Won't know about very recent techniques | Use for established techniques; human review for novel attacks |
| Over-confidence | AI sounds certain even when wrong | Always require human review of high-severity findings |

### The Golden Rule

> **AI triage accelerates the analyst's work — it does not replace the analyst's judgment.**

---

> This document covers the core security concepts applied in this project. For more depth on any topic, see `docs/09_references_security_lessons.md`.
