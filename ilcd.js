// ilcd.js
// Moved JavaScript from HTML to external file

/**
 * Toggle language columns and definitions
 * @param {string} strLang - 'en' or 'de'
 */
function selectLang(strLang) {
    var checkFieldNameEn = document.getElementById('checkFieldNameEn');
    var checkFieldNameDe = document.getElementById('checkFieldNameDe');
    var checkDefinitionEn = document.getElementById('checkDefinitionEn');
    var checkDefinitionDe = document.getElementById('checkDefinitionDe');

    if (strLang === 'en') {
        checkFieldNameEn.checked = true;
        checkFieldNameDe.checked = false;
        checkDefinitionEn.checked = true;
        checkDefinitionDe.checked = false;

        toggleCol('tableID', 0, 'none');
        toggleCol('tableID', 1, '');
        toggleCol('tableID', 6, 'none');
        toggleCol('tableID', 7, '');
    } else {
        checkFieldNameEn.checked = false;
        checkFieldNameDe.checked = true;
        checkDefinitionEn.checked = false;
        checkDefinitionDe.checked = true;

        toggleCol('tableID', 0, '');
        toggleCol('tableID', 1, 'none');
        toggleCol('tableID', 6, '');
        toggleCol('tableID', 7, 'none');
    }
}

/**
 * Show or hide a column in the table
 * @param {string} strID - ID of the table
 * @param {number} intCol - zero-based column index
 * @param {string|null} strDisplay - 'none' to hide, '' to show, or null to toggle
 */
function toggleCol(strID, intCol, strDisplay) {
    var objTable = document.getElementById(strID);
    if (!objTable) return;
    if (strDisplay == null) {
        strDisplay = (objTable.rows[0].cells[intCol].style.display === 'none') ? '' : 'none';
    }

    var currentStatus = (objTable.rows[0].cells[intCol].style.display === 'none') ? 'hide' : 'show';
    var newStatus = (strDisplay === 'none') ? 'hide' : 'show';

    var action;
    if (currentStatus === 'hide' && newStatus === 'show') action = 'show';
    else if (currentStatus === 'show' && newStatus === 'hide') action = 'hide';
    else action = 'none';

    // Toggle each cell in that column
    for (var i = 0; i < objTable.rows.length; i++) {
        var cell = objTable.rows[i].cells[intCol];
        if (cell && cell.colSpan === 1) {
            cell.style.display = strDisplay;
        }
    }

    // Adjust colSpan for cells that span multiple columns
    var objCells = objTable.getElementsByTagName('td');
    for (var j = 0; j < objCells.length; j++) {
        var td = objCells[j];
        if (td.colSpan > 1) {
            if (action === 'hide') td.colSpan--;
            else if (action === 'show') td.colSpan++;
        }
    }
}

/**
 * Initialize column visibility based on checked boxes
 */
function initializeColumns() {
    var form = document.getElementById('formSelectFields');
    if (!form) return;

    for (var i = 0; i < form.elements.length; i++) {
        var el = form.elements[i];
        if (el.type === 'checkbox') {
            toggleCol('tableID', parseInt(el.value, 10), el.checked ? '' : 'none');
        }
    }
    // Default to English
    selectLang('en');
}

// Run on page load
window.onload = initializeColumns;