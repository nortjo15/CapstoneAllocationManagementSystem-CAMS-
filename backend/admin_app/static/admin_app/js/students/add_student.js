const addStudentForm = document.getElementById("addStudentForm");
const addStudentModal = document.getElementById("addStudentModal");
const addStudentCloseBtn = addStudentModal ? addStudentModal.querySelector(".close-btn") : null;
const addStudentErrorDiv = document.getElementById("addStudentErrors"); 
const submitBtn = document.getElementById("addStudentSubmit");

// Inline validation elements
const studentIdInput = addStudentForm ? addStudentForm.querySelector("input[name='student_id']") : null;
const cwaInput = addStudentForm ? addStudentForm.querySelector("input[name='cwa']") : null;

// --- Frontend live validation for Student ID ---
if (studentIdInput) {
    const errorEl = document.createElement("div");
    errorEl.id = "studentIdError";
    errorEl.style.color = "red";
    studentIdInput.insertAdjacentElement("afterend", errorEl);

    studentIdInput.addEventListener("input", () => {
        const val = studentIdInput.value.trim();
        if (!/^\d{8}$/.test(val)) {
            errorEl.textContent = "Student ID must be exactly 8 digits.";
            submitBtn.disabled = true;
        } else {
            errorEl.textContent = "";
            submitBtn.disabled = false;
        }
    });
}

// --- Clamp CWA within value range ---
if (cwaInput) {
    cwaInput.addEventListener("input", () => {
        let val = parseFloat(cwaInput.value);
        if (isNaN(val)) return;
        if (val < 0) val = 0;
        if (val > 100) val = 100;
        cwaInput.value = val;
    });
}

if (addStudentForm) {
    addStudentForm.addEventListener("submit", function (e) {
        e.preventDefault();
        addStudentErrorDiv.innerHTML = ""; // clear old errors

        const formData = new FormData(addStudentForm);
        const payload = {};

        for (const [key, value] of formData.entries()) {
            payload[key] = value.trim();
        }

        // --- Frontend validation before sending ---
        const errors = [];
        if (!/^\d{8}$/.test(payload.student_id || "")) {
            errors.push("Student ID must be exactly 8 digits.");
        }
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

        // Get CSRF token from hidden input
        const csrfTokenInput = addStudentForm.querySelector("input[name='csrfmiddlewaretoken']");
        const csrfToken = csrfTokenInput ? csrfTokenInput.value : "";

        // --- Submit to API ---
        fetch("/api/students/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(payload),
        })
        .then(async res => {
            const text = await res.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch {
                throw { non_field_errors: [`Server returned non-JSON response`, text.slice(0, 200)] };
            }
            if (!res.ok) throw data;
            return data;
        })
        .then(data => {
            alert("Student created successfully!");
            addStudentForm.reset();
            if (addStudentModal) addStudentModal.style.display = "none";
            fetchStudents("studentsTableBody"); // reload table
        })
        .catch(err => {
            console.error("Failed to create student", err);
            const backendErrors = [];
            for (const [field, messages] of Object.entries(err)) {
                backendErrors.push(`${field}: ${messages.join(", ")}`);
            }
            addStudentErrorDiv.innerHTML = backendErrors.map(m => `<p style="color:red;">${m}</p>`).join("");
        });
    });
}

if (addStudentCloseBtn) {
    addStudentCloseBtn.onclick = () => {
        addStudentModal.style.display = "none";
    };
}