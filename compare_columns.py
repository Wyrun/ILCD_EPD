#!/usr/bin/env python3
"""
Compare columns between Excel source and generated AsciiDoc/HTML to identify missing columns.
"""

import pandas as pd
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# File paths
EXCEL_FILE = os.path.join(DATA_DIR, 'ILCD_Format_Documentation_v1.3_2025-10-16_final_for_InData-Meeting.xlsx')
ADOC_FILE = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')
HTML_FILE = os.path.join(BASE_DIR, 'docs', 'epd_documentation_report.html')

print("="*80)
print("COLUMN COMPARISON ANALYSIS")
print("="*80)

# Step 1: Read Excel columns
print("\n1. Reading Excel file columns...")
try:
    excel_df = pd.read_excel(EXCEL_FILE, sheet_name='ILCD EPD Format v1.3 Doc', header=0, nrows=0)
    excel_columns = list(excel_df.columns)
    print(f"   Found {len(excel_columns)} columns in Excel")
    print("\n   Excel columns:")
    for i, col in enumerate(excel_columns, 1):
        print(f"   {i:2d}. {col}")
except Exception as e:
    print(f"   ERROR reading Excel: {e}")
    excel_columns = []

# Step 2: Read AsciiDoc columns
print("\n2. Reading AsciiDoc file columns...")
try:
    with open(ADOC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the table header
    table_match = re.search(r'options="header"\].*?\|===(.*?)\n\n', content, re.DOTALL)
    if table_match:
        table_content = table_match.group(1)
        # Extract headers (first set of cells after |===)
        header_cells = re.findall(r'\[role="title"\]##(.*?)##', table_content)
        adoc_columns = header_cells
        print(f"   Found {len(adoc_columns)} columns in AsciiDoc")
        print("\n   AsciiDoc columns:")
        for i, col in enumerate(adoc_columns, 1):
            print(f"   {i:2d}. {col}")
    else:
        print("   ERROR: Could not find table in AsciiDoc")
        adoc_columns = []
except Exception as e:
    print(f"   ERROR reading AsciiDoc: {e}")
    adoc_columns = []

# Step 3: Read HTML columns (from presentation columns in generate_html_report.py)
print("\n3. Checking HTML presentation columns...")
try:
    with open(os.path.join(BASE_DIR, 'scripts', 'generate_html_report.py'), 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # Find PRESENTATION_COLUMNS definition
    match = re.search(r'PRESENTATION_COLUMNS = \[(.*?)\]', script_content, re.DOTALL)
    if match:
        cols_text = match.group(1)
        html_columns = re.findall(r"'([^']+)'", cols_text)
        print(f"   Found {len(html_columns)} columns in HTML presentation")
        print("\n   HTML presentation columns:")
        for i, col in enumerate(html_columns, 1):
            print(f"   {i:2d}. {col}")
    else:
        print("   ERROR: Could not find PRESENTATION_COLUMNS")
        html_columns = []
except Exception as e:
    print(f"   ERROR reading HTML script: {e}")
    html_columns = []

# Step 4: Compare and identify missing columns
print("\n" + "="*80)
print("COMPARISON RESULTS")
print("="*80)

# Columns in Excel but not in AsciiDoc
missing_in_adoc = set(excel_columns) - set(adoc_columns)
if missing_in_adoc:
    print(f"\n❌ MISSING IN ASCIIDOC ({len(missing_in_adoc)} columns):")
    for col in sorted(missing_in_adoc):
        print(f"   - {col}")
else:
    print("\n✅ All Excel columns are present in AsciiDoc")

# Columns in AsciiDoc but not in Excel
extra_in_adoc = set(adoc_columns) - set(excel_columns)
if extra_in_adoc:
    print(f"\n⚠️  EXTRA IN ASCIIDOC ({len(extra_in_adoc)} columns):")
    for col in sorted(extra_in_adoc):
        print(f"   - {col}")

# Columns in Excel but not in HTML presentation
missing_in_html = set(excel_columns) - set(html_columns)
if missing_in_html:
    print(f"\n❌ MISSING IN HTML PRESENTATION ({len(missing_in_html)} columns):")
    for col in sorted(missing_in_html):
        print(f"   - {col}")
else:
    print("\n✅ All Excel columns are presented in HTML")

# Step 5: Detailed column mapping
print("\n" + "="*80)
print("DETAILED COLUMN MAPPING")
print("="*80)
print(f"\n{'Excel Column':<50} {'In AsciiDoc':<15} {'In HTML':<15}")
print("-"*80)

for col in excel_columns:
    in_adoc = "✅ YES" if col in adoc_columns else "❌ NO"
    in_html = "✅ YES" if col in html_columns else "❌ NO"
    print(f"{col:<50} {in_adoc:<15} {in_html:<15}")

# Step 6: Summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)
print(f"Excel columns:           {len(excel_columns)}")
print(f"AsciiDoc columns:        {len(adoc_columns)}")
print(f"HTML presentation cols:  {len(html_columns)}")
print(f"Missing in AsciiDoc:     {len(missing_in_adoc)}")
print(f"Missing in HTML:         {len(missing_in_html)}")
print(f"Extra in AsciiDoc:       {len(extra_in_adoc)}")

# Step 7: Check if column order matches
print("\n" + "="*80)
print("COLUMN ORDER CHECK")
print("="*80)

# Compare order for columns that exist in both
common_cols = [col for col in excel_columns if col in adoc_columns]
adoc_order = [col for col in adoc_columns if col in excel_columns]

if common_cols == adoc_order:
    print("✅ Column order matches between Excel and AsciiDoc")
else:
    print("⚠️  Column order differs between Excel and AsciiDoc")
    print("\nFirst 10 columns comparison:")
    print(f"{'Excel':<50} {'AsciiDoc':<50}")
    print("-"*100)
    for i in range(min(10, len(common_cols), len(adoc_order))):
        excel_col = common_cols[i] if i < len(common_cols) else "---"
        adoc_col = adoc_order[i] if i < len(adoc_order) else "---"
        match = "✅" if excel_col == adoc_col else "❌"
        print(f"{excel_col:<50} {adoc_col:<50} {match}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
