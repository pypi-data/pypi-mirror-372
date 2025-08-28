"""
Page Analysis Module

Intelligently analyzes product descriptions to determine which pages are needed
for a multi-page website. Uses AI to extract entities and suggest page types.
"""

import re
from typing import Dict, List, Tuple, Any
from rich.console import Console
from .claude_integration import run_claude_with_progress


class PageAnalyzer:
    """Intelligent page analysis system for multi-page websites"""
    
    def __init__(self):
        self.console = Console()
        self.page_types = {
            'homepage': {
                'always_include': True,
                'description': 'Main landing page with overview and hero section',
                'path': 'index.html',
                'priority': 1
            },
            'features': {
                'keywords': ['feature', 'functionality', 'capability', 'tool', 'benefit', 'advantage'],
                'description': 'Detailed features and product capabilities',
                'path': 'features/index.html',
                'priority': 2
            },
            'pricing': {
                'keywords': ['pricing', 'price', 'plan', 'subscription', 'cost', 'free', 'paid', 'tier', '$', 'payment'],
                'description': 'Pricing plans and subscription options',
                'path': 'pricing/index.html',
                'priority': 3
            },
            'about': {
                'keywords': ['team', 'company', 'founded', 'mission', 'vision', 'story', 'about', 'history', 'founder'],
                'description': 'About the company and team',
                'path': 'about/index.html',
                'priority': 4
            },
            'contact': {
                'keywords': ['contact', 'support', 'email', 'phone', 'address', 'location', 'reach', 'get in touch'],
                'description': 'Contact information and support',
                'path': 'contact/index.html',
                'priority': 5
            },
            'blog': {
                'keywords': ['blog', 'articles', 'content', 'resources', 'news', 'updates', 'insights'],
                'description': 'Blog and content hub',
                'path': 'blog/index.html',
                'priority': 6
            },
            'case-studies': {
                'keywords': ['case study', 'testimonial', 'success story', 'customer', 'results', 'example'],
                'description': 'Customer case studies and testimonials',
                'path': 'case-studies/index.html',
                'priority': 7
            },
            'integrations': {
                'keywords': ['integration', 'api', 'connect', 'plugin', 'addon', 'extension', 'workflow'],
                'description': 'Integrations and API documentation',
                'path': 'integrations/index.html',
                'priority': 8
            }
        }
    
    def analyze_description(self, description: str) -> Dict[str, Any]:
        """Analyze product description to suggest pages"""
        
        # Keyword-based analysis
        suggested_pages = self._keyword_analysis(description)
        
        # AI-enhanced analysis
        ai_suggestions = self._ai_analysis(description)
        
        # Merge suggestions
        final_suggestions = self._merge_suggestions(suggested_pages, ai_suggestions)
        
        return {
            'suggested_pages': final_suggestions,
            'analysis_summary': self._generate_summary(final_suggestions),
            'total_pages': len(final_suggestions)
        }
    
    def _keyword_analysis(self, description: str) -> List[Dict[str, Any]]:
        """Analyze description using keyword matching"""
        description_lower = description.lower()
        suggested = []
        
        for page_type, config in self.page_types.items():
            if config.get('always_include', False):
                suggested.append({
                    'type': page_type,
                    'confidence': 1.0,
                    'reason': 'Always included',
                    'config': config
                })
                continue
            
            keywords = config.get('keywords', [])
            matches = sum(1 for keyword in keywords if keyword in description_lower)
            
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                suggested.append({
                    'type': page_type,
                    'confidence': confidence,
                    'reason': f'Found {matches} keyword matches',
                    'config': config
                })
        
        return suggested
    
    def _ai_analysis(self, description: str) -> Dict[str, Any]:
        """Use AI to analyze and suggest pages with dynamic navigation names"""
        
        prompt = f"""Analyze this product description and suggest which website pages would be most valuable, including product-specific navigation names.

Product Description:
{description}

Available page types:
- homepage: Main landing page (always needed)
- features: Detailed product capabilities
- pricing: Plans and pricing information
- about: Company and team information
- contact: Contact and support
- blog: Content and resources
- case-studies: Customer success stories
- integrations: API and integrations

For each page type:
1. Rate from 0.0 to 1.0 how valuable it would be
2. Suggest a product-specific navigation name (if applicable)
3. Provide a brief reason for the score

Consider the product type, target audience, and what users would need.

Respond in JSON format:
{{
    "homepage": {{
        "score": 1.0,
        "nav_name": "Home",
        "reason": "Essential landing page"
    }},
    "features": {{
        "score": 0.8,
        "nav_name": "Capabilities",
        "reason": "Users need to understand product functionality"
    }},
    "pricing": {{
        "score": 0.6,
        "nav_name": "Plans & Pricing",
        "reason": "Important for conversion decisions"
    }},
    "about": {{
        "score": 0.3,
        "nav_name": "About Us",
        "reason": "Good for trust building but not critical"
    }},
    "contact": {{
        "score": 0.7,
        "nav_name": "Get Support",
        "reason": "Users need support access"
    }},
    "blog": {{
        "score": 0.2,
        "nav_name": "Resources",
        "reason": "Content marketing not essential for MVP"
    }},
    "case-studies": {{
        "score": 0.4,
        "nav_name": "Success Stories",
        "reason": "Social proof valuable but secondary"
    }},
    "integrations": {{
        "score": 0.9,
        "nav_name": "Integrations",
        "reason": "Critical for API-based products"
    }}
}}"""
        
        try:
            result, _ = run_claude_with_progress(prompt, "AI analyzing page suggestions...")
            
            # Parse JSON response
            import json
            result_clean = result.strip()
            
            # Extract JSON if wrapped in code blocks
            if '```json' in result_clean:
                # Extract JSON from code blocks
                json_start = result_clean.find('```json') + 7
                json_end = result_clean.find('```', json_start)
                result_clean = result_clean[json_start:json_end].strip()
            elif '```' in result_clean:
                # Extract JSON from any code blocks
                json_start = result_clean.find('```') + 3
                json_end = result_clean.rfind('```')
                result_clean = result_clean[json_start:json_end].strip()
            
            # Find JSON object in response
            if '{' in result_clean and '}' in result_clean:
                json_start = result_clean.find('{')
                json_end = result_clean.rfind('}') + 1
                result_clean = result_clean[json_start:json_end]
            
            ai_scores = json.loads(result_clean)
            return ai_scores
        except json.JSONDecodeError as e:
            self.console.print(f"[yellow]⚠️  AI analysis failed: JSON parse error. Using keyword analysis only.[/yellow]")
            return {}
        except Exception as e:
            self.console.print(f"[yellow]⚠️  AI analysis failed: {e}. Using keyword analysis only.[/yellow]")
            return {}
    
    def _merge_suggestions(self, keyword_suggestions: List[Dict], ai_suggestions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Merge keyword and AI suggestions with dynamic navigation names"""
        final_suggestions = []
        
        # Create a mapping of existing suggestions
        keyword_map = {s['type']: s for s in keyword_suggestions}
        
        # Process all page types
        for page_type, config in self.page_types.items():
            keyword_suggestion = keyword_map.get(page_type)
            ai_data = ai_suggestions.get(page_type, {})
            
            # Handle both old format (float) and new format (dict)
            if isinstance(ai_data, dict):
                ai_score = ai_data.get('score', 0.0)
                ai_nav_name = ai_data.get('nav_name', config.get('description', page_type.title()))
                ai_reason = ai_data.get('reason', 'AI suggested')
            else:
                ai_score = ai_data if isinstance(ai_data, (int, float)) else 0.0
                ai_nav_name = config.get('description', page_type.replace('-', ' ').title())
                ai_reason = f'AI score: {ai_score:.1f}'
            
            if keyword_suggestion:
                # Combine keyword and AI confidence
                combined_confidence = (keyword_suggestion['confidence'] + ai_score) / 2
                final_suggestions.append({
                    'type': page_type,
                    'confidence': combined_confidence,
                    'reason': f"{keyword_suggestion['reason']} + {ai_reason}",
                    'config': config,
                    'nav_name': ai_nav_name,  # Use AI-suggested navigation name
                    'selected': combined_confidence >= 0.5
                })
            elif ai_score >= 0.5:
                # AI suggests this page even without keyword matches
                final_suggestions.append({
                    'type': page_type,
                    'confidence': ai_score,
                    'reason': ai_reason,
                    'config': config,
                    'nav_name': ai_nav_name,  # Use AI-suggested navigation name
                    'selected': True
                })
        
        # Sort by priority and confidence
        final_suggestions.sort(key=lambda x: (x['config']['priority'], -x['confidence']))
        
        return final_suggestions
    
    def _generate_summary(self, suggestions: List[Dict]) -> str:
        """Generate a summary of the analysis"""
        total_suggested = len([s for s in suggestions if s.get('selected', False)])
        high_confidence = len([s for s in suggestions if s['confidence'] >= 0.8])
        
        summary = f"Suggested {total_suggested} pages total"
        if high_confidence > 0:
            summary += f", {high_confidence} with high confidence"
        
        return summary
    
    def get_page_dependencies(self) -> Dict[str, List[str]]:
        """Define page dependencies for generation ordering"""
        return {
            'homepage': [],  # No dependencies
            'features': ['homepage'],
            'pricing': ['homepage', 'features'],
            'about': ['homepage'],
            'contact': ['homepage'],
            'blog': ['homepage'],
            'case-studies': ['homepage', 'features'],
            'integrations': ['homepage', 'features']
        }
    
    def optimize_page_order(self, selected_pages: List[str]) -> List[str]:
        """Optimize page generation order based on dependencies"""
        dependencies = self.get_page_dependencies()
        ordered_pages = []
        remaining_pages = set(selected_pages)
        
        # Iteratively add pages whose dependencies are satisfied
        while remaining_pages:
            added_this_round = False
            
            for page in list(remaining_pages):
                page_deps = dependencies.get(page, [])
                
                # Check if all dependencies are already in ordered_pages or not in selected pages
                if all(dep in ordered_pages or dep not in selected_pages for dep in page_deps):
                    ordered_pages.append(page)
                    remaining_pages.remove(page)
                    added_this_round = True
            
            # Safety check to prevent infinite loops
            if not added_this_round and remaining_pages:
                # Add remaining pages in priority order
                remaining_sorted = sorted(remaining_pages, 
                                        key=lambda x: self.page_types[x]['priority'])
                ordered_pages.extend(remaining_sorted)
                break
        
        return ordered_pages