"""
Project Management Module

Provides project discovery and selection utilities for CCUX.
Handles output directory management and project metadata extraction.
"""

import os
import json
import re
import time
from typing import List, Dict, Any


def get_next_available_output_dir() -> str:
    """Find the next available output directory"""
    # Check base 'output' directory first
    if not os.path.exists("output"):
        return "output"
    
    # If output exists, check output1, output2, etc.
    for i in range(1, 100):  # Support up to 99 projects
        output_dir = f"output{i}"
        if not os.path.exists(output_dir):
            return output_dir
    
    # Fallback if somehow we have 100+ projects
    return f"output-{int(time.time())}"


def discover_existing_projects() -> List[Dict[str, str]]:
    """Discover all existing CCUX projects in current directory
    Only includes projects with both index.html and design_analysis.json
    """
    projects = []
    
    # Check for output directory
    if (os.path.exists("output") and 
        os.path.exists(os.path.join("output", "index.html")) and
        os.path.exists(os.path.join("output", "design_analysis.json"))):
        project_name = extract_project_name_from_dir("output")
        projects.append({
            "directory": "output",
            "name": project_name,
            "path": os.path.join("output", "index.html")
        })
    
    # Check for output1, output2, etc.
    for i in range(1, 100):
        output_dir = f"output{i}"
        if (os.path.exists(output_dir) and 
            os.path.exists(os.path.join(output_dir, "index.html")) and
            os.path.exists(os.path.join(output_dir, "design_analysis.json"))):
            project_name = extract_project_name_from_dir(output_dir)
            projects.append({
                "directory": output_dir,
                "name": project_name,
                "path": os.path.join(output_dir, "index.html")
            })
    
    return projects


def extract_project_name_from_dir(output_dir: str) -> str:
    """Extract project name from design analysis or HTML content"""
    try:
        # Try to get from design_analysis.json first
        analysis_file = os.path.join(output_dir, "design_analysis.json")
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
                # Look for brand name or product description
                if 'brand_name' in analysis:
                    return analysis['brand_name'][:30]
                if 'product_description' in analysis:
                    return analysis['product_description'][:30] + "..."
        
        # Fallback: extract from HTML title or first heading
        html_file = os.path.join(output_dir, "index.html")
        if os.path.exists(html_file):
            with open(html_file, 'r') as f:
                content = f.read()
                # Try to extract title
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                if title_match:
                    return title_match.group(1)[:30]
                # Try to extract first h1
                h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
                if h1_match:
                    # Remove HTML tags
                    clean_text = re.sub(r'<[^>]+>', '', h1_match.group(1))
                    return clean_text[:30].strip()
    except:
        pass
    
    return f"Project in {output_dir}"


def validate_project_directory(project_dir: str) -> bool:
    """Validate that a directory contains a valid CCUX project"""
    required_files = ['index.html', 'design_analysis.json']
    return all(os.path.exists(os.path.join(project_dir, file)) for file in required_files)


def get_project_metadata(project_dir: str) -> Dict[str, Any]:
    """Extract metadata from project directory"""
    metadata = {}
    
    try:
        analysis_file = os.path.join(project_dir, "design_analysis.json")
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
                metadata.update(analysis)
    except:
        pass
    
    return metadata


def create_output_directory(output_dir: str) -> bool:
    """Create output directory if it doesn't exist"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        return True
    except:
        return False


def list_project_files(project_dir: str) -> List[str]:
    """List all files in a project directory"""
    try:
        return [f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]
    except:
        return []