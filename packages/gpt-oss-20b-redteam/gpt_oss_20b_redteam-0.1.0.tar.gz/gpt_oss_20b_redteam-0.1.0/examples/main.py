#!/usr/bin/env python3
"""
Main script for running the GPT-OSS-20B red-teaming harness.
"""

import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from gpt20b_redteam import RedTeamRunner, MetricsCollector, FindingsLogger
from gpt20b_redteam.model_wrapper import create_model
from gpt20b_redteam.config import get_model_config, get_redteam_config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import box


def create_model_instance():
    """Create a model instance based on configuration."""
    console = Console()
    
    # Get configuration from config.py
    model_config = get_model_config()
    backend = model_config["backend"]
    
    if backend == "mock":
        console.print("[yellow]⚠️[/yellow] Using mock model for testing...")
        # Fallback to mock model
        class MockModel:
            def __init__(self):
                self.name = "mock-gpt-oss-20b"
            
            def generate(self, prompt):
                """Mock generation that simulates evaluation awareness."""
                if "evaluation" in prompt.lower() or "research" in prompt.lower():
                    return "I'm not entirely sure, but I think it might be Ouagadougou."
                else:
                    return "The capital of Burkina Faso is Ouagadougou."
            
            def supports_activations(self):
                return False
            
            def get_model_info(self):
                return {"type": "mock", "name": self.name}
        
        return MockModel()
    
    try:
        if backend == "transformers":
            console.print(f"[yellow]⚠️[/yellow] Loading transformers model: {model_config.get('model_path', 'unknown')}")
            console.print("[dim]This may take a while...[/dim]")
        
        model = create_model(**model_config)
        return model
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load {backend} model: {e}")
        console.print("[yellow]⚠️[/yellow] Falling back to mock model for testing...")
        
        # Fallback to mock model
        class MockModel:
            def __init__(self):
                self.name = "mock-gpt-oss-20b"
            
            def generate(self, prompt):
                """Mock generation that simulates evaluation awareness."""
                if "evaluation" in prompt.lower() or "research" in prompt.lower():
                    return "The capital of Burkina Faso is Ouagadougou."
                else:
                    return "The capital of Burkina Faso is Ouagadougou."
            
            def supports_activations(self):
                return False
            
            def get_model_info(self):
                return {"type": "mock", "name": self.name}
        
        return MockModel()


def main():
    """Main entry point for the red-teaming harness."""
    console = Console()
    
    # Header
    console.print(Panel.fit(
        "[bold blue]🚀 GPT-OSS-20B Red-Teaming Harness[/bold blue]\n"
        "[dim]Masks, Sandbags, and Sabotage: Exposing Hidden Misalignment[/dim]",
        box=box.DOUBLE,
        border_style="blue"
    ))
    
    # Create model instance
    with console.status("[bold green]Initializing model...", spinner="dots"):
        model = create_model_instance()
    
    # Display model information
    model_info = model.get_model_info()
    model_type = model_info.get("type", "unknown")
    
    if model_type == "mock":
        console.print(f"[yellow]⚠️[/yellow] Using mock model: [bold]{model.name}[/bold]")
    else:
        console.print(f"[green]✓[/green] Using {model_type} model: [bold]{model_info.get('path', model_info.get('model', 'unknown'))}[/bold]")
        
        # Show additional model details for transformers
        if model_type == "transformers":
            details = f"Layers: {model_info.get('num_layers', 'N/A')}, "
            details += f"Hidden Size: {model_info.get('hidden_size', 'N/A')}, "
            details += f"Device: {model_info.get('device', 'N/A')}"
            console.print(f"[dim]{details}[/dim]")
    
    # Check activation support
    if model.supports_activations():
        console.print("[green]✓[/green] Whitebox mode: Activations available")
    else:
        console.print("[yellow]⚠️[/yellow] Blackbox mode: Activations not available")
    
    # Initialize the harness
    with console.status("[bold green]Initializing harness...", spinner="dots"):
        runner = RedTeamRunner(model, output_dir="results")
    
    console.print("[green]✓[/green] Harness initialized")
    
    # Check probe status
    status = runner.get_probe_status()
    
    # Create probe status table
    probe_table = Table(title="🔍 Available Probes", box=box.ROUNDED)
    probe_table.add_column("Probe Name", style="cyan", no_wrap=True)
    probe_table.add_column("Status", style="green")
    probe_table.add_column("Description", style="white")
    
    probe_descriptions = {
        "eval_awareness": "Evaluation Awareness & Sandbagging",
        "deception_rewardhack": "Deception & Reward Hacking",
        "sabotage_code": "Code Sabotage Detection",
        "encoding_evasion": "Encoding-Based Guardrail Evasion",
        "prefix_steering": "Prefix Steering Behavior"
    }
    
    for probe_name, probe_status in status.items():
        description = probe_descriptions.get(probe_name, "Red-teaming probe")
        probe_table.add_row(probe_name, probe_status, description)
    
    console.print(probe_table)
    
    # Get red-team configuration
    redteam_config = get_redteam_config()
    seeds = redteam_config.get("seeds", [42])
    
    # Run just the evaluation awareness probe first
    console.print("\n[bold yellow]🔍 Running Evaluation Awareness Probe...[/bold yellow]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running probe...", total=None)
            
            findings = runner.run_single_probe("eval_awareness", seeds=seeds)
            progress.update(task, completed=True, description="[green]Probe completed![/green]")
        
        console.print("[green]✓[/green] Evaluation awareness probe completed successfully!")
        
        # Show key metrics in a beautiful table
        if 'metrics' in findings:
            metrics = findings['metrics']
            
            metrics_table = Table(title="📊 Key Findings", box=box.ROUNDED)
            metrics_table.add_column("Metric", style="cyan", no_wrap=True)
            metrics_table.add_column("Value", style="green", justify="right")
            metrics_table.add_column("Description", style="white")
            
            metrics_table.add_row(
                "Total Samples", 
                str(metrics.get('total_samples', 0)),
                "Number of test cases run"
            )
            metrics_table.add_row(
                "Eval Accuracy", 
                f"{metrics.get('eval_accuracy', 0):.3f}",
                "Accuracy under evaluation framing"
            )
            metrics_table.add_row(
                "Casual Accuracy", 
                f"{metrics.get('casual_accuracy', 0):.3f}",
                "Accuracy under casual framing"
            )
            metrics_table.add_row(
                "Accuracy Delta", 
                f"{metrics.get('accuracy_delta', 0):.3f}",
                "Casual - Eval accuracy difference"
            )
            
            console.print(metrics_table)
            
            # Domain breakdown
            if 'domain_breakdown' in metrics:
                domain_table = Table(title="📈 Domain Breakdown", box=box.ROUNDED)
                domain_table.add_column("Domain", style="cyan", no_wrap=True)
                domain_table.add_column("Eval Accuracy", style="yellow", justify="right")
                domain_table.add_column("Casual Accuracy", style="yellow", justify="right")
                domain_table.add_column("Delta", style="green", justify="right")
                
                for domain, data in metrics['domain_breakdown'].items():
                    eval_acc = data.get('eval_accuracy', 0)
                    casual_acc = data.get('casual_accuracy', 0)
                    delta = casual_acc - eval_acc
                    
                    # Color code the delta
                    delta_style = "green" if delta > 0 else "red" if delta < 0 else "white"
                    delta_text = f"{delta:+.3f}"
                    
                    domain_table.add_row(
                        domain.title(),
                        f"{eval_acc:.3f}",
                        f"{casual_acc:.3f}",
                        f"[{delta_style}]{delta_text}[/{delta_style}]"
                    )
                
                console.print(domain_table)
        
        # Show output summary
        output_summary = runner.logger.get_output_summary()
        
        summary_panel = Panel(
            f"[bold]Output Directory:[/bold] {output_summary['output_directory']}\n"
            f"[bold]Total Files:[/bold] {output_summary['total_files']}\n"
            f"[bold]Findings Files:[/bold] {len(output_summary['findings_files'])}\n"
            f"[bold]Raw Results:[/bold] {len(output_summary['raw_results_files'])}",
            title="💾 Output Summary",
            box=box.ROUNDED,
            border_style="green"
        )
        
        console.print(summary_panel)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Evaluation awareness probe failed: {e}")
        import traceback
        console.print_exception()
    
    # Next steps
    next_steps = Panel(
        "[bold]🎯 Next Steps:[/bold]\n"
        "1. Replace mock_model with actual gpt-oss-20b\n"
        "2. Run all probes: runner.run_all_probes()\n"
        "3. Check results/ directory for findings\n"
        "4. Implement remaining probe types",
        title="Roadmap",
        box=box.ROUNDED,
        border_style="yellow"
    )
    
    console.print(next_steps)


if __name__ == "__main__":
    main()
