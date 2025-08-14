//Get form elements
const import_form = document.getElementById('importStudentForm');
const import_modal = document.getElementById('importModal')
const import_closeBtn = import_modal.querySelector('close-btn')
const import_modalSubmit = import_form.querySelector('button[type="submit"]');

function openImportModal()
{
    import_modalSubmit.disabled = true; 
    import_modal.style.display = 'flex';
}

import_closeBtn.onclick = () => import_modal.style.display = 'none';
window.onclick = (e) => {
    if (e.target == import_modal) modal.style.display = 'none';
}