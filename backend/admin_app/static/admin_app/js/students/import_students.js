const importForm = document.getElementById("studentImportForm");
const importModal = document.getElementById("importModal");
const importCloseBtn = importModal ? importModal.querySelector(".close-btn") : null;
const importFormErrors = document.getElementById("importFormErrors");

if (importForm) {
    importForm.addEventListener("submit", function (e) {
        e.preventDefault();
        importFormErrors.innerHTML = ""; // clear old errors

        const formData = new FormData(importForm);
        const importUrl = importModal.dataset.importUrl; 

        const csrfTokenInput = importForm.querySelector("input[name='csrfmiddlewaretoken']");
        const csrfToken = csrfTokenInput ? csrfTokenInput.value : "";

        fetch(importUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken, // CSRF if enabled
            },
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) 
            {
                // Show success inline
                importFormErrors.innerHTML =
                `<p style="color:green;">
                    Imported successfully!<br>
                    Created: ${data.created_count}, Updated: ${data.updated_count}, Skipped: ${data.skipped_count}
                </p>`;
    
                if (data.errors && data.errors.length > 0)
                {
                    importFormErrors.innerHTML +=
                    "<ul style='color:red;'>" +
                    data.errors.map(err => `<li>${err}</li>`).join("") +
                    "</ul>";
                }

                importForm.reset();

            }
            else 
            {
                // Always render errors inline
                importFormErrors.innerHTML = "";
                if (data.error) 
                {
                    importFormErrors.innerHTML += `<p style="color:red;">${data.error}</p>`;
                }
                if (data.errors && data.errors.length > 0) 
                {
                    importFormErrors.innerHTML +=
                        "<ul style='color:red;'>" +
                        data.errors.map(err => `<li>${err}</li>`).join("") +
                        "</ul>";
                }
            }
        })
        .catch(err => {
            console.error("Import request failed", err);
            importFormErrors.innerHTML = "<p>Request failed. Check console.</p>";
        });
    });
}

if (importCloseBtn) {
    importCloseBtn.onclick = () => {
        importModal.style.display = "none";
        fetchStudents("studentsTableBody"); // reload table when actively closed
    };
}

window.onclick = (e) => {
    if (e.target === importModal) {
        importModal.style.display = "none";
        fetchStudents("studentsTableBody"); // reload table when clicking outside
    }
};