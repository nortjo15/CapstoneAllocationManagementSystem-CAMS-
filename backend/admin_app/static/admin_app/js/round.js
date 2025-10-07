const roundsList = document.getElementById('rounds-list');
const createNewRoundBtn = document.getElementById('create-new-round-btn');
const rightPaneTitle = document.getElementById('right-pane-title');

const roundDetailsView = document.getElementById('round-details-view');
const createRoundView = document.getElementById('create-round-view');

const createRoundForm = document.getElementById('create-round-form');
const editRoundForm = document.getElementById('edit-round-form');
const deleteRoundBtn = document.getElementById('delete-round-btn');

const createAlertBox = document.getElementById('create-submit-alert');
const editAlertBox = document.getElementById('edit-submit-alert');

function showRightPane(view) {
    roundDetailsView.classList.add('hidden');
    createRoundView.classList.add('hidden');
    view.classList.remove('hidden');
}

function formatDateForInput(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function showSuccessAlert(alertBox) {
    alertBox.style.display = 'block';
    setTimeout(() => alertBox.style.display = 'none', 3000);
}

async function fetchProjects() {
    const apiUrl = window.ENDPOINTS.projects;
    try {
        const response = await fetch(apiUrl);
        if(!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const projects = await response.json();
        return projects;
    } catch (error) {
        console.error('Problem fetching projects:', error);
    }  
}

async function fetchRounds() {
    const apiUrl = window.ENDPOINTS.rounds;
    try {
        const response = await fetch(apiUrl);
        if(!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const rounds = await response.json();
        return rounds;
    } catch (error) {
        console.error('Problem fetching rounds:', error);
    }  
}

async function populateRoundsList() {
    try {
        const rounds = await fetchRounds();

        roundsList.innerHTML = '';
        
        rounds.forEach(round => {
            const roundItem = document.createElement('div');
            roundItem.className = 'round-item';
            roundItem.innerHTML = `
                <p>${round.round_name}</p>
                <p>Status: ${round.status}</p>
            `;
            roundItem.dataset.id = round.round_id;
            roundItem.addEventListener('click', () => showRoundDetails(round.round_id));
            roundsList.appendChild(roundItem);
        });
    } catch (error) {
        console.error('Error fetching rounds:', error);
        roundsList.innerHTML = '<p>Failed to load rounds.</p>';
    }
}

async function showRoundDetails(roundId) {
    const apiUrl = window.ENDPOINTS.rounds;
    try {
        const response = await fetch(`${apiUrl}${roundId}/`);
        const round = await response.json();
        const projects = await fetchProjects();

        document.getElementById('edit-round-id').value = round.round_id;
        document.getElementById('edit-round-name').value = round.round_name;
        document.getElementById('edit-open-date').value = formatDateForInput(round.open_date);
        document.getElementById('edit-close-date').value = formatDateForInput(round.close_date);
        document.getElementById('edit-status').value = round.status;
        document.getElementById('edit-type').value = round.is_internal;

        const editProjectsSelect = document.getElementById('edit-round-projects');
        editProjectsSelect.innerHTML = '';

        const roundProjectIds = round.projects.map(p => p.project_id);

        projects.forEach(project => {
            const option = document.createElement('input');
            option.type = 'checkbox';
            option.name = 'projects';
            option.id = project.project_id;
            option.value = project.project_id;
            const label = document.createElement('label');
            label.htmlFor = project.project_id;
            label.textContent = project.title;
            if (roundProjectIds.includes(project.project_id)) {
                option.checked = true;
            }
            editProjectsSelect.appendChild(option);
            editProjectsSelect.appendChild(label);
        });

        rightPaneTitle.textContent = `Edit Round: ${round.round_name}`;
        showRightPane(roundDetailsView);

    } catch (error) {
        console.error('Error fetching round details:', error);
    }
}

async function showCreateForm() {
    rightPaneTitle.textContent = 'Create New Round';
    showRightPane(createRoundView);
    const projects = await fetchProjects();
    const createProjectsSelect = document.getElementById('create-round-projects');
    projects.forEach(project => {
        const option = document.createElement('input');
        option.type = 'checkbox';
        option.name = 'projects';
        option.id = project.project_id;
        option.value = project.project_id;
        const label = document.createElement('label');
        label.htmlFor = project.project_id;
        label.textContent = project.title;
        createProjectsSelect.appendChild(option);
        createProjectsSelect.appendChild(label);
    });
}

async function getSelectedProjects() {
    
    return checkboxes;
}

createRoundForm.addEventListener('submit', async function(e) {
    const apiUrl = window.ENDPOINTS.rounds;
    e.preventDefault();
    
    const roundName = document.getElementById('create-round-name').value;
    const openDate = document.getElementById('create-open-date').value;
    const closeDate = document.getElementById('create-close-date').value;
    const status = document.getElementById('edit-status').value;
    //const isInternal = 'False';
    const type = document.getElementById('create-type').value;

    let selectedProjects = Array.from(
        document.querySelectorAll('#create-round-projects input[type="checkbox"]:checked')
    ).map(cb => parseInt(cb.value));
    console.log(selectedProjects);

    const newRound = {
        round_name: roundName,
        open_date: openDate,
        close_date: closeDate,
        status: status,
        is_internal: type,
        project_ids: selectedProjects
    };

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "Content-Type": "application/json",
            },
            body: JSON.stringify(newRound)
        });
        if (response.ok) {
            console.log('Round created successfully!', 'success');
            showSuccessAlert(createAlertBox);
            createRoundForm.reset();
            populateRoundsList(); 
            rightPaneTitle.textContent = 'Select a Round';
            roundDetailsView.classList.add('hidden');
            createRoundView.classList.add('hidden');
        } else {
            console.error('Error creating round:', response.statusText);
            //showMessage('Error creating round.', 'error');
        }
    } catch (error) {
        console.error('Failed to create round:', error);
        //showMessage('An error occurred. Please try again.', 'error');
    }
});




editRoundForm.addEventListener('submit', async function(e) {
    const apiUrl = window.ENDPOINTS.rounds;
    e.preventDefault();
    const roundId = document.getElementById('edit-round-id').value;
    const roundName = document.getElementById('edit-round-name').value;
    const openDate = document.getElementById('edit-open-date').value;
    const closeDate = document.getElementById('edit-close-date').value;
    const status = document.getElementById('edit-status').value;
    const type = document.getElementById('create-type').value;

    let selectedProjects = Array.from(
        document.querySelectorAll('#edit-round-projects input[type="checkbox"]:checked')
    ).map(cb => parseInt(cb.value));

    const updatedRound = {
        round_name: roundName,
        open_date: openDate,
        close_date: closeDate,
        status: status,
        is_internal: type,
        project_ids: selectedProjects
    };

    try {
        const response = await fetch(`${apiUrl}${roundId}/`, {
            method: 'PATCH',
            headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "Content-Type": "application/json",
            },
            body: JSON.stringify(updatedRound)
        });
        if (response.ok) {
            //showMessage('Round updated successfully!', 'info');
            showSuccessAlert(editAlertBox);
            populateRoundsList();
        } else {
            console.error('Error updating round:', response.statusText);
            //showMessage('Error updating round.', 'error');
        }
    } catch (error) {
        console.error('Failed to update round:', error);
        //showMessage('An error occurred. Please try again.', 'error');
    }
});

deleteRoundBtn.addEventListener('click', async function() {
    const apiUrl = window.ENDPOINTS.rounds;
    const roundId = document.getElementById('edit-round-id').value;
    if (confirm('Are you sure you want to delete this round?')) {
        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await fetch(`${apiUrl}${roundId}/`, {
                method: 'DELETE',
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/json"
                }
            });
            if (response.status === 204) {
                //showMessage('Round deleted successfully!', 'error');
                populateRoundsList(); 
                rightPaneTitle.textContent = 'Select a Round';
                roundDetailsView.classList.add('hidden');
                createRoundView.classList.add('hidden');
            } else {
                console.error('Error deleting round:', response.statusText);
                //showMessage('Error deleting round.', 'error');
            }
        } catch (error) {
            console.error('Failed to delete round:', error);
            //showMessage('An error occurred. Please try again.', 'error');
        }
    }
});

function setup() {
    createNewRoundBtn.addEventListener('click', showCreateForm);
    roundDetailsView.classList.add('hidden');
    createRoundView.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', function() {
    setup();
    populateRoundsList();
});