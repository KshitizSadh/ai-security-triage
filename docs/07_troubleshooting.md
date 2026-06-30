# 🔧 Troubleshooting Guide — AI Security Alert Triage Assistant

> **Document:** `docs/07_troubleshooting.md`

---

## Quick Diagnosis

Run this first — it checks all common issues automatically:

```bash
python scripts/utils.py --diagnose
```

---

## Common Issues & Solutions

### Issue 1: `ConnectionRefusedError` — Wazuh API Unreachable

**Symptom:**
```
ConnectionRefusedError: [Errno 111] Connection refused
Error: Cannot connect to Wazuh API at https://192.168.1.100:55000
```

**Causes & Solutions:**

```bash
# Cause 1: Wazuh is not running
sudo systemctl status wazuh-manager
sudo systemctl start wazuh-manager   # Start if stopped

# Cause 2: Wrong IP in .env
grep WAZUH_HOST .env
# Verify this matches your Wazuh manager's IP
ip addr show  # On Wazuh machine to get its IP

# Cause 3: Port 55000 is blocked by firewall
# On Wazuh machine:
sudo ufw allow 55000/tcp
sudo ufw reload

# Cause 4: Wazuh API service specifically is down
sudo systemctl status wazuh-api
sudo systemctl restart wazuh-api
```

---

### Issue 2: `SSL Certificate Verification Failed`

**Symptom:**
```
requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**
```bash
# Solution 1 (Quick): Disable SSL verification (for lab only)
# In .env:
WAZUH_VERIFY_SSL=false

# Solution 2 (Proper): Add certificate to trusted store
# On Wazuh machine, export the certificate:
sudo cat /etc/wazuh-indexer/certs/wazuh-indexer.pem

# Copy to your machine, then:
export REQUESTS_CA_BUNDLE=/path/to/wazuh-cert.pem
```

---

### Issue 3: `401 Unauthorized` — Wazuh Authentication Failed

**Symptom:**
```
WazuhAuthError: 401 Client Error: Unauthorized
```

**Solutions:**
```bash
# Test credentials manually
curl -k -u YOUR_USER:YOUR_PASSWORD \
  https://YOUR_WAZUH_IP:55000/security/user/authenticate

# If fails — wrong credentials. Reset via Wazuh CLI:
# On Wazuh Manager:
/var/ossec/bin/wazuh-control stop
sudo -u wazuh /var/ossec/bin/wazuh-authd
# Then reset password through Wazuh web UI
```

---

### Issue 4: `anthropic.AuthenticationError`

**Symptom:**
```
anthropic.AuthenticationError: Error code 401 - Invalid API key
```

**Solutions:**
```bash
# Verify key is in .env
grep ANTHROPIC_API_KEY .env

# Test key directly
python3 -c "
import os
from dotenv import load_dotenv
import anthropic
load_dotenv()
print('Key starts with:', os.getenv('ANTHROPIC_API_KEY', 'NOT SET')[:15])
"

# Common mistake: key copied with trailing space
# Fix: Open .env in nano and ensure no trailing spaces
```

---

### Issue 5: `JSON Decode Error` — AI Response Not Parseable

**Symptom:**
```
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
AIResponseError: Claude returned non-JSON response
```

**Explanation:** Occasionally the AI model returns text instead of JSON, or wraps JSON in markdown fences (```json).

**Solution:** The AI engine has automatic retry logic (3 attempts). If it persists:

```bash
# Enable debug mode to see raw AI responses
python main.py --mode demo --debug

# The debug output will show the exact Claude response
# If it's wrapped in ```json ... ``` the parser should handle it
# If not, check ai_engine.py clean_response() method
```

---

### Issue 6: `WeasyPrint` PDF Generation Failed

**Symptom:**
```
OSError: libpangoft2-1.0.so.0: cannot open shared object file
```

**Solution:**
```bash
# Install missing Pango system library
sudo apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libffi-dev

# Reinstall weasyprint
pip uninstall weasyprint -y
pip install weasyprint

# Test
python -c "from weasyprint import HTML; print('WeasyPrint OK')"
```

**Alternative:** Disable PDF generation:
```env
# In .env:
GENERATE_PDF=false
```

---

### Issue 7: `No Alerts Returned` from Wazuh

**Symptom:**
```
ℹ️  No alerts found above level 7 in the last 60 seconds.
```

**This might be expected** (no attacks!). To verify and fix:

```bash
# Lower the minimum alert level to get more alerts
python main.py --mode live --min-level 3

# Check Wazuh directly — what levels are your alerts?
curl -k -H "Authorization: Bearer $(TOKEN)" \
  "https://WAZUH_IP:55000/security/events?limit=5" | \
  python3 -m json.tool | grep '"level"'

# If no events at all — check agents are connected
curl -k -H "Authorization: Bearer $(TOKEN)" \
  "https://WAZUH_IP:55000/agents?status=active"
```

---

### Issue 8: `ModuleNotFoundError`

**Symptom:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Cause:** Running Python outside the virtual environment.

**Solution:**
```bash
# Always activate venv first!
source venv/bin/activate  # Note the (venv) prompt

# Then install and run
pip install -r requirements.txt
python main.py --mode demo
```

---

## Debug Mode

Enable verbose logging to diagnose any issue:

```bash
# Full debug output
python main.py --mode demo --debug

# Save debug output to file
python main.py --mode demo --debug 2>&1 | tee debug_output.txt
```

In debug mode you will see:
- Full Wazuh API requests and responses
- Complete prompts sent to Claude
- Raw Claude responses before parsing
- Step-by-step parsing of the response

---

## Getting Help

If you can't resolve an issue:

1. Run `python scripts/utils.py --diagnose` and save the output
2. Run `python main.py --mode demo --debug 2>&1 | tail -50` and save the output
3. Open an issue on GitHub with both outputs attached
4. Include your OS version: `uname -a` and Python version: `python3 --version`

---

> **Previous:** [Testing ←](06_testing.md) | **Next:** [FAQ →](08_faq.md)
