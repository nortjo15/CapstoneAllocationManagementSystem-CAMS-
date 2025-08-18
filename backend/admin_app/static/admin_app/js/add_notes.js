//Function to open the notes Modal
function openNotesModal(button)
{
    const notes_modal = document.getElementById('notesModal');
    const notes_textarea = document.getElementById('notesTextarea');
    notes_textarea.value = button.dataset.studentNotes || ''
    notes_modal.dataset.studentId = button.dataset.studentId; 
    notes_modal.style.display = 'flex';
}

//Close Modal
document.querySelector('#notesModal .close-btn').onclick = function() {
    document.getElementById('notesModal').style.display = 'none';
}
window.onclick = function(e) {
    const notes_modal = document.getElementById('notesModal');
    if (e.target == notes_modal) modal.style.display = 'none';
}

// Handle AJAX
document.getElementById('notesForm').addEventListener('submit', function(e){
    e.preventDefault();
    const studentId = document.getElementById('notesModal').dataset.studentId;
    const notes = document.getElementById('notesTextarea').value;
});