// ilcd.js
// Moved JavaScript from HTML to external file

/**
 * Toggle language columns and definitions
 * @param {string} strLang - 'en' or 'de'
 */
function selectLang(strLang) {
    var table = document.getElementById('tableID');
    if (!table) return;

    if (strLang === 'en') {
        table.classList.remove('lang-de');
        table.classList.add('lang-en');
    } else { // de
        table.classList.remove('lang-en');
        table.classList.add('lang-de');
    }
}

function initialize() {
    // Set default language
    selectLang('en');

    // Add event listeners to radio buttons
    document.getElementById('langEn').addEventListener('click', function() { selectLang('en'); });
    document.getElementById('langDe').addEventListener('click', function() { selectLang('de'); });
}

// Defer execution to ensure the AsciiDoc table is fully rendered
window.onload = function() {
    setTimeout(initialize, 100); // A small delay to ensure the DOM is ready
};