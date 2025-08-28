#!/usr/bin/env python3
"""
CCUX - Claude Code UI Generator CLI
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
    help="Claude Code UI Generator - Automatically generate conversion-optimized landing pages",
    no_args_is_help=True,
    rich_markup_mode="rich"
)
console = Console()

# Import core module functions (these will override any duplicates below due to import order)
from .core.usage_tracking import (
    calculate_estimated_cost,
    get_latest_usage, 
    calculate_usage_difference,
    display_usage_stats
)
from .core.signal_handling import register_signal_handler
from .core.configuration import Config  
from .core.project_management import (
    get_next_available_output_dir,
    discover_existing_projects,
    extract_project_name_from_dir
)
from .core.claude_integration import run_claude_with_progress, summarize_long_description
from .core.content_processing import safe_json_parse, strip_code_blocks
from .core.animation_utilities import add_theme_appropriate_animations, remove_animations_from_content

# Register signal handler
register_signal_handler()

def calculate_estimated_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost based on Claude pricing"""
    # Claude 3.5 Sonnet pricing (as of 2024)
    # Input: $3.00 per million tokens
    # Output: $15.00 per million tokens
    input_cost = (input_tokens / 1_000_000) * 3.00
    output_cost = (output_tokens / 1_000_000) * 15.00
    return input_cost + output_cost

def get_latest_usage() -> Dict[str, Any]:
    """Get the latest usage data from ccusage"""
    try:
        result = subprocess.run(['ccusage', '--json', '--order', 'desc'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get('daily') and len(data['daily']) > 0:
                return data['daily'][0]  # Most recent day
    except Exception:
        pass
    return {}

def calculate_usage_difference(pre_usage: Dict[str, Any], post_usage: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate the difference in usage between two ccusage snapshots"""
    if not pre_usage or not post_usage:
        return {}
    
    # Calculate differences
    input_diff = post_usage.get('inputTokens', 0) - pre_usage.get('inputTokens', 0)
    output_diff = post_usage.get('outputTokens', 0) - pre_usage.get('outputTokens', 0)
    cost_diff = post_usage.get('totalCost', 0) - pre_usage.get('totalCost', 0)
    
    # Return usage stats in expected format
    return {
        'input_tokens': max(0, input_diff),
        'output_tokens': max(0, output_diff),
        'cost': max(0.0, cost_diff)
    }

# Global variables for signal handling
current_subprocess = None
current_progress = None

def signal_handler(signum, frame):
    """Handle keyboard interrupts gracefully"""
    global current_subprocess, current_progress
    
    console.print("\n[yellow]⚠️  Interrupt received, cleaning up...[/yellow]")
    
    if current_subprocess:
        try:
            current_subprocess.terminate()
            current_subprocess.wait(timeout=5)
        except:
            try:
                current_subprocess.kill()
            except:
                pass
    
    if current_progress:
        current_progress.stop()
    
    console.print("[red]❌ Operation cancelled by user[/red]")
    sys.exit(1)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

class Config:
    """Configuration management for CCUX"""
    
    def __init__(self, config_path: str = "ccux.yaml"):
        self.config_path = config_path
        self.defaults = {
            'framework': 'html',
            'theme': 'minimal',
            'sections': ['hero', 'features', 'pricing', 'footer'],
            'claude_cmd': 'claude',
            'output_dir': 'output/landing-page'
        }
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                # Merge with defaults
                return {**self.defaults, **config}
            except Exception as e:
                console.print(f"[yellow]⚠️  Error loading config: {e}. Using defaults.[/yellow]")
        
        return self.defaults.copy()
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)

def get_next_available_output_dir() -> str:
    """Find the next available output directory"""
    # Check base 'output' directory first
    if not os.path.exists("output"):
        return "output"
    
    # If output exists, check output1, output2, etc.
    for i in range(1, 100):  # Support up to 99 projects
        output_dir = f"output{i}"
        if not os.path.exists(output_dir):
            return output_dir
    
    # Fallback if somehow we have 100+ projects
    import time
    return f"output-{int(time.time())}"

def discover_existing_projects() -> List[Dict[str, str]]:
    """Discover all existing CCUX projects in current directory"""
    projects = []
    
    # Check for output directory
    if os.path.exists("output") and os.path.exists(os.path.join("output", "index.html")):
        project_name = extract_project_name_from_dir("output")
        projects.append({
            "directory": "output",
            "name": project_name,
            "path": os.path.join("output", "index.html")
        })
    
    # Check for output1, output2, etc.
    for i in range(1, 100):
        output_dir = f"output{i}"
        if os.path.exists(output_dir) and os.path.exists(os.path.join(output_dir, "index.html")):
            project_name = extract_project_name_from_dir(output_dir)
            projects.append({
                "directory": output_dir,
                "name": project_name,
                "path": os.path.join(output_dir, "index.html")
            })
    
    return projects

def extract_project_name_from_dir(output_dir: str) -> str:
    """Extract project name from design analysis or HTML content"""
    try:
        # Try to get from design_analysis.json first
        analysis_file = os.path.join(output_dir, "design_analysis.json")
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
                # Look for brand name or product description
                if 'brand_name' in analysis:
                    return analysis['brand_name'][:30]
                if 'product_description' in analysis:
                    return analysis['product_description'][:30] + "..."
        
        # Fallback: extract from HTML title or first heading
        html_file = os.path.join(output_dir, "index.html")
        if os.path.exists(html_file):
            with open(html_file, 'r') as f:
                content = f.read()
                # Try to extract title
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                if title_match:
                    return title_match.group(1)[:30]
                # Try to extract first h1
                h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
                if h1_match:
                    # Remove HTML tags
                    clean_text = re.sub(r'<[^>]+>', '', h1_match.group(1))
                    return clean_text[:30].strip()
    except:
        pass
    
    return f"Project in {output_dir}"

def select_project_interactively(projects: List[Dict[str, str]], action: str = "work with") -> str:
    """Show interactive menu to select a project"""
    if not projects:
        console.print(f"[red]❌ No existing CCUX projects found.[/red]")
        console.print("Run [bold]ccux gen[/bold] first to create a project.")
        raise typer.Exit(1)
    
    if len(projects) == 1:
        console.print(f"[green]📁 Using project: {projects[0]['directory']}/[/green]")
        return projects[0]['directory']
    
    console.print(f"\n[bold cyan]📋 Select project to {action}:[/bold cyan]")
    
    # Create table showing projects
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Directory", style="cyan")
    table.add_column("Project Name", style="green")
    
    for i, project in enumerate(projects, 1):
        table.add_row(str(i), project['directory'], project['name'])
    
    console.print(table)
    
    while True:
        try:
            choice = IntPrompt.ask(
                f"[bold]Choose project (1-{len(projects)})[/bold]",
                default=1,
                show_default=True
            )
            if 1 <= choice <= len(projects):
                selected = projects[choice - 1]
                console.print(f"[green]✅ Selected: {selected['directory']}/[/green]")
                return selected['directory']
            else:
                console.print(f"[red]Please enter a number between 1 and {len(projects)}[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled[/yellow]")
            raise typer.Exit(1)

def select_theme_interactively() -> str:
    """Show interactive menu to select a theme with descriptions"""
    themes_data = []
    valid_themes = get_theme_choices()
    
    # Group themes by category for better organization
    theme_categories = {
        "Core Themes": ["minimal", "brutalist", "playful", "corporate"],
        "Modern Design": ["morphism", "animated", "terminal", "aesthetic"],
        "Specialized": ["dark", "vibrant", "sustainable", "data", "illustrated"]
    }
    
    console.print("\n[bold cyan]🎨 Select a design theme:[/bold cyan]")
    
    # Display themes by category
    current_index = 1
    for category, theme_names in theme_categories.items():
        console.print(f"\n[bold magenta]{category}:[/bold magenta]")
        
        for theme_name in theme_names:
            if theme_name in valid_themes:
                desc = get_theme_description(theme_name)
                themes_data.append({"name": theme_name, "description": desc})
                console.print(f"  [dim]{current_index:2}.[/dim] [cyan]{theme_name.title()}[/cyan]")
                console.print(f"      [dim]{desc}[/dim]")
                current_index += 1
    
    console.print(f"\n[bold]Total themes available: {len(themes_data)}[/bold]")
    
    while True:
        try:
            choice = IntPrompt.ask(
                f"[bold]Choose theme (1-{len(themes_data)})[/bold]",
                default=1,
                show_default=True
            )
            if 1 <= choice <= len(themes_data):
                selected = themes_data[choice - 1]
                console.print(f"[green]✅ Selected: {selected['name'].title()} theme[/green]")
                console.print(f"[dim]{selected['description']}[/dim]")
                return selected['name']
            else:
                console.print(f"[red]Please enter a number between 1 and {len(themes_data)}[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Theme selection cancelled[/yellow]")
            raise typer.Exit(1)

def run_claude_with_progress(prompt: str, description: str = "Claude Code is thinking...") -> tuple[str, Dict[str, Any]]:
    """Run Claude CLI with real-time progress indication and usage tracking via ccusage"""
    global current_subprocess, current_progress
    
    config = Config()
    claude_cmd = config.get('claude_cmd', 'claude')
    
    # Get usage before Claude call for comparison
    pre_usage = get_latest_usage()
    
    # Prepare Claude command
    cmd = [claude_cmd, '--print', prompt]
    
    output_lines = []
    stderr_lines = []
    
    def read_stream(stream, lines_list):
        """Read from stream and collect output"""
        try:
            for line in iter(stream.readline, ''):
                if line:
                    lines_list.append(line.strip())
        except:
            pass
    
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]{description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        current_progress = progress
        task = progress.add_task("Processing", total=None)
        
        try:
            # Start Claude process
            current_subprocess = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=read_stream, 
                args=(current_subprocess.stdout, output_lines)
            )
            stderr_thread = threading.Thread(
                target=read_stream, 
                args=(current_subprocess.stderr, stderr_lines)
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process with timeout (5 minutes)
            try:
                current_subprocess.wait(timeout=300)
            except subprocess.TimeoutExpired:
                current_subprocess.kill()
                raise Exception("Claude Code timed out after 5 minutes")
            
            # Wait for threads to finish
            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            
            if current_subprocess.returncode != 0:
                error_msg = '\n'.join(stderr_lines) if stderr_lines else "Claude Code execution failed"
                raise Exception(f"Claude Code failed: {error_msg}")
            
            
        except Exception as e:
            current_progress = None
            current_subprocess = None
            raise e
        
        finally:
            current_progress = None
            current_subprocess = None
    
    # Combine output
    full_output = '\n'.join(output_lines)
    
    # Get usage after Claude call and calculate difference
    post_usage = get_latest_usage()
    usage_stats = calculate_usage_difference(pre_usage, post_usage)
    
    # Show usage statistics if available
    if usage_stats and any(usage_stats.get(key, 0) > 0 for key in ['input_tokens', 'output_tokens']):
        console.print("\n[bold cyan]📊 Usage Statistics:[/bold cyan]")
        if 'input_tokens' in usage_stats:
            console.print(f"  Input tokens: [green]{usage_stats['input_tokens']:,}[/green]")
        if 'output_tokens' in usage_stats:
            console.print(f"  Output tokens: [green]{usage_stats['output_tokens']:,}[/green]")
        if 'cost' in usage_stats:
            console.print(f"  Cost: [green]${usage_stats['cost']:.4f}[/green]")
        console.print()
    
    return full_output, usage_stats

def extract_sections_html(html_content: str, section_names: List[str]) -> str:
    """Extract specific sections from HTML content for section-only editing"""
    extracted = []
    
    for section_name in section_names:
        # Look for section markers
        start_marker = f"<!-- START: {section_name} -->"
        end_marker = f"<!-- END: {section_name} -->"
        
        start_pos = html_content.find(start_marker)
        if start_pos == -1:
            continue
            
        end_pos = html_content.find(end_marker, start_pos)
        if end_pos == -1:
            continue
            
        # Extract the section including markers
        section_content = html_content[start_pos:end_pos + len(end_marker)]
        extracted.append(section_content)
    
    return '\n\n'.join(extracted)

def merge_sections_into_html(original_html: str, updated_sections: str) -> str:
    """Merge updated sections back into the original HTML"""
    result_html = original_html
    
    # Parse updated sections and replace them one by one
    import re
    section_pattern = r'<!-- START: (\w+) -->(.*?)<!-- END: \1 -->'
    
    for match in re.finditer(section_pattern, updated_sections, re.DOTALL):
        section_name = match.group(1)
        new_section_content = match.group(0)  # Full section with markers
        
        # Find and replace the section in original HTML
        original_section_pattern = f'<!-- START: {section_name} -->.*?<!-- END: {section_name} -->'
        result_html = re.sub(original_section_pattern, new_section_content, result_html, flags=re.DOTALL)
    
    return result_html

def summarize_long_description(desc: str) -> str:
    """Summarize product description if longer than 300 words"""
    word_count = len(desc.split())
    
    if word_count <= 300:
        return desc
    
    console.print(f"[yellow]📝 Description has {word_count} words, summarizing to 200-300 words...[/yellow]")
    
    summarization_prompt = f"""You are given a long product description. 
If the text is fewer than 300 words, return it unchanged. 
If it is longer than 300 words, summarize it into 200–300 words while keeping only the most important details:

- Problem it solves
- Target user
- Unique differentiator
- Best feature

Make the summary clear, concise, and business-oriented. 
Do not include filler or marketing fluff. 
Output only the final text (no explanations).

Product description to summarize:
{desc}"""
    
    try:
        summary, _ = run_claude_with_progress(summarization_prompt, "Summarizing description...")
        return summary.strip()
    except Exception as e:
        console.print(f"[yellow]⚠️  Failed to summarize description: {e}. Using original.[/yellow]")
        return desc


def validate_html_output(html_content: str) -> bool:
    """Validate that HTML output is not an error message"""
    if not html_content or len(html_content.strip()) < 50:
        return False
    
    # Check for common error patterns first (be more specific to avoid false positives)
    error_patterns = [
        "execution error",
        "error occurred", 
        "failed to generate",
        "request timeout",
        "connection timeout", 
        "claude code failed",
        "i'm unable to",
        "i cannot",
        "sorry, i can't"
    ]
    
    content_lower = html_content.lower()
    for pattern in error_patterns:
        if pattern in content_lower:
            return False
    
    # Check for basic HTML indicators (more lenient and case-insensitive)
    html_indicators = [
        "<!doctype html",
        "<html",
        "<head>",
        "<body>",
        "<div",
        "<section",
        "tailwindcss",
        "<nav",
        "<main",
        "<footer"
    ]
    
    # Must have at least 2 HTML indicators
    found_indicators = 0
    for indicator in html_indicators:
        if indicator in content_lower:
            found_indicators += 1
    
    # Additional check: if it starts with DOCTYPE and has basic HTML structure
    if content_lower.strip().startswith('<!doctype html'):
        found_indicators += 2  # Give extra weight to proper DOCTYPE
    
    return found_indicators >= 2

def extract_brand_name(description: str) -> str:
    """Extract brand/product name from description for display (max 10 words)"""
    import re
    
    # Common patterns for product names
    patterns = [
        r'^([A-Z][A-Za-z0-9\s]{1,30})\s*[-–—]\s*',  # "ProductName - description"
        r'^([A-Z][A-Za-z0-9\s]{1,30})\s*\([^)]+\)',  # "ProductName (description)"  
        r'^([A-Z][A-Za-z0-9\s]{1,30})\s+is\s+',      # "ProductName is a..."
        r'^([A-Z][A-Za-z0-9\s]{1,30})\s*:\s*',       # "ProductName: description"
        r'^([A-Z][A-Za-z0-9\s]{1,30})\s*,\s*',       # "ProductName, description"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, description.strip())
        if match:
            brand = match.group(1).strip()
            if len(brand.split()) <= 10:
                return brand
    
    # Enhanced fallback: look for capitalized words that might be brand names
    words = description.strip().split()
    
    # Look for sequences of capitalized words (likely brand names)
    brand_candidates = []
    current_brand = []
    
    for word in words[:15]:  # Check first 15 words only
        if word[0].isupper() or word.isdigit() or any(c.isupper() for c in word):
            current_brand.append(word)
        else:
            if current_brand and len(current_brand) <= 3:  # Max 3 words for brand name
                brand_candidates.append(' '.join(current_brand))
            current_brand = []
    
    # Add final candidate if exists
    if current_brand and len(current_brand) <= 3:
        brand_candidates.append(' '.join(current_brand))
    
    # Return the first reasonable brand candidate
    for candidate in brand_candidates:
        if len(candidate.split()) <= 4 and len(candidate) > 1:
            return candidate
    
    # Final fallback: first 8 words with ellipsis
    return ' '.join(words[:8]) + ('...' if len(words) > 8 else '')

def safe_json_parse(text: str) -> Dict[str, Any]:
    """Safely parse JSON from Claude output"""
    try:
        # Try to extract JSON from code blocks
        lines = text.strip().split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            if line.strip().startswith('```json') or line.strip().startswith('```'):
                in_json = True
                continue
            elif line.strip() == '```' and in_json:
                break
            elif in_json:
                json_lines.append(line)
            elif line.strip().startswith('{'):
                # Direct JSON start
                json_lines = [line]
                in_json = True
            elif in_json and line.strip().endswith('}'):
                json_lines.append(line)
                break
            elif in_json:
                json_lines.append(line)
        
        if json_lines:
            json_text = '\n'.join(json_lines)
            return json.loads(json_text)
        
        # Fallback: try parsing entire text
        return json.loads(text)
        
    except Exception:
        return {}

def strip_code_blocks(text: str) -> str:
    """Strip markdown code blocks from Claude output"""
    lines = text.strip().split('\n')
    result_lines = []
    in_code_block = False
    
    for line in lines:
        # Check for start of code block
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        # If not in code block, include the line
        if not in_code_block:
            result_lines.append(line)
    
    return '\n'.join(result_lines).strip()

def get_form_specification_interactive(type_arg, fields_arg, style_arg, cta_arg, theme):
    """Get form specification either from arguments or interactive prompts"""
    
    # Default values
    form_types = ['contact', 'newsletter', 'signup', 'custom']
    field_options = ['name', 'email', 'phone', 'message', 'company', 'website', 'subject']
    style_options = ['inline', 'modal', 'sidebar', 'fullpage']
    
    # Get form type
    if type_arg and type_arg in form_types:
        form_type = type_arg
    else:
        if type_arg:
            console.print(f"[yellow]⚠️  Invalid form type: {type_arg}[/yellow]")
        console.print("\n[bold]Form Types:[/bold]")
        for i, ft in enumerate(form_types, 1):
            descriptions = {
                'contact': 'General contact form with name, email, message',
                'newsletter': 'Simple email signup form',
                'signup': 'Registration form with multiple fields', 
                'custom': 'Specify your own field configuration'
            }
            console.print(f"  {i}. [cyan]{ft}[/cyan]: {descriptions[ft]}")
        
        form_type = Prompt.ask(
            "\n[bold]Select form type[/bold]",
            choices=form_types,
            default='contact'
        )
    
    # Get form fields
    if fields_arg:
        fields = [f.strip() for f in fields_arg.split(',') if f.strip() in field_options]
        if not fields:
            console.print(f"[yellow]⚠️  No valid fields in: {fields_arg}[/yellow]")
            fields = None
    else:
        fields = None
    
    if not fields:
        # Set default fields based on form type
        default_fields = {
            'contact': ['name', 'email', 'message'],
            'newsletter': ['email'],
            'signup': ['name', 'email', 'phone'],
            'custom': ['name', 'email']
        }
        
        suggested_fields = default_fields.get(form_type, ['name', 'email'])
        
        console.print(f"\n[bold]Available Fields:[/bold] {', '.join(field_options)}")
        console.print(f"[bold]Suggested for {form_type}:[/bold] {', '.join(suggested_fields)}")
        
        fields_input = Prompt.ask(
            "\n[bold]Enter fields (comma-separated)[/bold]",
            default=','.join(suggested_fields)
        )
        
        fields = [f.strip() for f in fields_input.split(',') if f.strip()]
        # Filter to valid fields only
        fields = [f for f in fields if f in field_options]
        
        if not fields:
            fields = ['name', 'email']  # Fallback
    
    # Get form style
    if style_arg and style_arg in style_options:
        form_style = style_arg
    else:
        if style_arg:
            console.print(f"[yellow]⚠️  Invalid form style: {style_arg}[/yellow]")
        
        console.print("\n[bold]Form Styles:[/bold]")
        style_descriptions = {
            'inline': 'Embedded directly in page sections',
            'modal': 'Popup modal overlay (click to open)',
            'sidebar': 'Fixed sidebar form',
            'fullpage': 'Dedicated full-page form section'
        }
        
        for style, desc in style_descriptions.items():
            console.print(f"  • [cyan]{style}[/cyan]: {desc}")
        
        form_style = Prompt.ask(
            "\n[bold]Select form style[/bold]",
            choices=style_options,
            default='inline'
        )
    
    # Get CTA text
    if not cta_arg:
        default_ctas = {
            'contact': 'Send Message',
            'newsletter': 'Subscribe Now',
            'signup': 'Sign Up',
            'custom': 'Submit'
        }
        
        cta_text = Prompt.ask(
            "\n[bold]CTA button text[/bold]",
            default=default_ctas.get(form_type, 'Submit')
        )
    else:
        cta_text = cta_arg
    
    # Create specification object
    spec = {
        'type': form_type,
        'fields': fields,
        'style': form_style,
        'cta': cta_text,
        'theme': theme,
        'description': f"{form_type.title()} form with {len(fields)} fields ({', '.join(fields)}) in {form_style} style"
    }
    
    return spec

def generate_custom_form_prompt(form_spec, theme):
    """Generate Claude prompt for custom form specifications"""
    
    field_html_map = {
        'name': '<input type=\"text\" name=\"name\" placeholder=\"Your Name\" required>',
        'email': '<input type=\"email\" name=\"email\" placeholder=\"Your Email\" required>',
        'phone': '<input type=\"tel\" name=\"phone\" placeholder=\"Phone Number\">',
        'message': '<textarea name=\"message\" rows=\"4\" placeholder=\"Your Message\" required></textarea>',
        'company': '<input type=\"text\" name=\"company\" placeholder=\"Company Name\">',
        'website': '<input type=\"url\" name=\"website\" placeholder=\"Website URL\">',
        'subject': '<input type=\"text\" name=\"subject\" placeholder=\"Subject\" required>'
    }
    
    form_fields_html = '\\n    '.join([field_html_map.get(field, f'<input type=\"text\" name=\"{field}\" placeholder=\"{field.title()}\">') for field in form_spec['fields']])
    
    style_requirements = {
        'inline': 'Embed form directly within appropriate page sections (hero, contact, or footer)',
        'modal': 'Create popup modal form with overlay background and close button',
        'sidebar': 'Create fixed position sidebar form (right side of screen)',
        'fullpage': 'Create dedicated full-width form section with prominent placement'
    }
    
    theme_styles = get_theme_form_styles(theme)
    
    return f"""
CUSTOM FORM SPECIFICATION REQUIREMENTS:

Form Type: {form_spec['type'].upper()}
Fields Required: {', '.join(form_spec['fields'])}
Form Style: {form_spec['style'].upper()}
CTA Button Text: "{form_spec['cta']}"

FORM STRUCTURE TEMPLATE:
<form action="#" method="POST" class="[THEME-SPECIFIC-CLASSES]">
    <h3 class="[THEME-HEADER-CLASSES]">Form Title</h3>
    {form_fields_html}
    <button type="submit" class="[THEME-BUTTON-CLASSES]">{form_spec['cta']}</button>
</form>

PLACEMENT REQUIREMENTS:
{style_requirements[form_spec['style']]}

STYLING REQUIREMENTS FOR {theme.upper()} THEME:
{theme_styles}

FUNCTIONAL REQUIREMENTS:
• Form must have proper action="#" method="POST" attributes
• All required fields must have 'required' attribute
• Include proper input types (email, tel, url, text, textarea)
• Add appropriate placeholder text for each field
• Include form validation styling (focus states, error states)
• Ensure mobile responsiveness
• Add proper labels for accessibility (aria-label or visible labels)

IMPORTANT: The form must seamlessly integrate with the {theme} theme's design system and be placed according to the {form_spec['style']} style requirements.
"""

def get_theme_form_styles(theme: str) -> str:
    """Get theme-specific form styling requirements"""
    
    if theme.lower() == 'brutalist':
        return """
BRUTALIST FORM REQUIREMENTS:
• Forms: bg-white border-4 border-black p-6 shadow-[8px_8px_0px_#000] (NO rounded corners)
• Form Headers: text-xl font-bold text-black uppercase
• Input Fields: bg-white text-black font-mono border-4 border-black shadow-[4px_4px_0px_#000] placeholder-gray-600 uppercase (NO rounded corners)
• Focus States: focus:border-primary focus:shadow-[8px_8px_0px_#FF0080]
• Submit Buttons: bg-primary text-white font-black uppercase border-4 border-black shadow-[4px_4px_0px_#000]
• Button Hover: hover:bg-primary-dark hover:shadow-[8px_8px_0px_#000] hover:translate-x-1 hover:translate-y-1
• Typography: All text UPPERCASE, heavy font weights, no soft styling
• Colors: Primary #FF0080, black borders, white backgrounds, harsh contrast
• NO rounded corners, NO soft shadows, NO gradients - pure geometric brutalism
        """
    
    elif theme.lower() == 'minimal':
        return """
MINIMAL FORM REQUIREMENTS:
• Forms: bg-white border border-gray-200 p-6 rounded-lg shadow-sm
• Form Headers: text-lg font-medium text-gray-900
• Input Fields: border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500
• Submit Buttons: bg-gray-900 text-white px-4 py-2 rounded-md hover:bg-gray-800
• Clean, simple styling with subtle shadows and rounded corners
        """
    
    elif theme.lower() == 'corporate':
        return """
CORPORATE FORM REQUIREMENTS:
• Forms: bg-white border border-gray-300 p-8 rounded-lg shadow-lg
• Form Headers: text-xl font-semibold text-gray-900
• Input Fields: border-2 border-gray-300 rounded-lg px-4 py-3 focus:border-blue-600
• Submit Buttons: bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700
• Professional, trustworthy styling with blue accent colors
        """
    
    elif theme.lower() == 'playful':
        return """
PLAYFUL FORM REQUIREMENTS:
• Forms: bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 p-6 rounded-2xl
• Form Headers: text-xl font-bold text-purple-800
• Input Fields: border-2 border-purple-300 rounded-xl px-4 py-3 focus:border-pink-400
• Submit Buttons: bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-xl
• Fun, colorful styling with gradients and organic shapes
        """
    
    else:
        # Default fallback for other themes
        return f"""
{theme.upper()} FORM REQUIREMENTS:
• Forms should match the {theme} theme's established design system
• Use consistent colors, typography, spacing, and border styles from the theme
• Maintain theme-appropriate hover states and focus indicators
• Follow the theme's button and input styling conventions
        """

def find_landing_page_files(output_dir: str = None) -> Dict[str, str]:
    """Find existing landing page files in common locations"""
    if output_dir is None:
        output_dir = "output/landing-page"
    
    search_paths = [
        output_dir,
        ".",
        "dist",
        "build",
        "public"
    ]
    
    found_files = {}
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        # Look for HTML files
        for file_name in ['index.html', 'landing.html', 'page.html']:
            file_path = os.path.join(search_path, file_name)
            if os.path.exists(file_path):
                found_files['html'] = file_path
                break
                
        # Look for React files
        for file_name in ['App.jsx', 'Landing.jsx', 'Page.jsx']:
            file_path = os.path.join(search_path, file_name)
            if os.path.exists(file_path):
                found_files['react'] = file_path
                break
    
    return found_files

def add_theme_appropriate_animations(content: str, theme: str) -> str:
    """Add theme-appropriate animations to existing content without Claude API calls"""
    
    # Define theme-specific animation styles
    theme_animations = {
        'minimal': {
            'css': '''
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes slideUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .animate-fadeInUp { animation: fadeInUp 0.6s ease-out forwards; }
            .animate-slideUp { animation: slideUp 0.5s ease-out forwards; }
            .animate-delay-100 { animation-delay: 0.1s; }
            .animate-delay-200 { animation-delay: 0.2s; }
            .animate-delay-300 { animation-delay: 0.3s; }
            [data-animate] { opacity: 0; }
            @media (prefers-reduced-motion: reduce) {
                [data-animate] { opacity: 1; animation: none !important; }
            }
            ''',
            'attributes': [
                ('h1', 'data-animate="fadeInUp"'),
                ('.hero', 'data-animate="fadeInUp"'),
                ('.feature', 'data-animate="slideUp"'),
                ('.card', 'data-animate="slideUp"'),
                ('button', 'data-animate="slideUp"')
            ]
        },
        'brutalist': {
            'css': '''
            @keyframes brutalistSlam {
                0% { opacity: 0; transform: translateY(40px) scale(0.9); }
                70% { transform: translateY(-5px) scale(1.02); }
                100% { opacity: 1; transform: translateY(0) scale(1); }
            }
            @keyframes brutalistPop {
                from { opacity: 0; transform: scale(0.8); }
                to { opacity: 1; transform: scale(1); }
            }
            .animate-brutalistSlam { animation: brutalistSlam 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards; }
            .animate-brutalistPop { animation: brutalistPop 0.4s ease-out forwards; }
            .animate-delay-100 { animation-delay: 0.1s; }
            .animate-delay-200 { animation-delay: 0.2s; }
            [data-animate] { opacity: 0; }
            @media (prefers-reduced-motion: reduce) {
                [data-animate] { opacity: 1; animation: none !important; }
            }
            ''',
            'attributes': [
                ('h1', 'data-animate="brutalistSlam"'),
                ('.hero', 'data-animate="brutalistSlam"'),
                ('.feature', 'data-animate="brutalistPop"'),
                ('.card', 'data-animate="brutalistPop"'),
                ('button', 'data-animate="brutalistPop"')
            ]
        },
        'dark': {
            'css': '''
            @keyframes darkFadeIn {
                from { opacity: 0; transform: translateY(20px); filter: blur(5px); }
                to { opacity: 1; transform: translateY(0); filter: blur(0px); }
            }
            @keyframes darkGlow {
                from { opacity: 0; box-shadow: 0 0 0 rgba(255, 255, 255, 0.1); }
                to { opacity: 1; box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1); }
            }
            .animate-darkFadeIn { animation: darkFadeIn 0.8s ease-out forwards; }
            .animate-darkGlow { animation: darkGlow 0.6s ease-out forwards; }
            .animate-delay-100 { animation-delay: 0.1s; }
            .animate-delay-200 { animation-delay: 0.2s; }
            [data-animate] { opacity: 0; }
            @media (prefers-reduced-motion: reduce) {
                [data-animate] { opacity: 1; animation: none !important; }
            }
            ''',
            'attributes': [
                ('h1', 'data-animate="darkFadeIn"'),
                ('.hero', 'data-animate="darkFadeIn"'),
                ('.feature', 'data-animate="darkGlow"'),
                ('.card', 'data-animate="darkGlow"'),
                ('button', 'data-animate="darkFadeIn"')
            ]
        }
    }
    
    # Default to minimal if theme not found
    if theme not in theme_animations:
        theme = 'minimal'
    
    animation_config = theme_animations[theme]
    
    # Add CSS animations to existing <style> tag or create new one
    if '<style>' in content:
        # Insert before closing </style>
        content = content.replace('</style>', f"{animation_config['css']}\n</style>")
    else:
        # Add new style block in head
        if '</head>' in content:
            content = content.replace('</head>', f"<style>{animation_config['css']}</style>\n</head>")
    
    # Add data-animate attributes to appropriate elements
    for selector, attribute in animation_config['attributes']:
        # Add to elements that don't already have data-animate
        if selector.startswith('.'):
            # Class selector
            class_name = selector[1:]
            pattern = f'class="([^"]*{class_name}[^"]*)"(?![^<]*data-animate)'
            content = re.sub(pattern, f'class="\\1" {attribute}', content)
        else:
            # Element selector
            pattern = f'<{selector}([^>]*)(?<!data-animate="[^"]*")>'
            content = re.sub(pattern, f'<{selector}\\1 {attribute}>', content)
    
    # Add JavaScript for IntersectionObserver
    animation_js = '''
    // Animation controller
    document.addEventListener('DOMContentLoaded', function() {
        const animatedElements = document.querySelectorAll('[data-animate]');
        
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const animationType = element.getAttribute('data-animate');
                    element.classList.add(`animate-${animationType}`);
                    animationObserver.unobserve(element);
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(el => animationObserver.observe(el));
    });
    '''
    
    # Add JavaScript before closing </body> tag
    if '</body>' in content:
        content = content.replace('</body>', f"<script>{animation_js}</script>\n</body>")
    
    return content

def remove_animations_from_content(content: str) -> str:
    """Remove all animation code from content (used by edit mode)"""
    original_content = content  # Backup original content
    
    # Remove data-animate attributes
    if 'data-animate=' in content:
        content = re.sub(r'\s*data-animate="[^"]*"', '', content)
    
    # Remove animation-specific class names from class attributes
    if 'animate-' in content or 'fadeIn' in content or 'slideUp' in content:
        content = re.sub(r'class="([^"]*)\s*(animate-[\w-]+|fadeInUp|slideDown|countUp|fadeInStagger|bounce|pulse)\s*([^"]*)"', 
                        r'class="\1 \3"', content)
        content = re.sub(r'class="\s+"', 'class=""', content)  # Clean up empty spaces
        content = re.sub(r'class=""', '', content)  # Remove empty class attributes
    
    # Remove ONLY specific animation CSS (very precise patterns)
    animation_css_patterns = [
        r'@keyframes\s+(?:fadeInUp|slideUp|slideDown|countUp|fadeInStagger|bounce|pulse|darkFadeIn|darkGlow|brutalistSlam|brutalistPop)\s*\{[^}]+\}',  # Only animation keyframes
        r'\.animate-(?:fadeInUp|slideUp|slideDown|countUp|fadeInStagger|bounce|pulse|darkFadeIn|darkGlow|brutalistSlam|brutalistPop)\s*\{[^}]+\}',  # Only .animate-* for animations  
        r'\.(?:fadeInUp|slideUp|slideDown|countUp|fadeInStagger|bounce|pulse|darkFadeIn|darkGlow|brutalistSlam|brutalistPop)\s*\{[^}]+\}',  # Direct animation classes
        r'\.animate-delay-\d+\s*\{[^}]+\}',  # Animation delay classes
        r'\.delay-\d+\s*\{\s*\}',  # Empty delay classes
    ]
    
    for pattern in animation_css_patterns:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove animation-specific JavaScript
    js_patterns_to_remove = [
        r'//\s*Animation.*?(?=\n\s*(?://|</script>|$))',  # Animation comments
        r'const\s+animationObserver\s*=\s*new\s+IntersectionObserver\([^;]+\);',  # Observer creation
        r'document\.querySelectorAll\(\s*[\'\"]\[data-animate\][\'\"]\s*\)\.forEach\([^}]+\}\);',  # Animation setup
        r'observer\.observe\([^)]*\);',  # Observer observe calls
        r'function\s+initAnimations\s*\([^)]*\)\s*\{[^}]+\}',  # Animation functions
        r'initAnimations\(\);',  # Function calls
        r'document\.addEventListener\(\s*[\'"]DOMContentLoaded[\'"][^}]*animationObserver[^}]*\}\);',  # DOM ready handlers with animations
    ]
    
    for pattern in js_patterns_to_remove:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up whitespace and empty blocks
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    content = re.sub(r'<style[^>]*>\s*</style>', '', content)
    content = re.sub(r'<script[^>]*>\s*</script>', '', content)
    
    # Verify we didn't break the page structure
    if '<html' not in content or '<body' not in content:
        return original_content
        
    return content

def extract_page_context(file_path: str) -> Dict[str, Any]:
    """Extract metadata and context from existing landing page"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        context = {
            'framework': 'react' if file_path.endswith('.jsx') else 'html',
            'sections': [],
            'theme': 'minimal',  # Default
            'other_sections': []
        }
        
        # Extract sections using markers
        section_patterns = [
            r'<!-- START: (\w+) -->(.*?)<!-- END: \1 -->',
            r'<!-- SECTION: (\w+) -->(.*?)<!-- END SECTION: \1 -->'
        ]
        
        sections = []
        for pattern in section_patterns:
            found = re.findall(pattern, content, re.DOTALL)
            sections.extend(found)
        
        for section_name, _ in sections:
            context['sections'].append(section_name)
        
        # Additional header/navigation detection
        if re.search(r'<nav[^>]*>', content) and not any('header' in s.lower() or 'nav' in s.lower() for s in context['sections']):
            context['sections'].append('header')
        
        # Look for explicit header tags
        header_tags = re.findall(r'<header[^>]+id=["\']([^"\']+)["\']', content)
        context['sections'].extend(header_tags)
        
        # Enhanced theme detection using new system
        context['theme'] = detect_theme_from_content(content)
            
        return context
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not extract context from {file_path}: {e}[/yellow]")
        return {'framework': 'html', 'sections': [], 'theme': 'minimal', 'other_sections': []}

def remove_forms_surgically(content: str) -> str:
    """Remove all forms from HTML content without altering anything else"""
    import re
    
    # Remove form elements and their content
    # This regex matches <form...>...</form> including nested content
    form_pattern = r'<form[^>]*>.*?</form>'
    content = re.sub(form_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove standalone contact sections that are only forms
    # Look for contact sections that only contain form elements
    contact_section_pattern = r'<!-- START: contact -->\s*<section[^>]*id=["\']contact["\'][^>]*>.*?</section>\s*<!-- END: contact -->'
    
    def check_contact_section(match):
        section_content = match.group(0)
        # If the section only contains form-related content, remove it
        # Otherwise, just remove the form from within it
        section_inner = re.search(r'<section[^>]*>(.*?)</section>', section_content, re.DOTALL)
        if section_inner:
            inner_content = section_inner.group(1)
            # Remove forms from inner content
            inner_without_forms = re.sub(r'<form[^>]*>.*?</form>', '', inner_content, flags=re.DOTALL | re.IGNORECASE)
            # Remove empty divs and wrapper elements
            inner_without_forms = re.sub(r'<div[^>]*>\s*</div>', '', inner_without_forms, flags=re.DOTALL)
            inner_without_forms = inner_without_forms.strip()
            
            # If nothing meaningful left, remove the entire section
            if not inner_without_forms or len(inner_without_forms.strip()) < 50:
                return ''
            else:
                # Keep section but without forms
                return section_content.replace(inner_content, inner_without_forms)
        return section_content
    
    content = re.sub(contact_section_pattern, check_contact_section, content, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up extra whitespace/newlines left by form removal
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    return content

def insert_form_surgically(content: str, theme: str, form_type: str = 'contact', fields: List[str] = None, cta_text: str = "Send Message") -> str:
    """Insert a form into HTML content while matching the existing theme"""
    if fields is None:
        fields = ['name', 'email', 'message']
    
    # Generate theme-appropriate form HTML
    form_html = generate_theme_form_html(theme, form_type, fields, cta_text)
    
    # Find the best place to insert the form
    # 1. If there's already a contact section, add form there
    # 2. If there's a pricing section, add form after it
    # 3. If there's a footer, add form before it
    # 4. Otherwise, add at the end before closing body
    
    contact_section_pattern = r'(<!-- START: contact -->.*?<!-- END: contact -->)'
    pricing_section_pattern = r'(<!-- END: pricing -->\s*)'
    footer_pattern = r'(<footer[^>]*>)'
    closing_body_pattern = r'(</body>)'
    
    # Try to insert in contact section first
    if re.search(r'<!-- START: contact -->', content, re.IGNORECASE):
        # Add form inside existing contact section
        def replace_contact_section(match):
            section_content = match.group(0)
            # Insert form before the closing of the section
            section_content = re.sub(r'(</div>\s*</section>\s*<!-- END: contact -->)', 
                                   f'{form_html}\n\\1', section_content)
            return section_content
        
        content = re.sub(contact_section_pattern, replace_contact_section, content, flags=re.DOTALL | re.IGNORECASE)
    
    # If no contact section, try after pricing
    elif re.search(r'<!-- END: pricing -->', content, re.IGNORECASE):
        contact_section = f'''
<!-- START: contact -->
<section id="contact" class="py-20 bg-gray-800">
<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
<div class="text-center mb-16">
<h2 class="text-3xl md:text-5xl font-bold mb-4 text-white">Get Started Today</h2>
<p class="text-xl text-gray-300 max-w-3xl mx-auto">Ready to get started? Contact us and discover how our solution can benefit you.</p>
</div>
{form_html}
</div>
</section>
<!-- END: contact -->
'''
        content = re.sub(pricing_section_pattern, f'\\1\n{contact_section}\n', content, flags=re.IGNORECASE)
    
    # If no pricing, try before footer
    elif re.search(r'<footer', content, re.IGNORECASE):
        contact_section = f'''
<!-- START: contact -->
<section id="contact" class="py-20 bg-gray-800">
<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
<div class="text-center mb-16">
<h2 class="text-3xl md:text-5xl font-bold mb-4 text-white">Get Started Today</h2>
<p class="text-xl text-gray-300 max-w-3xl mx-auto">Ready to get started? Contact us and discover how our solution can benefit you.</p>
</div>
{form_html}
</div>
</section>
<!-- END: contact -->

'''
        content = re.sub(footer_pattern, f'{contact_section}\\1', content, flags=re.IGNORECASE)
    
    # Last resort - add before closing body
    else:
        contact_section = f'''
<!-- START: contact -->
<section id="contact" class="py-20 bg-gray-800">
<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
<div class="text-center mb-16">
<h2 class="text-3xl md:text-5xl font-bold mb-4 text-white">Get Started Today</h2>
<p class="text-xl text-gray-300 max-w-3xl mx-auto">Ready to get started? Contact us and discover how our solution can benefit you.</p>
</div>
{form_html}
</div>
</section>
<!-- END: contact -->

'''
        content = re.sub(closing_body_pattern, f'{contact_section}\\1', content, flags=re.IGNORECASE)
    
    return content

def generate_theme_form_html(theme: str, form_type: str, fields: List[str], cta_text: str) -> str:
    """Generate form HTML that matches the specified theme"""
    
    # Theme-specific styles
    theme_styles = {
        'dark': {
            'container': 'bg-gray-900 p-8 rounded-xl border border-gray-700',
            'input': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'textarea': 'w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'label': 'block text-sm font-medium text-gray-300 mb-2',
            'button': 'bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-blue-600/25'
        },
        'minimal': {
            'container': 'bg-white p-8 rounded-lg shadow-lg border border-gray-200',
            'input': 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'textarea': 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'label': 'block text-sm font-medium text-gray-700 mb-2',
            'button': 'bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-md transition-colors'
        },
        'brutalist': {
            'container': 'bg-white p-8 border-4 border-black shadow-[8px_8px_0px_#000]',
            'input': 'w-full px-4 py-3 border-4 border-black bg-white text-black font-mono shadow-[4px_4px_0px_#000] focus:outline-none',
            'textarea': 'w-full px-4 py-3 border-4 border-black bg-white text-black font-mono resize-none shadow-[4px_4px_0px_#000] focus:outline-none',
            'label': 'block text-sm font-black text-black uppercase mb-2',
            'button': 'bg-yellow-400 hover:translate-x-1 hover:translate-y-1 hover:shadow-none text-black font-black uppercase py-4 px-8 border-4 border-black shadow-[4px_4px_0px_#000] transition-transform'
        },
        'corporate': {
            'container': 'bg-white p-8 rounded-lg shadow-xl border border-gray-300',
            'input': 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
            'textarea': 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
            'label': 'block text-sm font-semibold text-gray-700 mb-2',
            'button': 'bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-md transition-colors'
        }
    }
    
    # Default to minimal if theme not found
    if theme not in theme_styles:
        theme = 'minimal'
    
    styles = theme_styles[theme]
    
    # Generate field inputs
    field_inputs = []
    
    for field in fields:
        if field == 'name':
            field_inputs.append(f'''
<div>
<label for="name" class="{styles['label']}">Name</label>
<input type="text" id="name" name="name" required class="{styles['input']}" placeholder="Your full name">
</div>''')
        elif field == 'email':
            field_inputs.append(f'''
<div>
<label for="email" class="{styles['label']}">Email</label>
<input type="email" id="email" name="email" required class="{styles['input']}" placeholder="your.email@example.com">
</div>''')
        elif field == 'phone':
            field_inputs.append(f'''
<div>
<label for="phone" class="{styles['label']}">Phone</label>
<input type="tel" id="phone" name="phone" class="{styles['input']}" placeholder="(555) 123-4567">
</div>''')
        elif field == 'company':
            field_inputs.append(f'''
<div>
<label for="company" class="{styles['label']}">Company</label>
<input type="text" id="company" name="company" class="{styles['input']}" placeholder="Your company name">
</div>''')
        elif field == 'website':
            field_inputs.append(f'''
<div>
<label for="website" class="{styles['label']}">Website</label>
<input type="url" id="website" name="website" class="{styles['input']}" placeholder="https://yourwebsite.com">
</div>''')
        elif field == 'subject':
            field_inputs.append(f'''
<div>
<label for="subject" class="{styles['label']}">Subject</label>
<input type="text" id="subject" name="subject" class="{styles['input']}" placeholder="How can we help?">
</div>''')
        elif field == 'message':
            field_inputs.append(f'''
<div class="md:col-span-2">
<label for="message" class="{styles['label']}">Message</label>
<textarea id="message" name="message" rows="6" required class="{styles['textarea']}" placeholder="Tell us about your project or ask any questions..."></textarea>
</div>''')
    
    # Arrange fields in a grid
    grid_classes = "grid-cols-1" if len([f for f in fields if f != 'message']) <= 1 else "grid-cols-1 md:grid-cols-2"
    
    form_html = f'''
<div class="{styles['container']}">
<form action="#" method="POST" class="space-y-6">
<div class="grid {grid_classes} gap-6">
{"".join(field_inputs)}
</div>

<div class="text-center">
<button type="submit" class="{styles['button']}">
{cta_text}
</button>
</div>
</form>
</div>'''
    
    return form_html

def update_design_analysis_for_regen(output_dir: str, sections_regenerated: List[str], product_desc: str, usage_stats: Dict[str, Any]) -> None:
    """Update design_analysis.json file with regeneration information"""
    analysis_file = os.path.join(output_dir, 'design_analysis.json')
    
    try:
        # Load existing analysis or create new one
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis_data = json.load(f)
        else:
            analysis_data = {}
        
        # Update regeneration history
        if 'regeneration_history' not in analysis_data:
            analysis_data['regeneration_history'] = []
        
        # Add current regeneration record
        regen_record = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sections_updated': sections_regenerated,
            'product_description': product_desc,
            'usage_stats': usage_stats,
            'method': 'regen_command'
        }
        
        analysis_data['regeneration_history'].append(regen_record)
        
        # Update last_updated timestamp
        analysis_data['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Update sections list
        if 'sections' not in analysis_data:
            analysis_data['sections'] = []
        
        # Add regenerated sections to sections list if not already present
        for section in sections_regenerated:
            if section not in analysis_data['sections']:
                analysis_data['sections'].append(section)
        
        # Update product understanding if provided
        if product_desc and product_desc != "Landing page product":
            if 'product_understanding' not in analysis_data:
                analysis_data['product_understanding'] = {}
            
            analysis_data['product_understanding']['description'] = product_desc
            analysis_data['product_understanding']['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save updated analysis
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        console.print(f"[cyan]📊 Updated design analysis: {analysis_file}[/cyan]")
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not update design analysis: {e}[/yellow]")


def replace_sections_in_file(file_path: str, new_sections_content: str, sections_to_replace: List[str]) -> bool:
    """Replace specific sections in the landing page file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        updated_content = original_content
        
        # Extract new sections from generated content
        new_section_pattern = r'<!-- START: (\w+) -->(.*?)<!-- END: \1 -->'
        new_sections = dict(re.findall(new_section_pattern, new_sections_content, re.DOTALL))
        
        # Replace each requested section
        for section_name in sections_to_replace:
            section_key = section_name.lower()
            if section_key in new_sections:
                new_section_code = f'<!-- START: {section_key} -->{new_sections[section_key]}<!-- END: {section_key} -->'
                
                # Try multiple patterns to find existing section
                patterns_to_try = [
                    f'<!-- START: {section_key} -->.*?<!-- END: {section_key} -->',
                    f'<!-- SECTION: {section_key} -->.*?<!-- END SECTION: {section_key} -->',
                    f'<!-- {section_name.title()} Section -->.*?(?=<!-- .* Section -->|</body>|$)',
                    f'<section[^>]*class="[^"]*{section_key}[^"]*"[^>]*>.*?</section>'
                ]
                
                # Add special patterns for header/navigation sections
                if section_key in ['header', 'nav', 'navigation']:
                    header_patterns = [
                        r'<nav[^>]*class="[^"]*fixed[^"]*"[^>]*>.*?</nav>',  # Fixed nav
                        r'<nav[^>]*>.*?</nav>',                              # Any nav tag
                        r'<header[^>]*>.*?</header>',                        # Any header tag
                    ]
                    patterns_to_try.extend(header_patterns)
                
                section_replaced = False
                for pattern in patterns_to_try:
                    if re.search(pattern, updated_content, re.DOTALL | re.IGNORECASE):
                        updated_content = re.sub(pattern, new_section_code, updated_content, flags=re.DOTALL | re.IGNORECASE)
                        section_replaced = True
                        console.print(f"[green]✓ Replaced {section_name} section using pattern match[/green]")
                        break
                
                if not section_replaced:
                    # Section doesn't exist, append it (could be a new section)
                    # Try to find a good insertion point (before closing body tag)
                    if '</body>' in updated_content:
                        # Insert before </body> and after </script> if it exists
                        script_end = updated_content.rfind('</script>')
                        body_end = updated_content.rfind('</body>')
                        
                        if script_end > 0 and script_end < body_end:
                            # Insert after </script> but before </body>
                            insertion_point = script_end + len('</script>')
                            updated_content = updated_content[:insertion_point] + f'\n{new_section_code}\n' + updated_content[insertion_point:]
                        else:
                            # Insert just before </body>
                            updated_content = updated_content.replace('</body>', f'{new_section_code}\n</body>')
                    else:
                        updated_content += f'\n{new_section_code}'
                    
                    console.print(f"[yellow]⚠ Added new {section_name} section (original not found)[/yellow]")
        
        # Clean up any duplicate sections that might have been created
        for section_name in sections_to_replace:
            section_key = section_name.lower()
            # Find all instances of this section and keep only the first one
            section_pattern = f'<!-- START: {section_key} -->.*?<!-- END: {section_key} -->'
            matches = list(re.finditer(section_pattern, updated_content, re.DOTALL))
            if len(matches) > 1:
                # Keep the first match, remove the rest
                for i in range(len(matches) - 1, 0, -1):  # Remove from end to beginning
                    match = matches[i]
                    updated_content = updated_content[:match.start()] + updated_content[match.end():]
                console.print(f"[yellow]🧹 Cleaned up duplicate {section_name} sections[/yellow]")
        
        # Write updated content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error updating file {file_path}: {e}[/red]")
        return False

@app.command()
def init():
    """Initialize CCUX by installing Playwright browsers"""
    console.print("[bold blue]🚀 Initializing CCUX...[/bold blue]")
    
    try:
        # Install Playwright browsers
        with Status("[bold green]Installing Playwright browsers...", console=console):
            result = subprocess.run(
                ["python", "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                check=True
            )
        
        console.print("[bold green]✅ CCUX initialized successfully![/bold green]")
        console.print("\nYou can now run:")
        console.print("  [bold]ccux gen --desc 'Your product description'[/bold]")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to initialize CCUX: {e.stderr}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error during initialization: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def gen(
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Product description"),
    desc_file: Optional[str] = typer.Option(None, "--desc-file", help="Path to file containing product description (supports .txt and .pdf files)"),
    urls: Optional[List[str]] = typer.Option(None, "--url", "-u", help="Reference URLs (can be used multiple times)"),
    framework: Optional[str] = typer.Option(None, "--framework", "-f", help="Output framework (html|react)"),
    theme: Optional[str] = typer.Option(None, "--theme", "-t", help=f"Design theme ({'/'.join(get_theme_choices())})"),
    no_design_thinking: bool = typer.Option(False, "--no-design-thinking", help="Skip design thinking process"),
    include_forms: bool = typer.Option(False, "--include-forms", help="Include contact forms in the landing page"),
    analyze_images: bool = typer.Option(True, "--analyze-images/--no-analyze-images", help="Enable visual analysis of competitor screenshots (uses more tokens)"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Generate a conversion-optimized landing page
    
    Run without arguments for interactive mode, or provide --desc for direct usage.
    Use --desc-file to load description from a text or PDF file for longer copy.
    """
    
    # Load configuration
    config = Config()
    
    # Handle desc from file or interactive mode
    if desc_file:
        # Read description from file
        if not os.path.exists(desc_file):
            console.print(f"[red]❌ Description file not found: {desc_file}[/red]")
            raise typer.Exit(1)
        try:
            # Check file extension to determine how to read
            file_ext = os.path.splitext(desc_file.lower())[1]
            
            if file_ext == '.pdf':
                # Read PDF file
                import PyPDF2
                with open(desc_file, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    desc = ""
                    for page in pdf_reader.pages:
                        desc += page.extract_text() + "\n"
                    desc = desc.strip()
                console.print(f"[green]📄 PDF description loaded from: {desc_file}[/green]")
            else:
                # Read text file
                with open(desc_file, 'r', encoding='utf-8') as f:
                    desc = f.read().strip()
                console.print(f"[green]📄 Description loaded from: {desc_file}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error reading description file: {e}[/red]")
            raise typer.Exit(1)
    elif not desc:
        # Interactive mode - prompt for inputs
        console.print("[bold blue]🎨 Interactive Mode - CCUX Generator[/bold blue]")
        console.print("Let's create your landing page step by step.\n")
        
        # Get product description with validation loop
        while True:
            desc = Prompt.ask(
                "[bold]What product/service would you like to create a landing page for?[/bold]",
                default="",
                show_default=False
            )
            if desc and desc.strip():
                break
            console.print("[red]❌ Product description is required. Please provide a description to continue.[/red]")
        
        # Optional URLs
        if not urls:
            url_input = Prompt.ask(
                "[bold]Reference URLs (optional)[/bold]\nEnter competitor or inspiration websites (comma-separated)",
                default="",
                show_default=False
            )
            if url_input.strip():
                # Split by comma and filter valid URLs
                url_list = [u.strip() for u in url_input.split(',') if u.strip().startswith('http')]
                if url_list:
                    urls = url_list
        
        # Framework selection
        if not framework:
            framework_choices = ['html', 'react']
            framework = Prompt.ask(
                "[bold]Output framework[/bold]",
                choices=framework_choices,
                default='html'
            )
        
        # Theme selection with descriptions
        if not theme:
            theme_choices = get_theme_choices()
            console.print("\n[bold]Available themes:[/bold]")
            for i, choice in enumerate(theme_choices, 1):
                desc = get_theme_description(choice)
                console.print(f"  {i}. [cyan]{choice}[/cyan]: {desc[:60]}...")
            
            theme = Prompt.ask(
                "\n[bold]Select design theme[/bold]",
                choices=theme_choices,
                default='minimal'
            )
        
        # Design thinking process option
        if not no_design_thinking:
            use_design_thinking = Confirm.ask(
                "[bold]Run full design thinking process?[/bold]\n"
                "This includes competitor research, user analysis, and wireframing (takes longer but better results)",
                default=True
            )
            no_design_thinking = not use_design_thinking
        
        console.print(f"\n[bold green]✅ Configuration complete![/bold green]")
        console.print(f"Product: [cyan]{desc}[/cyan]")
        if urls:
            console.print(f"References: [cyan]{', '.join(urls)}[/cyan]")
        console.print(f"Framework: [cyan]{framework}[/cyan] | Theme: [cyan]{theme}[/cyan]")
        console.print(f"Design thinking: [cyan]{'Yes' if not no_design_thinking else 'No'}[/cyan]\n")
    
    # Additional validation - ensure desc is not empty even if passed as argument
    if not desc or not desc.strip():
        console.print("[red]❌ Product description is required. Cannot generate landing page without a product description.[/red]")
        console.print("[dim]Use --desc 'Your product description' or run without arguments for interactive mode.[/dim]")
        raise typer.Exit(1)
    
    # Summarize description if too long
    if desc:
        desc = summarize_long_description(desc)
    
    # Override config with CLI arguments
    framework = framework or config.get('framework', 'html')
    theme = theme or config.get('theme', 'minimal')
    output_dir = output_dir or get_next_available_output_dir()
    sections = config.get('sections', ['hero', 'features', 'pricing', 'footer'])
    
    # Validate inputs
    valid_frameworks = ['html', 'react']
    valid_themes = get_theme_choices()
    
    if framework not in valid_frameworks:
        console.print(f"[red]❌ Invalid framework. Must be one of: {', '.join(valid_frameworks)}[/red]")
        raise typer.Exit(1)
    
    if theme not in valid_themes:
        console.print(f"[red]❌ Invalid theme. Must be one of: {', '.join(valid_themes)}[/red]")
        raise typer.Exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    brand_display = extract_brand_name(desc)
    console.print(f"[bold blue]🎨 Generating landing page for: {brand_display}[/bold blue]")
    console.print(f"Framework: [green]{framework}[/green] | Theme: [green]{theme}[/green]")
    
    if no_design_thinking:
        # Simple mode - direct generation (no screenshots needed)
        console.print("\n[bold yellow]⚡ Quick generation mode (no design thinking, no image analysis)[/bold yellow]")
        
        # Generate directly without any screenshot capture
        prompt = landing_prompt(desc, framework, theme, sections, include_forms=include_forms)
        output, stats = run_claude_with_progress(prompt, "Generating landing page...")
        
        # Save output
        if framework == 'react':
            # Save React component
            with open(os.path.join(output_dir, 'App.jsx'), 'w') as f:
                f.write(strip_code_blocks(output))
            
            # Create minimal index.html shell
            html_shell = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{desc}</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel" src="App.jsx"></script>
</body>
</html>'''
            
            with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                f.write(html_shell)
        else:
            # Save HTML
            with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                f.write(strip_code_blocks(output))
        
        # Save minimal design analysis for cost tracking
        fast_analysis = {
            'generation_mode': 'fast',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'product_description': desc,
            'theme': theme,
            'framework': framework,
            'total_usage': {
                'input_tokens': stats.get('input_tokens', 0),
                'output_tokens': stats.get('output_tokens', 0),
                'cost': stats.get('cost', 0.0)
            },
            'generation_stats': stats
        }
        
        try:
            with open(os.path.join(output_dir, 'design_analysis.json'), 'w') as f:
                json.dump(fast_analysis, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not save cost tracking data: {e}[/yellow]")

        console.print(f"[bold green]✅ Landing page generated successfully![/bold green]")
        console.print(f"📁 Output saved to: [bold]{output_dir}[/bold]")
        
        # Display usage stats  
        if stats:
            console.print(f"\n[dim]Tokens: {stats.get('input_tokens', 0)} in, {stats.get('output_tokens', 0)} out | Cost: ~${stats.get('cost', 0.0):.4f}[/dim]")
        
    else:
        # Full design thinking process
        console.print("\n[bold green]🧠 Running comprehensive design thinking process...[/bold green]")
        
        try:
            # Phase 1: Reference Discovery (only if image analysis is enabled)
            ref_urls = []
            if analyze_images:
                console.print("\n[bold]Phase 1: Reference Discovery[/bold]")
                prompt = reference_discovery_prompt(desc)
                refs_output, _ = run_claude_with_progress(prompt, "Discovering competitor references...")
                
                # Parse reference URLs
                for line in refs_output.split('\n'):
                    if '–' in line and 'http' in line:
                        try:
                            url_part = line.split('–')[1].strip()
                            if url_part.startswith('http'):
                                ref_urls.append(url_part.split()[0])
                        except:
                            continue
                
                # Add user-provided URLs if available
                if urls:
                    # Insert user URLs at the beginning, maintaining order
                    for i, user_url in enumerate(reversed(urls)):
                        ref_urls.insert(0, user_url)
                
                # Limit to 3 references for performance
                ref_urls = ref_urls[:3]
            else:
                console.print("\n[bold]Phase 1: Reference Discovery (Skipped - Image Analysis Disabled)[/bold]")
                console.print("ℹ️  Skipping reference discovery to save tokens")
                
                # Still add user-provided URLs if available, but limit them 
                if urls:
                    ref_urls = urls[:3]
            
            # 🔍 Debug / confirmation log
            if ref_urls:
                console.print("\n[bold]Discovered Reference URLs:[/bold]")
                for i, u in enumerate(ref_urls, 1):
                    console.print(f"  {i}. {u}", style="cyan")

            
            if not ref_urls:
                console.print("[yellow]⚠️  No reference URLs found. Continuing without screenshots.[/yellow]")
                screenshot_refs = []
            elif not analyze_images:
                console.print(f"\n[bold]Phase 2: Screenshot Capture (Skipped - Image Analysis Disabled)[/bold]")
                console.print("ℹ️  Skipping screenshot capture to save tokens")
                screenshot_refs = []
            else:
                # Phase 2: Screenshot Capture
                console.print(f"\n[bold]Phase 2: Capturing {len(ref_urls)} reference screenshots[/bold]")
                screenshot_results = capture_multiple_references(ref_urls, output_dir)
                screenshot_refs = [(url, screenshot_path) for url, _, screenshot_path in screenshot_results]
            
            # Phase 3: Product Analysis
            console.print("\n[bold]Phase 3: Product Analysis[/bold]")
            prompt = deep_product_understanding_prompt(desc)
            product_output, _ = run_claude_with_progress(prompt, "Analyzing product positioning...")
            product_understanding = safe_json_parse(product_output)
            
            # Phase 4: UX Research  
            ux_analysis = {}
            if screenshot_refs and analyze_images:
                console.print("\n[bold]Phase 4: UX Research (Visual Analysis)[/bold]")
                screenshot_paths = [screenshot_path for url, screenshot_path in screenshot_refs]
                prompt = ux_analysis_prompt(desc, screenshot_paths)
                ux_output, _ = run_claude_with_progress(prompt, "Analyzing competitor UX patterns...", enable_image_analysis=True)
                ux_analysis = safe_json_parse(ux_output)
            elif screenshot_refs and not analyze_images:
                console.print("\n[bold]Phase 4: UX Research (Skipped - Visual Analysis Disabled)[/bold]")
                console.print("ℹ️  Screenshots captured but visual analysis disabled to save tokens")
                console.print("   Use --analyze-images flag to enable competitor visual analysis")
            
            # Phase 5: Empathy & User Research
            console.print("\n[bold]Phase 5: User Empathy Mapping[/bold]")
            prompt = empathize_prompt(desc, product_understanding, ux_analysis)
            empathy_output, _ = run_claude_with_progress(prompt, "Mapping user empathy...")
            user_research = safe_json_parse(empathy_output)
            
            # Phase 6: Define Site Flow
            console.print("\n[bold]Phase 6: Defining Site Flow[/bold]")
            prompt = define_prompt(desc, user_research)
            define_output, _ = run_claude_with_progress(prompt, "Defining site architecture...")
            site_flow = safe_json_parse(define_output)
            
            # Phase 7: Content Strategy
            console.print("\n[bold]Phase 7: Content Strategy[/bold]")
            prompt = ideate_prompt(desc, user_research, site_flow)
            strategy_output, _ = run_claude_with_progress(prompt, "Developing content strategy...")
            content_strategy = safe_json_parse(strategy_output)
            
            # Phase 8: Wireframes (depends on content strategy)
            console.print("\n[bold]Phase 8: Wireframes[/bold]")
            wireframe_prompt_call = wireframe_prompt(desc, content_strategy, site_flow)
            wireframe_output, _ = run_claude_with_progress(wireframe_prompt_call, "Creating wireframes...")
            wireframes = safe_json_parse(wireframe_output)
            
            # Phase 9: Design System
            console.print("\n[bold]Phase 9: Design System[/bold]")
            design_prompt_call = design_system_prompt(desc, wireframes, content_strategy, theme)
            design_output, _ = run_claude_with_progress(design_prompt_call, "Building design system...")
            design_system = safe_json_parse(design_output)
            
            # Phase 10: Hi-Fi Design
            console.print("\n[bold]Phase 10: Hi-Fi Design[/bold]")
            prompt = high_fidelity_design_prompt(desc, design_system, wireframes, content_strategy)
            hifi_output, _ = run_claude_with_progress(prompt, "Creating high-fidelity design...")
            hifi_design = safe_json_parse(hifi_output)
            
            # Phase 11: Copy Generation
            console.print("\n[bold]Phase 11: Copy Generation[/bold]")
            prompt = prototype_prompt(desc, content_strategy, design_system, wireframes)
            copy_output, _ = run_claude_with_progress(prompt, "Generating final copy...")
            final_copy = safe_json_parse(copy_output)
            
            # Phase 12: Implementation
            console.print("\n[bold]Phase 12: Code Implementation[/bold]")
            screenshot_path = screenshot_refs[0][1] if screenshot_refs else None
            design_data = {
                'design_system': design_system,
                'ux_analysis': ux_analysis,
                'wireframes': wireframes,
                'content_strategy': content_strategy
            }
            # Implementation with error detection and retry
            max_attempts = 2
            code_output = None
            
            for attempt in range(max_attempts):
                try:
                    attempt_desc = "Implementing landing page..." if attempt == 0 else f"Regenerating landing page (attempt {attempt + 1})..."
                    prompt = implementation_prompt(desc, final_copy, framework, theme, design_data, include_forms=include_forms)
                    code_output, _ = run_claude_with_progress(prompt, attempt_desc)
                    
                    # Validate the output
                    cleaned_output = strip_code_blocks(code_output)
                    if validate_html_output(cleaned_output) or framework == 'react':
                        break
                    else:
                        if attempt < max_attempts - 1:
                            console.print("[yellow]⚠️  Generated output appears to be an error message. Retrying...[/yellow]")
                            continue
                        else:
                            console.print("[red]❌ Failed to generate valid output after multiple attempts[/red]")
                            
                except Exception as e:
                    if attempt < max_attempts - 1:
                        console.print(f"[yellow]⚠️  Implementation failed: {e}. Retrying...[/yellow]")
                        continue
                    else:
                        raise e
            
            # Save all outputs
            analysis_data = {
                'product_understanding': product_understanding,
                'ux_analysis': ux_analysis,
                'user_research': user_research,
                'site_flow': site_flow,
                'content_strategy': content_strategy,
                'wireframes': wireframes,
                'design_system': design_system,
                'hifi_design': hifi_design,
                'final_copy': final_copy
            }
            
            with open(os.path.join(output_dir, 'design_analysis.json'), 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            # Save code output with final validation
            cleaned_code = strip_code_blocks(code_output)
            
            if framework == 'react':
                with open(os.path.join(output_dir, 'App.jsx'), 'w') as f:
                    f.write(cleaned_code)
                
                html_shell = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{desc}</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel" src="App.jsx"></script>
</body>
</html>'''
                
                with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                    f.write(html_shell)
            else:
                # Final validation before writing HTML
                if not validate_html_output(cleaned_code):
                    console.print("[red]⚠️  Warning: Generated HTML may contain errors[/red]")
                    # Save the raw output for debugging
                    with open(os.path.join(output_dir, 'debug_output.txt'), 'w') as f:
                        f.write(code_output)
                    console.print(f"[yellow]Debug output saved to: {output_dir}/debug_output.txt[/yellow]")
                
                with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                    f.write(cleaned_code)
            
            console.print(f"\n[bold green]✅ Comprehensive landing page generated successfully![/bold green]")
            console.print(f"📁 Output saved to: [bold]{output_dir}[/bold]")
            console.print(f"📊 Design analysis saved to: [bold]{output_dir}/design_analysis.json[/bold]")
            
        except Exception as e:
            console.print(f"[red]❌ Error during design thinking process: {e}[/red]")
            raise typer.Exit(1)
    
    # Show preview instructions
    console.print("\n[bold cyan]🌐 Preview your landing page:[/bold cyan]")
    console.print(f"  [bold]cd {output_dir}[/bold]")
    console.print("  [bold]python -m http.server 3000[/bold]")
    console.print("  Then open [bold]http://localhost:3000[/bold] in your browser")

def _regenerate_sections_internal(
    sections_to_regenerate: List[str],
    target_file: str,
    output_dir: str,
    description: Optional[str] = None
) -> bool:
    """Internal function to regenerate sections - can be called from CLI or interactive interface
    
    Args:
        sections_to_regenerate: List of section names to regenerate
        target_file: Path to the HTML/React file to modify
        output_dir: Directory containing the project files  
        description: Product description (auto-detected if None)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Extract context from existing file
        context = extract_page_context(target_file)
        framework = context['framework']
        theme = context['theme']
        existing_sections = context['sections']
        
        console.print(f"Detected: [green]{framework}[/green] | Theme: [green]{theme}[/green] | Sections: [cyan]{', '.join(existing_sections)}[/cyan]")
        
        # Get product description
        desc = description
        if not desc:
            # Try to extract from existing metadata or config
            if os.path.exists(os.path.join(output_dir, 'design_analysis.json')):
                try:
                    with open(os.path.join(output_dir, 'design_analysis.json'), 'r') as f:
                        analysis = json.load(f)
                        # Try multiple possible locations for the description
                        desc = (
                            analysis.get('project_metadata', {}).get('product_description') or
                            analysis.get('product_understanding', {}).get('problem') or
                            analysis.get('product_description') or
                            'Landing page product'
                        )
                        if desc and desc != 'Landing page product':
                            desc = desc[:200]  # Limit length but allow more than 100 chars
                except:
                    pass
            
            if not desc:
                while True:
                    desc = Prompt.ask(
                        "[bold]What is this landing page for?[/bold]",
                        default="",
                        show_default=False
                    )
                    if desc and desc.strip():
                        break
                    console.print("[red]❌ Product description is required to regenerate sections properly.[/red]")
        
        # Final validation to ensure we have a meaningful description
        if not desc or not desc.strip() or desc.strip().lower() in ['landing page product', 'product landing page']:
            console.print("[red]❌ A meaningful product description is required to regenerate sections properly.[/red]")
            console.print("[dim]Please provide a specific description of what this landing page is for.[/dim]")
            return False
        
        console.print(f"Regenerating sections: [bold]{', '.join(sections_to_regenerate)}[/bold]")
        
        # Build context for existing page
        other_sections = [s for s in existing_sections if s not in sections_to_regenerate]
        existing_context = {
            'theme': theme,
            'framework': framework,
            'other_sections': f"Already has: {', '.join(other_sections)}" if other_sections else "No other sections"
        }
        
        # Generate new sections
        prompt = regeneration_prompt(desc, framework, theme, sections_to_regenerate, existing_context)
        new_sections_content, stats = run_claude_with_progress(
            prompt, 
            f"Regenerating {len(sections_to_regenerate)} section(s)..."
        )
        
        # Replace sections in the file
        success = replace_sections_in_file(target_file, new_sections_content, sections_to_regenerate)
        
        if success:
            console.print(f"[bold green]✅ Successfully regenerated {len(sections_to_regenerate)} section(s)![/bold green]")
            console.print(f"📁 Updated file: [bold]{target_file}[/bold]")
            
            # Update design_analysis.json with regeneration info
            update_design_analysis_for_regen(output_dir, sections_to_regenerate, desc, stats)
            
            # Show preview instructions
            console.print(f"\n[bold cyan]🌐 Preview your updated page:[/bold cyan]")
            console.print(f"  [bold]cd {os.path.dirname(target_file)}[/bold]")
            console.print("  [bold]python -m http.server 3000[/bold]")
            console.print("  Then open [bold]http://localhost:3000[/bold] in your browser")
            return True
        else:
            console.print("[red]❌ Failed to update the landing page file[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Error during regeneration: {e}[/red]")
        return False

@app.command()
def regen(
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Section(s) to regenerate (comma-separated)"),
    all: bool = typer.Option(False, "--all", help="Regenerate all sections"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Product description (auto-detected if not provided)"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to landing page file"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Regenerate specific sections of an existing landing page
    
    Examples:
      ccux regen --section hero
      ccux regen --section hero,features
      ccux regen --all
    """
    
    config = Config()
    
    # Find existing landing page files
    if file:
        if not os.path.exists(file):
            console.print(f"[red]❌ File not found: {file}[/red]")
            raise typer.Exit(1)
        target_file = file
        output_dir = os.path.dirname(file) or "."
    else:
        # If no output_dir specified, discover and select project interactively
        if output_dir is None:
            projects = discover_existing_projects()
            selected_dir = select_project_interactively(projects, "regenerate")
            output_dir = selected_dir
        
        found_files = find_landing_page_files(output_dir)
        if not found_files:
            console.print(f"[red]❌ No landing page files found in {output_dir}[/red]")
            console.print("Run [bold]ccux gen[/bold] first to create a landing page")
            raise typer.Exit(1)
        
        # Prefer React if both exist, otherwise use what's available
        if 'react' in found_files:
            target_file = found_files['react']
        else:
            target_file = found_files['html']
    
    console.print(f"[bold blue]🔄 Regenerating sections in: {target_file}[/bold blue]")
    
    # Extract context to determine sections
    context = extract_page_context(target_file)
    existing_sections = context['sections']
    
    # Determine sections to regenerate
    if all:
        sections_to_regen = existing_sections if existing_sections else ['header', 'hero', 'features', 'pricing', 'footer']
    elif section:
        sections_to_regen = [s.strip() for s in section.split(',')]
    else:
        console.print("[red]❌ Must specify --section or --all[/red]")
        console.print("Examples:")
        console.print("  [bold]ccux regen --section hero[/bold]")
        console.print("  [bold]ccux regen --section hero,features[/bold]")
        console.print("  [bold]ccux regen --all[/bold]")
        raise typer.Exit(1)
    
    # Call the internal function
    success = _regenerate_sections_internal(sections_to_regen, target_file, output_dir, desc)
    
    if not success:
        raise typer.Exit(1)

@app.command()
def editgen(
    instruction: str = typer.Argument(..., help="Specific edit instruction (what to change)"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Product description (auto-detected if not provided)"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to landing page file"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    sections: Optional[str] = typer.Option(None, "--sections", "-s", help="Specific sections to focus changes on (comma-separated)")
):
    """Edit specific parts of existing landing page while preserving theme and layout
    
    This command makes targeted edits to your landing page while preserving the overall 
    design theme, layout, and functionality. Only the requested changes are made.
    
    Examples:
      ccux editgen "Change the hero headline to 'Revolutionary AI Platform'"
      ccux editgen "Update the pricing section to show monthly prices" --sections hero,pricing
      ccux editgen "Replace the testimonial with a customer quote from John Doe" --file custom/page.html
    """
    
    config = Config()
    
    # Locate landing page file
    if file:
        target_file = Path(file)
        if not target_file.exists():
            console.print(f"[red]❌ File not found: {file}[/red]")
            raise typer.Exit(1)
        output_dir = str(target_file.parent)
    else:
        # If no output_dir specified, discover and select project interactively
        if output_dir is None:
            projects = discover_existing_projects()
            selected_dir = select_project_interactively(projects, "edit")
            output_dir = selected_dir
            
        # Look for landing page in selected directory
        target_file = Path(output_dir) / 'index.html'
        if not target_file.exists():
            console.print(f"[red]❌ No landing page found in {output_dir}. Run [cyan]ccux gen[/cyan] first[/red]")
            raise typer.Exit(1)
    
    console.print(f"[cyan]📝 Editing: {target_file}[/cyan]")
    console.print(f"[cyan]📝 Edit Instruction: {instruction}[/cyan]")
    
    # Extract context from existing file
    context = extract_page_context(str(target_file))
    
    # Auto-detect product description if not provided
    if not desc:
        try:
            analysis_file = Path(output_dir) / 'design_analysis.json'
            if analysis_file.exists():
                with open(analysis_file, 'r') as f:
                    analysis_data = json.load(f)
                    desc = analysis_data.get('product_description', 'Generated landing page')
                    console.print(f"[green]📄 Using product description from design analysis[/green]")
            else:
                desc = "Generated landing page"
                console.print(f"[yellow]⚠️  No product description found. Using default.[/yellow]")
        except Exception as e:
            desc = "Generated landing page"
            console.print(f"[yellow]⚠️  Could not read design analysis: {e}. Using default description.[/yellow]")
    
    # Parse affected sections if provided
    affected_sections = None
    if sections and isinstance(sections, str) and sections.strip():
        affected_sections = [s.strip() for s in sections.split(',')]
        console.print(f"[cyan]🎯 Focusing on sections: {', '.join(affected_sections)}[/cyan]")
    
    # Generate edit prompt
    framework = context.get('framework', 'html')
    theme = context.get('theme', 'minimal')
    
    console.print(f"[cyan]🎨 Detected theme: {theme} | Framework: {framework}[/cyan]")
    
    try:
        # OPTIMIZATION: Use section-only editing when --sections is specified (much faster)
        if affected_sections:
            console.print(f"[cyan]⚡ Using optimized section-only editing (faster)[/cyan]")
            
            # Extract only the specified sections from current HTML
            with open(target_file, 'r') as f:
                current_html = f.read()
            
            sections_html = extract_sections_html(current_html, affected_sections)
            
            # Use lightweight section-only prompt
            prompt = editgen_sections_prompt(
                product_desc=desc,
                framework=framework,
                theme=theme,
                edit_instruction=instruction,
                affected_sections=affected_sections,
                sections_html=sections_html
            )
            
            # Run Claude with lighter prompt
            console.print(f"\n[bold blue]🤖 Processing section edit with Claude AI...[/bold blue]")
            new_sections, stats = run_claude_with_progress(prompt, f"Editing {len(affected_sections)} section(s)...")
            
            # Merge updated sections back into the original HTML
            output = merge_sections_into_html(current_html, new_sections)
        else:
            # Full page editing (original behavior)
            console.print(f"[cyan]📄 Using full page editing[/cyan]")
            prompt = editgen_prompt(
                product_desc=desc,
                framework=framework,
                theme=theme,
                edit_instruction=instruction,
                existing_context=context,
                affected_sections=affected_sections
            )
            
            # Run Claude with the edit
            console.print(f"\n[bold blue]🤖 Processing edit with Claude AI...[/bold blue]")
            output, stats = run_claude_with_progress(prompt, f"Making edit: {instruction[:50]}...")
        
        # Validate output
        if not validate_html_output(output):
            console.print("[red]❌ Generated invalid HTML output[/red]")
            raise typer.Exit(1)
        
        # Save the edited file
        with open(target_file, 'w') as f:
            f.write(output)
        
        # Update design analysis if it exists
        try:
            analysis_file = Path(output_dir) / 'design_analysis.json'
            if analysis_file.exists():
                with open(analysis_file, 'r') as f:
                    analysis_data = json.load(f)
                
                # Add edit history
                if 'edit_history' not in analysis_data:
                    analysis_data['edit_history'] = []
                
                edit_entry = {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'instruction': instruction,
                    'affected_sections': affected_sections,
                    'usage_stats': stats
                }
                analysis_data['edit_history'].append(edit_entry)
                
                with open(analysis_file, 'w') as f:
                    json.dump(analysis_data, f, indent=2)
                    
                console.print(f"[cyan]📊 Updated design analysis with edit history[/cyan]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not update design analysis: {e}[/yellow]")
        
        # Show success message and usage stats
        console.print(f"\n[bold green]✅ Successfully edited landing page![/bold green]")
        console.print(f"[green]📄 File updated: {target_file}[/green]")
        
        if stats:
            console.print(f"\n[dim]📊 Usage: {stats.get('input_tokens', 0)} input tokens, {stats.get('output_tokens', 0)} output tokens[/dim]")
            if 'cost_estimate' in stats:
                console.print(f"[dim]💰 Estimated cost: ${stats['cost_estimate']:.4f}[/dim]")
        
        # Show preview instructions
        console.print("\n[bold cyan]🌐 Preview your edited page:[/bold cyan]")
        console.print(f"  • Open [bold]{target_file}[/bold] in your browser")
        if framework == 'react':
            console.print("  • Or run [bold]npx serve[/bold] in the output directory")
            console.print("  Then open [bold]http://localhost:3000[/bold] in your browser")
        
    except Exception as e:
        console.print(f"[red]❌ Error during edit: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def theme(
    new_theme: Optional[str] = typer.Argument(None, help=f"New design theme ({'/'.join(get_theme_choices())}) - leave empty for interactive selection"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to landing page file"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Change the design theme of an existing landing page
    
    This command re-runs the design system and implementation phases 
    while preserving all research and wireframe data from the original generation.
    
    Examples:
      ccux theme                                    # Interactive theme selection
      ccux theme brutalist                         # Direct theme selection
      ccux theme playful --file custom/page.html   # With specific file
    """
    
    config = Config()
    output_dir = output_dir or config.get('output_dir', 'output/landing-page')
    
    # Get theme - either from argument or interactive selection
    if new_theme is None:
        # Interactive theme selection
        new_theme = select_theme_interactively()
    else:
        # Validate provided theme
        valid_themes = get_theme_choices()
        if new_theme not in valid_themes:
            console.print(f"[red]❌ Invalid theme. Must be one of: {', '.join(valid_themes)}[/red]")
            console.print("\n[bold]Available themes:[/bold]")
            for choice in valid_themes:
                desc = get_theme_description(choice)
                console.print(f"  [cyan]{choice}[/cyan]: {desc}")
            raise typer.Exit(1)
    
    # Find existing landing page files
    if file:
        if not os.path.exists(file):
            console.print(f"[red]❌ File not found: {file}[/red]")
            raise typer.Exit(1)
        target_file = file
        output_dir = os.path.dirname(file) or "."
    else:
        # If no output_dir specified, discover and select project interactively
        if output_dir is None:
            projects = discover_existing_projects()
            selected_dir = select_project_interactively(projects, "change theme for")
            output_dir = selected_dir
            
        found_files = find_landing_page_files(output_dir)
        if not found_files:
            console.print(f"[red]❌ No landing page files found in {output_dir}[/red]")
            console.print("Run [bold]ccux gen[/bold] first to create a landing page")
            raise typer.Exit(1)
        
        # Prefer React if both exist, otherwise use what's available
        if 'react' in found_files:
            target_file = found_files['react']
        else:
            target_file = found_files['html']
    
    # Check for design analysis file
    analysis_file = os.path.join(output_dir, 'design_analysis.json')
    if not os.path.exists(analysis_file):
        console.print(f"[red]❌ Design analysis not found: {analysis_file}[/red]")
        console.print("This command requires a landing page generated with full design thinking process")
        console.print("Run [bold]ccux gen --desc 'your product'[/bold] without --no-design-thinking flag")
        raise typer.Exit(1)
    
    # Load existing design analysis
    try:
        with open(analysis_file, 'r') as f:
            analysis_data = json.load(f)
    except Exception as e:
        console.print(f"[red]❌ Error reading design analysis: {e}[/red]")
        raise typer.Exit(1)
    
    # Extract context from existing file
    context = extract_page_context(target_file)
    framework = context['framework']
    current_theme = context['theme']
    
    console.print(f"[bold blue]🎨 Changing theme from {current_theme} to {new_theme}[/bold blue]")
    console.print(f"Target file: [cyan]{target_file}[/cyan]")
    console.print(f"Framework: [green]{framework}[/green]")
    
    # Get product description from analysis (handle both fast and full mode structures)
    product_desc = analysis_data.get('product_description') or analysis_data.get('project_metadata', {}).get('product_description')
    if not product_desc:
        console.print("[red]❌ Product description not found in design analysis[/red]")
        console.print("Cannot change theme without original product description")
        raise typer.Exit(1)
    
    if len(product_desc) > 100:
        product_desc = product_desc[:100] + "..."
    
    console.print(f"Product: [cyan]{product_desc}[/cyan]")
    
    try:
        # Get required data from previous phases
        content_strategy = analysis_data.get('content_strategy', {})
        wireframes = analysis_data.get('wireframes', {})
        user_research = analysis_data.get('user_research', {})
        
        # Phase 9: Regenerate Design System with new theme
        console.print(f"\n[bold]Phase 9: Design System ({new_theme} theme)[/bold]")
        prompt = design_system_prompt(product_desc, wireframes, content_strategy, new_theme)
        design_output, _ = run_claude_with_progress(prompt, f"Building {new_theme} design system...")
        design_system = safe_json_parse(design_output)
        
        # Phase 10: High-Fidelity Design with new theme
        console.print(f"\n[bold]Phase 10: High-Fidelity Design ({new_theme} theme)[/bold]")
        prompt = high_fidelity_design_prompt(product_desc, design_system, wireframes, content_strategy)
        hifi_output, _ = run_claude_with_progress(prompt, f"Creating {new_theme} high-fidelity design...")
        hifi_design = safe_json_parse(hifi_output)
        
        # Phase 11: Keep existing copy (no need to regenerate)
        final_copy = analysis_data.get('final_copy', {})
        
        # Phase 12: Implementation with new theme
        console.print(f"\n[bold]Phase 12: Code Implementation ({new_theme} theme)[/bold]")
        design_data = {
            'design_system': design_system,
            'ux_analysis': analysis_data.get('ux_analysis', {}),
            'wireframes': wireframes,
            'content_strategy': content_strategy
        }
        prompt = implementation_prompt(product_desc, final_copy, framework, new_theme, design_data)
        code_output, stats = run_claude_with_progress(prompt, f"Implementing {new_theme} themed page...")
        
        # Save the new themed code
        if framework == 'react':
            with open(target_file, 'w') as f:
                f.write(strip_code_blocks(code_output))
        else:
            with open(target_file, 'w') as f:
                f.write(strip_code_blocks(code_output))
        
        # Update design analysis with new theme data
        analysis_data['design_system'] = design_system
        analysis_data['hifi_design'] = hifi_design
        analysis_data['current_theme'] = new_theme
        analysis_data['project_metadata']['theme'] = new_theme
        analysis_data['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Add theme change to history
        if 'theme_history' not in analysis_data:
            analysis_data['theme_history'] = []
        
        theme_record = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'from_theme': current_theme,
            'to_theme': new_theme,
            'usage_stats': stats,
            'method': 'theme_command'
        }
        analysis_data['theme_history'].append(theme_record)
        
        # Save updated analysis
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        console.print(f"[bold green]✅ Successfully changed theme to {new_theme}![/bold green]")
        console.print(f"📁 Updated file: [bold]{target_file}[/bold]")
        console.print(f"📊 Design analysis updated: [bold]{analysis_file}[/bold]")
        
        # Show preview instructions
        console.print(f"\n[bold cyan]🌐 Preview your themed page:[/bold cyan]")
        console.print(f"  [bold]cd {os.path.dirname(target_file)}[/bold]")
        console.print("  [bold]python -m http.server 3000[/bold]")
        console.print("  Then open [bold]http://localhost:3000[/bold] in your browser")
        
    except Exception as e:
        console.print(f"[red]❌ Error during theme change: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def form(
    state: str = typer.Argument(..., help="Form inclusion state (on|off|edit)"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to landing page file"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    form_type_param: Optional[str] = typer.Option(None, "--type", "-t", help="Form type (contact|newsletter|signup|custom)"),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated field list (name,email,phone,message)"),
    style: Optional[str] = typer.Option(None, "--style", "-s", help="Form style (inline|modal|sidebar|fullpage)"),
    cta: Optional[str] = typer.Option(None, "--cta", help="Custom CTA button text")
):
    """Advanced form control in landing pages using Claude AI
    
    Control forms with detailed customization including type, fields, styling, and placement.
    The 'edit' state allows complete customization of form specifications.
    
    Examples:
      ccux form on                                    # Add basic contact forms
      ccux form off                                   # Remove all forms
      ccux form edit --type contact --fields name,email,message --cta "Get In Touch"
      ccux form edit --type newsletter --fields email --style inline
      ccux form edit --type signup --fields name,email,phone --style modal
      ccux form on --file custom.html                # Target specific file
    """
    
    config = Config()
    
    # Validate state argument
    if state not in ['on', 'off', 'edit']:
        console.print("[red]❌ Form state must be 'on', 'off', or 'edit'[/red]")
        console.print("Examples:")
        console.print("  [cyan]ccux form on[/cyan]                                     - Add basic contact forms")
        console.print("  [cyan]ccux form off[/cyan]                                    - Remove all forms")
        console.print("  [cyan]ccux form edit --type contact --fields name,email[/cyan] - Custom form specification")
        raise typer.Exit(1)
    
    # Find target file
    if file:
        if not os.path.exists(file):
            console.print(f"[red]❌ File not found: {file}[/red]")
            raise typer.Exit(1)
        target_file = file
        output_dir = os.path.dirname(file) or "."
    else:
        # If no output_dir specified, discover and select project interactively
        if output_dir is None:
            projects = discover_existing_projects()
            selected_dir = select_project_interactively(projects, "manage forms for")
            output_dir = selected_dir
            
        found_files = find_landing_page_files(output_dir)
        if not found_files:
            console.print(f"[red]❌ No landing page files found in {output_dir}[/red]")
            console.print("Run [bold]ccux gen[/bold] first to create a landing page")
            raise typer.Exit(1)
        
        # Prefer HTML for form control (React not supported yet)
        if 'html' in found_files:
            target_file = found_files['html']
        else:
            console.print("[red]❌ Only HTML files are supported for form control[/red]")
            console.print("React form control coming soon!")
            raise typer.Exit(1)
    
    action_text = {
        'on': 'Adding basic contact form with Claude AI',
        'off': 'Removing all forms with Claude AI', 
        'edit': 'Customizing form with Claude AI'
    }[state]
    console.print(f"[bold blue]📝 {action_text}...[/bold blue]")
    
    try:
        # Read the current file content
        with open(target_file, 'r', encoding='utf-8') as f:
            existing_html = f.read()
        
        # Get product description from design analysis if available
        product_desc = "Landing page"
        design_analysis_file = os.path.join(os.path.dirname(target_file), 'design_analysis.json')
        if os.path.exists(design_analysis_file):
            try:
                with open(design_analysis_file, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    product_desc = analysis_data.get('product_description', product_desc)
            except:
                pass  # Fall back to default
        
        # Detect theme from existing content
        detected_theme = detect_theme_from_content(existing_html)
        
        # Generate appropriate Claude prompt based on state
        if state == 'on':
            prompt = form_on_prompt(product_desc, existing_html, detected_theme)
            description = f"Adding basic contact form with {detected_theme} theme"
        elif state == 'off':
            prompt = form_off_prompt(existing_html)
            description = "Removing all forms while preserving design"
        elif state == 'edit':
            # Parse and validate edit parameters - handle OptionInfo objects
            def clean_param(param, default):
                """Clean parameter that might be OptionInfo object"""
                if param is None or (hasattr(param, '__class__') and 'OptionInfo' in str(param.__class__)):
                    return default
                elif isinstance(param, str) and param.strip():
                    return param
                else:
                    return default
            
            form_type = clean_param(form_type_param, 'contact')
            fields_str = clean_param(fields, 'name,email,message')
            style = clean_param(style, None)
            cta = clean_param(cta, None)
            fields_list = [f.strip() for f in fields_str.split(',')]
            
            prompt = form_edit_prompt(
                existing_html, 
                form_type, 
                fields_list, 
                style, 
                cta, 
                detected_theme
            )
            form_desc = f"{form_type} form with {', '.join(fields_list)} fields"
            if style:
                form_desc += f" ({style} style)"
            description = f"Adding custom {form_desc}"
        
        # Call Claude AI to process forms
        output, stats = run_claude_with_progress(prompt, description)
        
        # Validate the output is valid HTML
        cleaned_output = strip_code_blocks(output)
        if not validate_html_output(cleaned_output):
            console.print("[red]❌ Claude generated invalid HTML output[/red]")
            console.print("[yellow]💡 Try running the command again or check the original file[/yellow]")
            raise typer.Exit(1)
        
        # Write the updated content back to the file
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_output)
        
        # Verify the operation and show results
        form_count = cleaned_output.count('<form')
        
        if state == 'off':
            if form_count == 0:
                console.print("[bold green]✅ Successfully removed all forms![/bold green]")
                console.print("• All form elements removed by Claude AI")
                console.print("• Page design and layout preserved")
            else:
                console.print(f"[yellow]⚠️  Found {form_count} remaining form(s). Some forms may not have been removed.[/yellow]")
                
        elif state in ['on', 'edit']:
            if form_count > 0:
                if state == 'edit':
                    console.print(f"[bold green]✅ Successfully added custom {form_type} form![/bold green]")
                    console.print(f"• Form type: {form_type}")
                    console.print(f"• Fields: {', '.join(fields_list)}")
                    if cta:
                        console.print(f"• CTA text: {cta}")
                    if style:
                        console.print(f"• Style: {style}")
                else:
                    console.print("[bold green]✅ Successfully added contact form![/bold green]")
                    console.print("• Basic contact form with name, email, message fields")
                    
                console.print(f"• Theme-matched styling: {detected_theme}")
                console.print("• Integrated seamlessly by Claude AI without altering existing design")
                
            else:
                console.print("[yellow]⚠️  Form may not have been added properly. Check the output file.[/yellow]")
        
        console.print(f"[green]📄 Updated: {target_file}[/green]")
        
        # Update design analysis to track form operations
        if os.path.exists(design_analysis_file):
            try:
                with open(design_analysis_file, 'r') as f:
                    analysis_data = json.load(f)
                
                # Track form operations in a separate history
                if 'form_history' not in analysis_data:
                    analysis_data['form_history'] = []
                
                form_operation = {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'operation': state,
                    'theme': detected_theme,
                    'method': 'claude_ai'
                }
                
                if state == 'edit':
                    form_operation.update({
                        'form_type': form_type,
                        'fields': fields_list,
                        'cta_text': cta,
                        'style': style
                    })
                
                analysis_data['form_history'].append(form_operation)
                
                with open(design_analysis_file, 'w') as f:
                    json.dump(analysis_data, f, indent=2)
                    
                console.print("[cyan]📊 Form operation tracked in design analysis[/cyan]")
                
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not update design analysis: {e}[/yellow]")
        
        # Show preview instructions and usage stats
        console.print("\n[bold green]✅ Form processing complete![/bold green]")
        console.print("\n[bold cyan]🌐 Preview your updated page:[/bold cyan]")
        console.print(f"  [bold]cd {os.path.dirname(target_file)}[/bold]")
        console.print("  [bold]python -m http.server 3000[/bold]")
        console.print("  Then open [bold]http://localhost:3000[/bold] in your browser")
        
        # Display usage stats
        if stats:
            console.print(f"\n[dim]Tokens: {stats.get('input_tokens', 0)} in, {stats.get('output_tokens', 0)} out | Cost: ~${stats.get('estimated_cost', 0.0):.4f}[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Error processing forms: {e}[/red]")
        console.print("\n[yellow]💡 Form control tips:[/yellow]")
        console.print("• Use [cyan]ccux form on[/cyan] to add basic contact form")
        console.print("• Use [cyan]ccux form off[/cyan] to remove all forms while preserving design")
        console.print("• Use [cyan]ccux form edit --type newsletter --fields email[/cyan] for custom forms")
        console.print("• Make sure you have Claude CLI installed and accessible")
        raise typer.Exit(1)


@app.command()
def help(
    topic: Optional[str] = typer.Argument(None, help="Specific help topic (quickstart|themes|examples|workflows)")
):
    """Show comprehensive help and usage examples
    
    Available help topics:
    - quickstart: Getting started guide
    - themes: Available design themes with descriptions
    - examples: Common usage examples  
    - workflows: Step-by-step workflows
    """
    
    if topic is None:
        # Show main help menu
        console.print("[bold blue]CCUX - Claude Code UI Generator[/bold blue]")
        console.print("Generate conversion-optimized landing pages using AI-powered design thinking\n")
        
        # Quick start section
        console.print("[bold green]Quick Start[/bold green]")
        console.print("1. Initialize: [cyan]ccux init[/cyan]")
        console.print("2. Generate: [cyan]ccux gen --desc 'Your product description'[/cyan]")
        console.print("3. Preview: [cyan]cd output/landing-page && python -m http.server 3000[/cyan]\n")
        
        # Main commands table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Command", style="green", width=15)
        table.add_column("Description", width=50)
        table.add_column("Example", style="dim")
        
        table.add_row("init", "Install Playwright browsers", "ccux init")
        table.add_row("gen", "Generate landing page", "ccux gen --desc 'AI tool' --theme brutalist")
        table.add_row("regen", "Regenerate specific sections", "ccux regen --section hero,pricing")
        table.add_row("theme", "Change design theme", "ccux theme minimal")
        table.add_row("form", "Advanced form control with customization", "ccux form edit --type contact")
        table.add_row("cost", "Show cost analysis", "ccux cost --detailed")
        table.add_row("help", "Show detailed help", "ccux help themes")
        table.add_row("version", "Show version info", "ccux version")
        
        console.print(table)
        
        # Available help topics
        console.print("\n[bold yellow]Detailed Help Topics[/bold yellow]")
        console.print("• [cyan]ccux help quickstart[/cyan] - Complete getting started guide")
        console.print("• [cyan]ccux help themes[/cyan] - All available design themes")
        console.print("• [cyan]ccux help examples[/cyan] - Common usage patterns")
        console.print("• [cyan]ccux help workflows[/cyan] - Step-by-step workflows")
        
        # Tips
        console.print("\n[bold magenta]Pro Tips[/bold magenta]")
        console.print("• Run [cyan]ccux gen[/cyan] (no args) for interactive mode")
        console.print("• Use [cyan]--no-design-thinking[/cyan] for faster generation")
        console.print("• Provide [cyan]--url[/cyan] references for better competitor analysis")
        console.print("• Save long descriptions in a text or PDF file and use [cyan]--desc-file[/cyan]")
        
    elif topic == "quickstart":
        console.print("[bold blue]CCUX Quick Start Guide[/bold blue]\n")
        
        console.print("[bold green]Step 1: Installation & Setup[/bold green]")
        console.print("# Install CCUX")
        console.print("[cyan]pip install ccux[/cyan]")
        console.print("# Initialize (download browsers)")  
        console.print("[cyan]ccux init[/cyan]\n")
        
        console.print("[bold green]Step 2: Your First Landing Page[/bold green]")
        console.print("# Interactive mode (recommended for beginners)")
        console.print("[cyan]ccux gen[/cyan]")
        console.print("# Or direct mode")
        console.print("[cyan]ccux gen --desc 'AI-powered project management tool'[/cyan]\n")
        
        console.print("[bold green]Step 3: Preview Your Page[/bold green]")
        console.print("[cyan]cd output/landing-page[/cyan]")
        console.print("[cyan]python -m http.server 3000[/cyan]")
        console.print("Open http://localhost:3000 in your browser\n")
        
        console.print("[bold green]Step 4: Customize & Iterate[/bold green]")
        console.print("# Change theme")
        console.print("[cyan]ccux theme brutalist[/cyan]")
        console.print("# Regenerate specific sections")
        console.print("[cyan]ccux regen --section hero[/cyan]")
        console.print("# Add competitor references")
        console.print("[cyan]ccux gen --desc 'Your product' --url https://competitor.com[/cyan]\n")
        
        console.print("[bold yellow]What You Get[/bold yellow]")
        console.print("• Professional conversion-optimized landing page")
        console.print("• Mobile-responsive design with TailwindCSS")
        console.print("• SEO-optimized HTML structure")
        console.print("• Design analysis JSON with research insights")
        console.print("• Screenshot references from competitors")
        
    elif topic == "themes":
        console.print("[bold blue]Available Design Themes[/bold blue]\n")
        
        # Core themes
        console.print("[bold green]Core Themes[/bold green]")
        core_themes = [
            ("minimal", "Clean, content-focused design following Dieter Rams principles"),
            ("brutalist", "Raw, honest design inspired by Brutalist architecture"),
            ("playful", "Joyful, approachable design with organic shapes"),
            ("corporate", "Traditional, trustworthy business design")
        ]
        
        for theme, desc in core_themes:
            console.print(f"• [cyan]{theme:12}[/cyan] {desc}")
        
        # Modern themes
        console.print(f"\n[bold green]Modern Design Theory Themes[/bold green]")
        modern_themes = [
            ("morphism", "Soft, tactile design combining neumorphism and glassmorphism"),
            ("animated", "Motion-first design where animation drives experience"),
            ("terminal", "Monospace, CLI-inspired aesthetic for developers"),
            ("aesthetic", "Retro-futuristic design from Y2K and vaporwave")
        ]
        
        for theme, desc in modern_themes:
            console.print(f"• [cyan]{theme:12}[/cyan] {desc}")
            
        # Additional themes
        console.print(f"\n[bold green]Specialized Themes[/bold green]")
        specialized_themes = [
            ("dark", "Modern dark theme optimized for contrast"),
            ("vibrant", "Colorful, dopamine-rich design that energizes"),
            ("sustainable", "Nature-inspired design for eco-conscious branding"),
            ("data", "Information-dense design for dashboards/analytics"),
            ("illustrated", "Hand-drawn, custom illustration-driven design")
        ]
        
        for theme, desc in specialized_themes:
            console.print(f"• [cyan]{theme:12}[/cyan] {desc}")
        
        console.print(f"\n[bold yellow]Usage Examples[/bold yellow]")
        console.print("[cyan]ccux gen --desc 'SaaS platform' --theme minimal[/cyan]")
        console.print("[cyan]ccux gen --desc 'Creative agency' --theme brutalist[/cyan]")
        console.print("[cyan]ccux theme morphism  # Change existing page theme[/cyan]")
        
    elif topic == "examples":
        console.print("[bold blue]Common Usage Examples[/bold blue]\n")
        
        # Basic examples
        console.print("[bold green]Basic Generation[/bold green]")
        examples_basic = [
            ("Interactive mode", "ccux gen", "Guided setup with prompts"),
            ("Simple generation", "ccux gen --desc 'AI writing tool'", "Quick page with minimal theme"),
            ("From file", "ccux gen --desc-file product.txt", "Load descriptions from text/PDF file"),
            ("Fast mode", "ccux gen --desc 'SaaS tool' --no-design-thinking", "Skip full research process")
        ]
        
        for name, cmd, desc in examples_basic:
            console.print(f"• [bold]{name}[/bold]: [cyan]{cmd}[/cyan]")
            console.print(f"  {desc}\n")
        
        # Advanced examples  
        console.print("[bold green]Advanced Usage[/bold green]")
        examples_advanced = [
            ("With competitors", "ccux gen --desc 'Project tool' --url https://linear.app --url https://notion.so", "Include competitor analysis"),
            ("Custom theme", "ccux gen --desc 'Design portfolio' --theme aesthetic --framework react", "React output with aesthetic theme"),
            ("Custom output", "ccux gen --desc 'Marketing site' --output custom-dir --theme vibrant", "Custom directory and theme")
        ]
        
        for name, cmd, desc in examples_advanced:
            console.print(f"• [bold]{name}[/bold]: [cyan]{cmd}[/cyan]")
            console.print(f"  {desc}\n")
        
        # Regeneration examples
        console.print("[bold green]Section Regeneration[/bold green]")
        examples_regen = [
            ("Single section", "ccux regen --section hero", "Regenerate just the hero section"),
            ("Multiple sections", "ccux regen --section hero,pricing,footer", "Regenerate multiple sections"),
            ("All sections", "ccux regen --all", "Regenerate entire page"),
            ("With new description", "ccux regen --section features --desc 'Updated product description'", "Update with new context")
        ]
        
        for name, cmd, desc in examples_regen:
            console.print(f"• [bold]{name}[/bold]: [cyan]{cmd}[/cyan]")
            console.print(f"  {desc}\n")
        
        # Theme changes
        console.print("[bold green]Theme Management[/bold green]")
        console.print("• [bold]Change theme[/bold]: [cyan]ccux theme brutalist[/cyan]")
        console.print("  Apply brutalist theme to existing page")
        console.print("• [bold]Custom file[/bold]: [cyan]ccux theme minimal --file custom/page.html[/cyan]")
        console.print("  Change theme of specific file")
        
        # Form control
        console.print("\n[bold green]Form Management[/bold green]")
        console.print("• [bold]Basic forms[/bold]: [cyan]ccux form on[/cyan]")
        console.print("  Add basic contact forms to appropriate sections")
        console.print("• [bold]Remove forms[/bold]: [cyan]ccux form off[/cyan]")
        console.print("  Remove all forms and use mailto: links")
        console.print("• [bold]Custom contact form[/bold]: [cyan]ccux form edit --type contact --fields name,email,message[/cyan]")
        console.print("  Create detailed contact form with specific fields")
        console.print("• [bold]Newsletter signup[/bold]: [cyan]ccux form edit --type newsletter --style inline[/cyan]")
        console.print("  Simple email signup form embedded in sections")
        console.print("• [bold]Modal signup form[/bold]: [cyan]ccux form edit --type signup --style modal --cta 'Join Beta'[/cyan]")
        console.print("  Registration form in popup modal with custom CTA text")

        # Animation control
        console.print("\n[bold green]Animation Control[/bold green]")
        console.print("• [bold]Smart animation addition[/bold]: [cyan]ccux animate on[/cyan]")
        console.print("  Analyze current design and add theme-appropriate animations")
        console.print("• [bold]Remove animation code[/bold]: [cyan]ccux animate off[/cyan]")
        console.print("  Remove only animation code (preserves essential styling)")
        console.print("• [bold]Granular control[/bold]: [cyan]ccux animate edit --target hero --action add[/cyan]")
        console.print("  Add/remove/modify animations for specific elements")
        console.print("• [bold]Custom file[/bold]: [cyan]ccux animate on --file custom.html[/cyan]")
        console.print("  Target specific files for animation control\n")
        
    elif topic == "workflows":
        console.print("[bold blue]Step-by-Step Workflows[/bold blue]\n")
        
        # Workflow 1: First-time user
        console.print("[bold green]Workflow 1: First Landing Page[/bold green]")
        steps_first = [
            "Install: pip install ccux",
            "Initialize: ccux init", 
            "Generate interactively: ccux gen",
            "Preview: cd output/landing-page && python -m http.server 3000",
            "Iterate: ccux regen --section hero (if needed)"
        ]
        
        for i, step in enumerate(steps_first, 1):
            console.print(f"{i}. {step}")
        console.print()
        
        # Workflow 2: Competitive analysis
        console.print("[bold green]Workflow 2: With Competitor Research[/bold green]")
        steps_competitive = [
            "Find 2-3 competitor websites",
            "Generate with references: ccux gen --desc 'Your product' --url https://competitor1.com --url https://competitor2.com",
            "Review design_analysis.json for insights",
            "Refine sections: ccux regen --section pricing",
            "Experiment with themes: ccux theme brutalist"
        ]
        
        for i, step in enumerate(steps_competitive, 1):
            console.print(f"{i}. {step}")
        console.print()
        
        # Workflow 3: Production ready
        console.print("[bold green]Workflow 3: Production-Ready Process[/bold green]")  
        steps_production = [
            "Prepare detailed product description (save to file)",
            "Generate with full process: ccux gen --desc-file product.txt --theme corporate",
            "Review and customize sections: ccux regen --section hero,features",
            "Test different themes: ccux theme minimal, ccux theme dark",
            "Final review and deployment prep"
        ]
        
        for i, step in enumerate(steps_production, 1):
            console.print(f"{i}. {step}")
        console.print()
        
        # Workflow 4: Iterative design
        console.print("[bold green]Workflow 4: Iterative Design Process[/bold green]")
        steps_iterative = [
            "Start with quick generation: ccux gen --desc 'Product' --no-design-thinking",
            "Review initial version",
            "Add competitor research: ccux gen --desc 'Product' --url https://competitor.com",
            "Refine individual sections: ccux regen --section pricing --desc 'Updated positioning'",
            "Add appropriate animations: ccux animate on",
            "Fine-tune animations: ccux animate edit --target hero --action modify",
            "Experiment with themes: ccux theme aesthetic, ccux theme terminal",
            "Final polish: ccux regen --section hero,footer"
        ]
        
        for i, step in enumerate(steps_iterative, 1):
            console.print(f"{i}. {step}")
            
    else:
        console.print(f"[red]❌ Unknown help topic: {topic}[/red]")
        console.print("Available topics: [cyan]quickstart[/cyan], [cyan]themes[/cyan], [cyan]examples[/cyan], [cyan]workflows[/cyan]")
        console.print("Run [cyan]ccux help[/cyan] for main help menu")
        raise typer.Exit(1)

@app.command()
def projects():
    """List all existing CCUX projects in the current directory"""
    projects = discover_existing_projects()
    
    if not projects:
        console.print("[yellow]No CCUX projects found in current directory.[/yellow]")
        console.print("Run [bold]ccux gen[/bold] to create your first project!")
        return
    
    console.print(f"\n[bold cyan]📁 Found {len(projects)} CCUX project(s):[/bold cyan]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Directory", style="cyan", width=15)
    table.add_column("Project Name", style="green")
    table.add_column("Status", style="yellow", width=10)
    
    for project in projects:
        # Check if it has design analysis and determine generation mode
        analysis_file = os.path.join(project['directory'], 'design_analysis.json')
        if os.path.exists(analysis_file):
            try:
                with open(analysis_file, 'r') as f:
                    analysis = json.load(f)
                generation_mode = analysis.get('generation_mode', 'full')
                status = "Fast" if generation_mode == 'fast' else "Full"
            except:
                status = "Full"  # Default for existing projects
        else:
            status = "No Data"  # No design analysis file
        
        table.add_row(
            project['directory'] + "/",
            project['name'],
            status
        )
    
    console.print(table)
    
    console.print(f"\n[dim]💡 Use other ccux commands without --output to select from these projects interactively[/dim]")

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
def cost(
    project_dir: Optional[str] = typer.Argument(None, help="Specific project directory to analyze"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed breakdown by operation"),
    summary: bool = typer.Option(False, "--summary", "-s", help="Show summary statistics only")
):
    """Show cost analysis for CCUX projects
    
    Analyzes token usage and estimated costs from design_analysis.json files.
    Without arguments, scans current directory for all CCUX projects.
    """
    
    try:
        projects_to_analyze = []
        
        if project_dir:
            # Analyze specific project
            if not os.path.exists(project_dir):
                console.print(f"[red]❌ Project directory not found: {project_dir}[/red]")
                raise typer.Exit(1)
            
            analysis_file = os.path.join(project_dir, 'design_analysis.json')
            if not os.path.exists(analysis_file):
                console.print(f"[yellow]⚠️  No design analysis found in: {project_dir}[/yellow]")
                console.print("This project may have been generated in fast mode.")
                raise typer.Exit(1)
            
            projects_to_analyze.append({
                'directory': project_dir,
                'name': os.path.basename(project_dir) or 'Current',
                'analysis_file': analysis_file
            })
        else:
            # Discover all CCUX projects in current directory
            current_dir = os.getcwd()
            for item in os.listdir(current_dir):
                item_path = os.path.join(current_dir, item)
                if os.path.isdir(item_path):
                    index_file = os.path.join(item_path, 'index.html')
                    analysis_file = os.path.join(item_path, 'design_analysis.json')
                    
                    if os.path.exists(index_file) and os.path.exists(analysis_file):
                        projects_to_analyze.append({
                            'directory': item,
                            'name': item.replace('-', ' ').title(),
                            'analysis_file': analysis_file
                        })
        
        if not projects_to_analyze:
            console.print("[yellow]No CCUX projects with cost data found.[/yellow]")
            console.print("Projects need design_analysis.json files to show cost information.")
            raise typer.Exit(1)
        
        # Analyze costs
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        project_costs = []
        
        for project in projects_to_analyze:
            try:
                with open(project['analysis_file'], 'r') as f:
                    analysis = json.load(f)
                
                project_cost = analyze_project_costs(analysis, project['name'], detailed)
                project_costs.append(project_cost)
                
                total_input_tokens += project_cost['input_tokens']
                total_output_tokens += project_cost['output_tokens']
                total_cost += project_cost['total_cost']
                
            except Exception as e:
                console.print(f"[yellow]⚠️  Error reading {project['name']}: {e}[/yellow]")
        
        # Display results
        if not summary:
            console.print("\n[bold cyan]💰 CCUX Cost Analysis[/bold cyan]")
            console.print("=" * 50)
            
            for project_cost in project_costs:
                display_project_costs(project_cost, detailed)
                console.print()
        
        # Summary
        if len(project_costs) > 1 or summary:
            console.print("[bold green]📊 Total Summary[/bold green]")
            console.print("-" * 30)
            console.print(f"Projects analyzed: [cyan]{len(project_costs)}[/cyan]")
            console.print(f"Total input tokens: [green]{total_input_tokens:,}[/green]")
            console.print(f"Total output tokens: [green]{total_output_tokens:,}[/green]") 
            console.print(f"Total estimated cost: [bold green]${total_cost:.3f}[/bold green]")
            
            if total_cost > 0:
                avg_cost_per_project = total_cost / len(project_costs)
                console.print(f"Average cost per project: [cyan]${avg_cost_per_project:.3f}[/cyan]")
        
        console.print(f"\n[dim]💡 Costs are estimates based on Claude usage patterns[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error analyzing costs: {e}[/red]")
        raise typer.Exit(1)


def analyze_project_costs(analysis_data: dict, project_name: str, detailed: bool) -> dict:
    """Analyze cost data from a project's design analysis"""
    
    project_cost = {
        'name': project_name,
        'input_tokens': 0,
        'output_tokens': 0,
        'total_cost': 0.0,
        'operations': []
    }
    
    # Main design phase costs (both full and fast mode)
    if 'total_usage' in analysis_data:
        usage = analysis_data['total_usage']
        project_cost['input_tokens'] += usage.get('input_tokens', 0)
        project_cost['output_tokens'] += usage.get('output_tokens', 0)
        project_cost['total_cost'] += usage.get('cost', 0.0)
        
        if detailed:
            generation_mode = analysis_data.get('generation_mode', 'full')
            operation_type = 'Fast Generation' if generation_mode == 'fast' else 'Full Design Process'
            
            project_cost['operations'].append({
                'type': operation_type,
                'input_tokens': usage.get('input_tokens', 0),
                'output_tokens': usage.get('output_tokens', 0),
                'cost': usage.get('cost', 0.0),
                'timestamp': analysis_data.get('created_at', 'Unknown')
            })
    
    # Individual phase costs (if available)
    if 'design_phases' in analysis_data and detailed:
        phases = analysis_data['design_phases']
        for phase_name, phase_data in phases.items():
            if 'stats' in phase_data:
                stats = phase_data['stats']
                if any(k in stats for k in ['input_tokens', 'output_tokens', 'cost']):
                    project_cost['operations'].append({
                        'type': f'Phase: {phase_name.replace("_", " ").title()}',
                        'input_tokens': stats.get('input_tokens', 0),
                        'output_tokens': stats.get('output_tokens', 0),
                        'cost': stats.get('cost', 0.0),
                        'timestamp': 'During generation'
                    })
    
    # Editing operations costs
    if 'edit_history' in analysis_data:
        for edit in analysis_data['edit_history']:
            if 'usage_stats' in edit:
                stats = edit['usage_stats']
                edit_input = stats.get('input_tokens', 0)
                edit_output = stats.get('output_tokens', 0)
                edit_cost = stats.get('cost', 0.0)
                
                project_cost['input_tokens'] += edit_input
                project_cost['output_tokens'] += edit_output
                project_cost['total_cost'] += edit_cost
                
                if detailed:
                    project_cost['operations'].append({
                        'type': f'Edit: {edit.get("instruction", "Content Edit")[:30]}...',
                        'input_tokens': edit_input,
                        'output_tokens': edit_output,
                        'cost': edit_cost,
                        'timestamp': edit.get('timestamp', 'Unknown')
                    })
    
    # Theme changes costs
    if 'theme_history' in analysis_data:
        for theme_change in analysis_data['theme_history']:
            if 'usage_stats' in theme_change:
                stats = theme_change['usage_stats']
                theme_input = stats.get('input_tokens', 0)
                theme_output = stats.get('output_tokens', 0)
                theme_cost = stats.get('cost', 0.0)
                
                project_cost['input_tokens'] += theme_input
                project_cost['output_tokens'] += theme_output  
                project_cost['total_cost'] += theme_cost
                
                if detailed:
                    project_cost['operations'].append({
                        'type': f'Theme Change to {theme_change.get("new_theme", "Unknown")}',
                        'input_tokens': theme_input,
                        'output_tokens': theme_output,
                        'cost': theme_cost,
                        'timestamp': theme_change.get('timestamp', 'Unknown')
                    })
    
    # Form operations costs
    if 'form_history' in analysis_data:
        for form_op in analysis_data['form_history']:
            if 'usage_stats' in form_op:
                stats = form_op['usage_stats']
                form_input = stats.get('input_tokens', 0)
                form_output = stats.get('output_tokens', 0)
                form_cost = stats.get('cost', 0.0)
                
                project_cost['input_tokens'] += form_input
                project_cost['output_tokens'] += form_output
                project_cost['total_cost'] += form_cost
                
                if detailed:
                    operation_type = f"Form {form_op.get('action', 'operation').title()}"
                    if 'type' in form_op and form_op['type']:
                        operation_type += f" ({form_op['type']})"
                    
                    project_cost['operations'].append({
                        'type': operation_type,
                        'input_tokens': form_input,
                        'output_tokens': form_output,
                        'cost': form_cost,
                        'timestamp': form_op.get('timestamp', 'Unknown')
                    })
    
    return project_cost


def display_project_costs(project_cost: dict, detailed: bool):
    """Display cost information for a single project"""
    
    console.print(f"[bold blue]📁 {project_cost['name']}[/bold blue]")
    console.print(f"Input tokens: [green]{project_cost['input_tokens']:,}[/green]")
    console.print(f"Output tokens: [green]{project_cost['output_tokens']:,}[/green]")
    console.print(f"Total cost: [bold green]${project_cost['total_cost']:.3f}[/bold green]")
    
    if detailed and project_cost['operations']:
        console.print("\n[cyan]Operation Breakdown:[/cyan]")
        
        table = Table(show_header=True, header_style="bold cyan", box=None)
        table.add_column("Operation", style="yellow", width=25)
        table.add_column("In", justify="right", width=8)
        table.add_column("Out", justify="right", width=8) 
        table.add_column("Cost", justify="right", width=8)
        table.add_column("When", style="dim", width=12)
        
        for op in project_cost['operations']:
            table.add_row(
                op['type'][:25],
                f"{op['input_tokens']:,}",
                f"{op['output_tokens']:,}",
                f"${op['cost']:.3f}",
                op['timestamp'][:12]
            )
        
        console.print(table)


def multipage(desc: Optional[str] = None, desc_file: Optional[str] = None, 
             theme: str = "minimal", base_url: str = "https://example.com", 
             output_dir: Optional[str] = None):
    """Generate intelligent multi-page website with parallel processing"""
    
    from .multipage import run_multipage_generation
    from PyPDF2 import PdfReader
    
    try:
        # Get product description
        if desc_file:
            desc_path = Path(desc_file)
            if not desc_path.exists():
                console.print(f"[red]❌ Description file not found: {desc_file}[/red]")
                raise typer.Exit(1)
            
            if desc_file.lower().endswith('.pdf'):
                try:
                    reader = PdfReader(desc_file)
                    desc = ""
                    for page in reader.pages:
                        desc += page.extract_text() + "\n"
                    desc = desc.strip()
                except Exception as e:
                    console.print(f"[red]❌ Error reading PDF: {e}[/red]")
                    raise typer.Exit(1)
            else:
                with open(desc_file, 'r', encoding='utf-8') as f:
                    desc = f.read().strip()
        
        if not desc:
            desc = Prompt.ask("[cyan]Enter product description for multi-page website[/cyan]")
        
        if not desc.strip():
            console.print("[red]❌ Product description is required[/red]")
            raise typer.Exit(1)
        
        # Validate theme
        if theme not in get_theme_choices():
            console.print(f"[red]❌ Invalid theme: {theme}[/red]")
            console.print(f"[yellow]Available themes: {', '.join(get_theme_choices())}[/yellow]")
            raise typer.Exit(1)
        
        # Show startup banner
        console.print(f"\n[bold blue]🌐 CCUX Multi-Page Website Generator[/bold blue]")
        console.print(f"[dim]Theme: {theme} | Base URL: {base_url}[/dim]")
        
        # Run multi-page generation (non-interactive mode for CLI)
        results = run_multipage_generation(desc, output_dir, theme, base_url, interactive=False)
        
        # Handle results
        if results.get('success', False):
            console.print(f"\n[bold green]🎉 Multi-page website generated successfully![/bold green]")
        elif results.get('cancelled', False):
            console.print(f"\n[yellow]⚠️  Generation cancelled by user[/yellow]")
            raise typer.Exit(1)
        else:
            error_msg = results.get('error', 'Unknown error occurred')
            console.print(f"\n[red]❌ Generation failed: {error_msg}[/red]")
            raise typer.Exit(1)
            
    except KeyboardInterrupt:
        console.print(f"\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information"""
    try:
        package_version = importlib.metadata.version('ccux')
    except importlib.metadata.PackageNotFoundError:
        package_version = 'unknown'
    
    console.print(f"[bold blue]CCUX v{package_version}[/bold blue]")
    console.print("Claude Code UI Generator - Interactive landing page creator")
    console.print("\n[dim]Run 'ccux init' to start the interactive application[/dim]")

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