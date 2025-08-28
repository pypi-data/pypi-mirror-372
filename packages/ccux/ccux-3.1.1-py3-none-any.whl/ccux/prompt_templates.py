
from textwrap import dedent
import os
from typing import List, Tuple, Dict

# Import theme specifications for theme-aware prompts
try:
    from .theme_specifications import get_theme_design_system_rules
except ImportError:
    # Fallback if theme_specifications not available
    def get_theme_design_system_rules(theme_name: str) -> str:
        return f"Generate design system for {theme_name} theme."

def get_functional_requirements(include_forms: bool = False) -> str:
    """Get standard functional requirements for all HTML generation prompts"""
    form_requirements = ""
    if include_forms:
        form_requirements = """
   - Include basic contact form with email input and submit button (action="#" method="POST")"""
    
    return f"""
CRITICAL FUNCTIONAL REQUIREMENTS:

1. Navigation System (MANDATORY):
   - Include sticky navbar with smooth scroll-to-section links (#hero, #features, #pricing, etc.)
   - Add mobile hamburger menu with JavaScript toggle functionality
   - Every major section MUST have an id attribute for navigation
   - Mobile menu implementation MUST include:
     * Hamburger button with id="mobile-menu-button" and proper aria attributes
     * Mobile menu with id="mobile-menu" (initially hidden with 'hidden' class)
     * Toggle function: onclick="toggleMobileMenu()" 
     * JavaScript function: function toggleMobileMenu() {{ const menu = document.getElementById('mobile-menu'); menu.classList.toggle('hidden'); }}
     * Proper aria-expanded and aria-controls attributes for accessibility
     * Close menu when clicking nav links: onclick="document.getElementById('mobile-menu').classList.add('hidden')"
   - Include smooth scrolling: html {{ scroll-behavior: smooth; }}

2. Responsive Design (REQUIRED):
   - Apply Tailwind breakpoints throughout: sm: (640px+), md: (768px+), lg: (1024px+)
   - Use responsive classes: text-sm md:text-lg, px-4 md:px-8, grid-cols-1 md:grid-cols-2 lg:grid-cols-3
   - Ensure mobile navigation works properly with hamburger menu
   - Test all sections at different breakpoints

3. Working CTAs (REQUIRED):
   - Primary CTA must be functional: use mailto: link for contact{form_requirements}
   - Secondary CTAs use real links (href="#contact" or "mailto:contact@example.com")
   - All buttons must have hover states and keyboard accessibility

4. JavaScript Requirements (MANDATORY):
   - MUST include this exact JavaScript function in a <script> tag before closing </body>:
   
   function toggleMobileMenu() {{
     const menu = document.getElementById('mobile-menu');
     const button = document.getElementById('mobile-menu-button');
     const isExpanded = menu.classList.contains('hidden');
     
     menu.classList.toggle('hidden');
     if (button) {{
       button.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
     }}
   }}
   
   // Close mobile menu when clicking nav links
   document.addEventListener('DOMContentLoaded', function() {{
     const mobileNavLinks = document.querySelectorAll('#mobile-menu a[href^="#"]');
     mobileNavLinks.forEach(link => {{
       link.addEventListener('click', () => {{
         document.getElementById('mobile-menu').classList.add('hidden');
       }});
     }});
   }});
"""

def get_animation_requirements() -> str:
    """Get smart animation system requirements for CLI-controlled animations"""
    return """
SMART ANIMATION SYSTEM (REQUIRED):

1. Section Detection & Conditional Animation:
   - Auto-detect existing sections: hero, features, pricing, testimonials, stats, cards
   - Apply animations ONLY to detected sections that exist on the page
   - Skip animations for empty or static sections
   - Use data attributes for section identification: data-animate="true"

2. Animation Types & Timings:
   - Entrance animations: fadeInUp (500ms ease-out) for main sections
   - Mobile menu toggle: slideDown (200ms ease-out) 
   - Feature cards: Progressive reveal with 150ms stagger delay
   - Stats/numbers: Count-up animation on scroll if numeric content detected
   - Testimonials: Auto-fade transition if multiple testimonials exist
   - Micro-interactions: Button hover/focus (100-150ms)

3. Accessibility & Performance:
   - MANDATORY: Respect @media (prefers-reduced-motion: reduce) - disable all animations
   - Use CSS transforms (translateX, translateY, scale) for GPU acceleration
   - Implement IntersectionObserver for scroll-triggered animations
   - Set will-change property only during animations

4. CLI Animation Control:
   - NO toggle button in navbar - controlled via CLI command
   - NO localStorage functionality - controlled via CSS classes
   - Animations enabled by default on generation
   - Support .no-animations class to disable all animations
   - Per-section control via data-animate attributes

5. Animation CSS & JavaScript:
   - Include @keyframes: fadeInUp, slideDown, countUp, fadeInStagger
   - Animation controller JavaScript with init(), detectSections()
   - Use CSS custom properties for stagger delays: --stagger-delay
   - Implement intersection observer with 0.1 threshold
   - Include .no-animations CSS rules to disable all animations

6. Smart Defaults:
   - Hero: Immediate fadeIn on page load
   - Features: Scroll-triggered staggered entrance
   - Stats: Count-up animation on scroll
   - Mobile menu: Slide animation with backdrop
   - Testimonials: Auto-rotate if multiple (5s intervals)
   - All animations: Enabled by default, controlled by CLI commands"""

def reference_discovery_prompt(desc: str) -> str:
    return f"Given this product: '{desc}', find 3 live product URLs of similar tools. Only list working websites, not blogs. Format: Name – URL – short note."


def deep_product_understanding_prompt(desc: str) -> str:
    return f'''Analyze this product for deep understanding: {desc}

Context: Perform a strategic analysis to understand the core problem this product solves, who needs it, what makes it different, its strongest feature, and potential risks.

Rules: Be concise, no fluff, focus on user pain and real market positioning.

IMPORTANT: You must respond with valid JSON only. No explanations, no markdown, no code blocks - just the raw JSON object.

{{
  "problem": "Core issue or pain point this product solves",
  "user": "Primary target user or customer segment who needs this",
  "differentiator": "Key factor that sets this apart from existing solutions", 
  "best_feature": "Most compelling or loved feature/capability",
  "risks": "Main reasons this product might fail or struggle"
}}'''


def ux_analysis_prompt(product_desc: str, refs: List[str]) -> str:
    refs_text = "\n".join(
        f"- {screenshot_path}" for screenshot_path in refs
    )

    image_count = len(refs)
    return f'''UX competitive analysis of: {product_desc}

I'm showing you {image_count} competitor website screenshot(s) below. Please analyze these images for UX patterns and design elements.

Screenshots to analyze:
{refs_text}

Provide a detailed visual analysis of the screenshots, focusing on:
- Navigation patterns and menu structures
- Call-to-action placement and design
- Layout and information hierarchy
- Typography and visual messaging
- Mobile responsiveness indicators
- Conversion-focused elements

Respond in JSON:
{{
  "patterns": {{
    "navigation": ["specific navigation patterns observed"],
    "ctas": ["call-to-action styles and placements seen"],
    "layouts": ["layout structures and grid systems used"],
    "messaging": ["headline and copy patterns identified"]
  }},
  "differentiators": [{{"screenshot":"reference_1_domain","element":"specific UI element","why":"what makes this unique or effective"}}],
  "weaknesses": {{
    "common": ["widespread UX issues seen across sites"],
    "severe": ["major usability problems identified"]
  }},
  "recommendations": {{
    "adopt": ["effective patterns to implement"],
    "avoid": ["problematic patterns to skip"],
    "innovate": ["opportunities to do better than competitors"]
  }},
  "summary": "1-2 sentence key takeaway from visual analysis"
}}

Rules: 
- Base analysis ONLY on what you can see in the images
- Be specific about visual elements and their placement
- Focus on mobile-first design considerations
- Identify conversion-optimization opportunities'''


def empathize_prompt(product_desc: str, product_understanding: Dict, ux_analysis: Dict) -> str:
    short_problem = str(product_understanding.get("problem", "N/A"))[:200]
    short_user = str(product_understanding.get("user", "N/A"))[:200]
    short_diff = str(product_understanding.get("differentiator", "N/A"))[:200]
    
    nav_patterns = ux_analysis.get("patterns", {}).get("navigation", [])
    adopt = ux_analysis.get("recommendations", {}).get("adopt", [])
    avoid = ux_analysis.get("recommendations", {}).get("avoid", [])
    return f'''Product: {product_desc}

Understanding (trimmed):
- Problem: {short_problem}
- User: {short_user}
- Differentiator: {short_diff}

UX Insights:
- Navigation patterns: {nav_patterns}
- Adopt: {adopt}
- Avoid: {avoid}

IMPORTANT: You must respond with valid JSON only. No explanations, no markdown, no code blocks - just the raw JSON object.

{{
  "context": {{
    "device": "...",
    "channels": ["...", "...", "..."],
    "immediate_need": "..."
  }},
  "questions": {{
    "identity": ["...", "..."],
    "value": ["...", "..."],
    "trust": ["...", "..."]
  }},
  "conversion": {{
    "primary": "...",
    "secondary": ["...", "..."],
    "required_info": ["...", "..."]
  }},
  "personas": [
    {{
      "name": "...",
      "role": "...",
      "urgency": "...",
      "decision_process": "...",
      "content_needs": ["...", "..."]
    }}
  ],
  "touchpoints": {{
    "first_impression": "...",
    "dropoff_risk": "...",
    "persuasive_element": "..."
  }},
  "research_gaps": ["...", "..."]
}}

Rules: Be concise, quote user questions, focus on behaviors. Output only the JSON structure above with no additional text.'''


def define_prompt(product_desc, user_research) -> str:
    return f'''Product: {product_desc}

Research:
- Goal: {user_research.get("conversion",{}).get("primary","N/A")}
- Context: {user_research.get("context",{}).get("immediate_need","N/A")}
- Questions: {user_research.get("questions",{}).get("value",[])}
- Personas: {[p.get("name","N/A")+" ("+p.get("role","")+")" for p in user_research.get("personas",[])]}

Output JSON only:
{{
  "core_pages": {{
    "homepage": {{"job":"...","must_show":["...","..."],"next_step":"..."}},
    "key_secondary": [{{"page":"...","job":"...","exit_risk":"...","recovery":"..."}}]
  }},
  "primary_flow": {{
    "steps":["...","...","..."],
    "dropoff_points":["...","..."],
    "support_elements":["...","..."]
  }},
  "alternate_paths": {{
    "price_concerns":"...",
    "trust_issues":"...",
    "feature_questions":"..."
  }},
  "navigation": {{
    "global_nav":["...","...","..."],
    "mobile_priority":"...",
    "footer_strategy":"..."
  }},
  "conflicts":["...","..."],
  "research_gaps":["...","..."]
}}
Rules: Be concrete, use UI elements, flag conflicts, note missing research.'''

def ideate_prompt(product_desc, user_research, site_flow) -> str:
    return f'''Product: {product_desc}

Research:
- Goal: {user_research.get("conversion",{}).get("primary","N/A")}
- Questions: {user_research.get("questions",{}).get("value",[])}
- Homepage Must Show: {site_flow.get("core_pages",{}).get("homepage",{}).get("must_show",[])}
- Primary Flow: {site_flow.get("primary_flow",{}).get("steps",[])}

Output JSON only:
{{
  "core_messaging": {{
    "value_proposition": "...",
    "unique_angle": "..."
  }},
  "hero": {{
    "headline": "...",
    "subhead": "...",
    "primary_cta": "...",
    "supporting_element": "..."
  }},
  "benefits": [
    {{"headline":"...","proof_point":"...","icon_concept":"..."}},
    {{"headline":"...","proof_point":"...","icon_concept":"..."}},
    {{"headline":"...","proof_point":"...","icon_concept":"..."}}
  ],
  "objections": {{
    "top_3_concerns": ["...","...","..."],
    "faq_answers": [{{"question":"...","answer":"..."}}],
    "trust_elements": ["...","..."]
  }},
  "ctas": {{
    "primary_action":"...",
    "secondary_action":"...",
    "microcopy":"..."
  }},
  "rules": {{
    "tone":"...",
    "avoid":["...","..."],
    "must_include":["...","..."]
  }}
}}
Rules: Be concise, outcome-focused, use real user wording where possible.'''

def wireframe_prompt(product_desc, content_strategy, site_flow) -> str:
    return f'''Product: {product_desc}

Content:
- Hero: {content_strategy.get("hero",{}).get("headline","N/A")}
- Benefits: {[b.get("headline","N/A") for b in content_strategy.get("benefits",[])]}
- CTA: {content_strategy.get("ctas",{}).get("primary_action","N/A")}

Flow:
- Pages: {list(site_flow.get("core_pages",{}).keys())}
- Nav Priority: {site_flow.get("navigation",{}).get("mobile_priority","N/A")}

Output JSON only:
{{
  "layout": {{
    "sections": [
      {{"name":"hero","elements":["..."],"mobile_stack":["..."],"priority":"..."}},
      {{"name":"benefits","elements":["..."],"mobile_stack":["..."],"priority":"..."}}
    ]
  }},
  "mobile_checks": {{
    "critical":["...","...","..."],
    "red_flags":["...","..."]
  }},
  "interactions": {{
    "key":[{{"element":"...","behavior":"...","mobile_consideration":"..."}}]
  }},
  "responsive": {{
    "breakpoints": {{
      "mobile": {{"rules":["...","..."]}},
      "tablet": {{"rules":["...","..."]}}
    }}
  }}
}}
Rules: Be concise, mobile-first, ensure CTA always visible.'''


def design_system_prompt(product_desc, wireframes, content_strategy, theme: str = "minimal") -> str:
    return f'''Product: {product_desc}

Wireframes:
- Sections: {[s.get("name","N/A") for s in wireframes.get("layout",{}).get("sections",[])]}
- Mobile Checks: {wireframes.get("mobile_checks",{}).get("critical",[])}

Tone: {content_strategy.get("rules",{}).get("tone","Professional")}

Output JSON only:
{{
  "typography": {{
    "typeface_choice": "...",
    "brand_rationale": "...",
    "heading_hierarchy": {{"h1":"...","h2":"...","h3":"..."}},
    "body_text": "..."
  }},
  "color_tokens": {{
    "primary":"#...","primary_light":"#...","primary_dark":"#...",
    "secondary":"#...","accent":"#...","surface":"#...","background":"#...",
    "success":"#...","warning":"#...","error":"#...",
    "text_primary":"#...","text_secondary":"#...","text_muted":"#...",
    "border":"#...","border_light":"#...","shadow":"#..."
  }},
  "gradients": {{
    "primary_gradient":"linear-gradient(135deg, #... 0%, #... 100%)",
    "hero_gradient":"linear-gradient(180deg, #... 0%, #... 100%)",
    "card_gradient":"linear-gradient(145deg, #... 0%, #... 100%)",
    "button_gradient":"linear-gradient(135deg, #... 0%, #... 100%)"
  }},
  "shadows": {{
    "card_shadow":"0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)",
    "button_shadow":"0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)",
    "hover_shadow":"0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)"
  }},
  "animations": {{
    "duration": {{"fast":"150ms","normal":"300ms","slow":"500ms"}},
    "easing": {{"ease_in":"cubic-bezier(0.4, 0, 1, 1)","ease_out":"cubic-bezier(0, 0, 0.2, 1)","ease_in_out":"cubic-bezier(0.4, 0, 0.2, 1)"}},
    "transforms": {{"scale_hover":"scale(1.05)","scale_click":"scale(0.95)","lift":"translateY(-2px)"}}
  }},
  "wcag_contrast": {{
    "primary_cta":"X.X:1 - PASS/FAIL",
    "body_text":"X.X:1 - PASS/FAIL",
    "secondary_text":"X.X:1 - PASS/FAIL",
    "error_text":"X.X:1 - PASS/FAIL",
    "accessible":"true/false"
  }},
  "signature_elements": [
    {{"element":"...","specification":"...","usage":"..."}},
    {{"element":"...","specification":"...","usage":"..."}}
  ],
  "components": {{
    "buttons": {{
      "primary":{{"default":"...","hover":"...","active":"...","disabled":"...","animation":"transform 300ms ease-out"}},
      "secondary":{{"default":"...","hover":"...","active":"...","disabled":"...","animation":"all 200ms ease-in-out"}},
      "ghost":{{"default":"...","hover":"...","active":"...","disabled":"...","animation":"all 150ms ease-in-out"}}
    }},
    "inputs": {{
      "text_field":{{"default":"...","focus":"...","error":"...","animation":"border-color 200ms ease-in-out"}},
      "select":{{"default":"...","focus":"...","hover":"...","animation":"all 150ms ease-out"}},
      "textarea":{{"default":"...","focus":"...","error":"...","animation":"border-color 200ms ease-in-out"}}
    }},
    "cards": {{
      "content":{{"default":"...","hover":"...","animation":"transform 300ms ease-out, box-shadow 300ms ease-out"}},
      "pricing":{{"default":"...","hover":"...","featured":"...","animation":"transform 200ms ease-in-out"}},
      "testimonial":{{"default":"...","hover":"...","animation":"all 250ms ease-out"}}
    }}
  }},
  "spacing_system": {{"scale":["2px","4px","8px","12px","16px","24px","32px","48px","64px","96px"],"usage":"..."}},
  "border_radius": {{"sm":"4px","md":"8px","lg":"12px","xl":"16px","2xl":"24px","full":"9999px"}},
  "svg_patterns": {{
    "hero_bg":"Complex geometric SVG background pattern with subtle animation",
    "section_divider":"Organic wave or curve SVG divider between sections",
    "decorative_elements":"Abstract shapes, dots, or lines for visual interest"
  }},
  "logo_concept": {{
    "style":"Modern, minimal, geometric/organic",
    "elements":"Icon + wordmark or symbol only",
    "colors":"Uses primary brand colors",
    "usage":"Header, footer, favicon"
  }},
  "summary": "..."
}}

{get_theme_design_system_rules(theme)}

Rules: Modern, animated, gradient-rich, high-contrast, mobile-optimized, includes SVG patterns and logo concept.'''


def high_fidelity_design_prompt(product_desc, design_system, wireframes, content_strategy) -> str:
    return f'''Product: {product_desc}

System:
- Typography: {design_system.get("typography",{}).get("typeface_choice","N/A")}
- Primary Color: {design_system.get("color_tokens",{}).get("primary","N/A")}
- Signature Elements: {[e.get("element","N/A") for e in design_system.get("signature_design_elements",[])]}

Wireframes: {[s.get("name","N/A") for s in wireframes.get("layout",{}).get("sections",[])]}
Tone: {content_strategy.get("rules",{}).get("tone","Professional")}

Output JSON only:
{{
  "design_specifications": {{
    "typography": "...",
    "colors": "...",
    "spacing": "...",
    "components": "..."
  }},
  "interactions": {{
    "hover_states": "...",
    "transitions": "...",
    "responsive": "..."
  }},
  "accessibility": {{
    "contrast": "...",
    "typography": "...",
    "navigation": "..."
  }},
  "implementation_ready": "..."
}}
Rules: Be clean, consistent, accessible, mobile-first.'''


def prototype_prompt(product_desc, content_strategy, design_system, wireframes) -> str:
    return f'''Product: {product_desc}

Content:
- Value Proposition: {content_strategy.get("core_messaging",{}).get("value_proposition","N/A")}
- Hero: {content_strategy.get("hero",{}).get("headline","N/A")}
- CTA: {content_strategy.get("ctas",{}).get("primary_action","N/A")}
- Tone: {content_strategy.get("rules",{}).get("tone","Professional")}

Design:
- Sections: {[s.get("name","N/A") for s in wireframes.get("layout",{}).get("sections",[])]}
- Personality: {design_system.get("typography",{}).get("brand_rationale","Modern and clean")}

Output JSON only:
{{
  "hero": {{"headline":"...","subheadline":"...","cta_primary":"...","cta_secondary":"..."}},
  "problem": {{"headline":"...","description":"...","pain_points":["...","...","..."]}},
  "solution": {{"headline":"...","value_proposition":"...","key_benefits":["...","...","..."]}},
  "features": {{"headline":"...","features":[{{"title":"...","description":"...","benefit":"..."}}]}},
  "social_proof": {{"headline":"...","testimonial":"...","stats":["...","...","..."]}},
  "pricing": {{"headline":"...","plan_name":"...","price":"...","features":["...","..."],"cta":"..."}},
  "footer": {{"cta_headline":"...","cta_description":"...","cta_button":"..."}}
}}
Rules: Use AIDA/PAS style, focus on benefits, strong CTAs, address objections, keep tone consistent.'''

def implementation_prompt(product_description, copy_content, framework, theme, design_data, include_forms: bool = False) -> str:
    """Final implementation prompt that consolidates all previous steps"""
    # Extract only what's essential from previous stages
    design_system = design_data.get('design_system', {})
    content_strategy = design_data.get('content_strategy', {})
    ux_analysis = design_data.get('ux_analysis', {})
    
    # Dynamic color handling
    primary_color = design_system.get('color_tokens', {}).get('primary')
    color_context = f"Primary Color: {primary_color}" if primary_color else "Color System: Generate appropriate palette"
    
    # Content highlights
    value_prop = content_strategy.get('core_messaging', {}).get('value_proposition', '')
    primary_cta = content_strategy.get('ctas', {}).get('primary_action', 'Get Started')
    
    return f'''You are a senior product designer implementing the final landing page.

Product: {product_description}
Framework: {framework}
Theme: {theme}

Consolidated Design Inputs:
1. {color_context}
2. Value Proposition: {value_prop[:120]}
3. Primary CTA: {primary_cta}
4. UX Patterns: {ux_analysis.get('recommendations', {}).get('adopt', [])[:2]}

Implementation Rules:
- Start with mobile layout then enhance for desktop
- Make every visual element serve a purpose
- Ensure 1.5s first contentful paint
- Maintain AA accessibility throughout
- Use system-generated assets where needed
- Use SVG icons or icon libraries (Heroicons, Lucide, Feather) instead of emoji characters for professional appearance
- IMPORTANT: When referencing images (reference.jpg, reference_1_*.jpg, etc.), use relative path ../filename.jpg since HTML is in output/landing-page/ but images are in output/

CRITICAL FUNCTIONAL REQUIREMENTS:

1. Navigation System (MANDATORY):
   - Include sticky navbar with smooth scroll-to-section links (#hero, #features, #pricing, etc.)
   - Add mobile hamburger menu with JavaScript toggle functionality
   - Every major section MUST have an id attribute for navigation
   - Mobile menu implementation MUST include:
     * Hamburger button with id="mobile-menu-button" and proper aria attributes
     * Mobile menu with id="mobile-menu" (initially hidden with 'hidden' class)
     * Toggle function: onclick="toggleMobileMenu()" 
     * JavaScript function: function toggleMobileMenu() {{ const menu = document.getElementById('mobile-menu'); menu.classList.toggle('hidden'); }}
     * Proper aria-expanded and aria-controls attributes for accessibility
     * Close menu when clicking nav links: onclick="document.getElementById('mobile-menu').classList.add('hidden')"
   - Include smooth scrolling: html {{ scroll-behavior: smooth; }}

2. Responsive Design (REQUIRED):
   - Apply Tailwind breakpoints throughout: sm: (640px+), md: (768px+), lg: (1024px+)
   - Use responsive classes: text-sm md:text-lg, px-4 md:px-8, grid-cols-1 md:grid-cols-2 lg:grid-cols-3
   - Ensure mobile navigation works properly with hamburger menu
   - Test all sections at different breakpoints

3. Working CTAs (REQUIRED):
   - Primary CTA must be functional: use mailto: link for contact{" or working form with action='#'" if include_forms else ""}
   {"   - Include basic contact form with email input and submit button (action='#' method='POST')" if include_forms else ""}
   - Secondary CTAs use real links (href="#contact" or "mailto:contact@example.com")
   - All buttons must have hover states and keyboard accessibility

{get_animation_requirements()}

Visual Treatment Guide:
<!-- IMAGE-STRATEGY: [hero-image/product-shot/illustration/none] -->
<!-- ANIMATION-LEVEL: [none/micro/scroll-triggered] -->
<!-- VISUAL-DENSITY: [sparse/balanced/rich] -->

CRITICAL: Output ONLY the complete HTML code starting with <!DOCTYPE html>.
Do NOT include any explanations, descriptions, or markdown formatting.
Do NOT write about what you created - just output the raw HTML code.
Your response should begin immediately with <!DOCTYPE html> and end with </html>.'''


def landing_prompt(product_description, framework, theme, sections, design_data=None, include_forms: bool = False) -> str:
    sections_str = ", ".join(sections) if sections else "hero, features, pricing, footer"
    
    # Dynamic content integration
    content_hooks = ""
    if design_data:
        cs = design_data.get('content_strategy', {})
        hooks = [
            f"Value Hook: {cs.get('core_messaging',{}).get('unique_angle','')}",
            f"Emotional Trigger: {cs.get('hero',{}).get('supporting_element','')}",
            f"Social Proof: {cs.get('objections',{}).get('trust_elements',[])[:1]}"
        ]
        content_hooks = "\nContent Anchors:\n- " + "\n- ".join(filter(None, hooks))
    
    return f'''Create a high-converting landing page that adapts to its purpose.

Product: {product_description}
Sections: {sections_str}
Framework: {framework}
Theme: {theme}
{content_hooks}

Design Framework:
1. Assess each section's communication goal
2. Choose visual treatment accordingly:
   - Data → Charts/diagrams
   - Features → Product shots
   - Benefits → Illustrations
   - Social Proof → Testimonials with photos

Technical Requirements:
- Semantic HTML5
- CSS custom properties
- Responsive images
- Accessible interactions
- Use SVG icons or icon libraries (Heroicons, Lucide, Feather) instead of emoji characters for professional appearance
- IMPORTANT: When referencing images (reference.jpg, reference_1_*.jpg, etc.), use relative path ../filename.jpg since HTML is in output/landing-page/ but images are in output/

CRITICAL FUNCTIONAL REQUIREMENTS:

1. Navigation System (MANDATORY):
   - Create sticky navbar with logo and navigation links
   - Each nav link must use href="#section-id" for smooth scrolling to sections
   - Add mobile hamburger menu with toggle functionality
   - Every major section MUST have an id attribute (id="hero", id="features", id="pricing", etc.)
   - Mobile menu implementation MUST include:
     * Hamburger button with id="mobile-menu-button" and proper aria attributes
     * Mobile menu with id="mobile-menu" (initially hidden with 'hidden' class)
     * Toggle function: onclick="toggleMobileMenu()" 
     * JavaScript function: function toggleMobileMenu() {{ const menu = document.getElementById('mobile-menu'); menu.classList.toggle('hidden'); }}
     * Proper aria-expanded and aria-controls attributes for accessibility
     * Close menu when clicking nav links: onclick="document.getElementById('mobile-menu').classList.add('hidden')"
   - Add smooth scrolling CSS: html {{ scroll-behavior: smooth; }}

2. Responsive Design (REQUIRED):
   - Mobile-first approach: Base styles for mobile devices
   - Use Tailwind breakpoints consistently:
     * sm: (640px+) - Tablet adjustments
     * md: (768px+) - Small desktop
     * lg: (1024px+) - Large desktop
   - Apply responsive classes throughout: text-sm md:text-lg, px-4 md:px-8, grid-cols-1 md:grid-cols-2 lg:grid-cols-3
   - Ensure mobile navigation hamburger menu functions properly
   - Make all images and text scale appropriately

3. Working CTAs (REQUIRED):
   - Primary CTA must be functional: Use mailto: link for contact{" or implement working form" if include_forms else ""}
   {"   - Contact form example: action='#' method='POST' with email input and submit button" if include_forms else ""}
   - Secondary CTAs use real links: href="#contact" or "mailto:contact@example.com"
   - All buttons must have hover states and be keyboard accessible (tabindex, focus states)
   {"   - Include proper form validation and user feedback" if include_forms else ""}

{get_animation_requirements()}

CRITICAL: Output ONLY the complete HTML code starting with <!DOCTYPE html>.
Do NOT include any explanations, descriptions, or markdown formatting.
Do NOT write about what you created - just output the raw HTML code.
Your response should begin immediately with <!DOCTYPE html> and end with </html>.'''


def regeneration_prompt(product_desc, framework, theme, section_list, existing_context=None) -> str:
    """Smart regeneration that understands existing design language"""
    context_analysis = ""
    if existing_context:
        context_analysis = "\n".join(
            f"- {k}: {v[:60]}..." if isinstance(v,str) else f"- {k}: {v}"
            for k,v in existing_context.items()
        )
    
    sections_to_generate = "\n".join([f"- {section}" for section in section_list])
    
    # Add section-specific guidance
    section_guidance = ""
    if any(section.lower() in ['header', 'nav', 'navigation'] for section in section_list):
        section_guidance += """
HEADER/NAVIGATION SPECIFIC REQUIREMENTS:
- MUST include proper section markers: <!-- START: header --> and <!-- END: header -->
- MUST maintain all navigation links to existing sections (#hero, #features, #pricing, etc.)
- MUST preserve mobile hamburger menu functionality with onclick="toggleMobileMenu()"
- MUST keep fixed navigation: position fixed, top-0, z-50 classes
- MUST include backdrop-blur or similar styling for scroll effects
- MUST maintain brand logo and company name consistency
- Navigation links should match existing section structure
"""
    
    if any(section.lower() == 'footer' for section in section_list):
        section_guidance += """
FOOTER SPECIFIC REQUIREMENTS:
- MUST include proper section markers: <!-- START: footer --> and <!-- END: footer -->
- MUST include comprehensive company information and contact details
- MUST maintain multi-column responsive grid layout (4 columns on desktop, stacked on mobile)
- MUST include social media links with proper icons and hover effects
- MUST preserve business hours, location, and contact information
- MUST include quick navigation links to main page sections
- MUST maintain copyright notice and legal links (Privacy Policy, Terms, etc.)
- MUST preserve dark theme styling (typically bg-gray-900 with light text)
- Footer should be comprehensive and informative, containing all essential business info
"""
    
    # Get theme-specific design rules
    theme_rules = ""
    if theme == "brutalist":
        theme_rules = """
BRUTALIST THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Use ONLY these colors: bg-black, bg-white, bg-red-600, bg-yellow-400
- Use ONLY these text styles: font-black, font-bold, uppercase, tracking-tight, tracking-wide
- REQUIRED classes on ALL sections: brutalist-border, brutalist-shadow
- Typography: JetBrains Mono font (already loaded)
- NO rounded corners, NO gradients, NO soft shadows
- Use sharp, geometric layouts with high contrast
- All buttons MUST have: brutalist-border brutalist-shadow hover:translate-x-1 hover:translate-y-1 hover:shadow-none
- All text MUST be UPPERCASE where appropriate
- Color combinations: black text on white/yellow, white text on black/red"""
    elif theme == "minimal":
        theme_rules = """
MINIMAL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Use neutral colors: bg-white, bg-gray-50, bg-gray-100, text-gray-900, text-gray-600
- Typography: font-normal, font-medium, font-semibold (NO font-black)
- Generous whitespace: py-16, py-24, space-y-8, space-y-12
- Subtle borders: border border-gray-200, rounded-lg
- Clean buttons: bg-blue-600, hover:bg-blue-700, rounded-md, px-6 py-3
- Minimal shadows: shadow-sm, shadow-md
- Simple layouts with lots of breathing room"""
    elif theme == "playful":
        theme_rules = """
PLAYFUL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Bright colors: bg-pink-500, bg-purple-500, bg-blue-500, bg-yellow-400, bg-green-500
- Rounded elements: rounded-xl, rounded-2xl, rounded-full
- Fun typography: font-bold, font-extrabold
- Organic shapes and bouncy animations: hover:scale-105, transition-transform
- Colorful gradients: bg-gradient-to-r from-pink-500 to-purple-500
- Playful spacing and asymmetrical layouts"""
    elif theme == "corporate":
        theme_rules = """
CORPORATE THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Professional colors: bg-blue-900, bg-gray-800, bg-white, text-blue-900
- Conservative typography: font-medium, font-semibold
- Structured layouts: grid system, even spacing
- Subtle shadows: shadow-lg, shadow-xl
- Professional buttons: bg-blue-600, hover:bg-blue-700
- Clean, trustworthy design patterns"""
    elif theme == "terminal":
        theme_rules = """
TERMINAL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Matrix colors: bg-black, bg-gray-900, text-green-400, text-green-300
- Monospace font: font-mono (already loaded)
- Terminal aesthetics: border-green-500, bg-green-500/10
- Command-line elements: $ prompts, code blocks
- Pixelated/blocky design: sharp edges, no rounded corners
- Glowing effects: animate-pulse, text-green-400"""
    elif theme == "dark":
        theme_rules = """
DARK THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Dark backgrounds: bg-gray-900, bg-gray-800, bg-black
- Light text: text-white, text-gray-100, text-gray-300
- Dark accent colors: bg-blue-600, bg-purple-600, bg-indigo-600
- Subtle borders: border-gray-700, border-gray-600
- High contrast for accessibility"""
    elif theme == "morphism":
        theme_rules = """
MORPHISM THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Soft backgrounds: bg-gray-100, bg-white, bg-gradient-to-br
- Glass effects: backdrop-blur-sm, bg-white/20, border border-white/20
- Soft shadows: shadow-xl, shadow-2xl with blur
- Rounded corners: rounded-xl, rounded-2xl
- Subtle colors with transparency: bg-blue-500/10, text-gray-700"""
    else:
        theme_rules = f"Follow {theme} theme guidelines with appropriate colors and styling"
    
    return f'''You are a design system specialist refreshing page sections.

Product: {product_desc}
Sections to update: {", ".join(section_list)}
Framework: {framework}
Theme: {theme}

Existing Context:
{context_analysis or "No specific context provided"}

{section_guidance}

{theme_rules}

Generate ONLY the requested sections with proper markers. For each section, use this format:

<!-- START: section_name -->
<section>
  ... section content ...
</section>
<!-- END: section_name -->

Sections to generate:
{sections_to_generate}

CRITICAL REGENERATION RULES:
1. MUST preserve the exact {theme} theme styling - analyze existing sections first
2. MUST maintain consistent design patterns with other sections
3. MUST use the same CSS classes and color scheme as existing content
4. Content can be updated, but design MUST match existing sections perfectly
5. When referencing images: use relative path ../filename.jpg
6. NO deviation from established visual patterns

PRESERVE FUNCTIONALITY (MANDATORY):
- Maintain all navigation links and smooth scrolling functionality
- Keep mobile hamburger menu toggle intact: onclick="toggleMobileMenu()" with proper JavaScript function
- Preserve all section IDs for navigation (id="hero", id="features", etc.)
- Maintain responsive breakpoints: sm:, md:, lg: classes throughout
- Keep form actions and CTA functionality working
- Preserve all hover states and keyboard accessibility
- Maintain smooth scrolling CSS: html {{ scroll-behavior: smooth; }}

PRESERVE ANIMATION SYSTEM (MANDATORY):
- Keep all existing animation CSS keyframes (@keyframes fadeInUp, slideDown, etc.)
- Maintain animation toggle button and localStorage functionality
- Preserve data-animate attributes on sections
- Keep IntersectionObserver setup for scroll-triggered animations
- Maintain animation controller JavaScript (init, toggle, detectSections functions)
- Preserve @media (prefers-reduced-motion) accessibility rules
- Keep animation timing and stagger delays intact
- Maintain per-section animation controls

CRITICAL: Output ONLY the HTML sections with START/END markers.
Do NOT include any explanations, descriptions, or markdown formatting.
Do NOT output a complete HTML document - just the requested sections.'''


def editgen_prompt(product_desc, framework, theme, edit_instruction, existing_context=None, affected_sections=None) -> str:
    """Smart targeted editing that preserves design theme and layout while making specific changes"""
    context_analysis = ""
    if existing_context:
        context_analysis = "\n".join(
            f"- {k}: {v[:60]}..." if isinstance(v,str) else f"- {k}: {v}"
            for k,v in existing_context.items()
        )
    
    affected_sections_text = ""
    if affected_sections:
        affected_sections_text = f"Focus changes on these sections: {', '.join(affected_sections)}"
    
    # Get theme-specific design rules (same as regeneration)
    theme_rules = ""
    if theme == "brutalist":
        theme_rules = """
BRUTALIST THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Use ONLY these colors: bg-black, bg-white, bg-red-600, bg-yellow-400
- Use ONLY these text styles: font-black, font-bold, uppercase, tracking-tight, tracking-wide
- REQUIRED classes on ALL sections: brutalist-border, brutalist-shadow
- Typography: JetBrains Mono font (already loaded)
- NO rounded corners, NO gradients, NO soft shadows
- Use sharp, geometric layouts with high contrast
- All buttons MUST have: brutalist-border brutalist-shadow hover:translate-x-1 hover:translate-y-1 hover:shadow-none
- All text MUST be UPPERCASE where appropriate
- Color combinations: black text on white/yellow, white text on black/red"""
    elif theme == "minimal":
        theme_rules = """
MINIMAL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Use neutral colors: bg-white, bg-gray-50, bg-gray-100, text-gray-900, text-gray-600
- Typography: font-normal, font-medium, font-semibold (NO font-black)
- Generous whitespace: py-16, py-24, space-y-8, space-y-12
- Subtle borders: border border-gray-200, rounded-lg
- Clean buttons: bg-blue-600, hover:bg-blue-700, rounded-md, px-6 py-3
- Minimal shadows: shadow-sm, shadow-md
- Simple layouts with lots of breathing room"""
    elif theme == "playful":
        theme_rules = """
PLAYFUL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Bright colors: bg-pink-500, bg-purple-500, bg-blue-500, bg-yellow-400, bg-green-500
- Rounded elements: rounded-xl, rounded-2xl, rounded-full
- Fun typography: font-bold, font-extrabold
- Organic shapes and bouncy animations: hover:scale-105, transition-transform
- Colorful gradients: bg-gradient-to-r from-pink-500 to-purple-500
- Playful spacing and asymmetrical layouts"""
    elif theme == "corporate":
        theme_rules = """
CORPORATE THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Professional colors: bg-blue-900, bg-gray-800, bg-white, text-blue-900
- Conservative typography: font-medium, font-semibold
- Structured layouts: grid system, even spacing
- Subtle shadows: shadow-lg, shadow-xl
- Professional buttons: bg-blue-600, hover:bg-blue-700
- Clean, trustworthy design patterns"""
    elif theme == "terminal":
        theme_rules = """
TERMINAL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Matrix colors: bg-black, bg-gray-900, text-green-400, text-green-300
- Monospace font: font-mono (already loaded)
- Terminal aesthetics: border-green-500, bg-green-500/10
- Command-line elements: $ prompts, code blocks
- Pixelated/blocky design: sharp edges, no rounded corners
- Glowing effects: animate-pulse, text-green-400"""
    elif theme == "dark":
        theme_rules = """
DARK THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Dark backgrounds: bg-gray-900, bg-gray-800, bg-black
- Light text: text-white, text-gray-100, text-gray-300
- Dark accent colors: bg-blue-600, bg-purple-600, bg-indigo-600
- Subtle borders: border-gray-700, border-gray-600
- High contrast for accessibility"""
    elif theme == "morphism":
        theme_rules = """
MORPHISM THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Soft backgrounds: bg-gray-100, bg-white, bg-gradient-to-br
- Glass effects: backdrop-blur-sm, bg-white/20, border border-white/20
- Soft shadows: shadow-xl, shadow-2xl with blur
- Rounded corners: rounded-xl, rounded-2xl
- Subtle colors with transparency: bg-blue-500/10, text-gray-700"""
    else:
        theme_rules = f"Follow {theme} theme guidelines with appropriate colors and styling"
    
    return f'''You are a precision content editor for existing landing pages.

Product: {product_desc}
Framework: {framework}
Theme: {theme}
Edit Request: {edit_instruction}

Existing Context:
{context_analysis or "No specific context provided"}

{affected_sections_text}

{theme_rules}

EDIT INSTRUCTION:
{edit_instruction}

CRITICAL EDITING RULES:
1. PRESERVE DESIGN THEME - The {theme} theme styling MUST remain unchanged
2. PRESERVE LAYOUT - Overall page structure and visual hierarchy must stay intact
3. PRESERVE FUNCTIONALITY - All navigation, forms, CTAs, and interactions must work
4. PRESERVE ANIMATIONS - All existing animation systems must remain functional
5. MAKE ONLY REQUESTED CHANGES - Change only what was specifically requested
6. MAINTAIN CONSISTENCY - Any new content must match existing design patterns exactly

WHAT TO PRESERVE (MANDATORY):
- All CSS classes, color schemes, and styling patterns from the {theme} theme
- Navigation system: navbar, mobile menu, smooth scrolling, section IDs
- Responsive breakpoints and mobile compatibility
- Form functionality and CTA links
- Animation system: keyframes, JavaScript controllers, data attributes
- Section markers (<!-- START: section_name --> and <!-- END: section_name -->)
- Overall visual hierarchy and spacing

WHAT YOU CAN CHANGE:
- Text content, copy, and messaging (while maintaining tone and theme)
- Images and their alt text (using relative paths ../filename.jpg)
- Content structure within sections (while preserving layout patterns)
- Add/remove content elements if explicitly requested
- Adjust specific styling only if explicitly requested

CRITICAL FUNCTIONALITY PRESERVATION:
- Navigation: Keep all href="#section" links working
- Mobile Menu: Maintain onclick="toggleMobileMenu()" with proper JavaScript function
- Smooth Scrolling: Keep html {{ scroll-behavior: smooth; }} CSS
- Form Actions: Preserve all form action="#" method="POST" attributes
- Button Interactions: Maintain all hover states and onclick events
- Section IDs: Keep all id attributes for navigation (id="hero", id="features", etc.)
- Animation Controls: Preserve animation toggle functionality and localStorage
- Accessibility: Maintain ARIA labels, alt text, and keyboard navigation

OUTPUT FORMAT:
Generate the complete, updated HTML document with your changes.
Start with <!DOCTYPE html> and end with </html>.
Include all preserved functionality and styling.
Do NOT add explanations or describe your changes.
Your response should be the updated HTML code only.'''


def editgen_sections_prompt(product_desc, framework, theme, edit_instruction, affected_sections, sections_html) -> str:
    """Lightweight section-only editing - much faster than full page regeneration"""
    
    return f'''Edit these sections based on the instruction. PRESERVE all theme styling.

Product: {product_desc}
Theme: {theme} (MUST preserve all theme CSS classes and styling)
Edit Request: {edit_instruction}
Sections: {", ".join(affected_sections)}

CURRENT SECTIONS:
{sections_html}

CRITICAL RULES:
1. PRESERVE ALL theme styling - do NOT change CSS classes, colors, fonts
2. PRESERVE section markers (<!-- START/END -->)  
3. PRESERVE functionality (IDs, navigation, forms, animations)
4. ONLY change text content, copy, messaging as requested
5. Keep exact same layout structure and visual hierarchy

Output ONLY the edited sections with their markers:
<!-- START: section_name -->
... section with only text/content changes ...
<!-- END: section_name -->'''


def form_on_prompt(product_desc: str, existing_html: str, detected_theme: str) -> str:
    """Generate concise prompt for adding contact form with correct placement"""
    return f'''Add a professional contact form to the landing page below. 
Theme: {detected_theme}

PRODUCT:
{product_desc}

CURRENT HTML:
{existing_html}

REQUIREMENTS:
1. PRESERVE DESIGN:
   - Do NOT edit existing text, images, layout, or styles
   - Only ADD form code (HTML/CSS/JS)
   - Keep all existing features (nav, CTAs, menus, animations)

2. FORM:
   - Fields: Name, Email, Message
   - Analyze the HTML and place form in the correct section:
     * Contact → inside contact section
     * Footer → if no dedicated contact section
     * Hero → if form is meant to capture leads quickly
   - Semantic HTML with labels, placeholders, accessibility
   - Required attributes + simple JS validation

3. THEME:
   - Match {detected_theme} style (colors, fonts, spacing)
   - Seamlessly integrate into visual hierarchy

4. RESPONSIVE:
   - Mobile, tablet, desktop friendly
   - Proper spacing at all sizes

5. FUNCTION:
   - action="#" method="POST"
   - JS validation + success message
   - Hover/focus states

6. ACCESSIBILITY:
   - ARIA labels, associations
   - Keyboard navigation
   - Contrast ratios + screen reader friendly

OUTPUT:
Return full HTML starting with <!DOCTYPE html> and ending with </html>. 
No explanations, only updated code.'''

def form_off_prompt(existing_html: str) -> str:
    """Generate concise prompt for removing all forms from landing page"""
    return f'''Remove all forms from the landing page below while keeping design and functionality intact.

CURRENT HTML:
{existing_html}

REQUIREMENTS:
- Do NOT alter existing design, text, images, layout, or non-form features
- Delete all <form> elements, inputs, textareas, selects, and related JS/CSS
- Keep non-form buttons (CTAs, nav, etc.)
- Clean unused form-specific CSS/JS and empty containers
- Maintain section structure, spacing, and layout integrity

OUTPUT:
Return the full HTML (<!DOCTYPE html> … </html>) with forms removed.
Only output updated code, no explanations.'''


def form_edit_prompt(existing_html: str, form_type: str, fields: list, style: str = None, cta: str = None, detected_theme: str = "minimal") -> str:
    """Prompt for inserting/editing forms with correct placement in landing page"""
    field_descriptions = {
        'name': 'Full name',
        'email': 'Email address',
        'phone': 'Phone number',
        'message': 'Message textarea',
        'company': 'Company/organization',
        'website': 'Website URL',
        'subject': 'Subject line'
    }

    fields_list = ', '.join([field_descriptions.get(field, field) for field in fields])
    cta_text = cta or "Submit"
    style_context = f" ({style} style)" if style else ""

    return f'''Insert a {form_type} form{style_context} into the landing page below.
Theme: {detected_theme}

CURRENT HTML:
{existing_html}

FORM DETAILS:
- Fields: {fields_list}
- CTA: "{cta_text}"
- Style: {style or 'inline (embedded)'}

PLACEMENT RULES:
- Analyze the HTML structure to find the correct section:
  * Contact → place in contact section
  * Newsletter → place in hero/footer
  * Signup → place prominently (hero or dedicated signup area)
- Replace old forms if present, otherwise insert into the right section
- Preserve existing design and styling (do not alter theme)

OTHER RULES:
- Use semantic HTML with validation + accessibility
- Keep responsive behavior
- Form action="#" method="POST"
- Show success/error messages

OUTPUT:
Return the full HTML (<!DOCTYPE html> … </html>) with the form correctly placed.
Only output updated code, no explanations.'''