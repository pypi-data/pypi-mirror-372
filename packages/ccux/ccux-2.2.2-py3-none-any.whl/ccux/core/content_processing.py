"""
Content Processing Module

Provides HTML validation and content processing utilities.
Handles parsing Claude output, stripping code blocks, and safe JSON parsing.
"""

import json
import re
from typing import Dict, Any, List
from rich.console import Console


def safe_json_parse(text: str) -> Dict[str, Any]:
    """Safely parse JSON from Claude output with fallback"""
    try:
        # Try direct JSON parse first
        return json.loads(text.strip())
    except:
        # Try to extract JSON from code blocks
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except:
                pass
        
        # Try to find JSON-like content
        json_pattern = r'\{.*\}'
        json_match = re.search(json_pattern, text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        # Fallback to empty dict
        console = Console()
        console.print(f"[yellow]⚠️  Could not parse JSON from Claude output[/yellow]")
        return {}


def strip_code_blocks(text: str) -> str:
    """Remove code block markers from Claude output"""
    # Remove ```html and ``` markers
    text = re.sub(r'^```html\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'```$', '', text)
    return text.strip()


def extract_html_content(claude_output: str) -> str:
    """Extract HTML content from Claude's response"""
    # First try to find HTML in code blocks
    html_match = re.search(r'```html\s*\n?(.*?)\n?```', claude_output, re.DOTALL)
    if html_match:
        return html_match.group(1).strip()
    
    # If no code blocks, try to find HTML tags
    if '<html' in claude_output.lower() or '<!doctype' in claude_output.lower():
        return claude_output.strip()
    
    # Return as-is if no clear HTML structure
    return claude_output.strip()


def validate_html_structure(html_content: str) -> bool:
    """Basic validation of HTML structure"""
    required_tags = ['<html', '<head', '<body']
    return all(tag in html_content.lower() for tag in required_tags)


def extract_title_from_html(html_content: str) -> str:
    """Extract title from HTML content"""
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    if title_match:
        return title_match.group(1).strip()
    return ""


def extract_description_from_html(html_content: str) -> str:
    """Extract meta description from HTML content"""
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', 
                          html_content, re.IGNORECASE)
    if desc_match:
        return desc_match.group(1).strip()
    return ""


def clean_html_content(html_content: str) -> str:
    """Clean and normalize HTML content"""
    # Remove excessive whitespace
    html_content = re.sub(r'\n\s*\n', '\n', html_content)
    html_content = re.sub(r'[ \t]+', ' ', html_content)
    
    # Ensure proper line endings
    html_content = html_content.replace('\r\n', '\n').replace('\r', '\n')
    
    return html_content.strip()


def extract_sections_from_html(html_content: str) -> Dict[str, str]:
    """Extract sections marked with HTML comments from content"""
    sections = {}
    
    # Find all section markers
    pattern = r'<!-- START: (\w+) -->(.*?)<!-- END: \1 -->'
    matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for section_name, section_content in matches:
        sections[section_name.lower()] = section_content.strip()
    
    return sections


def replace_section_in_html(html_content: str, section_name: str, new_section_content: str) -> str:
    """Replace a specific section in HTML content"""
    pattern = f'<!-- START: {section_name} -->.*?<!-- END: {section_name} -->'
    replacement = f'<!-- START: {section_name} -->\n{new_section_content}\n<!-- END: {section_name} -->'
    
    return re.sub(pattern, replacement, html_content, flags=re.DOTALL | re.IGNORECASE)


def validate_section_markers(html_content: str) -> List[str]:
    """Validate and return list of available section markers"""
    pattern = r'<!-- START: (\w+) -->'
    matches = re.findall(pattern, html_content, re.IGNORECASE)
    return [match.lower() for match in matches]


def minify_html(html_content: str) -> str:
    """Basic HTML minification"""
    # Remove comments (except section markers)
    html_content = re.sub(r'<!--(?! START:|END:).*?-->', '', html_content, flags=re.DOTALL)
    
    # Remove extra whitespace between tags
    html_content = re.sub(r'>\s+<', '><', html_content)
    
    # Remove leading/trailing whitespace from lines
    lines = [line.strip() for line in html_content.split('\n')]
    html_content = '\n'.join(line for line in lines if line)
    
    return html_content