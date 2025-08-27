# CCUX Core Modules

This directory contains the modular core system for CCUX, organizing reusable utilities by function to eliminate code duplication and improve maintainability.

## Modules

### `usage_tracking.py`
Cost calculation and token analytics functionality.
- Track Claude API usage via ccusage integration
- Calculate token differences between operations
- Estimate costs based on Claude pricing
- Generate usage reports

### `signal_handling.py` 
Graceful interrupt handling for CLI operations.
- Handle SIGINT (Ctrl+C) gracefully
- Clean up subprocess and progress indicators
- Provide user-friendly interrupt messages

### `configuration.py`
YAML configuration file management.
- Load and merge configuration with defaults
- Support for ccux.yaml project configuration
- Environment variable support

### `project_management.py`
Project discovery and selection utilities.
- Discover existing CCUX projects in directories
- Extract project names from content/metadata
- Manage output directory creation

### `claude_integration.py`
Claude API integration with progress indicators.
- Run Claude CLI with real-time progress
- Handle timeouts and error conditions
- Stream output processing

### `content_processing.py`
HTML validation and content processing utilities.
- Parse and validate HTML content
- Strip code blocks and clean Claude output
- Safe JSON parsing with fallbacks

### `form_handling.py`
Interactive form generation and management.
- Generate contact, newsletter, signup forms
- Handle form styling and customization
- Form state management

### `section_management.py`
Section replacement with semantic ordering.
- Identify and extract HTML sections
- Replace specific sections while preserving others
- Maintain section ordering and structure

### `animation_utilities.py`
Theme-appropriate animations and interactions.
- Generate theme-specific animation rules
- Handle animation requirements by theme
- Animation utility functions

## Benefits

- **No Code Duplication**: Each function exists in only one place
- **Easy Maintenance**: Changes only need to be made in one location
- **Clear Dependencies**: Import system makes relationships clear
- **Better Testing**: Modular functions are easier to test
- **Shared Utilities**: Common functionality available to CLI and interactive modes