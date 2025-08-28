"""
Sitemap Generator Module

Generates XML sitemaps for SEO optimization of multi-page websites.
Creates comprehensive sitemaps with proper metadata and indexing information.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from rich.console import Console


class SitemapGenerator:
    """Generates XML sitemaps for multi-page websites"""
    
    def __init__(self, base_url: str = "https://example.com"):
        self.console = Console()
        self.base_url = base_url.rstrip('/')
        
        # Page priority and frequency settings
        self.page_config = {
            'homepage': {
                'priority': '1.0',
                'changefreq': 'weekly',
                'importance': 'highest'
            },
            'features': {
                'priority': '0.9',
                'changefreq': 'monthly',
                'importance': 'high'
            },
            'pricing': {
                'priority': '0.9',
                'changefreq': 'monthly',
                'importance': 'high'
            },
            'about': {
                'priority': '0.7',
                'changefreq': 'yearly',
                'importance': 'medium'
            },
            'contact': {
                'priority': '0.8',
                'changefreq': 'yearly',
                'importance': 'medium'
            },
            'blog': {
                'priority': '0.8',
                'changefreq': 'weekly',
                'importance': 'high'
            },
            'case-studies': {
                'priority': '0.6',
                'changefreq': 'monthly',
                'importance': 'medium'
            },
            'integrations': {
                'priority': '0.7',
                'changefreq': 'monthly',
                'importance': 'medium'
            }
        }
    
    def generate_sitemap(self, successful_pages: List[str], output_dir: str,
                        base_url: Optional[str] = None) -> Dict[str, Any]:
        """Generate XML sitemap for all successful pages"""
        
        if base_url:
            self.base_url = base_url.rstrip('/')
        
        self.console.print(f"[cyan]🗺️  Generating sitemap for {len(successful_pages)} pages...[/cyan]")
        
        try:
            # Create XML sitemap
            sitemap_content = self._create_xml_sitemap(successful_pages)
            
            # Save sitemap file
            sitemap_path = Path(output_dir) / 'sitemap.xml'
            with open(sitemap_path, 'w', encoding='utf-8') as f:
                f.write(sitemap_content)
            
            # Generate robots.txt
            robots_content = self._create_robots_txt()
            robots_path = Path(output_dir) / 'robots.txt'
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(robots_content)
            
            # Create sitemap index if needed (for future expansion)
            sitemap_index_content = self._create_sitemap_index()
            sitemap_index_path = Path(output_dir) / 'sitemap_index.xml'
            with open(sitemap_index_path, 'w', encoding='utf-8') as f:
                f.write(sitemap_index_content)
            
            self.console.print(f"[green]✅ Generated sitemap with {len(successful_pages)} URLs[/green]")
            
            return {
                'success': True,
                'sitemap_path': str(sitemap_path),
                'robots_path': str(robots_path),
                'sitemap_index_path': str(sitemap_index_path),
                'total_urls': len(successful_pages),
                'base_url': self.base_url
            }
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to generate sitemap: {e}[/red]")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_xml_sitemap(self, pages: List[str]) -> str:
        """Create XML sitemap content"""
        
        # Create root element
        root = ET.Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation', 
                'http://www.sitemaps.org/schemas/sitemap/0.9 '
                'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')
        
        # Add each page as URL element
        for page_type in pages:
            url_element = self._create_url_element(page_type)
            root.append(url_element)
        
        # Convert to XML string with proper formatting
        xml_string = ET.tostring(root, encoding='unicode', method='xml')
        
        # Add XML declaration and format nicely
        formatted_xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n'
        formatted_xml += self._format_xml(xml_string)
        
        return formatted_xml
    
    def _create_url_element(self, page_type: str) -> ET.Element:
        """Create a URL element for a page"""
        
        url_element = ET.Element('url')
        
        # Location (URL)
        loc = ET.SubElement(url_element, 'loc')
        page_url = self._get_page_url(page_type)
        loc.text = page_url
        
        # Last modified date
        lastmod = ET.SubElement(url_element, 'lastmod')
        lastmod.text = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Change frequency
        changefreq = ET.SubElement(url_element, 'changefreq')
        page_config = self.page_config.get(page_type, {'changefreq': 'monthly'})
        changefreq.text = page_config['changefreq']
        
        # Priority
        priority = ET.SubElement(url_element, 'priority')
        priority.text = page_config.get('priority', '0.5')
        
        return url_element
    
    def _get_page_url(self, page_type: str) -> str:
        """Get the full URL for a page type"""
        
        if page_type == 'homepage':
            return self.base_url + '/'
        else:
            return self.base_url + f'/{page_type}/'
    
    def _format_xml(self, xml_string: str) -> str:
        """Format XML string with proper indentation"""
        
        # Basic formatting - add newlines and indentation
        formatted_lines = []
        indent_level = 0
        
        # Split by tags and format
        import re
        
        # Simple formatting - this could be enhanced with a proper XML formatter
        lines = xml_string.split('>')
        
        for line in lines:
            if line.strip():
                if line.strip().startswith('</'):
                    indent_level -= 1
                
                formatted_line = '  ' * indent_level + line.strip() + '>'
                formatted_lines.append(formatted_line)
                
                if not line.strip().startswith('</') and not line.strip().endswith('/>'):
                    if '</' not in line:
                        indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def _create_robots_txt(self) -> str:
        """Create robots.txt content"""
        
        robots_content = f"""# Robots.txt generated by CCUX
# Allow all web crawlers access to all content

User-agent: *
Allow: /

# Sitemap location
Sitemap: {self.base_url}/sitemap.xml
Sitemap: {self.base_url}/sitemap_index.xml

# Common crawl delays (optional)
# Crawl-delay: 1

# Disallow common non-content directories (if they exist)
Disallow: /admin/
Disallow: /private/
Disallow: /*.pdf$
Disallow: /search?
Disallow: /*?print=1
Disallow: /*?share=1

# Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        return robots_content
    
    def _create_sitemap_index(self) -> str:
        """Create sitemap index for future expansion"""
        
        # Create root element for sitemap index
        root = ET.Element('sitemapindex')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Add main sitemap
        sitemap_element = ET.SubElement(root, 'sitemap')
        
        loc = ET.SubElement(sitemap_element, 'loc')
        loc.text = f"{self.base_url}/sitemap.xml"
        
        lastmod = ET.SubElement(sitemap_element, 'lastmod')
        lastmod.text = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Convert to XML string
        xml_string = ET.tostring(root, encoding='unicode', method='xml')
        
        # Add XML declaration
        formatted_xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n'
        formatted_xml += self._format_xml(xml_string)
        
        return formatted_xml
    
    def validate_sitemap(self, sitemap_path: str) -> Dict[str, Any]:
        """Validate generated sitemap"""
        
        validation_results = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'url_count': 0,
            'file_size': 0
        }
        
        try:
            sitemap_file = Path(sitemap_path)
            
            if not sitemap_file.exists():
                validation_results['errors'].append('Sitemap file does not exist')
                return validation_results
            
            # Check file size
            file_size = sitemap_file.stat().st_size
            validation_results['file_size'] = file_size
            
            # Sitemap should be under 50MB (uncompressed)
            if file_size > 50 * 1024 * 1024:
                validation_results['errors'].append('Sitemap file exceeds 50MB limit')
            
            # Parse XML to validate structure
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                root = ET.fromstring(content)
                
                # Check if it's a valid sitemap
                if root.tag != '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset':
                    validation_results['errors'].append('Invalid sitemap root element')
                else:
                    # Count URLs
                    urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                    validation_results['url_count'] = len(urls)
                    
                    # Check URL count (max 50,000 for standard sitemap)
                    if len(urls) > 50000:
                        validation_results['errors'].append('Sitemap contains more than 50,000 URLs')
                    
                    # Validate each URL
                    for url in urls:
                        loc_element = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        if loc_element is not None:
                            url_value = loc_element.text
                            if not url_value or not url_value.startswith(('http://', 'https://')):
                                validation_results['warnings'].append(f'Invalid URL format: {url_value}')
            
            except ET.ParseError as e:
                validation_results['errors'].append(f'XML parsing error: {e}')
            
            # If no errors, mark as valid
            if not validation_results['errors']:
                validation_results['valid'] = True
            
        except Exception as e:
            validation_results['errors'].append(f'Validation error: {e}')
        
        return validation_results
    
    def create_html_sitemap(self, successful_pages: List[str], output_dir: str,
                          site_name: str = "Website") -> str:
        """Create an HTML sitemap page for users"""
        
        html_sitemap = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sitemap - {site_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #2563eb;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }}
        .sitemap-list {{
            list-style: none;
            padding: 0;
        }}
        .sitemap-list li {{
            margin: 1rem 0;
            padding: 1rem;
            background: #f9fafb;
            border-left: 4px solid #2563eb;
            border-radius: 0 4px 4px 0;
        }}
        .sitemap-list a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
            font-size: 1.1rem;
        }}
        .sitemap-list a:hover {{
            text-decoration: underline;
        }}
        .page-description {{
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}
        .stats {{
            background: #eff6ff;
            padding: 1rem;
            border-radius: 8px;
            margin: 2rem 0;
        }}
        .stats h2 {{
            margin-top: 0;
            color: #1e40af;
        }}
    </style>
</head>
<body>
    <h1>Sitemap - {site_name}</h1>
    
    <div class="stats">
        <h2>Site Statistics</h2>
        <p>This website contains <strong>{len(successful_pages)}</strong> pages, all optimized for search engines and accessibility.</p>
        <p>Last updated: {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    
    <h2>Pages</h2>
    <ul class="sitemap-list">
"""
        
        # Add each page to the HTML sitemap
        for page_type in successful_pages:
            page_name = self._get_page_display_name(page_type)
            page_url = self._get_page_url(page_type)
            page_description = self._get_page_description(page_type)
            
            html_sitemap += f"""
        <li>
            <a href="{page_url}">{page_name}</a>
            <div class="page-description">{page_description}</div>
        </li>"""
        
        html_sitemap += """
    </ul>
    
    <footer style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280;">
        <p>This sitemap was automatically generated by CCUX - Claude Code UI Generator</p>
        <p><a href="/sitemap.xml">XML Sitemap</a> | <a href="/robots.txt">Robots.txt</a></p>
    </footer>
</body>
</html>"""
        
        # Save HTML sitemap
        html_sitemap_path = Path(output_dir) / 'sitemap.html'
        with open(html_sitemap_path, 'w', encoding='utf-8') as f:
            f.write(html_sitemap)
        
        return str(html_sitemap_path)
    
    def _get_page_display_name(self, page_type: str) -> str:
        """Get display name for a page type"""
        name_map = {
            'homepage': 'Home',
            'features': 'Features',
            'pricing': 'Pricing',
            'about': 'About Us',
            'contact': 'Contact',
            'blog': 'Blog',
            'case-studies': 'Case Studies',
            'integrations': 'Integrations'
        }
        return name_map.get(page_type, page_type.replace('-', ' ').title())
    
    def _get_page_description(self, page_type: str) -> str:
        """Get description for a page type"""
        descriptions = {
            'homepage': 'Main landing page with overview and key information',
            'features': 'Detailed product features and capabilities',
            'pricing': 'Pricing plans and subscription options',
            'about': 'Company information and team details',
            'contact': 'Contact information and support options',
            'blog': 'Latest news, insights, and updates',
            'case-studies': 'Customer success stories and testimonials',
            'integrations': 'Available integrations and API documentation'
        }
        return descriptions.get(page_type, f'Information about {page_type.replace("-", " ")}')
    
    def get_seo_recommendations(self, pages: List[str]) -> List[str]:
        """Get SEO recommendations based on generated pages"""
        
        recommendations = []
        
        # Check for important pages
        if 'contact' not in pages:
            recommendations.append('Consider adding a Contact page for better local SEO')
        
        if 'about' not in pages:
            recommendations.append('An About page helps with trust and authority')
        
        if 'blog' not in pages:
            recommendations.append('A Blog page can improve content marketing and SEO')
        
        if len(pages) < 3:
            recommendations.append('Consider adding more pages to improve site authority')
        
        # SEO best practices
        recommendations.extend([
            'Submit your sitemap to Google Search Console',
            'Set up Google Analytics for traffic monitoring',
            'Consider adding schema markup for rich snippets',
            'Optimize page loading speeds for better rankings',
            'Add meta descriptions to all pages',
            'Include alt text for all images',
            'Set up proper redirect handling (301 redirects)',
            'Consider implementing HTTPS if not already done'
        ])
        
        return recommendations