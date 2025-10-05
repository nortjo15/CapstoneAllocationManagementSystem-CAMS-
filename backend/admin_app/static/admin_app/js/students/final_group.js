import { showPageLoader, hidePageLoader } from "../utils.js";

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

        // Remove all overlapping groups
        document
            .querySelectorAll("#suggested-groups-ul button, #manual-groups-ul button")
            .forEach((button) => {
                const gId = parseInt(button.dataset.id);
                const cachedGroup = window.suggestedGroupsCache.get(gId);
                if (!cachedGroup) return;

                const hasOverlap =
                    cachedGroup.members.some((m) =>
                        allocatedStudentIds.includes(m.student.student_id)
                    ) ||
                    (assignedProjectId &&
                        cachedGroup.project &&
                        cachedGroup.project.project_id === assignedProjectId);

                if (hasOverlap) {
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