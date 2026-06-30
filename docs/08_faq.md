# ❓ FAQ — AI Security Alert Triage Assistant

> **Document:** `docs/08_faq.md`

---

## General Questions

**Q: Do I need a real Wazuh deployment to use this?**
A: No. Demo mode (`python main.py --mode demo`) uses pre-loaded sample alerts and only requires the Claude API. This is ideal for learning, testing, and portfolio demos.

**Q: Can I use OpenAI/GPT-4 instead of Claude?**
A: The AI engine is designed to be modular. You can modify `scripts/ai_engine.py` to use the OpenAI API — the prompt structure is the same. However, Claude is tested and recommended for consistent JSON outputs.

**Q: Will this work with Splunk or Elastic instead of Wazuh?**
A: The `scripts/poller.py` module handles Wazuh-specific API calls. You can write an alternative poller (e.g., `elastic_poller.py`) that retrieves alerts from Elasticsearch and outputs the same normalized format expected by the parser. The rest of the pipeline works unchanged.

**Q: Is this safe to run in a production SOC?**
A: This is a **demonstration and learning project**. For production use, additional considerations are required: enterprise API rate limits, SOAR integration, analyst approval workflows, audit trails to a SIEM, and security review of the AI outputs. Do not automate remediation actions based solely on AI output.

**Q: How accurate are the MITRE ATT&CK mappings?**
A: The AI mappings are approximately 85–90% accurate for common alert types based on informal testing. The `configs/mitre_mapping.json` file provides rule-based fallback mappings that improve accuracy further. Always have a human analyst validate critical mappings.

**Q: Does this store my security alerts anywhere?**
A: Alert data is sent to the Anthropic Claude API for analysis. Anthropic's [privacy policy](https://www.anthropic.com/privacy) governs this data. For highly sensitive environments, consider running a self-hosted LLM (e.g., Ollama with Llama 3) instead of the Claude API — the architecture supports this swap.

**Q: How much does the Claude API cost?**
A: Each alert analysis uses approximately 1,500–2,500 tokens. At current Claude Sonnet pricing (as of 2024), processing 100 alerts costs roughly $0.10–$0.25. For high-volume use, claude-haiku is significantly cheaper.

**Q: Can I contribute to this project?**
A: Yes! See the contributing guidelines in `CONTRIBUTING.md`. Pull requests for new alert types, SIEM integrations, or output formats are especially welcome.

---

> **Previous:** [Troubleshooting ←](07_troubleshooting.md) | **Next:** [References →](09_references.md)
