#!/usr/bin/env python3
"""
Verify that data from all Excel columns is actually present in the generated files.
"""

import pandas as pd
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# File paths
EXCEL_FILE = os.path.join(DATA_DIR, 'ILCD_Format_Documentation_v1.3_2025-10-16_final_for_InData-Meeting.xlsx')
ADOC_FILE = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')

print("="*80)
print("DATA VERIFICATION - Checking if Excel data is in AsciiDoc")
print("="*80)

# Read Excel data
print("\nReading Excel file...")
excel_df = pd.read_excel(EXCEL_FILE, sheet_name='ILCD EPD Format v1.3 Doc', header=0)
print(f"Excel has {len(excel_df)} rows and {len(excel_df.columns)} columns")

# Read AsciiDoc data
print("\nReading AsciiDoc file...")
with open(ADOC_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Parse AsciiDoc table
table_match = re.search(r'options="header"\].*?\|===(.*)\|===', content, re.DOTALL)
if not table_match:
    print("ERROR: Could not find table in AsciiDoc")
    exit(1)

table_str = table_match.group(1).strip()

# Extract all cells
cells = re.findall(r'##(.*?)##', table_str, re.DOTALL)

# First N cells are headers
num_cols = len([c for c in re.findall(r'\[role="title"\]##(.*?)##', table_str)])
headers = [re.sub(r'\[role="title"\]', '', cells[i]).strip() for i in range(num_cols)]

print(f"AsciiDoc has {num_cols} columns")

# Build DataFrame from AsciiDoc
data_cells = cells[num_cols:]
num_rows = len(data_cells) // num_cols

adoc_data = []
for i in range(num_rows):
    row = []
    for j in range(num_cols):
        cell_idx = i * num_cols + j
        if cell_idx < len(data_cells):
            cell_content = data_cells[cell_idx].replace('{nbsp}', '').strip()
            # Remove visual indentation
            cell_content = re.sub(r'^(?:{nbsp}\s*)*', '', cell_content)
            row.append(cell_content)
        else:
            row.append('')
    adoc_data.append(row)

adoc_df = pd.DataFrame(adoc_data, columns=headers)
print(f"AsciiDoc DataFrame has {len(adoc_df)} rows and {len(adoc_df.columns)} columns")

# Compare specific columns
print("\n" + "="*80)
print("COLUMN-BY-COLUMN DATA VERIFICATION")
print("="*80)

# Check each Excel column
missing_columns = []
columns_with_data_loss = []

for col in excel_df.columns:
    if col in adoc_df.columns:
        # Check if data matches
        excel_col_data = excel_df[col].fillna('').astype(str).str.strip()
        adoc_col_data = adoc_df[col].fillna('').astype(str).str.strip()
        
        # Count non-empty cells
        excel_non_empty = (excel_col_data != '').sum()
        adoc_non_empty = (adoc_col_data != '').sum()
        
        # Check for data loss
        if excel_non_empty > 0:
            if adoc_non_empty == 0:
                print(f"\n❌ '{col}':")
                print(f"   Excel: {excel_non_empty} non-empty cells")
                print(f"   AsciiDoc: {adoc_non_empty} non-empty cells")
                print(f"   STATUS: ALL DATA LOST")
                columns_with_data_loss.append(col)
            elif adoc_non_empty < excel_non_empty:
                print(f"\n⚠️  '{col}':")
                print(f"   Excel: {excel_non_empty} non-empty cells")
                print(f"   AsciiDoc: {adoc_non_empty} non-empty cells")
                print(f"   STATUS: PARTIAL DATA LOSS ({excel_non_empty - adoc_non_empty} cells lost)")
                columns_with_data_loss.append(col)
            else:
                print(f"\n✅ '{col}': {excel_non_empty} cells → {adoc_non_empty} cells (OK)")
        else:
            print(f"\n⚪ '{col}': Empty in Excel (OK)")
    else:
        print(f"\n❌ '{col}': COLUMN MISSING IN ASCIIDOC")
        missing_columns.append(col)

# Sample data comparison for a few key columns
print("\n" + "="*80)
print("SAMPLE DATA COMPARISON (First 3 rows)")
print("="*80)

sample_cols = ['Element/Attribute Name', 'Field Name (en)', 'Definition (de)', 'eDoc ID']
for col in sample_cols:
    if col in excel_df.columns and col in adoc_df.columns:
        print(f"\n{col}:")
        print("-" * 60)
        for i in range(min(3, len(excel_df))):
            excel_val = str(excel_df[col].iloc[i])[:50] if pd.notna(excel_df[col].iloc[i]) else "(empty)"
            adoc_val = str(adoc_df[col].iloc[i])[:50] if pd.notna(adoc_df[col].iloc[i]) else "(empty)"
            match = "✅" if excel_val == adoc_val else "❌"
            print(f"  Row {i+1}: {match}")
            print(f"    Excel:    {excel_val}")
            print(f"    AsciiDoc: {adoc_val}")

# Final summary
print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"Total Excel columns:              {len(excel_df.columns)}")
print(f"Columns missing in AsciiDoc:      {len(missing_columns)}")
print(f"Columns with data loss:           {len(columns_with_data_loss)}")
print(f"Columns correctly transferred:    {len(excel_df.columns) - len(missing_columns) - len(columns_with_data_loss)}")

if missing_columns:
    print(f"\n❌ Missing columns: {missing_columns}")

if columns_with_data_loss:
    print(f"\n⚠️  Columns with data loss: {columns_with_data_loss}")

if not missing_columns and not columns_with_data_loss:
    print("\n✅ ALL EXCEL COLUMNS AND DATA SUCCESSFULLY TRANSFERRED TO ASCIIDOC")
else:
    print("\n❌ ISSUES FOUND - DATA TRANSFER INCOMPLETE")

print("\n" + "="*80)
