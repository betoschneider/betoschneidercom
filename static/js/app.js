async function fetchProjects() {
  const res = await fetch('/projects');
  if (!res.ok) return [];
  return await res.json();
}

function renderPublic(projects) {
  const root = document.getElementById('projects');
  if (!projects || projects.length === 0) {
    root.innerHTML = '<p>Nenhum projeto encontrado.</p>';
    return;
  }
  root.innerHTML = projects.map(p => `
    <a href="${p.url}" target="_blank">
      <strong>${escapeHtml(p.title)}</strong>
      <p class="desc">${escapeHtml(p.description || '')}</p>
    </a>
  `).join('');
}

function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]); }

// --- Admin logic ---
async function initAdmin(){
  const tokenInput = document.getElementById('token');
  const createBtn = document.getElementById('createBtn');
  const updateBtn = document.getElementById('updateBtn');
  const clearBtn = document.getElementById('clearBtn');

  createBtn.addEventListener('click', async ()=>{
    const token = tokenInput.value.trim();
    await createProject(token);
  });
  updateBtn.addEventListener('click', async ()=>{
    const token = tokenInput.value.trim();
    await updateProject(token);
  });
  clearBtn.addEventListener('click', clearForm);

  await loadProjectsForAdmin();
}

async function loadProjectsForAdmin(){
  const projects = await fetchProjects();
  const root = document.getElementById('projectsList');
  if (!projects || projects.length === 0){ root.innerHTML = '<p>Nenhum projeto.</p>'; return; }
  root.innerHTML = '';
  projects.forEach(p=>{
    const div = document.createElement('div'); div.className='project';
    div.innerHTML = `
      <h3>${escapeHtml(p.title)}</h3>
      <p>${escapeHtml(p.description||'')}</p>
      <p><a href="${p.url}" target="_blank">${p.url}</a></p>
      <div>
        <button data-id="${p.id}" class="edit">Editar</button>
        <button data-id="${p.id}" class="delete">Apagar</button>
      </div>
    `;
    root.appendChild(div);
  });

  root.querySelectorAll('.edit').forEach(btn=>btn.addEventListener('click', e=>{
    const id = e.target.dataset.id; fillFormForEdit(id);
  }));
  root.querySelectorAll('.delete').forEach(btn=>btn.addEventListener('click', async e=>{
    const id = e.target.dataset.id; const token = document.getElementById('token').value.trim();
    if (!confirm('Confirmar exclusão?')) return;
    await deleteProjectById(id, token);
    await loadProjectsForAdmin();
  }));
}

async function createProject(token){
  const title = document.getElementById('title').value.trim();
  const description = document.getElementById('description').value.trim();
  const url = document.getElementById('url').value.trim();
  if (!title || !url) { alert('Título e URL são obrigatórios'); return; }
  const res = await fetch('/projects', {method:'POST', headers:{'Content-Type':'application/json','X-Admin-Token':token}, body:JSON.stringify({title,description,url})});
  if (!res.ok){ alert('Erro: ' + res.status); return; }
  clearForm();
  await loadProjectsForAdmin();
}

let editingId = null;
async function fillFormForEdit(id){
  const projects = await fetchProjects();
  const p = projects.find(x=>String(x.id)===String(id));
  if (!p) return;
  editingId = id;
  document.getElementById('title').value = p.title;
  document.getElementById('description').value = p.description || '';
  document.getElementById('url').value = p.url;
  document.getElementById('updateBtn').disabled = false;
}

async function updateProject(token){
  if (!editingId) { alert('Nada selecionado para editar'); return; }
  const title = document.getElementById('title').value.trim();
  const description = document.getElementById('description').value.trim();
  const url = document.getElementById('url').value.trim();
  const res = await fetch(`/projects/${editingId}`, {method:'PUT', headers:{'Content-Type':'application/json','X-Admin-Token':token}, body:JSON.stringify({title,description,url})});
  if (!res.ok){ alert('Erro: ' + res.status); return; }
  editingId = null; document.getElementById('updateBtn').disabled = true; clearForm(); await loadProjectsForAdmin();
}

async function deleteProjectById(id, token){
  const res = await fetch(`/projects/${id}`, {method:'DELETE', headers:{'X-Admin-Token':token}});
  if (!res.ok){ alert('Erro ao apagar: ' + res.status); }
}

function clearForm(){
  editingId = null;
  document.getElementById('title').value='';
  document.getElementById('description').value='';
  document.getElementById('url').value='';
  document.getElementById('updateBtn').disabled = true;
}
