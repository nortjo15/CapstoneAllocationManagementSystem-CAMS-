document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.dataset.target; 

            //deactivate all buttons
            btn.closest(".tabs").querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            //deactive all content 
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

            //Activate specific button and content
            btn.classList.add("active");
            document.getElementById(targetId).classList.add("active");

            //Custom event so JS can listen
            document.dispatchEvent(new CustomEvent("tab:activated", {
                detail: { tabId: targetId }
            }));
        });
    });
});