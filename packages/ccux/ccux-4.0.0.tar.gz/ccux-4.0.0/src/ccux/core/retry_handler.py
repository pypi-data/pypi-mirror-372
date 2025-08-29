"""
Retry Handler Module

Implements intelligent retry logic with exponential backoff for failed operations.
Handles different types of failures with appropriate retry strategies.
"""

import time
import random
from typing import Callable, Any, Dict, List, Optional
from rich.console import Console


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_multiplier: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter  # Add randomization to prevent thundering herd


class RetryResult:
    """Result of a retry operation"""
    
    def __init__(self, success: bool, result: Any = None, error: str = "", 
                 attempts: int = 0, total_time: float = 0.0):
        self.success = success
        self.result = result
        self.error = error
        self.attempts = attempts
        self.total_time = total_time


class RetryHandler:
    """Intelligent retry handler with exponential backoff"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.console = Console()
        self.config = config or RetryConfig()
        
        # Define retry-worthy error patterns
        self.retryable_errors = [
            'timeout',
            'connection',
            'network',
            'rate limit',
            'temporarily unavailable',
            '500',  # Server errors
            '502',  # Bad gateway
            '503',  # Service unavailable
            '504',  # Gateway timeout
        ]
    
    def is_retryable_error(self, error_message: str) -> bool:
        """Determine if an error is worth retrying"""
        error_lower = error_message.lower()
        return any(pattern in error_lower for pattern in self.retryable_errors)
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number"""
        
        # Exponential backoff: base_delay * (backoff_multiplier ^ attempt)
        delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
        
        # Cap at max_delay
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            jitter = random.uniform(-jitter_range, jitter_range)
            delay += jitter
        
        return max(0.1, delay)  # Minimum 100ms delay
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> RetryResult:
        """Execute function with retry logic and exponential backoff"""
        
        start_time = time.time()
        last_error = ""
        
        for attempt in range(self.config.max_retries + 1):  # +1 for initial attempt
            try:
                if attempt > 0:
                    delay = self.calculate_delay(attempt - 1)
                    self.console.print(f"[yellow]🔄 Retry attempt {attempt} in {delay:.1f}s...[/yellow]")
                    time.sleep(delay)
                
                # Execute the function
                result = func(*args, **kwargs)
                
                total_time = time.time() - start_time
                
                if attempt > 0:
                    self.console.print(f"[green]✅ Succeeded on attempt {attempt + 1}[/green]")
                
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1,
                    total_time=total_time
                )
                
            except Exception as e:
                last_error = str(e)
                
                # Check if this error is worth retrying
                if not self.is_retryable_error(last_error):
                    self.console.print(f"[red]❌ Non-retryable error: {last_error}[/red]")
                    total_time = time.time() - start_time
                    return RetryResult(
                        success=False,
                        error=last_error,
                        attempts=attempt + 1,
                        total_time=total_time
                    )
                
                # If this is the last attempt, don't retry
                if attempt >= self.config.max_retries:
                    self.console.print(f"[red]❌ Max retries exceeded. Last error: {last_error}[/red]")
                    total_time = time.time() - start_time
                    return RetryResult(
                        success=False,
                        error=last_error,
                        attempts=attempt + 1,
                        total_time=total_time
                    )
                
                self.console.print(f"[yellow]⚠️  Attempt {attempt + 1} failed: {last_error}[/yellow]")
        
        # This shouldn't be reached, but just in case
        total_time = time.time() - start_time
        return RetryResult(
            success=False,
            error=last_error,
            attempts=self.config.max_retries + 1,
            total_time=total_time
        )
    
    def retry_page_generation(self, page_type: str, generation_func: Callable) -> RetryResult:
        """Specialized retry logic for page generation"""
        
        self.console.print(f"[cyan]🔄 Retrying {page_type.replace('-', ' ').title()} page generation...[/cyan]")
        
        # Use longer delays for page generation retries
        retry_config = RetryConfig(
            max_retries=2,  # Only 2 retries for page generation
            base_delay=5.0,  # Start with 5 second delay
            max_delay=30.0,  # Max 30 second delay
            backoff_multiplier=2.0
        )
        
        original_config = self.config
        self.config = retry_config
        
        try:
            result = self.retry_with_backoff(generation_func)
            return result
        finally:
            self.config = original_config
    
    def batch_retry_failed_operations(self, failed_operations: List[Dict[str, Any]]) -> Dict[str, RetryResult]:
        """Retry multiple failed operations with intelligent batching"""
        
        if not failed_operations:
            return {}
        
        self.console.print(f"[yellow]🔄 Retrying {len(failed_operations)} failed operations...[/yellow]")
        
        results = {}
        
        for operation in failed_operations:
            operation_id = operation.get('id', 'unknown')
            operation_func = operation.get('func')
            operation_args = operation.get('args', ())
            operation_kwargs = operation.get('kwargs', {})
            
            if not operation_func:
                results[operation_id] = RetryResult(
                    success=False,
                    error="No function provided for retry",
                    attempts=0
                )
                continue
            
            try:
                result = self.retry_with_backoff(operation_func, *operation_args, **operation_kwargs)
                results[operation_id] = result
            except Exception as e:
                results[operation_id] = RetryResult(
                    success=False,
                    error=str(e),
                    attempts=1
                )
        
        # Summary
        successful_retries = len([r for r in results.values() if r.success])
        
        if successful_retries > 0:
            self.console.print(f"[green]✅ {successful_retries}/{len(failed_operations)} operations succeeded on retry[/green]")
        else:
            self.console.print(f"[red]❌ All retry attempts failed[/red]")
        
        return results
    
    def create_retry_menu(self, failed_items: List[str], item_type: str = "items") -> Optional[List[str]]:
        """Create an interactive retry menu for failed items"""
        
        if not failed_items:
            return None
        
        from rich.prompt import Confirm, IntPrompt
        
        self.console.print(f"\n[bold yellow]⚠️  {len(failed_items)} {item_type} failed to generate[/bold yellow]")
        
        # Show failed items
        for i, item in enumerate(failed_items, 1):
            self.console.print(f"  {i}. {item.replace('-', ' ').title()}")
        
        self.console.print(f"\n[dim]Options:[/dim]")
        self.console.print(f"  [1] Retry all failed {item_type} ({len(failed_items)} {item_type})")
        self.console.print(f"  [2] Select specific {item_type} to retry")
        self.console.print(f"  [3] Skip retries and continue")
        self.console.print(f"  [4] View error details")
        
        try:
            choice = IntPrompt.ask(
                f"\n[cyan]What would you like to do?[/cyan]",
                choices=["1", "2", "3", "4"],
                default="1"
            )
            
            if choice == 1:
                return failed_items
            elif choice == 2:
                return self._select_items_for_retry(failed_items, item_type)
            elif choice == 3:
                return []
            elif choice == 4:
                self._show_error_details(failed_items)
                return self.create_retry_menu(failed_items, item_type)  # Show menu again
                
        except KeyboardInterrupt:
            self.console.print("[yellow]⚠️  Cancelled[/yellow]")
            return []
        
        return []
    
    def _select_items_for_retry(self, failed_items: List[str], item_type: str) -> List[str]:
        """Allow user to select specific items for retry"""
        
        self.console.print(f"\n[bold blue]Select {item_type} to retry:[/bold blue]")
        
        for i, item in enumerate(failed_items, 1):
            self.console.print(f"  [{i}] {item.replace('-', ' ').title()}")
        
        self.console.print(f"\n[dim]Enter numbers separated by commas (e.g., 1,3,5) or 'all' for all:[/dim]")
        
        try:
            selection = input(f"\n[cyan]{item_type.title()} to retry: [/cyan]").strip().lower()
            
            if selection == 'all':
                return failed_items
            elif selection == '':
                return []
            else:
                try:
                    numbers = [int(n.strip()) for n in selection.split(',') if n.strip()]
                    selected_items = []
                    
                    for num in numbers:
                        if 1 <= num <= len(failed_items):
                            selected_items.append(failed_items[num - 1])
                    
                    return selected_items
                except ValueError:
                    self.console.print("[red]❌ Invalid input. Please enter numbers separated by commas.[/red]")
                    return self._select_items_for_retry(failed_items, item_type)
                    
        except KeyboardInterrupt:
            return []
    
    def _show_error_details(self, failed_items: List[str]) -> None:
        """Show detailed error information for failed items"""
        
        self.console.print(f"\n[bold red]📋 Error Details[/bold red]")
        
        # This would need to be implemented with actual error storage
        # For now, show a placeholder
        for item in failed_items:
            self.console.print(f"\n[cyan]{item.replace('-', ' ').title()}:[/cyan]")
            self.console.print("[dim]  Error details would be shown here...[/dim]")
        
        input("\nPress Enter to continue...")