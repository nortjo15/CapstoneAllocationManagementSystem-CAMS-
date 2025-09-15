import { fetchStudents } from "./student_table.js";
import { removeStudentFromGroup } from "./suggested_groups.js";

// Helpers to open modals
export function openModal() {
    const modal = document.getElementById("addStudentModal");
    if (modal) modal.style.display = "flex";
}

export function openImportModal() {
    const modal = document.getElementById("importModal");
    if (modal) modal.style.display = "flex";
}

export function openFilterModal() {
    const modal = document.getElementById("filterModal");
    if (modal) modal.style.display = "flex";
}

export function openNotesModal(button) 
{
    const modal = document.getElementById("notesModal");
    
    if (modal) modal.style.display = "flex";
    const textarea = document.getElementById("notesTextarea");
    textarea.value = button.dataset.studentNotes || "";
    modal.dataset.studentId = button.dataset.studentId;
}

export function openPreferenceModal(student)
{
    const modal = document.getElementById("preferencesModal");
    const list = document.getElementById("preferencesList");

    if (modal) modal.style.display = "flex";

    //Clear old list
    list.innerHTML = "";

    //Populate ranked preferences
    student.preferences.forEach((pref, idx) => {
        const li = document.createElement("li");
        li.textContent = `${idx + 1}. ${pref.project_title}`;
        list.appendChild(li);
    });
}

export function openRemoveStudentModal(student, group) {
    const modal = document.getElementById("removeStudentModal");
    const msg = document.getElementById("removeStudentMessage");
    const confirmBtn = document.getElementById("confirmRemoveBtn");
    const cancelBtn = document.getElementById("cancelRemoveBtn");
    
    msg.innerHTML = `Remove <span class="student-tag">${student.name} 
        (${student.student_id})</span> from this group?`;
        
    if (modal) modal.style.display = 'flex';

    //Clean Buttons
    confirmBtn.onclick = null;
    cancelBtn.onclick = null;

    confirmBtn.onclick = () => {
        removeStudentFromGroup(student, group);
        modal.style.display = "none";
    };
    cancelBtn.onclick = () => modal.style.display = "none";
}

//Modal for student table pop-up in groups 
export function openStudentModal()
{
    const modal = document.getElementById("studentModal");
    
    if (modal) modal.style.display = 'flex';
    fetchStudents("studentsTableBodyModal", "?allocated_group=false");
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
setupModal("preferencesModal")
setupModal("removeStudentModal")
setupModal("studentModal")