import { showPageLoader, hidePageLoader } from "../utils.js";
import { updateGroupUI } from "./render_groups.js";

const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

export function setupFinaliseValidation() {
    const nameInput = document.getElementById("groupNameInput");
    const confirmBtn = document.getElementById("confirmGroupBtn");

    if (!nameInput || !confirmBtn) return;

    // initial state
    confirmBtn.disabled = nameInput.value.trim() === "";

    // re-check on input
    nameInput.addEventListener("input", () => {
        confirmBtn.disabled = nameInput.value.trim() === "";
    });
}

export function finaliseGroup(groupId, name, notes) 
{
    const errorBox = document.getElementById("finalise-errors");
    errorBox.style.display = "none";
    errorBox.textContent = "";

    if (!name || name.trim() === "")
    {
        errorBox.textContent = "Group name is required.";
        errorBox.style.display = "block";
        return;
    }

    showPageLoader();

    fetch("/api/admin/final_groups/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
            suggestedgroup_id: groupId,
            name: name.trim(),
            notes: notes?.trim() || "",
        }),
    })
    .then(async (res) => {                  
        if (!res.ok) {
            const errData = await res.json().catch(() => ({})); 
            if (errData.name) {                               
                errorBox.textContent = errData.name.join(", ");
                errorBox.style.display = "block";
            } else if (errData.detail) {                      
                errorBox.textContent = errData.detail;
                errorBox.style.display = "block";
            } else {
                errorBox.textContent = "An unknown error occurred.";
                errorBox.style.display = "block";
            }
            throw new Error("Failed to finalise group");
        }
        return res.json();
    })
    .then(data => 
    {
        const modal = document.getElementById("createGroupModal");
        if (modal) modal.style.display = "none";

        //Remove the SuggestedGroup button from either list 
        const btn = document.querySelector(
            `#manual-groups-ul button[data-id="${groupId}"], #suggested-groups-ul button[data-id="${groupId}"]`
        );
        if (btn) btn.parentElement.remove();

        errorBox.style.display = "none";

        // Remove cached entry for this  group 
        window.suggestedGroupsCache.delete(parseInt(groupId));

        const allocatedStudentIds = data.members.map((m) => m.student.student_id);  
        const assignedProjectId = data.project?.project_id;  

       // --- Remove all overlapping groups (students or project) ---
        document.querySelectorAll("#suggested-groups-ul button, #manual-groups-ul button").forEach(button => {
            const gId = parseInt(button.dataset.id);
            const cachedGroup = window.suggestedGroupsCache.get(gId);
            if (!cachedGroup) return;

            const members = cachedGroup.members || [];
            const projectId = cachedGroup.project?.project_id;

            // refresh 'assigned' status from the DOM if visible
            const projectIsAssigned = cachedGroup.project?.is_assigned === true;

            const memberOverlap = members.some(m =>
                allocatedStudentIds.map(String).includes(String(m.student.student_id))
            );

            const projectOverlap =
                assignedProjectId &&
                projectId &&
                Number(projectId) === Number(assignedProjectId);

            if (memberOverlap || projectOverlap || projectIsAssigned) {
                button.parentElement.remove();
                window.suggestedGroupsCache.delete(gId);
            }
        });

        window.cachedProjects = null; 

        // Clear central panel
        if (window.activeGroupId == groupId)
        {
            document.getElementById("group-title").textContent = "Select a group";
            document.getElementById("group-members").innerHTML = "";
            document.getElementById("group-project-name").innerHTML = "";
            document.getElementById("group-capacity").innerHTML = "";
            document.getElementById("group-host").innerHTML = "";
            document.getElementById("group-size").innerHTML = "";
        }
    })
    .catch((err) => {                        
        console.error("Error creating final group:", err);
    })
    .finally(() => hidePageLoader());      
}

const finalGroupsUl = document.createElement("ul");
finalGroupsUl.id = "final-groups-ul";
finalGroupsUl.classList.add("list");

function renderFinalGroups(groups) {
    finalGroupsUl.innerHTML = "";
    if (!groups.length) {
        const p = document.createElement("p");
        p.textContent = "No final groups yet.";
        finalGroupsUl.appendChild(p);
        return;
    }

    groups.forEach((g, idx) => {
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.classList.add("btn", "list-item-btn");
        btn.dataset.id = g.finalgroup_id;
        btn.textContent = g.name || `Final Group ${idx + 1}`;
        li.appendChild(btn);
        finalGroupsUl.appendChild(li);

        btn.addEventListener("click", () => {
            loadFinalGroup(g.finalgroup_id);
        });
    });
}

function loadFinalGroups() {
    const container = document.querySelector("#final-tab .panel");
    if (!container) return;

    container.innerHTML = "<h3>Final Groups</h3>";
    container.appendChild(finalGroupsUl);

    fetch("/api/admin/final_groups/list/")
        .then(res => res.json())
        .then(data => renderFinalGroups(data))
        .catch(err => {
            console.error("Failed to load final groups:", err);
        });
}

document.addEventListener("tab:activated", e => {
    if (e.detail.tabId === "final-tab") {
        loadFinalGroups();
    }
});

function loadFinalGroup(id) {
    showPageLoader();

    fetch(`/api/admin/final_groups/${id}/`)
        .then(res => res.json())
        .then(group => {
            renderFinalGroupUI(group);
        })
        .catch(err => console.error("Failed to load final group:", err))
        .finally(() => hidePageLoader());
}

function renderFinalGroupUI(group) {
    // --- clear old content before rendering ---
    document.getElementById("final-group-title").textContent = group.name || "Unnamed Final Group";
    document.getElementById("final-group-size").innerHTML = `<p><strong>Group Size:</strong> ${group.members.length}</p>`;

    const projectBox = document.getElementById("final-group-project-name");
    projectBox.innerHTML = group.project
        ? `<p><strong>Project:</strong> ${group.project.title}</p>`
        : `<p><strong>Project:</strong> None</p>`;

    const hostBox = document.getElementById("final-group-host");
    hostBox.innerHTML = group.project
        ? `<p><strong>Host:</strong> ${group.project.host_name}</p>`
        : `<p><strong>Host:</strong> N/A</p>`;

    const membersContainer = document.querySelector("#final-group-members .members-container");
    membersContainer.innerHTML = ""; // clear previous

    if (group.members && group.members.length) {
        group.members.forEach(m => {
            const div = document.createElement("div");
            div.classList.add("card", "member-card");
            div.innerHTML = `
                <p><span class="member-label">Name:</span> ${m.student.name}</p>
                <p><span class="member-label">ID:</span> ${m.student.student_id}</p>
                <p><span class="member-label">CWA:</span> ${m.student.cwa ?? "N/A"}</p>
                <p><span class="member-label">Major:</span> ${m.student.major ? m.student.major.name : "N/A"}</p>
            `;
            membersContainer.appendChild(div);
        });
    } else {
        const empty = document.createElement("p");
        empty.textContent = "No members found.";
        membersContainer.appendChild(empty);
    }

    // --- notes handling ---
    const notesArea = document.getElementById("final-notes-area");
    if (notesArea) notesArea.value = group.notes || "";

    // --- delete handler ---
    const deleteBtn = document.getElementById("delete-final-group-btn");
    deleteBtn.onclick = () => deleteFinalGroup(group.finalgroup_id);

    // --- save handler ---
    const saveBtn = document.getElementById("save-final-notes-btn");
    saveBtn.onclick = () => {
        const updatedNotes = notesArea.value.trim();
        saveFinalGroupNotes(group.finalgroup_id, updatedNotes);
    };
}

function deleteFinalGroup(id) {
    if (!confirm("Delete this final group?")) return;
    showPageLoader();

    fetch(`/api/admin/final_groups/${id}/`, {
        method: "DELETE",
        headers: { "X-CSRFToken": csrfToken }
    })
        .then(res => {
            if (!res.ok) throw new Error("Failed to delete final group");

            // refresh sidebar list
            loadFinalGroups();

            // clear center panel
            document.getElementById("final-group-title").textContent = "Select a group";
            document.getElementById("final-group-size").innerHTML = "";
            document.querySelector("#final-group-members .members-container").innerHTML = "";
            document.getElementById("final-group-project-name").innerHTML = "";
            document.getElementById("final-group-host").innerHTML = "";
            document.getElementById("final-notes-area").value = "";
        })
        .catch(err => console.error(err))
        .finally(() => hidePageLoader());
}

function saveFinalGroupNotes(id, notes) {
    showPageLoader();

    fetch(`/api/admin/final_groups/${id}/`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({ notes })
    })
        .then(res => {
            if (!res.ok) throw new Error("Failed to update notes");
            console.log("Notes saved for Final Group", id);
        })
        .then(() => loadFinalGroups()) // refresh list to reflect updates
        .catch(err => console.error(err))
        .finally(() => hidePageLoader());
}