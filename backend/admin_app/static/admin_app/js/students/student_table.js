function fetchStudents(params = "") {
    fetch(`/api/students/${params}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("studentsTableBody");
            tbody.innerHTML = "";

            //Display message if there's no students
            if (data.length === 0)
            {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td colspan="8" style="text-align:center;">No Students Found</td>`;
                tbody.appendChild(tr);
                return;
            }

            data.forEach(student => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${student.student_id}</td>
                    <td>${student.name}</td>
                    <td>${student.cwa ?? ""}</td>
                    <td>${student.major ? student.major.name : ""}</td>
                    <td>${student.application_submitted ? "Yes" : "No"}</td>
                    <td>${student.allocated_group ? "Yes" : "No"}</td>
                    `;

                //--- Notes Button ---
                const tdNotes = document.createElement("td");
                const notesBtn = document.createElement("button");
                notesBtn.textContent = "Notes";
                notesBtn.className = student.notes ? "btn-primary" : "btn-secondary";
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
                    prefsBtn.className = "btn-primary";
                    prefsBtn.addEventListener("click", (e) => {
                        e.stopPropagation();
                        openPreferenceModal(student);
                    });
                }
                else 
                {
                    prefsBtn.className = "btn-primary"; 
                    prefsBtn.disabled = true;           
                }

                tdPrefs.appendChild(prefsBtn);
                tr.appendChild(tdPrefs);

                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Failed to fetch students", err));
}

// Load on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchStudents();
})