export function updateDeleteButton(group, csrfToken, callbacks = {})
{
    const deleteBtn = document.getElementById("delete-group-btn");
    if(!deleteBtn) return;

    if (group.is_manual)
    {
        //Only show delete button on manual groups
        deleteBtn.style.display = "block";
        deleteBtn.onclick = () => confirmDeleteGroup(group, csrfToken, callbacks);
    }
    else 
    {
        deleteBtn.style.display = "none";
        deleteBtn.onclick = null;
    }
}

function confirmDeleteGroup(group, csrfToken, callbacks)
{
    if (!confirm(`Delete ${group.name}?`)) return; 

    fetch(`/api/suggested_groups/${group.suggestedgroup_id}/delete/`, {
        method: "DELETE",
        headers: { "X-CSRFToken": csrfToken },
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to delete group");

        //Remove from sidebar
        const btn = document.querySelector(
            `#manual-groups-ul button[data-id="${group.suggestedgroup_id}"]`
        );
        if (btn) btn.parentElement.remove();

        //Reset panel
        if (callbacks.onDeleted) callbacks.onDeleted();
    })
    .catch(err => console.error(err));
}