"""
Usage Tracking Module

Provides cost calculation and token analytics functionality for CCUX operations.
Integrates with ccusage to track Claude API usage and estimate costs.
"""

import json
import subprocess
from typing import Dict, Any


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


def display_usage_stats(usage_stats: Dict[str, Any], console) -> None:
    """Display usage statistics in a formatted way"""
    if not usage_stats:
        return
        
    input_tokens = usage_stats.get('input_tokens', 0)
    output_tokens = usage_stats.get('output_tokens', 0)
    cost = usage_stats.get('cost', 0.0)
    
    if input_tokens > 0 or output_tokens > 0:
        console.print(f"\n[dim]📊 Usage: {input_tokens:,} input + {output_tokens:,} output tokens (~${cost:.4f})[/dim]")


def format_cost_display(cost: float) -> str:
    """Format cost for display with appropriate precision"""
    if cost >= 1.0:
        return f"${cost:.2f}"
    elif cost >= 0.01:
        return f"${cost:.3f}" 
    else:
        return f"${cost:.4f}"


def aggregate_usage_stats(stats_list: list) -> Dict[str, Any]:
    """Aggregate multiple usage statistics into totals"""
    total_input = sum(stats.get('input_tokens', 0) for stats in stats_list)
    total_output = sum(stats.get('output_tokens', 0) for stats in stats_list)
    total_cost = sum(stats.get('cost', 0.0) for stats in stats_list)
    
    return {
        'input_tokens': total_input,
        'output_tokens': total_output, 
        'cost': total_cost
    }