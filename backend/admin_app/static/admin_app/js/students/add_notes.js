const notesForm = document.getElementById("notesForm");
const notesModal = document.getElementById("notesModal");
const notesTextarea = document.getElementById("notesTextarea");

if (notesForm) {
    notesForm.addEventListener("submit", function (e) {
        e.preventDefault(); // stop page reload

        const studentId = notesModal.dataset.studentId;
        const notes = notesTextarea.value.trim();

        //Get CSRF token from hidden input
        const csrfTokenInput = notesForm.querySelector("input[name='csrfmiddlewaretoken']");
        const csrfToken = csrfTokenInput ? csrfTokenInput.value : "";

        fetch(`/api/students/${studentId}/notes/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ notes: notes })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // close modal
                notesModal.style.display = "none";

                // update button in table
                const button = document.querySelector(
                    `button[data-student-id="${studentId}"]`
                );
                if (button) {
                    button.dataset.studentNotes = notes;

                    if (notes === "") {
                        button.classList.remove("btn-primary");
                        button.classList.add("btn-secondary");
                    } else {
                        button.classList.remove("btn-secondary");
                        button.classList.add("btn-primary");
                    }
                }
            } else {
                alert("Error: " + (data.error || "Unknown error"));
            }
        })
        .catch(err => console.error("Request failed", err));
    });
}