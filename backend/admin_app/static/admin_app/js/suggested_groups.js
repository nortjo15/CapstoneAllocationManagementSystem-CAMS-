document.addEventListener("DOMContentLoaded", () => {
    const groupsUl = document.getElementById("groups-ul");
    const groupTitle = document.getElementById("group-title");
    const groupMeta = document.getElementById("group-meta");
    const groupMembers = document.getElementById("group-members")
    const createBtn = document.getElementById("create-group-btn")

    //Variable to track the active group
    let activeGroupId = null

    //Load suggested groups into left panel
    fetch("/api/suggested_groups/")
        .then(res => res.json())
        .then(data => {
            groupsUl.innerHTML = "";
            data.forEach(group => {
                const li = document.createElement("li");
                //Create a button per group
                li.innerHTML = `<button class="list-item-btn" data-id="${group.suggestedgroup_id}">
                    Group ${group.suggestedgroup_id}
                </button>`;

                //Add the button to the panel
                groupsUl.appendChild(li);
            });

            //Add handlers for the click
            groupsUl.querySelectorAll("button").forEach(btn => {
                btn.addEventListener("click", () => loadGroup(btn.dataset.id));
            });
        });

    //Loading a group onto the center panel
    function loadGroup(id)
    {
        fetch(`/api/suggested_groups/${id}/`)
            .then(res => res.json())
            .then(group => {
                activeGroupId = group.suggestedgroup_id;
                groupTitle.textContent = `Group ${group.suggestedgroup_id}`;
                groupMeta.innerHTML = `<p><strong>Strength:</strong> ${group.strength}</p>
                    <p><strong>Notes:</strong> ${group.notes || "None"}</p>`;
                groupMembers.innerHTML = "<h4>Members:</h4>";

                //Create a card for each member
                group.members.forEach(m => {
                    const div = document.createElement("div");
                    div.classList.add("card");
                    div.innerHTML = `<p>${m.student.name} (${m.student.student_id})
                        - ${m.student.major}, CWA: ${m.student.cwa}</p>`;

                    //Add card to the center panel
                    groupMembers.appendChild(div);
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
});