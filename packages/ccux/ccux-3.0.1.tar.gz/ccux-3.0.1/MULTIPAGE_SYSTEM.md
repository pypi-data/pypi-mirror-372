# 🌐 CCUX Multi-Page Website System

## Overview

The CCUX Multi-Page System transforms CCUX from a single-page generator into an intelligent multi-page website generator with smart analysis, selective generation, and parallel processing capabilities. Version 3.0.0 introduces this comprehensive system with production-ready features and robust error handling.

## ✨ Key Features

### 🧠 Intelligent Analysis
- **AI-Powered Page Detection**: Analyzes product descriptions to suggest relevant pages
- **Keyword-Based Fallback**: Uses keyword analysis when AI is unavailable
- **Confidence Scoring**: Rates each page suggestion with confidence levels
- **Smart Page Dependencies**: Understands page relationships and dependencies

### 🎯 Interactive Selection
- **Rich Terminal Interface**: Beautiful, interactive page selection with real-time feedback
- **Flexible Selection Options**: Toggle individual pages, select by confidence, or custom selection
- **Preview Mode**: Preview final selection before generation
- **Confirmation Workflow**: Clear confirmation before starting generation

### ⚡ Parallel Generation
- **Concurrent Processing**: Generates up to 3 pages simultaneously
- **Real-Time Progress**: Live progress tracking with individual page status
- **Intelligent Queuing**: Smart page ordering based on dependencies
- **Performance Optimized**: Efficient resource management and progress display

### 🛡️ Robust Error Handling
- **Graceful Failures**: If one page fails, others continue
- **Intelligent Retry Logic**: Exponential backoff for recoverable errors
- **Interactive Recovery**: User can choose which failed pages to retry
- **Detailed Error Reporting**: Clear error messages and recovery options

### 🔗 Smart Navigation
- **Automatic Navigation**: Generates consistent navigation across all pages
- **Theme-Aware Styling**: Navigation matches the selected theme
- **Mobile-Responsive**: Works perfectly on all device sizes
- **SEO-Optimized**: Proper HTML structure with accessibility features

### 📊 SEO & Analytics
- **XML Sitemap**: Automatic sitemap.xml generation for search engines
- **Robots.txt**: SEO-friendly robots.txt configuration
- **HTML Sitemap**: User-friendly sitemap page
- **Schema Markup**: Structured data for better search visibility

## 🚀 Usage

### Command Line Interface

```bash
# Basic usage
ccux multipage --desc "Your product description"

# With theme and output directory
ccux multipage --desc "SaaS platform for teams" --theme morphism --output ./my-website

# From file
ccux multipage --desc-file product-description.txt --theme brutalist

# With custom base URL for SEO
ccux multipage --desc "E-commerce platform" --base-url https://mysite.com
```

### Example Interactive Flow

```bash
ccux multipage --desc "TaskFlow: SaaS project management for remote teams"

# 1. 🔍 Analysis Phase
#    AI analyzes description and suggests 6 pages:
#    ✓ Homepage (100% confidence)
#    ✓ Features (85% confidence) 
#    ✓ Pricing (75% confidence)
#    ○ About (60% confidence)
#    ○ Contact (70% confidence)
#    ○ Case Studies (45% confidence)

# 2. 📝 Interactive Selection
#    User selects: Homepage, Features, Pricing, Contact

# 3. ⚡ Parallel Generation
#    🚀 Generating 4 pages in parallel...
#    [████████████████████] 100% Overall Progress
#    
#    ✓ Homepage     Generated successfully (1.2s)
#    ✓ Features     Generated successfully (1.8s)
#    ✓ Pricing      Generated successfully (1.5s)
#    ✓ Contact      Generated successfully (1.1s)

# 4. 🔗 Connection Phase
#    Building navigation system...
#    Generating SEO sitemap...

# 5. 🎉 Complete!
#    4/4 pages generated successfully
#    Navigation connected
#    SEO files created
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

### Three-Phase Execution Flow

1. **ANALYSIS PHASE**: Analyze product → Suggest pages → User selection
2. **GENERATION PHASE**: Parallel generation → Progress tracking → Error handling  
3. **CONNECTION PHASE**: Build navigation → Create sitemap → Generate summary

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

## 📁 Generated File Structure

```
output/
├── index.html                 # Homepage
├── features/
│   └── index.html            # Features page
├── pricing/
│   └── index.html            # Pricing page
├── about/
│   └── index.html            # About page
├── blog/
│   └── index.html            # Blog page
├── contact/
│   └── index.html            # Contact page
├── sitemap.xml               # SEO sitemap (main)
├── sitemap_index.xml          # Sitemap index file
├── sitemap.html              # User-friendly sitemap
├── robots.txt                # Search engine instructions
└── multipage_analysis.json   # Generation metadata
```

## 🎨 Theme Integration

The multi-page system fully integrates with all 13 CCUX themes:

- **Core Themes**: minimal, brutalist, playful, corporate
- **Modern Themes**: morphism, animated, terminal, aesthetic
- **Specialized Themes**: dark, vibrant, sustainable, data, illustrated

Each page maintains consistent theme styling while allowing for page-specific optimizations.

## 📊 Progress Tracking

Real-time progress display shows:

```
🚀 Generating 4 pages in parallel...

[██████████████████████] 75% Overall Progress

✓ Homepage     Generated successfully (1.8s)
⚡ Features     Generating... [█████-----] 60%
⏳ Pricing      Queued (starts when Features completes)  
⏳ Contact      Waiting for thread...

Pages completed: 1/4 | Failed: 0 | Remaining: 3
Estimated time remaining: ~45 seconds
```

## 🛠️ Error Handling

### Graceful Failure Recovery

```
❌ Generation Completed with 1 Failure

✓ Homepage     Success - /index.html
✓ Features     Success - /features/index.html  
❌ Pricing      Failed - API timeout (will retry)
✓ Contact      Success - /contact/index.html

Options:
[R] Retry failed pages only (1 page, ~2 min)
[G] Generate missing navigation anyway
[V] View error details
[Q] Quit and keep successful pages

Connected 3/4 pages successfully. Navigation built.
```

### Retry Strategies

- **Exponential Backoff**: 1s, 2s, 4s delay progression
- **Error Classification**: Distinguishes retryable vs permanent errors
- **User Choice**: Interactive retry menu for failed operations
- **Partial Success**: Connects successful pages even if some fail

## 🔍 SEO Features

### XML Sitemap Generation

The system generates both individual sitemaps and sitemap index files:

**sitemap.xml** (Main sitemap):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/features/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>
```

**sitemap_index.xml** (Sitemap index):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap.xml</loc>
    <lastmod>2024-01-15</lastmod>
  </sitemap>
</sitemapindex>
```

### Robots.txt

```
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

### SEO Recommendations

The system provides intelligent SEO recommendations:

- Submit sitemap to Google Search Console
- Set up Google Analytics
- Add schema markup for rich snippets
- Optimize page loading speeds
- Include meta descriptions and alt text

## 💡 Usage Examples

### SaaS Platform

```bash
ccux multipage --desc "CloudSync: File synchronization service for enterprises with advanced security, real-time collaboration, and API integrations. Three pricing tiers starting at $15/month."

# Generates: Homepage, Features, Pricing, Integrations, Contact
```

### E-commerce Store

```bash
ccux multipage --desc "EcoShop: Sustainable products marketplace. We curate eco-friendly items from verified suppliers. Founded by a team of environmental advocates."

# Generates: Homepage, About, Contact, Blog (for sustainable content)
```

### Consulting Firm

```bash
ccux multipage --desc "DataInsights: Business intelligence consulting. Our team of analysts helps companies make data-driven decisions. Case studies show 40% ROI improvement."

# Generates: Homepage, About, Case Studies, Contact
```

## 🔧 Configuration Options

### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--desc` | `-d` | Product description | Interactive prompt |
| `--desc-file` | | Description from file (.txt/.pdf) | None |
| `--theme` | `-t` | Design theme | minimal |
| `--base-url` | `-u` | Base URL for sitemap | https://example.com |
| `--output` | `-o` | Output directory | Auto-generated |

### Parallel Processing

- **Max Workers**: 3 concurrent pages (configurable)
- **Queue Strategy**: Dependency-aware ordering
- **Timeout**: 5-minute timeout per page
- **Progress Updates**: 2 refreshes per second

## 📈 Performance

### Generation Speed

- **Single Page**: ~60 seconds (full design thinking)
- **Multi-Page (4 pages)**: ~120 seconds (parallel processing)
- **Speedup**: ~50% faster than sequential generation

### Resource Usage

- **Memory**: Efficient threading with shared resources
- **API Calls**: Optimized prompts to minimize token usage
- **Disk I/O**: Streaming writes with progress tracking

## 🧪 Testing & Integration

### Integration with CCUX Interactive Mode

The multi-page system is fully integrated into the CCUX interactive application:

```bash
ccux init
# Select "Create Multi-Page Website" from the main menu
```

### Command Line Testing

```bash
# Test basic functionality
ccux multipage --desc "Test SaaS platform"

# Test with custom theme
ccux multipage --desc "Test platform" --theme morphism

# Test file input
echo "Test description" > test.txt
ccux multipage --desc-file test.txt
```

### Validation Points

The system validates:
- Page analysis accuracy and confidence scoring
- Parallel generation thread safety
- Navigation generation across all themes
- SEO file generation (sitemaps, robots.txt)
- Error recovery and retry mechanisms

## 🔮 Future Enhancements

### Planned Features

- **Dynamic Sitemap Updates**: Automatic sitemap regeneration after page updates
- **A/B Testing**: Generate multiple page variants for conversion optimization
- **Content Management**: Built-in content editing interface with live preview
- **Performance Analytics**: Page speed optimization suggestions and monitoring
- **Multi-language Support**: Internationalization capabilities with locale-aware generation
- **Advanced Page Types**: Support for specialized pages (testimonials, FAQ, documentation)
- **Theme Variants**: Page-specific theme customizations within the same website

### Extensibility

The modular architecture supports easy extension:

- Add new page types in `page_analysis.py`
- Create custom retry strategies in `retry_handler.py`
- Extend navigation patterns in `navigation_builder.py`
- Add new sitemap formats in `sitemap_generator.py`

## 🤝 Contributing

The multi-page system follows CCUX's modular architecture principles:

1. **No Code Duplication**: Each function exists in only one place
2. **Clean Separation**: Clear boundaries between analysis, generation, and connection
3. **Robust Error Handling**: Graceful degradation and recovery
4. **User-Centric Design**: Interactive and informative user experience

## 📚 API Reference

### Main Classes

- `MultipageGenerator`: Main orchestrator class
- `PageAnalyzer`: Intelligent page analysis and suggestion
- `PageSelector`: Interactive page selection interface
- `ParallelGenerator`: Multi-threaded page generation engine
- `NavigationBuilder`: Cross-page navigation system
- `SitemapGenerator`: SEO sitemap and robots.txt generation

### Key Functions

```python
# Main entry point
run_multipage_generation(description, output_dir, theme, base_url)

# Individual components
analyzer.analyze_description(description)
selector.interactive_selection(analysis_results)
generator.generate_all_pages()
nav_builder.connect_pages(pages, output_dir, theme)
sitemap_gen.generate_sitemap(pages, output_dir, base_url)
```

### Integration Points

The multi-page system integrates seamlessly with existing CCUX components:

- **Theme System**: All 13 themes work with multi-page generation
- **Interactive Mode**: Available through `ccux init` main menu
- **Cost Tracking**: Full token usage and cost analysis with `ccux cost`
- **Project Management**: Multi-page projects are auto-discovered by `ccux projects`
- **Section Regeneration**: Individual pages can be updated with `ccux regen`

---

The CCUX Multi-Page System represents a significant evolution from single-page generation to comprehensive website creation, maintaining the quality and user experience that makes CCUX exceptional while adding powerful new capabilities for modern web development.

**Version 3.0.0** introduces this production-ready multi-page system with intelligent analysis, parallel processing, robust error handling, and complete SEO optimization - making CCUX a comprehensive website generation platform.