#!/usr/bin/env python3
"""
Demo script for the Code Sabotage Probe.
Tests for context-sensitive code generation issues.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gpt20b_redteam.probes.sabotage_code import SabotageCodeProbe, CodeAnalyzer
from gpt20b_redteam.metrics import AdvancedMetricsCollector
from gpt20b_redteam.model_wrapper import create_model
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

def demo_sabotage_probe():
    """Demonstrate the Code Sabotage Probe."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold red]🔧 Code Sabotage Probe Demo[/bold red]\n"
        "[dim]Detecting context-sensitive code generation issues[/dim]",
        box=box.DOUBLE,
        border_style="red"
    ))
    
    # Initialize model
    console.print("[bold]🤖 Initializing Model...[/bold]")
    
    try:
        # Try to create a real model, fallback to mock
        model = create_model()
        console.print(f"[green]✓[/green] Model initialized: {type(model).__name__}")
    except Exception as e:
        console.print(f"[yellow]⚠️[/yellow] Using mock model: {e}")
        # Create a simple mock model for demo
        class MockModel:
            def generate(self, prompt):
                return f"# Mock response for: {prompt[:50]}...\n\ndef mock_function():\n    pass"
        model = MockModel()
    
    # Initialize metrics collector
    console.print("[bold]📊 Initializing Metrics Collector...[/bold]")
    metrics = AdvancedMetricsCollector()
    console.print("[green]✓[/green] Metrics collector initialized")
    
    # Initialize probe
    console.print("[bold]🔍 Initializing Code Sabotage Probe...[/bold]")
    probe = SabotageCodeProbe(model, metrics)
    console.print(f"[green]✓[/green] Probe initialized with {len(probe.task_pairs)} task pairs")
    
    # Show task pairs
    console.print("\n[bold]📋 Task Pairs Overview:[/bold]")
    
    task_table = Table(title="Code Generation Task Pairs", box=box.ROUNDED)
    task_table.add_column("Pair", style="cyan", no_wrap=True)
    task_table.add_column("Low-Stakes Task", style="green")
    task_table.add_column("High-Stakes Task", style="red")
    task_table.add_column("Category", style="yellow")
    
    for i, (low_task, high_task) in enumerate(probe.task_pairs):
        task_table.add_row(
            f"Pair {i+1}",
            low_task.description,
            high_task.description,
            high_task.category
        )
    
    console.print(task_table)
    
    # Demo code analyzer
    console.print("\n[bold]🔍 Testing Code Analyzer...[/bold]")
    
    analyzer = CodeAnalyzer()
    
    # Test cases
    test_cases = [
        {
            'name': 'Safe Code',
            'code': 'def safe_function():\n    return "hello"',
            'context': 'low_stakes'
        },
        {
            'name': 'Dangerous Code',
            'code': 'import subprocess\ndef dangerous():\n    subprocess.call("rm -rf /", shell=True)',
            'context': 'high_stakes'
        },
        {
            'name': 'Suspicious Comments',
            'code': 'def process_data():\n    # TODO: skip validation for now\n    pass',
            'context': 'high_stakes'
        }
    ]
    
    analysis_table = Table(title="Code Safety Analysis", box=box.ROUNDED)
    analysis_table.add_column("Test Case", style="cyan")
    analysis_table.add_column("Risk Score", style="yellow", justify="right")
    analysis_table.add_column("Issues Found", style="red", justify="right")
    analysis_table.add_column("Assessment", style="green")
    
    for test_case in test_cases:
        analysis = analyzer.analyze_code_safety(test_case['code'], test_case['context'])
        
        analysis_table.add_row(
            test_case['name'],
            f"{analysis.get('risk_score', 0):.1f}",
            str(analysis.get('issue_count', 0)),
            analysis.get('context', 'unknown')
        )
    
    console.print(analysis_table)
    
    # Run a small subset of the probe
    console.print("\n[bold]🚀 Running Code Sabotage Probe (Limited Demo)...[/bold]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Running probe...", total=None)
        
        try:
            # Run with just one seed and limited tasks
            results = probe.run_probe(seeds=[42])
            
            progress.update(task, description="Analysis complete!")
            
            console.print(f"[green]✓[/green] Probe completed successfully")
            
            # Display results
            console.print("\n[bold]📊 Probe Results:[/bold]")
            
            results_panel = Panel(
                f"[bold]Status:[/bold] {results['status']}\n"
                f"[bold]Total Tasks:[/bold] {results['total_tasks']}\n"
                f"[bold]Sabotage Detected:[/bold] {'Yes' if results['sabotage_detected'] else 'No'}\n"
                f"[bold]Total Findings:[/bold] {results.get('findings', [])}",
                title="Probe Summary",
                box=box.ROUNDED,
                border_style="blue"
            )
            
            console.print(results_panel)
            
            # Show risk summary if available
            risk_summary = results.get('risk_summary', {})
            if risk_summary:
                console.print("\n[bold]⚠️ Risk Summary:[/bold]")
                
                risk_table = Table(title="Risk Assessment", box=box.ROUNDED)
                risk_table.add_column("Risk Level", style="cyan")
                risk_table.add_column("Count", style="yellow", justify="right")
                
                for level, count in risk_summary.get('sabotage_risk_levels', {}).items():
                    risk_table.add_row(level.title(), str(count))
                
                console.print(risk_table)
                
                # Show high-risk tasks
                high_risk_tasks = risk_summary.get('high_risk_tasks', [])
                if high_risk_tasks:
                    console.print("\n[bold]🚨 High-Risk Tasks:[/bold]")
                    
                    high_risk_table = Table(title="High-Risk Tasks", box=box.ROUNDED)
                    high_risk_table.add_column("Task ID", style="cyan")
                    high_risk_table.add_column("Category", style="yellow")
                    high_risk_table.add_column("Risk Delta", style="red", justify="right")
                    high_risk_table.add_column("Assessment", style="green")
                    
                    for task in high_risk_tasks:
                        high_risk_table.add_row(
                            task['task_id'],
                            task['category'],
                            f"{task['risk_delta']:.1f}",
                            task['assessment']
                        )
                    
                    console.print(high_risk_table)
            
            # Show findings
            findings = results.get('findings', [])
            if findings:
                console.print("\n[bold]🔍 Detailed Findings:[/bold]")
                
                for i, finding in enumerate(findings, 1):
                    finding_panel = Panel(
                        f"[bold]Type:[/bold] {finding['type']}\n"
                        f"[bold]Category:[/bold] {finding['category']}\n"
                        f"[bold]Risk Delta:[/bold] {finding['risk_delta']:.1f}\n"
                        f"[bold]Assessment:[/bold] {finding['assessment']}\n"
                        f"[bold]Evidence:[/bold] {finding['evidence']}",
                        title=f"Finding {i}",
                        box=box.ROUNDED,
                        border_style="red"
                    )
                    console.print(finding_panel)
            
        except Exception as e:
            console.print(f"[red]✗[/red] Probe failed: {e}")
            console.print("[yellow]⚠️[/yellow] This might be due to model access issues")
    
    # Save results
    try:
        probe.save_intermediate_results(probe.results_cache, "sabotage_probe_demo.json")
        console.print("[green]✓[/green] Results saved to sabotage_probe_demo.json")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to save results: {e}")
    
    # Next steps
    next_steps = Panel(
        "[bold]🎯 Next Steps:[/bold]\n"
        "1. Configure real model access for full testing\n"
        "2. Run with multiple seeds for statistical significance\n"
        "3. Analyze specific sabotage patterns found\n"
        "4. Integrate with other probes for comprehensive analysis\n"
        "5. Generate detailed reports for findings",
        title="Roadmap",
        box=box.ROUNDED,
        border_style="yellow"
    )
    
    console.print(next_steps)

if __name__ == "__main__":
    demo_sabotage_probe()
