const pageCache = {};
let currentLogsUrl = null; // track current page URL for refreshes

// Exported so settings.html can call it after clear
window.loadAdminLogs = loadAdminLogs;

document.addEventListener('DOMContentLoaded', function() {
    loadAdminLogs(window.ENDPOINTS.adminLogs);
});

async function loadAdminLogs(url) {
    const container = document.getElementById('admin-logs-container');
    if(!container) return; 

    // Invalidate cache when loading the first page after a clear
    if (url === window.ENDPOINTS.adminLogs) {
        for (const k in pageCache) delete pageCache[k];
    }

    // Track current url for refreshes (delete, etc.)
    currentLogsUrl = url;

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

// Safely escape HTML to avoid injecting markup when rendering notes
function escapeHTML(str) {
    if (str === null || str === undefined) return '';
    return String(str).replace(/[&<>"']/g, (s) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[s]);
}

function displayAdminLogs(data, container) {
    if (!container) {
        console.error('Container admin-logs-container not found!');
        return;
    }

    const logs = data.results || [];

    const ACTION_STYLES = {
        // Generic
        'CREATE': { color: '#d4edda' },
        'USER_CREATED': { color: '#d4edda' },
        'EDIT': { color: '#fff3cd' },
        'DELETE': { color: '#f8d7da' },
        'LOGIN': { color: '#cce5ff' },
        'LOGOUT': { color: '#d1ecf1' },

        // Groups
        'GROUP_CREATED': { color: '#f3d3f0' },
        'GROUP_UPDATED': { color: '#fff3cd' },
        'GROUP_DELETED': { color: '#f8d7da' },

        // Students
        'STUDENT_APPLIED': { color: '#d4edda' },
        'STUDENT_UPDATED': { color: '#fff3cd' },

        'default': { color: '#e2e3e5' }
    };

    if (!logs.length) {
        container.innerHTML = `
            <div style="border: 1px solid #ddd; border-radius: 4px; padding: 16px;">
                <p style="color: #6c757d; font-style: italic; margin: 0;">No admin logs found.</p>
                <div class="pagination-controls" style="margin-top: 10px; text-align: right;">
                    <button id="prev-btn" class="btn btn-secondary">Previous</button>
                    <button id="next-btn" class="btn btn-secondary">Next</button>
                </div>
            </div>
        `;
        return;
    }

    const tableRows = logs.map(log => {
        const style = ACTION_STYLES[log.action] || ACTION_STYLES['default'];
        // Debug: verify notes length is not truncated from API
        if (log && typeof log.notes === 'string') {
            try { console.debug('[AdminLogs] notes length:', log.notes.length, 'sample:', log.notes.slice(0, 80)); } catch (_) {}
        }
        const notesCell = log.notes
            ? `<div style="white-space: pre-wrap !important; overflow-wrap: anywhere !important; word-break: break-word !important;">${escapeHTML(log.notes)}</div>`
            : '<em>No notes</em>';
        const idVal = log.id ?? log.pk;

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
                <td style="padding: 8px; border: 1px solid #ddd; width: 65%; white-space: normal !important; overflow: visible !important; text-overflow: clip !important;">${notesCell}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right; white-space: nowrap;">
                    ${idVal !== undefined ? `<button class="btn btn-sm btn-outline-danger" onclick="deleteAdminLog(${idVal})">Delete</button>` : ''}
                </td>
            </tr>
        `;
    }).join('');

    const paginationHtml = `
        <div class="pagination-controls" style="margin-top: 10px; text-align: right;">
            <button id="prev-btn" class="btn btn-secondary">Previous</button>
            <button id="next-btn" class="btn btn-secondary">Next</button>
        </div>
    `;

    const tableHtml = `
        <div style="overflow-x: auto; max-height: 40vh; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ccc;">User</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ccc;">Action</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ccc;">Target</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ccc;">Timestamp</th>
                        <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ccc;">Notes</th>
                        <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ccc;">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        </div>
        ${paginationHtml}
    `;

    container.innerHTML = tableHtml;
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

// ==============================
// Clear-All-Data utilities (students, rounds, projects, groups)
// Note: Not wired to any button. Call window.clearAllData()
// ==============================

// Endpoints with fallbacks if not present in window.ENDPOINTS
const API = {
    students: (window.ENDPOINTS && window.ENDPOINTS.students) || '/api/admin/students/',
    rounds: (window.ENDPOINTS && window.ENDPOINTS.rounds) || '/api/admin/rounds/',
    projects: (window.ENDPOINTS && window.ENDPOINTS.projects) || '/api/admin/projects/',
    finalGroups: (window.ENDPOINTS && window.ENDPOINTS.finalGroups) || '/api/admin/final_groups/',
    suggestedGroups: (window.ENDPOINTS && window.ENDPOINTS.suggestedGroups) || '/api/admin/suggested_groups/',
};

async function fetchJson(url) {
    const resp = await fetch(url, { credentials: 'same-origin' });
    if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        throw new Error(`GET ${url} failed: ${resp.status} ${text}`);
    }
    return resp.json();
}

async function deleteById(urlBase, id) {
    const resp = await fetch(`${urlBase}${id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': (typeof getCSRFToken === 'function' ? getCSRFToken() : (function(){
            // Fallback CSRF token reader if not injected by template yet
            const value = `; ${document.cookie}`;
            const parts = value.split(`; csrftoken=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return '';
        })()) },
        credentials: 'same-origin',
    });
    if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        throw new Error(`DELETE ${urlBase}${id}/ failed: ${resp.status} ${text}`);
    }
}

// Collect all ids across paginated responses for a DRF list endpoint
async function getAllIds(urlBase, pageSize = 200) {
    const ids = [];
    let url = `${urlBase}?page_size=${pageSize}`;
    while (url) {
        const page = await fetchJson(url);
        if (Array.isArray(page.results)) {
            for (const item of page.results) {
                ids.push(
                    item.id ??
                    item.finalgroup_id ??
                    item.suggestedgroup_id ??
                    item.project_id ??
                    item.round_id ??
                    item.student_id ??
                    item.pk
                );
            }
        }
        url = page.next;
    }
    return ids.filter((x) => x !== undefined && x !== null);
}

// Delete with limited concurrency
async function deleteManyByIds(urlBase, ids, concurrency = 5, label = 'items') {
    let inFlight = 0;
    let i = 0;
    let errors = 0;

    return new Promise((resolve) => {
        const next = () => {
            if (i >= ids.length && inFlight === 0) {
                console.log(`[ClearData] Finished deleting ${ids.length} ${label}, errors=${errors}`);
                resolve({ total: ids.length, errors });
                return;
            }
            while (inFlight < concurrency && i < ids.length) {
                const id = ids[i++];
                inFlight++;
                deleteById(urlBase, id)
                    .catch((e) => {
                        console.error(`[ClearData] Failed to delete ${label} id=${id}:`, e);
                        errors++;
                    })
                    .finally(() => {
                        inFlight--;
                        next();
                    });
            }
        };
        next();
    });
}

function setBusy(isBusy) {
    const loader = document.getElementById('page-loader');
    if (loader) loader.classList.toggle('d-none', !isBusy);
    const btn = document.getElementById('confirmClearDataBtn');
    if (btn) btn.disabled = isBusy;
}

async function clearAllData() {
    setBusy(true);
    console.log('[ClearData] Starting');
    try {
        // 1) Final groups first
        const finalGroupIds = await getAllIds(API.finalGroups);
        console.log(`[ClearData] Deleting ${finalGroupIds.length} final groups`);
        await deleteManyByIds(API.finalGroups, finalGroupIds, 6, 'final groups');

        // 2) Suggested groups
        const sgIds = await getAllIds(API.suggestedGroups);
        console.log(`[ClearData] Deleting ${sgIds.length} suggested groups`);
        await deleteManyByIds(API.suggestedGroups, sgIds, 6, 'suggested groups');

        // 3) Rounds
        const roundIds = await getAllIds(API.rounds);
        console.log(`[ClearData] Deleting ${roundIds.length} rounds`);
        await deleteManyByIds(API.rounds, roundIds, 6, 'rounds');

        // 4) Projects
        const projectIds = await getAllIds(API.projects);
        console.log(`[ClearData] Deleting ${projectIds.length} projects`);
        await deleteManyByIds(API.projects, projectIds, 4, 'projects');

        // 5) Students
        const studentIds = await getAllIds(API.students);
        console.log(`[ClearData] Deleting ${studentIds.length} students`);
        await deleteManyByIds(API.students, studentIds, 6, 'students');

        console.log('[ClearData] Completed successfully');
        // Optional: refresh views
        if (window.loadAdminLogs) {
            window.loadAdminLogs(window.ENDPOINTS.adminLogs);
        }
    } catch (e) {
        console.error('[ClearData] Failed:', e);
        alert('Clear Data failed: ' + e.message);
    } finally {
        setBusy(false);
    }
}

// Expose to global for wiring from HTML if/when desired
window.clearAllData = clearAllData;

// Per-row delete for AdminLog entries
async function deleteAdminLog(id) {
    if (id === undefined || id === null) return;
    try {
        const resp = await fetch(`${window.ENDPOINTS.adminLogs}${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': (typeof getCSRFToken === 'function' ? getCSRFToken() : (function(){
                    const value = `; ${document.cookie}`;
                    const parts = value.split(`; csrftoken=`);
                    if (parts.length === 2) return parts.pop().split(';').shift();
                    return '';
                })())
            },
            credentials: 'same-origin'
        });
        if (!resp.ok) throw new Error(`Failed to delete log ${id}`);
        // Refresh current page without nuking the cache for others
        if (currentLogsUrl) {
            // Invalidate just this page
            delete pageCache[currentLogsUrl];
            await loadAdminLogs(currentLogsUrl);
        } else {
            await loadAdminLogs(window.ENDPOINTS.adminLogs);
        }
    } catch (e) {
        console.error('Delete log failed:', e);
        alert('Failed to delete log: ' + e.message);
    }
}

// Expose for debugging if needed
window.deleteAdminLog = deleteAdminLog;