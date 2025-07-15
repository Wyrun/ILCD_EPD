import codecs
from bs4 import BeautifulSoup


def get_role(cell):
    """Gets the role from the cell's class attribute."""
    classes = cell.get('class', [])
    # The role is the most specific class, usually the first one if it's not a generic class.
    # We will prioritize epd roles.
    role_map = {
        'root': 'root',
        'fieldname_epd': 'fieldname_epd',
        'fieldname_epd2': 'fieldname_epd2',
        'fieldname_epd2i': 'fieldname_epd2i',
        'fieldname_epd24': 'fieldname_epd24',
        'fieldname': 'fieldname',
    }
    for cls in classes:
        if cls in role_map:
            return role_map[cls]
    return 'data' # Default role

def clean_text(text):
    """Cleans text by stripping whitespace and replacing newlines. Returns {nbsp} for empty strings."""
    cleaned = ' '.join(text.strip().split())
    return cleaned if cleaned else '{nbsp}'

def convert_html_to_adoc(html_path, template_path, output_path):
    """Converts an HTML table to two separate AsciiDoc tables (EN/DE) and injects them into a template."""
    # Read the HTML file
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    # Find the main data table
    table = soup.find('table', {'id': 'tableID'})
    if not table:
        print("Error: Could not find table with id='tableID' in the HTML file.")
        return

    en_rows = []
    de_rows = []

    # Process rows from HTML
    rows = table.find_all('tr')
    for i, row in enumerate(rows):
        if i == 0:  # Skip header row of the HTML table
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
            f'[role="{role}"]#{en_name}#',
            f'[role="{role}"]#{element_name}#',
            f'[role="{role}"]#{req}#',
            f'[role="{role}"]#{occ}#',
            f'[role="{role}"]#{datatype}#',
            f'[role="{role}"]#{en_def}#',
            f'[role="{role}"]#{orig_def}#',
            f'[role="{role}"]#{edoc_id}#',
            f'[role="{role}"]#{en15804_comment}#',
            f'[role="{role}"]#{iso22057_guid}#',
            f'[role="{role}"]#{iso22057_mapping_comment}#']
        en_rows.append(' | '.join(en_row_parts))

        # Build German row
        de_row_parts = [
            f'[role="{role}"]#{de_name}#',
            f'[role="{role}"]#{element_name}#',
            f'[role="{role}"]#{req}#',
            f'[role="{role}"]#{occ}#',
            f'[role="{role}"]#{datatype}#',
            f'[role="{role}"]#{de_def}#',
            f'[role="{role}"]#{orig_def}#',
            f'[role="{role}"]#{edoc_id}#',
            f'[role="{role}"]#{en15804_comment}#',
            f'[role="{role}"]#{iso22057_guid}#',
            f'[role="{role}"]#{iso22057_mapping_comment}#']
        de_rows.append(' | '.join(de_row_parts))

    # Format the rows for AsciiDoc table
    en_rows_adoc = '\n'.join([f'| {row}' for row in en_rows])
    de_rows_adoc = '\n'.join([f'| {row}' for row in de_rows])

    # Read the template content
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Replace placeholders in the template
    final_content = template_content.replace('// English data rows will be appended here by the script', en_rows_adoc)
    final_content = final_content.replace('// German data rows will be appended here by the script', de_rows_adoc)

    # Write the final content to the output file
    with codecs.open(output_path, 'w', 'utf-8') as f_out:
        f_out.write(final_content)

    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    convert_html_to_adoc('EPD_DataSet.html', 'epd_documentation_template.adoc', 'epd_documentation.adoc')
