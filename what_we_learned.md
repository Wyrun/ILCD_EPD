# Project Reflection: From Manual Scripts to a Fully Automated Documentation Pipeline

This document summarizes the entire process of transforming the ILCD/EPD project. It's designed to be a personal reference to understand the technical decisions, challenges, and skills involved.

## 1. The Core Problem & Goal

- **Initial State**: A collection of Python scripts in a single folder that could convert an XLSX file into various formats (AsciiDoc, HTML). The process was manual, paths were fragile, and it wasn't suitable for web deployment.
- **End Goal**: To create a clean, maintainable, and fully automated system where updating a central data file would automatically regenerate and publish an interactive, user-friendly website.

## 2. Key Technical Components & Concepts

### The Data Pipeline: `XLSX -> AsciiDoc -> HTML`
- The project's core is a data transformation pipeline. We established that the **AsciiDoc file** (`data/epd_documentation_from_xlsx_combined.adoc`) is the **single source of truth**. 
- While the `convert_xlsx_to_adoc.py` script exists to generate this from the original Excel file (and validate it with a round-trip check), the day-to-day workflow assumes the `.adoc` file is what gets updated.
- The other scripts (`generate_html_report.py`, `generate_attribute_pages.py`) consume this `.adoc` file to produce the final HTML outputs.

### Python Scripting & Libraries
- **`pandas`**: Used for reading the `.xlsx` file into a DataFrame, which is a powerful, table-like data structure that makes data manipulation easy.
- **`BeautifulSoup4` & `lxml`**: Used for parsing HTML. Although we moved a legacy script, this is the standard tool for screen-scraping or parsing HTML/XML content in Python.
- **`regex`**: The `re` module was used for pattern matching to parse the custom structure of our AsciiDoc file, which doesn't have a standard library parser.
- **`os` module**: Crucial for making our file paths robust. We used `os.path.abspath(__file__)` to get the script's location, `os.path.dirname()` to navigate up the directory tree, and `os.path.join()` to build platform-agnostic file paths. This was key to the repository restructuring.

## 3. The Great Restructuring: From Chaos to Clarity

We moved from a flat file structure to a standard, organized layout. This is a critical skill for any software project.

- **`data/`**: For source data files. Separates the 'what' from the 'how'.
- **`docs/`**: For web-ready output. This is the standard name for GitHub Pages deployment roots.
- **`scripts/`**: For all the logic. Separates the 'how' from the 'what' and the 'result'.
- **`output/`**: For temporary build artifacts (like logs or round-trip files) that don't need to be committed.

This separation of concerns makes the project instantly easier to understand, maintain, and scale.

## 4. DevOps: Automation with GitHub Actions & Pages

This was the most significant leap, turning a local project into a professional, automated one.

### GitHub Pages
- A free service from GitHub to host static websites (HTML, CSS, JS) directly from a repository.
- We configured it to serve files from the `/docs` folder on our `main` branch. This is a standard and recommended setup.

### GitHub Actions (CI/CD)
- **CI/CD** stands for Continuous Integration/Continuous Deployment. It's the practice of automating the build, test, and deployment phases of software development.
- We created a **workflow** file: `.github/workflows/docs-build.yml`.
- **Key parts of the workflow:**
    1.  **Trigger (`on: push`)**: The workflow starts automatically every time you `git push` to the `main` branch.
    2.  **Environment (`runs-on: ubuntu-latest`)**: It spins up a fresh virtual machine (in this case, running Ubuntu Linux).
    3.  **Steps (`steps:`)**: It follows a series of commands:
        - `actions/checkout@v3`: Downloads your repository's code onto the virtual machine.
        - `actions/setup-python@v4`: Installs the Python programming language.
        - `pip install -r requirements.txt`: Installs all the necessary libraries.
        - `python scripts/...`: Runs our build scripts to generate the HTML files.
        - **The Magic Step**: It then uses `git` commands to automatically **commit and push** the newly generated files in the `docs/` folder back to the repository.

## 5. Problem Solving: The Journey of Debugging

- **Git Branch Confusion**: We had `main`, `master`, and `non-modular`. We resolved this by deciding on `main` as the source of truth and using `git push -f origin main` to forcefully overwrite the outdated remote branch. This is a powerful but sometimes necessary command.
- **GitHub Actions Permissions (`403 Forbidden`)**: A classic CI/CD issue. The workflow failed because, by default, it doesn't have permission to write (push) to your repository. 
    - **The Fix**: We had to explicitly grant it permission in two places: first, by adding `permissions: contents: write` to the workflow `.yml` file, and second, by ensuring the repository's own settings (**Settings > Actions > General**) allowed workflows to have write permissions.
- **GitHub Pages 404 (`File not found`)**: The site deployed but showed a 404 error. This was because GitHub Pages looks for an `index.html` file by default to serve as the homepage. Our scripts were creating `epd_documentation_report.html`.
    - **The Fix**: We created a simple `docs/index.html` file that contained only an HTML meta refresh tag to instantly redirect the user to the correct report page. This is a standard and effective trick.

## 6. Summary of Skills & Concepts Learned

- **Software Engineering**: Code organization, separation of concerns, creating maintainable project structures.
- **Python**: Advanced scripting, file system navigation, and using key data science/parsing libraries.
- **Version Control (Git)**: Advanced branch management, understanding remote vs. local branches, and using `force-push` responsibly.
- **DevOps & CI/CD**: The fundamentals of automated workflows, using GitHub Actions, and understanding the relationship between a build process and a deployment service like GitHub Pages.
- **Systematic Debugging**: Methodically diagnosing problems that span local code, version control, and remote cloud services.
