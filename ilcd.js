// ilcd.js

/**
 * Helper to locate the rendered <table> within AsciiDoc output
 * @param {string} tableId - ID applied to the AsciiDoc table block
 * @returns {HTMLTableElement|null}
 */
function getTableById(tableId) {
    const wrapper = document.getElementById(tableId);
    if (!wrapper) return null;
    // Asciidoctor wraps it in <div class="tableblock">
    if (wrapper.classList.contains('tableblock')) {
        const tbl = wrapper.querySelector('div.content > table');
        return tbl || null;
    }
    // if direct <table id=>
    if (wrapper.tagName.toLowerCase() === 'table') {
        return wrapper;
    }
    return null;
}

/**
 * Toggle a column's visibility
 * @param {string} tableId
 * @param {number} colIndex
 * @param {string} display - '' to show, 'none' to hide
 */
function toggleCol(tableId, colIndex, display) {
    const table = getTableById(tableId);
    if (!table) return;
    Array.from(table.rows).forEach(row => {
        const cell = row.cells[colIndex];
        if (cell && cell.colSpan === 1) {
            cell.style.display = display;
        }
    });
    // adjust colSpan for any spanning cells
    table.querySelectorAll('td[colspan], th[colspan]').forEach(cell => {
        cell.colSpan = Math.max(1, cell.colSpan + (display === '' ? 1 : -1));
    });
}

/**
 * Show/hide language columns
 * @param {'en'|'de'} lang
 */
function selectLang(lang) {
    if (lang === 'en') {
        toggleCol('tableID', 0, 'none'); // hide German header
        toggleCol('tableID', 1, '');     // show English header
        toggleCol('tableID', 6, 'none'); // hide Def (de)
        toggleCol('tableID', 7, '');     // show Def (en)
    } else {
        toggleCol('tableID', 0, '');     // show German
        toggleCol('tableID', 1, 'none'); // hide English
        toggleCol('tableID', 6, '');     // show Def (de)
        toggleCol('tableID', 7, 'none'); // hide Def (en)
    }
}

/**
 * Wire up the controls on DOM ready
 */
function initializeControls() {
    // language radios use inline onclick, so just honor default
    const tableInit = document.querySelector('#formSelectLang input[value=en]');
    if (tableInit) tableInit.checked = true, selectLang('en');
    // toggle checkboxes
    document.querySelectorAll('#formSelectFields input[type=checkbox]').forEach(cb => {
        // initialize
        toggleCol('tableID', Number(cb.value), cb.checked ? '' : 'none');
        // inline handlers not needed; keep or remove as desired
    });
}

window.addEventListener('DOMContentLoaded', initializeControls);