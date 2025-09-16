import 
    { openNotesModal, openPreferenceModal, openRemoveStudentModal, openStudentModal } 
    from "./modal_function.js";
import { loadGroup } from "./suggested_groups.js";

let cachedProjects = null;  
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

//Helper functions for suggested_groups.js
export function renderMemberCard(m, group) 
{
    const div = document.createElement("div");
    div.classList.add("card", "member-card");
    const majorName = m.student && m.student.major ? m.student.major.name : "N/A";

    // member details
    div.innerHTML = `
        <p><span class="member-label">Name:</span> ${m.student.name}</p>
        <p><span class="member-label">ID:</span> ${m.student.student_id}</p>
        <p><span class="member-label">CWA:</span> ${m.student.cwa ?? "N/A"}</p>
        <p><span class="member-label">Major:</span> ${majorName}</p>
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
    notesBtn.classList.add("btn", "btn-secondary");
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
    prefBtn.classList.add("btn", "btn-secondary");
    prefBtn.textContent = "Preferences";
    prefBtn.title = ("Open preferences");

    //Disable button if no preferences
    if (!m.student.preferences || m.student.preferences.length == 0) 
    {
        prefBtn.disabled = true;
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

export function renderAddStudentCard() 
{
    const addDiv = document.createElement("div");
    addDiv.textContent = "+ Add Student";
    addDiv.classList.add("card", "add-student-card");
    addDiv.addEventListener("click", () => {
        openStudentModal();
    });
    return addDiv;
}

export function renderProjectInfo(group, groupSize, projectName, 
    projectCapacity, projectHost, createBtn) 
{
    const size = group.members.length

    groupSize.innerHTML = `<p><strong>Group Size:</strong> ${size}</p>`
    const sizeElem = groupSize.querySelector("p");

    projectName.innerHTML = "";
    const label = document.createElement("label");
    label.innerHTML = "<strong>Project:</strong> ";

    // Dropdown
    const select = document.createElement("select");
    select.classList.add("project-select");

    function populate(projects)
    {
        select.innerHTML = "";

        const noneOption = document.createElement("option");
        noneOption.value = "";
        noneOption.textContent = "None";
        if (!group.project)
        {
            noneOption.selected = true; 
        }
        select.appendChild(noneOption);

        projects.forEach(p => {
            const option = document.createElement("option");
            option.value = p.project_id;
            option.textContent = p.title;
            if (group.project && group.project.project_id === p.project_id)
            {
                option.selected = true;
            }
            select.appendChild(option);
        });
    }

    //Use cached projects if they exist
    if (cachedProjects)
    {
        populate(cachedProjects);
        label.appendChild(select);
        projectName.appendChild(label);

        new Choices(select, {
        searchEnabled: true,
        itemSelectText: '',
        shouldSort: false
        });
    }
    else 
    {
        fetch("/api/project_list/")
            .then(res => res.json())
            .then(projects => {
                cachedProjects = projects;
                populate(projects);
                label.appendChild(select);
                projectName.appendChild(label);

                new Choices(select, {
                searchEnabled: true,
                itemSelectText: '',
                shouldSort: false
                });
            });
    }

    //Update backend
    select.addEventListener("change", () => 
    {
        const projectId = select.value;

        fetch(`/api/suggested_groups/${group.suggestedgroup_id}/update/`, 
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ project_id: projectId || null }),
        })
        .then(res => res.json())
        .then(updated => {
            console.log("Project updated:", updated);
            loadGroup(group.suggestedgroup_id);
        })
        .catch(err => console.error("Failed to update project:", err));
    });

    if (group.project) 
    {
        const capacity = group.project.capacity
        
        projectCapacity.innerHTML = `<p><strong>Project Capacity:</strong> ${capacity}</p>`;
        projectHost.innerHTML = `<p><strong>Host:</strong> ${group.project.host_name}</p>`;
        const capacityElem = projectCapacity.querySelector("p");
        const errorBox = document.getElementById("group-errors");

        //See if there's a mismatch in groupSize & Capacity
        if (size !== capacity)
        {

            capacityElem.classList.add("text-error");
            sizeElem.classList.add("text-error");
            createBtn.disabled = true;
            showError("Invalid Group Size", errorBox)
        }
        else 
        {
            capacityElem.classList.remove("text-error");
            sizeElem.classList.remove("text-error");
            createBtn.disabled = false;
            clearError(errorBox)
        }
    } 
    else 
    {
        projectCapacity.innerHTML = `<p><strong>Project Capacity:</strong> </p>`;
        projectHost.innerHTML = `<p><strong>Host:</strong> </p>`;
    }
}

export function renderCWARange(group, groupSize)
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

export function updateGroupUI(group)
{
    const membersContainer = document.querySelector("#group-members .members-container");
    const groupSize = document.getElementById("group-size");
    const projectName = document.getElementById("group-project-name");
    const projectCapacity = document.getElementById("group-capacity");
    const projectHost = document.getElementById("group-host");
    const finaliseBtn = document.getElementById("finalise-group-btn");

    //Clear members container 
    membersContainer.innerHTML = "";

    //Re-render members
    group.members.forEach(m => membersContainer.appendChild(renderMemberCard(m, group)));

    //Add Student card if space left 
    if (!group.project || group.members.length < group.project.capacity)
    {
        membersContainer.appendChild(renderAddStudentCard(group));
    }

    //Re-run group info & CWA 
    renderProjectInfo(group, groupSize, projectName, projectCapacity, projectHost, finaliseBtn);
    renderCWARange(group, groupSize);
}

export function showError(msg, errorBox)
{
    errorBox.textContent = msg; 
    errorBox.style.display = "block";
}

export function clearError(errorBox)
{
    errorBox.textContent = "";
    errorBox.style.display = "none";
}