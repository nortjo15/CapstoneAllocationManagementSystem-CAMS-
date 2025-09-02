const filterForm = document.getElementById("studentFilterForm");
const resetBtn = document.getElementById("reset-btn");
const cwaMinInput = document.getElementById("cwa_min");
const cwaMaxInput = document.getElementById("cwa_max");
const cwaError = document.getElementById("cwa_error"); 

if (filterForm) {
    filterForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const cwaMin = parseFloat(cwaMinInput.value) || null;
        const cwaMax = parseFloat(cwaMaxInput.value) || null;

        // Validation
        if ((cwaMin !== null && (cwaMin < 0 || cwaMin > 100)) ||
            (cwaMax !== null && (cwaMax < 0 || cwaMax > 100))) {
            cwaError.textContent = "CWA must be between 0 and 100.";
            cwaError.style.color = "red";
            return;
        }

        if (cwaMin !== null && cwaMax !== null && cwaMax < cwaMin) {
            cwaError.textContent = "Max CWA cannot be less than Min CWA.";
            cwaError.style.color = "red";
            return;
        }

        cwaError.textContent = "";

        const formData = new FormData(filterForm);
        const params = new URLSearchParams();

        for (const [key, value] of formData.entries()) {
            if (value && value.trim() !== "") {
                params.append(key, value);
            }
        }

        fetchStudents("?" + params.toString());
    });
}

if (resetBtn) {
    resetBtn.addEventListener("click", function () {
        filterForm.reset();
        cwaError.textContent = "";
        fetchStudents();
    });
}
