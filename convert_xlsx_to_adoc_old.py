import pandas as pd
import os
import codecs

# --- AsciiDoc Headers for XLSX conversion ---

EN_HEADER_XLSX = """= EPD Data Set Documentation (from XLSX)
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

[cols="2,4,1,1,2,3,3,1,2,2,2", options="header", frame="all", grid="all"]
|===
| [role="title"]#Field Name (en)#
| [role="title"]#Element/Attribute Name#
| [role="title"]#Requ.#
| [role="title"]#Occ.#
| [role="title"]#Datatype#
| [role="title"]#Definition (en)#
| [role="title"]#Original ILCD Definition (en)#
| [role="title"]#eDoc ID#
| [role="title"]#EN15804+A2 mapping comment#
| [role="title"]#ISO 22057 GUID#
| [role="title"]#ISO 22057 mapping comment#
"""

DE_HEADER_XLSX = """= EPD Data Set Documentation (aus XLSX)
:doctype: book
:stylesheet: ilcd.css
:source-highlighter: highlightjs

Dieses Dokument wurde aus der Datei EPD_DataSet.xlsx generiert.

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

[cols="2,4,1,1,2,3,3,1,2,2,2", options="header", frame="all", grid="all"]
|===
| [role="title"]#Field Name (de)#
| [role="title"]#Element/Attribute Name#
| [role="title"]#Requ.#
| [role="title"]#Occ.#
| [role="title"]#Datatype#
| [role="title"]#Definition (de)#
| [role="title"]#Original ILCD Definition (en)#
| [role="title"]#eDoc ID#
| [role="title"]#EN15804+A2 mapping comment#
| [role="title"]#ISO 22057 GUID#
| [role="title"]#ISO 22057 mapping comment#
"""

# --- Helper Functions ---

def clean_text(text):
    """Cleans and formats text for AsciiDoc, handling empty cells."""
    if pd.isna(text):
        return '{nbsp}'
    # Replace non-breaking spaces with regular spaces before stripping
    cleaned = str(text).replace('\u00a0', ' ').strip()
    return cleaned if cleaned else '{nbsp}'

def get_role_from_order(order):
    """Determines the role based on the 'order' column."""
    if pd.isna(order):
        return 'fieldname' # Default role
    order_str = str(order)
    if '.' not in order_str:
        return 'root'
    return 'fieldname'

# --- Main Conversion Logic ---

def convert_xlsx_to_adoc(xlsx_path, output_path_en, output_path_de):
    """Converts data from an XLSX sheet to two separate AsciiDoc files."""
    data_sheet_name = 'ILCD EPD Format v1.3 Doc'
    try:
        df = pd.read_excel(xlsx_path, sheet_name=data_sheet_name)
    except Exception as e:
        print(f"Error reading sheet '{data_sheet_name}' from {xlsx_path}: {e}")
        return

    en_rows = []
    de_rows = []

    for index, row in df.iterrows():
        if pd.isna(row['Field Name (en)']) and pd.isna(row['Field Name (de)']):
            continue

        role = get_role_from_order(row.get('order'))

        en_row_parts = [
            f"[role=\"{role}\"]##{clean_text(row['Field Name (en)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Element/Attribute Name'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Technically Required'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Occ.'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Datatype'])}##",
            f"[role=\"{role}\"]##{clean_text(row['IndData Definition (en) - new ones'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Original ILCD Format Definition (en)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['eDoc ID'])}##",
            f"[role=\"{role}\"]##{clean_text(row['EN15804+A2 mapping (chapter number)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['ISO 22057 mapping (GUID)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['ISO 22057 required information'])}##"
        ]
        en_rows.append(' | '.join(en_row_parts))

        de_row_parts = [
            f"[role=\"{role}\"]##{clean_text(row['Field Name (de)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Element/Attribute Name'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Technically Required'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Occ.'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Datatype'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Definition (de)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['Original ILCD Format Definition (en)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['eDoc ID'])}##",
            f"[role=\"{role}\"]##{clean_text(row['EN15804+A2 mapping (chapter number)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['ISO 22057 mapping (GUID)'])}##",
            f"[role=\"{role}\"]##{clean_text(row['ISO 22057 required information'])}##"
        ]
        de_rows.append(' | '.join(de_row_parts))

    with codecs.open(output_path_en, 'w', 'utf-8') as f_out:
        f_out.write(EN_HEADER_XLSX + '\n')
        f_out.write('\n'.join([f'| {row}' for row in en_rows]))
        f_out.write('\n|===\n')
    print(f"Successfully generated {output_path_en}")

    with codecs.open(output_path_de, 'w', 'utf-8') as f_out:
        f_out.write(DE_HEADER_XLSX + '\n')
        f_out.write('\n'.join([f'| {row}' for row in de_rows]))
        f_out.write('\n|===\n')
    print(f"Successfully generated {output_path_de}")

def main():
    XLSX_FILE = 'EPD_DataSet.xlsx'
    OUTPUT_FILE_EN = 'epd_documentation_from_xlsx_en.adoc'
    OUTPUT_FILE_DE = 'epd_documentation_from_xlsx_de.adoc'

    script_dir = os.path.dirname(os.path.abspath(__file__))
    xlsx_path = os.path.join(script_dir, XLSX_FILE)
    output_path_en = os.path.join(script_dir, OUTPUT_FILE_EN)
    output_path_de = os.path.join(script_dir, OUTPUT_FILE_DE)

    convert_xlsx_to_adoc(xlsx_path, output_path_en, output_path_de)

if __name__ == '__main__':
    main()
