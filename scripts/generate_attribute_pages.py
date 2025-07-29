import pandas as pd
import re
import html
import os
from urllib.parse import quote

# --- Constants ---
# Define base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

# Ensure output directory exists
os.makedirs(DOCS_DIR, exist_ok=True)

ADOC_SOURCE_FILE = os.path.join(DATA_DIR, 'epd_documentation_from_xlsx_combined.adoc')
PAGES_OUTPUT_DIR = os.path.join(DOCS_DIR, 'attribute_pages')

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

def sanitize_filename(path):
    """Convert a path to a safe filename."""
    return re.sub(r'[^a-zA-Z0-9._-]', '_', str(path))

def generate_attribute_page(row_data, index):
    """Generate a Wiktionary-style page for a single attribute."""
    
    element_name = str(row_data.get('Element/Attribute Name', '')).replace('|&nbsp;&nbsp;', '').strip()
    path = str(row_data.get('Path', f'row_{index}'))
    
    page_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(element_name)} - EPD Attribute</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        .header {{
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0 0 10px 0;
            font-size: 2.2em;
        }}
        .path {{
            color: #666;
            font-size: 0.9em;
            font-family: monospace;
            background-color: #f1f3f4;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
        }}
        .content {{
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .field {{
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
        }}
        .field:last-child {{
            border-bottom: none;
        }}
        .field-label {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
            font-size: 1.1em;
        }}
        .field-value {{
            color: #555;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .field-value.empty {{
            color: #999;
            font-style: italic;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #007bff;
            text-decoration: none;
            font-weight: 500;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        .lang-indicator {{
            font-size: 0.8em;
            color: #666;
            font-weight: normal;
        }}
        .controls {{
            background-color: #fff;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .lang-buttons, .download-buttons {{
            display: flex;
            gap: 10px;
        }}
        .lang-buttons button, .download-buttons button {{
            padding: 8px 16px;
            border: 1px solid #007bff;
            background-color: #fff;
            color: #007bff;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .lang-buttons button:hover, .download-buttons button:hover {{
            background-color: #007bff;
            color: #fff;
        }}
        .lang-buttons button.active {{
            background-color: #007bff;
            color: #fff;
        }}
        .download-buttons button {{
            border-color: #28a745;
            color: #28a745;
        }}
        .download-buttons button:hover {{
            background-color: #28a745;
            color: #fff;
        }}
        .show-en .lang-de, .show-de .lang-en {{
            display: none !important;
        }}
        .field.lang-en, .field.lang-de {{
            transition: opacity 0.2s;
        }}
    </style>
</head>
<body class="show-both">
    <a href="javascript:window.close()" class="back-link">← Close Window</a>
    
    <div class="controls">
        <div class="lang-buttons">
            <button id="show-en-btn">Show English</button>
            <button id="show-de-btn">Show German</button>
            <button id="show-both-btn" class="active">Show Both</button>
        </div>
        <div class="download-buttons">
            <button id="download-csv-btn">Download as CSV</button>
            <button id="download-adoc-btn">Download as AsciiDoc</button>
        </div>
    </div>
    
    <div class="header">
        <h1>{html.escape(element_name)}</h1>
        <div class="path">Path: {html.escape(path)}</div>
    </div>
    
    <div class="content">
"""

    # Dynamically iterate over all fields in the row data
    for field_name, field_value in row_data.items():
        # Skip internal fields, the name itself, or empty/NaN values
        if field_name in ['Path', 'Indent', 'order', 'Element/Attribute Name'] or pd.isna(field_value) or str(field_value).strip() == '':
            continue

        field_value_str = str(field_value).strip()

        # Handle boolean-like fields for better display
        if field_name in ['Technically Required']:
            if field_value_str.lower() in ['true', 'yes', '1']:
                field_value_str = 'Yes'
            elif field_value_str.lower() in ['false', 'no', '0']:
                field_value_str = 'No'

        # Prepare the field label, cleaning it and adding language indicators
        clean_field_name = field_name
        lang_indicator = ''
        field_class = 'field'
        
        if '(en)' in field_name:
            lang_indicator = ' <span class="lang-indicator">(English)</span>'
            clean_field_name = field_name.replace(' (en)', '').strip()
            field_class += ' lang-en'
        elif '(de)' in field_name:
            lang_indicator = ' <span class="lang-indicator">(German)</span>'
            clean_field_name = field_name.replace(' (de)', '').strip()
            field_class += ' lang-de'

        # Add the field to the page content
        page_content += f"""
        <div class="{field_class}">
            <div class="field-label">{html.escape(clean_field_name)}{lang_indicator}</div>
            <div class="field-value">{html.escape(field_value_str)}</div>
        </div>
"""

    page_content += """
    </div>
    
    <script>
        // Language toggle functionality
        document.getElementById('show-en-btn').addEventListener('click', function() {
            document.body.className = 'show-en';
            updateActiveButton('show-en-btn');
        });
        
        document.getElementById('show-de-btn').addEventListener('click', function() {
            document.body.className = 'show-de';
            updateActiveButton('show-de-btn');
        });
        
        document.getElementById('show-both-btn').addEventListener('click', function() {
            document.body.className = 'show-both';
            updateActiveButton('show-both-btn');
        });
        
        function updateActiveButton(activeId) {
            document.querySelectorAll('.lang-buttons button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(activeId).classList.add('active');
        }
        
        // Download functionality
        document.getElementById('download-csv-btn').addEventListener('click', function() {
            // Create a link to download the CSV file
            const link = document.createElement('a');
            link.href = '../../data/epd_documentation.csv';
            link.download = 'epd_documentation.csv';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
        
        document.getElementById('download-adoc-btn').addEventListener('click', function() {
            // Create a link to download the AsciiDoc file
            const link = document.createElement('a');
            link.href = '../../data/epd_documentation_from_xlsx_combined.adoc';
            link.download = 'epd_documentation_from_xlsx_combined.adoc';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    </script>
</body>
</html>
"""
    
    return page_content

def generate_all_attribute_pages(df):
    """Generate individual attribute pages for all rows in the DataFrame."""
    
    if not os.path.exists(PAGES_OUTPUT_DIR):
        os.makedirs(PAGES_OUTPUT_DIR)
        print(f"Created directory: {PAGES_OUTPUT_DIR}")
    
    generated_pages = []
    
    for index, row in df.iterrows():
        path = str(row.get('Path', f'row_{index}'))
        sanitized_path = sanitize_filename(path)
        
        page_content = generate_attribute_page(row, index)
        
        filename = f"{sanitized_path}.html"
        filepath = os.path.join(PAGES_OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(page_content)
        
        generated_pages.append({
            'path': path,
            'filename': filename,
            'filepath': filepath
        })
    
    return generated_pages

def generate_index_page(pages_info):
    """Generate an index page listing all attribute pages."""
    
    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPD Attribute Pages - Index</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
        }}
        .controls {{
            background-color: #fff;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .download-buttons {{
            display: flex;
            gap: 10px;
        }}
        .download-buttons button {{
            padding: 10px 20px;
            border: 1px solid #28a745;
            background-color: #fff;
            color: #28a745;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
            font-weight: 500;
        }}
        .download-buttons button:hover {{
            background-color: #28a745;
            color: #fff;
        }}
        .pages-list {{
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .page-link {{
            display: block;
            padding: 10px 15px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            text-decoration: none;
            color: #2c3e50;
            transition: background-color 0.2s;
        }}
        .page-link:hover {{
            background-color: #e9ecef;
            text-decoration: none;
        }}
        .path {{
            font-family: monospace;
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>EPD Attribute Pages</h1>
    
    <div class="controls">
        <div class="download-buttons">
            <button id="download-csv-btn">📊 Download as CSV</button>
            <button id="download-adoc-btn">📄 Download as AsciiDoc</button>
        </div>
    </div>
    
    <div class="pages-list">
        <p>Click on any attribute below to view its detailed information:</p>
"""

    for page_info in pages_info:
        index_content += f"""
        <a href="{html.escape(page_info['filename'])}" class="page-link" target="_blank">
            <div class="path">{html.escape(page_info['path'])}</div>
        </a>
"""

    index_content += """    </div>
    
    <script>
        // Download functionality
        document.getElementById('download-csv-btn').addEventListener('click', function() {
            // Create a link to download the CSV file
            const link = document.createElement('a');
            link.href = '../../data/epd_documentation.csv';
            link.download = 'epd_documentation.csv';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
        
        document.getElementById('download-adoc-btn').addEventListener('click', function() {
            // Create a link to download the AsciiDoc file
            const link = document.createElement('a');
            link.href = '../../data/epd_documentation_from_xlsx_combined.adoc';
            link.download = 'epd_documentation_from_xlsx_combined.adoc';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    </script>
</body>
</html>
"""
    
    index_filepath = os.path.join(PAGES_OUTPUT_DIR, 'index.html')
    with open(index_filepath, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    return index_filepath

# --- Main Execution ---
if __name__ == "__main__":
    try:
        # Parse the AsciiDoc data
        df = parse_asciidoc_table(ADOC_SOURCE_FILE)
        
        # Generate all attribute pages
        print("Generating individual attribute pages...")
        pages_info = generate_all_attribute_pages(df)
        
        # Generate index page
        print("Generating index page...")
        index_path = generate_index_page(pages_info)
        
        print(f"Successfully generated {len(pages_info)} attribute pages in '{PAGES_OUTPUT_DIR}' directory")
        print(f"Index page created at: {index_path}")
        print(f"Open '{os.path.join(PAGES_OUTPUT_DIR, 'index.html')}' to browse all pages")
        
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"An error occurred: {e}")
