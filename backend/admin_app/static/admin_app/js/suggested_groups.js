document.addEventListener("DOMContentLoaded", () => {
    const groupsUl = document.getElementById("groups-ul");
    const groupTitle = document.getElementById("group-title");
    const groupMeta = document.getElementById("group-meta");
    const groupMembers = document.getElementById("group-members")
    const createBtn = document.getElementById("create-group-btn")

    //Variable to track the active group
    let activeGroupId = null

    //Loading a group onto the center panel
    function loadGroup(id)
    {
        //Display consecutive numbers for groups
        const btn = groupsUl.querySelector(`button[data-id="${id}"]`);
        const displayNum = btn ? btn.dataset.display : id;

        fetch(`/api/suggested_groups/${id}/`)
            .then(res => res.json())
            .then(group => {
                activeGroupId = group.suggestedgroup_id;
                groupTitle.textContent = `Group ${displayNum}`;
                groupMeta.innerHTML = `<p><strong>Strength:</strong> ${group.strength}</p>
                    <p><strong>Notes:</strong> ${group.notes || "None"}</p>`;

                groupMembers.innerHTML = `
                    <h4>Members:</h4>
                    <div class="members-container"></div>
                `;

                const membersContainer = groupMembers.querySelector(".members-container");
                //Create a card for each member
                group.members.forEach(m => {
                    const div = document.createElement("div");
                    div.classList.add("card");
                    div.innerHTML = `
                        <p><strong>Name:</strong> ${m.student.name}</p>
                        <p><strong>ID:</strong> ${m.student.student_id}</p>
                        <p><strong>CWA:</strong> ${m.student.cwa}</p>
                    `;

                    //Add card to the center panel
                    membersContainer.appendChild(div);
                });

                createBtn.disabled = false;
            });
    }

    //Create button skeleton
    createBtn.addEventListener("click", () => {
        if (activeGroupId) {
            console.log("Create group from suggested: ", activeGroupId);
            alert(`This will create FinalGroup from SuggestedGroup ${activeGroupId}`);
        }
    });

    // Wire button to generate group suggestions
    const generateBtn = document.getElementById("generate-suggestions-btn");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    generateBtn.addEventListener("click", () => {
        fetch("/api/generate_suggestions/", {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken}
        })
        .then(res => res.json())
        .then(data => {
            //Refresh the list panel with new groups
            groupsUl.innerHTML = "";
            data.forEach((group, idx) => {
                const li = document.createElement("li");
                li.innerHTML = 
                    `<button class="list-item-btn" 
                    data-id="${group.suggested_group_id}"
                    data-display="${idx+1}">
                    Group ${idx+1}
                    </button>`;
                groupsUl.appendChild(li); //Create a button for each group
            });

            groupsUl.querySelectorAll("button").forEach(btn => {
                btn.addEventListener("click", () => loadGroup(btn.dataset.id));
            });
        });
    });
});