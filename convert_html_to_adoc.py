import os
import codecs
from bs4 import BeautifulSoup

# --- AsciiDoc Headers ---

EN_HEADER = """= EPD Data Set Documentation (English)
:doctype: book
:stylesheet: ilcd.css
:source-highlighter: highlightjs

This document lists the ILCD format fields that are used to model EPD data.

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

DE_HEADER = """= EPD Data Set Documentation (German)
:doctype: book
:stylesheet: ilcd.css
:source-highlighter: highlightjs

Dieses Dokument listet die ILCD-Formatfelder auf, die zur Modellierung von EPD-Daten verwendet werden.

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

def get_role(cell):
    """Extracts a role from the cell's class attribute."""
    class_attr = cell.get('class', [])
    if 'root' in class_attr:
        return 'root'
    if 'fieldname_epd' in class_attr:
        return 'fieldname_epd'
    if 'fieldname_epd2' in class_attr:
        return 'fieldname_epd2'
    return 'fieldname'

def clean_text(text):
    """Cleans and formats text for AsciiDoc, handling empty cells."""
    cleaned = ' '.join(text.strip().split())
    return cleaned if cleaned else '{nbsp}'

# --- Main Conversion Logic ---

def convert_html_to_adoc(html_path, output_path_en, output_path_de, en_header, de_header):
    """Converts an HTML table to two separate, self-contained AsciiDoc files (EN and DE)."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    table = soup.find('table', {'id': 'tableID'})
    if not table:
        print("Error: Could not find table with id='tableID' in the HTML file.")
        return

    en_rows = []
    de_rows = []

    rows = table.find_all('tr')
    for i, row in enumerate(rows):
        if i == 0:  # Skip header row
            continue

        cells = row.find_all(['td', 'th'])
        if not cells or len(cells) < 13:
            continue

        # Extract data from cells
        de_name = clean_text(cells[0].get_text())
        en_name = clean_text(cells[1].get_text())
        element_name = clean_text(cells[2].get_text())
        req = clean_text(cells[3].get_text())
        occ = clean_text(cells[4].get_text())
        datatype_cell = cells[5]
        datatype_link = datatype_cell.find('a')
        if datatype_link:
            href = datatype_link['href']
            text = clean_text(datatype_link.get_text())
            datatype = f'link:{href}[{text}]'
        else:
            datatype = clean_text(datatype_cell.get_text())
        de_def = clean_text(cells[6].get_text())
        en_def = clean_text(cells[7].get_text())
        orig_def = clean_text(cells[8].get_text())
        edoc_id = clean_text(cells[9].get_text())
        en15804_comment = clean_text(cells[10].get_text())
        iso22057_guid = clean_text(cells[11].get_text())
        iso22057_mapping_comment = clean_text(cells[12].get_text())
        role = get_role(cells[0])

        # Build English row
        en_row_parts = [
            f'[role="{role}"]#{en_name}#', f'[role="{role}"]#{element_name}#',
            f'[role="{role}"]#{req}#', f'[role="{role}"]#{occ}#', f'[role="{role}"]#{datatype}#',
            f'[role="{role}"]#{en_def}#', f'[role="{role}"]#{orig_def}#', f'[role="{role}"]#{edoc_id}#',
            f'[role="{role}"]#{en15804_comment}#', f'[role="{role}"]#{iso22057_guid}#',
            f'[role="{role}"]#{iso22057_mapping_comment}#']
        en_rows.append(' | '.join(en_row_parts))

        # Build German row
        de_row_parts = [
            f'[role="{role}"]#{de_name}#', f'[role="{role}"]#{element_name}#',
            f'[role="{role}"]#{req}#', f'[role="{role}"]#{occ}#', f'[role="{role}"]#{datatype}#',
            f'[role="{role}"]#{de_def}#', f'[role="{role}"]#{orig_def}#', f'[role="{role}"]#{edoc_id}#',
            f'[role="{role}"]#{en15804_comment}#', f'[role="{role}"]#{iso22057_guid}#',
            f'[role="{role}"]#{iso22057_mapping_comment}#']
        de_rows.append(' | '.join(de_row_parts))

    # --- Write English File ---
    with codecs.open(output_path_en, 'w', 'utf-8') as f_out:
        f_out.write(en_header + '\n')
        f_out.write('\n'.join([f'| {row}' for row in en_rows]))
        f_out.write('\n|===\n')
    print(f"Successfully generated {output_path_en}")

    # --- Write German File ---
    with codecs.open(output_path_de, 'w', 'utf-8') as f_out:
        f_out.write(de_header + '\n')
        f_out.write('\n'.join([f'| {row}' for row in de_rows]))
        f_out.write('\n|===\n')
    print(f"Successfully generated {output_path_de}")

def main():
    """Main function to run the conversion process."""
    HTML_FILE = 'EPD_DataSet.html'
    OUTPUT_FILE_EN = 'epd_documentation_en.adoc'
    OUTPUT_FILE_DE = 'epd_documentation_de.adoc'

    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, HTML_FILE)
    output_path_en = os.path.join(script_dir, OUTPUT_FILE_EN)
    output_path_de = os.path.join(script_dir, OUTPUT_FILE_DE)

    convert_html_to_adoc(html_path, output_path_en, output_path_de, EN_HEADER, DE_HEADER)

if __name__ == '__main__':
    main()
