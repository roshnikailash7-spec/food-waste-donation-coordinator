/**
 * Food Waste Reduction & Donation Coordinator (College DSA Project)
 * Frontend Controller & Canvas Route Visualizer
 * All core algorithmic logic resides in custom Python DSA modules (dsa/).
 */

document.addEventListener('DOMContentLoaded', () => {
  // Global State
  const state = {
    dashboard: null,
    foodItems: [],
    urgentHeapItems: [],
    queueItems: [],
    donors: [],
    ngos: [],
    history: [],
    graph: { nodes: [], edges: [] },
    activeRoutePath: [],
    activeRouteDist: null,
    canvasHoverNode: null,
  };

  // Canvas context & scaling
  const canvas = document.getElementById('cityMapCanvas');
  const ctx = canvas ? canvas.getContext('2d') : null;
  const tooltip = document.getElementById('canvasTooltip');

  // Initialize
  initApp();

  async function initApp() {
    setupEventListeners();
    setupCanvasInteractions();
    await refreshAllData();
  }

  async function refreshAllData() {
    await Promise.all([
      loadDashboard(),
      loadFood(),
      loadQueue(),
      loadPartners(),
      loadHistory(),
      loadGraph()
    ]);
  }

  // =========================================================================
  // API Fetchers
  // =========================================================================

  async function loadDashboard() {
    try {
      const res = await fetch('/api/dashboard');
      const data = await res.json();
      state.dashboard = data;

      // Update KPI numbers
      document.getElementById('kpiFoodSaved').textContent = data.stats.total_food_saved_kg;
      document.getElementById('kpiUrgentItems').textContent = data.stats.urgent_items_count;
      document.getElementById('kpiPendingPickups').textContent = data.stats.pending_pickups_count;
      document.getElementById('kpiDonors').textContent = data.stats.active_donors_count;
      document.getElementById('kpiNgos').textContent = data.stats.active_ngos_count;

      // Update Undo Button (LIFO Stack)
      const undoBtn = document.getElementById('undoBtn');
      const undoBadge = document.getElementById('undoBadge');
      if (data.can_undo) {
        undoBtn.removeAttribute('disabled');
        undoBadge.style.display = 'inline-flex';
        undoBadge.textContent = '1+';
      } else {
        undoBtn.setAttribute('disabled', 'true');
        undoBadge.style.display = 'none';
      }

      // Update Heap Spotlight (Root of Min-Heap)
      renderHeapSpotlight(data.most_urgent_food);

      // Update Queue Spotlight (Front of FIFO Queue)
      renderQueueSpotlight(data.next_pickup);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
  }

  function renderHeapSpotlight(item) {
    const container = document.getElementById('heapRootContent');
    if (!item) {
      container.innerHTML = `
        <div class="spotlight-item-name" style="color:var(--text-light); font-size:1rem;">No urgent food in heap</div>
        <p class="section-desc">All current surplus batches have been matched or delivered.</p>
      `;
      return;
    }

    const expBadgeClass = getExpiryClass(item.expiry_hours);
    container.innerHTML = `
      <div class="spotlight-item-name">${escapeHtml(item.name)}</div>
      <div class="spotlight-meta-line">
        <span class="badge-expiry ${expBadgeClass}">Expires in ${item.expiry_hours}h</span>
        <span>&bull;</span>
        <strong>${item.quantity} ${item.unit || 'kg'}</strong>
        <span>&bull;</span>
        <span>Donor: ${escapeHtml(item.donor_name || item.donor_id)}</span>
      </div>
      <p class="section-desc" style="font-size:0.8rem; margin-top:0.3rem;">
        Currently at the root of the Min-Heap. Ready for highest priority route dispatch.
      </p>
    `;
  }

  function renderQueueSpotlight(pickup) {
    const container = document.getElementById('queueFrontContent');
    if (!pickup) {
      container.innerHTML = `
        <div class="spotlight-item-name" style="color:var(--text-light); font-size:1rem;">Pickup queue is empty</div>
        <p class="section-desc">Trigger Auto-Match to schedule the next delivery mission.</p>
      `;
      return;
    }

    container.innerHTML = `
      <div class="spotlight-item-name">#${pickup.id}: ${escapeHtml(pickup.food_name)}</div>
      <div class="spotlight-meta-line">
        <span class="badge-status available">Ready for Dispatch</span>
        <span>&bull;</span>
        <strong>${pickup.quantity} ${pickup.unit || 'kg'}</strong>
        <span>&bull;</span>
        <span>${escapeHtml(pickup.ngo_name)} (${pickup.distance_km} km)</span>
      </div>
      <p class="section-desc" style="font-size:0.8rem; margin-top:0.3rem;">
        Next out of FIFO Queue. Shortest path via: [${(pickup.route_path || []).join(' &rarr; ')}].
      </p>
    `;
  }

  async function loadFood() {
    try {
      const activePill = document.querySelector('#foodStatusFilter .tab-pill.active');
      const status = activePill ? activePill.dataset.status : 'ALL';
      const sortSelect = document.getElementById('foodSortBy').value;

      let sortBy = 'expiry';
      let order = 'asc';
      if (sortSelect === 'expiry_desc') { sortBy = 'expiry'; order = 'desc'; }
      else if (sortSelect === 'qty_desc') { sortBy = 'quantity'; order = 'desc'; }
      else if (sortSelect === 'qty_asc') { sortBy = 'quantity'; order = 'asc'; }

      const res = await fetch(`/api/food?status=${status}&sort_by=${sortBy}&order=${order}`);
      const data = await res.json();
      state.foodItems = data.items || [];
      renderFoodGrid(state.foodItems);
    } catch (err) {
      console.error('Failed to load food items:', err);
    }
  }

  function renderFoodGrid(items) {
    const container = document.getElementById('foodGrid');
    if (!items || items.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1; padding:2.5rem; text-align:center;">
          <p>No food batches match this filter.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = items.map(food => {
      const expClass = getExpiryClass(food.expiry_hours);
      const statusClass = (food.status || 'AVAILABLE').toLowerCase();
      return `
        <div class="food-card" data-food-id="${food.id}">
          <div>
            <div class="food-card-top">
              <span class="badge-status ${statusClass}">${food.status}</span>
              <span class="badge-expiry ${expClass}">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                ${food.expiry_hours}h left
              </span>
            </div>
            <h4 class="food-card-title" style="margin-top:0.6rem;">${escapeHtml(food.name)}</h4>
            <div class="food-card-meta" style="margin-top:0.5rem;">
              <span><strong>Donor:</strong> ${escapeHtml(food.donor_name || food.donor_id)}</span>
              <span><strong>Category:</strong> ${escapeHtml(food.category || 'Food')}</span>
              <span><strong>Location:</strong> ${escapeHtml(food.donor_location || 'Central')}</span>
            </div>
          </div>
          <div class="food-card-footer">
            <span class="food-qty-pill">${food.quantity} ${food.unit || 'kg'}</span>
            <span style="font-size:0.75rem; color:var(--text-light); font-family:var(--font-mono);">${food.id}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  async function loadQueue() {
    try {
      const res = await fetch('/api/queue');
      const data = await res.json();
      state.queueItems = data.queue || [];
      renderQueue(state.queueItems);
    } catch (err) {
      console.error('Failed to load queue:', err);
    }
  }

  function renderQueue(queue) {
    const container = document.getElementById('pickupQueueList');
    if (!queue || queue.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="padding:2rem; width:100%; text-align:center;">
          <p>No pending pickup missions currently scheduled in the FIFO Queue.</p>
          <span class="hint-text">Click 'Run Auto-Match' above to match the most urgent food item to an NGO.</span>
        </div>
      `;
      return;
    }

    container.innerHTML = queue.map((pk, idx) => {
      const isFront = (idx === 0);
      return `
        <div class="queue-card" data-pickup-id="${pk.id}" onclick="window.highlightPickupRoute('${pk.id}')" style="cursor:pointer;">
          <span class="queue-card-badge">${isFront ? 'FRONT &bull; NEXT' : `#${idx + 1} IN QUEUE`}</span>
          <div>
            <span class="badge-status available">DISPATCH</span>
            <h4 style="font-family:var(--font-heading); font-size:1.1rem; margin-top:0.35rem; font-weight:700;">
              ${escapeHtml(pk.food_name)}
            </h4>
            <div style="font-size:0.83rem; color:var(--text-muted); margin-top:0.4rem; display:flex; flex-direction:column; gap:0.25rem;">
              <span><strong>Qty:</strong> ${pk.quantity} ${pk.unit || 'kg'} (${pk.expiry_hours}h exp)</span>
              <span><strong>From:</strong> ${escapeHtml(pk.donor_name)}</span>
              <span><strong>To:</strong> ${escapeHtml(pk.ngo_name)}</span>
              <span><strong>Route:</strong> ${(pk.route_path || []).join(' &rarr; ')}</span>
            </div>
          </div>
          <div style="display:flex; align-items:center; justify-content:space-between; margin-top:auto; padding-top:0.6rem; border-top:1px dashed var(--border-light); font-size:0.8rem;">
            <strong style="color:var(--primary); font-size:0.95rem;">${pk.distance_km} km</strong>
            <span style="font-size:0.75rem; color:var(--text-light);">${pk.id}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // Window helper to highlight route on map
  window.highlightPickupRoute = function(pickupId) {
    const pickup = state.queueItems.find(p => p.id === pickupId);
    if (!pickup) return;
    state.activeRoutePath = pickup.route_path || [];
    state.activeRouteDist = pickup.distance_km;
    drawMap();
    document.getElementById('routeSummaryText').textContent = 
      `Inspecting Pickup #${pickup.id}: Route [${(pickup.route_path || []).join(' -> ')}] &bull; Distance: ${pickup.distance_km} km`;
  };

  async function loadPartners() {
    try {
      const [donorsRes, ngosRes] = await Promise.all([
        fetch('/api/donors'),
        fetch('/api/ngos')
      ]);
      const donorsData = await donorsRes.json();
      const ngosData = await ngosRes.json();

      state.donors = donorsData.donors || [];
      state.ngos = ngosData.ngos || [];

      document.getElementById('dirDonorCount').textContent = state.donors.length;
      document.getElementById('dirNgoCount').textContent = state.ngos.length;

      renderDonors(state.donors);
      renderNgos(state.ngos);
      populateDonorSelect(state.donors);
    } catch (err) {
      console.error('Failed to load partners:', err);
    }
  }

  function renderDonors(donors) {
    const container = document.getElementById('donorsGrid');
    container.innerHTML = donors.map(d => `
      <div class="dir-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <span class="badge-status available">Donor</span>
          <span style="font-family:var(--font-mono); font-size:0.72rem; color:var(--text-light);">${d.id}</span>
        </div>
        <h4 style="font-family:var(--font-heading); font-size:1.15rem; font-weight:700;">${escapeHtml(d.name)}</h4>
        <div style="font-size:0.83rem; color:var(--text-muted); display:flex; flex-direction:column; gap:0.25rem;">
          <span><strong>Location:</strong> ${escapeHtml(d.location)}</span>
          <span><strong>Type:</strong> ${escapeHtml(d.type || 'Donor')}</span>
          <span><strong>Contact:</strong> ${escapeHtml(d.contact || 'N/A')}</span>
        </div>
      </div>
    `).join('');
  }

  function renderNgos(ngos) {
    const container = document.getElementById('ngosGrid');
    container.innerHTML = ngos.map(n => {
      const cap = parseFloat(n.capacity) || 100;
      const rem = parseFloat(n.remaining_capacity !== undefined ? n.remaining_capacity : n.capacity);
      const usedPct = Math.min(100, Math.max(0, ((cap - rem) / cap) * 100));

      return `
        <div class="dir-card">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <span class="badge-status available" style="background-color:#E3F2FD; color:#1976D2;">Shelter / NGO</span>
            <span style="font-family:var(--font-mono); font-size:0.72rem; color:var(--text-light);">${n.id}</span>
          </div>
          <h4 style="font-family:var(--font-heading); font-size:1.15rem; font-weight:700;">${escapeHtml(n.name)}</h4>
          <div style="font-size:0.83rem; color:var(--text-muted); display:flex; flex-direction:column; gap:0.25rem;">
            <span><strong>Location:</strong> ${escapeHtml(n.location)}</span>
            <span><strong>Serves:</strong> ${escapeHtml(n.serves || 'Community')}</span>
            <span><strong>Contact:</strong> ${escapeHtml(n.contact || 'N/A')}</span>
            <div style="margin-top:0.4rem;">
              <div style="display:flex; justify-content:space-between; font-size:0.78rem;">
                <span>Capacity:</span>
                <strong>${rem.toFixed(1)} / ${cap} kg available</strong>
              </div>
              <div class="capacity-progress-bar">
                <div class="capacity-fill" style="width:${usedPct}%;"></div>
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  function populateDonorSelect(donors) {
    const sel = document.getElementById('foodDonorSelect');
    if (!sel) return;
    sel.innerHTML = donors.map(d => `
      <option value="${d.id}">${escapeHtml(d.name)} (${escapeHtml(d.location)})</option>
    `).join('');
  }

  async function loadHistory() {
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      state.history = data.history || [];
      document.getElementById('historyRecordCount').textContent = data.total_records || state.history.length;
      renderHistory(state.history);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }

  function renderHistory(logs) {
    const container = document.getElementById('historyTimeline');
    if (!logs || logs.length === 0) {
      container.innerHTML = `<p style="color:var(--text-muted); font-size:0.85rem;">No historical events recorded yet.</p>`;
      return;
    }

    container.innerHTML = logs.map(entry => `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content">
          <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
            <span class="timeline-title">${escapeHtml(entry.title || entry.action_type)}</span>
            <span class="timeline-time">${escapeHtml(entry.timestamp)}</span>
          </div>
          <p class="timeline-desc">${escapeHtml(entry.description)}</p>
        </div>
      </div>
    `).join('');
  }

  async function loadGraph() {
    try {
      const res = await fetch('/api/graph');
      const data = await res.json();
      state.graph = data;
      drawMap();
    } catch (err) {
      console.error('Failed to load road graph:', err);
    }
  }

  // =========================================================================
  // Canvas Map Visualizer (Graph + Dijkstra)
  // =========================================================================

  function drawMap() {
    if (!canvas || !ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear
    ctx.clearRect(0, 0, width, height);

    const nodes = state.graph.nodes || [];
    const edges = state.graph.edges || [];

    // Helper: Node coordinates
    const nodeMap = {};
    nodes.forEach(n => {
      nodeMap[n.id] = {
        ...n,
        px: (n.x / 100) * width,
        py: (n.y / 100) * height
      };
    });

    // 1. Draw Inactive / Background Edges
    edges.forEach(edge => {
      const u = nodeMap[edge.source];
      const v = nodeMap[edge.target];
      if (!u || !v) return;

      const isRouteEdge = isEdgeInPath(edge.source, edge.target, state.activeRoutePath);
      if (isRouteEdge) return; // Draw later with glow

      ctx.beginPath();
      ctx.moveTo(u.px, u.py);
      ctx.lineTo(v.px, v.py);
      ctx.strokeStyle = '#D5DFD6';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      // Weight label pill
      drawEdgeWeight((u.px + v.px) / 2, (u.py + v.py) / 2, `${edge.weight}km`);
    });

    // 2. Draw Active Route Edges (Dijkstra Highlight)
    if (state.activeRoutePath && state.activeRoutePath.length > 1) {
      for (let i = 0; i < state.activeRoutePath.length - 1; i++) {
        const u = nodeMap[state.activeRoutePath[i]];
        const v = nodeMap[state.activeRoutePath[i + 1]];
        if (!u || !v) continue;

        // Outer glow
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(u.px, u.py);
        ctx.lineTo(v.px, v.py);
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.4)';
        ctx.lineWidth = 10;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Core bright line
        ctx.beginPath();
        ctx.moveTo(u.px, u.py);
        ctx.lineTo(v.px, v.py);
        ctx.strokeStyle = '#DD7816';
        ctx.lineWidth = 4.5;
        ctx.setLineDash([8, 4]);
        ctx.lineCap = 'round';
        ctx.stroke();
        ctx.restore();
      }
    }

    // 3. Draw Nodes
    nodes.forEach(n => {
      const pt = nodeMap[n.id];
      if (!pt) return;

      const inRoute = (state.activeRoutePath || []).includes(n.id);
      const isStart = state.activeRoutePath && state.activeRoutePath[0] === n.id;
      const isEnd = state.activeRoutePath && state.activeRoutePath[state.activeRoutePath.length - 1] === n.id;

      let radius = 10;
      let fill = '#94A3B8'; // transit default
      if (n.type === 'donor') fill = '#2D6A4F';
      if (n.type === 'ngo') fill = '#1976D2';

      if (inRoute) {
        radius = 13;
        // Golden highlight ring
        ctx.beginPath();
        ctx.arc(pt.px, pt.py, radius + 4, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(245, 158, 11, 0.35)';
        ctx.fill();
      }

      // Outer white ring
      ctx.beginPath();
      ctx.arc(pt.px, pt.py, radius, 0, Math.PI * 2);
      ctx.fillStyle = fill;
      ctx.fill();
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = '#FFFFFF';
      ctx.stroke();

      // Node label
      ctx.font = '600 11px Plus Jakarta Sans, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillStyle = '#1C2E26';

      let labelY = pt.py - (radius + 6);
      if (pt.py < 30) labelY = pt.py + (radius + 14);

      // Label background card
      const textWidth = ctx.measureText(n.label || n.id).width;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.fillRect(pt.px - textWidth / 2 - 4, labelY - 10, textWidth + 8, 14);

      ctx.fillStyle = inRoute ? '#DD7816' : '#1C2E26';
      ctx.fillText(n.label || n.id, pt.px, labelY);

      if (isStart) {
        drawEndpointTag(pt.px, pt.py + radius + 14, 'START (Donor)', '#2D6A4F');
      } else if (isEnd) {
        drawEndpointTag(pt.px, pt.py + radius + 14, 'END (Shelter)', '#1976D2');
      }
    });
  }

  function isEdgeInPath(u, v, path) {
    if (!path || path.length < 2) return false;
    for (let i = 0; i < path.length - 1; i++) {
      if ((path[i] === u && path[i + 1] === v) || (path[i] === v && path[i + 1] === u)) {
        return true;
      }
    }
    return false;
  }

  function drawEdgeWeight(x, y, text) {
    ctx.save();
    ctx.font = '500 9.5px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const width = ctx.measureText(text).width + 8;
    ctx.fillStyle = '#FAFBF8';
    ctx.strokeStyle = '#D5DFD6';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(x - width / 2, y - 7, width, 14, 4);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#566B62';
    ctx.fillText(text, x, y);
    ctx.restore();
  }

  function drawEndpointTag(x, y, text, color) {
    ctx.save();
    ctx.font = '700 9px Outfit, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const width = ctx.measureText(text).width + 8;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.roundRect(x - width / 2, y - 7, width, 14, 4);
    ctx.fill();

    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(text, x, y);
    ctx.restore();
  }

  function setupCanvasInteractions() {
    if (!canvas) return;

    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const mouseX = (e.clientX - rect.left) * scaleX;
      const mouseY = (e.clientY - rect.top) * scaleY;

      let hovered = null;
      (state.graph.nodes || []).forEach(n => {
        const px = (n.x / 100) * canvas.width;
        const py = (n.y / 100) * canvas.height;
        const dist = Math.hypot(mouseX - px, mouseY - py);
        if (dist <= 15) {
          hovered = n;
        }
      });

      if (hovered) {
        tooltip.style.display = 'block';
        tooltip.style.left = `${e.clientX - rect.left + 15}px`;
        tooltip.style.top = `${e.clientY - rect.top - 15}px`;
        tooltip.innerHTML = `<strong>${hovered.label || hovered.id}</strong><br><span style="text-transform:capitalize;">${hovered.type} Node</span>`;
      } else {
        tooltip.style.display = 'none';
      }
    });

    canvas.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
    });
  }

  // =========================================================================
  // Action Handlers
  // =========================================================================

  function setupEventListeners() {
    // 1. Auto-Match Buttons
    const triggerMatch = async () => {
      try {
        const res = await fetch('/api/match/auto', { method: 'POST' });
        const data = await res.json();

        if (!res.ok) {
          showToast(data.error || 'Failed to match food.', 'error');
          return;
        }

        state.activeRoutePath = data.path || [];
        state.activeRouteDist = data.distance_km;
        drawMap();

        renderMatchResult(data);
        showToast(`Auto-matched '${data.food.name}' to '${data.ngo.name}' (${data.distance_km} km)!`, 'success');

        await refreshAllData();
      } catch (err) {
        console.error('Match failed:', err);
        showToast('Error executing auto-match.', 'error');
      }
    };

    document.getElementById('triggerAutoMatchBtn')?.addEventListener('click', triggerMatch);
    document.getElementById('actionMatchBtn')?.addEventListener('click', triggerMatch);

    // 2. Complete Pickup (FIFO Queue)
    document.getElementById('completePickupBtn')?.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/queue/complete', { method: 'POST' });
        const data = await res.json();
        if (!res.ok) {
          showToast(data.error || 'No pickups in queue.', 'warning');
          return;
        }
        showToast(`Delivered: ${data.completed_pickup.food_name}!`, 'success');
        await refreshAllData();
      } catch (err) {
        console.error('Complete pickup failed:', err);
      }
    });

    // 3. Undo Last Action (LIFO Stack)
    document.getElementById('undoBtn')?.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/undo', { method: 'POST' });
        const data = await res.json();
        if (!res.ok) {
          showToast(data.error || 'Nothing to undo.', 'warning');
          return;
        }
        showToast(`Undo successful: ${data.message}`, 'info');
        state.activeRoutePath = [];
        drawMap();
        await refreshAllData();
      } catch (err) {
        console.error('Undo failed:', err);
      }
    });

    // 4. Status Filter Pills
    document.querySelectorAll('#foodStatusFilter .tab-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#foodStatusFilter .tab-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        loadFood();
      });
    });

    // 5. Merge Sort Selector
    document.getElementById('foodSortBy')?.addEventListener('change', () => {
      loadFood();
    });

    // 6. Directory Tabs (NGOs vs Donors)
    document.querySelectorAll('.dir-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.dir-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const target = tab.dataset.tab;
        if (target === 'ngos') {
          document.getElementById('ngosGrid').style.display = 'grid';
          document.getElementById('donorsGrid').style.display = 'none';
        } else {
          document.getElementById('ngosGrid').style.display = 'none';
          document.getElementById('donorsGrid').style.display = 'grid';
        }
      });
    });

    // 7. Modals Open / Close
    document.getElementById('openAddFoodModalBtn')?.addEventListener('click', () => openModal('addFoodModal'));
    document.getElementById('openAddDonorModalBtn')?.addEventListener('click', () => openModal('addDonorModal'));
    document.getElementById('openAddNgoModalBtn')?.addEventListener('click', () => openModal('addNgoModal'));
    document.getElementById('dsaGuideBtn')?.addEventListener('click', () => openModal('dsaGuideModal'));
    document.getElementById('viewHeapModalBtn')?.addEventListener('click', openHeapVisualizer);

    document.querySelectorAll('.close-modal-btn, [data-close]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const modalId = btn.dataset.close || btn.closest('.modal-overlay')?.id;
        if (modalId) closeModal(modalId);
      });
    });

    // 8. Add Food Form Submission
    document.getElementById('addFoodForm')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById('foodNameInput').value,
        donor_id: document.getElementById('foodDonorSelect').value,
        category: document.getElementById('foodCategorySelect').value,
        quantity: parseFloat(document.getElementById('foodQtyInput').value),
        expiry_hours: parseFloat(document.getElementById('foodExpiryInput').value),
      };

      try {
        const res = await fetch('/api/food', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          showToast(data.error || 'Failed to list food.', 'error');
          return;
        }
        closeModal('addFoodModal');
        document.getElementById('addFoodForm').reset();
        showToast(`Listed: '${data.food.name}' added to Min-Heap!`, 'success');
        await refreshAllData();
      } catch (err) {
        console.error('Add food failed:', err);
      }
    });

    // 9. Add Donor Form Submission
    document.getElementById('addDonorForm')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById('donorNameInput').value,
        location: document.getElementById('donorLocationSelect').value,
        type: document.getElementById('donorTypeInput').value,
        contact: document.getElementById('donorContactInput').value,
      };

      try {
        const res = await fetch('/api/donors', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          showToast(data.error || 'Failed to register donor.', 'error');
          return;
        }
        closeModal('addDonorModal');
        document.getElementById('addDonorForm').reset();
        showToast(`Donor '${data.donor.name}' registered into Hash Table!`, 'success');
        await refreshAllData();
      } catch (err) {
        console.error('Add donor failed:', err);
      }
    });

    // 10. Add NGO Form Submission
    document.getElementById('addNgoForm')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById('ngoNameInput').value,
        location: document.getElementById('ngoLocationSelect').value,
        capacity: parseFloat(document.getElementById('ngoCapacityInput').value),
        serves: document.getElementById('ngoServesInput').value,
      };

      try {
        const res = await fetch('/api/ngos', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          showToast(data.error || 'Failed to register NGO.', 'error');
          return;
        }
        closeModal('addNgoModal');
        document.getElementById('addNgoForm').reset();
        showToast(`NGO '${data.ngo.name}' registered into Hash Table!`, 'success');
        await refreshAllData();
      } catch (err) {
        console.error('Add NGO failed:', err);
      }
    });

    // 11. Search Mode Radio Switcher
    document.querySelectorAll('input[name="searchMode"]').forEach(radio => {
      radio.addEventListener('change', (e) => {
        const mode = e.target.value;
        if (mode === 'range') {
          document.getElementById('singleTargetInputGroup').style.display = 'none';
          document.getElementById('rangeInputGroup').style.display = 'flex';
        } else {
          document.getElementById('singleTargetInputGroup').style.display = 'flex';
          document.getElementById('rangeInputGroup').style.display = 'none';
        }
      });
    });

    // 12. Execute Binary Search
    document.getElementById('executeBinarySearchBtn')?.addEventListener('click', async () => {
      const mode = document.querySelector('input[name="searchMode"]:checked').value;
      let url = `/api/food/search?mode=${mode}`;

      if (mode === 'range') {
        const minVal = document.getElementById('searchMinQty').value || 0;
        const maxVal = document.getElementById('searchMaxQty').value || 999;
        url += `&min=${minVal}&max=${maxVal}`;
      } else {
        const targetVal = document.getElementById('searchTargetQty').value || 0;
        url += `&target=${targetVal}`;
      }

      try {
        const res = await fetch(url);
        const data = await res.json();
        renderSearchResults(data);
      } catch (err) {
        console.error('Search failed:', err);
      }
    });

    // 13. Reset System Seed Data
    document.getElementById('resetDataBtn')?.addEventListener('click', async () => {
      if (!confirm('Reset system data back to default 5 Donors, 5 NGOs, and 10 Food items?')) return;
      try {
        const res = await fetch('/api/reset', { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'System reset to seed data.', 'info');
        state.activeRoutePath = [];
        await refreshAllData();
      } catch (err) {
        console.error('Reset failed:', err);
      }
    });
  }

  // =========================================================================
  // Search Results Rendering
  // =========================================================================

  function renderSearchResults(data) {
    const summaryEl = document.getElementById('searchResultSummary');
    const listEl = document.getElementById('searchResultsList');

    summaryEl.textContent = `${data.explanation} Found ${data.count} matching food batches.`;

    if (!data.results || data.results.length === 0) {
      listEl.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 1.5rem; text-align: center; color: var(--text-muted);">
          No batches found matching this binary search criteria.
        </div>
      `;
      return;
    }

    listEl.innerHTML = data.results.map(f => `
      <div style="background:#FFFFFF; border:1px solid var(--border-light); border-radius:var(--radius-md); padding:0.85rem; display:flex; flex-direction:column; gap:0.25rem;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="color:var(--text-main); font-size:0.95rem;">${escapeHtml(f.name)}</strong>
          <span class="badge-status available" style="font-size:0.7rem;">${f.quantity} ${f.unit || 'kg'}</span>
        </div>
        <div style="font-size:0.8rem; color:var(--text-muted);">
          <span>Expires in ${f.expiry_hours}h &bull; ${escapeHtml(f.donor_name || f.donor_id)}</span>
        </div>
      </div>
    `).join('');
  }

  // =========================================================================
  // Match Result Breakdown
  // =========================================================================

  function renderMatchResult(data) {
    const area = document.getElementById('matchOutputArea');
    const food = data.food;
    const ngo = data.ngo;
    const pathStr = (data.path || []).join(' &rarr; ');

    let evalRows = (data.evaluations || []).map(ev => {
      const isWinner = (ev.ngo_id === ngo.id);
      return `
        <tr class="${isWinner ? 'eval-winner' : ''}">
          <td>${isWinner ? '&#10004; ' : ''}${escapeHtml(ev.ngo_name)}</td>
          <td>${ev.location}</td>
          <td>${ev.capacity} kg</td>
          <td><strong>${ev.distance !== null ? ev.distance + ' km' : 'Unreachable'}</strong></td>
        </tr>
      `;
    }).join('');

    area.innerHTML = `
      <div class="match-result-box">
        <div class="match-badge-banner">
          <div>
            <span class="match-badge-title">Optimal Route Found &bull; Dijkstra</span>
            <div style="font-family:var(--font-heading); font-size:1.1rem; font-weight:700; margin-top:0.2rem;">
              ${escapeHtml(food.name)} &rarr; ${escapeHtml(ngo.name)}
            </div>
          </div>
          <div class="match-badge-dist">${data.distance_km} km</div>
        </div>

        <div class="match-route-steps">
          <div style="font-size:0.8rem; font-weight:700; color:var(--primary); text-transform:uppercase;">Road Traversal:</div>
          <div class="route-step-node">${pathStr}</div>
        </div>

        <div>
          <div style="font-size:0.8rem; font-weight:700; color:var(--text-muted); margin-bottom:0.3rem;">All NGO Dijkstra Distance Calculations:</div>
          <table class="evaluations-table">
            <thead>
              <tr>
                <th>Shelter</th>
                <th>Location</th>
                <th>Cap</th>
                <th>Distance</th>
              </tr>
            </thead>
            <tbody>
              ${evalRows}
            </tbody>
          </table>
        </div>
      </div>
    `;

    document.getElementById('routeSummaryText').textContent = 
      `Shortest route: [${(data.path || []).join(' -> ')}] &bull; Distance: ${data.distance_km} km &bull; Enqueued to FIFO pickup queue.`;
  }

  // =========================================================================
  // Heap Visualizer Modal
  // =========================================================================

  async function openHeapVisualizer() {
    try {
      const res = await fetch('/api/food/urgent');
      const data = await res.json();
      const items = data.items || [];

      const container = document.getElementById('heapVisualizerContent');
      if (items.length === 0) {
        container.innerHTML = `<p style="padding:2rem; text-align:center; color:var(--text-muted);">The Min-Heap is currently empty.</p>`;
      } else {
        let cardsHtml = items.map((item, idx) => `
          <div style="background:#FFFFFF; border:1px solid var(--border-light); border-radius:var(--radius-md); padding:0.95rem; display:flex; flex-direction:column; gap:0.35rem; ${idx === 0 ? 'border:2px solid var(--urgent-red); box-shadow:0 4px 12px rgba(217,56,58,0.15);' : ''}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-family:var(--font-mono); font-size:0.75rem; font-weight:700; color:${idx === 0 ? 'var(--urgent-red)' : 'var(--text-muted)'};">
                ${idx === 0 ? 'ROOT (Index 0)' : `Index ${idx}`}
              </span>
              <span class="badge-expiry ${getExpiryClass(item.expiry_hours)}">${item.expiry_hours}h</span>
            </div>
            <strong style="font-size:1rem; font-family:var(--font-heading);">${escapeHtml(item.name)}</strong>
            <span style="font-size:0.8rem; color:var(--text-muted);">${item.quantity} ${item.unit || 'kg'} &bull; ${escapeHtml(item.donor_name || item.donor_id)}</span>
          </div>
        `).join('');

        container.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:1rem;">
            <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:0.85rem;">
              ${cardsHtml}
            </div>
            <p style="font-size:0.82rem; color:var(--text-light); text-align:center;">
              Heap Invariant: Every parent node at index <code>(i - 1) // 2</code> has an expiry &le; child nodes at <code>2i + 1</code> and <code>2i + 2</code>.
            </p>
          </div>
        `;
      }

      openModal('heapModal');
    } catch (err) {
      console.error('Failed to view heap:', err);
    }
  }

  // =========================================================================
  // Helpers & Utilities
  // =========================================================================

  function getExpiryClass(hours) {
    const h = parseFloat(hours);
    if (h < 6.0) return 'urgent';
    if (h <= 24.0) return 'soon';
    return 'safe';
  }

  function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'flex';
  }

  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  }

  function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(20px)';
      toast.style.transition = 'all 300ms ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
