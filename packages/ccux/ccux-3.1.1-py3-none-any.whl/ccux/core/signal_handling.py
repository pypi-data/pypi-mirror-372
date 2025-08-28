"""
Signal Handling Module

Provides graceful interrupt handling for CLI operations.
Manages subprocess cleanup and progress indicator termination.
"""

import sys
import signal
from typing import Optional
from rich.console import Console

# Global variables for signal handling
current_subprocess = None
current_progress = None


def signal_handler(signum, frame):
    """Handle keyboard interrupts gracefully"""
    global current_subprocess, current_progress
    
    console = Console()
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


def register_signal_handler():
    """Register the signal handler for SIGINT"""
    signal.signal(signal.SIGINT, signal_handler)


def set_current_subprocess(subprocess_obj):
    """Set the current subprocess for cleanup"""
    global current_subprocess
    current_subprocess = subprocess_obj


def set_current_progress(progress_obj):
    """Set the current progress indicator for cleanup"""
    global current_progress
    current_progress = progress_obj


def clear_current_subprocess():
    """Clear the current subprocess reference"""
    global current_subprocess
    current_subprocess = None


def clear_current_progress():
    """Clear the current progress reference"""
    global current_progress
    current_progress = None


def cleanup_on_exit():
    """Perform cleanup operations on exit"""
    clear_current_subprocess()
    clear_current_progress()