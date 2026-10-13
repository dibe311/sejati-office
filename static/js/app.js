/**
 * Hermes Telemetry & Multi-Agent Observability Engine
 * Linear Design System Implementation — 100% Anti-Slop Precision Architecture
 * Ref: popular-web-designs/templates/linear.app.md
 */

// Global State
let socket = null;
let agentsState = {};
let messagesState = [];
let activeFilter = 'all';
let selectedAgentFilter = null;
let autoScrollEnabled = true;
let consoleExpanded = true;

let latencyChartInstance = null;
let systemChartInstance = null;

const systemTelemetryHistory = {
  labels: [],
  cpu: [],
  ram: []
};

// 12 Agent Order & Metadata
const AGENT_ORDER = [
  'orchestrator',
  'frontend',
  'backend',
  'security',
  'migration',
  'integration',
  'reviewer',
  'researcher',
  'database',
  '3d',
  'gamedev',
  'api'
];

const AGENT_META = {
  orchestrator: { code: 'ORC', color: '#8B5CF6' },
  frontend:     { code: 'FRN', color: '#06B6D4' },
  backend:      { code: 'BCK', color: '#3B82F6' },
  security:     { code: 'SEC', color: '#EF4444' },
  migration:    { code: 'MIG', color: '#F59E0B' },
  integration:  { code: 'INT', color: '#10B981' },
  reviewer:     { code: 'REV', color: '#84CC16' },
  researcher:   { code: 'RES', color: '#EC4899' },
  database:     { code: 'DAT', color: '#0284C7' },
  '3d':         { code: '3DR', color: '#F97316' },
  gamedev:      { code: 'GAM', color: '#A855F7' },
  api:          { code: 'API', color: '#F43F5E' }
};

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initLucide();
  initCharts();
  connectWebSocket();
  setupEventListeners();
  loadInitialData();
});

function initLucide() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// -------------------------------------------------------------
// WebSocket Connection
// -------------------------------------------------------------
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;
  
  updateConnectionStatus('connecting');

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    updateConnectionStatus('connected');
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleSocketMessage(data);
    } catch (err) {
      console.error('Error parsing WS message:', err);
    }
  };

  socket.onclose = () => {
    updateConnectionStatus('disconnected');
    setTimeout(connectWebSocket, 3000);
  };

  socket.onerror = () => {
    updateConnectionStatus('disconnected');
  };
}

function updateConnectionStatus(status) {
  const badge = document.getElementById('connectionBadge');
  const text = document.getElementById('connectionText');
  if (!badge || !text) return;

  if (status === 'connected') {
    badge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
    badge.style.color = 'var(--status-emerald)';
    badge.firstElementChild.className = 'status-dot dot-emerald';
    text.textContent = 'WS: LIVE';
  } else if (status === 'connecting') {
    badge.style.borderColor = 'rgba(245, 158, 11, 0.3)';
    badge.style.color = 'var(--status-amber)';
    badge.firstElementChild.className = 'status-dot dot-amber';
    text.textContent = 'CONNECTING';
  } else {
    badge.style.borderColor = 'rgba(244, 63, 94, 0.3)';
    badge.style.color = 'var(--status-rose)';
    badge.firstElementChild.className = 'status-dot dot-rose';
    text.textContent = 'OFFLINE';
  }
}

function handleSocketMessage(data) {
  switch (data.type) {
    case 'init':
      agentsState = data.agents || {};
      messagesState = data.messages || [];
      renderAgentMatrix();
      renderMessageStream();
      updateCharts();
      updateHeaderStats();
      break;

    case 'telemetry_tick':
      updateTelemetry(data);
      break;

    case 'agent_update':
      if (data.agent) {
        agentsState[data.agent.name] = data.agent;
        renderAgentMatrix();
        updateCharts();
        updateHeaderStats();
      }
      break;

    case 'message_new':
      if (data.message) {
        messagesState.push(data.message);
        if (messagesState.length > 600) messagesState.shift();
        appendMessageToStream(data.message);
        updateHeaderStats();
        handleSwarmStepUpdate(data.message);
      }
      break;

    case 'benchmark_started':
      updateBenchmarkUI(data.benchmark);
      break;

    case 'benchmark_completed':
      updateBenchmarkUI(data.benchmark);
      break;

    default:
      break;
  }
}

// -------------------------------------------------------------
// Top Header Telemetry Ticker
// -------------------------------------------------------------
function updateTelemetry(data) {
  if (!data.system) return;

  const cpu = data.system.cpu_percent || 0;
  const ram = data.system.ram_percent || 0;
  const uptimeSec = data.system.uptime_seconds || 0;

  const metricCpu = document.getElementById('metricCpu');
  const metricRam = document.getElementById('metricRam');
  const metricUptime = document.getElementById('metricUptime');
  const metricFleet = document.getElementById('metricFleet');
  const hostResourceLegend = document.getElementById('hostResourceLegend');

  if (metricCpu) metricCpu.textContent = `${cpu}%`;
  if (metricRam) metricRam.textContent = `${ram}% (${data.system.ram_used_gb} GB)`;
  if (hostResourceLegend) {
    hostResourceLegend.textContent = `CPU: ${cpu}% | RAM: ${ram}% (${data.system.ram_used_gb} GB)`;
  }
  
  if (metricUptime) {
    const h = Math.floor(uptimeSec / 3600).toString().padStart(2, '0');
    const m = Math.floor((uptimeSec % 3600) / 60).toString().padStart(2, '0');
    const s = (uptimeSec % 60).toString().padStart(2, '0');
    metricUptime.textContent = `${h}:${m}:${s}`;
  }

  if (metricFleet) {
    const busyCount = data.agents_active_count || 0;
    const totalCount = data.agents_total_count || Object.keys(agentsState).length || AGENT_ORDER.length;
    if (busyCount > 0) {
      metricFleet.style.color = 'var(--status-amber)';
      metricFleet.textContent = `${busyCount} BUSY / ${totalCount} TOTAL`;
    } else {
      metricFleet.style.color = 'var(--status-emerald)';
      metricFleet.textContent = `${totalCount}/${totalCount} READY`;
    }
  }

  // Update System Chart
  const timeLabel = data.timestamp || new Date().toLocaleTimeString();
  systemTelemetryHistory.labels.push(timeLabel);
  systemTelemetryHistory.cpu.push(cpu);
  systemTelemetryHistory.ram.push(ram);

  if (systemTelemetryHistory.labels.length > 25) {
    systemTelemetryHistory.labels.shift();
    systemTelemetryHistory.cpu.shift();
    systemTelemetryHistory.ram.shift();
  }

  if (systemChartInstance) {
    systemChartInstance.data.labels = systemTelemetryHistory.labels;
    systemChartInstance.data.datasets[0].data = systemTelemetryHistory.cpu;
    systemChartInstance.data.datasets[1].data = systemTelemetryHistory.ram;
    systemChartInstance.update('none');
  }
}

function updateHeaderStats() {
  const agents = Object.values(agentsState);
  const totalTasks = agents.reduce((sum, a) => sum + (a.total_tasks || 0), 0);
  
  const latencies = agents.filter(a => a.avg_latency_ms > 0).map(a => a.avg_latency_ms);
  const avgLatency = latencies.length > 0 
    ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length) 
    : 0;

  const metricTotalTasks = document.getElementById('metricTotalTasks');
  const metricAvgLatency = document.getElementById('metricAvgLatency');
  const streamItemCount = document.getElementById('streamItemCount');

  if (metricTotalTasks) metricTotalTasks.textContent = totalTasks;
  if (metricAvgLatency) {
    metricAvgLatency.textContent = avgLatency > 1000 ? `${(avgLatency/1000).toFixed(1)}s` : `${avgLatency} ms`;
  }
  if (streamItemCount) streamItemCount.textContent = `${messagesState.length} EVENTS`;
  const traceTabCount = document.getElementById('traceTabCount');
  if (traceTabCount) traceTabCount.textContent = messagesState.filter(m => m.type !== 'probe').length;
}

// -------------------------------------------------------------
// High-Density Fleet Execution Matrix Table
// -------------------------------------------------------------
function renderAgentMatrix() {
  const tbody = document.getElementById('agentMatrixBody');
  if (!tbody) return;

  tbody.innerHTML = AGENT_ORDER.map((name, idx) => {
    const agent = agentsState[name] || {
      name: name,
      role: 'Specialist',
      status: 'idle',
      total_tasks: 0,
      avg_latency_ms: 0
    };

    const isBusy = agent.status === 'busy';
    const isError = agent.status === 'error';
    const isSelected = selectedAgentFilter === name;
    const meta = AGENT_META[name] || { code: 'AGT', color: '#94A3B8' };

    let statusPill = `<span class="status-pill" style="border-color: rgba(16, 185, 129, 0.25); color: var(--status-emerald); padding: 0 6px; height: 18px; font-size: 9px;"><span class="status-dot dot-emerald" style="width: 5px; height: 5px;"></span>IDLE</span>`;
    if (isBusy) {
      statusPill = `<span class="status-pill" style="border-color: rgba(245, 158, 11, 0.35); color: var(--status-amber); padding: 0 6px; height: 18px; font-size: 9px;"><span class="status-dot dot-amber" style="width: 5px; height: 5px;"></span>BUSY</span>`;
    } else if (isError) {
      statusPill = `<span class="status-pill" style="border-color: rgba(244, 63, 94, 0.35); color: var(--status-rose); padding: 0 6px; height: 18px; font-size: 9px;"><span class="status-dot dot-rose" style="width: 5px; height: 5px;"></span>ERR</span>`;
    }

    const latencyFormatted = agent.avg_latency_ms > 0 
      ? (agent.avg_latency_ms > 1000 ? `${(agent.avg_latency_ms/1000).toFixed(1)}s` : `${agent.avg_latency_ms}ms`)
      : '-';

    return `
      <tr 
        onclick="toggleAgentFilter('${name}')"
        class="${isSelected ? 'row-selected' : ''}"
      >
        <td style="width: 50px;">
          <span class="agent-code-badge" style="border-left: 2px solid ${meta.color};">
            ${meta.code}
          </span>
        </td>
        <td>
          <div class="agent-meta-cell">
            <span class="agent-name">
              <span>${agent.name.toUpperCase()}</span>
            </span>
            <span class="agent-role" title="${escapeHtml(agent.role || '')}">${agent.role || ''}</span>
          </div>
        </td>
        <td style="text-align: center; width: 65px;">${statusPill}</td>
        <td style="text-align: right; width: 45px; font-weight: 600; color: var(--text-secondary);" class="tabular-nums">${agent.total_tasks || 0}</td>
        <td style="text-align: right; width: 65px; font-weight: 600; color: var(--status-sky);" class="tabular-nums">${latencyFormatted}</td>
      </tr>
    `;
  }).join('');
}

function toggleAgentFilter(agentName) {
  if (selectedAgentFilter === agentName) {
    selectedAgentFilter = null;
    showToast('Filter agen dibersihkan (menampilkan semua)', 'info');
  } else {
    selectedAgentFilter = agentName;
    showToast(`Filter aktif: @${agentName.toUpperCase()}`, 'info');
    
    // Auto-select agent in the Command Dispatch Select and focus prompt input
    const select = document.getElementById('dispatchTargetSelect');
    if (select) {
      select.value = agentName;
      updateDispatchTargetHint();
    }
    const input = document.getElementById('dispatchPromptInput');
    if (input) {
      input.focus();
    }
  }
  renderAgentMatrix();
  renderMessageStream();
}

function clearAgentFilter() {
  selectedAgentFilter = null;
  renderAgentMatrix();
  renderMessageStream();
  showToast('Filter agen dibersihkan (menampilkan semua)', 'info');
}
window.clearAgentFilter = clearAgentFilter;

// -------------------------------------------------------------
// Structured Execution Trace Log Viewport
// -------------------------------------------------------------
function renderMessageStream() {
  const container = document.getElementById('messageStream');
  if (!container) return;

  container.innerHTML = '';
  
  // Active Agent Filter Banner
  if (selectedAgentFilter) {
    const banner = document.createElement('div');
    banner.style.cssText = 'display: flex; align-items: center; justify-content: space-between; padding: 5px 10px; background: rgba(112, 126, 255, 0.1); border: 1px solid rgba(112, 126, 255, 0.25); border-radius: 5px; font-family: var(--font-mono); font-size: 10px; color: var(--brand-violet); margin-bottom: 6px;';
    banner.innerHTML = `
      <span>Filter Spesialis Aktif: <strong>@${selectedAgentFilter.toUpperCase()}</strong></span>
      <button onclick="clearAgentFilter()" style="background: transparent; border: none; color: var(--text-primary); cursor: pointer; font-size: 13px; font-weight: bold; line-height: 1;" title="Hapus filter">×</button>
    `;
    container.appendChild(banner);
  }

  const filtered = filterMessages(messagesState);
  if (filtered.length === 0) {
    const emptyBox = document.createElement('div');
    emptyBox.style.cssText = 'height: 160px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-subtle); font-family: var(--font-mono); font-size: 11px; gap: 8px;';
    emptyBox.innerHTML = `
      <i data-lucide="terminal" style="width: 20px; height: 20px; opacity: 0.35;"></i>
      <span>[TIDAK ADA EVENT LOG UNTUK FILTER INI]</span>
      ${selectedAgentFilter ? `<button onclick="clearAgentFilter()" class="btn-linear" style="font-size: 10px; padding: 2px 8px;">Hapus Filter @${selectedAgentFilter.toUpperCase()}</button>` : ''}
    `;
    container.appendChild(emptyBox);
    initLucide();
    return;
  }

  filtered.forEach(msg => {
    container.appendChild(createTraceElement(msg));
  });

  scrollMessageStreamToBottom();
  initLucide();
}

function appendMessageToStream(msg) {
  const container = document.getElementById('messageStream');
  if (!container) return;

  if (selectedAgentFilter) {
    const s = msg.sender.toLowerCase();
    const t = (msg.target || '').toLowerCase();
    if (!s.includes(selectedAgentFilter) && !t.includes(selectedAgentFilter)) return;
  }

  if (activeFilter !== 'all') {
    if (activeFilter === 'task' && !['task', 'result', 'broadcast'].includes(msg.type)) return;
    if (activeFilter === 'chat' && msg.type !== 'chat') return;
    if (activeFilter === 'swarm' && !['swarm_step', 'swarm_init', 'swarm_done'].includes(msg.type)) return;
    if (activeFilter === 'benchmark' && !['benchmark', 'benchmark_summary'].includes(msg.type)) return;
    if (activeFilter === 'blackboard' && msg.type !== 'blackboard') return;
  }

  const elem = createTraceElement(msg);
  container.appendChild(elem);
  scrollMessageStreamToBottom();
  initLucide();
}

function createTraceElement(msg) {
  const div = document.createElement('div');
  div.className = 'trace-card';

  // Event category tag
  let eventBadge = `<span class="event-type-pill pill-dialog">TRACE</span>`;
  if (msg.type === 'task') {
    eventBadge = `<span class="event-type-pill pill-dispatch">DISPATCH</span>`;
  } else if (msg.type === 'result') {
    eventBadge = `<span class="event-type-pill pill-result">RESULT</span>`;
  } else if (msg.type === 'benchmark' || msg.type === 'benchmark_summary') {
    eventBadge = `<span class="event-type-pill pill-benchmark">BENCHMARK</span>`;
  } else if (msg.type === 'swarm_step' || msg.type === 'swarm_init' || msg.type === 'swarm_done') {
    eventBadge = `<span class="event-type-pill pill-swarm">SWARM</span>`;
  } else if (msg.type === 'broadcast') {
    eventBadge = `<span class="event-type-pill pill-broadcast">BROADCAST</span>`;
  } else if (msg.type === 'blackboard') {
    eventBadge = `<span class="event-type-pill pill-blackboard">BLACKBOARD</span>`;
  } else if (msg.type === 'chat') {
    eventBadge = `<span class="event-type-pill pill-dialog">DIALOG</span>`;
  }

  // Format latency pill
  const latencyBadge = msg.latency_ms 
    ? `<span class="latency-tag tabular-nums">⚡ ${msg.latency_ms > 1000 ? `${(msg.latency_ms/1000).toFixed(2)}s` : `${msg.latency_ms}ms`}</span>`
    : '';

  const senderStr = (msg.sender || 'UNKNOWN').toUpperCase();
  const targetStr = (msg.target || 'ALL').toUpperCase();

  div.innerHTML = `
    <!-- Trace Header -->
    <div class="trace-card-header">
      <div class="trace-route">
        <span class="trace-timestamp tabular-nums">${msg.timestamp || ''}</span>
        ${eventBadge}
        <span class="trace-actor">${escapeHtml(senderStr)}</span>
        <span class="trace-arrow">➔</span>
        <span class="trace-target">@${escapeHtml(targetStr)}</span>
      </div>
      <div class="trace-actions">
        ${latencyBadge}
        <button onclick="copyPayload(this)" data-payload="${encodeURIComponent(msg.content)}" class="copy-payload-btn" title="Salin payload">
          <i data-lucide="copy" style="width: 12px; height: 12px;"></i>
        </button>
      </div>
    </div>
    <!-- Trace Payload Body -->
    <div class="trace-payload-body">
      ${formatContentClean(msg.content, msg.id)}
    </div>
  `;
  return div;
}

function formatContentClean(text, msgId) {
  if (!text) return '';
  const lines = text.split('\n');
  const isLong = text.length > 420 || lines.length > 6;
  const safeId = msgId ? String(msgId).replace(/[^a-zA-Z0-9_]/g, '_') : 'msg_' + Math.random().toString(36).substr(2, 9);

  if (!isLong) {
    return renderMarkdown(text);
  }

  const previewLines = lines.slice(0, 5).join('\n') + '\n...';
  return `
    <div id="short_${safeId}">
      ${renderMarkdown(previewLines)}
      <button type="button" onclick="expandPayload('${safeId}')" class="expand-toggle-btn">
        <i data-lucide="chevrons-down" style="width: 11px; height: 11px;"></i>
        <span>Tampilkan selengkapnya (${lines.length} baris)</span>
      </button>
    </div>
    <div id="full_${safeId}" style="display: none;">
      ${renderMarkdown(text)}
      <button type="button" onclick="collapsePayload('${safeId}')" class="expand-toggle-btn" style="color: var(--text-subtle);">
        <i data-lucide="chevrons-up" style="width: 11px; height: 11px;"></i>
        <span>Ciutkan</span>
      </button>
    </div>
  `;
}

function renderMarkdown(text) {
  let content = escapeHtml(text);
  // Code blocks ```code```
  content = content.replace(/```([\s\S]*?)```/g, (match, code) => {
    return `<pre><code>${code.trim()}</code></pre>`;
  });
  // Inline code `code`
  content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bold **text**
  content = content.replace(/\*\*([^*]+)\*\*/g, '<strong style="color: var(--text-primary); font-weight: 600;">$1</strong>');
  return content;
}

function expandPayload(id) {
  const shortEl = document.getElementById('short_' + id);
  const fullEl = document.getElementById('full_' + id);
  if (shortEl) shortEl.style.display = 'none';
  if (fullEl) fullEl.style.display = 'block';
  initLucide();
}

function collapsePayload(id) {
  const shortEl = document.getElementById('short_' + id);
  const fullEl = document.getElementById('full_' + id);
  if (fullEl) fullEl.style.display = 'none';
  if (shortEl) shortEl.style.display = 'block';
  initLucide();
}

function copyPayload(btn) {
  const payload = decodeURIComponent(btn.dataset.payload || '');
  if (!payload) return;
  navigator.clipboard.writeText(payload).then(() => {
    const origHtml = btn.innerHTML;
    btn.innerHTML = `<i data-lucide="check" style="width: 12px; height: 12px; color: var(--status-emerald);"></i>`;
    initLucide();
    showToast('Payload disalin ke clipboard', 'success');
    setTimeout(() => {
      btn.innerHTML = origHtml;
      initLucide();
    }, 1800);
  }).catch(err => {
    showToast('Gagal menyalin: ' + err.message, 'error');
  });
}

function filterMessages(messages) {
  let list = messages.filter(m => m.type !== 'probe');

  // Real-time search query filter
  const searchInput = document.getElementById('searchTraceInput');
  if (searchInput && searchInput.value.trim()) {
    const q = searchInput.value.trim().toLowerCase();
    list = list.filter(m => {
      const c = (m.content || '').toLowerCase();
      const s = (m.sender || '').toLowerCase();
      const t = (m.target || '').toLowerCase();
      return c.includes(q) || s.includes(q) || t.includes(q);
    });
  }

  if (selectedAgentFilter) {
    list = list.filter(m => {
      const s = m.sender.toLowerCase();
      const t = (m.target || '').toLowerCase();
      return s.includes(selectedAgentFilter) || t.includes(selectedAgentFilter);
    });
  }
  if (activeFilter === 'all') return list;
  if (activeFilter === 'task') return list.filter(m => ['task', 'result', 'broadcast'].includes(m.type));
  if (activeFilter === 'chat') return list.filter(m => m.type === 'chat');
  if (activeFilter === 'swarm') return list.filter(m => ['swarm_step', 'swarm_init', 'swarm_done'].includes(m.type));
  if (activeFilter === 'benchmark') return list.filter(m => ['benchmark', 'benchmark_summary'].includes(m.type));
  if (activeFilter === 'blackboard') return list.filter(m => m.type === 'blackboard');
  return list;
}

function scrollMessageStreamToBottom() {
  if (!autoScrollEnabled) return;
  const container = document.getElementById('messageStream');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

// -------------------------------------------------------------
// Precision Technical Charts (Chart.js)
// -------------------------------------------------------------
function initCharts() {
  // Chart 1: Latency Benchmark (Bar Chart)
  const ctxLatency = document.getElementById('latencyChart');
  if (ctxLatency) {
    latencyChartInstance = new Chart(ctxLatency.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['Orch', 'Front', 'Back', 'Sec', 'Mig', 'Int', 'Rev', 'Res', 'DB', '3D', 'Game', 'API'],
        datasets: [{
          label: 'Latensi (ms)',
          data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          backgroundColor: [
            '#8B5CF6', '#06B6D4', '#3B82F6', '#EF4444',
            '#F59E0B', '#10B981', '#84CC16', '#EC4899',
            '#0284C7', '#F97316', '#A855F7', '#F43F5E'
          ],
          borderWidth: 0,
          borderRadius: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f1011',
            borderColor: 'rgba(255, 255, 255, 0.12)',
            borderWidth: 1,
            titleColor: '#f7f8f8',
            bodyColor: '#38bdf8',
            titleFont: { family: 'JetBrains Mono', size: 10, weight: 'bold' },
            bodyFont: { family: 'JetBrains Mono', size: 10 },
            padding: 8,
            displayColors: false,
            callbacks: {
              title: (items) => {
                const idx = items[0].dataIndex;
                const name = AGENT_ORDER[idx] || '';
                return `[${AGENT_META[name]?.code || 'AGT'}] ${name.toUpperCase()}`;
              },
              label: (item) => {
                const val = item.raw || 0;
                return val > 1000 ? ` Latensi: ${(val/1000).toFixed(2)} detik` : ` Latensi: ${val} ms`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#8a8f98', font: { family: 'JetBrains Mono', size: 9, weight: 'bold' } }
          },
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(255, 255, 255, 0.04)' },
            ticks: { 
              color: '#62666d', 
              font: { family: 'JetBrains Mono', size: 9 },
              callback: (v) => v >= 1000 ? (v/1000).toFixed(1) + 's' : v + 'ms'
            }
          }
        }
      }
    });
  }

  // Chart 2: System Telemetry (Line Chart, CPU & RAM)
  const ctxSystem = document.getElementById('systemChart');
  if (ctxSystem) {
    systemChartInstance = new Chart(ctxSystem.getContext('2d'), {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'CPU %',
            data: [],
            borderColor: '#38bdf8',
            borderWidth: 1.5,
            fill: false,
            tension: 0.2,
            pointRadius: 0
          },
          {
            label: 'RAM %',
            data: [],
            borderColor: '#10b981',
            borderWidth: 1.5,
            fill: false,
            tension: 0.2,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: '#8a8f98', font: { family: 'JetBrains Mono', size: 9 }, boxWidth: 10 }
          },
          tooltip: {
            backgroundColor: '#0f1011',
            borderColor: 'rgba(255, 255, 255, 0.12)',
            borderWidth: 1,
            titleFont: { family: 'JetBrains Mono', size: 10 },
            bodyFont: { family: 'JetBrains Mono', size: 10 },
            padding: 8
          }
        },
        scales: {
          x: { display: false },
          y: {
            min: 0,
            max: 100,
            grid: { color: 'rgba(255, 255, 255, 0.04)' },
            ticks: { 
              color: '#62666d', 
              font: { family: 'JetBrains Mono', size: 9 },
              stepSize: 25,
              callback: (v) => v + '%'
            }
          }
        }
      }
    });
  }
}

function updateCharts() {
  const agents = AGENT_ORDER.map(name => agentsState[name] || { avg_latency_ms: 0 });
  if (latencyChartInstance) {
    latencyChartInstance.data.datasets[0].data = agents.map(a => a.avg_latency_ms || 0);
    latencyChartInstance.update();
  }
}

// -------------------------------------------------------------
// UI Event Handlers
// -------------------------------------------------------------
function setupEventListeners() {
  // Filter Buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('tab-active');
      });
      btn.classList.add('tab-active');
      
      activeFilter = btn.dataset.filter;
      const badge = document.getElementById('activeFilterBadge');
      if (badge) badge.textContent = btn.textContent.toUpperCase();
      renderMessageStream();
    });
  });

  // Auto-Scroll Toggle
  const btnToggleAutoScroll = document.getElementById('btnToggleAutoScroll');
  if (btnToggleAutoScroll) {
    btnToggleAutoScroll.addEventListener('click', () => {
      autoScrollEnabled = !autoScrollEnabled;
      const text = document.getElementById('autoScrollText');
      if (text) text.textContent = `SCROLL: ${autoScrollEnabled ? 'ON' : 'OFF'}`;
      if (autoScrollEnabled) {
        btnToggleAutoScroll.style.color = 'var(--text-primary)';
      } else {
        btnToggleAutoScroll.style.color = 'var(--text-subtle)';
      }
      showToast(`Auto-Scroll ${autoScrollEnabled ? 'Diaktifkan' : 'Dimatikan'}`, 'info');
    });
  }

  // Copy Bus Log
  const btnCopyBusLogs = document.getElementById('btnCopyBusLogs');
  if (btnCopyBusLogs) {
    btnCopyBusLogs.addEventListener('click', () => {
      const rawText = messagesState.map(m => `[${m.timestamp}] ${m.sender.toUpperCase()} -> ${m.target.toUpperCase()}:\n${m.content}`).join('\n\n---\n\n');
      navigator.clipboard.writeText(rawText).then(() => {
        showToast('Seluruh riwayat log disalin ke clipboard!', 'success');
      }).catch(err => {
        showToast('Gagal menyalin log: ' + err.message, 'error');
      });
    });
  }

  // Clear Chat Buffer
  const btnClearChat = document.getElementById('btnClearChat');
  if (btnClearChat) {
    btnClearChat.addEventListener('click', () => {
      messagesState = [];
      renderMessageStream();
      showToast('Buffer tampilan dibersihkan', 'info');
    });
  }

  // Real-time Trace Search
  const searchTraceInput = document.getElementById('searchTraceInput');
  if (searchTraceInput) {
    searchTraceInput.addEventListener('input', () => {
      renderMessageStream();
    });
  }

  // Command & Dispatch Console Bar
  const dispatchSelect = document.getElementById('dispatchTargetSelect');
  if (dispatchSelect) {
    dispatchSelect.addEventListener('change', updateDispatchTargetHint);
  }

  const btnDispatchSend = document.getElementById('btnDispatchSend');
  const dispatchInput = document.getElementById('dispatchPromptInput');

  if (btnDispatchSend) {
    btnDispatchSend.addEventListener('click', handleDispatchSubmit);
  }
  if (dispatchInput) {
    dispatchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleDispatchSubmit();
      }
    });
  }

  setupModals();
}

function updateDispatchTargetHint() {
  const select = document.getElementById('dispatchTargetSelect');
  const hint = document.getElementById('dispatchTargetHint');
  if (!select || !hint) return;
  const val = select.value;
  const hints = {
    all: 'Broadcast ke seluruh 11 spesialis',
    orchestrator: 'Lead Architect & Swarm Commander',
    frontend: 'UI/UX & Creative 3D WebGL',
    backend: 'Distributed Systems & Server API',
    api: 'Postman & 2,000+ Public APIs',
    database: 'DB Architect & Query Optimization',
    '3d': 'Blender 5.1 & Unity 6 Assets',
    gamedev: 'Unity 6 C# Gameplay Mechanics',
    security: 'AppSec & OWASP Audit',
    migration: 'Database Schema Evolution',
    integration: 'DevOps & Systems Integration',
    reviewer: 'Lead QA & Test Verification',
    researcher: 'Systems Technical Research',
    dev: 'Dev Team (Backend + Frontend + GameDev + API)',
    'api-team': 'API Team (API + Backend + Integration)',
    game: 'Game Team (GameDev + 3D)',
    data: 'Data Team (Database + Migration)',
    qa: 'QA Team (Reviewer + Security)',
    infra: 'Infra Team (Backend + DB + Migration + Integration)',
    creative: 'Creative Team (Frontend + 3D)'
  };
  hint.textContent = `Target: @${val.toUpperCase()} — ${hints[val] || ''}`;
}

async function handleDispatchSubmit() {
  const dispatchInput = document.getElementById('dispatchPromptInput');
  if (!dispatchInput) return;
  const prompt = dispatchInput.value.trim();
  if (!prompt) {
    showToast('Silakan masukkan prompt perintah.', 'error');
    dispatchInput.focus();
    return;
  }
  const target = document.getElementById('dispatchTargetSelect')?.value || 'backend';
  const btn = document.getElementById('btnDispatchSend');
  const btnText = document.getElementById('btnDispatchText');

  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = 'Mengirim...';

  try {
    const res = await fetch('/api/dispatch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        profile: target,
        prompt: prompt,
        sender: 'Dimas (Commander)',
        sync_blackboard: true
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Dispatch failed');
    }
    const data = await res.json();
    dispatchInput.value = '';
    const isBc = data.is_broadcast;
    showToast(isBc ? `Broadcast ke ${data.targets.length} agen dimulai!` : `Perintah terkirim ke @${target.toUpperCase()}!`, 'success');
  } catch (err) {
    showToast(`Gagal mengirim: ${err.message}`, 'error');
  } finally {
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = 'Kirim';
  }
}

function setupModals() {
  // Benchmark Modal
  const modalBench = document.getElementById('benchmarkModal');
  const btnOpenBench = document.getElementById('btnOpenBenchmark');
  const btnCloseBench = document.getElementById('btnCloseBenchmark');
  const btnStartBench = document.getElementById('btnStartBenchmark');

  if (btnOpenBench) btnOpenBench.addEventListener('click', () => modalBench.classList.remove('hidden'));
  if (btnCloseBench) btnCloseBench.addEventListener('click', () => modalBench.classList.add('hidden'));

  if (btnStartBench) {
    btnStartBench.addEventListener('click', async () => {
      const prompt = document.getElementById('benchmarkPrompt').value;
      const mode = document.querySelector('input[name="benchMode"]:checked').value;
      const spinner = document.getElementById('benchmarkSpinner');
      const statusText = document.getElementById('benchmarkStatusText');

      spinner.classList.remove('hidden');
      statusText.textContent = `Menguji ${AGENT_ORDER.length} agen (${mode})...`;

      try {
        await fetch('/api/benchmark', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt, mode })
        });
        showToast('Benchmark armada dimulai...', 'info');
      } catch (err) {
        showToast(`Gagal memulai: ${err.message}`, 'error');
        spinner.classList.add('hidden');
      }
    });
  }

  // Swarm Pipeline Modal
  const modalSwarm = document.getElementById('swarmModal');
  const btnOpenSwarm = document.getElementById('btnOpenSwarm');
  const btnCloseSwarm = document.getElementById('btnCloseSwarm');
  const btnStartSwarm = document.getElementById('btnStartSwarm');

  if (btnOpenSwarm) btnOpenSwarm.addEventListener('click', () => modalSwarm.classList.remove('hidden'));
  if (btnCloseSwarm) btnCloseSwarm.addEventListener('click', () => modalSwarm.classList.add('hidden'));

  document.querySelectorAll('.swarm-preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById('swarmGoalInput');
      if (input) input.value = btn.textContent.trim();
    });
  });

  if (btnStartSwarm) {
    btnStartSwarm.addEventListener('click', async () => {
      const goalInput = document.getElementById('swarmGoalInput');
      const goal = goalInput ? goalInput.value.trim() : '';
      if (!goal) {
        showToast('Goal swarm tidak boleh kosong', 'error');
        return;
      }
      const spinner = document.getElementById('swarmSpinner');
      const statusText = document.getElementById('swarmStageStatus');
      if (spinner) spinner.classList.remove('hidden');
      if (statusText) statusText.textContent = 'Tahap 1: Orchestrator Membedah Arsitektur...';

      // Reset step highlights
      ['stepOrchestrator', 'stepBackend', 'stepSecurity', 'stepReviewer'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
          el.style.borderColor = 'var(--border-default)';
          el.style.background = 'rgba(0,0,0,0.25)';
        }
      });
      const sOrch = document.getElementById('stepOrchestrator');
      if (sOrch) {
        sOrch.style.borderColor = 'var(--brand-violet)';
        sOrch.style.background = 'rgba(112, 126, 255, 0.1)';
      }

      try {
        const res = await fetch('/api/swarm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ goal: goal })
        });
        const data = await res.json();
        showToast(`Swarm '${goal.substring(0, 30)}...' diluncurkan!`, 'success');
      } catch (err) {
        showToast(`Gagal memulai swarm: ${err.message}`, 'error');
        if (spinner) spinner.classList.add('hidden');
      }
    });
  }

  // Obsidian Blackboard Modal
  const modalBlackboard = document.getElementById('blackboardModal');
  const btnOpenBlackboard = document.getElementById('btnOpenBlackboard');
  const btnCloseBlackboard = document.getElementById('btnCloseBlackboard');
  const btnSyncBlackboardModal = document.getElementById('btnSyncBlackboardModal');

  if (btnOpenBlackboard) {
    btnOpenBlackboard.addEventListener('click', async () => {
      modalBlackboard.classList.remove('hidden');
      await fetchBlackboardContent();
    });
  }
  if (btnCloseBlackboard) btnCloseBlackboard.addEventListener('click', () => modalBlackboard.classList.add('hidden'));

  if (btnSyncBlackboardModal) {
    btnSyncBlackboardModal.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/blackboard/sync', { method: 'POST' });
        const data = await res.json();
        showToast(`Berhasil sync ${data.messages_written} pesan ke Obsidian!`, 'success');
        await fetchBlackboardContent();
      } catch (err) {
        showToast(`Sync gagal: ${err.message}`, 'error');
      }
    });
  }
}

function handleSwarmStepUpdate(msg) {
  const content = msg.content || '';
  const statusText = document.getElementById('swarmStageStatus');
  const spinner = document.getElementById('swarmSpinner');
  const sOrch = document.getElementById('stepOrchestrator');
  const sBack = document.getElementById('stepBackend');
  const sSec = document.getElementById('stepSecurity');
  const sRev = document.getElementById('stepReviewer');

  if (msg.type === 'swarm_init') {
    if (spinner) spinner.classList.remove('hidden');
    if (statusText) statusText.textContent = 'Tahap 1: Orchestrator Memecah Arsitektur...';
    if (sOrch) {
      sOrch.style.borderColor = 'var(--brand-violet)';
      sOrch.style.background = 'rgba(112, 126, 255, 0.1)';
    }
  } else if (content.includes('TAHAP 1: ARSITEKTUR')) {
    if (sOrch) { sOrch.style.borderColor = 'var(--status-emerald)'; sOrch.style.background = 'var(--status-emerald-bg)'; }
    if (sBack) { sBack.style.borderColor = '#3b82f6'; sBack.style.background = 'rgba(59, 130, 246, 0.12)'; }
    if (statusText) statusText.textContent = 'Tahap 2: Backend Mengimplementasikan Kode...';
  } else if (content.includes('TAHAP 2: IMPLEMENTASI')) {
    if (sBack) { sBack.style.borderColor = 'var(--status-emerald)'; sBack.style.background = 'var(--status-emerald-bg)'; }
    if (sSec) { sSec.style.borderColor = 'var(--status-rose)'; sSec.style.background = 'var(--status-rose-bg)'; }
    if (statusText) statusText.textContent = 'Tahap 3: Security Mengaudit Keamanan & OWASP...';
  } else if (content.includes('TAHAP 3: AUDIT')) {
    if (sSec) { sSec.style.borderColor = 'var(--status-emerald)'; sSec.style.background = 'var(--status-emerald-bg)'; }
    if (sRev) { sRev.style.borderColor = 'var(--status-emerald)'; sRev.style.background = 'rgba(16, 185, 129, 0.15)'; }
    if (statusText) statusText.textContent = 'Tahap 4: Reviewer Memvalidasi Test Suite...';
  } else if (content.includes('TAHAP 4: QA') || msg.type === 'swarm_done') {
    if (sRev) { sRev.style.borderColor = 'var(--status-emerald)'; sRev.style.background = 'var(--status-emerald-bg)'; }
    if (spinner) spinner.classList.add('hidden');
    if (statusText) statusText.textContent = '🎯 Swarm Pipeline Berhasil Selesai!';
  }
}

async function fetchBlackboardContent() {
  const contentArea = document.getElementById('blackboardContentArea');
  contentArea.textContent = 'Memuat isi Blackboard dari Obsidian vault...';
  try {
    const res = await fetch('/api/blackboard');
    const data = await res.json();
    contentArea.textContent = data.content;
  } catch (err) {
    contentArea.textContent = `Error memuat blackboard: ${err.message}`;
  }
}

function updateBenchmarkUI(benchmark) {
  const tbody = document.getElementById('benchmarkTableBody');
  const spinner = document.getElementById('benchmarkSpinner');
  const statusText = document.getElementById('benchmarkStatusText');

  if (benchmark.status === 'completed') {
    if (spinner) spinner.classList.add('hidden');
    if (statusText) statusText.textContent = `Selesai (${benchmark.summary.avg_latency_ms} ms avg)`;
  }

  if (!benchmark.results || Object.keys(benchmark.results).length === 0) return;

  const sorted = Object.values(benchmark.results).sort((a, b) => {
    if (!a.success) return 1;
    if (!b.success) return -1;
    return a.latency_ms - b.latency_ms;
  });

  tbody.innerHTML = sorted.map((r, idx) => {
    const statusPill = r.success 
      ? '<span style="color: var(--status-emerald); font-weight: 600;">PASS (0)</span>'
      : '<span style="color: var(--status-rose); font-weight: 600;">FAIL</span>';

    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-muted); width: 50px;">#${idx + 1}</td>
        <td style="font-weight: 600; color: var(--text-primary);">${r.profile.toUpperCase()}</td>
        <td style="text-align: right; color: var(--status-sky);" class="tabular-nums">${r.latency_ms} ms</td>
        <td style="text-align: center; width: 65px;">${statusPill}</td>
      </tr>
    `;
  }).join('');
}

// -------------------------------------------------------------
// Toast Notifications
// -------------------------------------------------------------
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  const dotColor = type === 'success' ? 'var(--status-emerald)' : (type === 'error' ? 'var(--status-rose)' : 'var(--brand-violet)');

  toast.className = 'linear-toast';
  toast.innerHTML = `
    <span class="status-dot" style="background: ${dotColor};"></span>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(4px)';
    setTimeout(() => toast.remove(), 250);
  }, 3200);
}

// -------------------------------------------------------------
// Initial Data Fetch & Helpers
// -------------------------------------------------------------
async function loadInitialData() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    console.log('Engine Telemetry Connected:', data);
    // Apply initial view setup
    switchView(currentView);
  } catch (err) {
    console.warn('Initial fetch warning:', err);
  }
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

function toggleConsole() {
  consoleExpanded = !consoleExpanded;
  const body = document.getElementById('dispatchConsoleBody');
  const icon = document.getElementById('consoleToggleIcon');
  const label = document.getElementById('consoleToggleLabel');
  if (consoleExpanded) {
    if (body) body.style.display = 'flex';
    if (icon) icon.style.transform = 'rotate(0deg)';
    if (label) label.textContent = 'ACP COMMAND CONSOLE';
  } else {
    if (body) body.style.display = 'none';
    if (icon) icon.style.transform = 'rotate(180deg)';
    if (label) label.textContent = 'ACP COMMAND CONSOLE (MINIMIZED)';
  }
}
window.toggleConsole = toggleConsole;

// View Switcher & Layout Controls
let currentView = 'trace';
let layoutMode = window.innerWidth >= 1100 ? 'split' : 'tabbed';

function switchView(viewName) {
  currentView = viewName;
  const sidebar = document.querySelector('.linear-sidebar');
  const mainView = document.querySelector('.linear-main-view');
  const btnFleet = document.getElementById('viewBtnFleet');
  const btnTrace = document.getElementById('viewBtnTrace');

  if (layoutMode === 'tabbed') {
    if (viewName === 'fleet') {
      if (sidebar) sidebar.style.display = 'flex';
      if (mainView) mainView.style.display = 'none';
      btnFleet?.classList.add('active');
      btnTrace?.classList.remove('active');
      setTimeout(() => updateCharts(), 50);
    } else {
      if (sidebar) sidebar.style.display = 'none';
      if (mainView) mainView.style.display = 'flex';
      btnTrace?.classList.add('active');
      btnFleet?.classList.remove('active');
    }
  } else {
    // Split mode: both visible
    if (sidebar) sidebar.style.display = 'flex';
    if (mainView) mainView.style.display = 'flex';
    if (viewName === 'fleet') {
      btnFleet?.classList.add('active');
      btnTrace?.classList.remove('active');
    } else {
      btnTrace?.classList.add('active');
      btnFleet?.classList.remove('active');
    }
  }
  initLucide();
}

function toggleLayoutMode() {
  const ws = document.querySelector('.linear-workspace');
  const btnText = document.getElementById('layoutModeText');
  const sidebar = document.querySelector('.linear-sidebar');
  const mainView = document.querySelector('.linear-main-view');

  if (layoutMode === 'tabbed') {
    layoutMode = 'split';
    ws?.classList.remove('mode-tabbed');
    ws?.classList.add('mode-split');
    if (sidebar) sidebar.style.display = 'flex';
    if (mainView) mainView.style.display = 'flex';
    if (btnText) btnText.textContent = 'Tabbed View';
  } else {
    layoutMode = 'tabbed';
    ws?.classList.remove('mode-split');
    ws?.classList.add('mode-tabbed');
    if (btnText) btnText.textContent = 'Split View';
    switchView(currentView);
  }
  setTimeout(() => updateCharts(), 100);
}

window.switchView = switchView;
window.toggleLayoutMode = toggleLayoutMode;
