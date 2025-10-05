import 
    { openNotesModal, openPreferenceModal, openRemoveStudentModal, openStudentModal, openMemberPreferenceModal } 
    from "./modal_function.js";
import { loadGroup } from "./suggested_groups.js";
import { updateDeleteButton } from "./group_actions.js";

let cachedProjects = null;  
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

//Helper functions for suggested_groups.js
export function renderMemberCard(m, group) 
{
    const div = document.createElement("div");
    div.classList.add("card", "member-card");
    div.dataset.studentId = m.student.student_id;
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
    prefBtn.textContent = "Projects";
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

    // Member Preferences Button 
    const memberPrefBtn = document.createElement("span");
    memberPrefBtn.classList.add("btn", "btn-secondary", "member-pref-btn");
    memberPrefBtn.dataset.studentId = m.student.student_id;
    memberPrefBtn.textContent = "Members";
    memberPrefBtn.title = ("Open member preferences");

    if (!m.student.group_preferences || m.student.group_preferences.length == 0)
    {
        memberPrefBtn.disabled = true;
        memberPrefBtn.style.opacity = "0.5";
        memberPrefBtn.style.cursor = "not-allowed";
    }
    else 
    {
        memberPrefBtn.addEventListener("click", (e) => 
        {
            e.stopPropagation();
            openMemberPreferenceModal(m.student)
        })
    }

    div.appendChild(removeBtn);
    div.appendChild(notesBtn);
    div.appendChild(prefBtn);
    div.appendChild(memberPrefBtn);
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

            //Disable if project is already assigned to a FinalGroup
            if (p.is_assigned)
            {
                option.disabled = true;
                option.textContent += " (Assigned)";
            }

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
        const apiUrl = window.ENDPOINTS.projects;
        fetch(apiUrl)
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

        group.project = cachedProjects.find(p => p.project_id == projectId) || null;
        window.suggestedGroupsCache.delete(group.suggestedgroup_id);
        loadGroup(group.suggestedgroup_id);

        fetch(`/api/admin/suggested_groups/${group.suggestedgroup_id}/update/`, 
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ project_id: projectId || null }),
        })
        .then(res => {
            if (!res.ok) throw new Error("Failed to update project");
            return res.json();
        })
        .catch(err => {
            console.error("Failed to update project:", err);
            loadGroup(group.suggestedgroup_id)
        });
    });

    const errorBox = document.getElementById("group-errors");

    if (group.project) 
    {
        const capacity = group.project.capacity
        
        projectCapacity.innerHTML = `<p><strong>Project Capacity:</strong> ${capacity}</p>`;
        projectHost.innerHTML = `<p><strong>Host:</strong> ${group.project.host_name}</p>`;
        const capacityElem = projectCapacity.querySelector("p");

        //See if there's a mismatch in groupSize & Capacity
        if (size !== capacity)
        {

            capacityElem.classList.add("text-error");
            sizeElem.classList.add("text-error");
            showError("Invalid Group Size", errorBox)
        }
        else 
        {
            capacityElem.classList.remove("text-error");
            sizeElem.classList.remove("text-error");
            clearError(errorBox, "Invalid Group Size");
        }
    } 
    else 
    {
        projectCapacity.innerHTML = `<p><strong>Project Capacity:</strong> </p>`;
        projectHost.innerHTML = `<p><strong>Host:</strong> </p>`;
    }

    updateFinaliseButton(errorBox, createBtn, group);
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

export function showError(msg, errorBox) 
{
    const ul = errorBox.querySelector("ul") || errorBox.appendChild(document.createElement("ul"));

    const exists = Array.from(ul.children).some(li => li.textContent === msg);
    if (exists) return;

    const li = document.createElement("li");
    li.textContent = msg;
    li.classList.add("error-item");
    ul.appendChild(li);
    errorBox.style.display = "block";
}

export function clearError(errorBox, msg = null) 
{
    const ul = errorBox.querySelector("ul");
    if (!ul) return;

    if (msg) 
    {
        // Remove only specific error
        ul.querySelectorAll("li").forEach(li => {
            if (li.textContent === msg) li.remove();
        });
    } 
    else 
    {
        // Remove all errors
        ul.innerHTML = "";
    }

    if (!ul.children.length) {
        errorBox.style.display = "none";
    }
}

export function updateFinaliseButton(errorBox, finaliseBtn, group=null) 
{
    const hasErrors = errorBox.querySelector("ul")?.children.length > 0;
    const noProject = group ? !group.project : false;
    finaliseBtn.disabled = hasErrors || noProject;
}

export function checkAntiPreferences(group)
{
    const memberIds = new Set(group.members.map(m => m.student.student_id));
    const conflicts = [];

    for (const m of group.members)
    {
        if (!m.student.group_preferences) continue;

        // Go through each student and check their anti prefs
        for (const pref of m.student.group_preferences)
        {
            if (pref.preference_type == "avoid" && memberIds.has(pref.target_id))
            {
                conflicts.push({ from: m.student.student_id, to: pref.target_id });
            }
        }
    }

    return conflicts;
}

export function applyAntiPreferenceUI(group, finaliseBtn)
{
    const conflicts = checkAntiPreferences(group);
    const errorBox = document.getElementById("group-errors");

    // Remove existing highlight
    document.querySelectorAll(".member-card.conflict").forEach(el =>
        el.classList.remove("conflict")
    );
    document.querySelectorAll(".member-pref-btn.btn-danger").forEach(el => {
        el.classList.remove("btn-danger");
        el.classList.add("btn-secondary");
    });

    if (conflicts.length > 0) 
    {
        conflicts.forEach(conf => 
        {
            // highlight both cards
            [conf.from, conf.to].forEach(id => {
                const card = document.querySelector(
                    `.member-card[data-student-id="${id}"]`
                );
                if (card) card.classList.add("conflict");
            });

            // make only the 'from' button danger
            const btn = document.querySelector(
                `.member-pref-btn[data-student-id="${conf.from}"]`
            );

            if (btn) 
            {
                btn.classList.remove("btn-secondary");
                btn.classList.add("btn-danger");
            }
        });

        showError("Member Anti-Preference", errorBox);
    }
    else 
    {
        clearError(errorBox, "Member Anti-Preference");
    }

    updateFinaliseButton(errorBox, finaliseBtn, group);
}

// render_groups.js
export function updateGroupUI(group, finaliseBtn) {
    const groupTitle = document.getElementById("group-title");
    const groupSize = document.getElementById("group-size");
    const groupMembers = document.getElementById("group-members");
    const projectName = document.getElementById("group-project-name");
    const projectCapacity = document.getElementById("group-capacity");
    const projectHost = document.getElementById("group-host");
    const errorBox = document.getElementById("group-errors");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    // keep global state in sync
    window.activeGroupId = group.suggestedgroup_id;
    const members = Array.isArray(group.members) ? group.members : [];
    window.currentMemberIds = new Set(members.map(m => m.student.student_id));

    // clear title and member container
    groupTitle.textContent = "";
    groupMembers.innerHTML = `<div class="members-container"></div>`;
    const membersContainer = groupMembers.querySelector(".members-container");

    // render each member
    group.members.forEach(m => membersContainer.appendChild(renderMemberCard(m, group)));

    // add student card if space left
    if (!group.project || group.members.length < group.project.capacity) {
        membersContainer.appendChild(renderAddStudentCard(group));
    }

    // update group info + project details
    renderProjectInfo(group, groupSize, projectName, projectCapacity, projectHost, finaliseBtn);
    // render CWA range
    renderCWARange(group, groupSize);
    // delete button handling for manual groups
    updateDeleteButton(group, csrfToken, {
        onDeleted: () => {
            groupTitle.textContent = "Select a group";
            groupMembers.innerHTML = "";
            projectName.innerHTML = "";
            projectCapacity.innerHTML = "";
            projectHost.innerHTML = "";
            groupSize.innerHTML = "";

            // hide delete button
            const deleteBtn = document.getElementById("delete-group-btn");
            if (deleteBtn) {
                deleteBtn.style.display = "none";
                deleteBtn.onclick = null;
            }

            // clear errors
            if (errorBox) clearError(errorBox);
        }
    });

    // anti-preference highlighting
    applyAntiPreferenceUI(group, finaliseBtn);

    window.suggestedGroupsCache.set(group.suggestedgroup_id, group);
}