#!/usr/bin/env python3
"""
Script to process definitions according to the following rules:
1. If 'Definition (en)' is '~', copy 'Original ILCD Format Definition (en)' into it
2. Mark rows where 'Definition (en)' == 'Original ILCD Format Definition (en)' for graying out
"""

import pandas as pd
import re
import os

# Define base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    
    if 'Indent' in df.columns:
        df['Indent'] = pd.to_numeric(df['Indent'], errors='coerce').fillna(0).astype(int)
    else:
        df['Indent'] = 0
        
    return df

def process_definitions(df, column_map):
    """Process definitions according to the specified rules."""
    
    # Use mapped column names
    definition_col = column_map.get('Definition (en)', 'Definition (en)')
    original_col = column_map.get('Original ILCD Format Definition (en)', 'Original ILCD Format Definition (en)')
    
    if definition_col not in df.columns:
        print(f"Column '{definition_col}' not found. Available columns: {list(df.columns)}")
        return df
    
    if original_col not in df.columns:
        print(f"Column '{original_col}' not found. Available columns: {list(df.columns)}")
        return df
    
    print(f"Processing definitions in columns '{definition_col}' and '{original_col}'...")
    
    # Count initial tilde entries
    tilde_count = (df[definition_col] == '~').sum()
    print(f"Found {tilde_count} entries with '~' in '{definition_col}'")
    
    # Step 1: Replace '~' in Definition (en) with Original ILCD Format Definition (en)
    mask_tilde = df[definition_col] == '~'
    df.loc[mask_tilde, definition_col] = df.loc[mask_tilde, original_col]
    
    replaced_count = mask_tilde.sum()
    print(f"Replaced {replaced_count} '~' entries with original definitions")
    
    # Step 2: Add a flag column to mark rows where definitions are identical
    # This will be used by the HTML generator to apply gray styling
    df['_definitions_identical'] = (
        df[definition_col].fillna('').str.strip() == 
        df[original_col].fillna('').str.strip()
    ) & (df[definition_col].fillna('').str.strip() != '')
    
    identical_count = df['_definitions_identical'].sum()
    print(f"Found {identical_count} rows where definitions are identical")
    

    
    
    return df

def write_asciidoc_table(df, filename):
    """Write the DataFrame back to AsciiDoc format."""
    print(f"Writing updated data to {filename}...")
    
    # Read the original file to preserve the header
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the table section
    table_match = re.search(r'(.*?\.EPD Data Structure\n.*?\|===)(.*?)(\|===.*)', content, re.DOTALL)
    if not table_match:
        raise ValueError("Could not find the table structure in the file.")
    
    before_table = table_match.group(1)
    after_table = table_match.group(3)
    
    # Generate the new table content
    table_content = "\n"
    
    # Write headers
    for header in df.columns:
        table_content += f"| [role=\"title\"]##{header}##\n"
    
    # Write data rows
    for _, row in df.iterrows():
        for col in df.columns:
            cell_value = str(row[col]) if not pd.isna(row[col]) else ''
            # Escape any existing ## in the content
            cell_value = cell_value.replace('##', '\\##')
            table_content += f"| ##{cell_value}##\n"
    
    # Combine everything
    new_content = before_table + table_content + after_table
    
    # Write back to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    """Main function to process definitions."""
    COLUMN_MAPPING = {
        'Definition (en)': 'IndData Definition (en)\u00a0- new ones',
        'Original ILCD Format Definition (en)': 'InData / ÖKOBAUDAT Definition and explanation (EN)\u00a0- old ones'
    }

    try:
        # Parse the current AsciiDoc data
        df = parse_asciidoc_table(ADOC_SOURCE_FILE)
        
        print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")
        
        # Process the definitions
        df_processed = process_definitions(df, COLUMN_MAPPING)
        
        # Write the updated data back to the file
        write_asciidoc_table(df_processed, ADOC_SOURCE_FILE)
        
        print(f"\nSuccessfully processed definitions in {ADOC_SOURCE_FILE}")
        print("- Replaced '~' entries with original definitions")
        print("- Added internal flag for identical definitions (for HTML styling)")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
