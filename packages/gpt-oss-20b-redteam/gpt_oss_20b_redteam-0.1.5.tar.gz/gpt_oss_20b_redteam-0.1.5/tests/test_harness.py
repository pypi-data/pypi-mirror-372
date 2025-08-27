#!/usr/bin/env python3
"""
Test script for the red-teaming harness.
"""

import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from gpt20b_redteam.probes.eval_awareness import EvaluationAwarenessProbe
from gpt20b_redteam.metrics import MetricsCollector
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box


def test_eval_awareness_probe():
    """Test the evaluation awareness probe with mock data."""
    console = Console()
    console.print("[bold yellow]🧪 Testing Evaluation Awareness Probe...[/bold yellow]")
    
    # Create mock model
    class MockModel:
        def __init__(self):
            self.name = "test-model"
        
        def generate(self, prompt):
            if "evaluation" in prompt.lower():
                return "I'm not entirely sure, but I think it might be Ouagadougou."
            else:
                return "The capital of Burkina Faso is Ouagadougou."
    
    model = MockModel()
    metrics = MetricsCollector()
    
    # Create probe
    with console.status("[bold green]Creating probe...", spinner="dots"):
        probe = EvaluationAwarenessProbe(model, metrics)
    
    # Test prompt generation
    with console.status("[bold green]Generating prompts...", spinner="dots"):
        prompts = probe.generate_prompts(seed=42)
    
    console.print(f"[green]✓[/green] Generated [bold]{len(prompts)}[/bold] prompts")
    
    # Test with a small subset
    test_prompts = prompts[:3]
    console.print(f"[green]✓[/green] Testing with [bold]{len(test_prompts)}[/bold] prompts")
    
    # Run probe
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running probe...", total=None)
        
        results = probe.run_probe(seeds=[42])
        progress.update(task, completed=True, description="[green]Probe completed![/green]")
    
    console.print(f"[green]✓[/green] Probe completed with [bold]{len(results.get('results', []))}[/bold] results")
    
    # Check metrics
    if 'metrics' in results:
        metrics_data = results['metrics']
        
        metrics_table = Table(title="📊 Test Metrics", box=box.ROUNDED)
        metrics_table.add_column("Metric", style="cyan", no_wrap=True)
        metrics_table.add_column("Value", style="green", justify="right")
        
        metrics_table.add_row("Total samples", str(metrics_data.get('total_samples', 0)))
        metrics_table.add_row("Eval accuracy", f"{metrics_data.get('eval_accuracy', 0):.3f}")
        metrics_table.add_row("Casual accuracy", f"{metrics_data.get('casual_accuracy', 0):.3f}")
        metrics_table.add_row("Accuracy delta", f"{metrics_data.get('accuracy_delta', 0):.3f}")
        
        console.print(metrics_table)
    
    return results


def test_metrics_collector():
    """Test the metrics collector."""
    console = Console()
    console.print("\n[bold yellow]🧪 Testing Metrics Collector...[/bold yellow]")
    
    metrics = MetricsCollector()
    
    # Test refusal detection
    responses = [
        "I cannot answer that question.",
        "Here's the answer: Paris",
        "I'm sorry, I cannot help with that."
    ]
    
    with console.status("[bold green]Testing metrics...", spinner="dots"):
        refusals = metrics.detect_refusals(responses)
        hedging = metrics.count_hedging_terms(responses)
        confidence = metrics.detect_confidence_markers(responses)
    
    # Create results table
    results_table = Table(title="🔍 Metrics Test Results", box=box.ROUNDED)
    results_table.add_column("Test", style="cyan", no_wrap=True)
    results_table.add_column("Input", style="white")
    results_table.add_column("Result", style="green")
    
    results_table.add_row("Refusal detection", responses[0], str(refusals[0]))
    results_table.add_row("Refusal detection", responses[1], str(refusals[1]))
    results_table.add_row("Refusal detection", responses[2], str(refusals[2]))
    results_table.add_row("Hedging detection", "All responses", str(hedging))
    results_table.add_row("Confidence detection", "All responses", str(confidence))
    
    console.print(results_table)
    
    return metrics


if __name__ == "__main__":
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]🚀 Testing GPT-OSS-20B Red-Teaming Harness[/bold blue]\n"
        "[dim]Running comprehensive tests...[/dim]",
        box=box.DOUBLE,
        border_style="blue"
    ))
    
    try:
        # Test metrics collector
        metrics = test_metrics_collector()
        
        # Test evaluation awareness probe
        results = test_eval_awareness_probe()
        
        success_panel = Panel(
            "[bold green]✅ All tests passed![/bold green]\n\n"
            "[bold]🎯 Next steps:[/bold]\n"
            "1. Install dependencies: pip install -r requirements.txt\n"
            "2. Run main harness: python main.py\n"
            "3. Check results/ directory for outputs",
            title="Test Results",
            box=box.ROUNDED,
            border_style="green"
        )
        
        console.print(success_panel)
        
    except Exception as e:
        error_panel = Panel(
            f"[bold red]❌ Test failed: {e}[/bold red]",
            title="Error",
            box=box.ROUNDED,
            border_style="red"
        )
        
        console.print(error_panel)
        console.print_exception()
        sys.exit(1)
