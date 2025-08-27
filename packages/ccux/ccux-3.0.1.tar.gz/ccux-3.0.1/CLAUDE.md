# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CCUX (Claude Code UI Generator) is a sophisticated Python CLI tool that automatically generates conversion-optimized frontend landing pages using professional UX design thinking methodology. The tool features both command-line and interactive interfaces, leveraging Claude AI to implement a comprehensive 12-phase design process used by professional UX agencies.

### Architecture
- **Interactive Interface** (`src/ccux/interactive.py`): Rich terminal application with project management
- **Main CLI** (`src/ccux/cli.py`): User-facing CLI with help system and command delegation
- **Implementation CLI** (`src/ccux/cli_old.py`): Core command implementations and business logic
- **Multi-Page Generator** (`src/ccux/multipage.py`): Orchestrator for intelligent multi-page website generation
- **Modular Core System** (`src/ccux/core/`): Organized utility modules by function
  - `usage_tracking.py`: Cost calculation and token analytics
  - `signal_handling.py`: Graceful interrupt handling
  - `configuration.py`: YAML config management
  - `project_management.py`: Project discovery and selection
  - `claude_integration.py`: Claude API integration with progress
  - `content_processing.py`: HTML validation and content processing
  - `form_handling.py`: Interactive form generation and management
  - `section_management.py`: Section replacement with semantic ordering
  - `animation_utilities.py`: Theme-appropriate animations
  - `page_analysis.py`: Intelligent page detection for multi-page websites
  - `page_selection.py`: Interactive page selection interface with confidence scoring
  - `parallel_generator.py`: Multi-threaded page generation engine
  - `navigation_builder.py`: Cross-page navigation system builder
  - `sitemap_generator.py`: SEO sitemap and robots.txt generation
  - `retry_handler.py`: Error handling and retry logic for robust generation
- **Theme System** (`src/ccux/theme_specifications.py`): 13 professional design themes
- **Prompt Templates** (`src/ccux/prompt_templates.py`): 12-phase design methodology prompts
- **Web Scraping** (`src/ccux/scrape.py`, `src/ccux/scrape_simple.py`): Competitor analysis automation

## Core Capabilities

### 🎨 Interactive Application
The main interface launched with `ccux init`:
- **Single-Page Creation**: Guided landing page generation with theme/form selection
- **Multi-Page Websites**: Complete website generation with intelligent page analysis
- **Multi-Project Management**: Discover, select, and manage multiple projects
- **Visual Section Editing**: Number-based section selection with live feedback  
- **Theme Switching**: Interactive theme selection with preview
- **Form Management**: Add, remove, customize contact forms with visual feedback
- **Smart Detection**: Auto-detects themes, sections, and project configurations
- **ESC Key Support**: Press ESC at any point to immediately exit the application

### 🚀 AI-Powered Generation
Implements professional UX methodology:
- **Reference Discovery**: Automatically finds 3 competitor websites using Claude AI
- **Screenshot Capture**: Uses Playwright to capture competitor landing pages
- **12-Phase Design Process**: Complete UX research including personas, empathy maps, user journeys
- **Strategic Copywriting**: Conversion-optimized headlines and content based on research
- **Design Systems**: Consistent visual languages with proper typography and color schemes

### 🎭 13 Professional Themes
**Core Themes:**
- `minimal`: Clean, content-focused design (Dieter Rams principles)  
- `brutalist`: Raw, honest design (Brutalist architecture inspired)
- `playful`: Joyful, approachable design with organic shapes
- `corporate`: Traditional, trustworthy business design

**Modern Themes:**
- `morphism`: Soft, tactile design (neumorphism + glassmorphism)
- `animated`: Motion-first design where animation drives experience  
- `terminal`: Monospace, CLI-inspired aesthetic for developers
- `aesthetic`: Retro-futuristic Y2K and vaporwave styling

**Specialized Themes:**
- `dark`: Modern dark theme optimized for reduced eye strain
- `vibrant`: Colorful, dopamine-rich design that energizes users
- `sustainable`: Nature-inspired design for eco-conscious brands
- `data`: Information-dense design for dashboards and analytics  
- `illustrated`: Hand-drawn, custom illustration-driven design

### ⚡ Advanced Section Management
- **Precision Targeting**: Regenerate only specific sections (hero, features, pricing, footer, etc.)
- **Content Preservation**: Maintains untouched sections exactly as they are
- **Smart Context Detection**: Auto-detects product description from `design_analysis.json`
- **Theme Consistency**: Preserves visual design while updating content
- **Section Detection**: Automatically identifies available sections in HTML

## Commands Reference

### `ccux init`
Launch CCUX Interactive Application (Main Entry Point)

**Description:** The primary interface providing guided project creation, management, and customization through rich terminal menus.

**Features:**
- Single-page project creation wizard with theme and form selection
- **Multi-page website generation** with intelligent page analysis and parallel processing
- Multi-project management and discovery
- Visual section regeneration with numbered selection
- Interactive theme switching with live preview
- Form management (contact, newsletter, signup forms)
- Built-in help system and workflows
- Content editing with natural language instructions
- **ESC Key Support**: Press ESC anywhere to immediately exit

### `ccux gen`
Generate conversion-optimized landing page using AI design methodology

**Options:**
- `--desc, -d TEXT`: Product description
- `--desc-file FILE`: Path to file containing product description (supports .txt and .pdf files)
- `--url, -u URL`: Reference URLs (max 3, can be used multiple times)
- `--framework, -f [html|react]`: Output framework (default: html)
- `--theme, -t THEME`: Design theme (default: minimal)
- `--no-design-thinking`: Skip full design process for faster generation
- `--include-forms`: Include contact forms in the landing page
- `--analyze-images/--no-analyze-images`: Enable/disable visual analysis of competitor screenshots (default: enabled, uses more tokens when enabled)
- `--output, -o DIR`: Output directory

**Examples:**
```bash
# Interactive mode (recommended)
ccux gen

# Full design process with theme
ccux gen --desc "AI project management tool" --theme brutalist

# Fast generation mode
ccux gen --desc "SaaS platform" --no-design-thinking

# With competitor analysis (visual analysis enabled by default)
ccux gen --desc "Video platform" --url https://loom.com --url https://vimeo.com

# Load description from PDF file
ccux gen --desc-file product-description.pdf --theme minimal

# Save tokens by disabling image analysis
ccux gen --desc "SaaS platform" --no-analyze-images

# React output with forms
ccux gen --desc "Landing page" --framework react --include-forms
```

### `ccux regen`
Regenerate specific sections of existing landing pages

**Options:**  
- `--section, -s TEXT`: Section(s) to regenerate (comma-separated)
- `--all`: Regenerate all sections
- `--desc, -d TEXT`: Product description (auto-detected if not provided)
- `--file, -f FILE`: Path to landing page file
- `--output, -o DIR`: Output directory

**Key Features:**
- **Precision Targeting**: Only regenerates specified sections
- **Smart Context**: Auto-detects product description from project metadata
- **Theme Preservation**: Maintains existing design consistency
- **Section Detection**: Automatically identifies available sections

**Examples:**
```bash
# Regenerate hero section only
ccux regen --section hero

# Regenerate multiple sections  
ccux regen --section hero,features,pricing

# Regenerate all sections
ccux regen --all

# Target specific file
ccux regen --section pricing --file custom/page.html
```

**Note:** Advanced commands like `editgen`, `theme`, and `form` are available through the interactive application launched with `ccux init`. The interactive interface provides guided workflows for these advanced features with rich terminal UI and visual feedback.

### `ccux multipage`
Generate intelligent multi-page website with parallel processing

**Options:**
- `--desc, -d TEXT`: Product description for multi-page website
- `--desc-file FILE`: Path to file containing product description (supports .txt and .pdf files)
- `--theme, -t THEME`: Design theme (default: minimal)
- `--base-url, -u URL`: Base URL for sitemap generation (default: https://example.com)
- `--output, -o DIR`: Output directory

**Key Features:**
- **Intelligent Analysis**: AI-powered page detection with confidence scoring
- **Interactive Selection**: Rich terminal interface for page selection
- **Parallel Generation**: Generate multiple pages simultaneously
- **Smart Navigation**: Automatic cross-page navigation and linking
- **SEO Optimization**: XML/HTML sitemaps and robots.txt generation
- **Error Handling**: Graceful failure recovery with retry options

**Examples:**
```bash
# Basic multi-page website
ccux multipage --desc "SaaS platform for remote teams"

# With custom theme and base URL
ccux multipage --desc "E-commerce platform" --theme morphism --base-url https://mystore.com

# From PDF description file
ccux multipage --desc-file product-description.pdf --theme brutalist

# Interactive mode (recommended)
ccux init
# Then select "Create Multi-Page Website" from the menu
```

**Three-Phase Process:**
1. **Analysis Phase**: AI analyzes description → Suggests pages → Interactive selection
2. **Generation Phase**: Parallel page generation → Real-time progress → Error handling
3. **Connection Phase**: Build navigation → Generate sitemaps → SEO optimization

### `ccux help`
Comprehensive help system with specialized topics

**Usage:** `ccux help [TOPIC]`

**Topics:**
- `quickstart`: Step-by-step setup guide for new users
- `themes`: Complete theme guide with descriptions and use cases
- `examples`: Common usage patterns and practical scenarios  
- `workflows`: Step-by-step workflows for different user types

### `ccux cost`
Show cost analysis and token usage for CCUX projects

**Usage:** `ccux cost [PROJECT_DIR] [OPTIONS]`

**Options:**
- `--detailed, -d`: Show detailed breakdown by operation type
- `--summary, -s`: Show summary statistics only  
- `PROJECT_DIR`: Analyze specific project (optional, defaults to all projects in current directory)

**Features:**
- **Token Analysis**: Input/output token usage for all operations
- **Cost Estimation**: Calculated costs based on Claude pricing
- **Operation Breakdown**: Costs by generation phase, edits, theme changes, form operations
- **Multi-Project Reports**: Aggregate costs across multiple projects
- **Historical Tracking**: Shows costs from design_analysis.json files
- **Full & Fast Mode Support**: Tracks costs for both design thinking and quick generation modes

**Examples:**
```bash
# Analyze all projects in current directory
ccux cost

# Analyze specific project with detailed breakdown  
ccux cost my-landing-page --detailed

# Show summary only across all projects
ccux cost --summary

# Detailed analysis of specific project
ccux cost ./output/landing-page --detailed
```

### `ccux projects`
List and discover existing CCUX projects in current directory

**Features:**
- Discovers all projects with both `index.html` and `design_analysis.json`
- Shows project names extracted from content or metadata
- Displays project status and directory information

### `ccux version`
Show version information and basic usage guidance

## Design Workflow

CCUX implements a comprehensive 12-phase professional design methodology:

1. **Reference Discovery** - Auto-finds competitor websites using Claude AI
2. **Screenshot Capture** - Playwright automation captures competitor pages  
3. **Deep Product Understanding** - Value proposition and problem analysis
4. **Competitive UX Analysis** - Screenshot analysis for patterns and opportunities
5. **User Empathy Mapping** - User research, personas, and pain points
6. **Define Site Flow** - Journey mapping and lean sitemap creation
7. **Content Strategy** - Strategic copy development before visual design
8. **Wireframe Validation** - Mobile-first layout structure validation
9. **Design System** - Typography, colors, spacing, WCAG compliance
10. **High-Fidelity Design** - Interactive elements and visual polish
11. **Final Copy Generation** - Conversion-optimized copy refinement
12. **Implementation** - Production-ready code generation

## Output Structure

### Generated Files

**Single-Page Projects:**
- `index.html` or `App.jsx` - Main landing page file
- `design_analysis.json` - Complete design research and metadata
- `*.jpg` - Competitor screenshot references (when applicable)

**Multi-Page Projects:**
- `index.html` - Homepage file
- `features/index.html`, `pricing/index.html`, etc. - Individual page files
- `multipage_analysis.json` - Multi-page generation metadata
- `sitemap.xml` - XML sitemap for search engines
- `sitemap.html` - Human-readable sitemap
- `robots.txt` - Search engine crawler instructions

### HTML Features
- **Semantic Structure** with proper heading hierarchy and ARIA labels
- **TailwindCSS Styling** with custom design system implementation
- **Responsive Design** with mobile-first breakpoints  
- **SEO Optimization** with meta tags and schema markup
- **Performance** with optimized images and minimal dependencies
- **Section Markers** with HTML comments for precise regeneration
- **Accessibility** following WCAG guidelines

### Section Identification
Pages use HTML comment markers for section management:
```html
<!-- START: hero -->
<section id="hero">...</section>
<!-- END: hero -->

<!-- START: features -->  
<section id="features">...</section>
<!-- END: features -->
```

## Claude Integration

### AI Processing
- **Claude CLI Integration**: Uses `claude --print` for AI processing
- **Timeout Protection**: 5-minute timeout per Claude invocation
- **Usage Tracking**: Displays input/output tokens and estimated costs
- **Error Handling**: Graceful fallbacks with user-friendly messages
- **Streaming Output**: Real-time progress indication during generation

### Token Optimization
- **Smart Summarization**: Auto-summarizes product descriptions >100 words to optimize usage
- **Screenshot Compression**: JPEG compression for captured images
- **Reference Limits**: Maximum 3 competitor URLs to prevent prompt bloat
- **Context Management**: Efficient prompt structuring for optimal results

## Configuration

### Project Configuration (`ccux.yaml`)
Optional configuration file for project defaults:
```yaml
framework: html              # html or react
theme: minimal              # Any available theme
sections: [hero, features, pricing, footer]
claude_cmd: claude          # Claude CLI command
output_dir: output/landing-page
```

### Environment Variables
- `CCUX_CLAUDE_CMD`: Override default Claude CLI command
- `CCUX_DEFAULT_THEME`: Set default theme for projects
- `CCUX_OUTPUT_DIR`: Default output directory

## Development Notes

### Code Architecture
- **Modular Design**: Clean separation of concerns with organized core modules
- **Command Delegation**: User-facing CLI delegates to implementation CLI for complex operations
- **Shared Utilities**: Common functionality centralized in `src/ccux/core/` modules
- **No Code Duplication**: Each function exists in only one place, imported where needed
- **Theme System**: Comprehensive theme specifications with design philosophy and implementation rules
- **Error Handling**: Robust error handling with graceful degradation
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Easy Maintenance**: Modular structure makes finding and modifying code much easier

### Dependencies
- **Typer** (≥0.12.0): CLI framework with rich terminal features
- **Rich** (≥13.7.0): Terminal formatting, progress bars, and UI components
- **Playwright** (≥1.45.0): Web scraping and screenshot automation
- **PyYAML** (≥6.0.1): Configuration file parsing
- **PyPDF2** (≥3.0.0): PDF processing for description files

### File Structure
```
src/ccux/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point for python -m ccux
├── cli.py                   # User-facing CLI with help system
├── cli_old.py               # Implementation CLI with core commands
├── interactive.py           # Interactive application interface
├── multipage.py             # Multi-page website generation orchestrator
├── core/                    # Modular utility system
│   ├── __init__.py
│   ├── README.md            # Core modules documentation
│   ├── usage_tracking.py    # Cost calculation and analytics
│   ├── signal_handling.py   # Graceful interrupt handling
│   ├── configuration.py     # YAML config management
│   ├── project_management.py # Project discovery and selection
│   ├── claude_integration.py # Claude API integration
│   ├── content_processing.py # HTML validation and processing
│   ├── form_handling.py     # Form generation and management
│   ├── section_management.py # Section replacement logic
│   ├── animation_utilities.py # Theme-appropriate animations
│   ├── page_analysis.py     # Intelligent page detection for multi-page websites
│   ├── page_selection.py    # Interactive page selection interface
│   ├── parallel_generator.py # Multi-threaded page generation engine
│   ├── navigation_builder.py # Cross-page navigation system builder
│   ├── sitemap_generator.py # SEO sitemap and robots.txt generation
│   └── retry_handler.py     # Error handling and retry logic
├── prompt_templates.py      # 12-phase design methodology prompts
├── theme_specifications.py  # Theme system with 13 professional themes
├── scrape.py               # Advanced Playwright web scraping
└── scrape_simple.py        # Simplified screenshot capture
```

## Modular Architecture Benefits

The recent reorganization provides significant improvements:

### 🧹 **Code Deduplication**  
- **78% Reduction**: Eliminated duplicate code through smart modularization
- **Organized Core Modules**: Each utility function exists in only one place
- **Clean Imports**: Clear dependency relationships between modules
- **Multi-Page Integration**: 6 new specialized modules seamlessly integrated

### 📖 **Improved Readability**
- `cli.py`: Clean user interface with comprehensive help system
- `cli_old.py`: Focused implementation with core business logic
- `multipage.py`: Dedicated orchestrator for multi-page website generation
- `core/` modules: Logical organization by function and responsibility

### 🔧 **Better Maintainability**
- Changes only need to be made in one location
- Easy to find and modify specific functionality
- Clear separation between CLI interface and implementation
- Modular testing becomes straightforward

### 🏗️ **Enhanced Development**
- New features can be added to appropriate modules
- Import system makes dependencies clear and manageable
- Core utilities shared between CLI, interactive, and multi-page modes
- Better code reuse across the entire application
- Parallel processing capabilities for scalable website generation

## Important Notes

- **Production Ready**: All generated code is production-ready with proper SEO, accessibility, and performance optimization
- **No Manual Editing Required**: Generated HTML/React can be deployed immediately
- **Extensible**: Theme system and prompt templates can be extended for custom requirements  
- **Professional Quality**: Uses methodology from professional UX agencies and design systems
- **Developer Friendly**: Clean, semantic code that developers can easily modify and extend