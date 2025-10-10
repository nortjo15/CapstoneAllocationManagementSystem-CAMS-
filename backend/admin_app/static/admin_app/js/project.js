// static/admin_app/js/project.js
document.addEventListener('DOMContentLoaded', () => {
  const wrap = document.getElementById('project-container');
  const apiUrl = window.ENDPOINTS?.projects || null;

  // ---------- helpers ----------
  function getCsrfToken() {
    const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : (document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');
  }
  function joinDetailUrl(listUrl, id) {
    // "/api/projects/" + "<id>/" → "/api/projects/123/"
    const base = listUrl.endsWith('/') ? listUrl : listUrl + '/';
    return base + String(id).replace(/^\/|\/$/g, '') + '/';
  }

  // ---------- list loader ----------
  async function getProjectData() {
    if (!wrap || !apiUrl) return;
    wrap.innerHTML = '<div class="text-secondary">Loading…</div>';

    try {
      const rsp = await fetch(apiUrl, {
        headers: { 'Accept': 'application/json' },
        credentials: 'same-origin',
        cache: 'no-store',
      });

      if (!rsp.ok) {
        const txt = await rsp.text();
        wrap.innerHTML = `<div class="text-danger">GET ${rsp.status}</div>`;
        console.error('List error', rsp.status, txt);
        return;
      }

      const data = await rsp.json();
      const items = Array.isArray(data) ? data : (data.results || []);
      wrap.innerHTML = '';

      if (!items.length) {
        wrap.innerHTML = '<div class="text-secondary">No Projects Found</div>';
        return;
      }

      items.forEach(p => wrap.appendChild(renderCard(p)));
    } catch (e) {
      wrap.innerHTML = '<div class="text-danger">Network error</div>';
      console.error(e);
    }
  }

  // ---------- card renderer ----------
  function renderCard(p) {
    const el = document.createElement('div');
    el.className = 'project-card';
    el.innerHTML = `
      <h3 class="h5 mb-1">${p.title ?? 'Untitled project'}</h3>
      <div class="meta">Host: ${p.host_name ?? 'N/A'} · Email: ${p.host_email ?? 'N/A'}</div>
      <p class="mb-3">${p.description ?? ''}</p>
      <div class="actions">
        <div class="d-flex gap-2">
          <button
            type="button"
            class="btn btn-outline-primary btn-sm js-edit"
            data-bs-toggle="modal"
            data-bs-target="#editProjectModal"
            data-payload='${JSON.stringify(p)}'
          >Edit</button>

          <button
            type="button"
            class="btn btn-outline-danger btn-sm js-delete"
            data-id="${p.project_id ?? p.id ?? ''}"
          >Delete</button>
        </div>
        <span class="text-secondary ms-auto">Capacity: ${p.capacity ?? '—'}</span>
      </div>
    `;
    return el;
  }

  // ---------- add-project submit ----------
  const addForm = document.getElementById('add-project-form');
  if (addForm && apiUrl) {
    addForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const csrf = addForm.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
      const data = Object.fromEntries(new FormData(addForm).entries());

      try {
        const rsp = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf,
          },
          credentials: 'same-origin',
          cache: 'no-store',
          body: JSON.stringify(data),
        });

        const bodyText = await rsp.clone().text();
        console.log('Create:', rsp.status, bodyText);

        if (!rsp.ok) {
          alert(`Create failed (${rsp.status})\n${bodyText}`);
          return;
        }

        await getProjectData();

        const modalEl = document.getElementById('pModal');
        if (modalEl && window.bootstrap?.Modal) {
          window.bootstrap.Modal.getOrCreateInstance(modalEl).hide();
        }
        addForm.reset();
      } catch (err) {
        console.error(err);
        alert('Network error during create');
      }
    });
  }

  // ---------- edit prefill + delete delegate ----------
  document.addEventListener('click', async (ev) => {
    // prefill edit
    const editBtn = ev.target.closest('.js-edit');
    if (editBtn) {
      const payload = JSON.parse(editBtn.getAttribute('data-payload') || '{}');
      const modalEl = document.getElementById('editProjectModal');
      if (modalEl) {
        modalEl.querySelector('#edit-project-id')?.setAttribute('value', payload.id ?? payload.project_id ?? '');
        modalEl.querySelector('#edit-project-title')?.setAttribute('value', payload.title ?? '');
        const desc = modalEl.querySelector('#edit-project-description');
        if (desc) desc.value = payload.description ?? '';
        modalEl.querySelector('#edit-project-capacity')?.setAttribute('value', payload.capacity ?? '');
        modalEl.querySelector('#edit-host-name')?.setAttribute('value', payload.host_name ?? '');
        modalEl.querySelector('#edit-host-email')?.setAttribute('value', payload.host_email ?? '');
        modalEl.querySelector('#edit-host-phone')?.setAttribute('value', payload.host_phone ?? '');
      }
      return;
    }

    // delete
    const delBtn = ev.target.closest('.js-delete');
    if (delBtn) {
      ev.preventDefault();
      const id = delBtn.getAttribute('data-id');
      if (!id) return;

      if (!confirm('Delete this project? This cannot be undone.')) return;

      const detailUrl = joinDetailUrl(apiUrl, id);

      try {
        const rsp = await fetch(detailUrl, {
          method: 'DELETE',
          headers: {
            'Accept': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          credentials: 'same-origin',
          cache: 'no-store',
        });

        if (rsp.status === 204 || rsp.status === 200) {
          const card = delBtn.closest('.project-card') || delBtn.closest('#project-container > *');
          if (card) card.remove();
          return;
        }

        const txt = await rsp.text();
        alert(`Delete failed (${rsp.status})\n${txt}`);
      } catch (e) {
        console.error(e);
        alert('Network error during delete');
      }
    }
  });

  // ---------- initial load ----------
  getProjectData();
});
