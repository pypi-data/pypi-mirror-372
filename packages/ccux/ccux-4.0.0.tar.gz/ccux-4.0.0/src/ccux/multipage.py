"""
CCUX Multi-Page Website Generator

Main orchestrator for intelligent multi-page website generation with
smart analysis, selective generation, and parallel processing.
"""

import os
import json
import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.align import Align

# Import core modules
from .core.page_analysis import PageAnalyzer
from .core.page_selection import PageSelector
from .core.parallel_generator import ParallelGenerator
from .core.navigation_builder import NavigationBuilder
from .core.sitemap_generator import SitemapGenerator
from .core.retry_handler import RetryHandler
from .core.project_management import get_next_available_output_dir
from .core.claude_integration import summarize_long_description
from .core.configuration import Config
from .core.usage_tracking import get_latest_usage, calculate_usage_difference

# Import existing CCUX functionality
from .prompt_templates import (
    deep_product_understanding_prompt,
    implementation_prompt,
    get_animation_requirements
)
from .theme_specifications import THEME_SPECIFICATIONS, get_theme_choices


class MultipageGenerator:
    """Main orchestrator for multi-page website generation"""
    
    def __init__(self):
        self.console = Console()
        self.config = Config()
        
        # Initialize components
        self.analyzer = PageAnalyzer()
        self.selector = PageSelector()
        self.generator = ParallelGenerator(max_workers=3)
        self.nav_builder = NavigationBuilder()
        self.sitemap_gen = SitemapGenerator()
        self.retry_handler = RetryHandler()
        
        # Generation state
        self.product_description = ""
        self.theme = "minimal"
        self.output_dir = ""
        self.base_url = "https://example.com"
        self.site_name = "Website"
        self.analysis_results = {}
        self.selected_pages = []
        self.generation_results = {}
        self.navigation_html = ""  # Store pre-generated navigation
        
        # Cost tracking across all phases
        self.total_usage_stats = {
            'analysis_cost': 0.0,
            'navigation_cost': 0.0,
            'page_generation_cost': 0.0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_cost': 0.0
        }
        
    def generate_multipage_website(self, description: str, output_dir: Optional[str] = None,
                                 theme: str = "minimal", base_url: str = "https://example.com", 
                                 interactive: bool = True) -> Dict[str, Any]:
        """Complete three-phase multi-page website generation"""
        
        self.product_description = description
        self.theme = theme
        self.output_dir = output_dir or get_next_available_output_dir()
        self.base_url = base_url
        self.interactive = interactive
        
        # Extract site name from description
        self.site_name = self._extract_site_name(description)
        
        try:
            # Phase 1: Analysis & Selection
            self.console.print(f"\n[bold blue]🔍 Phase 1: Intelligent Analysis[/bold blue]")
            analysis_success = self._phase_1_analysis()
            
            if not analysis_success:
                return {'success': False, 'phase': 1, 'error': 'Analysis phase failed'}
            
            # Phase 2: Navigation Generation
            self.console.print(f"\n[bold blue]🧭 Phase 2: Navigation Generation[/bold blue]")
            navigation_success = self._phase_2_navigation()
            
            if not navigation_success:
                return {'success': False, 'phase': 2, 'error': 'Navigation generation failed'}
            
            # Phase 3: Parallel Page Generation
            self.console.print(f"\n[bold blue]⚡ Phase 3: Parallel Page Generation[/bold blue]")
            generation_success = self._phase_3_generation()
            
            if not generation_success:
                return {'success': False, 'phase': 3, 'error': 'Page generation failed'}
            
            # Phase 4: Navigation Injection & Finalization
            self.console.print(f"\n[bold blue]🔗 Phase 4: Navigation Injection & Finalization[/bold blue]")
            finalization_success = self._phase_4_finalization()
            
            # Generate final summary
            final_results = self._create_final_summary()
            
            self.console.print(f"\n[bold green]🎉 Multi-page website generation complete![/bold green]")
            self._display_final_results(final_results)
            
            return final_results
            
        except KeyboardInterrupt:
            self.console.print(f"\n[yellow]⚠️  Generation cancelled by user[/yellow]")
            return {'success': False, 'cancelled': True}
        except Exception as e:
            self.console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
            return {'success': False, 'error': str(e)}
    
    def _phase_1_analysis(self) -> bool:
        """Phase 1: Analyze description and get page selection"""
        
        try:
            # Get usage before analysis
            pre_analysis_usage = get_latest_usage()
            
            # Analyze the product description
            self.console.print("[cyan]Analyzing product description...[/cyan]")
            self.analysis_results = self.analyzer.analyze_description(self.product_description)
            
            # Track analysis cost
            post_analysis_usage = get_latest_usage()
            analysis_usage_stats = calculate_usage_difference(pre_analysis_usage, post_analysis_usage)
            if analysis_usage_stats:
                self.total_usage_stats['analysis_cost'] = analysis_usage_stats.get('cost', 0.0)
                self.total_usage_stats['total_input_tokens'] += analysis_usage_stats.get('input_tokens', 0)
                self.total_usage_stats['total_output_tokens'] += analysis_usage_stats.get('output_tokens', 0)
            
            # Page selection (interactive or automatic)
            if self.interactive:
                self.selected_pages = self.selector.interactive_selection(self.analysis_results)
            else:
                # Auto-select pages with confidence >= 50%
                self.selected_pages = [
                    page['type'] for page in self.analysis_results['suggested_pages'] 
                    if page.get('selected', False) or page['confidence'] >= 0.5
                ]
                self.console.print(f"[yellow]📄 Auto-selected {len(self.selected_pages)} pages: {', '.join(self.selected_pages)}[/yellow]")
            
            if not self.selected_pages:
                self.console.print("[red]❌ No pages selected for generation[/red]")
                return False
            
            # Confirm selection (only in interactive mode)
            if self.interactive and not self.selector.confirm_selection(self.selected_pages):
                self.console.print("[yellow]⚠️  Generation cancelled[/yellow]")
                return False
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Analysis phase error: {e}[/red]")
            return False
    
    def _phase_2_navigation(self) -> bool:
        """Phase 2: Generate navigation HTML first"""
        
        try:
            # Get usage before navigation generation
            pre_nav_usage = get_latest_usage()
            
            self.console.print("[cyan]Generating navigation system...[/cyan]")
            
            # Create navigation prompt
            nav_prompt = self._create_navigation_prompt()
            
            # Generate navigation HTML
            from .core.claude_integration import run_claude_with_progress
            navigation_html, nav_usage_stats = run_claude_with_progress(
                nav_prompt, 
                "Generating navigation HTML..."
            )
            
            # Track navigation cost
            if not nav_usage_stats or nav_usage_stats.get('input_tokens', 0) == 0:
                # Fallback to usage difference if run_claude_with_progress didn't return stats
                post_nav_usage = get_latest_usage()
                nav_usage_stats = calculate_usage_difference(pre_nav_usage, post_nav_usage)
            
            if nav_usage_stats:
                self.total_usage_stats['navigation_cost'] = nav_usage_stats.get('cost', 0.0)
                self.total_usage_stats['total_input_tokens'] += nav_usage_stats.get('input_tokens', 0)
                self.total_usage_stats['total_output_tokens'] += nav_usage_stats.get('output_tokens', 0)
            
            # Clean and store navigation
            self.navigation_html = self._clean_navigation_html(navigation_html)
            
            # Validate navigation
            if not self.navigation_html or len(self.navigation_html.strip()) < 50:
                self.console.print("[red]❌ Navigation generation failed - empty or too short[/red]")
                return False
            
            self.console.print("[green]✅ Navigation HTML generated successfully[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Navigation generation error: {e}[/red]")
            return False
    
    def _phase_3_generation(self) -> bool:
        """Phase 3: Generate pages in parallel WITHOUT navigation"""
        
        try:
            # Prepare generation tasks (now without navigation)
            self._prepare_generation_tasks_without_navigation()
            
            # Generate pages in parallel
            self.generation_results = self.generator.generate_all_pages()
            
            # Display generation summary
            self.generator.display_final_summary()
            
            # Handle failed pages if any
            failed_pages = self.generator.get_failed_pages()
            
            if failed_pages:
                retry_menu = self.retry_handler.create_retry_menu(failed_pages, "pages")
                
                if retry_menu:
                    self.console.print(f"[yellow]🔄 Retrying {len(retry_menu)} failed pages...[/yellow]")
                    retry_results = self.generator.retry_failed_pages()
                    
                    # Update results
                    for page_type, result in retry_results.items():
                        self.generation_results[page_type] = result
            
            # Check if we have any successful pages
            successful_pages = [page for page, result in self.generation_results.items() if result.success]
            
            if not successful_pages:
                self.console.print("[red]❌ No pages generated successfully[/red]")
                return False
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Generation phase error: {e}[/red]")
            return False
    
    def _phase_4_finalization(self) -> bool:
        """Phase 4: Inject navigation into pages and generate sitemap"""
        
        try:
            successful_pages = [page for page, result in self.generation_results.items() if result.success]
            
            if not successful_pages:
                return False
            
            # Inject navigation into all generated pages
            self.console.print("[cyan]Injecting navigation into pages...[/cyan]")
            injection_results = self._inject_navigation_into_pages(successful_pages)
            
            if not injection_results:
                self.console.print("[red]❌ Navigation injection failed[/red]")
                return False
            
            # Generate sitemap
            self.console.print("[cyan]Generating SEO sitemap...[/cyan]")
            sitemap_results = self.sitemap_gen.generate_sitemap(
                successful_pages, self.output_dir, self.base_url
            )
            
            # Create HTML sitemap
            html_sitemap_path = self.sitemap_gen.create_html_sitemap(
                successful_pages, self.output_dir, self.site_name
            )
            
            # Save generation metadata
            self._save_generation_metadata(successful_pages, injection_results, sitemap_results)
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Finalization phase error: {e}[/red]")
            return False
    
    def _prepare_generation_tasks_without_navigation(self) -> None:
        """Prepare all generation tasks for parallel execution WITHOUT navigation"""
        
        # Summarize description if needed
        desc_for_generation = summarize_long_description(self.product_description)
        
        # Get optimized page order
        ordered_pages = self.analyzer.optimize_page_order(self.selected_pages)
        
        # Create generation tasks
        for i, page_type in enumerate(ordered_pages):
            
            # Create page-specific prompt WITHOUT navigation placeholders
            prompt = self._create_page_prompt_without_navigation(page_type, desc_for_generation)
            
            # Determine output path
            output_path = self._get_page_output_path(page_type)
            
            # Add task to generator
            self.generator.add_task(
                page_type=page_type,
                config=self.analyzer.page_types[page_type],
                prompt=prompt,
                output_path=output_path,
                priority=i + 1  # Priority based on order
            )
    
    def _create_page_prompt(self, page_type: str, description: str) -> str:
        """Create generation prompt for a specific page type"""
        
        # Get theme specifications
        theme_spec = THEME_SPECIFICATIONS.get(self.theme)
        if theme_spec:
            theme_rules = {
                'visual_characteristics': theme_spec.visual_characteristics,
                'design_philosophy': theme_spec.design_philosophy,
                'target_audience': theme_spec.target_audience
            }
        else:
            theme_rules = {}
        
        # Base prompt for the page
        if page_type == 'homepage':
            page_prompt = f"""Generate a conversion-optimized homepage for this product:

{description}

Create a complete HTML landing page that includes:
- Hero section with compelling headline and CTA
- Key features overview
- Social proof/testimonials if mentioned
- Clear value proposition
- Call-to-action sections

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

This page is part of a multi-page website. Focus on overview and driving visitors to other pages.
Include navigation placeholders that will be filled later.

Return only the complete HTML code."""

        elif page_type == 'features':
            page_prompt = f"""Generate a detailed features page for this product:

{description}

Create a complete HTML page that includes:
- Comprehensive feature breakdown
- Detailed explanations of capabilities
- Feature comparisons or tiers
- Visual elements and icons
- Integration information if mentioned

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

This is part of a multi-page website. Focus on detailed feature explanations.
Include navigation placeholders that will be filled later.

Return only the complete HTML code."""

        elif page_type == 'pricing':
            page_prompt = f"""Generate a pricing page for this product:

{description}

Create a complete HTML page that includes:
- Clear pricing tiers/plans
- Feature comparison between plans
- FAQ about pricing
- Call-to-action for each plan
- Money-back guarantee if appropriate

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

This is part of a multi-page website. Focus on pricing clarity and conversion.
Include navigation placeholders that will be filled later.

Return only the complete HTML code."""

        elif page_type == 'about':
            page_prompt = f"""Generate an about page for this company/product:

{description}

Create a complete HTML page that includes:
- Company story and mission
- Team information if mentioned
- Company values and vision
- History and milestones
- Contact information integration

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

This is part of a multi-page website. Focus on building trust and authority.
Include navigation placeholders that will be filled later.

Return only the complete HTML code."""

        elif page_type == 'contact':
            page_prompt = f"""Generate a contact page for this company/product:

{description}

Create a complete HTML page that includes:
- Contact form
- Contact information (email, phone if available)
- Office address if mentioned
- Support options
- FAQ section if appropriate

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

This is part of a multi-page website. Focus on making it easy to get in touch.
Include navigation placeholders that will be filled later.

Return only the complete HTML code."""

        else:
            # Generic prompt for other page types
            page_prompt = f"""Generate a {page_type.replace('-', ' ')} page for this product:

{description}

Create a complete HTML page focused on {page_type.replace('-', ' ')} information.

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

This is part of a multi-page website.
Include navigation placeholders that will be filled later.

Return only the complete HTML code."""
        
        return page_prompt
    
    def _get_page_output_path(self, page_type: str) -> str:
        """Get the output file path for a page"""
        
        if page_type == 'homepage':
            return os.path.join(self.output_dir, 'index.html')
        else:
            return os.path.join(self.output_dir, page_type, 'index.html')
    
    def _extract_site_name(self, description: str) -> str:
        """Extract site name from product description"""
        
        # Simple extraction - look for company names or product names
        words = description.split()
        
        # Look for capitalized words that might be names
        potential_names = [word for word in words[:20] if word[0].isupper() and len(word) > 2]
        
        if potential_names:
            return potential_names[0]
        
        return "Website"
    
    def _create_navigation_prompt(self) -> str:
        """Create prompt to generate navigation HTML"""
        
        # Get theme specifications
        theme_spec = THEME_SPECIFICATIONS.get(self.theme)
        if theme_spec:
            theme_rules = {
                'visual_characteristics': theme_spec.visual_characteristics,
                'design_philosophy': theme_spec.design_philosophy,
                'target_audience': theme_spec.target_audience
            }
        else:
            theme_rules = {}
        
        # Create page list with dynamic names from analysis and RELATIVE paths for file structure
        page_items = []
        
        # Create a map of page types to their analysis data for quick lookup
        page_analysis_map = {}
        if 'suggested_pages' in self.analysis_results:
            for page_data in self.analysis_results['suggested_pages']:
                page_analysis_map[page_data['type']] = page_data
        
        for page_type in self.selected_pages:
            # Get dynamic navigation name from analysis results
            page_analysis = page_analysis_map.get(page_type, {})
            nav_name = page_analysis.get('nav_name', self._get_default_nav_name(page_type))
            
            if page_type == 'homepage':
                page_items.append({
                    'name': nav_name, 
                    'href_from_root': '../index.html',  # From subfolder to root
                    'href_from_subfolder': '../index.html',
                    'page_type': 'homepage'
                })
            elif page_type == 'case-studies':
                page_items.append({
                    'name': nav_name, 
                    'href_from_root': 'case-studies/index.html',  # From root to subfolder
                    'href_from_subfolder': '../case-studies/index.html',  # From subfolder to subfolder
                    'page_type': 'case-studies'
                })
            else:
                page_items.append({
                    'name': nav_name,
                    'href_from_root': f'{page_type}/index.html',  # From root to subfolder
                    'href_from_subfolder': f'../{page_type}/index.html',  # From subfolder to subfolder
                    'page_type': page_type
                })
        
        prompt = f"""Generate a responsive navigation HTML component for a multi-page website.

Product/Website: {self.product_description}
Site Name: {self.site_name}
Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

File Structure:
- Homepage: index.html (root directory)
- Other pages: [page-name]/index.html (subfolders)

Navigation Requirements:
1. Generate ONLY the navigation HTML (header/nav element)
2. Use semantic HTML with proper accessibility
3. Make it fully responsive (mobile-first)
4. Include a mobile hamburger menu
5. Use TailwindCSS classes matching the theme
6. Include proper aria labels and navigation structure
7. Style should match the theme's visual characteristics
8. Use JavaScript to dynamically set correct paths based on current location
9. Add active state styling for current page
10. Include site logo/name as specified
11. CRITICAL: Add data-page attribute to ALL navigation links consistently

Pages to include in navigation:
{json.dumps(page_items, indent=2)}

IMPORTANT PATH HANDLING:
- Use placeholder hrefs that will be replaced programmatically
- For homepage: use href="{{HOME_PATH}}"
- For other pages: use href="{{PAGE_PATH_[PAGE_TYPE]}}" (e.g., href="{{PAGE_PATH_FEATURES}}")
- These placeholders will be replaced with correct relative paths

CRITICAL DATA-PAGE ATTRIBUTES:
- Add data-page attribute to EVERY navigation link (both desktop and mobile)
- Use the page_type from the JSON data for data-page values
- Example: data-page="homepage" for home, data-page="features" for features, etc.
- This is REQUIRED for proper active state detection

Pages and their placeholder patterns:
- Home: href="{{HOME_PATH}}" data-page="homepage" 
- Features: href="{{PAGE_PATH_FEATURES}}" data-page="features"
- Pricing: href="{{PAGE_PATH_PRICING}}" data-page="pricing"
- About: href="{{PAGE_PATH_ABOUT}}" data-page="about"
- Contact: href="{{PAGE_PATH_CONTACT}}" data-page="contact"
- Blog: href="{{PAGE_PATH_BLOG}}" data-page="blog"
- Case Studies: href="{{PAGE_PATH_CASE_STUDIES}}" data-page="case-studies"
- Integrations: href="{{PAGE_PATH_INTEGRATIONS}}" data-page="integrations"

Return ONLY the navigation HTML component with placeholder hrefs.

Example structure (adapt to your theme):
<header class="bg-white shadow-sm">
  <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Main navigation">
    <!-- Navigation content with JavaScript path resolution -->
  </nav>
</header>"""
        
        return prompt
    
    def _clean_navigation_html(self, raw_html: str) -> str:
        """Clean and validate navigation HTML"""
        
        # Remove code blocks if present
        if '```html' in raw_html:
            start = raw_html.find('```html') + 7
            end = raw_html.find('```', start)
            raw_html = raw_html[start:end]
        elif '```' in raw_html:
            start = raw_html.find('```') + 3
            end = raw_html.rfind('```')
            raw_html = raw_html[start:end]
        
        # Extract only the navigation part if full HTML is returned
        
        # Look for header/nav elements
        nav_patterns = [
            r'<header[^>]*>.*?</header>',
            r'<nav[^>]*>.*?</nav>',
            r'<div[^>]*class=["\'][^"\']*nav[^"\']*["\'][^>]*>.*?</div>'
        ]
        
        for pattern in nav_patterns:
            match = re.search(pattern, raw_html, re.DOTALL | re.IGNORECASE)
            if match:
                nav_html = match.group(0).strip()
                break
        else:
            nav_html = raw_html.strip()
        
        # Post-process: Convert absolute paths to placeholders if Claude didn't follow instructions
        nav_html = self._convert_absolute_paths_to_placeholders(nav_html)
        
        # Validate and fix data-page attributes
        nav_html = self._ensure_consistent_data_page_attributes(nav_html)
        
        return nav_html
    
    def _convert_absolute_paths_to_placeholders(self, nav_html: str) -> str:
        """Convert absolute paths to placeholders if Claude didn't follow instructions"""
        
        # Mapping of absolute paths to placeholders
        path_conversions = [
            (r'href="/"', 'href="{{HOME_PATH}}"'),
            (r'href="/pricing/"', 'href="{{PAGE_PATH_PRICING}}"'),
            (r'href="/about/"', 'href="{{PAGE_PATH_ABOUT}}"'),
            (r'href="/contact/"', 'href="{{PAGE_PATH_CONTACT}}"'),
            (r'href="/case-studies/"', 'href="{{PAGE_PATH_CASE_STUDIES}}"'),
            (r'href="/features/"', 'href="{{PAGE_PATH_FEATURES}}"'),
            (r'href="/blog/"', 'href="{{PAGE_PATH_BLOG}}"'),
            (r'href="/integrations/"', 'href="{{PAGE_PATH_INTEGRATIONS}}"'),
        ]
        
        # Apply conversions
        for absolute_path, placeholder in path_conversions:
            nav_html = re.sub(absolute_path, placeholder, nav_html, flags=re.IGNORECASE)
        
        return nav_html
    
    def _ensure_consistent_data_page_attributes(self, nav_html: str) -> str:
        """Ensure all navigation links have consistent data-page attributes"""
        
        # Define mapping of href patterns to data-page values
        page_mappings = {
            r'href=[\'"]\{\{HOME_PATH\}\}[\'"]': 'data-page="homepage"',
            r'href=[\'"]\{\{PAGE_PATH_FEATURES\}\}[\'"]': 'data-page="features"',
            r'href=[\'"]\{\{PAGE_PATH_PRICING\}\}[\'"]': 'data-page="pricing"',
            r'href=[\'"]\{\{PAGE_PATH_ABOUT\}\}[\'"]': 'data-page="about"',
            r'href=[\'"]\{\{PAGE_PATH_CONTACT\}\}[\'"]': 'data-page="contact"',
            r'href=[\'"]\{\{PAGE_PATH_BLOG\}\}[\'"]': 'data-page="blog"',
            r'href=[\'"]\{\{PAGE_PATH_CASE_STUDIES\}\}[\'"]': 'data-page="case-studies"',
            r'href=[\'"]\{\{PAGE_PATH_INTEGRATIONS\}\}[\'"]': 'data-page="integrations"'
        }
        
        # Add missing data-page attributes
        for href_pattern, data_page in page_mappings.items():
            # Find all matching anchor tags
            import re
            pattern = r'(<a[^>]*' + href_pattern + r'[^>]*)((?!data-page)[^>]*)>'
            def add_data_page(match):
                opening_tag = match.group(1)
                rest_of_tag = match.group(2)
                # Check if data-page already exists
                if 'data-page=' in opening_tag + rest_of_tag:
                    return match.group(0)  # Already has data-page
                else:
                    return f'{opening_tag} {data_page}{rest_of_tag}>'
            
            nav_html = re.sub(pattern, add_data_page, nav_html, flags=re.IGNORECASE)
        
        return nav_html
    
    def _create_page_prompt_without_navigation(self, page_type: str, description: str) -> str:
        """Create generation prompt for a page WITHOUT navigation"""
        
        # Get theme specifications
        theme_spec = THEME_SPECIFICATIONS.get(self.theme)
        if theme_spec:
            theme_rules = {
                'visual_characteristics': theme_spec.visual_characteristics,
                'design_philosophy': theme_spec.design_philosophy,
                'target_audience': theme_spec.target_audience
            }
        else:
            theme_rules = {}
        
        if page_type == 'homepage':
            prompt = f"""Generate a conversion-optimized homepage content for this product:

{description}

Create the HTML content for the homepage (EXCLUDING navigation):
- Start directly with main content (no nav/header)
- Hero section with compelling headline and CTA
- Key features overview
- Social proof/testimonials if mentioned
- Clear value proposition
- Call-to-action sections
- Include a placeholder comment: <!-- NAVIGATION_PLACEHOLDER -->

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

IMPORTANT: 
- Do NOT include navigation/header in your response
- Start with the main content area
- Navigation will be injected later
- Return complete HTML with proper structure but no nav

Return only the HTML code starting from main content."""

        elif page_type == 'features':
            prompt = f"""Generate a detailed features page content for this product:

{description}

Create the HTML content for features page (EXCLUDING navigation):
- Start directly with main content (no nav/header)
- Comprehensive feature breakdown
- Detailed explanations of capabilities
- Feature comparisons or tiers
- Visual elements and icons
- Integration information if mentioned
- Include a placeholder comment: <!-- NAVIGATION_PLACEHOLDER -->

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

IMPORTANT: 
- Do NOT include navigation/header in your response
- Start with the main content area
- Navigation will be injected later
- Return complete HTML with proper structure but no nav

Return only the HTML code starting from main content."""

        elif page_type == 'pricing':
            prompt = f"""Generate a pricing page content for this product:

{description}

Create the HTML content for pricing page (EXCLUDING navigation):
- Start directly with main content (no nav/header)
- Clear pricing tiers/plans
- Feature comparison between plans
- FAQ about pricing
- Call-to-action for each plan
- Money-back guarantee if appropriate
- Include a placeholder comment: <!-- NAVIGATION_PLACEHOLDER -->

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

IMPORTANT: 
- Do NOT include navigation/header in your response
- Start with the main content area
- Navigation will be injected later
- Return complete HTML with proper structure but no nav

Return only the HTML code starting from main content."""

        elif page_type == 'about':
            prompt = f"""Generate an about page content for this company/product:

{description}

Create the HTML content for about page (EXCLUDING navigation):
- Start directly with main content (no nav/header)
- Company story and mission
- Team information if mentioned
- Company values and vision
- History and milestones
- Contact information integration
- Include a placeholder comment: <!-- NAVIGATION_PLACEHOLDER -->

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

IMPORTANT: 
- Do NOT include navigation/header in your response
- Start with the main content area
- Navigation will be injected later
- Return complete HTML with proper structure but no nav

Return only the HTML code starting from main content."""

        elif page_type == 'contact':
            prompt = f"""Generate a contact page content for this company/product:

{description}

Create the HTML content for contact page (EXCLUDING navigation):
- Start directly with main content (no nav/header)
- Contact form
- Contact information (email, phone if available)
- Office address if mentioned
- Support options
- FAQ section if appropriate
- Include a placeholder comment: <!-- NAVIGATION_PLACEHOLDER -->

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

IMPORTANT: 
- Do NOT include navigation/header in your response
- Start with the main content area
- Navigation will be injected later
- Return complete HTML with proper structure but no nav

Return only the HTML code starting from main content."""

        else:
            # Generic prompt for other page types
            prompt = f"""Generate {page_type.replace('-', ' ')} page content for this product:

{description}

Create the HTML content for {page_type.replace('-', ' ')} page (EXCLUDING navigation):
- Start directly with main content (no nav/header)
- Focus on {page_type.replace('-', ' ')} information
- Include a placeholder comment: <!-- NAVIGATION_PLACEHOLDER -->

Theme: {self.theme}
Theme Rules: {json.dumps(theme_rules, indent=2)}

IMPORTANT: 
- Do NOT include navigation/header in your response
- Start with the main content area
- Navigation will be injected later
- Return complete HTML with proper structure but no nav

Return only the HTML code starting from main content."""
        
        return prompt
    
    def _inject_navigation_into_pages(self, successful_pages: List[str]) -> Dict[str, Any]:
        """Inject pre-generated navigation into all pages with correct paths"""
        
        injection_results = {
            'injected_pages': [],
            'failed_pages': [],
            'navigation_html': self.navigation_html
        }
        
        for page_type in successful_pages:
            try:
                # Get the page file path
                page_path = self._get_page_output_path(page_type)
                
                # Read the current page content
                with open(page_path, 'r', encoding='utf-8') as f:
                    page_content = f.read()
                
                # Generate navigation with correct paths for this page location
                page_specific_nav = self._adapt_navigation_for_page(page_type)
                
                # Inject navigation
                updated_content = self._inject_navigation_into_html(page_content, page_type, page_specific_nav)
                
                # Write back the updated content
                with open(page_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                injection_results['injected_pages'].append(page_type)
                
            except Exception as e:
                self.console.print(f"[red]❌ Failed to inject navigation into {page_type}: {e}[/red]")
                injection_results['failed_pages'].append(page_type)
        
        self.console.print(f"[green]✅ Navigation injected into {len(injection_results['injected_pages'])} pages[/green]")
        
        return injection_results
    
    def _adapt_navigation_for_page(self, current_page_type: str) -> str:
        """Adapt navigation HTML with correct relative paths based on current page location"""
        
        nav_html = self.navigation_html
        
        # Replace placeholders with correct relative paths based on current page location
        
        # Homepage placeholder
        if current_page_type == 'homepage':
            # From homepage to homepage: ./index.html
            home_href = './index.html'
        else:
            # From subpage to homepage: ../index.html
            home_href = '../index.html'
        
        # Replace both single and double brace formats
        nav_html = nav_html.replace('{{HOME_PATH}}', home_href)
        nav_html = nav_html.replace('{HOME_PATH}', home_href)
        
        # Other page placeholders
        for page_type in self.selected_pages:
            if page_type == 'homepage':
                continue  # Already handled above
                
            # Create placeholder name (uppercase and replace hyphens)
            placeholder_name = page_type.replace('-', '_').upper()
            
            # Create correct relative path based on current page location
            if current_page_type == 'homepage':
                # From homepage to subpage: ./features/index.html
                correct_href = f'./{page_type}/index.html'
            elif current_page_type == page_type:
                # From page to itself: ./index.html
                correct_href = './index.html'
            else:
                # From one subpage to another: ../pricing/index.html
                correct_href = f'../{page_type}/index.html'
            
            # Replace both single and double brace formats
            double_brace_placeholder = f'{{{{PAGE_PATH_{placeholder_name}}}}}'
            single_brace_placeholder = f'{{PAGE_PATH_{placeholder_name}}}'
            
            nav_html = nav_html.replace(double_brace_placeholder, correct_href)
            nav_html = nav_html.replace(single_brace_placeholder, correct_href)
        
        return nav_html
    
    def _inject_navigation_into_html(self, page_content: str, page_type: str, navigation_html: str = None) -> str:
        """Inject navigation HTML into a page's content"""
        
        # Create the complete HTML structure with navigation
        
        # Extract doctype and html opening if present
        doctype = "<!DOCTYPE html>"
        html_start = '<html lang="en">'
        
        # Look for existing structure
        
        # Remove existing doctype and html tags if present to avoid duplication
        page_content = re.sub(r'<!DOCTYPE[^>]*>', '', page_content, flags=re.IGNORECASE)
        page_content = re.sub(r'<html[^>]*>', '', page_content, flags=re.IGNORECASE)
        page_content = re.sub(r'</html>', '', page_content, flags=re.IGNORECASE)
        
        # Remove head section if present (we'll add our own)
        page_content = re.sub(r'<head>.*?</head>', '', page_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove body tags if present (content should be body content)
        page_content = re.sub(r'<body[^>]*>', '', page_content, flags=re.IGNORECASE)
        page_content = re.sub(r'</body>', '', page_content, flags=re.IGNORECASE)
        
        # Clean up the page content
        page_content = page_content.strip()
        
        # Replace navigation placeholder if it exists
        if '<!-- NAVIGATION_PLACEHOLDER -->' in page_content:
            page_content = page_content.replace('<!-- NAVIGATION_PLACEHOLDER -->', '')
        
        # Use provided navigation HTML or fallback to stored one
        nav_to_inject = navigation_html if navigation_html is not None else self.navigation_html
        
        # Create complete HTML with navigation
        full_html = f"""{doctype}
{html_start}
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_type.replace('-', ' ').title()} - {self.site_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    // Theme-specific customizations can be added here
                }}
            }}
        }}
    </script>
</head>
<body class="bg-gray-50 text-gray-900">
    {nav_to_inject}
    
    {page_content}
    
    <!-- Active state navigation script (handled by navigation builder) -->
</body>
</html>"""
        
        return full_html
    
    def _get_default_nav_name(self, page_type: str) -> str:
        """Get default navigation name for a page type"""
        default_names = {
            'homepage': 'Home',
            'features': 'Features',
            'pricing': 'Pricing',
            'about': 'About',
            'contact': 'Contact',
            'blog': 'Blog',
            'case-studies': 'Case Studies',
            'integrations': 'Integrations'
        }
        return default_names.get(page_type, page_type.replace('-', ' ').title())
    
    def _save_generation_metadata(self, successful_pages: List[str], 
                                injection_results: Dict, sitemap_results: Dict) -> None:
        """Save metadata about the generation process"""
        
        metadata = {
            'generation_type': 'multipage',
            'product_description': self.product_description,
            'theme': self.theme,
            'base_url': self.base_url,
            'site_name': self.site_name,
            'generated_pages': successful_pages,
            'total_pages': len(successful_pages),
            'generation_time': time.time(),
            'analysis_results': self.analysis_results,
            'injection_results': injection_results,
            'sitemap_results': sitemap_results,
            'generation_summary': self.generator.get_generation_summary()
        }
        
        # Save to multipage_analysis.json
        metadata_path = os.path.join(self.output_dir, 'multipage_analysis.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def _create_final_summary(self) -> Dict[str, Any]:
        """Create final generation summary"""
        
        successful_pages = [page for page, result in self.generation_results.items() if result.success]
        failed_pages = [page for page, result in self.generation_results.items() if not result.success]
        
        generation_summary = self.generator.get_generation_summary()
        
        # Aggregate costs from all phases
        page_gen_stats = generation_summary.get('usage_stats', {})
        self.total_usage_stats['page_generation_cost'] = page_gen_stats.get('cost', 0.0)
        self.total_usage_stats['total_input_tokens'] += page_gen_stats.get('input_tokens', 0)
        self.total_usage_stats['total_output_tokens'] += page_gen_stats.get('output_tokens', 0)
        
        # Calculate total cost
        self.total_usage_stats['total_cost'] = (
            self.total_usage_stats['analysis_cost'] + 
            self.total_usage_stats['navigation_cost'] + 
            self.total_usage_stats['page_generation_cost']
        )
        
        return {
            'success': len(successful_pages) > 0,
            'total_pages_requested': len(self.selected_pages),
            'pages_generated': len(successful_pages),
            'pages_failed': len(failed_pages),
            'successful_pages': successful_pages,
            'failed_pages': failed_pages,
            'output_directory': self.output_dir,
            'site_name': self.site_name,
            'theme': self.theme,
            'base_url': self.base_url,
            'generation_time': generation_summary.get('total_time', 0),
            'usage_stats': {
                'input_tokens': self.total_usage_stats['total_input_tokens'],
                'output_tokens': self.total_usage_stats['total_output_tokens'],
                'cost': self.total_usage_stats['total_cost'],
                'breakdown': {
                    'analysis_cost': self.total_usage_stats['analysis_cost'],
                    'navigation_cost': self.total_usage_stats['navigation_cost'],
                    'page_generation_cost': self.total_usage_stats['page_generation_cost']
                }
            },
            'files_created': self._get_created_files()
        }
    
    def _get_created_files(self) -> List[str]:
        """Get list of files created during generation"""
        
        files = []
        output_path = Path(self.output_dir)
        
        if output_path.exists():
            for file_path in output_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(output_path)
                    files.append(str(relative_path))
        
        return sorted(files)
    
    def _display_final_results(self, results: Dict[str, Any]) -> None:
        """Display final generation results"""
        
        # Create summary text
        if results['success']:
            summary_text = f"""✅ Successfully generated {results['pages_generated']}/{results['total_pages_requested']} pages

📁 Output Directory: {results['output_directory']}
🎨 Theme: {results['theme']}
⏱️  Total Time: {results['generation_time']:.1f}s

📄 Generated Pages:"""
            
            for page in results['successful_pages']:
                summary_text += f"\n  • {page.replace('-', ' ').title()}"
            
            if results['failed_pages']:
                summary_text += f"\n\n⚠️  Failed Pages: {', '.join(results['failed_pages'])}"
            
            summary_text += f"\n\n🔗 Files Created: {len(results['files_created'])}"
            summary_text += "\n  • HTML pages with navigation"
            summary_text += "\n  • sitemap.xml for SEO"
            summary_text += "\n  • robots.txt"
            summary_text += "\n  • sitemap.html (user-friendly)"
            
            # Usage stats if available
            if results['usage_stats'].get('input_tokens', 0) > 0:
                summary_text += f"\n\n📊 Usage Stats:"
                summary_text += f"\n  • Input tokens: {results['usage_stats']['input_tokens']:,}"
                summary_text += f"\n  • Output tokens: {results['usage_stats']['output_tokens']:,}"
                summary_text += f"\n  • Estimated cost: ${results['usage_stats']['cost']:.3f}"
            
        else:
            summary_text = f"❌ Generation failed\n\nSome pages may have been created in: {results['output_directory']}"
        
        # Display in a panel
        panel = Panel(
            Align.left(summary_text),
            title="[bold green]🌐 Multi-Page Website Generated[/bold green]" if results['success'] else "[bold red]❌ Generation Failed[/bold red]",
            border_style="green" if results['success'] else "red",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        # Show next steps
        if results['success']:
            self.console.print(f"\n[bold blue]🚀 Next Steps:[/bold blue]")
            self.console.print(f"1. Open [cyan]{results['output_directory']}/index.html[/cyan] in your browser")
            self.console.print(f"2. Customize the content and styling as needed")
            self.console.print(f"3. Update the base URL in sitemap.xml for your domain")
            self.console.print(f"4. Upload to your web host")
            self.console.print(f"5. Submit sitemap.xml to Google Search Console")


def run_multipage_generation(description: str, output_dir: Optional[str] = None,
                           theme: str = "minimal", base_url: str = "https://example.com",
                           interactive: bool = True) -> Dict[str, Any]:
    """Main entry point for multi-page generation"""
    
    generator = MultipageGenerator()
    return generator.generate_multipage_website(description, output_dir, theme, base_url, interactive)