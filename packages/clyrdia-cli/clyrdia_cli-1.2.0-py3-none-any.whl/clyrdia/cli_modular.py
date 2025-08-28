#!/usr/bin/env python3
"""
Clyrdia CLI - Zero-Knowledge AI Benchmarking Platform
The most advanced local-first AI model benchmarking tool
"""

# ============================================================================
# Environment Loading - THIS IS THE FIX
# ============================================================================
from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file FIRST
# ============================================================================

import os
import sys
import json
import time
import asyncio
import uuid
import webbrowser
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict
import yaml

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.tree import Tree
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import box
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt

import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# Local imports from modularized structure
from .core.console import console, format_help_text, _display_welcome_screen
from .core.decorators import require_auth, _handle_first_run_auth, _is_first_run, _get_original_command
from .models.enums import ModelProvider
from .models.config import ModelConfig, ClyrdiaConfig
from .models.results import BenchmarkResult, TestCase
from .models.user import UserStatus, CreditEstimate
from .auth.licensing import LicensingManager
from .caching.manager import CacheManager
from .caching.models import CachedResult
from .database.local_db import LocalDatabase
from .benchmarking.engine import BenchmarkEngine
from .benchmarking.interface import ModelInterface
from .benchmarking.evaluator import QualityEvaluator
from .benchmarking.ratchet import RatchetSystem
from .benchmarking.canary import CanarySystem
from .dashboard import SimpleDashboard

app = typer.Typer(
    name="clyrdia-cli",
    help="🚀 Clyrdia - Zero-Knowledge AI Benchmarking Platform",
    pretty_exceptions_show_locals=False,
    rich_markup_mode="rich",  # Enable Rich markup in help text
    add_completion=False,  # Disable completion to avoid formatting issues
    no_args_is_help=True,  # Show help when no args provided
)

# Custom help callback to ensure proper formatting
def custom_help_callback(ctx: typer.Context, value: bool):
    if value:
        # Get help text and clean it up
        help_text = ctx.get_help()
        # Remove excessive blank lines at the beginning
        help_lines = help_text.split('\n')
        while help_lines and help_lines[0].strip() == '':
            help_lines.pop(0)
        # Ensure we have one clean line at the top
        clean_help = '\n' + '\n'.join(help_lines)
        typer.echo(clean_help)
        raise typer.Exit()

# ============================================================================
# CLI Commands
# ============================================================================

@app.command(name="run")
@require_auth
def run(
    config_file: str = typer.Option(..., "--config", "-c", help="Path to benchmark configuration file"),
    models: Optional[List[str]] = typer.Option(None, "--models", "-m", help="Specific models to test"),
    use_cache: bool = typer.Option(True, "--cache/--no-cache", help="Use cached results when available"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory for results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run a benchmark using the specified configuration"""
    try:
        # Load configuration
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Extract test cases
        test_cases = []
        for test_config in config.get('tests', []):
            test_case = TestCase(
                name=test_config['name'],
                prompt=test_config['prompt'],
                expected_output=test_config.get('expected_output'),
                max_tokens=test_config.get('max_tokens', 1000),
                temperature=test_config.get('temperature', 0.7),
                evaluation_criteria=test_config.get('evaluation_criteria', []),
                tags=test_config.get('tags', []),
                weight=test_config.get('weight', 1.0)
            )
            test_cases.append(test_case)
        
        # Get models to test
        if models:
            models_to_test = models
        else:
            models_to_test = config.get('models', ['gpt-5', 'claude-opus-4.1'])
        
        # Setup API keys using environment loader
        from .core.env_loader import get_api_keys, has_api_keys
        
        api_keys = get_api_keys()
        
        if not has_api_keys():
            console.print("[red]❌ No API keys found. Please create a .env file with your API keys.[/red]")
            console.print("[yellow]💡 Supported providers: OPENAI_API_KEY, ANTHROPIC_API_KEY[/yellow]")
            raise typer.Exit(1)
        
        console.print(f"[green]✅ Loaded API keys for providers: {', '.join(api_keys.keys())}[/green]")
        
        # Run benchmark
        console.print(f"[bold]🚀 Running benchmark with {len(test_cases)} test cases on {len(models_to_test)} models...[/bold]")
        
        engine = BenchmarkEngine(api_keys)
        results = asyncio.run(engine.run_benchmark(test_cases, models_to_test, use_cache))
        
        # Display results
        display_results(results, output_dir)
        
        console.print(f"[green]✅ Benchmark completed successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error running benchmark: {str(e)}[/red]")
        if verbose:
            raise
        raise typer.Exit(1)

@app.command(name="models")
def models():
    """List available models and their configurations"""
    try:
        available_models = ClyrdiaConfig.list_models()
        
        table = Table(title="Available Models")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Provider", style="magenta")
        table.add_column("Input Cost", style="green")
        table.add_column("Output Cost", style="green")
        table.add_column("Max Tokens", style="yellow")
        table.add_column("Capabilities", style="blue")
        
        for model_name in available_models:
            model_config = ClyrdiaConfig.get_model(model_name)
            if model_config:
                capabilities = ", ".join(model_config.capabilities[:3])
                if len(model_config.capabilities) > 3:
                    capabilities += "..."
                
                table.add_row(
                    model_name,
                    model_config.provider.value,
                    f"${model_config.input_cost}/1M",
                    f"${model_config.output_cost}/1M",
                    f"{model_config.max_tokens:,}",
                    capabilities
                )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error listing models: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command(name="cache")
@require_auth
def cache(
    action: str = typer.Argument(..., help="Action: stats, clear, or clear-model"),
    model: Optional[str] = typer.Argument(None, help="Model name for clear-model action")
):
    """Manage the result cache"""
    try:
        cache_manager = CacheManager()
        
        if action == "stats":
            stats = cache_manager.get_cache_stats()
            console.print(f"[bold]📊 Cache Statistics[/bold]")
            console.print(f"Total entries: {stats['total_entries']}")
            console.print(f"Cache size: {stats['cache_size_mb']} MB")
            console.print(f"Models: {', '.join([f'{m}: {c}' for m, c in stats['model_counts'].items()])}")
            
        elif action == "clear":
            cache_manager.clear_cache()
            console.print("[green]✅ Cache cleared successfully[/green]")
            
        elif action == "clear-model" and model:
            cache_manager.clear_cache(model)
            console.print(f"[green]✅ Cache cleared for model: {model}[/green]")
            
        else:
            console.print("[red]❌ Invalid action or missing model parameter[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error managing cache: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command(name="dashboard")
@require_auth
def dashboard():
    """Launch the Clyrdia dashboard"""
    try:
        dashboard_manager = SimpleDashboard()
        dashboard_manager.start_dashboard()
        dashboard_manager.open_dashboard_url()
        
    except Exception as e:
        console.print(f"[red]❌ Error starting dashboard: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command(name="credits")
@require_auth
def credits():
    """Show current credit balance and usage"""
    try:
        licensing_manager = LicensingManager()
        licensing_manager.show_credit_balance()
        
    except Exception as e:
        console.print(f"[red]❌ Error checking credits: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command(name="login")
def login():
    """Login to your Clyrdia account"""
    try:
        api_key = Prompt.ask("API Key", password=True)
        
        if not api_key or len(api_key.strip()) < 10:
            console.print("[red]❌ Invalid API key format.[/red]")
            raise typer.Exit(1)
        
        licensing_manager = LicensingManager()
        user_status = asyncio.run(licensing_manager.login(api_key.strip()))
        
        console.print(f"\n[green]✅ Successfully authenticated![/green]")
        console.print(f"Welcome, [bold]{user_status.user_name}[/bold]!")
        console.print(f"Plan: [bold]{user_status.plan.upper()}[/bold]")
        console.print(f"Credits: [bold]{user_status.credits_remaining:,}[/bold]")
        
    except Exception as e:
        console.print(f"[red]❌ Authentication failed: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command(name="logout")
def logout():
    """Logout and remove API key"""
    try:
        licensing_manager = LicensingManager()
        licensing_manager.logout()
        console.print("[green]✅ Logged out successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error logging out: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command(name="env")
def env():
    """Show environment configuration and API key status"""
    try:
        from .core.env_loader import env_loader
        env_loader.print_status()
    except Exception as e:
        console.print(f"[red]❌ Error showing environment: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command(name="optimize")
def optimize():
    """Show cost optimization recommendations based on benchmark results"""
    try:
        from .caching.manager import CacheManager
        from .models.config import get_model_configs
        
        console.print("\n[bold blue]💰 Cost Optimization Analysis[/bold blue]")
        console.print("=" * 50)
        
        # Get cache manager
        cache_manager = CacheManager()
        stats = cache_manager.get_cache_stats()
        
        if not stats.get('total_entries', 0):
            console.print("[yellow]⚠️  No benchmark results found. Run some benchmarks first to get optimization recommendations.[/yellow]")
            return
        
        # Get model configs (only OpenAI and Anthropic)
        model_configs = get_model_configs()
        
        console.print(f"\n[green]📊 Based on {stats['total_entries']} benchmark results:[/green]")
        
        # Analyze cost savings
        total_cost = 0
        model_costs = {}
        
        # Get cached results for analysis
        cached_results = cache_manager.get_all_cached_results()
        
        for result in cached_results:
            if result.model not in model_costs:
                model_costs[result.model] = {'total_cost': 0, 'count': 0, 'avg_quality': 0}
            
            model_costs[result.model]['total_cost'] += result.cost
            model_costs[result.model]['count'] += 1
            model_costs[result.model]['avg_quality'] += result.quality_score
            total_cost += result.cost
        
        # Calculate averages and recommendations
        console.print("\n[bold]Model Performance Analysis:[/bold]")
        console.print("─" * 50)
        
        recommendations = []
        
        for model, data in model_costs.items():
            if data['count'] > 0:
                avg_quality = data['avg_quality'] / data['count']
                avg_cost = data['total_cost'] / data['count']
                
                console.print(f"\n[bold]{model}:[/bold]")
                console.print(f"  • Tests run: {data['count']}")
                console.print(f"  • Total cost: ${data['total_cost']:.4f}")
                console.print(f"  • Average cost per test: ${avg_cost:.4f}")
                console.print(f"  • Average quality score: {avg_quality:.2f}")
                
                # Get model config for recommendations
                if model in model_configs:
                    config = model_configs[model]
                    recommendations.append({
                        'model': model,
                        'avg_cost': avg_cost,
                        'avg_quality': avg_quality,
                        'config': config
                    })
        
        # Sort by cost efficiency (quality per dollar)
        recommendations.sort(key=lambda x: x['avg_quality'] / x['avg_cost'] if x['avg_cost'] > 0 else float('inf'), reverse=True)
        
        console.print(f"\n[bold green]💡 Optimization Recommendations:[/bold green]")
        console.print("─" * 50)
        
        if recommendations:
            console.print(f"\n🥇 [bold]Most Cost-Effective:[/bold] {recommendations[0]['model']}")
            if recommendations[0]['avg_cost'] > 0:
                console.print(f"   Quality per dollar: {recommendations[0]['avg_quality'] / recommendations[0]['avg_cost']:.2f}")
            else:
                console.print(f"   Quality per dollar: ∞ (zero cost)")
            
            if len(recommendations) > 1:
                console.print(f"\n🥈 [bold]Second Best:[/bold] {recommendations[1]['model']}")
                if recommendations[1]['avg_cost'] > 0:
                    console.print(f"   Quality per dollar: {recommendations[1]['avg_quality'] / recommendations[1]['avg_cost']:.2f}")
                else:
                    console.print(f"   Quality per dollar: ∞ (zero cost)")
            
            # Cost savings analysis
            if len(recommendations) > 1:
                best_model = recommendations[0]
                second_best = recommendations[1]
                
                if best_model['avg_cost'] < second_best['avg_cost']:
                    savings_per_test = second_best['avg_cost'] - best_model['avg_cost']
                    console.print(f"\n💰 [bold]Potential Savings:[/bold] ${savings_per_test:.4f} per test by using {best_model['model']}")
                    
                    # Estimate annual savings
                    estimated_tests_per_month = 100  # Conservative estimate
                    annual_savings = savings_per_test * estimated_tests_per_month * 12
                    console.print(f"   Estimated annual savings: ${annual_savings:.2f}")
        
        console.print(f"\n[bold]Total Spent on Benchmarks:[/bold] ${total_cost:.4f}")
        console.print(f"[bold]Cache Hit Rate:[/bold] {stats.get('cache_hit_rate', 0):.1f}%")
        
        # Smart caching recommendations
        console.print(f"\n[bold blue]🗄️  Caching Recommendations:[/bold blue]")
        console.print("─" * 50)
        
        if stats.get('cache_hit_rate', 0) < 50:
            console.print("🔴 [red]Low cache hit rate detected. Consider:[/red]")
            console.print("   • Running similar benchmarks more frequently")
            console.print("   • Using consistent prompt templates")
            console.print("   • Enabling cache for repeated tests")
        else:
            console.print("🟢 [green]Good cache utilization![/green]")
            console.print("   • Cache is helping reduce costs")
            console.print("   • Consider running more diverse benchmarks")
        
        console.print(f"\n[bold]💡 Pro Tips:[/bold]")
        console.print("• Use `--no-cache` only when you need fresh results")
        console.print("• Run benchmarks in batches to maximize cache efficiency")
        console.print("• Monitor costs with `clyrdia-cli credits`")
        console.print("• Use `clyrdia-cli cache stats` to track cache performance")
        
    except Exception as e:
        console.print(f"[red]❌ Error analyzing optimization: {str(e)}[/red]")
        raise typer.Exit(1)

# ============================================================================
# Helper Functions
# ============================================================================

def display_results(results: List[BenchmarkResult], output_dir: Optional[str] = None):
    """Display benchmark results in a formatted table"""
    table = Table(title="Benchmark Results")
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Test", style="magenta")
    table.add_column("Latency", style="green")
    table.add_column("Cost", style="yellow")
    table.add_column("Success", style="blue")
    table.add_column("Quality", style="red")
    
    for result in results:
        quality_score = result.quality_scores.get('overall', 0.0) if result.quality_scores else 0.0
        
        # Format cost with appropriate precision
        if result.cost < 0.0001:
            cost_display = f"${result.cost:.6f}"
        elif result.cost < 0.01:
            cost_display = f"${result.cost:.5f}"
        else:
            cost_display = f"${result.cost:.4f}"
        
        table.add_row(
            result.model,
            result.test_name,
            f"{result.latency_ms}ms",
            cost_display,
            "✅" if result.success else "❌",
            f"{quality_score:.2f}"
        )
    
    console.print(table)
    
    # Save results if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        results_file = output_path / f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump([asdict(result) for result in results], f, indent=2, default=str)
        
        console.print(f"[green]📁 Results saved to: {results_file}[/green]")

if __name__ == "__main__":
    app()
