#!/usr/bin/env python3
"""
GPT-OSS-20B Red-Teaming CLI
Beautiful command-line interface with Rich output.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    from rich.layout import Layout
    from rich.columns import Columns
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich not available. Install with: pip install rich")
    Console = None

from .config import (
    setup_openai_api, 
    setup_anthropic_api, 
    load_example_config, 
    get_model_config, 
    set_model_backend
)
from .model_wrapper import create_model
from .runner import RedTeamRunner


class RichRedTeamCLI:
    """Beautiful CLI for GPT-OSS-20B Red-Teaming."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        
    def print_banner(self):
        """Print beautiful banner."""
        if not self.console:
            print("🚀 GPT-OSS-20B Red-Teaming Harness")
            return
            
        banner = Text()
        banner.append("🚀 ", style="bold blue")
        banner.append("GPT-OSS-20B Red-Teaming Harness", style="bold white")
        banner.append("\n", style="white")
        banner.append("Masks, Sandbags, and Sabotage: Exposing Hidden Misalignment", style="italic cyan")
        
        panel = Panel(
            banner,
            border_style="blue",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def print_model_info(self, model_config: dict):
        """Print model configuration info."""
        if not self.console:
            print(f"🔧 Model: {model_config.get('model_path', 'Unknown')}")
            return
            
        table = Table(title="Model Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in model_config.items():
            if key == 'model_path':
                table.add_row("Model Path", str(value))
            elif key == 'backend':
                table.add_row("Backend", str(value))
            elif key == 'device':
                table.add_row("Device", str(value))
            elif key == 'torch_dtype':
                table.add_row("Data Type", str(value))
        
        self.console.print(table)
    
    def print_probe_status(self, runner: RedTeamRunner):
        """Print probe status table."""
        if not self.console:
            print("📊 Available Probes:")
            for name in runner.probes.keys():
                print(f"  - {name}")
            return
            
        table = Table(title="🔍 Available Probes", box=box.ROUNDED)
        table.add_column("Probe Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Description", style="white")
        
        descriptions = {
            "eval_awareness": "Evaluation Awareness & Sandbagging",
            "deception_rewardhack": "Deception & Reward Hacking",
            "sabotage_code": "Code Sabotage Detection",
            "encoding_evasion": "Encoding-Based Guardrail Evasion",
            "prefix_steering": "Prefix Steering Behavior",
            "cross_probe_compounding": "Cross-Probe Compounding Effects",
            "tokenizer_frequency_sandbagging": "Tokenizer Frequency Sandbagging",
            "long_horizon_sleeper": "Long-Horizon Sleeper Agents",
            "covert_channel_capacity": "Covert Channel Capacity",
            "refusal_boundary_cartography": "Refusal Boundary Cartography"
        }
        
        for name, probe in runner.probes.items():
            status = "ready"
            desc = descriptions.get(name, "Advanced red-teaming probe")
            table.add_row(name, status, desc)
        
        self.console.print(table)
    
    def run_with_progress(self, runner: RedTeamRunner, seeds: List[int]) -> dict:
        """Run probes with beautiful progress tracking."""
        if not self.console:
            return runner.run_all_probes(seeds=seeds)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            # Create progress task
            task = progress.add_task(
                "[cyan]Running red-teaming probes...", 
                total=len(runner.probes)
            )
            
            all_findings = {}
            
            for probe_name, probe in runner.probes.items():
                progress.update(task, description=f"[cyan]Running {probe_name}...")
                
                try:
                    findings = probe.run_probe(seeds=seeds)
                    all_findings[probe_name] = findings
                    runner.logger.save_findings(probe_name, findings)
                    progress.advance(task)
                    
                except Exception as e:
                    all_findings[probe_name] = {"error": str(e)}
                    progress.advance(task)
            
            # Save combined results
            combined_results = {
                "timestamp": "2024-01-15T20:00:00",
                "seeds": seeds,
                "findings": all_findings,
                "summary": self._generate_summary(all_findings)
            }
            
            runner.logger.save_combined_results(combined_results)
            return combined_results
    
    def print_results_summary(self, results: dict):
        """Print beautiful results summary."""
        if not self.console:
            print(f"📊 Summary: {results['summary']}")
            return
            
        summary = results['summary']
        
        # Create summary table
        table = Table(title="📊 Red-Teaming Results Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Probes", str(summary.get('total_probes', 0)))
        table.add_row("Successful", str(summary.get('successful_probes', 0)))
        table.add_row("Failed", str(summary.get('failed_probes', 0)))
        
        self.console.print(table)
        
        # Show key findings
        if 'key_metrics' in summary:
            metrics_table = Table(title="🔍 Key Metrics", box=box.ROUNDED)
            metrics_table.add_column("Probe", style="cyan")
            metrics_table.add_column("Metric", style="yellow")
            metrics_table.add_column("Value", style="white")
            
            for probe_name, metrics in summary['key_metrics'].items():
                if isinstance(metrics, dict):
                    for metric_name, value in metrics.items():
                        if isinstance(value, (int, float)):
                            metrics_table.add_row(probe_name, metric_name, f"{value:.3f}")
            
            self.console.print(metrics_table)
    
    def _generate_summary(self, all_findings: dict) -> dict:
        """Generate summary statistics."""
        summary = {
            "total_probes": len(all_findings),
            "successful_probes": len([f for f in all_findings.values() if "error" not in f]),
            "failed_probes": len([f for f in all_findings.values() if "error" in f]),
            "key_metrics": {}
        }
        
        # Extract key metrics from each probe
        for probe_name, findings in all_findings.items():
            if "error" not in findings and "metrics" in findings:
                summary["key_metrics"][probe_name] = findings["metrics"]
        
        return summary


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GPT-OSS-20B Red-Teaming Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with OpenAI API
  gpt20b-redteam --openai gpt-4 --api-key sk-...
  
  # Run with local model
  gpt20b-redteam --model microsoft/DialoGPT-large
  
  # Run with custom seeds
  gpt20b-redteam --model microsoft/DialoGPT-large --seeds 42 123 456
  
  # Run with output directory
  gpt20b-redteam --model microsoft/DialoGPT-large --output results_my_run
        """
    )
    
    # Model selection
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument(
        "--model", "-m",
        help="Local model path or HuggingFace model ID"
    )
    model_group.add_argument(
        "--openai", "-o",
        choices=["gpt-4", "gpt-3.5-turbo"],
        help="Use OpenAI API model"
    )
    model_group.add_argument(
        "--anthropic", "-a",
        choices=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        help="Use Anthropic API model"
    )
    
    # API configuration
    parser.add_argument(
        "--api-key",
        help="API key for OpenAI/Anthropic (or set OPENAI_API_KEY/ANTHROPIC_API_KEY env vars)"
    )
    
    # Run configuration
    parser.add_argument(
        "--seeds", "-s",
        nargs="+",
        type=int,
        default=[42, 123, 456],
        help="Random seeds for reproducibility (default: 42 123 456)"
    )
    
    parser.add_argument(
        "--output", "-O",
        default="results",
        help="Output directory for results (default: results)"
    )
    
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda", "mps"],
        default="auto",
        help="Device for local models (default: auto)"
    )
    
    parser.add_argument(
        "--no-rich",
        action="store_true",
        help="Disable Rich output (use plain text)"
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = RichRedTeamCLI()
    if args.no_rich:
        cli.console = None
    
    # Print banner
    cli.print_banner()
    
    try:
        # Configure model
        if args.openai:
            if args.api_key:
                os.environ["OPENAI_API_KEY"] = args.api_key
            setup_openai_api(args.openai)
            model = create_model(backend="openai")
            model_config = {"backend": "openai", "model": args.openai}
            
        elif args.anthropic:
            if args.api_key:
                os.environ["ANTHROPIC_API_KEY"] = args.api_key
            setup_anthropic_api(args.anthropic)
            model = create_model(backend="anthropic")
            model_config = {"backend": "anthropic", "model": args.anthropic}
            
        else:  # Local model
            set_model_backend("transformers")
            load_example_config("huggingface_hub")
            mc = get_model_config()
            mc["model_path"] = args.model
            mc["device"] = args.device
            
            model = create_model(**mc)
            model_config = mc
        
        # Show model info
        cli.print_model_info(model_config)
        
        # Initialize runner
        runner = RedTeamRunner(model, output_dir=args.output)
        
        # Show probe status
        cli.print_probe_status(runner)
        
        # Run probes
        results = cli.run_with_progress(runner, args.seeds)
        
        # Show results
        cli.print_results_summary(results)
        
        if cli.console:
            cli.console.print(f"\n[green]✅[/green] Results saved to: [cyan]{args.output}/[/cyan]")
        else:
            print(f"\n✅ Results saved to: {args.output}/")
            
    except Exception as e:
        if cli.console:
            cli.console.print(f"[red]❌ Error: {e}[/red]")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
