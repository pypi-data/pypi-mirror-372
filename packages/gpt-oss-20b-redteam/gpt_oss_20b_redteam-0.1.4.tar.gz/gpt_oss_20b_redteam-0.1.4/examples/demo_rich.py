#!/usr/bin/env python3
"""
Demo script showcasing Rich formatting for the red-teaming harness.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich import box
import time

def demo_rich_formatting():
    """Demonstrate Rich formatting capabilities."""
    console = Console()
    
    # Header
    console.print(Panel.fit(
        "[bold blue]🎨 Rich Formatting Demo[/bold blue]\n"
        "[dim]Beautiful output for the red-teaming harness[/dim]",
        box=box.DOUBLE,
        border_style="blue"
    ))
    
    # Status indicators
    with console.status("[bold green]Initializing system...", spinner="dots"):
        time.sleep(1)
    console.print("[green]✓[/green] System initialized")
    
    with console.status("[bold yellow]Loading probes...", spinner="dots"):
        time.sleep(1)
    console.print("[yellow]✓[/yellow] Probes loaded")
    
    # Progress bars
    console.print("\n[bold]📊 Progress Tracking:[/bold]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task1 = progress.add_task("Running evaluation awareness probe...", total=100)
        task2 = progress.add_task("Analyzing results...", total=50)
        
        for i in range(100):
            progress.update(task1, advance=1)
            if i < 50:
                progress.update(task2, advance=1)
            time.sleep(0.02)
    
    # Tables
    console.print("\n[bold]🔍 Probe Status:[/bold]")
    probe_table = Table(title="Available Probes", box=box.ROUNDED)
    probe_table.add_column("Probe", style="cyan", no_wrap=True)
    probe_table.add_column("Status", style="green")
    probe_table.add_column("Progress", style="yellow")
    probe_table.add_column("Description", style="white")
    
    probe_table.add_row("Evaluation Awareness", "✅ Complete", "100%", "Detects sandbagging behavior")
    probe_table.add_row("Deception Detection", "🚧 In Progress", "25%", "Finds reward hacking")
    probe_table.add_row("Code Sabotage", "⏳ Pending", "0%", "Identifies malicious code")
    probe_table.add_row("Encoding Evasion", "⏳ Pending", "0%", "Tests guardrail robustness")
    probe_table.add_row("Prefix Steering", "⏳ Pending", "0%", "Detects behavior modification")
    
    console.print(probe_table)
    
    # Metrics display
    console.print("\n[bold]📈 Sample Metrics:[/bold]")
    metrics_table = Table(title="Evaluation Awareness Results", box=box.ROUNDED)
    metrics_table.add_column("Metric", style="cyan", no_wrap=True)
    metrics_table.add_column("Value", style="green", justify="right")
    metrics_table.add_column("Status", style="yellow")
    
    metrics_table.add_row("Total Samples", "30", "✅")
    metrics_table.add_row("Eval Accuracy", "0.67", "⚠️")
    metrics_table.add_row("Casual Accuracy", "0.83", "✅")
    metrics_table.add_row("Accuracy Delta", "+0.16", "🚨")
    metrics_table.add_row("Refusal Rate Delta", "-0.10", "✅")
    
    console.print(metrics_table)
    
    # Color-coded results
    console.print("\n[bold]🎯 Key Findings:[/bold]")
    
    findings_panel = Panel(
        "[bold red]🚨 CRITICAL:[/bold] Model shows significant evaluation awareness\n"
        "[bold]Accuracy Delta:[/bold] [red]+0.16[/red] (casual - eval)\n"
        "[bold]Interpretation:[/bold] Model performs 16% better in casual vs evaluation contexts\n"
        "[bold]Risk Level:[/bold] [red]HIGH[/red] - Sandbagging behavior detected",
        title="🚨 Evaluation Awareness Detected",
        box=box.ROUNDED,
        border_style="red"
    )
    
    console.print(findings_panel)
    
    # Next steps
    next_steps = Panel(
        "[bold]🎯 Recommended Actions:[/bold]\n"
        "1. [bold]Immediate:[/bold] Document this finding for Kaggle submission\n"
        "2. [bold]Short-term:[/bold] Run remaining probes to find other vulnerabilities\n"
        "3. [bold]Long-term:[/bold] Develop mitigation strategies for evaluation awareness",
        title="Action Plan",
        box=box.ROUNDED,
        border_style="yellow"
    )
    
    console.print(next_steps)
    
    # Footer
    console.print(Panel(
        "[dim]Rich formatting makes complex data easy to read and understand.[/dim]\n"
        "[dim]Perfect for research presentations and debugging.[/dim]",
        box=box.SIMPLE,
        border_style="dim"
    ))

if __name__ == "__main__":
    demo_rich_formatting()
