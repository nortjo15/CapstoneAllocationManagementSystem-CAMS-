(function() {
    const state = {
        degrees: [],
        majors: [],
    };

    const elements = {
        // Main containers
        majorsTableContainer: document.getElementById('majors-table-container'),
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
            console.error("API Error:", response.status, await response.text());
            throw new Error('API request failed');
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
                    <button class="btn btn-sm btn-secondary edit-major-btn" data-major-id="${major.id}">Edit</button>
                    <button class="btn btn-sm btn-danger delete-major-btn" data-major-id="${major.id}">Delete</button>
                </td>
            </tr>
        `).join('');

        elements.majorsTableContainer.innerHTML = `
            <table class="table">
                <thead><tr><th>Degree</th><th>Major</th><th>Student Count</th><th>Actions</th></tr></thead>
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
            await init(); 
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
            await init();
        } catch (error) {
            alert('Failed to save major');
        }
    }

    async function handleDeleteMajor(majorId) {
        if (!confirm('Are you sure you want to delete this major?')) return;
            
        try {
            await apiFetch(`${window.ENDPOINTS.majors}${majorId}/`, { method: 'DELETE' });
            // Remove the major from the local state and re-render
            state.majors = state.majors.filter(m => m.id !== parseInt(majorId));
            await init();
        } catch (error) {
            alert('Failed to delete major.');
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
                handleDeleteMajor(event.target.dataset.id);
            }
        });
    }

    async function init() {
        // Fetch the initial list of majors to display in the table
        const majorsData = await apiFetch(window.ENDPOINTS.majors);
        // Handle both paginated and unpaginated responses
        state.majors = majorsData.results || majorsData;
        renderMajorsTable();
            
        // Set up all the interactive parts of the page
        setupEventListeners();
    }
        
    // Start the application
    init();
})();
