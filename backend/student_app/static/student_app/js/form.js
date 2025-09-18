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

function populateProjectDropdown(projects){
    const projectDropdown = document.getElementById('project');
    if(!projectDropdown) return;
    projectDropdown.innerHTML = '<option value=""> --Select a Project-- </option>';

    projects.forEach(p => {
        const option = document.createElement('option');
        option.value = p.project_id;
        option.textContent = p.title;
        projectDropdown.appendChild(option);
    });

}

//Autocomplete functionality
//dyanmic preferences functionality
function updateList(preferences){
    list.innerHTML = '';
    preferences.forEach((id, index) => {
    const currentId = id
    const li = document.createElement('li');
    li.textContent = `${index + 1}. ${dropdown.querySelector(`option[value="${id}"]`).text}`;
    console.log('Preferences:', preferences);

    const removeBtn = document.createElement('button');
    removeBtn.textContent = 'Remove';
        removeBtn.onclick = () => {
            preferences = preferences.filter(pid => pid != currentId);
            updateList();
        };
        li.appendChild(removeBtn);
        list.appendChild(li);
    });

    hiddenInput.value = JSON.stringify(projectPreferences);
}

//Posting the form to corresponding tables
//Document listener
document.addEventListener('DOMContentLoaded', async() => {
    //Majors list
    const majors = await getMajors();
    populateMajorDropdown(majors);

    //Preferences List
    const projects = await getProjects();
    populateProjectDropdown(projects);

    const list = document.getElementById('preference-list');
    const hiddenInput = document.getElementById('project-preferences-input');
});