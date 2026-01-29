#!/usr/bin/env python3
"""Update all visual inspection sample HTML files with new professional colors."""
import re
from pathlib import Path

# Define color replacements (old -> new)
COLOR_REPLACEMENTS = {
    # Language badge: green -> blue
    'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)': 'linear-gradient(135deg, #4A90E2 0%, #357ABD 100%)',
    
    # Summary cards
    '#667eea 0%, #764ba2': '#5C6BC0 0%, #7986CB',  # Total: purple -> indigo
    '#11998e 0%, #38ef7d': '#66BB6A 0%, #81C784',  # Passed: teal -> soft green
    '#eb3349 0%, #f45c43': '#EF5350 0%, #E57373',  # Failed: bright red -> coral
    '#f2994a 0%, #f2c94c': '#FFA726 0%, #FFB74D',  # Skipped: yellow -> orange
    '#4facfe 0%, #00f2fe': '#42A5F5 0%, #64B5F6',  # Duration: cyan -> sky blue
    '#fa709a 0%, #fee140': '#9CCC65 0%, #AED581',  # Rate: pink-yellow -> light green
    
    # Badge colors
    'background-color: #17a2b8': 'background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%)',
}

def update_html_colors(html_content):
    """Replace old colors with new professional colors."""
    updated = html_content
    for old_color, new_color in COLOR_REPLACEMENTS.items():
        updated = updated.replace(old_color, new_color)
    return updated

# Update all visual inspection samples
samples_dir = Path('visual_inspection_samples')
if samples_dir.exists():
    html_files = list(samples_dir.glob('report_*.html'))
    print(f"Found {len(html_files)} HTML files to update")
    
    for html_file in html_files:
        print(f"Updating {html_file.name}...", end=' ')
        try:
            content = html_file.read_text(encoding='utf-8')
            updated_content = update_html_colors(content)
            html_file.write_text(updated_content, encoding='utf-8')
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n✅ Updated {len(html_files)} visual inspection samples")
else:
    print("❌ visual_inspection_samples directory not found")
