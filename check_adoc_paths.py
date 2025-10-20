#!/usr/bin/env python3
"""
Check if the AsciiDoc file has proper Path information
"""

import pandas as pd
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ADOC_FILE = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')

with open(ADOC_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the table
table_match = re.search(r'options="header"\].*?\|===(.*)\|===', content, re.DOTALL)
if not table_match:
    print("ERROR: Could not find table in AsciiDoc file!")
    exit(1)

table_str = table_match.group(1).strip()

# Extract headers
header_match = re.search(r'(\| \[role="title"\]##.*?##\n)+', table_str)
header_str = header_match.group(0)
headers = [h.strip() for h in re.findall(r'##(.*?)##', header_str)]

print(f"Headers found: {len(headers)}")
print("Column names:")
for i, h in enumerate(headers):
    print(f"  {i}: {h}")

# Check if Path column exists
if 'Path' in headers:
    print("\n✓ Path column EXISTS in AsciiDoc!")
    path_idx = headers.index('Path')
    print(f"  Position: {path_idx}")
else:
    print("\n✗ Path column NOT FOUND in AsciiDoc!")
    exit(1)

# Parse some data rows
body_str = table_str[len(header_str):].strip()
cells = [c.strip() for c in re.findall(r'##(.*?)##', body_str, re.DOTALL)]

num_cols = len(headers)
element_idx = headers.index('Element/Attribute Name')
indent_idx = headers.index('Indent') if 'Indent' in headers else None

print(f"\nFirst 20 rows (Element Name, Indent, Path):")
print(f"{'Element/Attribute Name':<40} {'Indent':<8} {'Path':<50}")
print("-" * 100)

for i in range(0, min(20 * num_cols, len(cells)), num_cols):
    row = cells[i:i+num_cols]
    element = row[element_idx].replace('{nbsp}', '').strip()
    indent = row[indent_idx] if indent_idx else "?"
    path = row[path_idx]
    
    print(f"{element:<40} {str(indent):<8} {path:<50}")

print("\n" + "="*100)
print("Analysis:")
if any(cells[i+path_idx] for i in range(0, min(20 * num_cols, len(cells)), num_cols)):
    print("✓ Path column has data!")
else:
    print("✗ Path column exists but is EMPTY!")
