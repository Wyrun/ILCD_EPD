import pandas as pd
import os
import codecs
import re
from bs4 import BeautifulSoup

# --- AsciiDoc Header for Combined XLSX conversion ---

COMBINED_HEADER_XLSX = """= EPD Data Set Documentation (from XLSX)
:doctype: book
:stylesheet: ilcd.css
:source-highlighter: highlightjs

This document is generated from the EPD_DataSet.xlsx file.

.Namespace legend
[cols="1,1,3", frame="all", grid="rows"]
|===
| Information in the EPD namespace v1.1 is displayed with
| [role="fieldname_epd"]#blue background#
| (Namespace URI: "http://www.iai.kit.edu/EPD/2013", prefix "epd")

| Information in the EPD namespace v1.2 is displayed with
| [role="fieldname_epd2"]#purple background#
| (Namespace URI: "http://www.indata.network/EPD/2019", prefix "epd2")

| Information in the EPD namespace v1.3 is displayed with
| [role="fieldname_epd3"]#green background#
| (Namespace URI: "http://www.indata.network/EPD/2023", prefix "epd3")

| Information in the EPD namespace v1.4 is displayed with
| [role="fieldname_epd4"]#green background#
| (Namespace URI: "http://www.indata.network/EPD/2024", prefix "epd4")
|===

"""

# --- Helper Functions ---

def get_role_from_order(order_str):
    """Determines the role based on the 'Order' value."""
    if not order_str or pd.isna(order_str):
        return 'default'
    order_str = str(order_str)
    if '.' not in order_str:
        return 'default'
    main_level = order_str.split('.')[0]
    return f'epd_v{main_level}'

def clean_text(data):
    """Cleans text data for AsciiDoc compatibility."""
    if pd.isna(data):
        return '{nbsp}'
    text = str(data)
    # Escape pipe characters to prevent them from being interpreted as table column separators
    text = text.replace('|', '\\|')
    # Handle multi-line text for AsciiDoc tables
    if '\n' in text:
        text = text.replace('\n', ' +\n')
    return text

def get_indentation_map(html_path):
    """Parses the HTML file to extract indentation levels for each element."""
    indent_map = {}
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
        
        # Find the main data table by its ID
        table = soup.find('table', {'id': 'tableID'})
        if not table:
            print("Warning: Could not find table with id='tableID' in HTML.")
            return {}

        rows = table.find_all('tr')
        # Skip header row(s), find the first data row
        first_data_row_index = -1
        for i, row in enumerate(rows):
            if row.find('td'): # The first row with <td> is a data row
                first_data_row_index = i
                break
        
        if first_data_row_index == -1:
            return {}

        for row in rows[first_data_row_index:]:
            cells = row.find_all('td')
            if len(cells) > 2:
                element_cell = cells[2] # 'Element/Attribute Name' is the 3rd column
                element_name = element_cell.get_text(strip=True)

                # Determine indentation from the style of the first cell
                first_cell = cells[0]
                style = first_cell.get('style', '')
                match = re.search(r'padding-left:\s*(\d+)px', style)
                if match:
                    pixels = int(match.group(1))
                    indent_level = pixels // 10
                    indent_map[element_name] = indent_level
                else:
                    # Default to 0 if no padding is found (e.g., for the root element)
                    indent_map[element_name] = 0

    except FileNotFoundError:
        print(f"Warning: HTML file not found at {html_path}. Indentation will be 0.")
    except Exception as e:
        print(f"An error occurred while parsing HTML for indentation: {e}")
    
    return indent_map

# --- Core Conversion Functions ---

def convert_xlsx_to_adoc(xlsx_path, html_path, output_path):
    """Converts the XLSX file to a single combined AsciiDoc file with indentation."""
    try:
        df = pd.read_excel(xlsx_path, sheet_name='ILCD EPD Format v1.3 Doc', header=0)
    except FileNotFoundError:
        print(f"Error: XLSX file not found at {xlsx_path}")
        return False, None

    # Get indentation map from HTML
    indent_map = get_indentation_map(html_path)

    # Add 'Indent' column and populate it
    df['Indent'] = df['Element/Attribute Name'].map(indent_map).fillna(0).astype(int)

    # --- Build hierarchical path ---
    path_stack = {}
    paths = []
    for _, row in df.iterrows():
        indent = row['Indent']
        # Use a cleaned-up version for the path component
        name = str(row['Element/Attribute Name']).strip().replace(' ', '_')
        path_stack[indent] = name
        
        current_path = []
        for i in range(indent + 1):
            if i in path_stack:
                current_path.append(path_stack[i])
        paths.append('/'.join(current_path))
    df['Path'] = paths

    # Ensure 'Indent' and 'Path' are the last columns for clarity
    cols = [col for col in df.columns if col not in ['Indent', 'Path']] + ['Indent', 'Path']
    df = df[cols]

    original_columns = df.columns.tolist()

    with codecs.open(output_path, 'w', 'utf-8') as f:
        f.write(COMBINED_HEADER_XLSX)

        # Create AsciiDoc table
        col_str = ",".join(['1'] * len(original_columns))
        f.write(f'\n.EPD Data Structure\n')
        f.write(f'[cols="{col_str}", options="header"]\n')
        f.write('|===\n')

        # Write table header, one cell per line for consistency
        for col in original_columns:
            f.write(f'| [role="title"]##{col}##\n')

        # Write table rows, one cell per line
        for _, row in df.iterrows():
            f.write('\n') # Start each row with a blank line for separation
            for col_name in original_columns:
                cell_data = row[col_name]
                
                # Apply visual indentation to the 'Element/Attribute Name' column
                if col_name == 'Element/Attribute Name':
                    indent_level = row.get('Indent', 0)
                    indent_prefix = '{nbsp}' * 4 * indent_level
                    # Convert cell_data to string before concatenation
                    cleaned_data = indent_prefix + clean_text(cell_data)
                else:
                    cleaned_data = clean_text(cell_data)
                
                f.write(f'| ##{cleaned_data}##\n')

        f.write('|===\n')

    print(f"Successfully generated {output_path}")
    return True, original_columns

def convert_adoc_to_xlsx(adoc_path, xlsx_path, original_columns):
    """Converts a combined AsciiDoc file back to an XLSX file."""
    with open(adoc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the main table content
    table_match = re.search(r'options="header"\].*?\|===(.*)\|===', content, re.DOTALL)
    if not table_match:
        print("Error: Could not find main table in AsciiDoc file.")
        return False

    table_str = table_match.group(1).strip()
    
    # Use re.DOTALL to correctly handle multi-line content within cells
    raw_cells = re.findall(r'##(.*?)##', table_str, re.DOTALL)

    # The first N cells are the header, skip them.
    data_cells = raw_cells[len(original_columns):]

    if len(data_cells) % len(original_columns) != 0:
        print(f"Error: Cell count ({len(data_cells)}) is not a multiple of column count ({len(original_columns)}). File may be corrupt.")
        return False

    data = []
    element_attr_name_index = original_columns.index('Element/Attribute Name')
    num_cols = len(original_columns)

    # Reconstruct rows from the flat list of cells
    for i in range(0, len(data_cells), num_cols):
        row_cells = data_cells[i:i+num_cols]
        processed_cells = []
        for j, cell in enumerate(row_cells):
            # Restore newlines, un-escape pipes, and handle placeholders
            # The rstrip is crucial to remove the trailing ' +' from the last line of multi-line cells
            processed_cell = cell.rstrip(' ').rstrip('+').replace(' +\n', '\n').replace('\\|', '|')
            if processed_cell == '{nbsp}':
                processed_cell = None
            
            # Strip visual indentation from the specific column before comparison
            if j == element_attr_name_index and isinstance(processed_cell, str):
                processed_cell = re.sub(r'^(?:{nbsp})*', '', processed_cell)
            
            processed_cells.append(processed_cell)
        data.append(processed_cells)
    df = pd.DataFrame(data, columns=original_columns)
    df.to_excel(xlsx_path, index=False, sheet_name='ILCD EPD Format v1.3 Doc')
    print(f"Successfully generated round-trip file {xlsx_path}")
    return True

def compare_xlsx_files(file1, file2, log_file):
    """Compares two XLSX files and logs differences."""
    df1 = pd.read_excel(file1, sheet_name='ILCD EPD Format v1.3 Doc').fillna('').astype(str)
    df2 = pd.read_excel(file2, sheet_name='ILCD EPD Format v1.3 Doc').fillna('').astype(str)

    # Add 'Indent' column to original df for a fair comparison, as it's added during conversion
    if 'Indent' not in df1.columns and 'Indent' in df2.columns:
        # Find the position of 'Element/Attribute Name' to insert 'Indent' after it
        element_col_loc = df1.columns.get_loc('Element/Attribute Name')
        df1.insert(element_col_loc + 1, 'Indent', 0) # Default to 0 for comparison base
        # Now, populate it the same way the main script does to ensure a perfect match
        # Construct the path to the HTML file relative to the script's execution context
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(file1)))
        html_path = os.path.join(base_dir, 'data', 'EPD_DataSet.html')
        indent_map = get_indentation_map(html_path)
        df1['Indent'] = df1['Element/Attribute Name'].map(indent_map).fillna(0).astype(int).astype(str)

    # Ensure columns are in the same order, which is now guaranteed by the round-trip logic
    df2 = df2[df1.columns]

    # Manual, robust comparison to avoid metadata sensitivity
    num_diffs = 0
    with open(log_file, 'w', encoding='utf-8') as log:
        if df1.shape != df2.shape:
            log.write(f"Shape mismatch: Original {df1.shape}, New {df2.shape}\n")
            print(f"Comparison failed due to shape mismatch. See {log_file}.")
            return

        for r_idx in range(df1.shape[0]):
            for c_idx in range(df1.shape[1]):
                val1 = str(df1.iat[r_idx, c_idx]).strip()
                val2 = str(df2.iat[r_idx, c_idx]).strip()

                # Normalize for common data type differences (e.g., '1' vs '1.0')
                if val1.endswith('.0'): val1 = val1[:-2]
                if val2.endswith('.0'): val2 = val2[:-2]

                if val1 != val2:
                    num_diffs += 1
                    col_name = df1.columns[c_idx]
                    log.write(f"Difference at Row {r_idx + 2}, Column '{col_name}':\n")
                    log.write(f"  Original: '{df1.iat[r_idx, c_idx]}'\n")
                    log.write(f"  New     : '{df2.iat[r_idx, c_idx]}'\n\n")

    if num_diffs == 0:
        print("Comparison complete: No differences found.")
        with open(log_file, 'w') as f:
            f.write("Comparison complete: No differences found.")
    else:
        print(f"Comparison complete: Found {num_diffs} differences. See {log_file} for details.")
    return num_diffs

# --- Main Execution ---

if __name__ == "__main__":
    # Define base directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Define file paths - updated for new XLSX file
    xlsx_file = os.path.join(DATA_DIR, 'ILCD_Format_Documentation_v1.3_reformatted_final_2025-09-12.xlsx')
    html_file = os.path.join(DATA_DIR, 'EPD_DataSet.html') # Assuming this will be in data as well
    combined_adoc_file = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')
    roundtrip_xlsx_file = os.path.join(OUTPUT_DIR, 'roundtrip.xlsx')
    comparison_log_file = os.path.join(OUTPUT_DIR, 'comparison_log.txt')

    # Step 1: Convert XLSX to combined AsciiDoc
    success, columns = convert_xlsx_to_adoc(xlsx_file, html_file, combined_adoc_file)
    if success:
        # Step 2: Convert back to XLSX for verification
        if convert_adoc_to_xlsx(combined_adoc_file, roundtrip_xlsx_file, columns):
            # Step 3: Compare the original and round-tripped files
            compare_xlsx_files(xlsx_file, roundtrip_xlsx_file, comparison_log_file)
