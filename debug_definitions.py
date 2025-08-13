#!/usr/bin/env python3
"""
Debug script to check for identical definitions
"""

import pandas as pd
import re
import os

# Define base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

ADOC_SOURCE_FILE = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')

def parse_asciidoc_table(filename):
    """Parses the main data table from an AsciiDoc file."""
    print(f"Reading data from {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    table_match = re.search(r'\.EPD Data Structure\n.*?\|===(.*?)(\|===)', content, re.DOTALL)
    if not table_match:
        raise ValueError("Could not find the '.EPD Data Structure' table in the AsciiDoc file.")

    table_content = table_match.group(1).strip()
    
    header_match = re.search(r'(\| \[role="title"\]##.*?##\n)+', table_content)
    if not header_match:
        raise ValueError("Could not parse the table header.")
        
    header_str = header_match.group(0)
    headers = [h.strip() for h in re.findall(r'##(.*?)##', header_str)]
    
    body_str = table_content[len(header_str):].strip()
    cells = [c.strip() for c in re.findall(r'##(.*?)##', body_str, re.DOTALL)]
    
    num_columns = len(headers)
    
    if len(cells) % num_columns != 0:
        padding = num_columns - (len(cells) % num_columns)
        cells.extend([''] * padding)
        
    rows = [cells[i:i + num_columns] for i in range(0, len(cells), num_columns)]
    
    df = pd.DataFrame(rows, columns=headers)
    df.replace('{nbsp}', '', regex=True, inplace=True)
    
    return df

def main():
    """Main function to debug definitions."""
    try:
        # Parse the current AsciiDoc data
        df = parse_asciidoc_table(ADOC_SOURCE_FILE)
        
        print(f"Loaded {len(df)} rows")
        
        # Check if required columns exist
        definition_col = 'Definition (en)'
        original_col = 'Original ILCD Format Definition (en)'
        
        if definition_col not in df.columns:
            print(f"Column '{definition_col}' not found. Available columns: {list(df.columns)}")
            return
        
        if original_col not in df.columns:
            print(f"Column '{original_col}' not found. Available columns: {list(df.columns)}")
            return
        
        print(f"\nChecking for identical definitions...")
        
        # Find rows where definitions are identical
        identical_count = 0
        for index, row in df.iterrows():
            definition_en = str(row[definition_col]).strip()
            original_definition_en = str(row[original_col]).strip()
            
            if (definition_en == original_definition_en) and (definition_en != '') and (definition_en != 'nan'):
                identical_count += 1
                if identical_count <= 5:  # Show first 5 examples
                    element_name = str(row.get('Element/Attribute Name', 'Unknown')).strip()
                    print(f"\nRow {index + 1}: {element_name}")
                    print(f"  Definition (en): '{definition_en}'")
                    print(f"  Original ILCD: '{original_definition_en}'")
                    print(f"  Identical: {definition_en == original_definition_en}")
        
        print(f"\nTotal identical definitions found: {identical_count}")
        
        # Also check for tilde entries that should have been replaced
        tilde_count = (df[definition_col] == '~').sum()
        print(f"Remaining '~' entries: {tilde_count}")
        
        if tilde_count > 0:
            print("Examples of remaining '~' entries:")
            tilde_rows = df[df[definition_col] == '~'].head(3)
            for index, row in tilde_rows.iterrows():
                element_name = str(row.get('Element/Attribute Name', 'Unknown')).strip()
                original_def = str(row[original_col]).strip()
                print(f"  Row {index + 1}: {element_name}")
                print(f"    Definition (en): '~'")
                print(f"    Original ILCD: '{original_def}'")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
