import { setButtonLoading } from "./utils";

// Helper to compute current group capacity info
function getGroupCapacityInfo() {
    const membersCount = window.currentMemberIds ? window.currentMemberIds.size : 0;
    const capacityElem = document.querySelector("#group-capacity p");
    const capacity = capacityElem ? parseInt(capacityElem.textContent.match(/\d+/)) : null;
    const spaceLeft = capacity ? capacity - membersCount : Infinity;

    return { membersCount, capacity, spaceLeft };
}

function fetchStudents(targetId = "studentsTableBody", params = "") {
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
                prefsBtn.textContent = "Preferences";

                if (student.preferences && student.preferences.length > 0)
                {
                    prefsBtn.className = "btn btn-secondary";
                    prefsBtn.addEventListener("click", (e) => {
                        e.stopPropagation();
                        openPreferenceModal(student);
                    });
                }
                else 
                {
                    prefsBtn.className = "btn btn-secondary"; 
                    prefsBtn.disabled = true;           
                }

                tdPrefs.appendChild(prefsBtn);
                tr.appendChild(tdPrefs);

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
        })
        .catch(err => console.error("Failed to fetch students", err));
}

//Callable from elsewhere
window.fetchStudents = fetchStudents;

//Track checkbox changes to enable / disable the Add Button
document.addEventListener("change", (e) => {
    if (e.target.classList.contains("student-checkbox"))
    {
        const checkboxes = document.querySelectorAll(".student-checkbox");
        const checked = document.querySelectorAll(".student-checkbox:checked");
        const addBtn = document.getElementById("addSelectedBtn");

        if (addBtn)
        {
            addBtn.disabled = checked.length === 0; 
        }

        const { spaceLeft } = getGroupCapacityInfo();

        if (checked.length >= spaceLeft)
        {
            //Disable all other checkboxes 
            checkboxes.forEach(cb => {
                if (!cb.checked) cb.disabled = true; 
            }); 
        }
        else 
        {
            checkboxes.forEach(cb => {
                if (!window.currentMemberIds.has(cb.dataset.studentId))
                {
                    cb.disabled = false;
                }
            });
        }
    }
});

// Handle Add Button click
const addBtn = document.getElementById("addSelectedBtn");

addBtn.addEventListener("click", (e) => 
{
    setButtonLoading(addBtn, true)
    const checkboxes = document.querySelectorAll(".student-checkbox:checked");
    if (!checkboxes.length) 
    {
        setButtonLoading(addBtn, false);
        return;
    }
    
    const selectedIds = Array.from(checkboxes).map(cb => cb.dataset.studentId);

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
    .then(() => {
        loadGroup(activeGroupId);
        document.getElementById("studentModal").style.display = "none";
    })
    .catch(err => console.error("Error adding students:", err))
    .finally(() => {
        setButtonLoading(addBtn, false)
    });
});