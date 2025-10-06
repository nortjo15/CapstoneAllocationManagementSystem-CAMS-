import { fetchStudents } from "./student_table.js";
import { removeStudentFromGroup } from "./suggested_groups.js";
import { finaliseGroup, setupFinaliseValidation } from "./final_group.js";

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

export function openMemberPreferenceModal(student)
{
    const modal = document.getElementById("memberPreferenceModal");
    const likesList = document.getElementById("memberPreferencesLikes");
    const avoidsList = document.getElementById("memberPreferencesAvoids");
    const avoidHeader = document.getElementById("avoidHeader");

    if (modal) modal.style.display = "flex";

    //Clear old lists
    likesList.innerHTML = "";
    avoidsList.innerHTML = "";
    avoidHeader.style.display = "none";

    student.group_preferences.forEach((pref, idx) => 
    {
        const li = document.createElement("li");
        li.textContent = `${pref.target_name} (${pref.target_id})`;

        if (pref.preference_type === "like") 
        {
            likesList.appendChild(li);
        } 
        else if (pref.preference_type === "avoid") 
        {
            avoidsList.appendChild(li);
        }
    });

    if (avoidsList.children.length > 0) {
        avoidHeader.style.display = "block";
    }
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

    //Reset filters when re-opening student modal
    const filterForm = document.getElementById("studentFilterForm");
    if (filterForm) filterForm.reset();

    console.log("Fetching:", "/api/admin/students/?allocated_group=false");
    fetchStudents("studentsTableBodyModal", "?allocated_group=false");
}

// Modal for creating a final gruop
export function openCreateGroupModal(groupId)
{
    const modal = document.getElementById("createGroupModal");
    if (modal) modal.style.display = "flex";
    setupFinaliseValidation();

    const confirmBtn = document.getElementById("confirmGroupBtn");
    confirmBtn.onclick = () => {
        const name = document.getElementById("groupNameInput").value.trim();
        const notes = document.getElementById("groupNotesInput").value.trim();

        finaliseGroup(groupId, name, notes);
    }
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
            if (modalId == "studentModal")
            {
                window.selectedStudentIds.clear(); 
            }

            const form = modal.querySelector("form");
            if (form) form.reset();
        };
    }

    // Close when clicking outside modal content
    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
            if (modalId == "studentModal")
            {
                window.selectedStudentIds.clear(); 
            }

            const form = modal.querySelector("form");
            if (form) form.reset();
        }
    });
}

// Apply to each modal
setupModal("addStudentModal");
setupModal("importModal");
setupModal("filterModal");
setupModal("notesModal");
setupModal("preferencesModal");
setupModal("removeStudentModal");
setupModal("studentModal");
setupModal("memberPreferenceModal");
setupModal("createGroupModal");