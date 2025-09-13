const projectList = document.getElementById('projectList');

async function getProjectData(){
    const projectContainer = document.getElementById('project-container');
    const apiUrl = document.body.dataset.projectsApiUrl;

    try{
        const response = await fetch(apiUrl);
        const projects = await response.json();
        //Clear loading
        projectContainer.innerHTML = '';

        if(projects.length == 0){
            projectList.innerHTML = '<li>No Projects Found</li>';
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
                    </div>
                `;
                projectContainer.appendChild(card);
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
