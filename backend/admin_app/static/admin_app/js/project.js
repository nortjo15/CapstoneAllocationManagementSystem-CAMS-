const projectList = document.getElementById('projectList');

async function getProjectData(){
    const apiUrl = document.body.dataset.projectsApiUrl;

    try{
        const response = await fetch(apiUrl);
        const data = await response.json();

        projectList.innerHTML = '';

        if(data.length == 0){
            projectList.innerHTML = '<li>No Projects Found</li>';
        } else {
            data.forEach(project => {
                const listItem = document.createElement('li');
                listItem.textContent = `${project.title}`;
                projectList.appendChild(listItem);
            });
        }   
    } catch (error) {
        console.error('Error fetching data:', error);
        projectList.innerHTML = '<li>Could not load projects</li>';
    }
}

// 1. Call the function immediately when the page loads
document.addEventListener('DOMContentLoaded', getProjectData);

// 2. Set an interval to call the function again every 10 seconds (10000 milliseconds)
setInterval(getProjectData, 10000);
