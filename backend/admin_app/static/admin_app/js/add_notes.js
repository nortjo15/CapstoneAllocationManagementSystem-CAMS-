notes_form.addEventListener('submit', function(e) {
    e.preventDefault();
    const studentId = notes_modal.dataset.studentId;
    const notes = notes_textarea.value.trim();

    fetch(`/api/students/${studentId}/notes/`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),  // if CSRF is enforced
        },
        body: JSON.stringify({ notes: notes })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            notes_modal.style.display = 'none';
            alert("Notes saved successfully!");

            // Update button in table
            const button = document.querySelector(`button[data-student-id="${studentId}"]`);
            if (button) {
                button.dataset.studentNotes = notes;

                if (notes === "") {
                    button.classList.remove("btn-success");
                    button.classList.add("btn-secondary");
                } else {
                    button.classList.remove("btn-secondary");
                    button.classList.add("btn-success");
                }
            }
        } else {
            alert("Error: " + (data.error || "Unknown error"));
        }
    })
    .catch(err => console.error("Request failed", err));
});