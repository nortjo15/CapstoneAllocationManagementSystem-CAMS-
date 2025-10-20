import { hidePageLoader, setButtonLoading, showPageLoader } from "../utils.js";
import { updateGroupUI } from "./render_groups.js";
import { openCreateGroupModal } from "./modal_function.js";

const manualGroupsUl = document.getElementById("manual-groups-ul");
const suggestedGroupsUl = document.getElementById("suggested-groups-ul");
const groupTitle = document.getElementById("group-title");
const groupSize = document.getElementById("group-size");
const groupMembers = document.getElementById("group-members")
const finaliseBtn = document.getElementById("finalise-group-btn")
const projectName = document.getElementById("group-project-name")
const projectHost = document.getElementById("group-host")
const projectCapacity = document.getElementById("group-capacity")
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
let suggestedGroupsInitialised = false;
window.suggestedGroupsCache = new Map(); 


export function renderManualGroup(group) {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.classList.add("btn", "list-item-btn", "strength-manual");
    btn.dataset.id = group.suggestedgroup_id;

    const index = manualGroupsUl.children.length + 1;
    const displayName = group.project
        ? `${group.project.title || group.project} (Manual)`
        : `Group ${index}`;

    btn.textContent = displayName;
    btn.dataset.display = displayName;

    li.appendChild(btn);
    manualGroupsUl.appendChild(li);
    btn.addEventListener("click", () => loadGroup(btn.dataset.id));
}

export function renderSuggestedGroups(groups) 
{
    const order = {strongest: 0, strong: 1, medium: 2, weak: 3};
    groups.sort((a, b) => {
        const orderA = order[a.strength?.toLowerCase()] ?? 999;
        const orderB = order[b.strength?.toLowerCase()] ?? 999;
        return orderA - orderB;
    });

    suggestedGroupsUl.innerHTML = "";
    groups.forEach((group, idx) => {
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.classList.add("btn", "list-item-btn");
        btn.dataset.id = group.suggestedgroup_id;

        const displayName = group.project
            ? `${(group.project.title || group.project)} (Auto)`
            : `Group ${idx + 1}`;
        btn.textContent = displayName;
        btn.dataset.display = displayName;

        btn.classList.add(`strength-${group.strength.toLowerCase()}`);

        btn.dataset.projectId = group.project ? group.project.project_id : "";
        btn.dataset.isAssigned = group.project ? group.project.is_assigned : false;
        btn.dataset.members = JSON.stringify(group.members || []);

        li.appendChild(btn);
        suggestedGroupsUl.appendChild(li);
    });

    suggestedGroupsUl.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", () => loadGroup(btn.dataset.id));
    });
}

document.addEventListener("DOMContentLoaded", () => {

    //Variable to track the active group
    window.activeGroupId = null

    // When tab is activated, run logic
    document.addEventListener("tab:activated", e => {
        console.log("tab activate");
        if (e.detail.tabId === "suggested-tab") 
        {
            initSuggestedGroups();
            initManualGroups();
        }
    });

    function initSuggestedGroups() 
    {
        if (suggestedGroupsInitialised) return; 
        suggestedGroupsInitialised = true; 

        showPageLoader();
        // --- Load existing auto-suggested groups on page reload ---
        fetch("/api/admin/suggested_groups/auto/")
            .then(res => res.json())
            .then(data => {
                renderSuggestedGroups(data);
            })
            .catch(err => console.error("Failed to load suggested groups:", err))
            .finally(() => hidePageLoader());

        // --- Finalise button skeleton ---
        finaliseBtn.addEventListener("click", () => 
        {
            if (activeGroupId)
            {
                openCreateGroupModal(activeGroupId);
            }
        });

        // --- Generate button wiring ---
        const generateBtn = document.getElementById("generate-suggestions-btn");
        generateBtn.type = "button";

        generateBtn.addEventListener("click", () => {
            setButtonLoading(generateBtn, true);
        
            fetch("/api/admin/generate_suggestions/", {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken }
            })
            .then(res => res.json())
            .then(data => {
                const autoGroups = data.filter(g => !g.is_manual);
                renderSuggestedGroups(autoGroups); 
            })
            .catch(err => console.error("Failed to generate suggestions:", err))
            .finally(() => {
                setButtonLoading(generateBtn, false);
            });
        });

        // --- Notes form reload ---
        const notesForm = document.getElementById("notesForm");
        if (notesForm) {
            notesForm.addEventListener("submit", () => {
                if (activeGroupId) {
                    setTimeout(() => loadGroup(activeGroupId), 200);
                }
            });
        }

        // --- Create manual group button wiring ---
        const createBtn = document.getElementById("create-group-btn");
        createBtn.type = "button";

        createBtn.addEventListener("click", () => {
            setButtonLoading(createBtn, true);

            fetch("/api/admin/suggested_groups/create_manual/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({}),
            })
            .then(res => res.json())
            .then(group => {
                renderManualGroup(group);
            })
            .catch(err => console.error("Failed to create manual group:", err))
            .finally(() => setButtonLoading(createBtn, false));
        });
    }

    function initManualGroups()
    {
        fetch("/api/admin/suggested_groups/manual/")
            .then(res => res.json())
            .then(groups => {
                manualGroupsUl.innerHTML = "";
                groups.forEach(group => renderManualGroup(group));
            })
            .catch(err => console.error("Failed to load manual groups:", err));
    }

    //Trigger tab:activated if SuggestedGroups is active on load 
    if (document.querySelector("#suggested-tab.tab-content.active"))
    {
        document.dispatchEvent(new CustomEvent("tab:activated", {
            detail: { tabId: "suggested-tab" }
        }));
    }
});

if (document.querySelector("#suggested-tab.tab-content.active")) {
    document.dispatchEvent(new CustomEvent("tab:activated", { detail: { tabId: "suggested-tab" } }));
}

export function removeStudentFromGroup(student, group) 
{
    group.members = group.members.filter(m => m.student.student_id !== student.student_id);
    updateGroupUI(group, finaliseBtn);

    fetch(`/api/admin/suggested_groups/${group.suggestedgroup_id}/remove_student/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({ student_id: student.student_id })
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to remove student");
        return res.json();
    })
    .then(() => {
        //Invalidate cache & reload
        window.suggestedGroupsCache.delete(group.suggestedgroup_id);
        loadGroup(group.suggestedgroup_id);
    })
    .catch(err => 
    {
        console.error("Failed to remove student:", err);
        // reload from backend if error
        loadGroup(group.suggestedgroup_id);
    });
}

//Loading a group onto the center panel
export function loadGroup(id) {
    showPageLoader();

    const btn = document.querySelector(
        `#manual-groups-ul button[data-id="${id}"], #suggested-groups-ul button[data-id="${id}"]`
    );

    if (btn) setButtonLoading(btn, true);

    // Check cache first
    const cached = window.suggestedGroupsCache.get(Number(id));
    if (cached) {
        renderGroupUI(cached, btn);
        if (btn) setButtonLoading(btn, false);
        hidePageLoader();
        return;
    }

    fetch(`/api/admin/suggested_groups/${id}/`)
        .then(res => {
            if (!res.ok) throw new Error(`Group ${id} not found or deleted`);
            return res.json();
        })
        .then(group => {
            if (!group) throw new Error(`Group ${id} missing in response`);
            window.suggestedGroupsCache.set(group.suggestedgroup_id, group);
            renderGroupUI(group, btn);
        })
        .catch(err => {
            console.warn("Group load failed:", err.message);

            // Clear center panel if deleted or failed
            if (window.activeGroupId == id) {
                document.getElementById("group-title").textContent = "Select a group";
                document.getElementById("group-members").innerHTML = "";
                document.getElementById("group-project-name").innerHTML = "";
                document.getElementById("group-capacity").innerHTML = "";
                document.getElementById("group-host").innerHTML = "";
                document.getElementById("group-size").innerHTML = "";
            }
        })
        .finally(() => {
            if (btn) setButtonLoading(btn, false);
            hidePageLoader();
        });
}

export function renderGroupUI(group, btn) 
{
    // Clear active buttons
    document.querySelectorAll("#manual-groups-ul button, #suggested-groups-ul button")
        .forEach(b => b.classList.remove("active"));
    if (btn) btn.classList.add("active");

    // Update central panel
    updateGroupUI(group, finaliseBtn);
}