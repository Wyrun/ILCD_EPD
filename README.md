# EPD/ILCD Data Documentation Workflow

This project provides a set of Python scripts to convert EPD (Environmental Product Declaration) data from an XLSX spreadsheet into a structured, bilingual AsciiDoc format and then into a final, interactive HTML report with individual attribute pages.

## Project Goal

The primary goal is to transform a complex, bilingual (English and German) EPD specification from an Excel file into a user-friendly, interactive HTML report. This report allows for easy navigation, language switching, and detailed inspection of the data's hierarchical structure.

## File Structure

-   `data/`: Contains the primary data files.
    -   `EPD_DataSet.xlsx`: The original source file.
    -   `epd_documentation_from_xlsx_combined.adoc`: The generated bilingual AsciiDoc source of truth.
    -   `epd_documentation.csv`: The generated CSV version of the data.
-   `docs/`: Contains the generated web content ready for deployment.
    -   `epd_documentation_report.html`: The main interactive HTML report.
    -   `attribute_pages/`: Contains individual HTML pages for each attribute.
-   `scripts/`: Contains all the Python scripts for the workflow.
-   `output/`: Contains temporary files generated during the workflow, such as `roundtrip.xlsx` and `comparison_log.txt`.
-   `legacy_scripts/`: Contains older, unused scripts for archival purposes.
-   `README.md`: This documentation file.

## Workflow Overview

The workflow consists of two main stages:

1.  **XLSX to AsciiDoc Conversion & Validation**: The `epd_documentation_from_xlsx_combined.py` script performs a round-trip data conversion:
    -   It reads the source `ILCD_EPD_Data_Structure.xlsx`.
    -   It generates the `epd_documentation_from_xlsx_combined.adoc` file, combining English and German data.
    -   It calculates hierarchical indentation and paths for each data entry.
    -   It converts the `.adoc` file back into a new XLSX file in memory.
    -   It compares this new XLSX with the original to ensure a lossless conversion.

2.  **AsciiDoc to HTML Report Generation**: The `generate_html_report.py` script takes the `.adoc` file and produces the final `epd_documentation_report.html`.

## Key Features of the HTML Report

-   **Interactive Language Toggle**: Buttons allow users to switch between viewing English, German, or both languages.
-   **Column Visibility Control**: Checkboxes let users show or hide specific data columns to focus on the information they need.
-   **Hierarchical View**: The `Element/Attribute Name` column is indented with tree lines to visually represent the data's parent-child relationships.
-   **Path Tooltips**: Hovering over an element's name displays a tooltip showing the full hierarchical path of that data element, providing complete context.
-   **Advanced Search**: A powerful search bar supports filtering by name, full path, and case-insensitive regular expressions. See details below.

### Search Functionality Explained

The search bar supports three different modes:

1.  **By Element/Attribute Name (Default):**
    *   Simply type any text into the search bar.
    *   The table will filter to show only rows where the `Element/Attribute Name` contains your text.
    *   *Example:* `flow` will find `flowProperties`, `flowCategorization`, etc.

2.  **By Full Hierarchical Path:**
    *   To search by a node's full path, include a period (`.`) in your search term.
    *   The search will match against the full path tooltip of each row.
    *   *Example:* `process.completeness` will find nodes under the `process` section related to completeness.

3.  **By Regular Expression (Regex):**
    *   The search bar supports case-insensitive JavaScript regular expressions for advanced filtering.
    *   *Example 1 (Starts with):* `^process` will find all root elements that start with `process`.
    *   *Example 2 (Ends with):* `Info$` will find all elements ending in `Info`.
    *   *Example 3 (Exact match):* `^name$` will find elements that are exactly `name`.
    *   *Example 4 (Complex path):* `process\.name` will find `name` nodes that are direct children of a `process` node (note the double backslash to escape the `.` for a literal match).

## How to Use

1.  **Install Dependencies**: Make sure you have Python and the required libraries installed:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Full Workflow**: To regenerate everything from the source XLSX, you can run the scripts in order. Note that the primary source of truth is now the AsciiDoc file, so this is typically only needed if the `EPD_DataSet.xlsx` file changes.

    -   **Convert XLSX to AsciiDoc (Round-trip validation)**:
        ```bash
        python scripts/convert_xlsx_to_adoc.py
        ```

    -   **Generate the main HTML report**:
        ```bash
        python scripts/generate_html_report.py
        ```

    -   **Generate the individual attribute pages**:
        ```bash
        python scripts/generate_attribute_pages.py
        ```

    -   **(Optional) Generate a CSV export**:
        ```bash
        python scripts/generate_csv_from_adoc.py
        ```

3.  **View the Documentation**: Open `docs/epd_documentation_report.html` or `docs/attribute_pages/index.html` in your web browser.

## GitHub Pages Deployment

This project is designed to be easily deployed using GitHub Pages. The `docs/` directory is the root for the GitHub Pages site.

1.  **Push to GitHub**: Make sure your repository is pushed to GitHub.
2.  **Enable GitHub Pages**: In your repository's settings, go to the "Pages" section.
3.  **Configure Source**: Select the branch you want to deploy from (e.g., `main`) and set the folder to `/docs`.
4.  **Access Your Site**: GitHub will provide you with the URL for your live documentation.
