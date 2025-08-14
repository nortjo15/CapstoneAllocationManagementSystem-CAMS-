//Get form elements
const import_form = document.getElementById('importStudentForm');
const import_modal = document.getElementById('importModal')
const import_closeBtn = import_modal.querySelector('.close-btn')
const import_modalSubmit = import_form.querySelector('button[type="submit"]');
const import_fileInput = import_form.querySelector('input[type="file"');
const importErrorDiv = document.getElementById('importFormErrors');

function openImportModal()
{
    import_modalSubmit.disabled = true; 
    import_modal.style.display = 'flex';
}

import_closeBtn.onclick = () => import_modal.style.display = 'none';
window.onclick = (e) => {
    if (e.target == import_modal) import_modal.style.display = 'none';
}

//Listen for changes
import_fileInput.addEventListener('change', () => {
    if (import_fileInput.isDefaultNamespace.length > 0)
    {
        import_modalSubmit.disabled=false; 
    }
    else 
    {
        import_modalSubmit.disabled=true;
    }   
})

//AJAX Submission
import_form.addEventListener('submit', function(e)
{
    e.preventDefault(); //Prevent normal form submit

    const importFormData = new FormData(import_form)

    //Disable button to prevent multiple submissions
    import_modalSubmit.disabled = true;

    fetch(import_form.action, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: importFormData
    })
    .then(response => response.json())
    .then(data => {
        //Clear previous error messages
        importErrorDiv.innerHTML = '';

        if(data.success || data.skipped_count > 0) {
            let summaryHTML = `
                <p style=font-weight:bold; color:green;">
                    ${data.created_count} students imported successfully.
                </p>
                <p styl="font-weight:bold; color:red;">
                    ${data.skipped_count} students skipped.
                </p>
                <p style="font-weight:bold; color:orange;">
                    ${data.duplicate_count} duplicates skipped.
                </p>
            `;

            //Message
            importErrorDiv.style.color = 'green';
            importErrorDiv.textContent = `${data.created_count} students imported successfully!`;

            //Reset form
            import_form.reset();
            import_modalSubmit.disabled = true;
            import_modal.style.display = 'none';

            //Reload page to show new students
            location.reload();
        }
        else 
        {
            //Display errors returned 
            importErrorDiv.style.color = 'red';
            if (Array.isArray(data.errors))
            {
                importErrorDiv.innerHTML = data.errors.json('<br>');
            }
            else 
            {
                importErrorDiv.textContent = 'Error importing students.';
            }
        }
    })
    .catch(err => {
        importErrorDiv.style.color = 'red';
        importErrorDiv.textContent = 'Unexpected error occurred.';
    })
    .finally(() => {
        import_modalSubmit.disabled = false;
    });
});