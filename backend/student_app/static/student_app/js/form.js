const pathParts = window.location.pathname.split('/').filter(Boolean);
const roundId = pathParts[pathParts.length - 1];

let roundData = null;

async function getRoundData() {
    if (roundData) return roundData;

    try {
        const response = await fetch(`/api/student/rounds/${roundId}/`);
        if (!response.ok) throw new Error("Failed to fetch round");

        roundData = await response.json();
        return roundData;
    } catch (error) {
        console.error(error);
        return null;
    }
}

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
// async function getProjects(){
//    try{
//         const response = await fetch(window.ENDPOINTS.projects);
        
//         if(!response.ok){
//             throw new Error('Failed to fetch projects');
//         } 
        
//         return await response.json();

//     }catch(error){
//         console.error('Error fetching project data:', error);
//         return[];
//     }
// }

//get list of projects from API
// async function getProjects(){
//     try {
//         const response  = await fetch(`/api/student/rounds/${roundId}/`);

//         if(!response.ok) {
//             throw new Error('Failed to fetch round');
//         }

//         const json = await response.json();
//         return json.projects || [];

//     } catch(error) {
//         console.error(error);
//         return [];
//     }
// }

async function getProjects() {
    const round = await getRoundData();
    return round?.projects || [];
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
    if(!element) return;

    element.classList.add('is-invalid');
    const errorContainer = element.parentElement.querySelector('.invalid-feedback');
    if(errorContainer){
        errorContainer.textContent = message;
    }

}

function clearError(elementId){
    const element = document.getElementById(elementId);
    if(!element) return;

    element.classList.remove('is-invalid');
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
function validateFile(fileInput, keyword, required = false){
    clearError(fileInput.id);

    const file = fileInput.files[0];
    
    if (!file) {
        if (required) {
            showError(fileInput.id, `Please upload a ${keyword.toUpperCase()} file`);
            return false;
        }
        return true;
    }

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
    //Set flag for Split group
    const checkBoxSplitProject = document.getElementById('split_project');
    //const isSplit = checkBoxSplitProject.value;
    const isSplit = checkBoxSplitProject.checked;
    formData.append('split_project', isSplit);

    //Check the agree terms value
    const termsCheckbox = document.getElementById('terms');
    const isChecked = termsCheckbox.checked;
    
    try{
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });


        if (response.ok && isChecked){
            alert('Application submitted successfully!');
            const redirectPage = window.ENDPOINTS.success;
            window.location.href = redirectPage;
        } else if (!isChecked){
            alert('You have not agreed to terms and conidtions, your application will not be submitted')
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
    
    if(!roundData?.is_internal)
    {
        console.log("External round: CV and Resume required");
        const isResumeValid = validateFile(document.getElementById('resume'), 'resume', true);
        const isCvValid = validateFile(document.getElementById('cv'), 'cv', true);
        return isStudentIdValid && isEmailValid && isCwaValid && isResumeValid && isCvValid;
    }

    const isResumeValid = validateFile(document.getElementById('resume'), 'resume', false);
    const isCvValid = validateFile(document.getElementById('cv'), 'cv', false);
    
    return isStudentIdValid && isEmailValid && isCwaValid && isResumeValid && isCvValid;
}

//Document listener
document.addEventListener('DOMContentLoaded', async() => {
    
    getRoundData(roundId);

    //Majors list
    const majors = await getMajors();
    const projects = await getProjects();
    
    populateProjectDropdown(projects);
    populateMajorDropdown(majors);

    setupProjectPreferences(projects);
    setupSearchFunctionality();

    if (roundData?.is_internal) {
        //Hides CV and Resume upload areas
        document.getElementById('resume-section').classList.add('d-none');
        document.getElementById('cv-section').classList.add('d-none');
    } else {
        //Keeps/Shows CV and Resume upload areas
        document.getElementById('resume-section').classList.remove('d-none');
        document.getElementById('cv-section').classList.remove('d-none');
    }

    //Input validation
    document.getElementById('student_id').addEventListener('blur', validateStudentId);
    document.getElementById('cwa').addEventListener('blur', validateCWA);
    document.getElementById('email').addEventListener('blur', validateEmail);
    //File validation
    const resumeInput = document.getElementById('resume');
    resumeInput.addEventListener('change', () => {
        validateFile(resumeInput, 'resume'); 
    });

    const cvInput = document.getElementById('cv');
    resumeInput.addEventListener('change', () => {
        validateFile(cvInput, 'cv'); 
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

// Find all elements that are configured to be popovers
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');

// Initialize each popover
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
document.addEventListener('DOMContentLoaded', function () {
    const $ = (id) => document.getElementById(id);

    const prefList   = $('preference-list');
    const preferred  = $('preferred-list');
    const avoided    = $('avoided-list');
    const hiddenPref = $('project_preferences');
    const select     = $('project');
    const results    = $('autocomplete-results');
    const search     = $('user-search');

    const MAX_PREF  = 5;
    const MAX_AVOID = 5;

    /* ---------- one-time preload + cached searches for students ---------- */
    const studentsEndpoint = (window.ENDPOINTS && window.ENDPOINTS.students) || null;
    const nativeFetch = window.fetch.bind(window);
    let studentsCache = null; // { list: [...], paginated: bool }

    async function preloadStudents() {
        if (studentsCache !== null) return studentsCache;
        if (!studentsEndpoint) return null;

        const all = [];
        let paginated = false;
        let url = studentsEndpoint;

        try {
            while (url) {
                const res = await nativeFetch(url, { credentials: 'same-origin' });
                if (!res.ok) break;

                const json = await res.json();

                if (Array.isArray(json)) {
                    all.push(...json);
                    url = null;
                } else if (json && Array.isArray(json.results)) {
                    all.push(...json.results);
                    paginated = true;
                    url = json.next ? new URL(json.next, window.location.origin).toString() : null;
                } else {
                    url = null;
                }
            }

            studentsCache = { list: all, paginated };
        } catch (e) {
            studentsCache = null;
        }

        return studentsCache;
    }

    if (studentsEndpoint && search) {
        const kick = async () => { await preloadStudents(); };
        search.addEventListener('focus', kick, { once: true });
        search.addEventListener('input', kick, { once: true });
    }

    window.fetch = async function (input, init) {
        const url = (typeof input === 'string') ? input : (input && input.url) || '';

        if (studentsEndpoint && url.startsWith(studentsEndpoint)) {
            await preloadStudents();

            if (studentsCache && Array.isArray(studentsCache.list)) {
                const u = new URL(url, window.location.origin);
                const q = (u.searchParams.get('q') || u.searchParams.get('search') || '').toLowerCase();

                const nameOf = (s) => (s.full_name || s.name || [s.first_name, s.last_name].filter(Boolean).join(' ')).toLowerCase();
                const filtered = q ? studentsCache.list.filter((s) => nameOf(s).includes(q)) : [];

                const payload = studentsCache.paginated
                    ? { results: filtered, next: null, previous: null, count: filtered.length }
                    : filtered;

                return new Response(
                    new Blob([JSON.stringify(payload)], { type: 'application/json' }),
                    { status: 200, headers: { 'Content-Type': 'application/json' } }
                );
            }
        }

        return nativeFetch(input, init);
    };
    /* --------------------------- end cache layer -------------------------- */

    /* ---------------------------- selected tiles -------------------------- */
    function decorateTile(li) {
        if (!li || li.dataset.decorated) return;

        li.classList.add('list-tile');

        li.querySelectorAll('button').forEach((b) => {
            const txt = (b.textContent || '').trim().toLowerCase();
            b.classList.add('btn', 'btn-sm', 'rounded-pill');
            if (txt.startsWith('remove')) b.classList.add('btn-outline-danger');
        });

        if (!li.dataset.cleaned) {
            li.childNodes.forEach((n) => {
                if (n.nodeType === 3) n.textContent = n.textContent.replace(/^\s*\d+\.?\s*/, '');
            });
            li.dataset.cleaned = '1';
        }

        li.dataset.decorated = '1';
    }

    function observeList(list) {
        if (!list) return;

        new MutationObserver((muts) => {
            muts.forEach((m) => {
                m.addedNodes.forEach((n) => { if (n.nodeType === 1) decorateTile(n); });
            });
            updateResultButtons();
        }).observe(list, { childList: true });

        [...list.children].forEach(decorateTile);
    }

    observeList(preferred);
    observeList(avoided);

    /* -------- preferences: numbering + controls + hidden sync ------------ */
    function liId(li) {
        const btn = li.querySelector('button[data-id]');
        return (btn && btn.getAttribute('data-id')) || li.dataset.projectId || '';
    }

    function renumber() {
        if (!prefList) return;
        [...prefList.children].forEach((li, i) => {
            const b = li.querySelector('.pref-num');
            if (b) b.textContent = i + 1;
        });
    }

    function syncHidden() {
        if (!prefList || !hiddenPref) return;

        const ids = [...prefList.children]
            .map((li) => {
                const id = liId(li);
                if (id && !li.dataset.projectId) li.dataset.projectId = id;
                return id;
            })
            .filter(Boolean);

        hiddenPref.value = JSON.stringify(ids);
    }

    function decoratePrefItem(li) {
        if (li.classList.contains('pref-item')) return;

        decorateTile(li);
        li.classList.add('pref-item');

        if (!li.querySelector('.pref-title')) {
            const t = document.createElement('div');
            t.className = 'pref-title';

            const raw = [...li.childNodes]
                .filter((n) => n.nodeType === 3)
                .map((n) => n.textContent)
                .join(' ');

            [...li.childNodes].forEach((n) => { if (n.nodeType === 3) li.removeChild(n); });

            t.textContent = (raw || '').replace(/^\s*\d+\.?\s*/, '').trim();
            li.insertBefore(t, li.firstChild);
        }

        if (!li.querySelector('.pref-num')) {
            const num = document.createElement('span');
            num.className = 'pref-num';
            num.textContent = '0';
            li.insertBefore(num, li.firstChild);
        }

        if (!li.querySelector('.pref-controls')) {
            const grp  = document.createElement('div');
            const up   = document.createElement('button');
            const down = document.createElement('button');

            grp.className = 'pref-controls btn-group ms-2';

            up.type  = 'button';
            down.type = 'button';

            up.className   = 'btn btn-sm btn-outline-secondary';
            down.className = 'btn btn-sm btn-outline-secondary';

            up.title   = 'Move up';
            down.title = 'Move down';

            up.innerHTML   = '&#9650;';
            down.innerHTML = '&#9660;';

            grp.appendChild(up);
            grp.appendChild(down);

            const removeBtn = li.querySelector('button.btn-outline-danger');
            li.insertBefore(grp, removeBtn || null);

            up.addEventListener('click', () => {
                const prev = li.previousElementSibling;
                if (prev) prefList.insertBefore(li, prev);
                renumber(); syncHidden(); syncOptions();
            });

            down.addEventListener('click', () => {
                const next = li.nextElementSibling;
                if (next) prefList.insertBefore(next, li);
                renumber(); syncHidden(); syncOptions();
            });
        }
    }

    if (prefList) {
        new MutationObserver((m) => {
            m.forEach((x) => x.addedNodes.forEach((n) => { if (n.nodeType === 1) decoratePrefItem(n); }));
            renumber(); syncHidden(); syncOptions();
        }).observe(prefList, { childList: true });

        [...prefList.children].forEach(decoratePrefItem);
        renumber();
        syncHidden();
    }

    /* -------------------- autocomplete dropdown: style only --------------- */
    if (results && search) {
        function decorateResultItem(li) {
            if (li.dataset.decorated) return;

            li.classList.add(
                'student-result', 'dropdown-item', 'd-flex',
                'align-items-center', 'px-3', 'py-2'
            );

            const btns = [...li.querySelectorAll('button')];
            if (btns[0]) btns[0].classList.add('ms-auto');

            btns.forEach((b) => {
                const lbl = (b.textContent || '').trim().toLowerCase();
                b.classList.add('chip-btn');
                if (lbl.startsWith('prefer')) b.classList.add('chip-success');
                if (lbl.startsWith('avoid'))  b.classList.add('chip-danger');
            });

            li.dataset.decorated = '1';
        }

        function decorateAll() {
            [...results.children].forEach(decorateResultItem);
            updateResultButtons();
        }

        function syncDropdown() {
            const has     = results.children.length > 0;
            const focused = document.activeElement === search;

            results.classList.toggle('show', has && focused);
            search.setAttribute('aria-expanded', String(has && focused));

            decorateAll();
        }

        // Keep dropdown open during clicks so original handlers fire
        results.addEventListener('mousedown', (e) => e.preventDefault());
        results.addEventListener('click', () => setTimeout(() => results.classList.remove('show'), 150));

        new MutationObserver((m) => {
            if (m.some((x) => x.addedNodes.length || x.removedNodes.length)) syncDropdown();
        }).observe(results, { childList: true });

        search.addEventListener('focus', syncDropdown);
        search.addEventListener('blur',  () => setTimeout(() => results.classList.remove('show'), 120));
    }

    /* ---------------- cap lists at 5 each + disable buttons --------------- */
    function updateResultButtons() {
        if (!results) return;

        const prefFull  = preferred && preferred.children.length >= MAX_PREF;
        const avoidFull = avoided   && avoided.children.length   >= MAX_AVOID;

        [...results.querySelectorAll('button')].forEach((b) => {
            const lbl = (b.textContent || '').trim().toLowerCase();
            if (lbl.startsWith('prefer')) {
                b.disabled = prefFull;
                b.title = prefFull ? `Limit ${MAX_PREF} reached` : '';
            }
            if (lbl.startsWith('avoid')) {
                b.disabled = avoidFull;
                b.title = avoidFull ? `Limit ${MAX_AVOID} reached` : '';
            }
        });
    }

    if (results) {
        new MutationObserver(() => updateResultButtons()).observe(results, { childList: true, subtree: true });

        results.addEventListener('click', (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;

            const lbl = (btn.textContent || '').trim().toLowerCase();

            if (lbl.startsWith('prefer') && preferred.children.length >= MAX_PREF) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }

            if (lbl.startsWith('avoid') && avoided.children.length >= MAX_AVOID) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        });
    }

    /* ----------------- grey-out already chosen project options ------------- */
    function chosenIds() {
        return new Set(prefList ? [...prefList.children].map(liId).filter(Boolean) : []);
    }

    function stripTag(t) {
        return t.replace(/\s+\(chosen\)$/, '');
    }

    function syncOptions() {
        if (!select) return;

        const chosen = chosenIds();

        [...select.options].forEach((opt) => {
            if (!opt.value) return; // skip placeholder

            const used = chosen.has(opt.value);

            if (opt.disabled !== used) opt.disabled = used;

            const clean = stripTag(opt.textContent);
            opt.textContent = used ? `${clean} (chosen)` : clean;
        });

        // Reset if user had a now-disabled option selected
        if (select.selectedOptions[0] && select.selectedOptions[0].disabled) {
            select.value = '';
        }
    }

    if (select) {
        new MutationObserver(() => syncOptions()).observe(select, { childList: true });
        syncOptions();
    }

    // Initial state
    updateResultButtons();
});