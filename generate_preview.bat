@echo off
REM This script converts ilcd.adoc to ilcd.html and opens it in your browser.

REM Add the Ruby gems bin directory to the PATH for this script's session
set "PATH=%PATH%;C:\Users\Dns\.local\share\gem\ruby\3.4.0\bin"

REM Run the asciidoctor conversion
echo Converting ilcd.adoc to ilcd.html...
asciidoctor ilcd.adoc

REM Check if the conversion was successful
if exist ilcd.html (
    echo Conversion successful. Opening preview in browser...
    REM Open the generated HTML file in the default browser
    start ilcd.html
) else (
    echo Conversion failed. Please check for errors.
)

pause
