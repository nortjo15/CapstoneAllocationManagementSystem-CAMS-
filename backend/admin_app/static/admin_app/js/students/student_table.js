function fetchStudents(params = "") {
    fetch(`/api/students/${params}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("studentsTableBody");
            tbody.innerHTML = "";

            data.forEach(student => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${student.student_id}</td>
                    <td>${student.name}</td>
                    <td>${student.cwa ?? ""}</td>
                    <td>${student.major ? student.major.name : ""}</td>
                    <td>${student.application_submitted ? "Yes" : "No"}</td>
                    <td>${student.allocated_group ? "Yes" : "No"}</td>
                    <td>
                        <button class="notes-btn ${student.notes ? "btn-success" : "btn-secondary"}"
                                data-student-id="${student.student_id}"
                                data-student-notes="${student.notes || ""}"
                                onclick="openNotesModal(this)">
                            Notes
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Failed to fetch students", err));
}

// Load on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchStudents();
})