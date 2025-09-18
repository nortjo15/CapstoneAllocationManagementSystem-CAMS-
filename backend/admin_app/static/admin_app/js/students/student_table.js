import { setButtonLoading } from "./utils.js";
import { openNotesModal, openPreferenceModal, openModal, openImportModal, openFilterModal, openMemberPreferenceModal } from "./modal_function.js";
import { loadGroup } from "./suggested_groups.js";
import { updateGroupUI } from "./render_groups.js";

window.selectedStudentIds = new Set();

// Helper to compute current group capacity info
function getGroupCapacityInfo() {
    const membersCount = window.currentMemberIds ? window.currentMemberIds.size : 0;
    const capacityElem = document.querySelector("#group-capacity p");
    const capacity = capacityElem ? parseInt(capacityElem.textContent.match(/\d+/)) : null;
    const spaceLeft = capacity ? capacity - membersCount : Infinity;

    return { membersCount, capacity, spaceLeft };
}

export function fetchStudents(targetId = "studentsTableBody", params = "") {
    fetch(`/api/students/${params}`)
        .then(res => res.json())
        .then(data => {

            console.log("Rendering for:", targetId);
            
            const tbody = document.getElementById(targetId);
            tbody.innerHTML = "";

            // Work out colspan depending on mode
            const colspan = targetId === "studentsTableBody" ? 8 : 7;

            // Display message if there's no students
            if (data.length === 0) {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td colspan="${colspan}" style="text-align:center;">No Students Found</td>`;
                tbody.appendChild(tr);
                return;
            }

            data.forEach(student => {
                const tr = document.createElement("tr");

                // Build first column with a checkbox only for the modal
                let checkBoxTd = "";
                if (targetId === "studentsTableBodyModal")
                {
                    checkBoxTd = `<td><input type="checkbox" class="student-checkbox" data-student-id="${student.student_id}"></td>`;
                }


                tr.innerHTML = `
                    ${checkBoxTd}
                    <td>${student.student_id}</td>
                    <td>${student.name}</td>
                    <td>${student.cwa ?? ""}</td>
                    <td>${student.major ? student.major.name : ""}</td>
                    <td>${student.application_submitted ? "Yes" : "No"}</td>

                    ${targetId === "studentsTableBody"
                        ? `<td>${student.allocated_group ? "Yes" : "No"}</td>` 
                        : "" }
                `;

                // Restore checked state if student ID is in selectedStudentIds 
                if (targetId === "studentsTableBodyModal")
                {
                    const checkbox = tr.querySelector(".student-checkbox");
                    if (checkbox)
                    {
                        if (window.selectedStudentIds && window.selectedStudentIds.has(student.student_id.toString()))
                        {
                            checkbox.checked = true;
                        }
                    }
                }

                //--- Notes Button ---
                const tdNotes = document.createElement("td");
                const notesBtn = document.createElement("button");
                notesBtn.textContent = "Notes";
                notesBtn.className = "btn btn-secondary";

                if (student.notes && student.notes.trim() !== "")
                {
                    notesBtn.classList.add("has-content");
                }

                notesBtn.dataset.studentId = student.student_id;
                notesBtn.dataset.studentNotes = student.notes || "";
                notesBtn.addEventListener("click", () => openNotesModal(notesBtn));
                tdNotes.appendChild(notesBtn);
                tr.appendChild(tdNotes);

                //--- Preferences Button ---
                const tdPrefs = document.createElement("td");
                const prefsBtn = document.createElement("button");
                prefsBtn.textContent = "Project Prefs";

                if (student.has_preferences)
                {
                    prefsBtn.className = "btn btn-secondary";
                    prefsBtn.addEventListener("click", (e) => 
                    {
                        e.stopPropagation();

                        //Get the full student before opening modal
                        fetch(`/api/students/${student.student_id}/`)
                            .then(res => res.json())
                            .then(fullStudent => openPreferenceModal(fullStudent))
                    });
                }
                else 
                {
                    prefsBtn.className = "btn btn-secondary"; 
                    prefsBtn.disabled = true;
                }

                tdPrefs.appendChild(prefsBtn);
                tr.appendChild(tdPrefs);

                // -- Member Preferences Button
                const tdMemberPrefs = document.createElement("td");
                const memberPrefsBtn = document.createElement("button");
                memberPrefsBtn.textContent = "Team Prefs";

                if (student.has_teamPref)
                {
                    memberPrefsBtn.className = "btn btn-secondary";
                    memberPrefsBtn.addEventListener("click", (e) => 
                    {
                        e.stopPropagation();

                        //Get full student before opening modal
                        fetch(`/api/students/${student.student_id}`)
                            .then(res => res.json())
                            .then(fullStudent => openMemberPreferenceModal(fullStudent))
                    })
                }
                else 
                {
                    memberPrefsBtn.className = "btn btn-secondary";
                    memberPrefsBtn.disabled = true;
                }

                tdMemberPrefs.appendChild(memberPrefsBtn);
                tr.appendChild(tdMemberPrefs)


                if (targetId === "studentsTableBodyModal")
                {
                    const checkbox = tr.querySelector(".student-checkbox");
                    const isAlreadyMember = window.currentMemberIds && window.currentMemberIds.has(student.student_id)

                    if (isAlreadyMember)
                    {
                        //Disable checkbox if already in group
                        checkbox.disabled = true; 
                        tr.style.opacity = "0.5";
                        tr.title = "Already in this group";
                    }
                }

                //Append row to the table
                tbody.appendChild(tr);   
            });

            //Enforce Capacity Rules
            if (targetId === "studentsTableBodyModal") 
            {
                enforceCapacityRules();
            }    
        })
        .catch(err => console.error("Failed to fetch students", err));
}

//Track checkbox changes to enable / disable the Add Button
document.addEventListener("change", (e) => {
    if (e.target.classList.contains("student-checkbox"))
    {
        //maintain state globally so filtering restores it
        const id = e.target.dataset.studentId; 

        if (e.target.checked)
        {
            window.selectedStudentIds.add(id.toString());
        }
        else 
        {
            window.selectedStudentIds.delete(id.toString());
        }

        enforceCapacityRules();
    }
});

//Enforces Group Capacity rules 
export function enforceCapacityRules() 
{
    const checkboxes = document.querySelectorAll(".student-checkbox");
    const totalSelected = window.selectedStudentIds.size; 
    const addBtn = document.getElementById("addSelectedBtn");

    if (addBtn) {
        addBtn.disabled = totalSelected === 0; 
    }

    const { spaceLeft } = getGroupCapacityInfo();

    if (totalSelected >= spaceLeft) {
        checkboxes.forEach(cb => {
            if (!cb.checked && !window.currentMemberIds.has(cb.dataset.studentId)) {
                cb.disabled = true; 
                cb.closest("tr").style.opacity = "0.5";  
                cb.closest("tr").style.cursor = "not-allowed";
            }
        }); 
    } else {
        checkboxes.forEach(cb => {
            if (!window.currentMemberIds.has(cb.dataset.studentId)) {
                cb.disabled = false;
                cb.closest("tr").style.opacity = "1"; 
                cb.closest("tr").style.cursor = "default";
            }
        });
    }
}

// Handle Add Button click
const addBtn = document.getElementById("addSelectedBtn");

addBtn.addEventListener("click", (e) => 
{
    setButtonLoading(addBtn, true)
    const selectedIds = Array.from(window.selectedStudentIds);
    if (!selectedIds.length) 
    {
        setButtonLoading(addBtn, false);
        return;
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    Promise.all(
        selectedIds.map(id => 
            fetch(`/api/suggested_groups/${activeGroupId}/add_student/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ student_id: id }),
            }).then(res => {
                if (!res.ok) throw new Error("Failed to add student " + id);
                return res.json();
            })
        )
    )
    .then((updatedGroups) => {
        console.log("Add response:", updatedGroups);

        const updatedGroup = updatedGroups[updatedGroups.length - 1];
        window.suggestedGroupsCache.set(parseInt(activeGroupId), updatedGroup);

        //Render UI
        loadGroup(activeGroupId);
        enforceCapacityRules();

        document.getElementById("studentModal").style.display = "none";
        window.selectedStudentIds.clear();
    })
    .catch(err => {
        console.error("Error adding students:", err);

        // Invalidate cache and reload from backend
        window.suggestedGroupsCache.delete(parseInt(activeGroupId));
        loadGroup(activeGroupId);
    })
    .finally(() => {
        setButtonLoading(addBtn, false)
    });
});

const addStudentBtn = document.getElementById("addStudentBtn")
const importStudentBtn = document.getElementById("importStudentBtn")
const openFiltersBtn_s = document.getElementById("openFilterBtnStudents");

if (addStudentBtn) addStudentBtn.addEventListener("click", openModal);
if (importStudentBtn) importStudentBtn.addEventListener("click", openImportModal);
if (openFiltersBtn_s) openFiltersBtn_s.addEventListener("click", openFilterModal);

// Function to apply filters and search the student table 
function applyFiltersAndSearch(targetId, searchVal= "")
{
    const form = document.getElementById("studentFilterForm");
    const params = new URLSearchParams();

    //Collect filter form data
    if (form)
    {
        const formData = new FormData(form);
        for (const [key, value] of formData.entries())
        {
            if (value && value.trim() !== "" && key !== "major")
            {
                params.append(key, value);
            }
        }
        //Multi-value majors 
        const majors = formData.getAll("major");
        majors.forEach(m => 
        {
            if (m && m.trim() != "") params.append("major", m);
        });
    }

    //Add search param
    if (searchVal)
    {
        params.append("student_id", searchVal);
    }

    fetchStudents(targetId, "?" + params.toString());
}


// Search by Student ID 
const studentIdSearch = document.getElementById("studentIdSearch");
if (studentIdSearch)
{
    studentIdSearch.addEventListener("input", (e) => 
    {
        const searchVal = e.target.value.trim();
        applyFiltersAndSearch("studentsTableBody", searchVal);
    });
}

// Search by Student ID (modal)
const studentIdSearchModal = document.getElementById("studentIdSearchModal");
if (studentIdSearchModal) 
{
    studentIdSearchModal.addEventListener("input", (e) => 
    {
        const searchVal = e.target.value.trim();
        applyFiltersAndSearch("studentsTableBodyModal", searchVal);
    });
}