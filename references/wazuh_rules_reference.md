# 📋 Wazuh Rules Reference — AI Security Alert Triage Assistant

> **Document:** `references/wazuh_rules_reference.md`
> Quick reference for commonly encountered Wazuh rule IDs

---

## Authentication Rules

| Rule ID | Level | Description | MITRE |
|---------|-------|-------------|-------|
| 5551 | 5 | Failed password for user | T1110 |
| 5710 | 10 | SSH brute force detected | T1110.001 |
| 5720 | 10 | Multiple SSH brute force (blocked) | T1110.001 |
| 5503 | 5 | PAM: User login failed | T1110 |
| 5501 | 12 | sudo privilege escalation attempt | T1548.003 |
| 2501 | 5 | User authentication failed | T1110 |
| 2502 | 10 | Multiple user auth failures | T1110 |

## File Integrity (FIM)

| Rule ID | Level | Description | MITRE |
|---------|-------|-------------|-------|
| 550 | 7 | Integrity checksum changed | T1070 |
| 554 | 5 | File added to system | T1105 |
| 553 | 7 | File modified by md5/sha1 change | T1070 |
| 551 | 5 | Integrity checksum changed (alert only) | T1070 |

## Web Attacks

| Rule ID | Level | Description | MITRE |
|---------|-------|-------------|-------|
| 31103 | 9 | Web attack: SQL injection | T1190 |
| 31106 | 9 | Web attack: XSS attempt | T1190 |
| 31151 | 10 | Web attack: directory traversal | T1190 |
| 31170 | 10 | Web attack: RCE attempt | T1190 |
| 30101 | 6 | Web server 400 error | T1190 |

## Network / Firewall

| Rule ID | Level | Description | MITRE |
|---------|-------|-------------|-------|
| 40101 | 8 | Firewall drop — possible scan | T1046 |
| 40110 | 12 | Multiple firewall drops from same source | T1595 |
| 4151 | 5 | Firewall configuration change | T1562 |

## System Events

| Rule ID | Level | Description | MITRE |
|---------|-------|-------------|-------|
| 2930 | 7 | Rootkit detection | T1014 |
| 510 | 7 | Host-based anomaly detected | T1203 |
| 5104 | 8 | Process creation by non-admin | T1059 |

## Wazuh Level Scale

| Level | Meaning | Typical Action |
|-------|---------|---------------|
| 0 | Ignored | None |
| 1–3 | Informational | Log only |
| 4–6 | Low | Review at end of shift |
| 7–11 | Medium/High | Investigate within 24h / 1h |
| 12–14 | Critical | Immediate response |
| 15 | Maximum | Emergency escalation |
