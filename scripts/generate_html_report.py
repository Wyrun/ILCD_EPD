import pandas as pd
import re
import html
import os

# --- Constants ---
# Define base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

# Ensure output directory exists
os.makedirs(DOCS_DIR, exist_ok=True)

ADOC_SOURCE_FILE = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')
HTML_OUTPUT_FILE = os.path.join(DOCS_DIR, 'epd_documentation_report.html')

# --- Data Loading and Parsing ---
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

# --- HTML Generation ---
def generate_html_report(df_source, presentation_columns, column_map):
    """Generates the final interactive HTML report from the DataFrame."""
    # Create a new DataFrame for presentation, ensuring it's a copy.
    # It will be built column-by-column in the correct, final order.
    df_presentation = pd.DataFrame(index=df_source.index)

    # Build the presentation dataframe column-by-column, strictly following the presentation_columns list.
    for col_name in presentation_columns:
        source_col_name = column_map.get(col_name, col_name)

        # For the special 'Element/Attribute Name' column, add the indentation.
        if col_name == 'Element/Attribute Name':
            indentation = df_source['Indent'].apply(lambda x: '|&nbsp;&nbsp;' * x) if 'Indent' in df_source.columns else ''
            values = df_source.get(source_col_name, '').astype(str)
            df_presentation[col_name] = indentation + values
        # For all other columns, just copy the data.
        else:
            df_presentation[col_name] = df_source.get(source_col_name, '')

    # --- Build HTML Manually for Interactivity ---
    def get_col_class(col_name):
        if col_name == 'Original ILCD Format Definition (en)':
            return ''  # Always visible
        if '(de)' in col_name: return 'lang-de'
        if '(en)' in col_name: return 'lang-en'
        return ''

    # Create Checkboxes HTML
    checkboxes_html = ""
    for col in presentation_columns:
        if col not in ['Field Name (en)', 'Element/Attribute Name']:
            checkboxes_html += f'''
            <label>
                <input type="checkbox" class="col-toggle" value="{html.escape(col)}" checked>
                {html.escape(col)}
            </label>'''

    # Create Table Header HTML - Add "View Attribute" column first, then presentation_columns
    header_html = "<thead><tr>"
    header_html += '<th data-col="View Attribute">View Attribute</th>'  # New column
    for col in presentation_columns:
        col_class = get_col_class(col)
        header_html += f'<th class="{col_class}" data-col="{html.escape(col)}">{html.escape(col)}</th>'
    header_html += "</tr></thead>"

    # Create Table Body HTML
    body_html = "<tbody>"
    for index, row in df_presentation.iterrows():
        path_tooltip = html.escape(str(df_source.loc[index, 'Path'])) if 'Path' in df_source.columns else ''
        attribute_path = str(df_source.loc[index, 'Path']) if 'Path' in df_source.columns else f'row_{index}'
        
        body_html += f'<tr data-tooltip="{path_tooltip}">'
        
        # Add "View Attribute" button column first
        body_html += f'<td data-col="View Attribute">'
        body_html += f'<button class="view-attr-btn" onclick="openAttributePage(\'{html.escape(attribute_path)}\')" title="View detailed information for this attribute">View Attribute</button>'
        body_html += f'</td>'
        
        # Then add all the regular columns
        for col in presentation_columns:
            col_class = get_col_class(col)
            cell_value = str(row[col]) if pd.notna(row[col]) else ''
            
            # Special handling for 'Element/Attribute Name' column to add tooltip
            if col == 'Element/Attribute Name':
                body_html += f'<td class="{col_class}" data-col="{html.escape(col)}">'
                body_html += f'<div class="tooltip-wrapper">'
                body_html += cell_value  # This already includes indentation from above
                body_html += f'<span class="tooltip-text">{path_tooltip}</span>'
                body_html += f'</div>'
                body_html += f'</td>'
            else:
                body_html += f'<td class="{col_class}" data-col="{html.escape(col)}">{html.escape(cell_value)}</td>'
        body_html += "</tr>"
    body_html += "</tbody>"

    html_table = f'<table id="report-table">{header_html}{body_html}</table>'

    # --- Final HTML Document with CSS and JS ---
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EPD Documentation Report</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body class="show-en">
    <h1>EPD Documentation Report</h1>
    <div class="controls">
        <input type="text" id="search-bar" placeholder="Search by Name, Path (e.g. 'proc.name'), or Regex (e.g. '^process')">
        <div class="lang-buttons">
            <button id="show-en-btn">Show English</button>
            <button id="show-de-btn">Show German</button>
            <button id="show-all-btn">Show Both</button>
        </div>
        <div class="download-buttons">
            <button id="download-csv-btn">Download CSV</button>
            <button id="download-adoc-btn">Download AsciiDoc</button>
        </div>
        <div class="view-options">
            <button id="toggle-stripes-btn">Toggle Stripes</button>
        </div>
        <div class="col-toggles">{checkboxes_html}</div>
    </div>
    {html_table}
    <script src="js/script.js"></script>
</body>
</html>
"""
    return html_template

# --- Main Execution ---
if __name__ == "__main__":
    PRESENTATION_COLUMNS = [
        'Field Name (en)',
        'Field Name (de)',
        'Element/Attribute Name',
        'Requ.',
        'Occ.',
        'Datatype',
        'Definition (en)',
        'Definition (de)',
        'Original ILCD Format Definition (en)',
        'eDoc ID',
        'EN15804+A2 mapping comment',
        'ISO 22057 GUID',
        'ISO 22057 mapping comment',
    ]

    COLUMN_MAPPING = {
        'Requ.': 'Technically Required',
        'Definition (en)': 'IndData Definition (en)\u00a0- new ones',
        'Original ILCD Format Definition (en)': 'InData / ÖKOBAUDAT Definition and explanation (EN)\u00a0- old ones'
    }

    try:
        df = parse_asciidoc_table(ADOC_SOURCE_FILE)
        html_content = generate_html_report(df, PRESENTATION_COLUMNS, COLUMN_MAPPING)
        with open(HTML_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully generated interactive HTML report: {HTML_OUTPUT_FILE}")

    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"An error occurred: {e}")
