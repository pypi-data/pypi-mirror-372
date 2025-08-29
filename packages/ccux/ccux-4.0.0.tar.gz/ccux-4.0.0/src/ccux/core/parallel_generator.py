"""
Parallel Generation Engine

Manages concurrent page generation with real-time progress tracking,
error handling, and intelligent resource management.
"""

import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, List, Any, Callable, Optional, Tuple
from pathlib import Path
import json
import os

from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

from .claude_integration import run_claude_with_progress
from .retry_handler import RetryHandler


class PageGenerationResult:
    """Result of a page generation attempt"""
    
    def __init__(self, page_type: str, success: bool, content: str = "", 
                 error: str = "", execution_time: float = 0.0, 
                 usage_stats: Dict = None):
        self.page_type = page_type
        self.success = success
        self.content = content
        self.error = error
        self.execution_time = execution_time
        self.usage_stats = usage_stats or {}
        self.timestamp = time.time()


class PageGenerationTask:
    """Individual page generation task"""
    
    def __init__(self, page_type: str, config: Dict, prompt: str, 
                 output_path: str, priority: int = 0):
        self.page_type = page_type
        self.config = config
        self.prompt = prompt
        self.output_path = output_path
        self.priority = priority
        self.status = "queued"  # queued, running, completed, failed
        self.result: Optional[PageGenerationResult] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.retry_count = 0
        self.max_retries = 2


class ParallelGenerator:
    """Parallel page generation engine with progress tracking"""
    
    def __init__(self, max_workers: int = 3):
        self.console = Console()
        self.max_workers = max_workers
        self.tasks: Dict[str, PageGenerationTask] = {}
        self.results: Dict[str, PageGenerationResult] = {}
        self.retry_handler = RetryHandler()
        
        # Progress tracking
        self.progress_data = {
            'total_pages': 0,
            'completed': 0,
            'failed': 0,
            'running': 0,
            'queued': 0,
            'start_time': None
        }
    
    def add_task(self, page_type: str, config: Dict, prompt: str, 
                 output_path: str, priority: int = 0) -> None:
        """Add a page generation task"""
        task = PageGenerationTask(page_type, config, prompt, output_path, priority)
        self.tasks[page_type] = task
        self.progress_data['total_pages'] += 1
        self.progress_data['queued'] += 1
    
    def generate_all_pages(self) -> Dict[str, PageGenerationResult]:
        """Generate all pages in parallel with simple progress display"""
        
        if not self.tasks:
            self.console.print("[red]❌ No tasks to generate[/red]")
            return {}
        
        self.progress_data['start_time'] = time.time()
        
        # Sort tasks by priority
        sorted_tasks = sorted(self.tasks.values(), key=lambda t: t.priority)
        
        # Show initial status
        self._show_initial_status()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures: Dict[Future, PageGenerationTask] = {}
            
            for task in sorted_tasks:
                future = executor.submit(self._generate_single_page, task)
                futures[future] = task
                task.status = "queued"
            
            # Process completed tasks
            last_update = time.time()
            while futures:
                completed_futures = []
                
                for future in list(futures.keys()):
                    if future.done():
                        completed_futures.append(future)
                
                for future in completed_futures:
                    task = futures.pop(future)
                    try:
                        result = future.result()
                        self.results[task.page_type] = result
                        
                        if result.success:
                            self.progress_data['completed'] += 1
                            task.status = "completed"
                            self.console.print(f"[green]✅ {task.page_type.replace('-', ' ').title()} completed ({result.execution_time:.1f}s)[/green]")
                        else:
                            self.progress_data['failed'] += 1
                            task.status = "failed"
                            error_preview = result.error[:50] + "..." if len(result.error) > 50 else result.error
                            self.console.print(f"[red]❌ {task.page_type.replace('-', ' ').title()} failed: {error_preview}[/red]")
                        
                        self.progress_data['running'] = max(0, self.progress_data['running'] - 1)
                        
                    except Exception as e:
                        # Handle unexpected errors
                        result = PageGenerationResult(
                            task.page_type, False, "", str(e)
                        )
                        self.results[task.page_type] = result
                        self.progress_data['failed'] += 1
                        task.status = "failed"
                        self.progress_data['running'] = max(0, self.progress_data['running'] - 1)
                        
                        self.console.print(f"[red]❌ {task.page_type.replace('-', ' ').title()} failed: {str(e)[:50]}[/red]")
                
                # Show progress update every 3 seconds
                current_time = time.time()
                if current_time - last_update > 3.0:
                    self._show_progress_update()
                    last_update = current_time
                
                # Small delay to prevent excessive CPU usage
                if futures:
                    time.sleep(0.5)
        
        # Show final summary
        self._show_final_summary()
        
        return self.results
    
    def _generate_single_page(self, task: PageGenerationTask) -> PageGenerationResult:
        """Generate a single page with error handling and proper usage tracking"""
        
        task.status = "running"
        task.start_time = time.time()
        
        # Update progress counters
        self.progress_data['queued'] = max(0, self.progress_data['queued'] - 1)
        self.progress_data['running'] += 1
        
        try:
            # Import usage tracking functions
            from .usage_tracking import get_latest_usage, calculate_usage_difference, calculate_estimated_cost
            from .configuration import Config
            import subprocess
            import os
            
            # Get usage before Claude call for comparison
            pre_usage = get_latest_usage()
            
            # Use claude CLI with proper configuration
            config = Config()
            claude_cmd = config.get_claude_command()
            cmd = [claude_cmd, '--print', task.prompt]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise Exception(f"Claude command failed: {result.stderr}")
            
            content = result.stdout.strip()
            
            # Get usage after Claude call and calculate difference
            post_usage = get_latest_usage()
            usage_stats = calculate_usage_difference(pre_usage, post_usage)
            
            # If ccusage tracking failed, fall back to estimation
            if not usage_stats or usage_stats.get('input_tokens', 0) == 0:
                estimated_input_tokens = max(1, len(task.prompt.split()) * 1.3)  # Rough estimation
                estimated_output_tokens = max(1, len(content.split()) * 1.3)
                estimated_cost = calculate_estimated_cost(int(estimated_input_tokens), int(estimated_output_tokens))
                
                usage_stats = {
                    'input_tokens': int(estimated_input_tokens),
                    'output_tokens': int(estimated_output_tokens),
                    'cost': estimated_cost
                }
            
            # Save the generated content
            self._save_page_content(task.output_path, content)
            
            task.end_time = time.time()
            execution_time = task.end_time - task.start_time
            
            return PageGenerationResult(
                task.page_type,
                success=True,
                content=content,
                execution_time=execution_time,
                usage_stats=usage_stats
            )
            
        except Exception as e:
            task.end_time = time.time()
            execution_time = task.end_time - task.start_time if task.start_time else 0
            
            return PageGenerationResult(
                task.page_type,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def _show_initial_status(self) -> None:
        """Show initial generation status"""
        total = self.progress_data['total_pages']
        page_list = ", ".join([task.page_type.replace('-', ' ').title() for task in self.tasks.values()])
        
        self.console.print(f"[bold blue]🚀 Starting parallel generation of {total} pages...[/bold blue]")
        self.console.print(f"[dim]Pages: {page_list}[/dim]")
        self.console.print()
    
    def _show_progress_update(self) -> None:
        """Show periodic progress updates"""
        total = self.progress_data['total_pages']
        completed = self.progress_data['completed']
        failed = self.progress_data['failed']
        running = self.progress_data['running']
        
        progress_percentage = int((completed + failed) / total * 100) if total > 0 else 0
        
        self.console.print(f"[cyan]📊 Progress: {completed + failed}/{total} pages ({progress_percentage}%) | Running: {running} | Completed: {completed} | Failed: {failed}[/cyan]")
    
    def _show_final_summary(self) -> None:
        """Show final generation summary"""
        total = self.progress_data['total_pages']
        completed = self.progress_data['completed']
        failed = self.progress_data['failed']
        total_time = time.time() - self.progress_data['start_time'] if self.progress_data['start_time'] else 0
        
        if failed == 0:
            self.console.print(f"\n[bold green]🎉 All {completed} pages generated successfully in {total_time:.1f}s![/bold green]")
        else:
            self.console.print(f"\n[bold yellow]⚠️  Generation completed: {completed} successful, {failed} failed ({total_time:.1f}s)[/bold yellow]")
    
    def _save_page_content(self, output_path: str, content: str) -> None:
        """Save generated page content to file"""
        
        # Create directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Clean up content (remove code blocks if present)
        if content.strip().startswith('```'):
            lines = content.strip().split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            content = '\n'.join(lines)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_progress_display(self) -> Panel:
        """Create real-time progress display"""
        
        # Create overall progress info
        total = self.progress_data['total_pages']
        completed = self.progress_data['completed']
        failed = self.progress_data['failed']
        running = self.progress_data['running']
        queued = self.progress_data['queued']
        
        # Calculate progress percentage
        progress_percentage = int((completed + failed) / total * 100) if total > 0 else 0
        
        # Create progress bar visualization
        bar_length = 20
        filled_length = int(progress_percentage / 100 * bar_length)
        progress_bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # Calculate time estimates
        elapsed_time = time.time() - self.progress_data['start_time'] if self.progress_data['start_time'] else 0
        
        remaining_pages = total - completed - failed
        if completed > 0 and remaining_pages > 0:
            avg_time_per_page = elapsed_time / (completed + failed)
            estimated_remaining = int(avg_time_per_page * remaining_pages)
        else:
            estimated_remaining = 0
        
        # Create header
        header_text = Text()
        header_text.append("🚀 Generating ", style="bold blue")
        header_text.append(f"{total} pages", style="bold white")
        header_text.append(" in parallel...", style="bold blue")
        
        # Create progress info as Text object
        progress_text = Text()
        progress_text.append(f"[{progress_bar}] {progress_percentage}% Overall Progress\n\n")
        
        # Create task status lines as text instead of table
        status_lines = []
        for page_type, task in self.tasks.items():
            if task.status == "completed":
                icon = "✓"
                status_color = "green"
                status_text = f"Generated successfully ({task.result.execution_time:.1f}s)" if task.result else "Completed"
            elif task.status == "running":
                icon = "⚡"
                status_color = "yellow"
                # Create a simple progress indicator
                dots = "." * ((int(time.time() * 2) % 3) + 1)
                status_text = f"Generating{dots}"
            elif task.status == "failed":
                icon = "❌"
                status_color = "red"
                status_text = f"Failed - {task.result.error[:50]}..." if task.result and task.result.error else "Failed"
            else:  # queued
                icon = "⏳"
                status_color = "dim"
                status_text = "Queued" if running < self.max_workers else "Waiting for thread..."
            
            page_name = page_type.replace('-', ' ').title()
            status_line = f"[{status_color}]{icon} {page_name:<12} {status_text}[/{status_color}]"
            status_lines.append(status_line)
        
        # Create complete content as a single formatted string
        content_lines = []
        content_lines.append(f"[{progress_bar}] {progress_percentage}% Overall Progress")
        content_lines.append("")
        
        # Add task status lines
        content_lines.extend(status_lines)
        
        # Add summary
        content_lines.append("")
        content_lines.append(f"Pages completed: {completed}/{total} | Failed: {failed} | Running: {running}")
        if estimated_remaining > 0:
            content_lines.append(f"Estimated time remaining: ~{estimated_remaining} seconds")
        
        # Join all content into a single string with Rich markup
        content_string = "\n".join(content_lines)
        
        return Panel(
            content_string,
            title=header_text,
            border_style="blue",
            padding=(1, 2)
        )
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get a summary of the generation results"""
        
        total_time = time.time() - self.progress_data['start_time'] if self.progress_data['start_time'] else 0
        
        successful_pages = [page_type for page_type, result in self.results.items() if result.success]
        failed_pages = [page_type for page_type, result in self.results.items() if not result.success]
        
        # Calculate total usage stats
        total_input_tokens = sum(result.usage_stats.get('input_tokens', 0) 
                               for result in self.results.values() if result.success)
        total_output_tokens = sum(result.usage_stats.get('output_tokens', 0) 
                                for result in self.results.values() if result.success)
        total_cost = sum(result.usage_stats.get('cost', 0.0) 
                        for result in self.results.values() if result.success)
        
        return {
            'total_pages': self.progress_data['total_pages'],
            'successful_pages': successful_pages,
            'failed_pages': failed_pages,
            'success_count': len(successful_pages),
            'failure_count': len(failed_pages),
            'total_time': total_time,
            'usage_stats': {
                'input_tokens': total_input_tokens,
                'output_tokens': total_output_tokens,
                'cost': total_cost
            }
        }
    
    def display_final_summary(self) -> None:
        """Display final generation summary"""
        
        summary = self.get_generation_summary()
        
        # Determine overall status
        if summary['failure_count'] == 0:
            status_icon = "✅"
            status_text = "All Pages Generated Successfully"
            status_color = "green"
        elif summary['success_count'] == 0:
            status_icon = "❌"
            status_text = "Generation Failed"
            status_color = "red"
        else:
            status_icon = "⚠️"
            status_text = f"Completed with {summary['failure_count']} Failure(s)"
            status_color = "yellow"
        
        # Create summary display
        self.console.print(f"\n[bold {status_color}]{status_icon} Generation Complete[/bold {status_color}]")
        self.console.print(f"[{status_color}]{status_text}[/{status_color}]")
        
        # Create results table
        if self.results:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Page", style="cyan", width=15)
            table.add_column("Status", width=10, justify="center")
            table.add_column("Details", style="white")
            
            for page_type, result in self.results.items():
                page_name = page_type.replace('-', ' ').title()
                
                if result.success:
                    status = "[green]✓ Success[/green]"
                    details = f"Generated in {result.execution_time:.1f}s"
                else:
                    status = "[red]❌ Failed[/red]"
                    error_preview = result.error[:50] + "..." if len(result.error) > 50 else result.error
                    details = error_preview
                
                table.add_row(page_name, status, details)
            
            self.console.print("\n")
            self.console.print(table)
        
        # Show usage statistics
        if summary['usage_stats']['input_tokens'] > 0:
            self.console.print(f"\n[dim]📊 Usage Stats:[/dim]")
            self.console.print(f"[dim]Input tokens: {summary['usage_stats']['input_tokens']:,}[/dim]")
            self.console.print(f"[dim]Output tokens: {summary['usage_stats']['output_tokens']:,}[/dim]")
            self.console.print(f"[dim]Estimated cost: ${summary['usage_stats']['cost']:.3f}[/dim]")
        
        self.console.print(f"[dim]Total time: {summary['total_time']:.1f} seconds[/dim]")
    
    def get_failed_pages(self) -> List[str]:
        """Get list of pages that failed to generate"""
        return [page_type for page_type, result in self.results.items() if not result.success]
    
    def retry_failed_pages(self) -> Dict[str, PageGenerationResult]:
        """Retry generation for failed pages only"""
        
        failed_pages = self.get_failed_pages()
        
        if not failed_pages:
            self.console.print("[green]✅ No failed pages to retry[/green]")
            return {}
        
        self.console.print(f"[yellow]🔄 Retrying {len(failed_pages)} failed pages...[/yellow]")
        
        # Reset progress for retry
        retry_generator = ParallelGenerator(self.max_workers)
        
        for page_type in failed_pages:
            task = self.tasks[page_type]
            retry_generator.add_task(
                task.page_type, 
                task.config, 
                task.prompt, 
                task.output_path, 
                task.priority
            )
        
        # Generate with retry logic
        retry_results = retry_generator.generate_all_pages()
        
        # Update our results with retry results
        for page_type, result in retry_results.items():
            self.results[page_type] = result
        
        return retry_results