//Get form elements
const import_form = document.getElementById('importStudentForm');
const import_modal = document.getElementById('importModal')
const import_closeBtn = import_modal.querySelector('.close-btn')
const import_modalSubmit = import_form.querySelector('button[type="submit"]');
const import_fileInput = import_form.querySelector('input[type="file"');
const importErrorDiv = document.getElementById('importFormErrors');

//Create a new div for success message
const importSuccessDiv = document.createElement('div');
importSuccessDiv.style.color = 'green';
importSuccessDiv.style.fontWeight = 'bold';
importSuccessDiv.style.marginTop = '10px';
import_form.appendChild(importSuccessDiv); //Attach it to the parent form

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
        importSuccessDiv.textContent = '';

        if (data.created_count > 0)
        {
            importSuccessDiv.textContent = `${data.created_count} students imported successfully!`;

            //Reset form
            import_form.reset();
            import_modalSubmit.disabled = true;

            //Reload page to show new students after delay
            setTimeout(() => {
                location.reload();
            }, 3000);
        }

        if(data.errors && data.errors.length > 0)
        {
            importErrorDiv.innerHTML = '<ul style="color:red; max-height:200px; overflow-y:auto;">' +
                data.errors.map(err => `<li>${err}</li>`).join('') +
                '</ul>';

            import_modalSubmit.disabled = false; 
        }
        else if (data.created_count === 0)
        {
            //Generic error if nothing created, no specific errors
            importErrorDiv.textContent = 'No students were imported';
            import_modalSubmit.disabled = false;
        }
    })
    .catch(err => {
        importErrorDiv.style.color = 'red';
        importErrorDiv.textContent = 'Unexpected error occurred.';
        import_modalSubmit.disabled = false;    
    });
});