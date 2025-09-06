
//Helper functions for suggested_groups.js
function renderMemberCard(m, group) 
{
    const div = document.createElement("div");
    div.classList.add("card", "member-card");

    // member details
    div.innerHTML = `
        <p><strong>Name:</strong> ${m.student.name}</p>
        <p><strong>ID:</strong> ${m.student.student_id}</p>
        <p><strong>CWA:</strong> ${m.student.cwa}</p>
    `;

    // remove button
    const removeBtn = document.createElement("span");
    removeBtn.classList.add("remove-btn");
    removeBtn.innerHTML = "&times;";
    removeBtn.title = "Remove student";
    removeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        openRemoveStudentModal(m.student, group);
    });

    // Notes Button
    const notesBtn = document.createElement("span");
    notesBtn.classList.add("secondary-btn");
    notesBtn.textContent = "Notes";
    notesBtn.title = ("Open notes");

    //Indicate if notes exist
    if (m.student.notes && m.student.notes.trim() != "")
    {
        notesBtn.classList.add("has-content");
    }

    notesBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        openNotesModal({
            dataset: {
                studentId: m.student.student_id, 
                studentNotes: m.student.notes || ""
            }
        });
    });

    // Preferences Button
    const prefBtn = document.createElement("span");
    prefBtn.classList.add("secondary-btn");
    prefBtn.textContent = "Preferences";
    prefBtn.title = ("Open preferences");

    //Disable button if no preferences
    if (!m.student.preferences || m.student.preferences.length == 0) 
    {
        prefBtn.classList.add("disabled");
        prefBtn.style.opacity = "0.5";
        prefBtn.style.cursor = "not-allowed";
    }
    else 
    {
        prefBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            openPreferenceModal(m.student);
        })
    }

    div.appendChild(removeBtn);
    div.appendChild(notesBtn);
    div.appendChild(prefBtn);
    return div;
}

function renderAddStudentCard(group) 
{
    const addDiv = document.createElement("div");
    addDiv.textContent = "+ Add Student";
    addDiv.classList.add("card", "add-student-card");
    addDiv.addEventListener("click", () => {
        openStudentModal();
    });
    return addDiv;
}

function renderProjectInfo(group, groupSize, projectName, 
    projectCapacity, projectHost, createBtn) 
{
    const size = group.members.length
    const capacity = group.project.capacity
    groupSize.innerHTML = `<p><strong>Group Size:</strong> ${size}</p>`

    if (group.project) 
    {
        projectName.innerHTML = `<p><strong>Project:</strong> ${group.project.title}</p>`;
        projectCapacity.innerHTML = `<p><strong>Project Capacity:</strong> ${capacity}</p>`;
        projectHost.innerHTML = `<p><strong>Host:</strong> ${group.project.host_name}</p>`;

        //See if there's a mismatch in groupSize & Capacity
        if (size !== capacity)
        {
            projectCapacity.querySelector("p").style.color = "red";
            groupSize.querySelector("p").style.color = "red";
            createBtn.disabled = true;
        }
        else 
        {
            projectCapacity.querySelector("p").style.color = "";
            groupSize.querySelector("p").style.color = "";
            createBtn.disabled = false;
        }
    } 
    else 
    {
        projectName.innerHTML = "";
        projectCapacity.innerHTML = "";
        projectHost.innerHTML = "";
    }
}

function renderCWARange(group, groupSize)
{
    if (group.members.length > 0)
    {
        //Clear old CWA Range
        const existing = document.getElementById("cwa-range");
        if (existing) existing.remove();

        const cwas = group.members.map(m => m.student.cwa).filter(c => c!= null);
        if (cwas.length > 0)
        {
            const minCwa = Math.min(...cwas);
            const maxCwa = Math.max(...cwas);

            const cwaElem = document.createElement("p");
            cwaElem.id = "cwa-range";
            cwaElem.innerHTML = `<strong>CWA Range:</strong> ${minCwa} - ${maxCwa}`;

            groupSize.appendChild(cwaElem);
        }
    }
}

window.renderMemberCard = renderMemberCard;
window.renderAddStudentCard = renderAddStudentCard;
window.renderProjectInfo = renderProjectInfo;
window.renderCWARange = renderCWARange;