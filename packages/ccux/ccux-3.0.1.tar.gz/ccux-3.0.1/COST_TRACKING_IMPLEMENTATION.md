# CCUX Cost Tracking Implementation

This document explains the cost tracking and reporting functionality added to CCUX.

## Overview

The CCUX cost tracking system provides comprehensive analysis of Claude API usage and estimated costs for landing page projects without modifying the existing workflow. All cost data is automatically tracked in the `design_analysis.json` files that CCUX already creates.

## Implementation Details

### 1. Cost Calculation Enhancement

**Enhanced Function**: `run_claude_with_progress()`
- **Location**: `src/ccux/cli_old.py:292`
- **Enhancement**: Added automatic cost calculation when Claude CLI doesn't provide cost data
- **Method**: Uses Claude 3.5 Sonnet pricing ($3/1M input tokens, $15/1M output tokens)

### 2. Fast Mode Cost Tracking

**Enhancement**: Added `design_analysis.json` creation for fast mode
- **CLI Location**: `src/ccux/cli_old.py:1725-1744`
- **Interactive Location**: `src/ccux/interactive.py:722-742`
- **Feature**: Fast mode now creates minimal design analysis files for cost tracking
- **Backward Compatible**: Existing fast mode projects without cost data show "No Data" status

```python
def calculate_estimated_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost based on Claude pricing"""
    input_cost = (input_tokens / 1_000_000) * 3.00
    output_cost = (output_tokens / 1_000_000) * 15.00
    return input_cost + output_cost
```

### 3. New Cost Command

**Command**: `ccux cost [PROJECT_DIR] [OPTIONS]`
- **Location**: `src/ccux/cli_old.py:2981`
- **Features**:
  - Analyzes single projects or all projects in current directory
  - Shows detailed breakdowns by operation type
  - Provides summary statistics across multiple projects
  - Reads existing `design_analysis.json` files (no workflow changes needed)

**Options**:
- `--detailed, -d`: Show operation-by-operation breakdown
- `--summary, -s`: Show only aggregated statistics
- `PROJECT_DIR`: Target specific project directory

### 4. Cost Data Analysis

**Function**: `analyze_project_costs()`
- **Purpose**: Extract and aggregate cost data from project metadata
- **Data Sources**:
  - `total_usage`: Main generation costs
  - `design_phases`: Individual phase costs (12-phase methodology)
  - `edit_history`: Content editing operations
  - `theme_history`: Theme change operations 
  - `form_history`: Form add/edit operations

**Cost Categories Tracked**:
1. **Initial Generation**: 
   - **Full Design Process**: Complete 12-phase UX methodology
   - **Fast Generation**: Direct landing page generation
2. **Design Phases**: Individual UX methodology phases (reference discovery, user research, etc.)
3. **Content Edits**: Using `ccux editgen` command
4. **Theme Changes**: Using `ccux theme` command
5. **Form Operations**: Using `ccux form` command

### 5. Existing Data Compatibility

**Backward Compatibility**: The system works with existing `design_analysis.json` files
- **No Migration Required**: Reads existing cost data structure
- **Graceful Fallbacks**: Handles missing cost fields appropriately
- **Historical Tracking**: Shows costs from past operations

## Usage Examples

### Basic Usage
```bash
# Show costs for all projects in current directory
ccux cost

# Analyze specific project
ccux cost my-landing-page

# Get detailed breakdown
ccux cost my-landing-page --detailed

# Summary only
ccux cost --summary
```

### Sample Output

**Basic Project Analysis**:
```
💰 CCUX Cost Analysis
==================================================

📁 My Landing Page
Input tokens: 45,230
Output tokens: 12,850
Total cost: $0.328

📊 Total Summary
------------------------------
Projects analyzed: 1
Total input tokens: 45,230
Total output tokens: 12,850
Total estimated cost: $0.328
```

**Detailed Breakdown**:
```
📁 My Landing Page (Full Design Process)
Input tokens: 45,230
Output tokens: 12,850
Total cost: $0.328

Operation Breakdown:
Operation                 In      Out    Cost     When
Full Design Process   42,150   11,200  $0.294   2024-08-22
Edit: Update pricing   2,080    1,200  $0.024   2024-08-22  
Theme Change to Dark   1,000      450  $0.010   2024-08-22

📁 Quick Website (Fast Generation)
Input tokens: 8,500
Output tokens: 3,200
Total cost: $0.073

Operation Breakdown:
Operation                 In      Out    Cost     When
Fast Generation        8,500    3,200  $0.073   2024-08-22
```

## Technical Architecture

### Data Flow
1. **Cost Capture**: `run_claude_with_progress()` captures token usage from Claude CLI
2. **Cost Calculation**: Automatic fallback calculation if Claude doesn't provide costs
3. **Data Storage**: Costs stored in existing `design_analysis.json` structure
4. **Cost Analysis**: `ccux cost` command reads and aggregates stored data
5. **Reporting**: Rich terminal output with tables and formatting

### Integration Points
- **No Workflow Changes**: Works with existing CCUX commands seamlessly
- **Automatic Tracking**: All operations automatically tracked in background
- **Claude CLI Integration**: Uses existing Claude CLI usage statistics
- **Project Detection**: Uses same project discovery as `ccux projects` command

## Benefits

### For Users
1. **Zero Configuration**: Works automatically with existing projects
2. **Historical Analysis**: Track costs over time and across projects
3. **Operation Transparency**: See exactly which operations cost what
4. **Budget Planning**: Estimate costs for similar future projects

### For Development
1. **Non-Invasive**: No changes to existing core functionality
2. **Extensible**: Easy to add new cost categories
3. **Maintainable**: Separate cost logic from generation logic
4. **Testable**: Isolated functions for cost calculation and analysis

## Error Handling

The system gracefully handles various scenarios:
- **Missing Files**: Clear messages when `design_analysis.json` not found
- **Corrupted Data**: Continues analysis with available data
- **No Projects**: Helpful guidance when no trackable projects exist
- **Partial Data**: Works with incomplete cost information

## Future Enhancements

Potential extensions to the cost tracking system:
1. **Cost Budgets**: Set spending limits per project
2. **Time Analysis**: Track generation time vs. cost relationships
3. **Export Options**: JSON, CSV export for further analysis
4. **Cost Optimization**: Suggest ways to reduce costs
5. **Team Reporting**: Aggregate costs across team members

## Configuration

The cost tracking system uses Claude pricing information that can be updated:

```python
# Located in calculate_estimated_cost() function
input_cost = (input_tokens / 1_000_000) * 3.00   # $3 per million input tokens
output_cost = (output_tokens / 1_000_000) * 15.00 # $15 per million output tokens
```

Update these values as Claude pricing changes.