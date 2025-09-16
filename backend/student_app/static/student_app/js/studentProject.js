async function getProjectData() {
    const projectContainer = document.getElementById('project-container');
    const apiUrl = window.ENDPOINTS.projects;

    try {
        const response = await fetch(apiUrl);
        const projects = await response.json();
        projectContainer.innerHTML = ''; // Clear loading

        if (projects.length === 0) {
            projectContainer.innerHTML = '<li>No Projects Found</li>';
        } else {
            projects.forEach(project => {
                const card = document.createElement('div');
                card.classList.add('project-card');
                card.innerHTML = `
                    <h3>${project.title}</h3>
                    <p>${project.description}</p>
                    <h4>${project.host_name}</h4>
                    <div class="card-footer">
                        <span>Capacity: ${project.capacity}</span>
                    </div>  
                `;
                projectContainer.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        projectContainer.innerHTML = '<li>Could not load projects</li>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial data load
    getProjectData();

    // Set an interval to refresh data every 30 seconds (30000 milliseconds)
    setInterval(getProjectData, 30000);
});