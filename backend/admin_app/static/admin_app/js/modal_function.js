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