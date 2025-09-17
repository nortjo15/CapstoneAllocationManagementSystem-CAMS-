//get the list of majors from API
async function getMajors(){
    try{
        const response = await fetch(window.ENDPOINTS.majors);
        if(!response.ok){
            throw new Error('Failed to fetch Majors');
        } else {
            return await response.json();
        }
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
    const response = await fetch(window.ENDPOINTS.students);
    if(!response.ok){
        throw new Error('Failed to fetch Students');
    } else {
        console.error('Error fetching Student data:', error);
        return [];
    }
}
//get list of projects from API
async function getProjects(){
    const response = await fetch(window.ENDPOINTS.projects);
    if(!response.ok){
        throw new Error('Failed to fetch Projects');
    } else {
        console.error('Error fetching project data');
        return [];
    }
}

//Autocomplete functionality
//dyanmic preferences functionality

//Posting the form to corresponding tables
//Document listener
document.addEventListener('DOMContentLoaded', async() => {
    const majors = await getMajors();
    populateMajorDropdown(majors);
});