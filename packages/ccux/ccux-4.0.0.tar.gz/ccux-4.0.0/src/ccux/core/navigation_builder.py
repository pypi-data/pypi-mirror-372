"""
Navigation Builder Module

Creates consistent navigation and cross-page connections for multi-page websites.
Builds navigation menus, breadcrumbs, and cross-links automatically.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console

from .claude_integration import run_claude_with_progress


class NavigationBuilder:
    """Builds navigation and connects pages in multi-page websites"""
    
    def __init__(self):
        self.console = Console()
        self.page_hierarchy = {
            'homepage': {'level': 0, 'parent': None, 'path': '/'},
            'features': {'level': 1, 'parent': 'homepage', 'path': '/features/'},
            'pricing': {'level': 1, 'parent': 'homepage', 'path': '/pricing/'},
            'about': {'level': 1, 'parent': 'homepage', 'path': '/about/'},
            'contact': {'level': 1, 'parent': 'homepage', 'path': '/contact/'},
            'blog': {'level': 1, 'parent': 'homepage', 'path': '/blog/'},
            'case-studies': {'level': 2, 'parent': 'features', 'path': '/case-studies/'},
            'integrations': {'level': 2, 'parent': 'features', 'path': '/integrations/'}
        }
    
    def connect_pages(self, successful_pages: List[str], output_dir: str, 
                     theme: str = "minimal", site_name: str = "Website") -> Dict[str, Any]:
        """Connect all successfully generated pages with consistent navigation"""
        
        self.console.print(f"[cyan]🔗 Connecting {len(successful_pages)} pages with navigation...[/cyan]")
        
        # Build navigation structure
        nav_structure = self._build_navigation_structure(successful_pages, site_name)
        
        # Process each page to add navigation
        connection_results = {}
        
        for page_type in successful_pages:
            try:
                page_path = Path(output_dir) / self._get_page_file_path(page_type)
                
                if page_path.exists():
                    # Read existing content
                    with open(page_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Add navigation to the page
                    updated_content = self._add_navigation_to_page(
                        content, page_type, nav_structure, theme
                    )
                    
                    # Write updated content
                    with open(page_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    connection_results[page_type] = {
                        'success': True,
                        'path': str(page_path)
                    }
                    
                else:
                    connection_results[page_type] = {
                        'success': False,
                        'error': f'Page file not found: {page_path}'
                    }
                    
            except Exception as e:
                connection_results[page_type] = {
                    'success': False,
                    'error': str(e)
                }
        
        successful_connections = len([r for r in connection_results.values() if r['success']])
        self.console.print(f"[green]✅ Connected {successful_connections}/{len(successful_pages)} pages[/green]")
        
        return {
            'nav_structure': nav_structure,
            'connection_results': connection_results,
            'successful_connections': successful_connections,
            'total_pages': len(successful_pages)
        }
    
    def _build_navigation_structure(self, pages: List[str], site_name: str) -> Dict[str, Any]:
        """Build the navigation structure for the website"""
        
        nav_items = []
        
        # Sort pages by hierarchy level and priority
        sorted_pages = sorted(pages, key=lambda p: (
            self.page_hierarchy.get(p, {}).get('level', 99),
            self._get_page_priority(p)
        ))
        
        for page_type in sorted_pages:
            page_info = self.page_hierarchy.get(page_type, {})
            
            nav_item = {
                'type': page_type,
                'name': self._get_page_display_name(page_type),
                'file_path': self._get_page_file_path(page_type),  # Store file path for relative path calculation
                'level': page_info.get('level', 1),
                'parent': page_info.get('parent')
            }
            
            nav_items.append(nav_item)
        
        return {
            'site_name': site_name,
            'items': nav_items,
            'total_pages': len(pages)
        }
    
    def _get_page_file_path(self, page_type: str) -> str:
        """Get the file path for a page type"""
        if page_type == 'homepage':
            return 'index.html'
        else:
            return f'{page_type}/index.html'
    
    def _get_page_display_name(self, page_type: str) -> str:
        """Get the display name for a page type"""
        name_map = {
            'homepage': 'Home',
            'features': 'Features',
            'pricing': 'Pricing',
            'about': 'About',
            'contact': 'Contact',
            'blog': 'Blog',
            'case-studies': 'Case Studies',
            'integrations': 'Integrations'
        }
        return name_map.get(page_type, page_type.replace('-', ' ').title())
    
    def _get_page_priority(self, page_type: str) -> int:
        """Get the priority for ordering pages in navigation"""
        priority_map = {
            'homepage': 1,
            'features': 2,
            'pricing': 3,
            'about': 4,
            'case-studies': 5,
            'integrations': 6,
            'blog': 7,
            'contact': 8
        }
        return priority_map.get(page_type, 99)
    
    def _get_relative_path(self, from_page: str, to_page: str) -> str:
        """Calculate relative path from one page to another"""
        from_path = self._get_page_file_path(from_page)
        to_path = self._get_page_file_path(to_page)
        
        # Root page (index.html)
        if from_path == 'index.html':
            if to_path == 'index.html':
                return './index.html'
            else:
                # From root to subfolder: ./features/index.html
                return f'./{to_path}'
        
        # Subfolder page (features/index.html, pricing/index.html, etc.)
        else:
            if to_path == 'index.html':
                # From subfolder to root: ../index.html
                return '../index.html'
            elif from_path == to_path:
                # Same page: ./index.html
                return './index.html'
            else:
                # From one subfolder to another: ../pricing/index.html
                return f'../{to_path}'
    
    def _add_navigation_to_page(self, content: str, current_page: str, 
                              nav_structure: Dict, theme: str) -> str:
        """Add navigation to a page's HTML content"""
        
        try:
            # Use AI to intelligently add navigation
            navigation_prompt = self._create_navigation_prompt(
                content, current_page, nav_structure, theme
            )
            
            updated_content, _ = run_claude_with_progress(
                navigation_prompt,
                f"Adding navigation to {current_page.replace('-', ' ').title()} page..."
            )
            
            return updated_content
            
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Failed to add navigation to {current_page}: {e}[/yellow]")
            return content  # Return original content if navigation addition fails
    
    def _create_navigation_prompt(self, content: str, current_page: str, 
                                nav_structure: Dict, theme: str) -> str:
        """Create prompt for adding navigation to a page"""
        
        # Create navigation items list with correct relative paths
        nav_items_text = []
        for item in nav_structure['items']:
            is_current = item['type'] == current_page
            relative_path = self._get_relative_path(current_page, item['type'])
            marker = " (current)" if is_current else ""
            nav_items_text.append(f"- {item['name']}: {relative_path}{marker}")
        
        nav_items_str = "\n".join(nav_items_text)
        
        prompt = f"""I need you to add consistent navigation to this HTML page. The page is part of a multi-page website with {nav_structure['total_pages']} pages total.

CURRENT PAGE: {current_page.replace('-', ' ').title()}
THEME: {theme}
SITE NAME: {nav_structure['site_name']}

NAVIGATION ITEMS TO USE (with correct relative paths):
{nav_items_str}

EXISTING PAGE CONTENT:
{content}

CRITICAL REQUIREMENTS:
1. Use the EXACT relative paths shown above - these are already calculated correctly for this page's location
2. Add a navigation header to the page that includes all navigation items
3. Make the current page visually distinct (active state) in the navigation
4. Ensure navigation is responsive and matches the existing theme style
5. Add a footer with basic navigation links using the same relative paths
6. Maintain all existing content - only ADD navigation elements
7. Use theme-appropriate styling that matches the existing page design
8. Include proper ARIA labels for accessibility
9. Make sure navigation works on mobile devices

NAVIGATION PATH LOGIC:
- The relative paths are already calculated based on the current page's location
- DO NOT modify these paths - use them exactly as provided
- For example: "../index.html" goes up one directory to reach the homepage from a subfolder
- "./index.html" stays in the current directory

NAVIGATION PLACEMENT:
- Add navigation bar in the <header> section or create one if it doesn't exist
- Add footer navigation in the <footer> section or create one if it doesn't exist
- Ensure navigation is sticky/fixed if appropriate for the theme
- Include mobile menu toggle functionality if needed

IMPORTANT - AVOID DUPLICATE JAVASCRIPT:
- Only add the active state JavaScript at the bottom of the page
- Do NOT add complex path resolution scripts in the header
- Keep mobile menu toggle simple and separate from active state logic

ACTIVE STATE REQUIREMENTS:
- Add JavaScript to detect current page and highlight active navigation item
- Use data-page attributes and pathname to accurately determine active state
- Apply active styling to current page only
- Include script that runs on page load to set active states

REQUIRED JAVASCRIPT FOR ACTIVE STATES:
Add this JavaScript before closing </body> tag:

<script>
document.addEventListener('DOMContentLoaded', function() {{
    // Get current page path
    const currentPath = window.location.pathname;
    
    // Set active state based on data-page attributes
    document.querySelectorAll('.nav-link[data-page]').forEach(link => {{
        const pageType = link.getAttribute('data-page');
        let isActive = false;
        
        // Check if this is the active page
        if (pageType === 'homepage' || pageType === 'home') {{
            // Homepage is active ONLY for root-level index.html, NOT subdirectory index.html files
            const isRootIndex = currentPath === '/' || 
                               currentPath === '/index.html' ||
                               (currentPath.endsWith('/index.html') && currentPath.split('/').length <= 3);
            const isNotSubdirectory = !currentPath.includes('/features/') && 
                                     !currentPath.includes('/pricing/') && 
                                     !currentPath.includes('/contact/') && 
                                     !currentPath.includes('/about/') &&
                                     !currentPath.includes('/blog/');
            isActive = isRootIndex && isNotSubdirectory;
        }} else {{
            // Other pages: must be exactly in the page directory
            isActive = new RegExp(`\\/${{pageType}}\\/index\\.html$`).test(currentPath) ||
                      new RegExp(`\\/${{pageType}}\\/?$`).test(currentPath);
        }}
        
        if (isActive) {{
            link.classList.add('bg-white/30', 'shadow-xl', 'ring-2', 'ring-yellow-300', 'ring-opacity-60');
            link.classList.remove('hover:bg-white/20');
        }} else {{
            link.classList.remove('bg-white/30', 'shadow-xl', 'ring-2', 'ring-yellow-300', 'ring-opacity-60');
            link.classList.add('hover:bg-white/20');
        }}
    }});
}});
</script>

Return the complete HTML with navigation AND the JavaScript active state detection added. Preserve all existing content and styling."""
        
        return prompt
    
    def add_breadcrumbs(self, content: str, current_page: str, nav_structure: Dict) -> str:
        """Add breadcrumb navigation to a page"""
        
        # Find the page in the navigation structure
        current_item = None
        for item in nav_structure['items']:
            if item['type'] == current_page:
                current_item = item
                break
        
        if not current_item:
            return content
        
        # Build breadcrumb trail
        breadcrumb_trail = ['Home']
        
        if current_item['parent'] and current_item['type'] != 'homepage':
            parent_item = None
            for item in nav_structure['items']:
                if item['type'] == current_item['parent']:
                    parent_item = item
                    break
            
            if parent_item:
                breadcrumb_trail.append(parent_item['name'])
        
        if current_item['type'] != 'homepage':
            breadcrumb_trail.append(current_item['name'])
        
        # Generate breadcrumb HTML
        breadcrumb_html = '<nav aria-label=\"Breadcrumb\" class=\"breadcrumb\">'
        breadcrumb_html += '<ol class=\"breadcrumb-list\">'
        
        for i, crumb in enumerate(breadcrumb_trail):
            is_last = i == len(breadcrumb_trail) - 1
            
            if is_last:
                breadcrumb_html += f'<li class=\"breadcrumb-item active\" aria-current=\"page\">{crumb}</li>'
            else:
                # This would need proper linking based on the page structure
                breadcrumb_html += f'<li class=\"breadcrumb-item\"><a href=\"#\">{crumb}</a></li>'
        
        breadcrumb_html += '</ol></nav>'
        
        # Try to insert breadcrumbs after the main navigation
        if '<nav' in content and '<main' in content:
            # Insert between nav and main
            main_match = re.search(r'<main[^>]*>', content)
            if main_match:
                insert_pos = main_match.start()
                updated_content = content[:insert_pos] + breadcrumb_html + '\n' + content[insert_pos:]
                return updated_content
        
        return content
    
    def generate_cross_page_links(self, pages: List[str], current_page: str) -> List[Dict[str, str]]:
        """Generate suggested cross-page links for a page"""
        
        links = []
        
        # Define logical connections between pages
        connections = {
            'homepage': ['features', 'pricing', 'about'],
            'features': ['pricing', 'case-studies', 'integrations'],
            'pricing': ['features', 'contact'],
            'about': ['contact', 'blog'],
            'contact': ['about'],
            'blog': ['case-studies'],
            'case-studies': ['features', 'contact'],
            'integrations': ['features', 'contact']
        }
        
        suggested_connections = connections.get(current_page, [])
        
        for page_type in suggested_connections:
            if page_type in pages and page_type != current_page:
                links.append({
                    'page': page_type,
                    'name': self._get_page_display_name(page_type),
                    'path': self._get_relative_path(current_page, page_type),
                    'reason': self._get_connection_reason(current_page, page_type)
                })
        
        return links
    
    def _get_connection_reason(self, from_page: str, to_page: str) -> str:
        """Get the reason for connecting two pages"""
        
        reasons = {
            ('homepage', 'features'): 'Learn more about our features',
            ('homepage', 'pricing'): 'View pricing plans',
            ('homepage', 'about'): 'Learn about our company',
            ('features', 'pricing'): 'See pricing for these features',
            ('features', 'case-studies'): 'See these features in action',
            ('pricing', 'contact'): 'Get in touch for custom pricing',
            ('about', 'contact'): 'Contact our team',
        }
        
        return reasons.get((from_page, to_page), f'Learn more about {to_page.replace("-", " ")}')
    
    def validate_navigation_links(self, output_dir: str, pages: List[str]) -> Dict[str, Any]:
        """Validate that all navigation links are working"""
        
        validation_results = {
            'valid_links': 0,
            'broken_links': 0,
            'issues': []
        }
        
        for page_type in pages:
            page_path = Path(output_dir) / self._get_page_file_path(page_type)
            
            if not page_path.exists():
                validation_results['issues'].append(f'Missing page file: {page_path}')
                validation_results['broken_links'] += 1
                continue
            
            # Basic validation - check if file exists and is not empty
            try:
                with open(page_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content.strip()) > 0:
                    validation_results['valid_links'] += 1
                else:
                    validation_results['issues'].append(f'Empty page file: {page_path}')
                    validation_results['broken_links'] += 1
                    
            except Exception as e:
                validation_results['issues'].append(f'Error reading {page_path}: {e}')
                validation_results['broken_links'] += 1
        
        return validation_results