import { openFilterModal } from "./modal_function.js";
import { fetchStudents } from "./student_table.js";

console.log("student_filters.js loaded");

const filterForm = document.getElementById("studentFilterForm");
const resetBtn = document.getElementById("reset-btn");
const cwaMinInput = document.getElementById("cwa_min");
const cwaMaxInput = document.getElementById("cwa_max");
const cwaError = document.getElementById("cwa_error"); 
const filterBtn = filterForm ? filterForm.querySelector("button[type='submit']") : null;

//Make sure CWA range is appropriate
function validateRange() {
    const minVal = parseFloat(cwaMinInput.value);
    const maxVal = parseFloat(cwaMaxInput.value);

    if (!isNaN(minVal) && !isNaN(maxVal) && maxVal < minVal) {
        cwaError.textContent = "Max CWA cannot be less than Min CWA.";
        cwaError.style.color = "red";
        cwaError.style.display = "block"; 
        if (filterBtn) filterBtn.disabled = true;
        return false;
    }

    //Clear errors
    cwaError.textContent = "";
    if (filterBtn) filterBtn.disabled = false;
    cwaError.style.display = "none";
    return true;
}

//Keep wtihin ranges
function clamp(input) {
    let val = parseFloat(input.value);
    if (!isNaN(val)) 
    {
        if (val < 0) val = 0;
        if (val > 100) val = 100;
        input.value = val;
    }
}

if (cwaMinInput) {
    cwaMinInput.addEventListener("input", () => {
        clamp(cwaMinInput);
        validateRange();
    });
}

if (cwaMaxInput) {
    cwaMaxInput.addEventListener("input", () => {
        clamp(cwaMaxInput);
        validateRange();
    });
}


if (filterForm) {
    filterForm.addEventListener("submit", function (e) {
        e.preventDefault();

        //central validation
        if (!validateRange()) return

        const formData = new FormData(filterForm);
        const params = new URLSearchParams();

        const majors = formData.getAll("major");
        majors.forEach(m => {
            if (m && m.trim() !== "") 
            {
                params.append("major", m);
            }
        });

        for (const [key, value] of formData.entries()) 
        {
            if (key === "major") continue;
            if (value && value.trim() !== "") {
                params.append(key, value);
            }
        }

        // decide target
        let targetId = "studentsTableBody";
        if (document.getElementById("studentsTableBodyModal")) {
            targetId = "studentsTableBodyModal";
        }

        fetchStudents(targetId, "?" + params.toString());

        //Close modal upon success
        const filterModal = document.getElementById("filterModal");
        if (filterModal) {
            filterModal.style.display = "none";
        }
    });
}

if (resetBtn) {
    resetBtn.addEventListener("click", function () {
        filterForm.reset();
        cwaError.textContent = "";
        if (filterBtn) filterBtn.disabled = false;
        
        let targetId = "studentsTableBody";
        if (document.getElementById("studentsTableBodyModal")) {
            targetId = "studentsTableBodyModal";
        }

        fetchStudents(targetId); //Reload
    });
}

const openFiltersBtn = document.getElementById("openFilterBtn");
if (openFiltersBtn) openFiltersBtn.addEventListener("click", openFilterModal);