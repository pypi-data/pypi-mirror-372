"""
Section Management Module

Provides section replacement with semantic ordering utilities.
Handles identification, extraction, and replacement of HTML sections.
"""

import re
from typing import List, Dict, Any, Optional
from rich.console import Console

from .content_processing import extract_sections_from_html, replace_section_in_html


# Standard section ordering for landing pages
SECTION_ORDER = [
    'header', 'nav', 'hero', 'features', 'benefits', 'testimonials', 
    'pricing', 'cta', 'about', 'faq', 'contact', 'footer'
]


def detect_available_sections(html_content: str) -> List[str]:
    """Detect all available sections in HTML content"""
    pattern = r'<!-- START: (\w+) -->'
    matches = re.findall(pattern, html_content, re.IGNORECASE)
    return [match.lower() for match in matches]


def extract_section_content(html_content: str, section_name: str) -> Optional[str]:
    """Extract content of a specific section"""
    sections = extract_sections_from_html(html_content)
    return sections.get(section_name.lower())


def replace_sections_in_html(html_content: str, section_replacements: Dict[str, str]) -> str:
    """Replace multiple sections in HTML content"""
    result = html_content
    
    for section_name, new_content in section_replacements.items():
        result = replace_section_in_html(result, section_name, new_content)
    
    return result


def validate_section_names(section_names: List[str], available_sections: List[str]) -> List[str]:
    """Validate section names against available sections"""
    valid_sections = []
    invalid_sections = []
    
    for section in section_names:
        if section.lower() in [s.lower() for s in available_sections]:
            valid_sections.append(section.lower())
        else:
            invalid_sections.append(section)
    
    if invalid_sections:
        console = Console()
        console.print(f"[yellow]⚠️  Invalid sections ignored: {', '.join(invalid_sections)}[/yellow]")
        console.print(f"Available sections: {', '.join(available_sections)}")
    
    return valid_sections


def order_sections_semantically(sections: List[str]) -> List[str]:
    """Order sections according to semantic landing page structure"""
    ordered = []
    unordered = []
    
    # Add sections in standard order if they exist
    for standard_section in SECTION_ORDER:
        for section in sections:
            if section.lower() == standard_section:
                ordered.append(section)
                break
    
    # Add any remaining sections that don't match standard order
    for section in sections:
        if section not in ordered:
            unordered.append(section)
    
    return ordered + unordered


def get_section_dependencies(section_name: str) -> List[str]:
    """Get sections that should be regenerated together"""
    dependencies = {
        'hero': ['cta'],  # Hero changes might affect CTA
        'pricing': ['cta'],  # Pricing changes often affect CTA
        'features': ['benefits'],  # Features and benefits are often related
        'testimonials': ['cta']  # Social proof affects conversion
    }
    
    return dependencies.get(section_name.lower(), [])


def suggest_related_sections(section_name: str, available_sections: List[str]) -> List[str]:
    """Suggest related sections that might need updating"""
    suggestions = []
    dependencies = get_section_dependencies(section_name)
    
    for dep in dependencies:
        if dep in [s.lower() for s in available_sections]:
            suggestions.append(dep)
    
    return suggestions


def validate_section_structure(html_content: str) -> Dict[str, Any]:
    """Validate section structure and report issues"""
    issues = []
    sections = detect_available_sections(html_content)
    
    # Check for proper section markers
    start_markers = re.findall(r'<!-- START: (\w+) -->', html_content, re.IGNORECASE)
    end_markers = re.findall(r'<!-- END: (\w+) -->', html_content, re.IGNORECASE)
    
    # Check for mismatched markers
    for start in start_markers:
        if start.lower() not in [end.lower() for end in end_markers]:
            issues.append(f"Missing END marker for section: {start}")
    
    for end in end_markers:
        if end.lower() not in [start.lower() for start in start_markers]:
            issues.append(f"Missing START marker for section: {end}")
    
    # Check for duplicate sections
    section_counts = {}
    for section in sections:
        section_counts[section] = section_counts.get(section, 0) + 1
    
    for section, count in section_counts.items():
        if count > 1:
            issues.append(f"Duplicate section markers found: {section} ({count} times)")
    
    return {
        'valid': len(issues) == 0,
        'sections': sections,
        'issues': issues,
        'section_count': len(sections)
    }


def extract_section_metadata(html_content: str, section_name: str) -> Dict[str, Any]:
    """Extract metadata about a section"""
    section_content = extract_section_content(html_content, section_name)
    if not section_content:
        return {}
    
    metadata = {
        'name': section_name,
        'length': len(section_content),
        'has_forms': '<form' in section_content.lower(),
        'has_images': '<img' in section_content.lower(),
        'has_links': '<a' in section_content.lower()
    }
    
    # Extract headings
    headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', section_content, re.IGNORECASE | re.DOTALL)
    metadata['headings'] = [re.sub(r'<[^>]+>', '', h).strip() for h in headings]
    
    return metadata


def generate_section_summary(html_content: str) -> Dict[str, Any]:
    """Generate a summary of all sections in the HTML"""
    sections = detect_available_sections(html_content)
    ordered_sections = order_sections_semantically(sections)
    
    summary = {
        'total_sections': len(sections),
        'sections': ordered_sections,
        'structure_valid': validate_section_structure(html_content)['valid'],
        'metadata': {}
    }
    
    for section in sections:
        summary['metadata'][section] = extract_section_metadata(html_content, section)
    
    return summary