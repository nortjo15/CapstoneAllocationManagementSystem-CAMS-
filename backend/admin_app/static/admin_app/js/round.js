document.addEventListener('DOMContentLoaded', function() {
    console.log("testing if this is connected");
    const roundsList = document.getElementById('rounds-list');
    const createNewRoundBtn = document.getElementById('create-new-round-btn');
    const rightPaneTitle = document.getElementById('right-pane-title');

    const roundDetailsView = document.getElementById('round-details-view');
    const createRoundView = document.getElementById('create-round-view');

    const createRoundForm = document.getElementById('create-round-form');
    const editRoundForm = document.getElementById('edit-round-form');
    const deleteRoundBtn = document.getElementById('delete-round-btn');

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

    async function fetchProjects() {
        const response = await fetch('/api/projects/');
        if (!response.ok) {
            console.error('Failed to fetch projects');
            return [];
        }
        return await response.json();
    }

    function showMessage(message, type = 'info') {
        const msgBox = document.createElement('div');
        msgBox.textContent = message;
        msgBox.classList.add('message-box', `${type}-message`);
        document.body.appendChild(msgBox);
        setTimeout(() => msgBox.remove(), 3000);
    }

    async function populateRoundsList() {
        try {
            const response = await fetch('/api/rounds/');
            const rounds = await response.json();

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
        try {
            const response = await fetch(`/api/rounds/${roundId}/`);
            const round = await response.json();
            const projects = await fetchProjects();

            document.getElementById('edit-round-id').value = round.round_id;
            document.getElementById('edit-round-name').value = round.round_name;
            document.getElementById('edit-open-date').value = formatDateForInput(round.open_date);
            document.getElementById('edit-close-date').value = formatDateForInput(round.close_date);

            const editProjectsSelect = document.getElementById('edit-round-projects');
            editProjectsSelect.innerHTML = '';
            projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project.project_id;
                option.textContent = project.title;
                if (round.projects.includes(project.project_id)) {
                    option.selected = true;
                }
                editProjectsSelect.appendChild(option);
            });

            rightPaneTitle.textContent = `Edit Round: ${round.round_name}`;
            showRightPane(roundDetailsView);
        } catch (error) {
            console.error('Error fetching round details:', error);
            showMessage('Failed to load round details.', 'error');
        }
    }

    async function showCreateForm() {
        rightPaneTitle.textContent = 'Create New Round';
        showRightPane(createRoundView);
        const projects = await fetchProjects();
        const createProjectsSelect = document.getElementById('create-round-projects');
        createProjectsSelect.innerHTML = '';
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.project_id;
            option.textContent = project.title;
            createProjectsSelect.appendChild(option);
        });
    }

    createNewRoundBtn.addEventListener('click', showCreateForm);

    createRoundForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const roundName = document.getElementById('create-round-name').value;
        const openDate = document.getElementById('create-open-date').value;
        const closeDate = document.getElementById('create-close-date').value;
        const selectedProjects = [...document.getElementById('create-round-projects').options]
            .filter(option => option.selected)
            .map(option => option.value);

        const newRound = {
            round_name: roundName,
            open_date: openDate,
            close_date: closeDate,
            projects: selectedProjects
        };

        try {
            const response = await fetch('/api/rounds/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newRound)
            });
            if (response.ok) {
                showMessage('Round created successfully!', 'success');
                createRoundForm.reset();
                populateRoundsList(); 
                rightPaneTitle.textContent = 'Select a Round';
                roundDetailsView.classList.add('hidden');
                createRoundView.classList.add('hidden');
            } else {
                console.error('Error creating round:', response.statusText);
                showMessage('Error creating round.', 'error');
            }
        } catch (error) {
            console.error('Failed to create round:', error);
            showMessage('An error occurred. Please try again.', 'error');
        }
    });

    editRoundForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const roundId = document.getElementById('edit-round-id').value;
        const roundName = document.getElementById('edit-round-name').value;
        const openDate = document.getElementById('edit-open-date').value;
        const closeDate = document.getElementById('edit-close-date').value;
        const selectedProjects = [...document.getElementById('edit-round-projects').options]
            .filter(option => option.selected)
            .map(option => option.value);

        const updatedRound = {
            round_name: roundName,
            open_date: openDate,
            close_date: closeDate,
            projects: selectedProjects
        };

        try {
            const response = await fetch(`/api/rounds/${roundId}/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedRound)
            });
            if (response.ok) {
                showMessage('Round updated successfully!', 'info');
                populateRoundsList();
            } else {
                console.error('Error updating round:', response.statusText);
                showMessage('Error updating round.', 'error');
            }
        } catch (error) {
            console.error('Failed to update round:', error);
            showMessage('An error occurred. Please try again.', 'error');
        }
    });


    deleteRoundBtn.addEventListener('click', async function() {
        const roundId = document.getElementById('edit-round-id').value;
        if (confirm('Are you sure you want to delete this round?')) {
            try {
                const response = await fetch(`/api/rounds/${roundId}/`, {
                    method: 'DELETE'
                });
                if (response.status === 204) {
                    showMessage('Round deleted successfully!', 'error');
                    populateRoundsList(); 
                    rightPaneTitle.textContent = 'Select a Round';
                    roundDetailsView.classList.add('hidden');
                    createRoundView.classList.add('hidden');
                } else {
                    console.error('Error deleting round:', response.statusText);
                    showMessage('Error deleting round.', 'error');
                }
            } catch (error) {
                console.error('Failed to delete round:', error);
                showMessage('An error occurred. Please try again.', 'error');
            }
        }
    });

    populateRoundsList();
});
