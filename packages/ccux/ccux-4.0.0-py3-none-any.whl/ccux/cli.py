#!/usr/bin/env python3
"""
CCUX - Claude Code UI Generator CLI (Interactive Version)
A sophisticated Python CLI tool that automatically generates conversion-optimized 
frontend landing pages using professional UX design thinking methodology.
"""

import os
import sys
import json
import time
import threading
import subprocess
import signal
import re
import importlib.metadata
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import typer
import yaml
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.status import Status
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel

# Import all the existing functionality we need
from .scrape import capture_multiple_references
from .scrape_simple import capture
from .theme_specifications import (
    THEME_SPECIFICATIONS,
    get_theme_choices,
    get_theme_description,
    get_theme_design_system_rules,
    detect_theme_from_content
)
from .prompt_templates import (
    reference_discovery_prompt,
    deep_product_understanding_prompt,
    ux_analysis_prompt,
    empathize_prompt,
    define_prompt,
    ideate_prompt,
    wireframe_prompt,
    design_system_prompt,
    high_fidelity_design_prompt,
    prototype_prompt,
    implementation_prompt,
    landing_prompt,
    regeneration_prompt,
    editgen_prompt,
    editgen_sections_prompt,
    get_animation_requirements,
    form_on_prompt,
    form_off_prompt,
    form_edit_prompt
)

app = typer.Typer(
    name="ccux",
    help="CCUX - Interactive AI Landing Page Generator",
    no_args_is_help=False,
    rich_markup_mode="rich"
)
console = Console()

# Import usage tracking functions from core module
from .core.usage_tracking import get_latest_usage, calculate_usage_difference

# Import signal handling from core module
from .core.signal_handling import register_signal_handler

# Register signal handler
register_signal_handler()

# Import configuration management from core module
from .core.configuration import Config

# Import project management functions from core module
from .core.project_management import (
    get_next_available_output_dir,
    discover_existing_projects, 
    extract_project_name_from_dir
)

# Import Claude integration and content processing from core modules
from .core.claude_integration import run_claude_with_progress, summarize_long_description
from .core.content_processing import safe_json_parse, strip_code_blocks

@app.command()
def init():
    """Launch CCUX Interactive Application (Main Entry Point)"""
    try:
        from .interactive import run_interactive_app
        run_interactive_app()
    except ImportError as e:
        console.print(f"[red]❌ Error importing interactive module: {e}[/red]")
        console.print("Please ensure all dependencies are installed.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error running interactive app: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def version():
    """Show version information"""
    try:
        package_version = importlib.metadata.version('ccux')
    except importlib.metadata.PackageNotFoundError:
        package_version = '1.0.1'
    
    console.print(f"[bold blue]CCUX v{package_version}[/bold blue]")
    console.print("Claude Code UI Generator - Interactive landing page creator")
    console.print("\n[dim]Run 'ccux init' to start the interactive application[/dim]")

@app.command()
def projects():
    """List all existing CCUX projects in the current directory"""
    projects = discover_existing_projects()
    
    if not projects:
        console.print("[yellow]No CCUX projects found in current directory.[/yellow]")
        console.print("Run [bold]ccux init[/bold] to create your first project!")
        return
    
    console.print(f"\n[bold cyan]📁 Found {len(projects)} CCUX project(s):[/bold cyan]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Directory", style="cyan", width=15)
    table.add_column("Project Name", style="green")
    table.add_column("Status", style="yellow", width=10)
    
    for project in projects:
        # All projects now have design analysis (since we filter for it)
        status = "Full"
        
        table.add_row(
            project['directory'] + "/",
            project['name'],
            status
        )
    
    console.print(table)
    
    console.print(f"\n[dim]💡 Run 'ccux init' to manage these projects interactively[/dim]")

@app.command()
def help(topic: Optional[str] = typer.Argument(None, help="Help topic (quickstart|themes|examples|workflows)")):
    """Show comprehensive help and usage examples"""
    # Import and use the help function from cli_old
    from . import cli_old
    cli_old.help(topic)

@app.command()
def gen(
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Product description"),
    desc_file: Optional[str] = typer.Option(None, "--desc-file", help="Path to file containing product description (supports .txt and .pdf files)"),
    url: Optional[List[str]] = typer.Option(None, "--url", "-u", help="Reference URLs (can be used multiple times, max 3)"),
    framework: Optional[str] = typer.Option("html", "--framework", "-f", help="Output framework (html|react)"),
    theme: Optional[str] = typer.Option("minimal", "--theme", "-t", help="Design theme"),
    no_design_thinking: bool = typer.Option(False, "--no-design-thinking", help="Skip full design thinking process"),
    include_forms: bool = typer.Option(False, "--include-forms", help="Include contact forms"),
    analyze_images: bool = typer.Option(True, "--analyze-images/--no-analyze-images", help="Enable visual analysis of competitor screenshots (uses more tokens)"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Generate conversion-optimized landing page"""
    # Import and use the gen function from cli_old
    from . import cli_old
    cli_old.gen(desc, desc_file, url, framework, theme, no_design_thinking, include_forms, analyze_images, output_dir)

@app.command()
def regen(
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Section(s) to regenerate (comma-separated)"),
    all: bool = typer.Option(False, "--all", help="Regenerate all sections"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Product description"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to landing page file"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Regenerate specific sections of existing landing page"""
    # Import and use the regen function from cli_old
    from . import cli_old
    cli_old.regen(section, all, desc, file, output_dir)

@app.command()
def multipage(
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Product description for multi-page website"),
    desc_file: Optional[str] = typer.Option(None, "--desc-file", help="Path to file containing product description"),
    theme: Optional[str] = typer.Option("minimal", "--theme", "-t", help="Design theme"),
    base_url: Optional[str] = typer.Option("https://example.com", "--base-url", "-u", help="Base URL for sitemap generation"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Generate intelligent multi-page website with parallel processing"""
    # Import and use the multipage function from cli_old
    from . import cli_old
    cli_old.multipage(desc, desc_file, theme, base_url, output_dir)

# Default command when no arguments provided
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """CCUX - Interactive AI Landing Page Generator
    
    Run 'ccux init' to start the interactive application.
    """
    if ctx.invoked_subcommand is None:
        # If no command is provided, launch the interactive app
        ctx.invoke(init)

if __name__ == "__main__":
    app()