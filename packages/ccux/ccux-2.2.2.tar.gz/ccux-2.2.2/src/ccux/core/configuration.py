"""
Configuration Management Module

Provides YAML configuration file management for CCUX projects.
Supports loading project defaults and environment variable overrides.
"""

import os
import yaml
from typing import Dict, Any
from rich.console import Console


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
        console = Console()
        
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
        """Get configuration value with optional default"""
        return self.config.get(key, default)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        self.config.update(updates)
    
    def save(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False)
        except Exception as e:
            console = Console()
            console.print(f"[yellow]⚠️  Error saving config: {e}[/yellow]")
    
    def get_claude_command(self) -> str:
        """Get Claude CLI command with environment variable override"""
        return os.getenv('CCUX_CLAUDE_CMD', self.get('claude_cmd', 'claude'))
    
    def get_default_theme(self) -> str:
        """Get default theme with environment variable override"""
        return os.getenv('CCUX_DEFAULT_THEME', self.get('theme', 'minimal'))
    
    def get_output_dir(self) -> str:
        """Get output directory with environment variable override"""
        return os.getenv('CCUX_OUTPUT_DIR', self.get('output_dir', 'output/landing-page'))


def load_project_config(config_path: str = "ccux.yaml") -> Config:
    """Load project configuration from file"""
    return Config(config_path)


def get_environment_overrides() -> Dict[str, str]:
    """Get all CCUX environment variable overrides"""
    overrides = {}
    env_vars = {
        'CCUX_CLAUDE_CMD': 'claude_cmd',
        'CCUX_DEFAULT_THEME': 'theme',
        'CCUX_OUTPUT_DIR': 'output_dir'
    }
    
    for env_var, config_key in env_vars.items():
        value = os.getenv(env_var)
        if value:
            overrides[config_key] = value
    
    return overrides