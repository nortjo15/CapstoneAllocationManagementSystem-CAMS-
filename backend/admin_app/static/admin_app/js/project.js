
async function getProjectData() {
    const projectContainer = document.getElementById('project-container');
    const apiUrl = window.ENDPOINTS.projects;

    try {
        const response = await fetch(apiUrl);
        const projects = await response.json();
        projectContainer.innerHTML = ''; // Clear loading

        if (projects.length === 0) {
            // BUG FIX: Was 'projectList', now 'projectContainer'
            projectContainer.innerHTML = '<li>No Projects Found</li>';
        } else {
            projects.forEach(project => {
                const card = document.createElement('div');
                card.classList.add('project-card');
                card.innerHTML = `
                    <h3>${project.title}</h3>
                    <p>${project.description}</p>
                    <h4>${project.host_name}</h4>
                    <h4>${project.host_email}</h4>
                    <h4>${project.host_phone}</h4>
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

async function handleAddProject(event) {
    event.preventDefault(); // Stop the page from reloading

    const apiUrl = window.ENDPOINTS.projects;
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            getProjectData(); // Refresh the project list
            form.reset(); // Clear the form
            document.getElementById('pModal').style.display = 'none'; // Close the modal
            
        } else {
            const errorData = await response.json();
            console.error('Failed to add project', errorData);
            alert('Error: Could not add Project');
        }

    } catch (error) {
        console.error('Network error:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial data load
    getProjectData();

    // Set an interval to refresh data every 30 seconds (30000 milliseconds)
    setInterval(getProjectData, 30000);

    // Get modal elements
    const modal = document.getElementById('pModal');
    const openBtn = document.getElementById('openModalBtn');
    // BUG FIX: Use querySelector for classes, not getElementById
    const closeBtn = document.querySelector('.close-button');
    const addProjectForm = document.getElementById('add-project-modal-form');

    // Attach event listeners
    addProjectForm.addEventListener('submit', handleAddProject);

    openBtn.onclick = function() {
        modal.style.display = 'block';
    }

    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});