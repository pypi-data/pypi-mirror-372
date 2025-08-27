"""
Page Selection Module

Interactive page selection interface for multi-page website generation.
Provides rich terminal interface for users to select/deselect pages.
"""

from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, IntPrompt
from rich.panel import Panel
from rich.align import Align
from rich.text import Text


class PageSelector:
    """Interactive page selection interface"""
    
    def __init__(self):
        self.console = Console()
    
    def show_analysis_results(self, analysis: Dict[str, Any]) -> None:
        """Display the analysis results in a formatted way"""
        
        self.console.print(f"\n[bold cyan]🔍 Page Analysis Complete[/bold cyan]")
        self.console.print(f"[dim]{analysis['analysis_summary']}[/dim]")
        
        # Create suggestions table
        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Page Type", style="cyan", width=15)
        table.add_column("Description", style="white")
        table.add_column("Confidence", style="green", width=12, justify="center")
        table.add_column("Suggested", style="yellow", width=10, justify="center")
        
        for i, page in enumerate(analysis['suggested_pages'], 1):
            confidence_bar = self._create_confidence_bar(page['confidence'])
            suggested_icon = "✓" if page.get('selected', False) else "○"
            suggested_color = "green" if page.get('selected', False) else "dim"
            
            table.add_row(
                str(i),
                page['type'].replace('-', ' ').title(),
                page['config']['description'],
                confidence_bar,
                f"[{suggested_color}]{suggested_icon}[/{suggested_color}]"
            )
        
        self.console.print("\n")
        self.console.print(table)
    
    def _create_confidence_bar(self, confidence: float) -> str:
        """Create a visual confidence bar"""
        filled_blocks = int(confidence * 8)
        bar = "█" * filled_blocks + "░" * (8 - filled_blocks)
        percentage = int(confidence * 100)
        
        if confidence >= 0.8:
            color = "green"
        elif confidence >= 0.5:
            color = "yellow"
        else:
            color = "red"
        
        return f"[{color}]{bar}[/{color}] {percentage}%"
    
    def interactive_selection(self, analysis: Dict[str, Any]) -> List[str]:
        """Interactive page selection with rich interface"""
        
        # Show analysis results
        self.show_analysis_results(analysis)
        
        # Create a mutable list of pages with selection status
        pages = analysis['suggested_pages'].copy()
        
        while True:
            self.console.print(f"\n[bold blue]📝 Page Selection Menu[/bold blue]")
            self.console.print("[dim]Choose what to do next:[/dim]")
            
            selected_count = len([p for p in pages if p.get('selected', False)])
            
            menu_options = [
                f"[1] Toggle individual pages ({selected_count} selected)",
                "[2] Select all suggested pages",
                "[3] Select only high-confidence pages (80%+)",
                "[4] Custom selection (choose by number)",
                "[5] Preview final selection",
                "[6] Continue with selected pages",
                "[7] Cancel and exit"
            ]
            
            for option in menu_options:
                self.console.print(f"  {option}")
            
            try:
                try:
                    choice = IntPrompt.ask(
                        "\n[cyan]What would you like to do?[/cyan]",
                        choices=["1", "2", "3", "4", "5", "6", "7"],
                        default="6"
                    )
                except (EOFError, KeyboardInterrupt):
                    # Non-interactive mode or user cancelled - auto-select pages
                    selected_pages = [p['type'] for p in pages if p.get('selected', False)]
                    if not selected_pages:
                        # If no pages selected, select all that were suggested
                        for page in pages:
                            if page['confidence'] >= 0.5:  # Only select confident suggestions
                                page['selected'] = True
                        selected_pages = [p['type'] for p in pages if p.get('selected', False)]
                    
                    if selected_pages:
                        self.console.print(f"[yellow]📄 Auto-selecting {len(selected_pages)} pages for non-interactive mode[/yellow]")
                        return selected_pages
                    else:
                        self.console.print("[red]❌ No pages selected and no confident suggestions available.[/red]")
                        return []
                
                if choice == 1:
                    pages = self._toggle_individual_pages(pages)
                elif choice == 2:
                    pages = self._select_all_suggested(pages)
                elif choice == 3:
                    pages = self._select_high_confidence(pages)
                elif choice == 4:
                    pages = self._custom_selection(pages)
                elif choice == 5:
                    self._preview_selection(pages)
                elif choice == 6:
                    selected_pages = [p['type'] for p in pages if p.get('selected', False)]
                    if not selected_pages:
                        self.console.print("[red]❌ No pages selected! Please select at least one page.[/red]")
                        continue
                    return selected_pages
                elif choice == 7:
                    self.console.print("[yellow]⚠️  Operation cancelled.[/yellow]")
                    return []
                
            except KeyboardInterrupt:
                self.console.print("[yellow]⚠️  Operation cancelled.[/yellow]")
                return []
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")
                continue
    
    def _toggle_individual_pages(self, pages: List[Dict]) -> List[Dict]:
        """Allow user to toggle individual pages"""
        
        while True:
            self.console.print(f"\n[bold blue]📄 Toggle Individual Pages[/bold blue]")
            
            # Show current selection status
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("#", width=3)
            table.add_column("Page", style="cyan", width=15)
            table.add_column("Status", width=8, justify="center")
            table.add_column("Confidence", width=12, justify="center")
            
            for i, page in enumerate(pages, 1):
                status = "[green]✓[/green]" if page.get('selected', False) else "[dim]○[/dim]"
                confidence = f"{int(page['confidence'] * 100)}%"
                
                table.add_row(
                    str(i),
                    page['type'].replace('-', ' ').title(),
                    status,
                    confidence
                )
            
            self.console.print(table)
            
            self.console.print(f"\n[dim]Enter page number to toggle, or 0 to return to main menu:[/dim]")
            
            try:
                choice = IntPrompt.ask(
                    "[cyan]Page number[/cyan]",
                    choices=[str(i) for i in range(0, len(pages) + 1)],
                    default="0"
                )
                
                if choice == 0:
                    return pages
                else:
                    # Toggle the selection
                    page_idx = choice - 1
                    pages[page_idx]['selected'] = not pages[page_idx].get('selected', False)
                    
                    status = "selected" if pages[page_idx]['selected'] else "deselected"
                    page_name = pages[page_idx]['type'].replace('-', ' ').title()
                    self.console.print(f"[green]✓ {page_name} {status}[/green]")
                    
            except KeyboardInterrupt:
                return pages
    
    def _select_all_suggested(self, pages: List[Dict]) -> List[Dict]:
        """Select all pages that were initially suggested"""
        for page in pages:
            page['selected'] = True
        
        self.console.print("[green]✓ All pages selected[/green]")
        return pages
    
    def _select_high_confidence(self, pages: List[Dict]) -> List[Dict]:
        """Select only high-confidence pages (80%+)"""
        high_confidence_count = 0
        for page in pages:
            if page['confidence'] >= 0.8:
                page['selected'] = True
                high_confidence_count += 1
            else:
                page['selected'] = False
        
        self.console.print(f"[green]✓ Selected {high_confidence_count} high-confidence pages[/green]")
        return pages
    
    def _custom_selection(self, pages: List[Dict]) -> List[Dict]:
        """Allow custom selection by entering page numbers"""
        
        self.console.print(f"\n[bold blue]🎯 Custom Page Selection[/bold blue]")
        
        # Show pages with numbers
        for i, page in enumerate(pages, 1):
            confidence = int(page['confidence'] * 100)
            self.console.print(f"  [{i}] {page['type'].replace('-', ' ').title()} ({confidence}% confidence)")
        
        self.console.print(f"\n[dim]Enter page numbers separated by commas (e.g., 1,3,5):[/dim]")
        self.console.print(f"[dim]Or enter 'all' for all pages, 'none' to deselect all[/dim]")
        
        try:
            selection = input("\n[cyan]Page numbers: [/cyan]").strip().lower()
            
            if selection == 'all':
                for page in pages:
                    page['selected'] = True
                self.console.print("[green]✓ All pages selected[/green]")
            elif selection == 'none':
                for page in pages:
                    page['selected'] = False
                self.console.print("[yellow]○ All pages deselected[/yellow]")
            else:
                # Parse comma-separated numbers
                for page in pages:
                    page['selected'] = False
                
                try:
                    numbers = [int(n.strip()) for n in selection.split(',') if n.strip()]
                    for num in numbers:
                        if 1 <= num <= len(pages):
                            pages[num - 1]['selected'] = True
                    
                    selected_names = [p['type'] for p in pages if p.get('selected', False)]
                    self.console.print(f"[green]✓ Selected: {', '.join(selected_names)}[/green]")
                except ValueError:
                    self.console.print("[red]❌ Invalid input. Please enter numbers separated by commas.[/red]")
                    
        except KeyboardInterrupt:
            pass
        
        return pages
    
    def _preview_selection(self, pages: List[Dict]) -> None:
        """Preview the final selection"""
        
        selected_pages = [p for p in pages if p.get('selected', False)]
        
        if not selected_pages:
            self.console.print("[yellow]⚠️  No pages currently selected.[/yellow]")
            return
        
        self.console.print(f"\n[bold green]📋 Final Selection Preview[/bold green]")
        self.console.print(f"[dim]{len(selected_pages)} pages will be generated:[/dim]\n")
        
        # Create preview table
        table = Table(show_header=True, header_style="bold green", show_lines=True)
        table.add_column("Order", width=6, justify="center")
        table.add_column("Page Type", style="cyan", width=15)
        table.add_column("Description", style="white")
        table.add_column("Path", style="dim")
        
        for i, page in enumerate(selected_pages, 1):
            table.add_row(
                str(i),
                page['type'].replace('-', ' ').title(),
                page['config']['description'],
                page['config']['path']
            )
        
        self.console.print(table)
        
        # Show generation estimate
        estimated_time = len(selected_pages) * 60  # Rough estimate: 1 minute per page
        self.console.print(f"\n[dim]⏱️  Estimated generation time: ~{estimated_time} seconds[/dim]")
    
    def confirm_selection(self, selected_pages: List[str]) -> bool:
        """Final confirmation before generation"""
        
        if not selected_pages:
            return False
        
        page_list = ", ".join(page.replace('-', ' ').title() for page in selected_pages)
        
        self.console.print(f"\n[bold yellow]🚀 Ready to Generate[/bold yellow]")
        self.console.print(f"[dim]Selected pages: {page_list}[/dim]")
        
        return Confirm.ask(
            f"\n[cyan]Generate {len(selected_pages)} pages?[/cyan]",
            default=True
        )