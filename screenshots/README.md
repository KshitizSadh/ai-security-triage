# 📸 Screenshots

This directory contains project screenshots for the README and documentation.

## Screenshot Index

| Filename | Description | Status |
|----------|-------------|--------|
| `01_wazuh_dashboard.png` | Wazuh security alerts dashboard — shows live alerts and their levels | *Pending deployment* |
| `02_cli_output.png` | Full CLI output of the triage assistant processing an SSH brute force alert | *Pending deployment* |
| `03_ai_analysis.png` | Close-up of the AI analysis panel: MITRE mapping and severity score | *Pending deployment* |
| `04_incident_report.png` | Generated Markdown incident report rendered in VS Code preview | *Pending deployment* |
| `05_pdf_report.png` | PDF incident report opened in a browser, showing professional formatting | *Pending deployment* |
| `06_demo_mode.png` | Demo mode running with all 5 sample alert types in sequence | *Pending deployment* |

## How to Capture Screenshots

### CLI Output Screenshot
```bash
# Run the assistant and capture output
python main.py --mode demo --limit 1
# Take screenshot of the terminal
```

### Wazuh Dashboard Screenshot
1. Open your Wazuh web UI (https://WAZUH_IP)
2. Navigate to Security Events → Threat Hunting
3. Set time range to "Last 24 hours"
4. Screenshot the alert table

## Screenshot Naming Convention

Format: `{number:02d}_{descriptive_name}.png`

Example: `02_cli_output.png`

Use PNG format for screenshots. Keep files under 2MB for fast page loads.
