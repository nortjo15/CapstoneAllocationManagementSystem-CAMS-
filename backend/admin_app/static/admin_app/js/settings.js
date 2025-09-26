const pageCache = {};

document.addEventListener('DOMContentLoaded', function() {
    loadAdminLogs(window.ENDPOINTS.adminLogs);
});

async function loadAdminLogs(url) {
    const container = document.getElementById('admin-logs-container');
    if(!container) return; 

    //Check cache
    if (pageCache[url]) {
        console.log(`Loading page ${url} from cache.`);
        displayAdminLogs(pageCache[url], container);
        setupPaginationListeners(pageCache[url]); // Re-attach listeners
        return; // Stop here and don't make a network request
    }

    container.innerHTML = '<p> Loading logs... </p>';

    try{
        const response = await fetch(url);

        if(!response.ok){
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        //Store newly fetched data in cache
        pageCache[url] = data;

        displayAdminLogs(data, container);
        setupPaginationListeners(data);
    } catch (error) {
        console.error('Error fecthing admin logs:', error);
        container.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }

}

function displayAdminLogs(data, container) {
    
    if (!container) {
        console.error('Container admin-logs-container not found!');
        return;
    }

    const logs = data.results;
    
    if (!logs || logs.length === 0) {
        container.innerHTML = '<p style="color: #6c757d; font-style: italic;">No admin logs found.</p>';
        return;
    }

    const ACTION_STYLES = {
        'CREATE': { color: '#d4edda' },
        'USER_CREATED': { color: '#d4edda' },
        'EDIT': { color: '#fff3cd' },
        'DELETE': { color: '#f8d7da' },
        'LOGIN': { color: '#cce5ff' },
        'LOGOUT': { color: '#d1ecf1' },
        'default': { color: '#e2e3e5' }
    }; 

    const truncate = (str, num) => {
        if (!str) return '<em>No notes</em>';
        return str.length <= num ? str : str.slice(0, num) + '...';
    };

    const tableRows = logs.map(log => {
        const style = ACTION_STYLES[log.action] || ACTION_STYLES['default'];

        return `
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">${log.user || '<em>System</em>'}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">
                    <span style="background-color: ${style.color}; padding: 2px 6px; border-radius: 3px; font-size: 0.85em;">
                        ${log.action_display || log.action}
                    </span>
                </td>
                <td style="padding: 8px; border: 1px solid #ddd;">${log.target || '<em>No target</em>'}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">${formatDate(log.timestamp)}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">${truncate(log.notes, 50)}</td>
            </tr>
        `;

    }).join('');

    const paginationHtml = `
        <div class="pagination-controls" style="margin-top: 10px; text-align: right;">
            <button id="prev-btn" class="btn btn-secondary"}>Previous</button>
            <button id="next-btn" class="btn btn-secondary"}>Next</button>
        </div>
    `;

    container.innerHTML = `
        <div style="max-height: 500px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #e9ecef;">
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">User</th>
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Action</th>
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Target</th>
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Timestamp</th>
                            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
            </table>
        </div>
        ${paginationHtml} `;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function setupPaginationListeners(data){
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    if (data.previous){
        prevBtn.disabled = false;
        prevBtn.onclick = () => loadAdminLogs(data.previous);
    } else {
        prevBtn.disabled = true;
    }

    if(data.next){
        nextBtn.disabled = false;
        nextBtn.onclick = () => loadAdminLogs(data.next);
    } else {
        nextBtn.disabled = true;
    }
}