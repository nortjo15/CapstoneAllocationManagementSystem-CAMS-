document.addEventListener('DOMContentLoaded', function() {
    loadAdminLogs();
});

function loadAdminLogs() {
    fetch('/api/admin-logs/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Admin Logs:', data);
            displayAdminLogs(data);
        })
        .catch(error => {
            console.error('Error fetching admin logs:', error);
            const container = document.getElementById('admin-logs-container');
            if (container) {
                container.innerHTML = '<p style="color: red;">Error loading admin logs: ' + error.message + '</p>';
            }
        });
}

function displayAdminLogs(logs) {
    const container = document.getElementById('admin-logs-container');
    
    if (!container) {
        console.error('Container admin-logs-container not found!');
        return;
    }
    
    if (!logs || logs.length === 0) {
        container.innerHTML = '<p style="color: #6c757d; font-style: italic;">No admin logs found.</p>';
        return;
    }

    let tableHTML = `
        <div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead style="position: sticky; top: 0; background-color: #e9ecef;">
                    <tr>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">User</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Action</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Notes</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Timestamp</th>
                    </tr>
                </thead>
                <tbody>
    `;

    logs.forEach(log => {
        tableHTML += `
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">${log.user || 'Unknown'}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">${log.action || 'N/A'}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">${log.notes || 'No notes'}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">${formatDate(log.timestamp)}</td>
            </tr>
        `;
    });

    tableHTML += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = tableHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}