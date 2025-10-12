(function() {
    const state = {
        degrees: [],
        majors: [],
    };

    const elements = {
        // Main containers
        majorsTableContainer: document.getElementById('majors-table-container'),
        degreesTableContainer: document.getElementById('degrees-table-container'),
        majorsHeading: document.getElementById('majors-heading'),
        backdrop: document.getElementById('backdrop'),

        // Buttons
        addDegreeBtn: document.getElementById('add-degree-btn'),
        addMajorBtn: document.getElementById('add-major-btn'),

        // Degree Form Slide-over
        degreeSlide: document.getElementById('degree-slide'),
        degreeForm: document.getElementById('degree-form'),
        degreeFormTitle: document.getElementById('degree-form-title'),
        degreeIdInput: document.getElementById('degree-id'),
        degreeNameInput: document.getElementById('degree-name'),

        // Major Form Slide-over 
        majorSlide: document.getElementById('major-slide'),
        majorForm: document.getElementById('major-form'),
        majorFormTitle: document.getElementById('major-form-title'),
        majorIdInput: document.getElementById('major-id'),
        majorNameInput: document.getElementById('major-name'),
        majorDegreeSelect: document.getElementById('major-degree-select'), // Dropdown for degrees
    };

    async function apiFetch(url, options = {}){
        if(options.method && options.method !== 'GET'){
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            options.headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                ...options.headers, 
            };
        }
        const response = await fetch(url, options);
        if(!response.ok){
            const errorData = await response.json();
            const error = new Error('API request failed');

            error.data = errorData;
            error.status = response.status;

            throw error;
        }
        // For DELETE requests that return no content
        if (response.status === 204) return null;
        return response.json();
    }

    function renderMajorsTable() {
        if(state.majors.length === 0){
            elements.majorsTableContainer.innerHTML = "<p>No majors found</p>";
            return;
        }
        const tableRows = state.majors.map(major => `
            <tr>
                <td>${major.degree_name}</td>
                <td>${major.name}</td>
                <td>${major.student_count}</td>
                <td class="actions">
                    <button class="btn btn-sm btn-secondary edit-major-btn" data-id="${major.id}">Edit</button>
                    <button class="btn btn-sm btn-danger delete-major-btn" data-id="${major.id}">Delete</button>
                </td>
            </tr>
        `).join('');

        elements.majorsTableContainer.innerHTML = `
            <table class="table">
                <thead><tr><th>Degree</th><th>Major</th><th>Student Count</th><th>Actions</th></tr></thead>
                <tbody>${tableRows}</tbody>
            </table>`;
    }

    function renderDegreesTable() {
        if(state.degrees.length === 0){
            elements.degreesTableContainer.innerHTML = "<p> No Degrees Found </p>";
            return;
        }

        const tableRows = state.degrees.map(degree => `
            <tr>   
                <td>${degree.name}</td>
                <td class="actions">
                    <button class="btn btn-sm btn-secondary edit-degree-btn" data-id="${degree.id}">Edit</button>
                    <button class="btn btn-sm btn-danger delete-degree-btn" data-id="${degree.id}">Delete</button>
                </td>
            </tr>
        `).join('');

         elements.degreesTableContainer.innerHTML = `
            <table class="table">
                <thead><tr><th>Degree</th></tr></thead>
                <tbody>${tableRows}</tbody>
            </table>`;
    }

    function openSlide(slideElement){
        slideElement.classList.add('open');
        elements.backdrop.style.display = 'block';
    }

    function closeSlides(){
        document.querySelectorAll('.slideover.open').forEach(el => el.classList.remove('open'));
        elements.backdrop.style.display = 'none';
    }

    async function handleOpenDegreeForm(degreeId = null) {
        elements.degreeForm.reset();
        elements.degreeIdInput.value = '';
        if (degreeId) {
            // Editing: fetch the existing degree data and populate the form
            const degree = await apiFetch(`${window.ENDPOINTS.degrees}${degreeId}/`);
            elements.degreeFormTitle.textContent = 'Edit Degree';
            elements.degreeIdInput.value = degree.id;
            elements.degreeNameInput.value = degree.name;
        } else {
            // Creating: show a blank form
            elements.degreeFormTitle.textContent = 'Create Degree';
        }
        openSlide(elements.degreeSlide);
    }

    async function handleOpenMajorForm(majorId = null){
        elements.majorForm.reset();
        elements.majorIdInput.value = '';

        //Populate degrees dropdown
        elements.majorDegreeSelect.innerHTML = '<option value="">Loading...</option>';
        state.degrees = await apiFetch(window.ENDPOINTS.degrees); // Fetch all degrees
        let degreeOptions = state.degrees.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
        elements.majorDegreeSelect.innerHTML = `<option value="">-- Select a Degree --</option>${degreeOptions}`;

        if(majorId){
            const major = await apiFetch(`${window.ENDPOINTS.majors}${majorId}/`);
            elements.majorFormTitle.textContent = 'Edit Major';
            elements.majorIdInput.value = major.id;
            elements.majorNameInput.value = major.name;
            elements.majorDegreeSelect.value = major.degree;
        } else {
            elements.majorFormTitle.textContent = 'Create Major';
        }
        openSlide(elements.majorSlide);
    }

    async function refreshMajors() {
        const majorData = await apiFetch(window.ENDPOINTS.majors);
        state.majors = majorData.results || majorData;
        renderMajorsTable();
    }

    async function refreshDegrees() {
        const degreeData = await apiFetch(window.ENDPOINTS.degrees);
        state.degrees = degreeData.results || degreeData;
        renderDegreesTable();
    }
    
    // Handles the submission for both creating and editing a degree.
    async function handleDegreeSubmit(event) {
        event.preventDefault();
        const degreeId = elements.degreeIdInput.value;
        const url = degreeId ? `${window.ENDPOINTS.degrees}${degreeId}/` : window.ENDPOINTS.degrees;
        const method = degreeId ? 'PUT' : 'POST';

        const data = { name: elements.degreeNameInput.value };
            
        try {
            await apiFetch(url, {
                method: method,
                body: JSON.stringify(data),
            });
            closeSlides();
            // Refresh the entire table to show the new/updated data
            await Promise.all([refreshDegrees(), refreshMajors()]);
        } catch (error) {
            alert('Failed to save degree.');
        }
    }

    async function handleMajorSubmit(event) {
        event.preventDefault();
        const majorId = elements.majorIdInput.value;
        const url = majorId ? `${window.ENDPOINTS.majors}${majorId}/` : window.ENDPOINTS.majors;
        const method = majorId ? 'PUT' : 'POST';

        const data = { 
            name: elements.majorNameInput.value,
            degree: elements.majorDegreeSelect.value,
        };
            
        try {
            await apiFetch(url, {
                method: method,
                body: JSON.stringify(data),
            });
            closeSlides();
            await refreshMajors();
        } catch (error) {
            alert('Failed to save major');
        }
    }

    async function handleDelete(type, id){
        const isMajor = type === 'major';
        const message = isMajor 
            ? 'Are you sure you want to delete this major?'
            : 'Are you sure you want to delete this degree? This will also delete all associated majors';
        
        if (!confirm(message)) return;

        const originalState = isMajor ? [...state.majors] : [...state.degrees];
        const url = isMajor ? `${window.ENDPOINTS.majors}${id}/` : `${window.ENDPOINTS.degrees}${id}/`;

        if(isMajor){
            state.majors = state.majors.filter(m => m.id !== parseInt(id));
            renderMajorsTable();
        } else {
            state.degrees = state.degrees.filter(d => d.id !== parseInt(id));
            state.majors = state.majors.filter(m => m.degree !== parseInt(id));

            renderDegreesTable();
            renderMajorsTable();
        }

        try {
            await apiFetch(url, {method: 'DELETE'});
            if(isMajor){
                await refreshMajors();
            }
        } catch (error){
            let errorMessage = `Failed to delete ${type}`;

            if(error && error.data && error.data.detail){
                errorMessage = error.data.detail;
            }

            alert(errorMessage);

            if(isMajor){
                state.majors = originalState;
                renderMajorsTable();
            } else {
                state.degrees = originalState;
                renderDegreesTable();
            }
        }

    }

    function setupEventListeners() {
        // Add Degree button
        elements.addDegreeBtn.addEventListener('click', () => handleOpenDegreeForm());
        elements.addMajorBtn.addEventListener('click', () => handleOpenMajorForm());
             
        // Form submission
        elements.degreeForm.addEventListener('submit', handleDegreeSubmit);
        elements.majorForm.addEventListener('submit', handleMajorSubmit);
            
        // Close buttons on slide-overs and backdrop
        document.querySelectorAll('.close-slide-btn, #backdrop').forEach(el => {
            el.addEventListener('click', closeSlides);
        });

        // Event delegation for Edit/Delete buttons on the table
        elements.majorsTableContainer.addEventListener('click', (event) => {
            if(event.target.matches('.edit-major-btn')) {
                handleOpenMajorForm(event.target.dataset.id)
            }
            if (event.target.matches('.delete-major-btn')) {
                handleDelete('major', event.target.dataset.id);
            }
        });

        elements.degreesTableContainer.addEventListener('click', (event) => {
            if(event.target.matches('.edit-degree-btn')) {
                handleOpenDegreeForm(event.target.dataset.id)
            }
            if (event.target.matches('.delete-degree-btn')) {
                handleDelete('degree', event.target.dataset.id);
            }
        });
    }

    async function init() {
        await Promise.all([refreshDegrees(), refreshMajors()]);
        // Set up all the interactive parts of the page
        setupEventListeners();
    }
        
    // Start the application
    init();
})();
