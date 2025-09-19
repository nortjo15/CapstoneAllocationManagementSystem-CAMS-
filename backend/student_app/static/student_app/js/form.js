//get the list of majors from API
async function getMajors(){
    try{
        const response = await fetch(window.ENDPOINTS.majors);
        if(!response.ok){
            throw new Error('Failed to fetch Majors');
        }

        return await response.json();
    }catch(error){
        console.error('Error fetching Major data:', error);
        return[];
    }
}

//get list of students from API
async function getStudents(){
    try{
        const response = await fetch(window.ENDPOINTS.students);
        if(!response.ok){
            throw new Error('Failed to fetch Students');
        } 
        
        return await response.json();
    }catch(error){
        console.error('Error fetching Student data:', error);
        return[];
    }
}
//get list of projects from API
async function getProjects(){
   try{
        const response = await fetch(window.ENDPOINTS.projects);
        if(!response.ok){
            throw new Error('Failed to fetch projects');
        } 
        
        return await response.json();

    }catch(error){
        console.error('Error fetching project data:', error);
        return[];
    }
}

function populateMajorDropdown(majors){
    const majorDropdown = document.getElementById('major');
    if(!majorDropdown) return;
    majorDropdown.innerHTML = '<option value=""> --Select a Major-- </option>';

    majors.forEach(major => {
        const option = document.createElement('option');
        option.value = major.id;
        option.textContent = major.name;
        majorDropdown.appendChild(option);
    });

}

function populateProjectDropdown(projects){
    const projectDropdown = document.getElementById('project');
    if(!projectDropdown) return;
    projectDropdown.innerHTML = '<option value=""> --Select a Project to Add-- </option>';

    projects.forEach(p => {
        const option = document.createElement('option');
        option.value = p.project_id;
        option.textContent = p.title;
        projectDropdown.appendChild(option);
    });

}

//Autocomplete functionality
function setupSearchFunctionality(){
    const searchInput = document.getElementById('user-search');
    const resultsList = document.getElementById('autocomplete-results');
    const preferredList = document.getElementById('preferred-list');
    const avoidedList = document.getElementById('avoided-list');
    const avoidedInput = document.getElementById('avoided_students');
    const preferredInput = document.getElementById('preferred_students');

    let preferred = [];
    let avoided = [];

    function updatePreferenceList(type){
        const list = type === 'preferred' ? preferredList : avoidedList;
        const input = type === 'preferred' ? preferredInput : avoidedInput;
        const data = type === 'preferred' ? preferred : avoided;

        list.innerHTML = '';
        data.forEach(student => {
            const li = document.createElement('li');
            li.textContent = student.name;

            const removeBtn = document.createElement('button');
            removeBtn.textContent = 'Remove';
            removeBtn.type ='button';
            removeBtn.className = 'remove-btn';
            removeBtn.dataset.id = student.id;
            removeBtn.dataset.type = type;

            li.appendChild(removeBtn);
            list.appendChild(li);
        });

        input.value = JSON.stringify(data.map(s => s.id));
    }

    resultsList.addEventListener('click', function(event){
        if(event.target.matches('.prefer-btn') || event.target.matches('.avoid-btn')){
            const button = event.target;
            const student = {
                id: button.dataset.id,
                name: button.dataset.name
            };

            const inPreferred = preferred.some(p => p.id === student.id);
            const inAvoided = avoided.some(a => a.id === student.id);

            if(inPreferred || inAvoided){
                alert(`${student.name} is already in a preference list`);
                return;
            }

            if(button.matches('.prefer-btn')){
                preferred.push(student);
                updatePreferenceList('preferred');
            } else if(button.matches('.avoid-btn')){
                avoided.push(student);
                updatePreferenceList('avoided');
            }

            searchInput.value ='';
            resultsList.innerHTML = '';
        }
    });

    searchInput.addEventListener('input', () => {
        fetch(`/students/autocomplete-results?q=${encodeURIComponent(searchInput.value)}`)
            .then(res => res.json())
            .then(data => {
                    resultsList.innerHTML = '';
                    data.forEach(student => {
                        const li = document.createElement('li');

                        li.innerHTML = `
                            <span>${student.name}</span>
                            <div>
                                <button type="button" class="prefer-btn" data-id="${student.student_id}" data-name="${student.name}"> Prefer </button>
                                <button type="button" class="avoid-btn" data-id="${student.student_id}" data-name="${student.name}"> Avoid </button>
                            </div>
                        `;
                        resultsList.appendChild(li);
                    });
            });
    });

    preferredList.addEventListener('click', function(event){
        if(event.target.matches('.remove-btn')){
            const idToRemove = event.target.dataset.id;
            preferred = preferred.filter(student => student.id !== idToRemove);
            updatePreferenceList('preferred');
        }
    });

    avoidedList.addEventListener('click', function(event){
        if(event.target.matches('.remove-btn')){
            const idToRemove = event.target.dataset.id;
            avoided = avoided.filter(student => student.id !== idToRemove);
            updatePreferenceList('avoided');
        }
    });
}

//dyanmic preferences functionality
function setupProjectPreferences(projects){
    const projectDropdown = document.getElementById('project');
    const preferenceList = document.getElementById('preference-list');
    const hiddenInput = document.getElementById('project_preferences');

    let selectedPreferences = [];

    function updatePreferenceDisplay(){
        preferenceList.innerHTML = '';

        selectedPreferences.forEach((projectId, index) => {
            const project = projects.find(p => p.project_id == projectId);
            if(!project) return
            const li = document.createElement('li');
            li.textContent = `${index + 1}. ${project.title}`;

            const removeBtn = document.createElement('button');
            removeBtn.textContent = 'Remove';
            removeBtn.type ='button';
            removeBtn.className = 'remove-btn';
            removeBtn.dataset.id = projectId;

            li.appendChild(removeBtn);
            preferenceList.appendChild(li);
        });

        hiddenInput.value = JSON.stringify(selectedPreferences);
    }

    projectDropdown.addEventListener('change', () => {
        const selectedId = projectDropdown.value;

        if(selectedId && !selectedPreferences.includes(selectedId)){
            if(selectedPreferences.length < 6){
                selectedPreferences.push(selectedId);
                updatePreferenceDisplay();
            } else {
                alert('You can only select up to 6 project preferences')
            }
        }
        projectDropdown.value = '';
    }); 

    preferenceList.addEventListener('click', (event) => {
        if(event.target.matches('.remove-btn')){
            const idToRemove = event.target.dataset.id;
            selectedPreferences = selectedPreferences.filter(pid => pid !== idToRemove);
            updatePreferenceDisplay();
        }
    });
}

function showError(elementId, message){
    const element = document.getElementById(elementId);

    const existingError = element.nextElementSibling;
    if(existingError && existingError.classList.contains('error-message')){
        existingError.remove();
    }

    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    element.parentElement.insertBefore(errorElement, element.nextSibling);
}

function clearError(elementId){
    const element = document.getElementById(elementId);
    const existingError = element.nextElementSibling;
    if(existingError && existingError.classList.contains('error-message')){
        existingError.remove();
    }
}

//Validate StudentId
function validateStudentId() {
    const studentId = document.getElementById('student_id');

    if(!/^\d{8}$/.test(studentId.value)){
        showError('student_id', 'Student ID must be exactly 8 digits');
        return false;
    }
    clearError('student_id');
    return true;
}
//Validate Email
function validateEmail(){
    const emailEl = document.getElementById('email');

    if(!/^[a-zA-Z0-9._%+-]+@student\.curtin\.edu\.au$/.test(emailEl.value)){
        showError('email', 'Email must be in the format E.g. john.smith@student.curtin.edu.au');
        return false;
    }
    clearError('email');
    return true;
}
//Validate CWA
function validateCWA() {
    const cwaEl = document.getElementById('cwa');
    let valueStr = cwaEl.value;

    clearError('cwa');

    if(valueStr.trim() === ''){
        showError('cwa', 'You must enter in a CWA');
        return false;
    }

    if(!/^\d+(\.\d{2})?$/.test(valueStr)){
        showError('cwa', 'CWA must be a number with up to two decimal places');
        return false;
    }

    const value = parseFloat(valueStr);

    if (value < 0 || value > 100){
        showError('cwa', 'CWA must be between 0 and 100');
        return false;
    }
    clearError('cwa');
    return true;
}
//Validate file name
function validateFile(fileInput, keyword){
    clearError(fileInput.id);

    const file = fileInput.files[0];
    if(!file) return true;

    if (file.type !== 'application/pdf'){
        showError(fileInput.id, 'File must be in PDF format');
        fileInput.value = '';
        return false;
    }

    const fileNameRegex = new RegExp(`^[a-zA-Z]+-[a-zA-Z]+_${keyword}_\\d{4}\\.pdf$`, 'i');
    if(!fileNameRegex.test(file.name)){
        showError(fileInput.id, `Filename must be in the format "Last-First_${keyword}_YYYY.pdf"`);
        fileInput.value = '';
        return false;
    }
    return true;
}

function displayBackendErrors(errors){
    for (const field in errors){
        const inputElement = document.getElementById(field);
        const errorValue = errors[field];
        let errorMessage;

        if(Array.isArray(errorValue)){
            errorMessage = errorValue.join(' ');
        } else {
            errorMessage = errorValue;
        }
        
        if(inputElement){
            showError(field, errorMessage);
        } else {
            alert(`Error with ${field}: ${errorMessage}`);
        }
    }
}

//Posting the form to corresponding tables
async function submitForm(){
    const apiUrl = window.ENDPOINTS.submit
    const form = document.getElementById('application-form');
    const formData = new FormData(form);
    const csrfToken = formData.get('csrfmiddlewaretoken');

    //Get List data
    const projectPreferences = JSON.parse(document.getElementById('project_preferences').value || '[]');
    const preferredStudents = JSON.parse(document.getElementById('preferred_students').value || '[]');
    const avoidedStudents = JSON.parse(document.getElementById('avoided_students').value || '[]');

    formData.delete('project_preferences');
    formData.delete('preferred_students');
    formData.delete('avoided_students');

    projectPreferences.forEach(id => formData.append('project_preferences', id));
    preferredStudents.forEach(id => formData.append('preferred_students', id));
    avoidedStudents.forEach(id => formData.append('avoided_students', id));
    
    //Set flag to application submitted
    formData.append('application_submitted', 'true');
    try{
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });

        if (response.ok){
            alert('Application submitted successfully!');
            const redirectPage = window.ENDPOINTS.success;
            window.location.href = redirectPage;
        } else {
            const errors = await response.json();
            console.error('Validation errors', errors);
            alert('Submission failed. Please check the form for errors');
            displayBackendErrors(errors);
        }
    } catch(error){
        console.error('Network error during submission', error);
        alert('A network error occurred. Please try again');
    }
}

//Validate entire form
function validateEntireForm() {
    const isStudentIdValid = validateStudentId();
    const isEmailValid = validateEmail();
    const isCwaValid = validateCWA();
    const isResumeValid = validateFile(document.getElementById('resume'), 'resume');
    
    return isStudentIdValid && isEmailValid && isCwaValid && isResumeValid;
}

//Document listener
document.addEventListener('DOMContentLoaded', async() => {
    //Majors list
    const majors = await getMajors();
    const projects = await getProjects();

    populateProjectDropdown(projects);
    populateMajorDropdown(majors);

    setupProjectPreferences(projects);
    setupSearchFunctionality();

    //Input validation
    document.getElementById('student_id').addEventListener('blur', validateStudentId);
    document.getElementById('cwa').addEventListener('blur', validateCWA);
    document.getElementById('email').addEventListener('blur', validateEmail);
    //File validation
    const resumeInput = document.getElementById('resume');
    resumeInput.addEventListener('change', () => {
        validateFile(resumeInput, 'resume'); 
    });
    //Submit form
    document.getElementById('application-form').addEventListener('submit', (event) => {
        event.preventDefault();
        if(validateEntireForm()){
            submitForm();
        } else {
            alert('Please correct the errors before submitting');
        }
        
    });
    
});