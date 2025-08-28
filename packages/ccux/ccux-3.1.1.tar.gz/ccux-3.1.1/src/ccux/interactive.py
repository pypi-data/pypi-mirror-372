#!/usr/bin/env python3
"""
CCUX Interactive Application
Complete interactive interface for CCUX landing page generation
"""

import os
import sys
import time
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm, IntPrompt

# Import utilities from core modules
from .core.content_processing import safe_json_parse

console = Console()

def get_key_with_esc_support(prompt_text: str, default: str = "") -> str:
    """Get single key press with ESC support"""
    import sys
    import tty
    import termios
    
    console.print(f"[bold]{prompt_text} (or press ESC to exit)[/bold]")
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        
        # Check for ESC key (ASCII 27)
        if ord(ch) == 27:
            console.print("\n[yellow]ESC pressed - exiting application...[/yellow]")
            sys.exit(0)
        
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def prompt_with_esc_support(prompt_text: str, default: str = "") -> str:
    """Prompt for input with ESC support"""
    import sys
    import tty
    import termios
    
    console.print(f"[bold]{prompt_text}[/bold]")
    if default:
        console.print(f"[dim]Default: {default}[/dim]")
    console.print("[dim]Press ESC to exit, Enter to confirm[/dim]")
    
    input_buffer = ""
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        
        while True:
            ch = sys.stdin.read(1)
            
            # Check for ESC key (ASCII 27)
            if ord(ch) == 27:
                console.print("\n[yellow]ESC pressed - exiting application...[/yellow]")
                sys.exit(0)
            
            # Check for Enter key
            if ch in ['\r', '\n'] or ord(ch) == 13:
                result = input_buffer if input_buffer else default
                console.print(f"\n[green]Input: {result}[/green]")
                return result
            
            # Check for backspace
            if ord(ch) == 127:
                if input_buffer:
                    input_buffer = input_buffer[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                continue
            
            # Regular character input
            if ch.isprintable():
                input_buffer += ch
                sys.stdout.write(ch)
                sys.stdout.flush()
                
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

@dataclass
class MenuOption:
    key: str
    label: str
    description: str
    icon: str = ""

@dataclass
class FormField:
    name: str
    label: str
    field_type: str  # text, dropdown, multi_url, checkbox
    value: Any = None
    options: List[tuple] = None
    placeholder: str = ""
    required: bool = False
    multiline: bool = False

class InteractiveMenu:
    """Base class for interactive menus using Rich prompts"""
    
    def __init__(self, title: str, options: List[MenuOption]):
        self.title = title
        self.options = options
    
    def show(self):
        """Show menu and get selection"""
        console.clear()
        
        # Create menu display
        menu_text = Text()
        menu_text.append(f"{self.title}\n\n", style="bold cyan")
        
        for i, option in enumerate(self.options, 1):
            menu_text.append(f"{i}. {option.icon} {option.label}\n", style="white")
            if option.description:
                menu_text.append(f"   {option.description}\n\n", style="dim")
            else:
                menu_text.append("\n")
        
        panel = Panel(
            menu_text,
            border_style="blue",
            padding=(1, 2)
        )
        
        console.print(Align.center(panel))
        
        # Get user choice
        try:
            import sys
            import tty
            import termios
            
            while True:
                console.print(f"[bold]Choose option (1-{len(self.options)}) or press ESC to exit[/bold]")
                
                # For single digit options, use single key press
                if len(self.options) <= 9:
                    # Get single key press
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                        
                        # Check for ESC key (ASCII 27)
                        if ord(ch) == 27:
                            console.print("\n[yellow]ESC pressed - exiting application...[/yellow]")
                            return 'exit'
                        
                        # Check for number keys
                        if ch.isdigit():
                            choice = int(ch)
                            if 1 <= choice <= len(self.options):
                                console.print(f"\n[green]Selected: {choice}[/green]")
                                return self.options[choice - 1].key
                            else:
                                console.print(f"\n[red]Please enter a number between 1 and {len(self.options)}[/red]")
                        else:
                            console.print(f"\n[red]Please enter a number between 1 and {len(self.options)} or press ESC[/red]")
                            
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                else:
                    # For multi-digit options, use line input with ESC support
                    try:
                        # Check for ESC key first
                        fd = sys.stdin.fileno()
                        old_settings = termios.tcgetattr(fd)
                        input_buffer = ""
                        
                        try:
                            tty.setraw(sys.stdin.fileno())
                            
                            while True:
                                ch = sys.stdin.read(1)
                                
                                # Check for ESC key (ASCII 27)
                                if ord(ch) == 27:
                                    console.print("\n[yellow]ESC pressed - exiting application...[/yellow]")
                                    return 'exit'
                                
                                # Check for Enter key
                                if ch in ['\r', '\n'] or ord(ch) == 13:
                                    if input_buffer.strip():
                                        try:
                                            choice = int(input_buffer.strip())
                                            if 1 <= choice <= len(self.options):
                                                console.print(f"\n[green]Selected: {choice}[/green]")
                                                return self.options[choice - 1].key
                                            else:
                                                console.print(f"\n[red]Please enter a number between 1 and {len(self.options)}[/red]")
                                                break
                                        except ValueError:
                                            console.print(f"\n[red]Please enter a valid number[/red]")
                                            break
                                    else:
                                        console.print(f"\n[red]Please enter a number between 1 and {len(self.options)}[/red]")
                                        break
                                
                                # Check for backspace
                                if ord(ch) == 127:
                                    if input_buffer:
                                        input_buffer = input_buffer[:-1]
                                        sys.stdout.write('\b \b')
                                        sys.stdout.flush()
                                    continue
                                
                                # Regular character input (only digits)
                                if ch.isdigit():
                                    input_buffer += ch
                                    sys.stdout.write(ch)
                                    sys.stdout.flush()
                                elif ch.isprintable() and not ch.isspace():
                                    # Ignore non-digit characters
                                    continue
                                    
                        finally:
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            
                    except Exception as e:
                        console.print(f"\n[red]Input error: {e}[/red]")
                        break
                    
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Interrupted - exiting application...[/yellow]")
            return 'exit'

class InteractiveForm:
    """Interactive form for project creation using Rich prompts"""
    
    def __init__(self, title: str, fields: List[FormField]):
        self.title = title
        self.fields = fields
        self.form_data = {}
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format and auto-fix common issues"""
        try:
            from urllib.parse import urlparse
            
            # Auto-fix URLs without protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc]) and parsed.scheme in ['http', 'https']
        except:
            return False
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL by adding protocol if missing"""
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url
    
    def show(self):
        """Show form and collect input"""
        console.clear()
        
        # Show form title
        title_text = Text(self.title, style="bold cyan")
        console.print(Align.center(Panel(title_text, border_style="green", padding=(1, 2))))
        console.print()
        
        try:
            # Process each field
            for field in self.fields:
                console.print(f"[bold]{field.label}[/bold]")
                
                if field.field_type == "text":
                    while True:
                        if field.multiline:
                            value = prompt_with_esc_support(f"{field.placeholder}", "")
                        else:
                            value = prompt_with_esc_support(f"{field.placeholder}", "")
                        
                        # Check if field is required and validate
                        if field.required and (not value or not value.strip()):
                            console.print(f"[red]❌ {field.label} is required. Please provide a value.[/red]")
                            continue
                        else:
                            break
                    
                    self.form_data[field.name] = value
                    
                elif field.field_type == "dropdown":
                    if field.options:
                        console.print()
                        # Show options
                        table = Table(show_header=True, header_style="bold magenta", box=None)
                        table.add_column("#", style="dim", width=3)
                        table.add_column("Option", style="cyan")
                        table.add_column("Description", style="white")
                        
                        for i, (key, desc) in enumerate(field.options, 1):
                            table.add_row(str(i), key, desc)
                        
                        console.print(table)
                        console.print()
                        
                        while True:
                            try:
                                # For dropdown with <= 9 options, use single key
                                if len(field.options) <= 9:
                                    ch = get_key_with_esc_support(f"Choose option (1-{len(field.options)})")
                                    if ch.isdigit():
                                        choice = int(ch)
                                        if 1 <= choice <= len(field.options):
                                            selected_key = field.options[choice - 1][0]
                                            self.form_data[field.name] = selected_key
                                            console.print(f"\n[green]✓ Selected: {selected_key}[/green]")
                                            break
                                        else:
                                            console.print(f"\n[red]Please enter a number between 1 and {len(field.options)}[/red]")
                                    else:
                                        console.print(f"\n[red]Please enter a valid number[/red]")
                                else:
                                    # For dropdown with >9 options, use multi-digit input
                                    selection = prompt_with_esc_support(f"Choose option (1-{len(field.options)})", "")
                                    if selection.strip():
                                        try:
                                            choice = int(selection.strip())
                                            if 1 <= choice <= len(field.options):
                                                selected_key = field.options[choice - 1][0]
                                                self.form_data[field.name] = selected_key
                                                console.print(f"\n[green]✓ Selected: {selected_key}[/green]")
                                                break
                                            else:
                                                console.print(f"\n[red]Please enter a number between 1 and {len(field.options)}[/red]")
                                        except ValueError:
                                            console.print(f"\n[red]Please enter a valid number[/red]")
                                    else:
                                        console.print(f"\n[red]Please enter a number between 1 and {len(field.options)}[/red]")
                            except SystemExit:
                                raise
                            except Exception:
                                console.print(f"\n[red]Please enter a number between 1 and {len(field.options)}[/red]")
                
                elif field.field_type == "multi_url":
                    urls = []
                    console.print(f"[dim]Enter up to 3 reference URLs for competitor analysis[/dim]")
                    console.print(f"[dim]Press Enter without input to finish, or type 'skip' to skip URLs[/dim]")
                    
                    for i in range(3):
                        url_prompt = f"URL {i+1}/3" if i == 0 else f"URL {i+1}/3 (optional)"
                        url = prompt_with_esc_support(url_prompt, "")
                        
                        if url.lower() == 'skip':
                            break
                        elif url.strip() == "":
                            break
                        elif self.validate_url(url):
                            normalized_url = self.normalize_url(url)
                            urls.append(normalized_url)
                            console.print(f"[green]✓ Added: {normalized_url}[/green]")
                        else:
                            console.print(f"[red]Invalid URL format. Skipping: {url}[/red]")
                    
                    self.form_data[field.name] = urls
                    if urls:
                        console.print(f"[cyan]📎 {len(urls)} reference URL(s) added for competitor analysis[/cyan]")
                    else:
                        console.print(f"[yellow]No URLs added - will use simple generation[/yellow]")
                
                console.print()
            
            # Show summary and confirm
            console.print("[bold cyan]📋 Project Summary:[/bold cyan]")
            for field in self.fields:
                value = self.form_data.get(field.name, "Not set")
                if field.field_type == "multi_url" and isinstance(value, list):
                    if value:
                        console.print(f"  {field.label}: [green]{len(value)} URL(s)[/green]")
                        for i, url in enumerate(value, 1):
                            console.print(f"    {i}. {url}")
                    else:
                        console.print(f"  {field.label}: [yellow]None (simple generation)[/yellow]")
                else:
                    console.print(f"  {field.label}: [green]{value}[/green]")
            
            console.print()
            generate = Confirm.ask("🚀 Generate this project?", default=True)
            
            if generate:
                return 'generate', self.form_data
            else:
                return 'cancel', {}
                
        except (KeyboardInterrupt, EOFError):
            return 'cancel', {}
    
    def show_with_conditional_urls(self):
        """Show form with conditional URL field based on design mode selection"""
        console.clear()
        
        # Show form title
        title_text = Text(self.title, style="bold cyan")
        console.print(Align.center(Panel(title_text, border_style="green", padding=(1, 2))))
        console.print()
        
        try:
            # Process each field
            for field in self.fields:
                # Skip image analysis field if fast mode is selected
                if field.name == "image_analysis" and self.form_data.get('design_mode') == 'fast':
                    self.form_data[field.name] = 'disabled'  # Set default for fast mode
                    continue
                
                console.print(f"[bold]{field.label}[/bold]")
                
                if field.field_type == "text":
                    while True:
                        if field.multiline:
                            value = prompt_with_esc_support(f"{field.placeholder}", "")
                        else:
                            value = prompt_with_esc_support(f"{field.placeholder}", "")
                        
                        # Check if field is required and validate
                        if field.required and (not value or not value.strip()):
                            console.print(f"[red]❌ {field.label} is required. Please provide a value.[/red]")
                            continue
                        else:
                            break
                    
                    self.form_data[field.name] = value
                    
                elif field.field_type == "dropdown":
                    if field.options:
                        console.print()
                        # Show options
                        table = Table(show_header=True, header_style="bold magenta", box=None)
                        table.add_column("#", style="dim", width=3)
                        table.add_column("Option", style="cyan")
                        table.add_column("Description", style="white")
                        
                        for i, (key, desc) in enumerate(field.options, 1):
                            table.add_row(str(i), key, desc)
                        
                        console.print(table)
                        console.print()
                        
                        while True:
                            try:
                                # For dropdown with <= 9 options, use single key
                                if len(field.options) <= 9:
                                    ch = get_key_with_esc_support(f"Choose option (1-{len(field.options)})")
                                    if ch.isdigit():
                                        choice = int(ch)
                                        if 1 <= choice <= len(field.options):
                                            selected_key = field.options[choice - 1][0]
                                            self.form_data[field.name] = selected_key
                                            console.print(f"\n[green]✓ Selected: {selected_key}[/green]")
                                            break
                                        else:
                                            console.print(f"\n[red]Please enter a number between 1 and {len(field.options)}[/red]")
                                    else:
                                        console.print(f"\n[red]Please enter a valid number[/red]")
                                else:
                                    # For dropdown with >9 options, use multi-digit input
                                    selection = prompt_with_esc_support(f"Choose option (1-{len(field.options)})", "")
                                    if selection.strip():
                                        try:
                                            choice = int(selection.strip())
                                            if 1 <= choice <= len(field.options):
                                                selected_key = field.options[choice - 1][0]
                                                self.form_data[field.name] = selected_key
                                                console.print(f"\n[green]✓ Selected: {selected_key}[/green]")
                                                break
                                            else:
                                                console.print(f"\n[red]Please enter a number between 1 and {len(field.options)}[/red]")
                                        except ValueError:
                                            console.print(f"\n[red]Please enter a valid number[/red]")
                                    else:
                                        console.print(f"\n[red]Please enter a number between 1 and {len(field.options)}[/red]")
                            except SystemExit:
                                raise
                            except Exception:
                                console.print(f"\n[red]Please enter a number between 1 and {len(field.options)}[/red]")
                
                console.print()
            
            # Conditionally ask for URLs only if design mode is 'full' AND image analysis is enabled
            design_mode = self.form_data.get('design_mode', 'full')
            image_analysis = self.form_data.get('image_analysis', 'enabled')
            if design_mode == 'full' and image_analysis == 'enabled':
                console.print(f"[bold]🔗 Reference URLs (optional, up to 3)[/bold]")
                urls = []
                console.print(f"[dim]Enter up to 3 reference URLs for competitor analysis[/dim]")
                console.print(f"[dim]Press Enter without input to finish, or type 'skip' to skip URLs[/dim]")
                
                for i in range(3):
                    url_prompt = f"URL {i+1}/3" if i == 0 else f"URL {i+1}/3 (optional)"
                    url = prompt_with_esc_support(url_prompt, "")
                    
                    if url.lower() == 'skip':
                        break
                    elif url.strip() == "":
                        break
                    elif self.validate_url(url):
                        normalized_url = self.normalize_url(url)
                        urls.append(normalized_url)
                        console.print(f"[green]✓ Added: {normalized_url}[/green]")
                    else:
                        console.print(f"[red]Invalid URL format. Skipping: {url}[/red]")
                
                self.form_data['urls'] = urls
                if urls:
                    console.print(f"[cyan]📎 {len(urls)} reference URL(s) added for competitor analysis[/cyan]")
                else:
                    console.print(f"[yellow]No URLs added - will use simple generation approach[/yellow]")
                console.print()
            else:
                # For fast mode or disabled image analysis, set empty URLs list
                self.form_data['urls'] = []
                if design_mode == 'fast':
                    console.print(f"[yellow]⚡ Fast mode selected - skipping reference URL collection[/yellow]")
                else:
                    console.print(f"[yellow]⚡ Image analysis disabled - skipping reference URL collection[/yellow]")
                console.print()
            
            # Show summary and confirm
            console.print("[bold cyan]📋 Project Summary:[/bold cyan]")
            for field in self.fields:
                # Skip image analysis field in summary if fast mode
                if field.name == "image_analysis" and design_mode == 'fast':
                    continue
                value = self.form_data.get(field.name, "Not set")
                console.print(f"  {field.label}: [green]{value}[/green]")
            
            # Show URLs summary
            urls = self.form_data.get('urls', [])
            if design_mode == 'full' and image_analysis == 'enabled':
                if urls:
                    console.print(f"  🔗 Reference URLs: [green]{len(urls)} URL(s)[/green]")
                    for i, url in enumerate(urls, 1):
                        console.print(f"    {i}. {url}")
                else:
                    console.print(f"  🔗 Reference URLs: [yellow]None (simple approach)[/yellow]")
            elif design_mode == 'full' and image_analysis == 'disabled':
                console.print(f"  🔗 Reference URLs: [yellow]N/A (image analysis disabled)[/yellow]")
            else:
                console.print(f"  🔗 Reference URLs: [yellow]N/A (fast mode)[/yellow]")
            
            console.print()
            generate = Confirm.ask("🚀 Generate this project?", default=True)
            
            if generate:
                return 'generate', self.form_data
            else:
                return 'cancel', {}
                
        except (KeyboardInterrupt, EOFError):
            return 'cancel', {}

class CCUXApp:
    """Main CCUX Interactive Application"""
    
    def __init__(self):
        self.current_project = None
        self.projects = []
        self.running = True
    
    def discover_projects(self):
        """Discover existing CCUX projects"""
        from .cli import discover_existing_projects
        self.projects = discover_existing_projects()
    
    def show_welcome(self):
        """Show welcome screen"""
        console.clear()
        welcome_text = Text()
        welcome_text.append("🎨 CCUX - AI Landing Page Generator\n\n", style="bold cyan")
        welcome_text.append("Welcome to CCUX! Create beautiful, conversion-optimized landing pages\n", style="white")
        welcome_text.append("powered by Claude AI and professional UX design methodology.\n\n", style="white")
        
        panel = Panel(
            welcome_text,
            border_style="cyan",
            padding=(2, 4)
        )
        
        console.print(Align.center(panel))
        
        try:
            import sys
            import tty
            import termios
            
            console.print(f"[bold]Ready to start? Press Y/Enter to continue or ESC to exit[/bold]")
            
            # Get single key press
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                
                # Check for ESC key (ASCII 27)
                if ord(ch) == 27:
                    console.print("\n[yellow]ESC pressed - exiting application...[/yellow]")
                    return False
                
                # Enter key or Y key continues
                if ch in ['\r', '\n', 'y', 'Y'] or ord(ch) == 13:
                    console.print("\n[green]Starting CCUX...[/green]")
                    return True
                
                # N key exits
                if ch in ['n', 'N']:
                    return False
                    
                # Any other key continues
                console.print("\n[green]Starting CCUX...[/green]")
                return True
                    
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Interrupted - exiting application...[/yellow]")
            return False
    
    def show_main_menu(self):
        """Show main menu"""
        self.discover_projects()
        project_count = len(self.projects)
        
        options = [
            MenuOption("create", "Create New Project", "Generate a fresh landing page", "🆕"),
            MenuOption("multipage", "Create Multi-Page Website", "Generate complete website with multiple pages", "🌐"),
            MenuOption("manage", f"Manage Existing Projects ({project_count} found)", "Edit, regenerate, or change themes", "📁"),
            MenuOption("help", "Help & Documentation", "Learn how to use CCUX effectively", "❓"),
            MenuOption("exit", "Exit", "Close CCUX application", "❌")
        ]
        
        menu = InteractiveMenu("CCUX - AI Landing Page Generator", options)
        return menu.show()
    
    def show_project_form(self):
        """Show project creation form"""
        from .theme_specifications import get_theme_choices, THEME_SPECIFICATIONS
        
        # Create theme options
        theme_options = []
        for theme in get_theme_choices():
            theme_spec = THEME_SPECIFICATIONS.get(theme)
            if theme_spec:
                desc = theme_spec.description[:40] + "..." if len(theme_spec.description) > 40 else theme_spec.description
            else:
                desc = f'{theme.title()} theme'
            theme_options.append((theme, desc))
        
        # Form options
        form_options = [
            ("none", "No forms"),
            ("contact", "Contact Form (name, email, message)"),
            ("newsletter", "Newsletter Signup (email only)"),
            ("signup", "Full Signup Form (all fields)")
        ]
        
        # Design mode options
        design_mode_options = [
            ("full", "Full Design Process - 12-phase professional methodology with competitor research (takes longer, better results)"),
            ("fast", "Fast Mode - Quick generation without research phases (faster, simpler results)"),
        ]
        
        image_analysis_options = [
            ("enabled", "🔍 Enable Visual Analysis (Higher quality, more tokens)"),
            ("disabled", "⚡ Skip Visual Analysis (Faster, saves tokens)")
        ]
        
        fields = [
            FormField("description", "📝 Project Description", "text", 
                     placeholder="Describe your project (e.g., 'AI-powered task manager')", 
                     required=True, multiline=True),
            FormField("design_mode", "🧠 Design Process", "dropdown", "full", design_mode_options),
            FormField("theme", "🎨 Theme", "dropdown", "minimal", theme_options),
            FormField("image_analysis", "📸 Competitor Screenshot Analysis", "dropdown", "enabled", image_analysis_options),
            FormField("forms", "📝 Contact Forms", "dropdown", "none", form_options),
        ]
        
        form = InteractiveForm("Create New Project", fields)
        return form.show_with_conditional_urls()
    
    def show_multipage_form(self):
        """Show multi-page website creation form"""
        from .theme_specifications import get_theme_choices, THEME_SPECIFICATIONS
        
        # Create theme options
        theme_options = []
        for theme in get_theme_choices():
            theme_spec = THEME_SPECIFICATIONS.get(theme)
            if theme_spec:
                desc = theme_spec.description[:40] + "..." if len(theme_spec.description) > 40 else theme_spec.description
            else:
                desc = f'{theme.title()} theme'
            theme_options.append((theme, desc))
        
        fields = [
            FormField("description", "📝 Product Description", "text", 
                     placeholder="Describe your product/service for multi-page website generation", 
                     required=True, multiline=True),
            FormField("theme", "🎨 Theme", "dropdown", "minimal", theme_options),
            FormField("base_url", "🌐 Base URL", "text", "https://example.com",
                     placeholder="Base URL for SEO sitemap (e.g., https://mysite.com)")
        ]
        
        form = InteractiveForm("Create Multi-Page Website", fields)
        return form.show()
    
    def generate_project(self, desc: str, theme: str, include_forms: bool, output_dir: str, urls: List[str] = None, design_mode: str = "full", analyze_images: bool = True) -> bool:
        """Generate project using either full design methodology or fast mode"""
        if design_mode == "fast":
            return self.generate_project_fast(desc, theme, include_forms, output_dir, urls)
        else:
            return self.generate_project_full(desc, theme, include_forms, output_dir, urls, analyze_images)
    
    def generate_project_full(self, desc: str, theme: str, include_forms: bool, output_dir: str, urls: List[str] = None, analyze_images: bool = True) -> bool:
        """Generate project using full 12-phase design thinking methodology"""
        try:
            # Import comprehensive design logic
            from .cli import (
                summarize_long_description, 
                get_theme_choices,
                run_claude_with_progress,
                strip_code_blocks,
                os
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
                implementation_prompt
            )
            import json
            import time
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Validate inputs
            if theme not in get_theme_choices():
                console.print(f"[red]Invalid theme: {theme}[/red]")
                return False
            
            # Summarize description if too long
            desc = summarize_long_description(desc)
            
            console.print(f"[bold green]🧠 Running comprehensive 12-phase design thinking process...[/bold green]")
            console.print(f"Framework: [green]html[/green] | Theme: [green]{theme}[/green] | URLs: [cyan]{len(urls) if urls else 0}[/cyan]")
            
            from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
            from rich.table import Table
            
            # Show design phase overview
            phase_table = Table(show_header=True, header_style="bold magenta")
            phase_table.add_column("Phase", style="cyan", width=8)
            phase_table.add_column("Process", style="green")
            phase_table.add_row("1-2", "Reference Discovery & Screenshot Capture")
            phase_table.add_row("3-5", "Product Analysis, UX Analysis & User Research") 
            phase_table.add_row("6-8", "Site Flow, Content Strategy & Wireframing")
            phase_table.add_row("9-11", "Design System, Visual Design & Prototyping")
            phase_table.add_row("12", "Final Implementation & Code Generation")
            console.print(phase_table)
            console.print()
            
            # Initialize design analysis data
            analysis_data = {
                'project_metadata': {
                    'product_description': desc,
                    'theme': theme,
                    'framework': 'html',
                    'include_forms': include_forms,
                    'reference_urls': urls or [],
                    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'sections': ['hero', 'features', 'pricing', 'footer']
                },
                'design_phases': {}
            }
            
            # Phase 1: Reference Discovery (only if image analysis is enabled)
            if analyze_images:
                # Reference Discovery (if URLs not provided, auto-discover)
                if not urls or len(urls) == 0:
                    console.print("\n[bold blue]📋 Phase 1/12: Reference Discovery[/bold blue]")
                    ref_prompt = reference_discovery_prompt(desc)
                    ref_output, ref_stats = run_claude_with_progress(ref_prompt, "Discovering competitor references...")
                    analysis_data['design_phases']['reference_discovery'] = {
                        'output': ref_output,
                        'stats': ref_stats
                    }
                    
                    # Extract URLs from Claude's response (simplified for now)
                    import re
                    discovered_urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', ref_output)
                    urls = discovered_urls[:3] if discovered_urls else []
                    analysis_data['project_metadata']['reference_urls'] = urls
                    
                    if urls:
                        console.print(f"[green]✓ Discovered {len(urls)} reference URLs[/green]")
                        for i, url in enumerate(urls, 1):
                            console.print(f"   {i}. {url}")
                    else:
                        console.print("[yellow]No reference URLs discovered, continuing with original approach[/yellow]")
                else:
                    console.print(f"\n[bold blue]📋 Phase 1/12: Using provided reference URLs ({len(urls)})[/bold blue]")
                    for i, url in enumerate(urls, 1):
                        console.print(f"   {i}. {url}")
            else:
                console.print("\n[bold blue]📋 Phase 1/12: Skipping Reference Discovery (image analysis disabled)[/bold blue]")
                urls = []
                analysis_data['project_metadata']['reference_urls'] = []
            
            # Phase 2: Screenshot Capture (only if image analysis is enabled)
            screenshot_refs = []
            if urls and len(urls) > 0 and analyze_images:
                console.print(f"\n[bold blue]📸 Phase 2/12: Capturing {len(urls)} reference screenshots[/bold blue]")
                try:
                    from .scrape import capture_multiple_references
                    screenshot_results = capture_multiple_references(urls, output_dir)
                    screenshot_refs = [(url, screenshot_path) for url, _, screenshot_path in screenshot_results]
                    console.print(f"[green]✓ Captured {len(screenshot_refs)} screenshots[/green]")
                except Exception as e:
                    console.print(f"[yellow]⚠️ Screenshot capture failed: {e}[/yellow]")
                    console.print("[yellow]Continuing without screenshots...[/yellow]")
            elif not analyze_images:
                console.print("\n[bold blue]📸 Phase 2/12: Skipping Screenshot Capture (image analysis disabled)[/bold blue]")
            
            # Phase 3: Deep Product Understanding
            console.print("\n[bold blue]🎯 Phase 3/12: Product Analysis[/bold blue]")
            product_prompt = deep_product_understanding_prompt(desc)
            product_output, product_stats = run_claude_with_progress(product_prompt, "Analyzing product positioning...")
            product_understanding = safe_json_parse(product_output)
            analysis_data['design_phases']['product_understanding'] = {
                'output': product_output,
                'stats': product_stats
            }
            
            # Phase 4: Competitive UX Analysis
            ux_analysis = {}
            if screenshot_refs and analyze_images:
                console.print("\n[bold blue]🔍 Phase 4/12: Competitive UX Analysis (Visual)[/bold blue]")
                # Extract only the screenshot paths from the tuples
                screenshot_paths = [screenshot_path for url, screenshot_path in screenshot_refs]
                ux_prompt = ux_analysis_prompt(desc, screenshot_paths)
                ux_output, ux_stats = run_claude_with_progress(ux_prompt, "Analyzing competitor UX patterns...", enable_image_analysis=True)
                ux_analysis = safe_json_parse(ux_output)
                analysis_data['design_phases']['ux_analysis'] = {
                    'output': ux_output,
                    'stats': ux_stats
                }
            elif screenshot_refs and not analyze_images:
                console.print("\n[bold blue]⏭️  Phase 4/12: Competitive UX Analysis (Skipped)[/bold blue]")
                console.print("   [dim]Screenshots captured but visual analysis disabled to save tokens[/dim]")
            
            # Phase 5: User Empathy Mapping
            console.print("\n[bold blue]👥 Phase 5/12: User Research[/bold blue]")
            empathy_prompt = empathize_prompt(desc, product_understanding, ux_analysis)
            empathy_output, empathy_stats = run_claude_with_progress(empathy_prompt, "Creating user empathy maps...")
            user_research = safe_json_parse(empathy_output)
            analysis_data['design_phases']['empathy_mapping'] = {
                'output': empathy_output,
                'stats': empathy_stats
            }
            
            # Phase 6: Define Site Flow
            console.print("\n[bold blue]🗺️ Phase 6/12: Site Flow Definition[/bold blue]")
            define_prompt_text = define_prompt(desc, user_research)
            define_output, define_stats = run_claude_with_progress(define_prompt_text, "Mapping user journey...")
            site_flow = safe_json_parse(define_output)
            analysis_data['design_phases']['site_flow'] = {
                'output': define_output,
                'stats': define_stats
            }
            
            # Phase 7: Content Strategy
            console.print("\n[bold blue]📝 Phase 7/12: Content Strategy[/bold blue]")
            ideate_prompt_text = ideate_prompt(desc, user_research, site_flow)
            ideate_output, ideate_stats = run_claude_with_progress(ideate_prompt_text, "Developing content strategy...")
            content_strategy = safe_json_parse(ideate_output)
            analysis_data['design_phases']['content_strategy'] = {
                'output': ideate_output,
                'stats': ideate_stats
            }
            
            # Phase 8: Wireframe Validation
            console.print("\n[bold blue]📐 Phase 8/12: Wireframe Validation[/bold blue]")
            wireframe_prompt_text = wireframe_prompt(desc, content_strategy, site_flow)
            wireframe_output, wireframe_stats = run_claude_with_progress(wireframe_prompt_text, "Validating layout structure...")
            wireframes = safe_json_parse(wireframe_output)
            analysis_data['design_phases']['wireframe'] = {
                'output': wireframe_output,
                'stats': wireframe_stats
            }
            
            # Phase 9: Design System
            console.print("\n[bold blue]🎨 Phase 9/12: Design System[/bold blue]")
            design_sys_prompt = design_system_prompt(desc, wireframes, content_strategy, theme)
            design_sys_output, design_sys_stats = run_claude_with_progress(design_sys_prompt, "Creating design system...")
            design_system = safe_json_parse(design_sys_output)
            analysis_data['design_phases']['design_system'] = {
                'output': design_sys_output,
                'stats': design_sys_stats
            }
            
            # Phase 10: High-Fidelity Design
            console.print("\n[bold blue]✨ Phase 10/12: High-Fidelity Design[/bold blue]")
            hifi_prompt = high_fidelity_design_prompt(desc, design_system, wireframes, content_strategy)
            hifi_output, hifi_stats = run_claude_with_progress(hifi_prompt, "Polishing visual design...")
            hifi_design = safe_json_parse(hifi_output)
            analysis_data['design_phases']['high_fidelity'] = {
                'output': hifi_output,
                'stats': hifi_stats
            }
            
            # Phase 11: Prototype Validation
            console.print("\n[bold blue]🔄 Phase 11/12: Interactive Prototype[/bold blue]")
            proto_prompt = prototype_prompt(desc, content_strategy, design_system, wireframes)
            proto_output, proto_stats = run_claude_with_progress(proto_prompt, "Adding interactions...")
            final_copy = safe_json_parse(proto_output)
            analysis_data['design_phases']['prototype'] = {
                'output': proto_output,
                'stats': proto_stats
            }
            
            # Phase 12: Final Implementation
            console.print("\n[bold blue]⚡ Phase 12/12: Code Generation[/bold blue]")
            # Build design_data structure for implementation_prompt
            design_data = {
                'design_system': design_system,
                'content_strategy': content_strategy,
                'ux_analysis': ux_analysis
            }
            impl_prompt = implementation_prompt(
                desc, final_copy, 'html', theme, design_data, 
                include_forms
            )
            code_output, impl_stats = run_claude_with_progress(impl_prompt, "Generating production code...")
            analysis_data['design_phases']['implementation'] = {
                'output': code_output,
                'stats': impl_stats
            }
            
            # Calculate total usage stats
            total_stats = {'input_tokens': 0, 'output_tokens': 0, 'cost': 0.0}
            for phase_data in analysis_data['design_phases'].values():
                stats = phase_data.get('stats', {})
                total_stats['input_tokens'] += stats.get('input_tokens', 0)
                total_stats['output_tokens'] += stats.get('output_tokens', 0)
                total_stats['cost'] += stats.get('cost', 0.0)
            
            analysis_data['total_usage'] = total_stats
            
            # Save design analysis
            with open(os.path.join(output_dir, 'design_analysis.json'), 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            # Save final code
            cleaned_code = strip_code_blocks(code_output)
            with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                f.write(cleaned_code)
            
            console.print(f"\n[bold green]✅ Complete 12-phase design process finished![/bold green]")
            console.print(f"[cyan]📊 Total tokens: {total_stats['input_tokens']} in, {total_stats['output_tokens']} out[/cyan]")
            if total_stats['cost'] > 0:
                console.print(f"[cyan]💰 Estimated cost: ${total_stats['cost']:.3f}[/cyan]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Generation error: {e}[/red]")
            return False
    
    def generate_project_fast(self, desc: str, theme: str, include_forms: bool, output_dir: str, urls: List[str] = None) -> bool:
        """Generate project using fast mode - direct generation without design thinking phases"""
        try:
            from .cli import (
                summarize_long_description, 
                get_theme_choices,
                run_claude_with_progress,
                strip_code_blocks
            )
            from .prompt_templates import landing_prompt
            
            # Validate inputs
            if theme not in get_theme_choices():
                console.print(f"[red]Invalid theme: {theme}[/red]")
                return False
            
            # Summarize description if too long
            desc = summarize_long_description(desc)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            console.print("\n[bold yellow]⚡ Fast generation mode (no design thinking, no reference URLs)[/bold yellow]")
            
            # Generate landing page directly
            console.print("\n[bold blue]🚀 Generating landing page...[/bold blue]")
            sections = ['hero', 'features', 'pricing', 'footer']
            prompt = landing_prompt(desc, 'html', theme, sections, include_forms=include_forms)
            output, stats = run_claude_with_progress(prompt, "Creating your landing page...")
            
            # Save output
            html_file = os.path.join(output_dir, 'index.html')
            with open(html_file, 'w') as f:
                f.write(strip_code_blocks(output))
            
            # Save minimal design analysis for cost tracking
            fast_analysis = {
                'generation_mode': 'fast',
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'product_description': desc,
                'theme': theme,
                'framework': 'html',
                'include_forms': include_forms,
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
            
            console.print(f"[green]✅ Landing page generated successfully![/green]")
            console.print(f"[cyan]💰 Cost: ${stats.get('cost', 0.0):.3f} | Tokens: {stats.get('input_tokens', 0):,} in, {stats.get('output_tokens', 0):,} out[/cyan]")
            console.print(f"[dim]🌐 Preview: cd {output_dir} && python -m http.server 3000[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Fast generation error: {e}[/red]")
            return False
    
    def show_project_menu(self):
        """Show project management menu"""
        if not self.current_project:
            return
        
        while True:
            project_name = f"Project ({self.current_project}/)"
            
            options = [
                MenuOption("theme", "Change Theme", "Switch to different visual style", "🎨"),
                MenuOption("edit", "Edit Content", "Modify text, headlines, copy", "✏️"),
                MenuOption("regen", "Regenerate Sections", "Recreate hero, features, pricing, etc.", "🔄"),
                MenuOption("forms", "Manage Forms", "Add, remove, or customize contact forms", "📝"),
                MenuOption("preview", "Preview Project", "Open in browser", "🌐"),
                MenuOption("back", "Back to Main Menu", "Return to main menu", "⬅️")
            ]
            
            menu = InteractiveMenu(f"Manage {project_name}", options)
            action = menu.show()
            
            if action == 'theme':
                self.show_theme_interface()
            elif action == 'edit':
                self.show_edit_interface()
            elif action == 'regen':
                self.show_regen_interface()
            elif action == 'forms':
                self.show_forms_interface()
            elif action == 'preview':
                self.preview_project()
            elif action == 'back' or action == 'exit':
                self.current_project = None
                break
    
    def show_theme_interface(self):
        """Show theme change interface"""
        from .theme_specifications import get_theme_choices, THEME_SPECIFICATIONS
        
        console.print(f"\n[bold cyan]🎨 Change Theme for: {self.current_project}/[/bold cyan]")
        
        # Show theme options
        theme_options = []
        for theme in get_theme_choices():
            theme_spec = THEME_SPECIFICATIONS.get(theme)
            if theme_spec:
                desc = theme_spec.description[:50] + "..." if len(theme_spec.description) > 50 else theme_spec.description
            else:
                desc = f'{theme.title()} theme'
            theme_options.append((theme, desc))
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Theme", style="cyan")
        table.add_column("Description", style="white")
        
        for i, (theme, desc) in enumerate(theme_options, 1):
            table.add_row(str(i), theme, desc)
        
        console.print(table)
        
        try:
            choice = IntPrompt.ask(f"[bold]Choose new theme (1-{len(theme_options)})[/bold]", default=1)
            if 1 <= choice <= len(theme_options):
                new_theme = theme_options[choice - 1][0]
                
                if Confirm.ask(f"[yellow]⚠️  This will regenerate your page with the '{new_theme}' theme. Continue?[/yellow]", default=False):
                    console.print(f"[green]🎨 Applying {new_theme} theme...[/green]")
                    # Import and call theme change function from cli_old
                    from . import cli_old
                    try:
                        # Find the HTML file
                        html_file = os.path.join(self.current_project, 'index.html')
                        if os.path.exists(html_file):
                            # Call the theme change logic with new theme
                            cli_old.theme(new_theme, file=html_file, output_dir=self.current_project)
                            console.print(f"[green]✅ Theme changed to {new_theme}![/green]")
                        else:
                            console.print("[red]❌ HTML file not found[/red]")
                    except Exception as e:
                        console.print(f"[red]❌ Error changing theme: {e}[/red]")
                    
        except (KeyboardInterrupt, EOFError):
            pass
        
        Prompt.ask("Press Enter to continue", default="")
    
    def show_edit_interface(self):
        """Show content editing interface"""
        console.print(f"\n[bold cyan]✏️  Edit Content: {self.current_project}/[/bold cyan]")
        console.print("What would you like to change?")
        
        instruction = Prompt.ask("[bold]Edit instruction[/bold]", default="")
        if instruction:
            # Import and call editgen function from cli_old
            from . import cli_old
            try:
                html_file = os.path.join(self.current_project, 'index.html')
                if os.path.exists(html_file):
                    cli_old.editgen(instruction, file=html_file, output_dir=self.current_project)
                    console.print(f"[green]✅ Content edited successfully![/green]")
                else:
                    console.print("[red]❌ HTML file not found[/red]")
            except Exception as e:
                console.print(f"[red]❌ Error editing content: {e}[/red]")
        
        Prompt.ask("Press Enter to continue", default="")
    
    def detect_sections_from_html(self, html_file_path: str) -> List[str]:
        """Detect available sections from HTML file by looking for various section markers"""
        sections = []
        try:
            if not os.path.exists(html_file_path):
                return sections
                
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # Method 1: Look for comment markers: <!-- START: section_name -->
            comment_sections = re.findall(r'<!-- START: (\w+) -->', content)
            sections.extend(comment_sections)
            
            # Method 2: Look for <section id="section_name">
            section_tags = re.findall(r'<section[^>]+id=["\']([^"\']+)["\']', content)
            sections.extend(section_tags)
            
            # Method 3: Look for <div id="section_name"> with common section names
            common_sections = ['header', 'nav', 'navigation', 'hero', 'features', 'pricing', 'testimonials', 'stats', 'about', 'contact', 'footer', 'cards', 'team', 'faq', 'cta']
            div_sections = re.findall(r'<div[^>]+id=["\']([^"\']+)["\']', content)
            for div_id in div_sections:
                if any(section_name in div_id.lower() for section_name in common_sections):
                    sections.append(div_id)
            
            # Method 4: Look for navigation/header elements without section markers
            if re.search(r'<nav[^>]*>', content) and not any('header' in s.lower() or 'nav' in s.lower() for s in sections):
                sections.append('header')
            
            # Method 5: Look for explicit header tags
            header_tags = re.findall(r'<header[^>]+id=["\']([^"\']+)["\']', content)
            sections.extend(header_tags)
            
            # Remove duplicates and sort
            sections = list(set(sections))
            sections.sort()
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read HTML file: {e}[/yellow]")
        
        return sections

    def detect_current_theme(self) -> str:
        """Detect current theme from design analysis or HTML"""
        try:
            # Try design analysis first
            analysis_file = os.path.join(self.current_project, 'design_analysis.json')
            if os.path.exists(analysis_file):
                import json
                with open(analysis_file, 'r') as f:
                    analysis = json.load(f)
                    # Handle both fast mode (theme at root) and full mode (theme in project_metadata)
                    theme = analysis.get('theme') or analysis.get('project_metadata', {}).get('theme', 'minimal')
                    return theme
            
            # Fallback: try to detect from HTML content (basic detection)
            html_file = os.path.join(self.current_project, 'index.html')
            if os.path.exists(html_file):
                with open(html_file, 'r') as f:
                    content = f.read()
                
                # Simple theme detection based on CSS classes
                if 'brutalist-border' in content or 'font-black' in content:
                    return 'brutalist'
                elif 'bg-gradient-to-r' in content and 'rounded-xl' in content:
                    return 'playful'
                elif 'bg-blue-900' in content and 'font-semibold' in content:
                    return 'corporate'
                else:
                    return 'minimal'
                    
        except Exception:
            pass
        
        return 'minimal'  # Default fallback

    def select_theme_interactive(self) -> str:
        """Show theme selection interface and return selected theme"""
        from .theme_specifications import get_theme_choices, THEME_SPECIFICATIONS
        
        theme_options = []
        for theme in get_theme_choices():
            theme_spec = THEME_SPECIFICATIONS.get(theme)
            if theme_spec:
                desc = theme_spec.description[:40] + "..." if len(theme_spec.description) > 40 else theme_spec.description
            else:
                desc = f'{theme.title()} theme'
            theme_options.append((theme, desc))
        
        console.print(f"\n[bold cyan]🎨 Select New Theme:[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Theme", style="cyan")
        table.add_column("Description", style="white")
        
        for i, (theme, desc) in enumerate(theme_options, 1):
            table.add_row(str(i), theme, desc)
        
        console.print(table)
        
        try:
            choice = IntPrompt.ask(f"[bold]Choose theme (1-{len(theme_options)})[/bold]", default=1)
            if 1 <= choice <= len(theme_options):
                return theme_options[choice - 1][0]
        except (KeyboardInterrupt, EOFError):
            pass
        
        return None

    def show_regen_interface(self):
        """Show section regeneration interface with section detection and theme options"""
        console.print(f"\n[bold cyan]🔄 Regenerate Sections: {self.current_project}/[/bold cyan]")
        
        # Detect available sections from HTML file
        html_file = os.path.join(self.current_project, 'index.html')
        available_sections = self.detect_sections_from_html(html_file)
        
        if not available_sections:
            console.print("[red]❌ Could not detect sections in HTML file[/red]")
            Prompt.ask("Press Enter to continue", default="")
            return
        
        console.print(f"[green]📋 Found {len(available_sections)} sections in your HTML:[/green]")
        
        # Show available sections
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Section", style="cyan")
        table.add_column("Status", style="green")
        
        for i, section in enumerate(available_sections, 1):
            table.add_row(str(i), section.title(), "✓ Available")
        
        console.print(table)
        console.print()
        
        # Section selection
        selections = Prompt.ask("[bold]Enter section numbers (e.g., 1,3,5) or 'all'[/bold]", default="1")
        
        selected_sections = []
        if selections.lower() == 'all':
            selected_sections = available_sections
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selections.split(',')]
                selected_sections = [available_sections[i] for i in indices if 0 <= i < len(available_sections)]
            except:
                console.print("[red]Invalid selection[/red]")
                Prompt.ask("Press Enter to continue", default="")
                return
        
        if not selected_sections:
            console.print("[yellow]No sections selected[/yellow]")
            Prompt.ask("Press Enter to continue", default="")
            return
        
        console.print(f"[green]📝 Selected sections: {', '.join(selected_sections)}[/green]")
        
        # Theme selection option
        current_theme = self.detect_current_theme()
        console.print(f"[cyan]🎨 Current theme: {current_theme}[/cyan]")
        
        change_theme = Confirm.ask("[bold]Would you like to change the theme during regeneration?[/bold]", default=False)
        
        new_theme = current_theme
        if change_theme:
            selected_theme = self.select_theme_interactive()
            if selected_theme and selected_theme != current_theme:
                new_theme = selected_theme
                console.print(f"[green]✅ Theme will be changed to: {new_theme}[/green]")
            else:
                console.print(f"[yellow]Theme remains: {current_theme}[/yellow]")
        
        # Confirm regeneration
        console.print(f"\n[bold yellow]⚠️  Regeneration Summary:[/bold yellow]")
        console.print(f"• Sections: {', '.join(selected_sections)}")
        console.print(f"• Theme: {new_theme}")
        console.print(f"• This will overwrite existing content in these sections")
        
        if Confirm.ask("\n[bold]Proceed with regeneration?[/bold]", default=True):
            console.print(f"[green]🔄 Regenerating {len(selected_sections)} section(s)...[/green]")
            
            # Call the internal regeneration function directly
            from .cli_old import _regenerate_sections_internal
            try:
                html_file = os.path.join(self.current_project, 'index.html')
                if os.path.exists(html_file):
                    success = _regenerate_sections_internal(
                        sections_to_regenerate=selected_sections,
                        target_file=html_file,
                        output_dir=self.current_project,
                        description=None  # Auto-detect from design analysis
                    )
                    if success:
                        console.print("[green]✅ Sections regenerated successfully![/green]")
                    else:
                        console.print("[red]❌ Section regeneration failed[/red]")
                else:
                    console.print("[red]❌ HTML file not found[/red]")
            except Exception as e:
                console.print(f"[red]❌ Error regenerating sections: {e}[/red]")
        
        Prompt.ask("Press Enter to continue", default="")
    
    def show_forms_interface(self):
        """Show form management interface"""
        console.print(f"\n[bold cyan]📝 Manage Forms: {self.current_project}/[/bold cyan]")
        
        options = [
            MenuOption("add", "Add Forms", "Add contact forms to the page", "➕"),
            MenuOption("remove", "Remove Forms", "Remove all forms", "➖"),
            MenuOption("edit", "Edit Forms", "Customize form fields and styling", "✏️"),
            MenuOption("back", "Back", "Return to project menu", "⬅️")
        ]
        
        menu = InteractiveMenu("Form Management", options)
        action = menu.show()
        
        if action == 'add':
            console.print("[green]📝 Adding contact forms...[/green]")
            # Import and call form function from cli_old
            from . import cli_old
            try:
                html_file = os.path.join(self.current_project, 'index.html')
                if os.path.exists(html_file):
                    cli_old.form('on', file=html_file, output_dir=self.current_project)
                    console.print("[green]✅ Forms added![/green]")
                else:
                    console.print("[red]❌ HTML file not found[/red]")
            except Exception as e:
                console.print(f"[red]❌ Error adding forms: {e}[/red]")
        elif action == 'remove':
            console.print("[yellow]📝 Removing all forms...[/yellow]")
            from . import cli_old
            try:
                html_file = os.path.join(self.current_project, 'index.html')
                if os.path.exists(html_file):
                    cli_old.form('off', file=html_file, output_dir=self.current_project)
                    console.print("[green]✅ Forms removed![/green]")
                else:
                    console.print("[red]❌ HTML file not found[/red]")
            except Exception as e:
                console.print(f"[red]❌ Error removing forms: {e}[/red]")
        elif action == 'edit':
            console.print("[blue]📝 Opening form editor...[/blue]")
            from . import cli_old
            try:
                html_file = os.path.join(self.current_project, 'index.html')
                if os.path.exists(html_file):
                    cli_old.form('edit', file=html_file, output_dir=self.current_project)
                    console.print("[green]✅ Forms customized![/green]")
                else:
                    console.print("[red]❌ HTML file not found[/red]")
            except Exception as e:
                console.print(f"[red]❌ Error editing forms: {e}[/red]")
        
        if action != 'back':
            Prompt.ask("Press Enter to continue", default="")
    
    def preview_project(self):
        """Preview project in browser"""
        console.print(f"[cyan]🌐 To preview your project:[/cyan]")
        console.print(f"  1. cd {self.current_project}")
        console.print("  2. python -m http.server 3000")
        console.print("  3. Open http://localhost:3000 in your browser")
        
        Prompt.ask("Press Enter to continue", default="")
    
    def run(self):
        """Main application loop"""
        if not self.show_welcome():
            return
        
        while self.running:
            action = self.show_main_menu()
            
            if action == 'create':
                result, form_data = self.show_project_form()
                if result == 'generate':
                    console.print("\n[green]🚀 Generating your landing page...[/green]")
                    
                    # Get form data
                    desc = form_data.get('description', '')
                    design_mode = form_data.get('design_mode', 'full')
                    theme = form_data.get('theme', 'minimal')
                    forms = form_data.get('forms', 'none')
                    image_analysis_mode = form_data.get('image_analysis', 'enabled')
                    urls = form_data.get('urls', [])
                    include_forms = forms != 'none'
                    analyze_images = image_analysis_mode == 'enabled'
                    
                    # Additional validation for description
                    if not desc or not desc.strip():
                        console.print("[red]❌ Product description is required. Cannot proceed without a description.[/red]")
                        Prompt.ask("Press Enter to continue", default="")
                        continue
                    
                    # Get next available output directory
                    from .cli import get_next_available_output_dir
                    output_dir = get_next_available_output_dir()
                    
                    console.print(f"[cyan]Description:[/cyan] {desc}")
                    console.print(f"[cyan]Design Mode:[/cyan] {'🚀 Full Design Process (12 phases)' if design_mode == 'full' else '⚡ Fast Mode'}")
                    console.print(f"[cyan]Theme:[/cyan] {theme}")
                    console.print(f"[cyan]Forms:[/cyan] {forms}")
                    console.print(f"[cyan]Image Analysis:[/cyan] {'🔍 Enabled (high quality)' if analyze_images else '⚡ Disabled (saves tokens)'}")
                    console.print(f"[cyan]URLs:[/cyan] {len(urls)} reference URL(s)" if urls else "[yellow]None (simple generation)[/yellow]")
                    console.print(f"[cyan]Output:[/cyan] {output_dir}/")
                    
                    # Call the actual generation logic
                    try:
                        success = self.generate_project(desc, theme, include_forms, output_dir, urls, design_mode, analyze_images)
                        if success:
                            console.print(f"\n[green]✅ Project created successfully in {output_dir}/![/green]")
                            
                            # For fast mode, terminate immediately after showing success
                            if design_mode == 'fast':
                                return  # Exit the interactive app immediately
                            
                            # For full mode, offer project management
                            if Confirm.ask("\n[bold]Would you like to manage this project now?[/bold]", default=True):
                                self.current_project = output_dir
                                self.show_project_menu()
                        else:
                            console.print("\n[red]❌ Project generation failed[/red]")
                            
                    except Exception as e:
                        console.print(f"\n[red]❌ Error generating project: {e}[/red]")
                    
                    Prompt.ask("Press Enter to continue", default="")
                
            elif action == 'multipage':
                result, form_data = self.show_multipage_form()
                if result == 'generate':
                    console.print("\n[green]🚀 Generating your multi-page website...[/green]")
                    
                    # Get form data
                    desc = form_data.get('description', '')
                    theme = form_data.get('theme', 'minimal')
                    base_url = form_data.get('base_url', 'https://example.com')
                    
                    # Additional validation for description
                    if not desc or not desc.strip():
                        console.print("[red]❌ Product description is required. Cannot proceed without a description.[/red]")
                        Prompt.ask("Press Enter to continue", default="")
                        continue
                    
                    # Get next available output directory
                    from .core.project_management import get_next_available_output_dir
                    output_dir = get_next_available_output_dir()
                    
                    console.print(f"[cyan]Description:[/cyan] {desc}")
                    console.print(f"[cyan]Theme:[/cyan] {theme}")
                    console.print(f"[cyan]Base URL:[/cyan] {base_url}")
                    console.print(f"[cyan]Output:[/cyan] {output_dir}/")
                    
                    # Call the multipage generation logic
                    try:
                        from .multipage import run_multipage_generation
                        results = run_multipage_generation(desc, output_dir, theme, base_url)
                        
                        if results.get('success', False):
                            console.print(f"\n[green]✅ Multi-page website created successfully in {output_dir}/![/green]")
                            console.print(f"[green]Generated {results.get('pages_generated', 0)} pages with navigation and SEO files![/green]")
                        else:
                            console.print("\n[red]❌ Multi-page website generation failed[/red]")
                            if results.get('error'):
                                console.print(f"[red]Error: {results['error']}[/red]")
                            
                    except Exception as e:
                        console.print(f"\n[red]❌ Error generating multi-page website: {e}[/red]")
                    
                    Prompt.ask("Press Enter to continue", default="")
                
            elif action == 'manage':
                if not self.projects:
                    console.print("\n[yellow]No existing projects found.[/yellow]")
                    Prompt.ask("Press Enter to continue", default="")
                else:
                    # Show project selection
                    console.clear()
                    console.print(f"\n[bold cyan]📁 Select Project to Manage ({len(self.projects)} found):[/bold cyan]")
                    
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("#", style="dim", width=3)
                    table.add_column("Directory", style="cyan")
                    table.add_column("Project Name", style="green")
                    
                    for i, project in enumerate(self.projects, 1):
                        table.add_row(str(i), project['directory'], project['name'])
                    
                    console.print(table)
                    
                    try:
                        choice = IntPrompt.ask(f"[bold]Choose project (1-{len(self.projects)})[/bold]", default=1)
                        if 1 <= choice <= len(self.projects):
                            selected_project = self.projects[choice - 1]
                            self.current_project = selected_project['directory']
                            console.print(f"[green]✅ Selected: {self.current_project}/[/green]")
                            self.show_project_menu()
                        else:
                            console.print(f"[red]Please enter a number between 1 and {len(self.projects)}[/red]")
                    except (KeyboardInterrupt, EOFError):
                        pass
                
            elif action == 'help':
                console.print("\n[cyan]📚 CCUX Help & Documentation[/cyan]")
                console.print("\n[bold]CCUX Features:[/bold]")
                console.print("• 🆕 [cyan]Single-Page Generation[/cyan] - Professional landing pages with 12-phase design methodology")
                console.print("• 🌐 [cyan]Multi-Page Websites[/cyan] - Complete websites with intelligent page detection and parallel generation")
                console.print("• 🤖 [cyan]AI-Powered Content[/cyan] - Claude AI generates optimized content and design")
                console.print("• 🎨 [cyan]13 Professional Themes[/cyan] - From minimal to brutalist to morphism")
                console.print("• 📱 [cyan]Mobile-First Design[/cyan] - Responsive design that works on all devices")
                console.print("• ♿ [cyan]Accessibility[/cyan] - WCAG compliance and semantic HTML")
                console.print("• 🔍 [cyan]SEO Optimization[/cyan] - Automatic sitemaps, meta tags, and schema markup")
                
                console.print("\n[bold]Multi-Page Features:[/bold]")
                console.print("• 🧠 Smart page analysis and suggestions")
                console.print("• ⚡ Parallel generation for faster results")
                console.print("• 🔗 Automatic navigation and cross-linking")
                console.print("• 📊 XML/HTML sitemaps and robots.txt")
                console.print("• 🛡️ Graceful error handling and retry logic")
                
                console.print("\n[bold]Getting Started:[/bold]")
                console.print("1. Choose 'Create New Project' for single landing pages")
                console.print("2. Choose 'Create Multi-Page Website' for complete websites")
                console.print("3. Follow the interactive prompts")
                console.print("4. Your website will be generated with professional quality")
                
                console.print("\nFor more info, visit: https://github.com/thisisharsh7/claude-cli-wrapper")
                Prompt.ask("Press Enter to continue", default="")
                
            elif action == 'exit':
                console.print("\n[cyan]👋 Thanks for using CCUX![/cyan]")
                self.running = False
                break
            
            else:
                self.running = False
                break

def run_interactive_app():
    """Entry point for interactive application"""
    try:
        app = CCUXApp()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        console.print("Please report this issue on GitHub")