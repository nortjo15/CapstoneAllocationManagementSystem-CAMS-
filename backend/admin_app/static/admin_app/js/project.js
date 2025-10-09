document.addEventListener('DOMContentLoaded', () => {
  const wrap = document.getElementById('project-container');
  const apiUrl = window.ENDPOINTS?.projects;

  if (!wrap || !apiUrl) return;

  // Render one card
  const renderCard = (p) => {
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
            data-id="${p.id}"
          >Delete</button>
        </div>
        <span class="text-secondary">Capacity: ${p.capacity ?? '—'}</span>
      </div>
    `;
    return el;
  };

  // Fetch and render
  (async () => {
    wrap.innerHTML = '<div class="text-secondary">Loading…</div>';
    try {
      const rsp = await fetch(apiUrl, { headers: { 'Accept': 'application/json' } });
      const data = await rsp.json();
      wrap.innerHTML = '';
      if (!Array.isArray(data) || data.length === 0) {
        wrap.innerHTML = '<div class="text-secondary">No Projects Found</div>';
        return;
      }
      data.forEach(p => wrap.appendChild(renderCard(p)));
      decorateCapacityBadges();
    } catch (e) {
      wrap.innerHTML = '<div class="text-danger">Failed to load projects.</div>';
      // Optional: console.error(e);
    }
  })();

  // Delegate clicks
  document.addEventListener('click', (ev) => {
    const editBtn = ev.target.closest('.js-edit');
    if (editBtn) {
      // Fill the edit modal fields before it opens
      const payload = JSON.parse(editBtn.getAttribute('data-payload') || '{}');
      fillEditModal(payload);
    }

    const delBtn = ev.target.closest('.js-delete');
    if (delBtn) {
      const id = delBtn.getAttribute('data-id');
      if (!id) return;
      // TODO: implement delete call
      // fetch(`${apiUrl}/${id}`, { method: 'DELETE' }).then(...);
    }
  });

  // Populate edit modal inputs
  function fillEditModal(p) {
    const modalEl = document.getElementById('editProjectModal');
    if (!modalEl) return;

    modalEl.querySelector('#edit-project-id')?.setAttribute('value', p.id ?? '');
    modalEl.querySelector('#edit-project-title')?.setAttribute('value', p.title ?? '');
    modalEl.querySelector('#edit-project-description') && (modalEl.querySelector('#edit-project-description').value = p.description ?? '');
    modalEl.querySelector('#edit-capacity')?.setAttribute('value', p.capacity ?? '');
    modalEl.querySelector('#edit-hostname')?.setAttribute('value', p.host_name ?? '');
    modalEl.querySelector('#edit-host-email')?.setAttribute('value', p.host_email ?? '');
    modalEl.querySelector('#edit-host-phone')?.setAttribute('value', p.host_phone ?? '');
  }

  // Optional: synthesize "Capacity: X" into a right-aligned badge
  function decorateCapacityBadges() {
    [...wrap.children].forEach(card => {
      const bar = card.querySelector('.actions');
      if (!bar) return;
      const label = bar.querySelector('span.text-secondary');
      if (label) bar.setAttribute('data-capacity', label.textContent.trim());
    });
  }
});
