#!/usr/bin/env python3
"""
Script to properly fix definitions by replacing '~' with original definitions
"""

import re
import os

# Define base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

ADOC_SOURCE_FILE = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')

def fix_definitions_in_adoc():
    """Fix definitions directly in the AsciiDoc file using regex."""
    print(f"Reading and processing {ADOC_SOURCE_FILE}...")
    
    with open(ADOC_SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the table section
    table_match = re.search(r'(.*?\.EPD Data Structure\n.*?\|===)(.*?)(\|===.*)', content, re.DOTALL)
    if not table_match:
        raise ValueError("Could not find the table structure in the file.")
    
    before_table = table_match.group(1)
    table_content = table_match.group(2)
    after_table = table_match.group(3)
    
    # Parse the header to find column positions
    header_match = re.search(r'(\| \[role="title"\]##.*?##\n)+', table_content)
    if not header_match:
        raise ValueError("Could not parse the table header.")
    
    header_str = header_match.group(0)
    headers = [h.strip() for h in re.findall(r'##(.*?)##', header_str)]
    
    print(f"Found {len(headers)} columns: {headers}")
    
    # Find the column indices
    try:
        definition_col_idx = headers.index('IndData Definition (en) - new ones')
        original_col_idx = headers.index('Original ILCD Format Definition (en)')
        print(f"IndData Definition (en) - new ones is column {definition_col_idx}")
        print(f"Original ILCD Format Definition (en) is column {original_col_idx}")
    except ValueError as e:
        print(f"Could not find required columns: {e}")
        print(f"Available columns: {headers}")
        return
    
    # Parse the table body
    body_str = table_content[len(header_str):].strip()
    cells = [c.strip() for c in re.findall(r'##(.*?)##', body_str, re.DOTALL)]
    
    num_columns = len(headers)
    
    if len(cells) % num_columns != 0:
        padding = num_columns - (len(cells) % num_columns)
        cells.extend([''] * padding)
    
    # Process rows and replace '~' with original definitions
    replacements_made = 0
    
    for i in range(0, len(cells), num_columns):
        row_cells = cells[i:i + num_columns]
        
        if len(row_cells) > max(definition_col_idx, original_col_idx):
            definition_cell = row_cells[definition_col_idx]
            original_cell = row_cells[original_col_idx]
            
            # If definition is '~', replace with original
            if definition_cell.strip() == '~':
                row_cells[definition_col_idx] = original_cell
                replacements_made += 1
                print(f"Replaced '~' with: {original_cell[:50]}...")
        
        # Update the cells list
        cells[i:i + num_columns] = row_cells
    
    print(f"Made {replacements_made} replacements")
    
    # Rebuild the table content
    new_table_content = "\n"
    
    # Write headers
    for header in headers:
        new_table_content += f"| [role=\"title\"]##{header}##\n"
    
    # Write data rows
    for i in range(0, len(cells), num_columns):
        row_cells = cells[i:i + num_columns]
        for cell in row_cells:
            # Escape any existing ## in the content
            cell_value = cell.replace('##', '\\##')
            new_table_content += f"| ##{cell_value}##\n"
    
    # Combine everything
    new_content = before_table + new_table_content + after_table
    
    # Write back to file
    with open(ADOC_SOURCE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully updated {ADOC_SOURCE_FILE}")
    return replacements_made

def main():
    """Main function."""
    try:
        replacements = fix_definitions_in_adoc()
        print(f"\nCompleted! Made {replacements} definition replacements.")
        
        # Verify by checking for remaining tildes
        with open(ADOC_SOURCE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        remaining_tildes = content.count('##~##')
        print(f"Remaining '~' entries: {remaining_tildes}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
