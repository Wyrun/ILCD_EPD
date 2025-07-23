import pandas as pd
import re
import html

# --- Constants ---
ADOC_SOURCE_FILE = 'epd_documentation_from_xlsx_combined.adoc'
HTML_OUTPUT_FILE = 'epd_documentation_report.html'

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

    # Create Table Header HTML - Use presentation_columns to guarantee order
    header_html = "<thead><tr>"
    for col in presentation_columns:
        col_class = get_col_class(col)
        header_html += f'<th class="{col_class}" data-col="{html.escape(col)}">{html.escape(col)}</th>'
    header_html += "</tr></thead>"

    # Create Table Body HTML
    body_html = "<tbody>"
    for index, row in df_presentation.iterrows():
        path_tooltip = html.escape(str(df_source.loc[index, 'Path'])) if 'Path' in df_source.columns else ''
        body_html += '<tr>'
        # Iterate using presentation_columns to ensure perfect alignment with the header
        for col_name in presentation_columns:
            col_class = get_col_class(col_name)
            cell_content = str(row[col_name])
            # The 'Element/Attribute Name' is already formatted with HTML, so don't escape it.
            if col_name != 'Element/Attribute Name':
                cell_content = html.escape(cell_content)
            
            # Wrap the first cell's content to handle the tooltip
            if col_name == presentation_columns[0]:
                body_html += f'<td class="{col_class}" data-col="{html.escape(col_name)}"><div class="tooltip-wrapper">{cell_content}<span class="tooltip-text">{path_tooltip}</span></div></td>'
            else:
                body_html += f'<td class="{col_class}" data-col="{html.escape(col_name)}">{cell_content}</td>'
        body_html += "</tr>"
    body_html += "</tbody>"

    html_table = f"<table class='styled-table' border='0'>{header_html}{body_html}</table>"

    # --- Final HTML Document with CSS and JS ---
    script_block = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const langToggle = document.getElementById('lang-toggle');
                const body = document.body;

                langToggle.addEventListener('click', function() {
                    if (body.classList.contains('show-en')) {
                        body.classList.remove('show-en');
                        body.classList.add('show-de');
                        langToggle.textContent = 'Show English';
                    } else {
                        body.classList.remove('show-de');
                        body.classList.add('show-en');
                        langToggle.textContent = 'Show German';
                    }
                });

                const colToggles = document.querySelectorAll('.col-toggle');
                colToggles.forEach(function(checkbox) {
                    checkbox.addEventListener('change', function() {
                        const colName = this.value;
                        const cells = document.querySelectorAll(`[data-col="${colName}"]`);
                        cells.forEach(cell => {
                            cell.style.display = this.checked ? '' : 'none';
                        });
                    });
                });
            });
        </script>
    """

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EPD Documentation Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 20px; color: #333; background-color: #f8f9fa; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        .controls {{ margin-bottom: 20px; padding: 15px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; flex-wrap: wrap; gap: 20px; align-items: center; }}
        .controls label {{ font-size: 14px; cursor: pointer; }}
        .controls button {{ padding: 8px 12px; font-size: 14px; cursor: pointer; border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; background-color: white; }}
        th, td {{ padding: 10px 14px; border: 1px solid #dee2e6; text-align: left; vertical-align: top; word-wrap: break-word; }}
        thead tr {{ background-color: #343a40; color: white; }}
        /* td:nth-child(3) was causing the alignment issue */
        tbody tr:nth-of-type(even) {{ background-color: #f2f2f2; }}
        .show-de .lang-en, .show-en .lang-de {{ display: none; }}
        
        /* Custom Tooltip Styles */
        td .tooltip-wrapper {{ position: relative; }}
        td .tooltip-wrapper .tooltip-text {{
            visibility: hidden;
            opacity: 0;
            position: absolute;
            bottom: 110%; /* Position above the cell */
            left: 50%;
            transform: translateX(-50%);
            background-color: #2c3e50;
            color: #fff;
            text-align: center;
            padding: 8px 12px;
            border-radius: 6px;
            z-index: 10;
            white-space: normal;
            max-width: 450px;
            transition: opacity 0.2s;
            pointer-events: none; /* Allow clicking through the tooltip */
        }}
        td .tooltip-wrapper:hover .tooltip-text {{
            visibility: visible;
            opacity: 1;
        }}
    </style>
</head>
<body class="show-en">
    <h1>EPD Documentation Report</h1>
    <div class="controls">
        <button id="lang-toggle">Show German</button>
        <div class="col-toggles">{checkboxes_html}</div>
    </div>
    {html_table}
    {script_block}
</body>
</html>
"""
    return html_template

# --- Main Execution ---
if __name__ == "__main__":
    PRESENTATION_COLUMNS = [
        'Field Name (en)',
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
        'Field Name (de)', # Keep for data availability, but hide with CSS
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
