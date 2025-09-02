// Helpers to open modals
function openModal() {
    const modal = document.getElementById("addStudentModal");
    if (modal) modal.style.display = "flex";
}

function openImportModal() {
    const modal = document.getElementById("importModal");
    if (modal) modal.style.display = "flex";
}

function openFilterModal() {
    const modal = document.getElementById("filterModal");
    if (modal) modal.style.display = "flex";
}

function openNotesModal(button) 
{
    const modal = document.getElementById("notesModal");
    
    if (modal) modal.style.display = "flex";
    const textarea = document.getElementById("notesTextarea");
    textarea.value = button.dataset.studentNotes || "";
    modal.dataset.studentId = button.dataset.studentId;
}

// Attach close + outside click for any modal
function setupModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    // Close button
    const closeBtn = modal.querySelector(".close-btn");
    if (closeBtn) {
        closeBtn.onclick = () => {
            modal.style.display = "none";
        };
    }

    // Close when clicking outside modal content
    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });
}

// Apply to each modal
setupModal("addStudentModal");
setupModal("importModal");
setupModal("filterModal");
setupModal("notesModal");