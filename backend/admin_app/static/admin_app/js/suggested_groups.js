document.addEventListener("DOMContentLoaded", () => {
    const groupsUl = document.getElementById("groups-ul");
    const groupTitle = document.getElementById("group-title");
    const groupMeta = document.getElementById("group-meta");
    const groupMembers = document.getElementById("group-members")
    const createBtn = document.getElementById("create-group-btn")
    const projectName = document.getElementById("group-project-name")
    const projectHost = document.getElementById("group-host")
    const projectCapacity = document.getElementById("group-capacity")

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
                // Clear active buttons, then assign to the new button
                groupsUl.querySelectorAll("button").forEach(b => b.classList.remove("active"))
                if (btn)
                {
                    btn.classList.add("active");
                }

                activeGroupId = group.suggestedgroup_id;
                groupTitle.textContent = `Group ${displayNum}`;
                groupMeta.innerHTML = `<p><strong>Notes:</strong> ${group.notes || "None"}</p>`;
                groupMembers.innerHTML = `<div class="members-container"></div>`;


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

                if (group.project && group.members.length < group.project.capacity)
                {
                    const addDiv = document.createElement("div");
                    addDiv.textContent = "+ Add Student";
                    addDiv.classList.add("card", "add-student-card");
                    addDiv.addEventListener("click", () => {
                        //some code here
                        alert(`Add student to group ${group.suggested_group_id}`);
                    })

                    membersContainer.appendChild(addDiv)
                }

                //Update group information
                if(group.project)
                {
                    projectName.innerHTML = `<p><strong>Project:</strong> ${group.project.title}</p>`
                    projectCapacity.innerHTML = `<p><strong>Capacity:</strong> ${group.project.capacity}</p>`
                    projectHost.innerHTML = `<p><strong>Host:</strong> ${group.project.host_name}</p>`
                }
            
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
            //Sort the groups by strength: strong -> medium -> weak
            const order = {strong: 1, medium: 2, weak: 3};

            data.sort((a, b) => {
                return order[a.strength] - order[b.strength];
            })

            //Refresh the list panel with new groups & render
            groupsUl.innerHTML = "";
            data.forEach((group, idx) => {
                const li = document.createElement("li");
                const btn = document.createElement("button");

                btn.classList.add("list-item-btn");
                btn.dataset.id = group.suggested_group_id;
                btn.dataset.display = idx + 1;
                btn.textContent = `Group ${idx+1}`;

                //Add Strength class to button
                btn.classList.add(`strength-${group.strength.toLowerCase()}`);
                li.appendChild(btn);
                groupsUl.appendChild(li); //Create a button for each group & append it
            });

            groupsUl.querySelectorAll("button").forEach(btn => {
                btn.addEventListener("click", () => loadGroup(btn.dataset.id));
            });
        });
    });
});