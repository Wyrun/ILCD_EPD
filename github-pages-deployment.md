# Deploying the EPD Documentation to GitHub Pages

This document outlines the steps to set up a fully automated workflow using GitHub Actions to publish the EPD documentation report to GitHub Pages.

The goal is to have a system where any update pushed to the `epd_documentation_from_xlsx_combined.adoc` file on the `main` branch will automatically trigger a process that:
1.  Generates the latest `epd_documentation_report.html`.
2.  Generates the latest CSV export (`epd_documentation.csv`).
3.  Publishes these files to your live GitHub Pages site.

---

## Step 1: Prepare Your Repository

1.  **Initialize Git:** If you haven't already, initialize a Git repository in your project folder.
    ```bash
    git init
    git add .
    git commit -m "Initial commit of EPD documentation project"
    ```

2.  **Create a GitHub Repository:** Go to [GitHub](https://github.com) and create a new repository. Do not initialize it with a README or .gitignore, as you already have a local repository.

3.  **Push Your Code:** Follow the instructions on GitHub to push your existing local repository to the remote.
    ```bash
    git remote add origin <YOUR_REPOSITORY_URL>
    git branch -M main
    git push -u origin main
    ```

4.  **Ensure `requirements.txt` Exists:** The GitHub Actions workflow needs to know which Python libraries to install. Make sure your `requirements.txt` file contains:
    ```
    pandas
    ```

---

## Step 2: Create the GitHub Actions Workflow

1.  **Create the Workflow Directory:** In your project root, create a new directory structure: `.github/workflows`.
    ```bash
    mkdir -p .github/workflows
    ```

2.  **Create the Workflow YAML File:** Inside the `.github/workflows` directory, create a new file named `deploy-to-pages.yml`.

3.  **Add Workflow Content:** Paste the following YAML code into `deploy-to-pages.yml`. This defines the entire CI/CD pipeline.

    ```yaml
    name: Deploy EPD Documentation to GitHub Pages

    # 1. TRIGGER: Run this workflow on a push to the main branch,
    # but only if the AsciiDoc file has changed.
    on:
      push:
        branches:
          - main
        paths:
          - 'epd_documentation_from_xlsx_combined.adoc'
      # Allows you to run this workflow manually from the Actions tab
      workflow_dispatch:

    # 2. PERMISSIONS: Grant the necessary permissions for the job to deploy to GitHub Pages.
    permissions:
      contents: read
      pages: write
      id-token: write

    # 3. JOB: Define the sequence of steps to run.
    jobs:
      deploy:
        runs-on: ubuntu-latest
        environment:
          name: github-pages
          url: ${{ steps.deployment.outputs.page_url }}
        steps:
          # Step 3a: Check out the repository's code
          - name: Checkout repository
            uses: actions/checkout@v4

          # Step 3b: Set up Python environment
          - name: Set up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.10'

          # Step 3c: Install Python dependencies
          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install -r requirements.txt

          # Step 3d: Run the scripts to build the HTML and CSV files
          - name: Build HTML and CSV from AsciiDoc
            run: |
              python generate_html_report.py
              python generate_csv_from_adoc.py

          # Step 3e: Prepare the generated files for deployment
          - name: Setup Pages
            uses: actions/configure-pages@v4

          # Step 3f: Upload the build artifacts (the generated files)
          - name: Upload artifact
            uses: actions/upload-pages-artifact@v2
            with:
              # Upload the root directory, which will contain the generated files
              path: '.'

          # Step 3g: Deploy the artifacts to GitHub Pages
          - name: Deploy to GitHub Pages
            id: deployment
            uses: actions/deploy-pages@v2
    ```

---

## Step 3: Configure GitHub Pages Settings

1.  **Commit and Push the Workflow:** Add the new workflow file to Git and push it to your repository.
    ```bash
    git add .github/workflows/deploy-to-pages.yml
    git commit -m "feat: Add GitHub Actions workflow for deployment"
    git push
    ```

2.  **Enable GitHub Pages:**
    *   In your GitHub repository, go to **Settings > Pages**.
    *   Under **Build and deployment**, change the **Source** from `Deploy from a branch` to **`GitHub Actions`**.

---

## How It Works from Now On

Once this is set up, the process is fully automated:

1.  A developer edits and commits a change to the `epd_documentation_from_xlsx_combined.adoc` file.
2.  They push the commit to the `main` branch.
3.  GitHub automatically detects the push and triggers the `Deploy EPD Documentation to GitHub Pages` action.
4.  The action runs through the build steps, creating the HTML and CSV files.
5.  The action then deploys these files to your GitHub Pages environment.
6.  Within a minute or two, the changes will be live on your public GitHub Pages URL.

Users visiting your site will see the latest version of the report and can access the CSV file by navigating to `https://<your-username>.github.io/<your-repo-name>/epd_documentation.csv`.
