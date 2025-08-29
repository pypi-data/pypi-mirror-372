# 🌐 CCUX Multi-Page Website System

## Overview

CCUX Multi-Page System generates complete multi-page websites from product descriptions using AI analysis and parallel processing. The system operates in a sophisticated 4-phase process with intelligent page analysis, parallel generation, and automatic navigation integration.

## Process Flow

The multi-page system operates in **4 distinct phases** with different behavior for interactive vs CLI usage:

### 1. Analysis & Page Selection Phase
**Analysis:**
- Analyzes product description using dual approach: AI analysis + keyword matching
- Suggests 8 possible page types: homepage, features, pricing, about, contact, blog, case-studies, integrations
- Returns confidence scores (0-1) and dynamic navigation names for each page
- AI provides product-specific navigation names (e.g., "Capabilities" instead of "Features")
- Merges keyword-based and AI-based suggestions for optimal accuracy

**Page Selection:**
- **Interactive Mode** (via `ccux init`): Rich terminal interface with:
  - Visual confidence bars and selection table
  - Multiple selection strategies: toggle individual, select all, high-confidence only, custom
  - Preview functionality and final confirmation
  - User can select/deselect any combination of suggested pages
- **CLI Mode** (via `ccux multipage --desc`): Auto-selects pages with confidence ≥ 0.5

### 2. Navigation Generation Phase  
- Generates consistent navigation HTML with product-specific dynamic names
- Creates responsive navigation with mobile hamburger menu
- Applies theme-specific styling matching overall design system
- Ensures proper data-page attributes for JavaScript active state detection
- Uses placeholder paths ({{HOME_PATH}}, {{PAGE_PATH_FEATURES}}) for later injection
- Validates navigation HTML and ensures accessibility compliance

### 3. Parallel Page Generation Phase
- Generates up to 3 pages concurrently using ThreadPoolExecutor
- Each page uses streamlined CCUX generation (without full 12-phase process)
- Pages generated WITHOUT navigation (content only) for clean separation
- Real-time progress tracking with success/failure reporting
- Pages generated: homepage (index.html), others in subfolders (features/index.html, etc.)
- Includes automatic retry mechanism for failed pages
- Usage tracking and cost calculation for each generated page

### 4. Navigation Injection & Finalization Phase
- Injects pre-generated navigation into all successfully created pages
- Replaces placeholder paths with correct relative paths based on page location
- Handles complex path resolution (root ↔ subfolder navigation)
- Generates comprehensive SEO files: sitemap.xml, robots.txt, sitemap.html
- Creates multipage_analysis.json with detailed generation metadata
- Adds JavaScript for active state detection and mobile menu functionality

## Command Syntax

```bash
ccux multipage --desc "PRODUCT_DESCRIPTION" [OPTIONS]
```

**Required:**
- `--desc "description"` - Product/service description
- `--desc-file FILE` - Path to file containing product description (supports .txt and .pdf files)

**Optional:**
- `--theme THEME` - Design theme (default: minimal)
- `--base-url URL` - Base URL for sitemap (default: https://example.com)
- `--output DIR` - Output directory (auto-generated if not specified)

## Execution Flow

### CLI Mode: `ccux multipage --desc "DESCRIPTION"`
```
Input: Product description + theme
  ↓
Phase 1 - Analysis: Dual AI+keyword analysis → confidence scores → auto-select ≥50%
  ↓
Phase 2 - Navigation: Generate theme-aware navigation HTML with placeholders
  ↓
Phase 3 - Generation: Parallel page creation (3 workers) WITHOUT navigation
  ↓
Phase 4 - Finalization: Inject navigation + generate SEO files + metadata
  ↓
Output: Complete multi-page website with navigation, sitemap, and analytics
```

### Interactive Mode: `ccux init` → "Create Multi-Page Website"
```
Input: Product description + theme
  ↓
Phase 1 - Analysis: Dual AI+keyword analysis → confidence scores → rich terminal interface
  ↓
Interactive Selection: Visual menu with confidence bars, multiple selection strategies
  ↓
Phase 2 - Navigation: Generate theme-aware navigation HTML with dynamic names
  ↓
Phase 3 - Generation: Parallel page creation with real-time progress tracking
  ↓
Phase 4 - Finalization: Navigation injection + SEO optimization + comprehensive metadata
  ↓
Output: Complete multi-page website with navigation, analytics, and usage tracking
```

## 🏗️ Architecture

### Core Components

```
src/ccux/
├── multipage.py                    # Main orchestrator
├── core/
│   ├── page_analysis.py           # Intelligent page detection
│   ├── page_selection.py          # Interactive selection interface
│   ├── parallel_generator.py      # Multi-threaded generation engine
│   ├── retry_handler.py           # Error handling & retry logic
│   ├── navigation_builder.py      # Cross-page navigation system
│   └── sitemap_generator.py       # SEO sitemap generation
```

### Four-Phase Execution Flow

1. **ANALYSIS & SELECTION PHASE**: Dual AI+keyword analysis → Confidence scoring → Dynamic navigation names → Interactive/Auto selection
2. **NAVIGATION GENERATION PHASE**: Theme-aware navigation HTML → Placeholder path system → Accessibility compliance → Mobile responsiveness
3. **PARALLEL GENERATION PHASE**: ThreadPoolExecutor (3 workers) → Content-only generation → Real-time progress → Retry mechanism → Usage tracking
4. **INJECTION & FINALIZATION PHASE**: Path resolution → Navigation injection → SEO files → Comprehensive metadata → Cost analysis

### Page Types & Detection

The system intelligently detects and suggests these page types:

| Page Type | Keywords | Priority | Description |
|-----------|----------|----------|-------------|
| **Homepage** | Always included | 1 | Main landing page with overview |
| **Features** | feature, functionality, tool, benefit | 2 | Detailed product capabilities |
| **Pricing** | pricing, plan, subscription, cost | 3 | Pricing plans and options |
| **About** | team, company, mission, story | 4 | Company and team information |
| **Contact** | contact, support, email, phone | 5 | Contact info and support |
| **Blog** | blog, articles, content, news | 6 | Content hub and resources |
| **Case Studies** | testimonial, success, customer | 7 | Customer success stories |
| **Integrations** | integration, API, connect | 8 | API and integration docs |

## Output Structure

```
output_dir/
├── index.html                    # Homepage with integrated navigation
├── [page-type]/index.html        # Generated pages in subfolders with navigation
├── sitemap.xml                   # XML sitemap for search engines
├── robots.txt                    # Search engine crawler instructions
├── sitemap.html                  # Human-readable sitemap
└── multipage_analysis.json       # Comprehensive generation metadata
```

**File Characteristics:**
- **HTML Pages**: Production-ready with integrated navigation, responsive design, SEO optimization, accessibility compliance
- **SEO Files**: XML/HTML sitemaps, robots.txt for optimal search engine discovery
- **Navigation System**: Consistent cross-page navigation with active state detection and mobile menu
- **Metadata**: Complete generation analytics including usage stats, timing, and cost breakdown

**Supported Themes:** minimal, brutalist, playful, corporate, morphism, animated, terminal, aesthetic, dark, vibrant, sustainable, data, illustrated

## Return Data

**Success Response:**
- `success`: boolean - Overall generation success
- `total_pages_requested`: int - Number of pages requested
- `pages_generated`: int - Number of successfully generated pages
- `successful_pages`: list - Generated page types
- `failed_pages`: list - Failed page types (if any)
- `output_directory`: string - Path to generated website
- `generation_time`: float - Total generation time in seconds
- `usage_stats`: object - Detailed cost and token usage breakdown
- `files_created`: list - All files created during generation

**Usage Statistics:**
- `input_tokens`: int - Total input tokens consumed
- `output_tokens`: int - Total output tokens generated  
- `cost`: float - Total estimated cost in USD
- `breakdown`: object - Cost breakdown by phase (analysis, navigation, page generation)

**Error Handling:**
- Graceful degradation - continues if individual pages fail
- Automatic retry mechanism for failed pages
- Partial success support with detailed reporting
- Comprehensive error logging and user feedback

## Performance

**Generation Time:**
- Single page: ~45-60 seconds
- Multi-page (4 pages): ~90-120 seconds (with navigation injection)
- Parallel processing provides ~60% speedup vs sequential
- Real-time progress tracking with phase-by-phase updates

**Resource Usage:**
- Memory: Efficient ThreadPoolExecutor with 3 concurrent workers
- API: Optimized prompts with intelligent content summarization
- Cost: Comprehensive tracking with phase-specific breakdown
- Disk: Streaming writes with automatic directory creation

**Scalability:**
- Handles up to 8 page types concurrently
- Intelligent retry mechanism for failed generations
- Usage tracking prevents cost overruns
- Automatic cleanup and error recovery

## Backend Integration Example

```python
import subprocess
import json
from pathlib import Path

def generate_multipage_website(description, theme="minimal", base_url="https://example.com", output_dir=None):
    """Generate multi-page website using CCUX with comprehensive error handling"""
    
    cmd = ["ccux", "multipage", "--desc", description, "--theme", theme, "--base-url", base_url]
    if output_dir:
        cmd.extend(["--output", output_dir])
    
    try:
        # Extended timeout for multi-page generation (10 minutes)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            # Parse metadata file for detailed results
            if output_dir:
                metadata_path = Path(output_dir) / "multipage_analysis.json"
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        metadata = json.load(f)
                        return {
                            "status": "success", 
                            "output": result.stdout,
                            "metadata": metadata,
                            "files_created": metadata.get("files_created", []),
                            "usage_stats": metadata.get("usage_stats", {}),
                            "successful_pages": metadata.get("successful_pages", [])
                        }
            
            return {"status": "success", "output": result.stdout}
        else:
            return {"status": "error", "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "Generation timed out after 10 minutes"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Usage Examples
result = generate_multipage_website("AI-powered project management SaaS", "morphism")
if result["status"] == "success":
    print(f"Generated {len(result.get('successful_pages', []))} pages")
    print(f"Total cost: ${result.get('metadata', {}).get('usage_stats', {}).get('cost', 0):.3f}")
```

## Key Points for Backend Integration

1. **Command**: `ccux multipage --desc "DESCRIPTION" --theme THEME --output DIR --base-url URL`
2. **Timeout**: Set 10-minute timeout for full multi-page generation
3. **Error Handling**: Check return code, capture stdout/stderr, parse metadata JSON
4. **Output**: Complete website with navigation + SEO files + comprehensive metadata
5. **Performance**: ~90-120 seconds for 4-page website with parallel processing
6. **Cost Tracking**: Full usage analytics with phase-specific breakdown
7. **Metadata**: Parse multipage_analysis.json for detailed generation results

