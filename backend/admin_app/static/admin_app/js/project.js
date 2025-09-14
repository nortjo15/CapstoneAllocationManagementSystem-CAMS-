
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

                        <div class="card-actions">
                            <button class="edit-btn" data-id="${project.project_id}"> Edit </button>
                            <button class="delete-btn" data-id="${project.project_id}"> Delete </button>
                        </div>
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

async function deleteProject(projectId){
    if(!confirm('Are you sure you want to delete this project?')){
        return;
    }

    const projectUrl = `${window.ENDPOINTS.projects}${projectId}/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const response = await fetch(projectUrl, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        if(response.ok){
            getProjectData();
        } else {
            alert('Error: Could not delete Project')
        }
    } catch (error){
        console.error('Error deleting project', error)
    }
}

async function openEditModal(projectId){
    const projectUrl = `${window.ENDPOINTS.projects}${projectId}/`;
    const response = await fetch(projectUrl);
    const project = await response.json();

    document.getElementById('edit-project-id').value = project.project_id; // Use a hidden input for the ID
    document.getElementById('edit-project-title').value = project.title;
    document.getElementById('edit-project-description').value = project.description;
    document.getElementById('edit-project-capacity').value = project.capacity;
    document.getElementById('edit-host-name').value = project.host_name;
    document.getElementById('edit-host-email').value = project.host_email;
    document.getElementById('edit-host-phone').value = project.host_phone;

    document.getElementById('editProjectModal').style.display = 'block';
}

async function editProject(event){
    event.preventDefault();
    const form = document.getElementById('edit-project-modal-form');
    const projectId = form.querySelector('#edit-project-id').value;
    const projectUrl = `${window.ENDPOINTS.projects}${projectId}/`;
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

    const updatedData = {
        title: form.querySelector('#edit-project-title').value,
        description: form.querySelector('#edit-project-description').value,
        capacity: form.querySelector('#edit-project-capacity').value,
        host_name: form.querySelector('#edit-host-name').value,
        host_email: form.querySelector('#edit-host-email').value,
        host_phone: form.querySelector('#edit-host-phone').value,
    };

    const response = await fetch(projectUrl, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(updatedData)
    });

    if(response.ok){
        document.getElementById('editProjectModal').style.display = 'none';
        getProjectData();
    } else {
        alert('Failed to update project.');
        console.error('Update failed:', await response.json());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial data load
    getProjectData();

    // Set an interval to refresh data every 30 seconds (30000 milliseconds)
    setInterval(getProjectData, 30000);

    // Get modal elements
    const addModal = document.getElementById('pModal');
    const editModal = document.getElementById('editProjectModal');
    
    const openBtn = document.getElementById('openModalBtn');
    const addModalCloseBtn = addModal.querySelector('.close-button');
    const editModalCloseBtn = editModal.querySelector('.close-button');

    const editForm = document.getElementById('edit-project-modal-form');
    const addProjectForm = document.getElementById('add-project-modal-form');
    const projectContainer = document.getElementById('project-container');

    
    // Attach event listeners
    addProjectForm.addEventListener('submit', handleAddProject);
    editForm.addEventListener('submit', editProject);


    projectContainer.addEventListener('click', function(event) {
        if(event.target.matches('.delete-btn')){
            const projectId = event.target.dataset.id;
            deleteProject(projectId);
        }

        if (event.target.matches('.edit-btn')) {
            const projectId = event.target.dataset.id;
            openEditModal(projectId);
        }
    });

    openBtn.onclick = function() {
        addModal.style.display = 'block';
    }

    addModalCloseBtn.onclick = function() {
        addModal.style.display = 'none';
    }
    editModalCloseBtn.onclick = function() {
        editModal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == addModal) {
            addModal.style.display = 'none';
        }
        if (event.target == editModal) {
            editModal.style.display = 'none';
        }
    }
});