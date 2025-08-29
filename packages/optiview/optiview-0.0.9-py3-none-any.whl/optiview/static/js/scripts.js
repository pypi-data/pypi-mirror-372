window.jsonlint = jsonlint;
const modeToggleBtn = document.getElementById('modeToggleBtn');
const modeToggleIcon = document.getElementById('modeToggleIcon');

function toggleMode() {
    const html = document.documentElement;
    const newTheme = html.dataset.theme === 'dark' ? 'light' : 'dark';
    html.dataset.theme = newTheme;
    document.getElementById('modeToggleIcon').src = newTheme === 'dark'
      ? '/static/icons/brightmode.png'
      : '/static/icons/darkmode.png';
  
    // 🔄 Sync CodeMirror theme
    if (window.codeMirrorEditor) {
      const cmTheme = newTheme === 'dark' ? 'material' : 'default';
      codeMirrorEditor.setOption('theme', cmTheme);
    }
  }
  

modeToggleBtn.addEventListener('click', toggleMode);

async function fetchApps() {
    const select = document.getElementById('appSelect');
    if (!select) return;  // prevent error if the element doesn't exist
  
    const res = await fetch('/apps');
    const data = await res.json();
    data.apps.forEach(app => {
      const option = document.createElement('option');
      option.value = app;
      option.textContent = app;
      select.appendChild(option);
    });
  }
  

let isRunning = false;
let logInterval = null;
let metricInterval = null;

async function startPipeline() {
  const app = document.getElementById('appSelect').value;
  if (!app) return;
  await fetch(`/start/${app}`, { method: 'POST' });
  isRunning = true;
  document.getElementById('startBtn').textContent = '■ Stop Pipeline';
  logInterval = setInterval(fetchLogs, 2000);
}

function stopPipeline() {
  fetch('/stop', { method: 'POST' });
  isRunning = false;
  document.getElementById('startBtn').textContent = '▶ Start Pipeline';
  if (logInterval) clearInterval(logInterval);
}

async function fetchLogs() {
  const res = await fetch('/logs');
  const text = await res.text();
  document.getElementById('logOutput').value = text;
}

let logPollingActive = false;

async function fetchMetrics() {
  const res = await fetch('/metrics');
  const data = await res.json();

  const cpu = data.cpu_load !== undefined ? data.cpu_load + '%' : '--%';
  const mem = data.memory?.percent !== undefined ? data.memory.percent + '%' : '--%';
  const mla = data.mla_allocated_bytes
    ? (data.mla_allocated_bytes / (1024 * 1024)).toFixed(2) + ' MB'
    : '--';
  const storage = data.disk?.percent !== undefined ? data.disk.percent + '%' : '--%';
  const temp = (typeof data.temperature_celsius_avg === 'number')
  ? `${data.temperature_celsius_avg.toFixed(1)}°C`
  : '--°C';

  document.getElementById('cpuStatus').textContent = 'CPU: ' + cpu;
  document.getElementById('ramStatus').textContent = 'RAM: ' + mem;
  document.getElementById('mlaStatus').textContent = 'MLA: ' + mla;

  let storageStatusEl = document.getElementById('storageStatus');
  if (!storageStatusEl) {
    storageStatusEl = document.createElement('span');
    storageStatusEl.id = 'storageStatus';
    document.querySelector('.status')?.appendChild(storageStatusEl);
  }
  storageStatusEl.textContent = 'Storage: ' + storage;

  let tempStatusEl = document.getElementById('tempStatus');
  if (!tempStatusEl) {
    tempStatusEl = document.createElement('span');
    tempStatusEl.id = 'tempStatus';
    document.querySelector('.status')?.appendChild(tempStatusEl);
  }
  tempStatusEl.textContent = 'Temp: ' + temp;

  const btnPlay = document.getElementById('btnPlay');
  const rocketIcon = document.getElementById('rocketIcon');
  const isRunning = data?.pipeline_status?.is_running;

  if (btnPlay && rocketIcon) {
    if (isRunning) {
      btnPlay.classList.add('running');
      rocketIcon.classList.add('rocket-fly');
      btnPlay.title = 'Click to stop';

      showLogPanel();

      if (!logPollingActive) {
        startLogPolling();
        logPollingActive = true;
      }

    } else {
      btnPlay.classList.remove('running');
      rocketIcon.classList.remove('rocket-fly');
      btnPlay.title = 'Start selected app';

      if (logPollingActive) {
        stopLogPolling();
        logPollingActive = false;
      }
    }
  }
}

async function fetchBuildInfo() {
  try {
    const res = await fetch('/buildinfo');
    const data = await res.json();

    let label = ''
    if (data.REMOTE === true) {
      label = " 🌐 ";
    }
    label += `Board: ${data.MACHINE} (${data.SIMA_BUILD_VERSION})`;
    document.getElementById('boardVersion').textContent = label;
  } catch (err) {
    document.getElementById('boardVersion').textContent = 'Board: N/A';
  }
}


document.getElementById('startBtn')?.addEventListener('click', () => {
  if (isRunning) stopPipeline();
  else startPipeline();
});

fetchApps();
fetchMetrics();
fetchBuildInfo();
metricInterval = setInterval(fetchMetrics, 2000);

const tabButtons = document.querySelectorAll('.tabs button');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
  button.addEventListener('click', () => {
    const tabId = button.getAttribute('data-tab');
    localStorage.setItem('lastSelectedTab', tabId);  // 💾 Save tab ID

    const tabElement = document.getElementById(tabId);
    if (!tabElement) {
      console.warn(`Tab element with ID ${tabId} not found.`);
      return;
    }

    tabButtons.forEach(b => b.classList.remove('active'));
    tabContents.forEach(tc => tc.style.display = 'none');

    button.classList.add('active');
    tabElement.style.display = 'block';

    const mode = document.documentElement.getAttribute('data-theme') || 'dark';

    if (tabId === 'monitorTab') {
      const iframe = document.getElementById('monitorIframe');
      const newSrc = `https://${location.hostname}:8081?mode=${mode}`;
      if (iframe) {
        const currentUrl = new URL(iframe.src, window.location.href).toString();
        const targetUrl = new URL(newSrc, window.location.href).toString();
      
        if (currentUrl !== targetUrl) {
          iframe.src = newSrc;
        }
      }
    } else if (tabId === 'settingsTab') {
      const panel = document.getElementById('settings-panel');
      if (panel && panel.style.display !== 'block') {
        panel.style.display = 'block';
      }
    } else {
      const panel = document.getElementById('settings-panel');
      if (panel) panel.style.display = 'none';
    }
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const savedTabId = localStorage.getItem('lastSelectedTab');
  if (savedTabId) {
    const savedButton = document.querySelector(`.tabs button[data-tab="${savedTabId}"]`);
    if (savedButton) savedButton.click();
  } else {
    // fallback: click the first tab
    const firstTab = document.querySelector('.tabs button[data-tab]');
    if (firstTab) firstTab.click();
  }
});



