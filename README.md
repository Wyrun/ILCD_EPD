# ILCD EPD Documentation Generator

This project contains a script to convert the EPD documentation from `EPD_DataSet.html` into a structured AsciiDoc file.

## Setup and Usage

A Python virtual environment is used to manage dependencies.

### Activating the Environment

To activate the virtual environment, run the following command from the project's root directory:


.\.venv\Scripts\activate


### Running the Conversion

Once the environment is activated, you can run the conversion script:


python convert_html_to_adoc.py


This will read `EPD_DataSet.html` and `ilcd.adoc` (for the header) and generate a new file named `documentation_from_html.adoc` with the full, converted documentation.
