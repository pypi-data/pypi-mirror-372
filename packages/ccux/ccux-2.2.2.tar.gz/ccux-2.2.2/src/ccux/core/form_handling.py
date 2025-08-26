"""
Form Handling Module

Provides interactive form generation and management utilities.
Handles different form types, styles, and customization options.
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table

from .content_processing import extract_sections_from_html
from .claude_integration import run_claude_with_progress
from ..theme_specifications import detect_theme_from_content
from ..prompt_templates import form_on_prompt, form_off_prompt, form_edit_prompt


FORM_TYPES = {
    'contact': {
        'name': 'Contact Form',
        'description': 'General contact form with name, email, message',
        'default_fields': ['name', 'email', 'message']
    },
    'newsletter': {
        'name': 'Newsletter Signup',
        'description': 'Simple email signup form',
        'default_fields': ['email']
    },
    'signup': {
        'name': 'User Registration',
        'description': 'Registration form with multiple user fields',
        'default_fields': ['name', 'email', 'phone']
    },
    'custom': {
        'name': 'Custom Form',
        'description': 'Custom field configuration',
        'default_fields': []
    }
}

FORM_STYLES = {
    'inline': 'Embedded directly in page sections',
    'modal': 'Popup modal overlay with click trigger',
    'sidebar': 'Fixed position sidebar form',
    'fullpage': 'Dedicated full-width form section'
}

AVAILABLE_FIELDS = [
    'name', 'email', 'phone', 'message', 'company', 'website', 'subject'
]


def add_forms_to_html(product_desc: str, existing_html: str, detected_theme: str = None) -> str:
    """Add contact forms to existing HTML"""
    if not detected_theme:
        detected_theme = detect_theme_from_content(existing_html)
    
    prompt = form_on_prompt(product_desc, existing_html, detected_theme)
    result, _ = run_claude_with_progress(prompt, "Adding contact forms...")
    return result


def remove_forms_from_html(existing_html: str) -> str:
    """Remove all forms from existing HTML"""
    prompt = form_off_prompt(existing_html)
    result, _ = run_claude_with_progress(prompt, "Removing forms...")
    return result


def edit_forms_in_html(existing_html: str, form_type: str, fields: List[str], 
                      style: str = None, cta: str = None, detected_theme: str = None) -> str:
    """Edit forms in existing HTML with specified configuration"""
    if not detected_theme:
        detected_theme = detect_theme_from_content(existing_html)
    
    prompt = form_edit_prompt(existing_html, form_type, fields, style, cta, detected_theme)
    result, _ = run_claude_with_progress(prompt, f"Customizing {form_type} forms...")
    return result


def interactive_form_configuration() -> Dict[str, Any]:
    """Interactive form configuration wizard"""
    console = Console()
    
    # Form type selection
    console.print("\n[bold cyan]📋 Form Configuration[/bold cyan]")
    console.print("Choose form type:")
    
    table = Table(show_header=False)
    for i, (key, info) in enumerate(FORM_TYPES.items(), 1):
        table.add_row(f"{i}. {info['name']}", info['description'])
    
    console.print(table)
    
    choice = IntPrompt.ask("Select form type", choices=list(range(1, len(FORM_TYPES) + 1)))
    form_type = list(FORM_TYPES.keys())[choice - 1]
    
    # Field selection
    if form_type == 'custom':
        fields = []
        console.print(f"\nAvailable fields: {', '.join(AVAILABLE_FIELDS)}")
        while True:
            field = Prompt.ask("Add field (or press Enter to finish)", 
                             choices=AVAILABLE_FIELDS + [""], default="")
            if not field:
                break
            if field not in fields:
                fields.append(field)
    else:
        fields = FORM_TYPES[form_type]['default_fields'].copy()
        if Confirm.ask(f"Use default fields ({', '.join(fields)})?"):
            pass
        else:
            fields = []
            console.print(f"Available fields: {', '.join(AVAILABLE_FIELDS)}")
            while True:
                field = Prompt.ask("Add field (or press Enter to finish)", 
                                 choices=AVAILABLE_FIELDS + [""], default="")
                if not field:
                    break
                if field not in fields:
                    fields.append(field)
    
    # Style selection
    console.print("\nForm styles:")
    for i, (style, description) in enumerate(FORM_STYLES.items(), 1):
        console.print(f"{i}. {style}: {description}")
    
    style_choice = IntPrompt.ask("Select style", choices=list(range(1, len(FORM_STYLES) + 1)))
    style = list(FORM_STYLES.keys())[style_choice - 1]
    
    # CTA customization
    cta = Prompt.ask("Custom call-to-action text (optional)", default="")
    
    return {
        'type': form_type,
        'fields': fields,
        'style': style,
        'cta': cta if cta else None
    }


def validate_form_fields(fields: List[str]) -> bool:
    """Validate form field list"""
    return all(field in AVAILABLE_FIELDS for field in fields)


def get_form_type_info(form_type: str) -> Dict[str, Any]:
    """Get information about a form type"""
    return FORM_TYPES.get(form_type, {})


def list_available_form_types() -> List[str]:
    """Get list of available form types"""
    return list(FORM_TYPES.keys())


def list_available_form_styles() -> List[str]:
    """Get list of available form styles"""
    return list(FORM_STYLES.keys())


def detect_existing_forms(html_content: str) -> bool:
    """Detect if HTML content already contains forms"""
    return '<form' in html_content.lower()


def extract_form_configuration(html_content: str) -> Dict[str, Any]:
    """Extract form configuration from existing HTML"""
    config = {
        'has_forms': detect_existing_forms(html_content),
        'form_count': html_content.lower().count('<form'),
        'fields': []
    }
    
    # Extract field types from input elements
    import re
    input_pattern = r'<input[^>]*name=["\']([^"\']*)["\']'
    textarea_pattern = r'<textarea[^>]*name=["\']([^"\']*)["\']'
    
    fields = set()
    fields.update(re.findall(input_pattern, html_content, re.IGNORECASE))
    fields.update(re.findall(textarea_pattern, html_content, re.IGNORECASE))
    
    config['fields'] = list(fields)
    return config