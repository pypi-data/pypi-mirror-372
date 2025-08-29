"""
Animation Utilities Module

Provides theme-appropriate animations and interactions for CCUX landing pages.
Handles animation addition, removal, and theme-specific customization.
"""

import re
from typing import Dict, List, Tuple
from rich.console import Console

from ..prompt_templates import get_animation_requirements


def add_theme_appropriate_animations(content: str, theme: str) -> str:
    """Add theme-appropriate animations to existing content without Claude API calls"""
    
    # Define theme-specific animation styles
    theme_animations = {
        "minimal": {
            "css": """
            @keyframes fadeInUp { 0% { opacity: 0; transform: translateY(30px); } 100% { opacity: 1; transform: translateY(0); } }
            @keyframes slideUp { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
            .animate-fadeInUp { animation: fadeInUp 0.6s ease-out forwards; }
            .animate-slideUp { animation: slideUp 0.5s ease-out forwards; }
            .animate-delay-100 { animation-delay: 0.1s; }
            .animate-delay-200 { animation-delay: 0.2s; }
            .animate-delay-300 { animation-delay: 0.3s; }
            @media (prefers-reduced-motion: reduce) {
                * { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
                [data-animate] { opacity: 1; animation: none !important; }
            }""",
            "attributes": [
                ("section", "data-animate='fadeInUp'"),
                ("h1,h2,h3", "data-animate='slideUp'"),
                (".card,.feature-item", "data-animate='fadeInUp'")
            ]
        },
        "brutalist": {
            "css": """
            @keyframes brutalistSlam { 0% { opacity: 0; transform: translateY(-20px) scale(0.9); } 100% { opacity: 1; transform: translateY(0) scale(1); } }
            @keyframes brutalistPop { 0% { transform: scale(0.95); } 100% { transform: scale(1); } }
            .animate-brutalistSlam { animation: brutalistSlam 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards; }
            .animate-brutalistPop { animation: brutalistPop 0.4s ease-out forwards; }
            .animate-delay-100 { animation-delay: 0.1s; }
            .animate-delay-200 { animation-delay: 0.2s; }
            @media (prefers-reduced-motion: reduce) {
                * { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
                [data-animate] { opacity: 1; animation: none !important; }
            }""",
            "attributes": [
                ("section", "data-animate='brutalistSlam'"),
                ("button,.cta", "data-animate='brutalistPop'"),
                ("h1,h2", "data-animate='brutalistSlam'")
            ]
        },
        "dark": {
            "css": """
            @keyframes darkFadeIn { 0% { opacity: 0; transform: translateY(20px) scale(0.98); } 100% { opacity: 1; transform: translateY(0) scale(1); } }
            @keyframes darkGlow { 0% { box-shadow: 0 0 0 rgba(255,255,255,0.1); } 100% { box-shadow: 0 4px 20px rgba(255,255,255,0.1); } }
            .animate-darkFadeIn { animation: darkFadeIn 0.8s ease-out forwards; }
            .animate-darkGlow { animation: darkGlow 0.6s ease-out forwards; }
            .animate-delay-100 { animation-delay: 0.1s; }
            .animate-delay-200 { animation-delay: 0.2s; }
            @media (prefers-reduced-motion: reduce) {
                * { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
                [data-animate] { opacity: 1; animation: none !important; }
            }""",
            "attributes": [
                ("section", "data-animate='darkFadeIn'"),
                (".card,.feature", "data-animate='darkGlow'"),
                ("h1,h2", "data-animate='darkFadeIn'")
            ]
        }
    }
    
    if theme not in theme_animations:
        theme = "minimal"  # fallback
    
    animation_config = theme_animations[theme]
    
    # Add CSS animations to existing <style> tag or create new one
    if '<style>' in content:
        content = content.replace('</style>', f"{animation_config['css']}\\n</style>")
    else:
        if '</head>' in content:
            content = content.replace('</head>', f"<style>{animation_config['css']}</style>\\n</head>")
    
    # Add animation attributes to elements
    for selector, attribute in animation_config['attributes']:
        # Simple regex to add attributes (this is a basic implementation)
        pattern = f'(<{selector}[^>]*?)(>)'
        replacement = f'\\1 {attribute}\\2'
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Add JavaScript for IntersectionObserver
    animation_js = '''
    document.addEventListener('DOMContentLoaded', function() {
        const animatedElements = document.querySelectorAll('[data-animate]');
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const animationType = element.getAttribute('data-animate');
                    element.classList.add(`animate-${animationType}`);
                    animationObserver.unobserve(element);
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(el => animationObserver.observe(el));
    });
    '''
    
    if '</body>' in content:
        content = content.replace('</body>', f"<script>{animation_js}</script>\\n</body>")
    
    return content


def remove_animations_from_content(content: str) -> str:
    """Remove all animation code from content (used by edit mode)"""
    
    # Remove animation-specific class names from class attributes
    content = re.sub(r'\\s*data-animate=[\'"][^\'"]*[\'"]', '', content)
    content = re.sub(r'\\s*class=[\'"]([^\'"]*?)\\s*animate-[^\\s\'"]*([^\'"]*)[\'"]', r' class="\\1\\2"', content)
    
    # Remove ONLY specific animation CSS (very precise patterns)
    animation_css_patterns = [
        r'@keyframes\\s+(?:fadeInUp|slideUp|slideDown|countUp|fadeInStagger|bounce|pulse|darkFadeIn|darkGlow|brutalistSlam|brutalistPop)\\s*\\{[^}]+\\}',  # Only animation keyframes
        r'\\.animate-(?:fadeInUp|slideUp|slideDown|countUp|fadeInStagger|bounce|pulse|darkFadeIn|darkGlow|brutalistSlam|brutalistPop)\\s*\\{[^}]+\\}',  # Only .animate-* for animations  
        r'\\.(?:fadeInUp|slideUp|slideDown|countUp|fadeInStagger|bounce|pulse|darkFadeIn|darkGlow|brutalistSlam|brutalistPop)\\s*\\{[^}]+\\}',  # Direct animation classes
        r'@media\\s*\\(prefers-reduced-motion:\\s*reduce\\)\\s*\\{[^}]*animation[^}]*\\}',  # Reduced motion media queries
    ]
    
    for pattern in animation_css_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove animation-specific JavaScript
    js_patterns = [
        r'const\\s+animationObserver\\s*=\\s*new\\s+IntersectionObserver\\([^;]+\\);',  # Observer creation
        r'document\\.addEventListener\\(\\s*["\']DOMContentLoaded["\'][^}]*animationObserver[^}]*\\}\\);',  # DOM ready handlers with animations
        r'animatedElements\\.forEach\\([^;]+\\);',  # Animation element loops
    ]
    
    for pattern in js_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    return content


def get_theme_animation_types(theme: str) -> List[str]:
    """Get available animation types for a specific theme"""
    theme_animations = {
        "minimal": ["fadeInUp", "slideUp"],
        "brutalist": ["brutalistSlam", "brutalistPop"],  
        "dark": ["darkFadeIn", "darkGlow"],
        "playful": ["bounce", "pulse"],
        "animated": ["fadeInStagger", "countUp", "slideDown"]
    }
    
    return theme_animations.get(theme, ["fadeInUp"])


def validate_animation_support(content: str) -> Dict[str, bool]:
    """Validate animation support in content"""
    checks = {
        "has_intersection_observer": "IntersectionObserver" in content,
        "has_animation_css": "@keyframes" in content,
        "has_animate_classes": "animate-" in content,
        "has_data_attributes": "data-animate" in content,
        "has_reduced_motion": "prefers-reduced-motion" in content
    }
    
    return checks


def extract_existing_animations(content: str) -> List[str]:
    """Extract existing animation names from content"""
    animations = []
    
    # Find keyframe animations
    keyframe_matches = re.findall(r'@keyframes\\s+(\\w+)', content, re.IGNORECASE)
    animations.extend(keyframe_matches)
    
    # Find animate classes
    class_matches = re.findall(r'\\.animate-(\\w+)', content, re.IGNORECASE)
    animations.extend(class_matches)
    
    return list(set(animations))


def generate_animation_report(content: str, theme: str) -> Dict[str, any]:
    """Generate comprehensive animation analysis report"""
    return {
        "theme": theme,
        "supported_animations": get_theme_animation_types(theme),
        "existing_animations": extract_existing_animations(content),
        "validation": validate_animation_support(content),
        "has_animations": bool(extract_existing_animations(content)),
        "recommended_animations": get_recommended_animations_for_theme(theme)
    }


def get_recommended_animations_for_theme(theme: str) -> List[Tuple[str, str]]:
    """Get recommended animation-element pairs for theme"""
    recommendations = {
        "minimal": [
            ("fadeInUp", "sections and cards"),
            ("slideUp", "headings and text blocks")
        ],
        "brutalist": [
            ("brutalistSlam", "main sections and headers"),
            ("brutalistPop", "buttons and CTAs")
        ],
        "dark": [
            ("darkFadeIn", "content sections"),
            ("darkGlow", "interactive elements")
        ],
        "playful": [
            ("bounce", "buttons and icons"),
            ("pulse", "call-to-action elements")
        ],
        "animated": [
            ("fadeInStagger", "list items and cards"),
            ("countUp", "statistics and numbers")
        ]
    }
    
    return recommendations.get(theme, [("fadeInUp", "general elements")])


def get_animation_requirements_string() -> str:
    """Get animation requirements from prompt templates"""
    return get_animation_requirements()