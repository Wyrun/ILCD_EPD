#!/usr/bin/env python3
"""
Simple script to inspect column structure
"""

import re
import os

# Define base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

ADOC_SOURCE_FILE = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')

def main():
    with open(ADOC_SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the table section
    table_match = re.search(r'\.EPD Data Structure\n.*?\|===(.*?)(\|===)', content, re.DOTALL)
    if not table_match:
        print("Could not find table")
        return
    
    table_content = table_match.group(1).strip()
    
    # Parse the header
    header_match = re.search(r'(\| \[role="title"\]##.*?##\n)+', table_content)
    if not header_match:
        print("Could not parse header")
        return
    
    header_str = header_match.group(0)
    headers = [h.strip() for h in re.findall(r'##(.*?)##', header_str)]
    
    print(f"Found {len(headers)} columns:")
    for i, header in enumerate(headers):
        print(f"  {i}: {header}")
    
    # Look for definition-related columns
    print("\nDefinition-related columns:")
    for i, header in enumerate(headers):
        if 'definition' in header.lower() or 'Definition' in header:
            print(f"  {i}: {header}")

if __name__ == "__main__":
    main()
