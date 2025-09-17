import { setButtonLoading } from "./utils.js";
import { updateDeleteButton } from "./group_actions.js";
import {
    renderMemberCard, renderAddStudentCard, renderProjectInfo, renderCWARange,
    clearError, applyAntiPreferenceUI, updateGroupUI
} from "./render_groups.js";

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

document.addEventListener("DOMContentLoaded", () => {

    //Variable to track the active group
    window.activeGroupId = null

    // When tab is activated, run logic
    document.addEventListener("tab:activated", e => {
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

        //Create button skeleton
        finaliseBtn.addEventListener("click", () => {
            if (activeGroupId) {
                alert(`This will create FinalGroup from SuggestedGroup ${activeGroupId}`);
            }
        });

        // Wire button to generate group suggestions
        const generateBtn = document.getElementById("generate-suggestions-btn");
        generateBtn.type = "button";

        generateBtn.addEventListener("click", () => {
            setButtonLoading(generateBtn, true);

            fetch("/api/generate_suggestions/", {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken}
            })
            .then(res => res.json())
            .then(data => {
                //Sort the groups by strength: strong -> medium -> weak
                const order = {strong: 1, medium: 2, weak: 3};

                data.sort((a, b) => {
                    return order[a.strength] - order[b.strength];
                })

                //Refresh the list panel with new groups & render
                suggestedGroupsUl.innerHTML = "";
                data.forEach((group, idx) => {
                    const li = document.createElement("li");
                    const btn = document.createElement("button");
                    btn.type = "button";

                    btn.classList.add("btn", "list-item-btn");
                    btn.dataset.id = group.suggestedgroup_id;
                    btn.dataset.display = idx + 1;
                    btn.textContent = `Group ${idx+1}`;

                    //Add Strength class to button
                    btn.classList.add(`strength-${group.strength.toLowerCase()}`);
                    li.appendChild(btn);
                    suggestedGroupsUl.appendChild(li); //Create a button for each group & append it
                });

                suggestedGroupsUl.querySelectorAll("button").forEach(btn => {
                    btn.addEventListener("click", () => loadGroup(btn.dataset.id));
                });
            })
            .catch(err => console.error("Failed to generate suggestions:", err))
            .finally(() => {
                setButtonLoading(generateBtn, false);
            })
        });

        //If notes form submits, reload current group
        const notesForm = document.getElementById("notesForm");
        if (notesForm) {
            notesForm.addEventListener("submit", () => {
                if (activeGroupId) {
                    setTimeout(() => loadGroup(activeGroupId), 200)
                }
            });
        }

        //Wireing the +Create Group Button
        const createBtn = document.getElementById("create-group-btn");
        createBtn.type = "button";

        createBtn.addEventListener("click", () => {
            setButtonLoading(createBtn, true);

            fetch("/api/suggested_groups/create_manual/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({}),
            })
            .then(res => res.json())
            .then(group => {
                renderManualGroup(group)
            })
            .catch(err => console.error("Failed to create manual group:", err))
            .finally(() => setButtonLoading(createBtn, false));
        });
    }

    function initManualGroups()
    {
        fetch("/api/suggested_groups/manual/")
            .then(res => res.json())
            .then(groups => {
                manualGroupsUl.innerHTML = "";
                groups.forEach(group => renderManualGroup(group));
            })
            .catch(err => console.error("Failed to load manual groups:", err));
    }

    function renderManualGroup(group)
    {
        //Add it to the sidebar 
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.classList.add("btn", "list-item-btn");
        btn.classList.add("strength-manual");
        btn.dataset.id = group.suggestedgroup_id;
        btn.dataset.display = group.name; 
        btn.textContent = group.name; 
        li.appendChild(btn);
        manualGroupsUl.appendChild(li);

        btn.addEventListener("click", () => loadGroup(btn.dataset.id));
    }

    //Trigger tab:activated if SuggestedGroups is active on load 
    if (document.querySelector("#suggested-tab.tab-content.active"))
    {
        document.dispatchEvent(new CustomEvent("tab:activated", {
            detail: { tabId: "suggested-tab" }
        }));
    }
});

export function removeStudentFromGroup(student, group) 
{
    group.members = group.members.filter(m => m.student.student_id !== student.student_id);
    updateGroupUI(group, finaliseBtn);

    fetch(`/api/suggested_groups/${group.suggestedgroup_id}/remove_student/`, {
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
    .catch(err => 
    {
        console.error("Failed to remove student:", err);
        // reload from backend if error
        loadGroup(group.suggestedgroup_id);
    });
}

//Loading a group onto the center panel
export function loadGroup(id)
{
    //Display consecutive numbers for groups

    const btn = document.querySelector(
        `#manual-groups-ul button[data-id="${id}"], #suggested-groups-ul button[data-id="${id}"]`   
    );
    const displayNum = btn ? btn.dataset.display : id;

    //Set it to load
    if (btn) setButtonLoading(btn, true);

    fetch(`/api/suggested_groups/${id}/`)
        .then(res => res.json())
        .then(group => {

            console.log(group)
            // Clear active buttons, then assign to the new button
            document.querySelectorAll("#manual-groups-ul button, #suggested-groups-ul button")
            .forEach(b => b.classList.remove("active"))
            if (btn)
            {
                btn.classList.add("active");
            }

            window.activeGroupId = group.suggestedgroup_id;
            window.currentMemberIds = new Set(group.members.map(m => m.student.student_id));

            groupTitle.textContent = "";
            groupMembers.innerHTML = `<div class="members-container"></div>`;

            const membersContainer = groupMembers.querySelector(".members-container");
            //Create a card for each member
            group.members.forEach(m => membersContainer.appendChild(renderMemberCard(m, group)));

            if (!group.project || group.members.length < group.project.capacity)
            {
                membersContainer.appendChild(renderAddStudentCard(group))
            }

            //Update Group Information
            renderProjectInfo(group, groupSize, projectName, 
                projectCapacity, projectHost, finaliseBtn);
            //CWA Information
            renderCWARange(group, groupSize);

            //Delete button for manual groups
            updateDeleteButton(group, csrfToken, {
                onDeleted: () => 
                {
                    groupTitle.textContent = "Select a group";
                    groupMembers.innerHTML = "";
                    projectName.innerHTML = "";
                    projectCapacity.innerHTML = "";
                    projectHost.innerHTML = "";
                    groupSize.innerHTML = "";

                    //hide delete button
                    const deleteBtn = document.getElementById("delete-group-btn");
                    if (deleteBtn)
                    {
                        deleteBtn.style.display = "none";
                        deleteBtn.onclick = null;
                    }

                    // Clear errors
                    const errorBox = document.getElementById("group-errors");
                    if (errorBox) clearError(errorBox);
                }
            });

            // Anti preference check
            applyAntiPreferenceUI(group, finaliseBtn);
            
        })
        .catch(err => {
            console.error("Failed to load group:", err);
            groupTitle.textContent = "Error loading group";
        })
        .finally(() => 
        {
            //stop spinner on this button 
            if (btn) setButtonLoading(btn, false);
        });
}