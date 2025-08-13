#!/usr/bin/env python3
"""
Script to convert existing dot-separated paths to X-path style (forward slash) paths
and remove @ characters from paths while preserving them in element names.
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

def convert_path_to_xpath(path_str):
    """Convert dot-separated path to X-path style and remove @ characters."""
    if pd.isna(path_str) or str(path_str).strip() == '':
        return path_str
    
    # Convert to string and strip whitespace
    path = str(path_str).strip()
    
    # Replace dots with forward slashes
    path = path.replace('.', '/')
    
    # Remove @ characters from the path
    path = path.replace('@', '')
    
    return path

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
    """Main function to convert paths to X-path style."""
    try:
        # Parse the current AsciiDoc data
        df = parse_asciidoc_table(ADOC_SOURCE_FILE)
        
        print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")
        
        # Check if Path column exists
        if 'Path' not in df.columns:
            print("No 'Path' column found in the data. Nothing to convert.")
            return
        
        # Show some examples of current paths
        print("\nExample current paths:")
        for i, path in enumerate(df['Path'].head(10)):
            if pd.notna(path) and str(path).strip():
                print(f"  {i+1}: {path}")
        
        # Convert paths to X-path style
        print("\nConverting paths to X-path style...")
        df['Path'] = df['Path'].apply(convert_path_to_xpath)
        
        # Show some examples of converted paths
        print("\nExample converted paths:")
        for i, path in enumerate(df['Path'].head(10)):
            if pd.notna(path) and str(path).strip():
                print(f"  {i+1}: {path}")
        
        # Write the updated data back to the file
        write_asciidoc_table(df, ADOC_SOURCE_FILE)
        
        print(f"\nSuccessfully updated paths in {ADOC_SOURCE_FILE}")
        print("All dots (.) have been replaced with forward slashes (/)")
        print("All @ characters have been removed from paths")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
