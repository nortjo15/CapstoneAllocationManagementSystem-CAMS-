const addStudentForm = document.getElementById("addStudentForm");
const addStudentModal = document.getElementById("addStudentModal");
const addStudentCloseBtn = addStudentModal ? addStudentModal.querySelector(".close-btn") : null;
const addStudentErrorDiv = document.getElementById("addStudentErrors"); 

if (addStudentForm) {
    addStudentForm.addEventListener("submit", function (e) {
        e.preventDefault();
        addStudentErrorDiv.innerHTML = ""; // clear old errors

        const formData = new FormData(addStudentForm);
        const payload = {};
        const errors = [];

        for (const [key, value] of formData.entries()) {
            payload[key] = value.trim();
        }

        // --- Frontend validation ---
        // Student ID must be exactly 8 digits
        if (!/^\d{8}$/.test(payload.student_id || "")) {
            errors.push("Student ID must be exactly 8 digits.");
        }

        // CWA must be between 0 and 100 (if provided)
        if (payload.cwa) {
            const cwaVal = parseFloat(payload.cwa);
            if (isNaN(cwaVal) || cwaVal < 0 || cwaVal > 100) {
                errors.push("CWA must be a number between 0 and 100.");
            }
        }

        if (errors.length > 0) {
            addStudentErrorDiv.innerHTML = errors.map(err => `<p style="color:red;">${err}</p>`).join("");
            return; // don’t submit if validation fails
        }

        // --- Submit to API ---
        fetch("/api/students/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify(payload),
        })
        .then(res => res.json())
        .then(data => {
            if (!data.errors && !data.error) {
                alert("Student created successfully!");
                addStudentForm.reset();
                if (addStudentModal) addStudentModal.style.display = "none";
                fetchStudents(); // reload table
            } else {
                // Show backend validation errors
                const backendErrors = [];
                for (const [field, messages] of Object.entries(data)) {
                    backendErrors.push(`${field}: ${messages}`);
                }
                addStudentErrorDiv.innerHTML = backendErrors.map(err => `<p style="color:red;">${err}</p>`).join("");
            }
        })
        .catch(err => {
            console.error("Failed to create student", err);
            addStudentErrorDiv.innerHTML = `<p style="color:red;">Request failed. Check console.</p>`;
        });
    });
}

if (addStudentCloseBtn) {
    addStudentCloseBtn.onclick = () => {
        addStudentModal.style.display = "none";
    };
}