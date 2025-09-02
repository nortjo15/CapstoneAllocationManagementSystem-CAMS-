fetch("/admin_dashboard/api/final_groups/")
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.error("Error fetching groups:", err));