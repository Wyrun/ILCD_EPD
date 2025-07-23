# EPD/ILCD Data Documentation Workflow

This project provides a set of Python scripts to convert EPD (Environmental Product Declaration) data from an XLSX spreadsheet into a structured AsciiDoc format and then into a final, interactive HTML report.

## Project Goal

The primary goal is to transform a complex, bilingual (English and German) EPD specification from an Excel file into a user-friendly, interactive HTML report. This report allows for easy navigation, language switching, and detailed inspection of the data's hierarchical structure.

## File Structure

-   `ILCD_EPD_Data_Structure.xlsx`: The original source file containing the EPD data definitions in both English and German.
-   `epd_documentation_from_xlsx_combined.py`: The main script responsible for the round-trip conversion. It reads the XLSX file, generates a combined AsciiDoc file, converts it back to XLSX, and compares it with the original to ensure data integrity.
-   `generate_html_report.py`: This script parses the `.adoc` file and generates the final, interactive HTML report.
-   `generate_csv_from_adoc.py`: An optional script to convert the AsciiDoc file into a CSV file.
-   `epd_documentation_from_xlsx_combined.adoc`: The intermediate AsciiDoc file. It contains all the data from the source XLSX in a structured, plain-text format. This file serves as the single source of truth for the HTML report.
-   `epd_documentation_report.html`: The final output. An interactive HTML page for browsing the EPD data.
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

-   **Interactive Language Toggle**: A button allows users to switch between viewing English and German columns.
-   **Column Visibility Control**: Checkboxes let users show or hide specific columns to focus on the information they need.
-   **Hierarchical View**: The `Element/Attribute Name` column is indented to visually represent the data's parent-child relationships.
-   **Path Tooltips**: Hovering over any row displays a custom tooltip showing the full hierarchical path of that data element, providing complete context.

## How to Use

1.  **Ensure all files are in the same directory.**
2.  **Run the data conversion and validation script** (optional, as the `.adoc` file is already provided):
    ```bash
    python epd_documentation_from_xlsx_combined.py
    ```
3.  **Generate the HTML report**:
    ```bash
    python generate_html_report.py
    ```
4.  **Open the Report**: Open `epd_documentation_report.html` in a web browser to view the interactive documentation.
5.  **(Optional) Generate a CSV export**:
    ```bash
    python generate_csv_from_adoc.py
    ```
