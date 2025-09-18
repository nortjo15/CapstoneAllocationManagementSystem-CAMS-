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
function setupSearchFunctionality(students){
    const searchInput = document.getElementById('user-search');
    const resultsList = document.getElementById('autocomplete-results');
    const preferredList = document.getElementById('preferred-list');
    const avoidedList = document.getElementById('avoided-list');
    const avoidedInput = document.getElementById('avoided-input');
    const preferredInput = document.getElementById('preferred-input');

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
    const hiddenInput = document.getElementById('project-preferences-input');

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

//Validate form


//Posting the form to corresponding tables
//Document listener
document.addEventListener('DOMContentLoaded', async() => {
    //Majors list
    const majors = await getMajors();
    const projects = await getProjects();
    const students = await getStudents();

    populateProjectDropdown(projects);
    populateMajorDropdown(majors);

    setupProjectPreferences(projects);
    setupSearchFunctionality(students);
    
});