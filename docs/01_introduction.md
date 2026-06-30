# 📖 Introduction — AI Security Alert Triage Assistant

> **Document:** `docs/01_introduction.md`
> **Audience:** Beginners, students, SOC analysts, recruiters
> **Purpose:** Understand what this project is, why it was built, and what problem it solves

---

## Table of Contents

- [What is This Project?](#what-is-this-project)
- [The Problem: Alert Fatigue in SOCs](#the-problem-alert-fatigue-in-socs)
- [The Solution: AI-Assisted Triage](#the-solution-ai-assisted-triage)
- [Key Concepts Explained](#key-concepts-explained)
- [Project Scope](#project-scope)
- [Who Should Use This?](#who-should-use-this)
- [What You Will Learn](#what-you-will-learn)

---

## What is This Project?

The **AI Security Alert Triage Assistant** is an automation tool that sits between your SIEM (Security Information and Event Management) system and your security analyst. It acts as a "first responder" for security alerts — taking raw, technical, and often confusing alert data from Wazuh and transforming it into clear, actionable intelligence using the power of large language models (LLMs).

### In Simple Terms

Imagine a hospital emergency room. When patients arrive, a **triage nurse** quickly assesses each patient — How serious is this? What's the priority? What should the doctor focus on first? — before a doctor takes over.

This project is the **triage nurse** for a Security Operations Center (SOC). Instead of humans reading every raw log line and alert, the AI:

1. **Reads** the raw Wazuh alert
2. **Understands** what happened (translates jargon to plain English)
3. **Classifies** the threat (maps to MITRE ATT&CK)
4. **Scores** the severity (1–10 with justification)
5. **Recommends** what the analyst should investigate and do
6. **Documents** everything in a professional incident report

The human analyst then reviews the AI's triage summary and makes the final decision — they are not replaced, but **empowered**.

---

## The Problem: Alert Fatigue in SOCs

### The Numbers Are Alarming

Modern Security Operations Centers face an overwhelming volume of security alerts:

- The average enterprise SOC receives **10,000+ alerts per day**
- Studies show SOC analysts manually investigate only **56% of daily alerts**
- **27% of security alerts** are never investigated due to volume
- The average **Mean Time to Respond (MTTR)** to a breach is 277 days
- **Alert fatigue** causes analysts to miss real threats buried in noise

### What is Alert Fatigue?

Alert fatigue occurs when security analysts become desensitized to alerts because of:

- **Volume:** Too many alerts to process in a workday
- **Noise:** High false positive rates (many alerts are benign)
- **Complexity:** Technical alerts require deep expertise to interpret
- **Repetition:** Seeing the same low-severity alerts repeatedly
- **Context:** Lack of context makes it hard to prioritize

### The Impact

```
Without AI Triage:
                    🚨 10,000 Alerts/Day
                           │
                    ┌──────▼──────┐
                    │  SOC Analyst │  ← overwhelmed, fatigued
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Manual Review│  ← slow, inconsistent
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │   56% Investigated      │
              │   27% NEVER Seen        │  ← real threats missed!
              │   17% False Positives   │
              └─────────────────────────┘
```

---

## The Solution: AI-Assisted Triage

This project demonstrates how AI can act as a **force multiplier** for SOC teams:

```
With AI Triage:
                    🚨 10,000 Alerts/Day
                           │
                    ┌──────▼──────┐
                    │ AI Pre-Triage│  ← fast, consistent, 24/7
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼───────┐
    │ Critical    │ │  Medium     │ │ Low/Benign  │
    │ 8-10/10     │ │  4-7/10     │ │  1-3/10     │
    │ Human First │ │ Human Review│ │ Auto-dismiss│
    └──────┬──────┘ └─────────────┘ └─────────────┘
           │
    ┌──────▼──────┐
    │  Analyst    │  ← focused, context-aware, efficient
    │  (Empowered)│
    └─────────────┘
```

### Key Benefits

| Metric | Without AI | With AI |
|--------|-----------|---------|
| Alert review rate | 56% | ~95% |
| Time per alert | 15-30 min | 2-5 min (review only) |
| Consistency | Variable | High |
| MITRE mapping | Manual lookup | Automated |
| Report generation | 1-2 hours | Seconds |
| 24/7 coverage | ❌ | ✅ |

---

## Key Concepts Explained

### 1. SIEM (Security Information and Event Management)

A **SIEM** is software that collects, aggregates, and analyzes security event logs from across an organization's IT infrastructure. Think of it as the nervous system that receives signals from every sensor in the environment.

**Wazuh** is the open-source SIEM used in this project. It:
- Installs lightweight agents on servers, endpoints, and cloud instances
- Collects logs (auth logs, syslog, Windows Event Logs, etc.)
- Applies detection rules to identify suspicious patterns
- Generates **alerts** when rules match

### 2. Alert Triage

**Triage** (from French: to sort) is the process of evaluating alerts to determine:
- Is this a real threat or a false positive?
- How severe is it?
- What needs to happen next?
- How urgent is the response?

Good triage reduces noise, prioritizes real threats, and ensures analysts focus their limited time on what matters most.

### 3. MITRE ATT&CK Framework

The **MITRE ATT&CK** (Adversarial Tactics, Techniques, and Common Knowledge) framework is a globally-accessible knowledge base of adversary tactics and techniques based on real-world observations.

It organizes attacks into:
- **Tactics** — The adversary's goal (e.g., "Initial Access", "Credential Access")
- **Techniques** — How they achieve the goal (e.g., "Brute Force", "Phishing")
- **Sub-techniques** — Specific variations (e.g., "Password Spraying")

Example: SSH brute force maps to:
- Tactic: `TA0006 - Credential Access`
- Technique: `T1110 - Brute Force`
- Sub-technique: `T1110.001 - Password Guessing`

This standardized language allows security teams worldwide to communicate precisely about threats.

### 4. Large Language Models (LLMs) in Security

**LLMs** like Claude are AI models trained on vast amounts of text data. They can:
- Understand context and nuance in technical text
- Generate human-readable explanations from structured data
- Apply pattern recognition from training on security literature
- Produce consistent, structured outputs with proper prompting

**Prompt Engineering** is the practice of crafting inputs to LLMs to get reliable, structured, and accurate outputs. It is a critical skill for AI security applications.

### 5. Incident Response (IR)

**Incident Response** is the structured methodology for handling a security breach or attack. The standard phases are:

1. **Preparation** — Policies, tools, training
2. **Identification** — Detecting the incident (triage!)
3. **Containment** — Stopping the spread
4. **Eradication** — Removing the threat
5. **Recovery** — Restoring operations
6. **Lessons Learned** — Improving defenses

This project automates the **Identification** phase.

---

## Project Scope

### In Scope

- ✅ Fetching alerts from Wazuh REST API
- ✅ Parsing and normalizing alert fields
- ✅ AI-powered plain-English summaries
- ✅ MITRE ATT&CK tactic and technique mapping
- ✅ Contextual severity scoring (1–10)
- ✅ Investigation step generation
- ✅ Remediation recommendation generation
- ✅ Markdown and PDF incident report generation
- ✅ Audit logging of all triage decisions
- ✅ CLI interface for analyst interaction
- ✅ Demo mode with sample alerts (no Wazuh required)

### Out of Scope

- ❌ Automated remediation execution (this project only recommends)
- ❌ SOAR (Security Orchestration, Automation, and Response) playbooks
- ❌ Threat intelligence platform integration (planned for v2.0)
- ❌ Machine learning model training
- ❌ Multi-tenant/enterprise deployment

---

## Who Should Use This?

| Audience | How This Project Helps |
|----------|----------------------|
| **Cybersecurity Students** | Hands-on experience with SIEM, AI, and SOC workflows |
| **Junior SOC Analysts** | Understand triage methodology and MITRE ATT&CK |
| **Security Engineers** | Reference implementation for AI-assisted detection |
| **Hiring Managers** | Evaluate candidate's ability to combine security + development |
| **Researchers** | Starting point for AI in security automation research |

---

## What You Will Learn

By studying and building this project, you will learn:

### Technical Skills
- How to use the Wazuh REST API to retrieve security alerts
- How to parse and normalize JSON security event data
- How to write effective security-focused prompts for LLMs
- How to structure AI outputs as machine-readable JSON
- How to generate professional incident reports programmatically
- How to build a rich CLI application in Python

### Security Concepts
- SIEM architecture and alert generation
- Alert triage methodology and best practices
- MITRE ATT&CK framework navigation
- Incident response lifecycle
- SOC workflow automation
- Defense in Depth principles
- Audit trail importance

### Professional Skills
- GitHub documentation and repository management
- Technical report writing
- Security project portfolio development
- Resume-worthy project narrative construction

---

> **Next:** [Architecture →](02_architecture.md)
