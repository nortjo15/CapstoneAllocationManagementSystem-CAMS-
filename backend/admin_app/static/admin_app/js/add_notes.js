const notes_form = document.getElementById('notesForm')
const notes_modal = document.getElementById('notesModal');
const notes_textarea = document.getElementById('notesTextarea');
const notes_closeBtn = notes_modal.querySelector('.close-btn')

//Function to open the notes Modal
function openNotesModal(button)
{
    notes_textarea.value = button.dataset.studentNotes || ''
    notes_modal.dataset.studentId = button.dataset.studentId; 
    notes_modal.style.display = 'flex';
}

//Close Modal
notes_closeBtn.onclick = () =>
{
    notes_modal.style.display = 'none';
}

window.onclick = (e) => 
{
    if (e.target == notes_modal)
    {
        notes_modal.style.display = 'none';
    }
}

// Handle AJAX
notes_form.addEventListener('submit', function(e)
{
    e.preventDefault();
    const studentId = notes_modal.dataset.studentId;
    const notes = notes_textarea.value 

    fetch("{% url 'admin_dashboard:update_student_notes' %}", 
    {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value 
        },

        body: new URLSearchParams({
            'student_id': studentId, 
            'notes': notes
        })
    })
    .then(res => res.json())
    .then(data => 
    {
        if (data.success) 
            {
            notes_modal.style.display = 'none'; //Close modal upon success
            alert("Notes saved successfully!");

            //Update button colour in the table 
        } 
        else 
        {
            alert("Error: " + data.error);
        }
    })
    .catch(err => console.error(err));
});