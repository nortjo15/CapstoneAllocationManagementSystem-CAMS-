const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

export function finaliseGroup(groupId, name, notes) 
{
    fetch("/api/final_groups/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
            suggested_group_id: groupId,
            name: name,
            notes: notes,
        }),
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to finalise group");
        return res.json();
    })
    .then(data => 
    {
        //Remove the SuggestedGroup button from either list 
        const btn = document.querySelector(
            `#manual-groups-ul button[data-id="${groupId}"], #suggested-groups-ul button[data-id="${groupId}"]`
        );

        if (btn)
        {
            btn.parentElement.remove();
        }
    })
    .catch(err => {
        console.error("Error creating final group:", err);
    });
}