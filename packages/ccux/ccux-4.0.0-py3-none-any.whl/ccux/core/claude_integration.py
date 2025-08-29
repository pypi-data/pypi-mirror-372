"""
Claude Integration Module

Provides Claude API integration with progress indicators and error handling.
Manages subprocess execution with timeout protection and usage tracking.
"""

import subprocess
import threading
import base64
import os
import re
import json
from typing import Dict, Any, Tuple, List
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

from .usage_tracking import get_latest_usage, calculate_usage_difference
from .signal_handling import set_current_subprocess, set_current_progress, clear_current_subprocess, clear_current_progress
from .configuration import Config


def extract_image_paths(prompt: str) -> List[str]:
    """Extract image file paths from prompt text"""
    # Look for common image file extensions in the prompt
    image_extensions = r'\.(jpg|jpeg|png|gif|bmp|webp|tiff)'
    # Find paths that end with image extensions
    pattern = r'([^\s\n]+' + image_extensions + r')'
    matches = re.findall(pattern, prompt, re.IGNORECASE)
    return [match[0] for match in matches]


def encode_image_to_base64(image_path: str) -> tuple[str, str]:
    """Encode image file to base64 and determine media type"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Determine media type from extension
    ext = os.path.splitext(image_path)[1].lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg', 
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.tiff': 'image/tiff'
    }
    
    media_type = media_type_map.get(ext, 'image/jpeg')
    
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    return encoded_string, media_type


def create_message_with_images(prompt: str, image_paths: List[str]) -> dict:
    """Create Claude API message format with images and text"""
    content = []
    
    # Add images first
    for image_path in image_paths:
        try:
            base64_data, media_type = encode_image_to_base64(image_path)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_data
                }
            })
        except Exception as e:
            # If image encoding fails, continue without this image
            console = Console()
            console.print(f"[yellow]⚠️  Failed to encode image {image_path}: {e}[/yellow]")
            continue
    
    # Add text content (remove image paths from prompt since we're now including them as images)
    text_prompt = prompt
    for image_path in image_paths:
        text_prompt = text_prompt.replace(f"- {image_path}", "")
        text_prompt = text_prompt.replace(image_path, "")
    
    # Clean up any empty lines or duplicate newlines
    text_prompt = re.sub(r'\n\s*\n', '\n', text_prompt.strip())
    
    content.append({
        "type": "text", 
        "text": text_prompt
    })
    
    return {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }


def run_claude_api_with_images(prompt: str, image_paths: List[str], description: str, pre_usage: Dict[str, Any], claude_cmd: str) -> Tuple[str, Dict[str, Any]]:
    """Run Claude with images by creating a prompt that uses the Read tool pattern"""
    console = Console()
    
    # Create a modified prompt that asks Claude to read the image files
    read_commands = []
    for i, image_path in enumerate(image_paths, 1):
        if os.path.exists(image_path):
            read_commands.append(f"Please read and analyze image {i}: {image_path}")
    
    if not read_commands:
        console.print("[yellow]⚠️  No valid image files found, falling back to text-only analysis[/yellow]")
        cmd = [claude_cmd, '--print', prompt]
        return run_claude_cli_fallback(cmd, description, pre_usage)
    
    # Create new prompt that asks Claude to read the images
    image_analysis_prompt = f"""I need you to analyze competitor website screenshots for UX patterns.

{' '.join(read_commands)}

After reading these images, please provide: {prompt.split('Respond in JSON:')[1] if 'Respond in JSON:' in prompt else prompt}

Focus your analysis on what you can actually see in the images - navigation, layouts, CTAs, typography, and overall design patterns."""
    
    # Use regular Claude CLI 
    cmd = [claude_cmd, '--print', image_analysis_prompt]
    return run_claude_cli_fallback(cmd, description, pre_usage)


def run_claude_cli_fallback(cmd: List[str], description: str, pre_usage: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Fallback to regular CLI execution"""
    console = Console()
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
        set_current_progress(progress)
        task = progress.add_task("Processing", total=None)
        
        try:
            current_subprocess = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            set_current_subprocess(current_subprocess)
            
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
            
            clear_current_subprocess()
            clear_current_progress()
            
            output_text = '\n'.join(output_lines)
            
            # Get usage after Claude call and calculate difference
            post_usage = get_latest_usage()
            usage_stats = calculate_usage_difference(pre_usage, post_usage)
            
            return output_text, usage_stats
            
        except Exception as e:
            clear_current_subprocess()
            clear_current_progress()
            raise e


def run_claude_with_progress(prompt: str, description: str = "Claude Code is thinking...", enable_image_analysis: bool = False) -> Tuple[str, Dict[str, Any]]:
    """Run Claude CLI with real-time progress indication and usage tracking via ccusage"""
    config = Config()
    claude_cmd = config.get_claude_command()
    
    # Get usage before Claude call for comparison
    pre_usage = get_latest_usage()
    
    # Only check for image paths if image analysis is enabled
    if enable_image_analysis:
        image_paths = extract_image_paths(prompt)
        if image_paths:
            # Use Claude API directly with images
            return run_claude_api_with_images(prompt, image_paths, description, pre_usage, claude_cmd)
    
    # Use regular Claude CLI (either no images found or image analysis disabled)
    cmd = [claude_cmd, '--print', prompt]
    return run_claude_cli_fallback(cmd, description, pre_usage)


def summarize_long_description(desc: str) -> str:
    """Summarize long product descriptions to optimize token usage"""
    console = Console()
    
    if len(desc.split()) <= 100:
        return desc
    
    console.print(f"[yellow]📝 Description is {len(desc.split())} words, summarizing to optimize Claude token usage...[/yellow]")
    
    summary_prompt = f"""Please summarize this product description in 100-150 words while preserving all key details, features, and benefits:

{desc}

Return only the summary, no additional text."""
    
    try:
        summary, _ = run_claude_with_progress(summary_prompt, "Summarizing product description...")
        return summary.strip()
    except Exception as e:
        console.print(f"[yellow]⚠️  Summarization failed: {e}. Using original description.[/yellow]")
        return desc


def validate_claude_command(claude_cmd: str = None) -> bool:
    """Validate that Claude CLI is available and working"""
    if not claude_cmd:
        config = Config()
        claude_cmd = config.get_claude_command()
    
    try:
        result = subprocess.run([claude_cmd, '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False


def get_claude_version(claude_cmd: str = None) -> str:
    """Get Claude CLI version information"""
    if not claude_cmd:
        config = Config()
        claude_cmd = config.get_claude_command()
    
    try:
        result = subprocess.run([claude_cmd, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return "Unknown"