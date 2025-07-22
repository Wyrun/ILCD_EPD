import pandas as pd
import os
import codecs
import re

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
|===

[cols="1,1,1,1,1,1,2,2,4,1,1,2,3,3,3,3,1,1,1,1,1,1,1,3,1,1,1,1,1,1", options="header", frame="all", grid="all"]
|===
| [role="title"]#order#
| [role="title"]#Question#
| [role="title"]#Changes observed by editors#
| [role="title"]#ID previous - check if correct#
| [role="title"]#ID new#
| [role="title"]#Format version ID - meaning? When issued the first time?#
| [role="title"]#Field Name (de)#
| [role="title"]#Field Name (en)#
| [role="title"]#Element/Attribute Name#
| [role="title"]#Technically Required#
| [role="title"]#Occ.#
| [role="title"]#Datatype#
| [role="title"]#Definition (de)#
| [role="title"]#Original ILCD Format Definition (en)#
| [role="title"]#IndData Definition (en) - new ones#
| [role="title"]#InData / ÖKOBAUDAT Definition and explanation (EN) - old ones#
| [role="title"]#InData compliance CP-2020#
| [role="title"]#ECO Platform conformity#
| [role="title"]#ÖKOBAUDAT conformity#
| [role="title"]#Deviation to ILCD format definition (see FAQ)#
| [role="title"]#Extension of ILCD format#
| [role="title"]#InData Compliance Construction Products CPEN2020#
| [role="title"]#eDoc ID#
| [role="title"]#Example of expected information in the field#
| [role="title"]#EN15804+A2 mapping (chapter number)#
| [role="title"]#EN15804+A2 required information#
| [role="title"]#ISO 22057 mapping (GUID)#
| [role="title"]#ISO 22057 required information#
| [role="title"]#ISO 21930 mapping#
| [role="title"]#ISO 21930 required information#
"""

# --- Helper Functions ---

def clean_text(text):
    """Cleans and formats text for AsciiDoc, handling empty cells and newlines."""
    if pd.isna(text):
        return '{nbsp}'
    # Convert to string, replace literal newlines with AsciiDoc line breaks, and strip whitespace
    cleaned = str(text).replace('\r', '').replace('\n', ' +\n')
    return cleaned.strip() if cleaned.strip() else '{nbsp}'

def get_role_from_order(order):
    """Determines the role based on the 'order' column."""
    if pd.isna(order):
        return 'fieldname' # Default role
    order_str = str(order)
    if '.' not in order_str:
        return 'root'
    return 'fieldname'

# --- Main Conversion Logic ---

def convert_xlsx_to_adoc(xlsx_path, output_path_combined):
    """Converts data from an XLSX sheet to a single combined AsciiDoc file."""
    data_sheet_name = 'ILCD EPD Format v1.3 Doc'
    try:
        df = pd.read_excel(xlsx_path, sheet_name=data_sheet_name)
    except Exception as e:
        print(f"Error reading sheet '{data_sheet_name}' from {xlsx_path}: {e}")
        return None

    combined_rows = []

    for index, row in df.iterrows():
        role = get_role_from_order(row.get('order'))

        # Build a row with all columns from the DataFrame
        row_parts = [f"[role=\"{role}\"]##{clean_text(row[col])}##" for col in df.columns]
        combined_rows.append(' | '.join(row_parts))

    with codecs.open(output_path_combined, 'w', 'utf-8') as f_out:
        f_out.write(COMBINED_HEADER_XLSX + '\n')
        f_out.write('\n'.join([f'| {row}' for row in combined_rows]))
        f_out.write('\n|===\n')
    print(f"Successfully generated {output_path_combined}")
    return df.columns

# --- Round-trip and Comparison Logic ---

def convert_adoc_to_xlsx(adoc_path, xlsx_path, columns):
    """Converts a combined AsciiDoc file back to an XLSX file."""
    with open(adoc_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = []
    table_content = []
    in_main_table = False
    table_def_found = False

    for line in lines:
        if line.startswith('[cols=') and 'options="header"' in line:
            table_def_found = True
            continue
        if table_def_found and line.strip() == '|===':
            in_main_table = True
            continue
        if in_main_table and line.strip() == '|===':
            break
        if in_main_table:
            table_content.append(line)

    full_table_str = ''.join(table_content)
    placeholder = "__NEWLINE__"
    full_table_str = full_table_str.replace(' +\n', placeholder)

    reconstructed_rows = full_table_str.splitlines()

    for row_line in reconstructed_rows:
        # Skip header lines and empty lines
        if '[role="title"]' in row_line or not row_line.strip():
            continue

        # Use regex to find all cell contents between ## markers.
        # This is more robust than splitting by '|'.
        raw_cells = re.findall(r'##(.*?)##', row_line, re.DOTALL)

        cleaned_cells = []
        for content in raw_cells:
            # Restore newlines and strip trailing ' +' from AsciiDoc multi-line syntax
            restored_content = content.replace(placeholder, '\n').rstrip(' +')
            if restored_content == '{nbsp}':
                cleaned_cells.append(None)
            else:
                cleaned_cells.append(restored_content)
        
        if cleaned_cells:
            # Ensure row has the correct number of columns, padding with None if necessary
            while len(cleaned_cells) < len(columns):
                cleaned_cells.append(None)
            data.append(cleaned_cells[:len(columns)]) # Truncate if there are too many

    if not data:
        print("Error: No data was extracted from the AsciiDoc file.")
        return False

    df = pd.DataFrame(data, columns=columns)
    df.to_excel(xlsx_path, index=False, sheet_name='ILCD EPD Format v1.3 Doc')
    print(f"Successfully generated round-trip file {xlsx_path}")
    return True

def compare_xlsx_files(original_path, new_path, log_path):
    """Compares two XLSX files and logs differences."""
    df_orig = pd.read_excel(original_path, sheet_name='ILCD EPD Format v1.3 Doc').fillna('')
    df_new = pd.read_excel(new_path, sheet_name='ILCD EPD Format v1.3 Doc').fillna('')

    diff_count = 0
    with open(log_path, 'w', encoding='utf-8') as log_file:
        if not df_orig.shape == df_new.shape:
            log_file.write(f"Shape mismatch: Original {df_orig.shape}, New {df_new.shape}\n")
            return

        for r_idx in range(df_orig.shape[0]):
            for c_idx in range(df_orig.shape[1]):
                orig_val = df_orig.iat[r_idx, c_idx]
                new_val = df_new.iat[r_idx, c_idx]

                # Normalize values for comparison
                orig_str = str(orig_val).strip().replace('\r\n', '\n')
                new_str = str(new_val).strip().replace('\r\n', '\n')

                # Treat float versions of integers as the same (e.g., '1.0' == '1')
                if orig_str.endswith('.0'):
                    orig_str = orig_str[:-2]
                if new_str.endswith('.0'):
                    new_str = new_str[:-2]

                if orig_str != new_str:
                    col_name = df_orig.columns[c_idx]
                    log_file.write(f"Difference at Row {r_idx + 2}, Column '{col_name}':\n")
                    log_file.write(f"  Original: '{orig_val}'\n")
                    log_file.write(f"  New     : '{new_val}'\n\n")
                    diff_count += 1
    
    if diff_count == 0:
        print("Comparison complete: No differences found.")
        with open(log_path, 'w', encoding='utf-8') as log_file:
            log_file.write("Comparison complete: No differences found.")
    else:
        print(f"Comparison complete: Found {diff_count} differences. See {log_path} for details.")

def main():
    XLSX_FILE = 'EPD_DataSet.xlsx'
    OUTPUT_FILE_COMBINED = 'epd_documentation_from_xlsx_combined.adoc'
    ROUNDTRIP_XLSX_FILE = 'roundtrip.xlsx'
    LOG_FILE = 'comparison_log.txt'

    script_dir = os.path.dirname(os.path.abspath(__file__))
    xlsx_path = os.path.join(script_dir, XLSX_FILE)
    output_path_combined = os.path.join(script_dir, OUTPUT_FILE_COMBINED)
    roundtrip_xlsx_path = os.path.join(script_dir, ROUNDTRIP_XLSX_FILE)
    log_path = os.path.join(script_dir, LOG_FILE)

    # Step 1: Convert XLSX to lossless AsciiDoc
    original_columns = convert_xlsx_to_adoc(xlsx_path, output_path_combined)

    if original_columns is not None:
        # Step 2: Convert AsciiDoc back to XLSX
        success = convert_adoc_to_xlsx(output_path_combined, roundtrip_xlsx_path, original_columns)

        # Step 3: Compare the two XLSX files only if the roundtrip file was created
        if success:
            compare_xlsx_files(xlsx_path, roundtrip_xlsx_path, log_path)

if __name__ == '__main__':
    main()
