const importForm = document.getElementById("studentImportForm");
const importModal = document.getElementById("importModal");
const importCloseBtn = importModal ? importModal.querySelector(".close-btn") : null;
const importFormErrors = document.getElementById("importFormErrors");

if (importForm) {
    importForm.addEventListener("submit", function (e) {
        e.preventDefault();
        importFormErrors.innerHTML = ""; // clear old errors

        const formData = new FormData(importForm);

        fetch("/api/students/import/", {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"), // CSRF if enabled
            },
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(
                    `Imported successfully! Created: ${data.created_count}, ` +
                    `Updated: ${data.updated_count}, Skipped: ${data.skipped_count}`
                );
                importForm.reset();
                if (importModal) importModal.style.display = "none";
                fetchStudents(); // reload table with new data
            } else {
                // Show backend errors inline
                if (data.error) {
                    importFormErrors.innerHTML = `<p>${data.error}</p>`;
                }
                if (data.errors && data.errors.length > 0) {
                    importFormErrors.innerHTML +=
                        "<ul>" +
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
    };
}