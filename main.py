# main.py
"""AI Security Alert Triage Assistant — Local LLM Edition. Entry point."""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from scripts.poller import WazuhPoller
from scripts.parser import AlertParser
from scripts.enricher import AlertEnricher
from scripts.ai_engine import AIEngine
from scripts.reporter import ReportGenerator

load_dotenv()
console = Console()

BANNER = """
[bold blue]╔══════════════════════════════════════════════════════════════════╗[/]
[bold blue]║[/]   [bold white]🛡️  AI Security Alert Triage Assistant  v2.0.0[/]                [bold blue]║[/]
[bold blue]║[/]   [dim]Wazuh SIEM + Ollama (Local LLM) — No Cloud, No API Key[/]        [bold blue]║[/]
[bold blue]╚══════════════════════════════════════════════════════════════════╝[/]
"""


def setup_logging(level: str = "INFO", log_file: str = "logs/triage.log"):
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
    )


def build_components():
    poller = WazuhPoller(
        host=os.getenv("WAZUH_HOST", "https://localhost"),
        port=int(os.getenv("WAZUH_PORT", 55000)),
        username=os.getenv("WAZUH_USER", ""),
        password=os.getenv("WAZUH_PASSWORD", ""),
        verify_ssl=os.getenv("WAZUH_VERIFY_SSL", "false").lower() == "true"
    )
    parser = AlertParser()
    enricher = AlertEnricher()
    ai_engine = AIEngine(
        model_fast=os.getenv("AI_MODEL_FAST", "llama3.1:8b"),
        model_deep=os.getenv("AI_MODEL_DEEP", "deepseek-r1:14b"),
        deep_threshold=int(os.getenv("DEEP_ANALYSIS_THRESHOLD", 7)),
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        max_tokens=int(os.getenv("AI_MAX_TOKENS", 2048)),
        temperature=float(os.getenv("AI_TEMPERATURE", 0.1))
    )
    reporter = ReportGenerator(
        output_dir=os.getenv("REPORT_OUTPUT_DIR", "reports/"),
        generate_pdf=os.getenv("GENERATE_PDF", "false").lower() == "true"
    )
    return poller, parser, enricher, ai_engine, reporter


def display_triage_result(alert: dict, analysis: dict):
    score = analysis.get("severity_score", 0)
    tier = analysis.get("_analysis_tier", "fast")
    color = "bold red" if score >= 9 else "red" if score >= 7 else "yellow" if score >= 4 else "green"

    console.print()
    console.rule(
        f"[{color}]🚨 Rule {alert['rule_id']} | Level {alert['rule_level']}/15 | "
        f"{alert['agent_name']}[/]"
    )
    console.print(Panel(analysis.get("summary", "N/A"), title="📝 Summary", border_style="blue"))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="dim", width=20)
    table.add_column("Value")
    table.add_row("Tactic", analysis.get("mitre_tactic", "N/A"))
    table.add_row("Technique", analysis.get("mitre_technique", "N/A"))
    table.add_row(f"[{color}]Severity[/]", f"[{color}]{score}/10[/]")
    table.add_row("Analysis Tier", f"{tier} ({analysis.get('_ai_model', 'N/A')})")
    console.print(table)

    console.print("\n[bold cyan]🔍 Investigation Steps:[/]")
    for i, step in enumerate(analysis.get("investigation_steps", []), 1):
        console.print(f"  {i}. {step}")

    console.print("\n[bold green]🛠️  Remediation Steps:[/]")
    for i, step in enumerate(analysis.get("remediation_steps", []), 1):
        console.print(f"  {i}. {step}")


def process_alert(alert_raw, parser, enricher, ai_engine, reporter):
    alert = parser.normalize(alert_raw)
    alert = enricher.enrich(alert)

    with console.status("[bold yellow]⚡ Fast-pass triage...[/]"):
        analysis = ai_engine.analyze(alert)

    display_triage_result(alert, analysis)
    paths = reporter.generate(alert, analysis)

    console.print("\n[bold]📄 Report saved:[/]")
    if paths.get("markdown"):
        console.print(f"  📝 [green]{paths['markdown']}[/]")
    return alert, analysis, paths


def run_demo_mode(parser, enricher, ai_engine, reporter, limit: int):
    import json
    fixtures_path = Path("tests/fixtures/sample_alerts.json")
    if not fixtures_path.exists():
        console.print("[red]ERROR: tests/fixtures/sample_alerts.json not found.[/]")
        sys.exit(1)

    alerts = json.loads(fixtures_path.read_text())["alerts"][:limit]
    console.print(f"[dim]📁 Demo mode: {len(alerts)} sample alerts loaded[/]\n")

    for i, raw_alert in enumerate(alerts, 1):
        console.print(f"\n[bold]Processing alert {i}/{len(alerts)}...[/]")
        process_alert(raw_alert, parser, enricher, ai_engine, reporter)


def main():
    p = argparse.ArgumentParser(description="AI Security Alert Triage Assistant")
    p.add_argument("--mode", choices=["demo", "live", "batch", "single"], default="demo")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--min-level", type=int, default=7)
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    setup_logging(level="DEBUG" if args.debug else os.getenv("LOG_LEVEL", "INFO"))
    console.print(BANNER)

    poller, alert_parser, enricher, ai_engine, reporter = build_components()

    with console.status("[cyan]Checking Ollama connection...[/]"):
        conn = ai_engine.test_connection()
    if not conn["connected"]:
        console.print("[red]ERROR: Cannot reach Ollama at the configured host.[/]")
        console.print("[dim]Is Ollama running? Try: ollama list[/]")
        sys.exit(1)
    if not conn["fast_model_available"]:
        console.print(f"[red]ERROR: Fast model not found. Run: ollama pull {ai_engine.model_fast}[/]")
        sys.exit(1)
    console.print(f"[green]✅ Ollama connected — models: {', '.join(conn['models_found'])}[/]")

    if args.mode == "demo":
        run_demo_mode(alert_parser, enricher, ai_engine, reporter, args.limit)
    elif args.mode == "live":
        with console.status("[cyan]Connecting to Wazuh...[/]"):
            wconn = poller.test_connection()
        if not wconn["connected"]:
            console.print(f"[red]Cannot connect to Wazuh: {wconn.get('error')}[/]")
            sys.exit(1)
        console.print(f"[green]✅ Wazuh connected (v{wconn['version']})[/]")

        with console.status("[cyan]Fetching alerts...[/]"):
            raw_alerts = poller.fetch_alerts(min_level=args.min_level, limit=args.limit)
        if not raw_alerts:
            console.print(f"[yellow]No alerts found above level {args.min_level}.[/]")
            return
        console.print(f"[green]Found {len(raw_alerts)} alerts to triage.[/]")
        for raw in raw_alerts:
            process_alert(raw, alert_parser, enricher, ai_engine, reporter)

    console.print("\n[bold green]✅ Triage session complete.[/]")


if __name__ == "__main__":
    main()
