let fullTreeData = null;
let selectedFilePath = null;
let originalContent = '';
let selectedFolder = null;

// Initialize CodeMirror (if not already done elsewhere)
let codeMirrorEditor;
document.addEventListener('DOMContentLoaded', () => {
    const isDark = document.documentElement.dataset.theme === 'dark';
    codeMirrorEditor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
        lineNumbers: true,
        theme: document.documentElement.dataset.theme === 'dark' ? 'material' : 'default',
        mode: 'plaintext',
        lineWrapping: true,
        theme: isDark ? 'material' : 'default'
    });
    codeMirrorEditor.setSize("100%", "100%");
    setupToolbar();
    fetchTreeAndRender();
    setupPlayButton();  

    codeMirrorEditor.on('change', () => {
        updateEditorButtons();
    });
});

async function fetchTreeAndRender() {
    const res = await fetch('/appsrc');
    fullTreeData = await res.json();

    populateFolderFilter(fullTreeData);
}

function populateFolderFilter(treeRoot) {
    const filter = document.getElementById('folderFilter');
    const playBtn = document.getElementById('btnPlay');
    if (!filter || !playBtn) return;

    const appFolders = treeRoot.children?.filter(c => c.type === 'directory') || [];

    // Reset options
    filter.innerHTML = `<option value="__all__">All pipelines</option>`;
    appFolders.forEach(folder => {
        const opt = document.createElement('option');
        opt.value = folder.name;
        opt.textContent = folder.name;
        filter.appendChild(opt);
    });

    // Try to restore last selected folder from localStorage
    const savedFolder = localStorage.getItem('selectedFolder');
    const isValid = appFolders.some(f => f.name === savedFolder);
    if (savedFolder && isValid) {
        filter.value = savedFolder;
        playBtn.disabled = false;

        selectedFolder = fullTreeData.children.find(c => c.name === savedFolder);
        if (selectedFolder) {
            renderTree(selectedFolder);
            selectManifestJson(selectedFolder);
            filter.dispatchEvent(new Event('change')); 
        }
    } else {
        filter.value = '__all__';
        playBtn.disabled = true;
        filter.dispatchEvent(new Event('change'));
        renderTree(fullTreeData);
    }

    // On dropdown change
    filter.addEventListener('change', () => {
        const selected = filter.value;
        localStorage.setItem('selectedFolder', selected);
        playBtn.disabled = selected === '__all__';

        if (selected === '__all__') {
            renderTree(fullTreeData);
        } else {
            const selectedFolder = fullTreeData.children.find(c => c.name === selected && c.type === 'directory');
            if (selectedFolder) {
                renderTree(selectedFolder);
                selectManifestJson(selectedFolder);
            }
        }
    });
}

// Helper to auto-select manifest.json if it exists
function selectManifestJson(folderNode) {
    if (!folderNode?.children) return;

    const manifest = folderNode.children.find(child => child.name === 'manifest.json');
    if (!manifest) return;

    const li = document.querySelector(`li[data-path="${manifest.path}"]`);
    if (li) li.click(); // simulate file selection
}


function renderTree(tree) {
    const container = document.getElementById('fileTree');
    container.innerHTML = buildTreeHTML(tree);
  
    container.querySelectorAll('li[data-type="file"]').forEach(li => {
      li.addEventListener('click', async () => {
        container.querySelectorAll('li[data-type="file"]').forEach(l => l.removeAttribute('data-selected'));
        li.setAttribute('data-selected', 'true');
        selectedFilePath = li.dataset.path;
  
        const res = await fetch(`/readfile?path=${encodeURIComponent(selectedFilePath)}`);
        const text = await res.text();
        const mode = getModeFromExtension(selectedFilePath);
        codeMirrorEditor.setOption("mode", mode);
        codeMirrorEditor.setValue(text);
        // Attempt to parse JSON and detect `gst` with `--gst-string`
        let gstEditButton = document.getElementById('btnGstEdit');
        if (gstEditButton) {
            try {
                const json = JSON.parse(text);
                const applications = json?.applications || [];
        
                let foundGstString = false;
        
                for (const app of applications) {
                    const pipelines = app?.pipelines || [];
                    for (const pipeline of pipelines) {
                        const gst = pipeline?.gst;
                        if (typeof gst === 'string' && gst.includes('--gst-string=')) {
                            // ✅ Found gst-string
                            const match = gst.match(/--gst-string="([^"]+)"/);
                            if (match && match[1]) {
                                console.log("📦 Found --gst-string:\n", match[1]);
                            } else {
                                console.log("⚠️ Found gst entry but could not extract --gst-string");
                            }
                            foundGstString = true;
                            break;
                        }
                    }
                    if (foundGstString) break;
                }
        
                gstEditButton.disabled = !foundGstString;
            } catch (e) {
                console.warn("JSON parsing failed or invalid structure:", e);
                gstEditButton.disabled = true;
            }
        }       
        originalContent = text;
        updateEditorButtons();
      });
    });
}
  

function buildTreeHTML(node) {
    if (node.type === 'file') {
        return `<li data-type="file" data-path="${node.path}">${node.name}</li>`;
    }

    let childrenHTML = '';
    if (node.children && node.children.length > 0) {
        childrenHTML = `<ul>${node.children.map(buildTreeHTML).join('')}</ul>`;
    }

    return `
    <li>
      <strong>${node.name}</strong>
      ${childrenHTML}
    </li>
  `;
}

function getModeFromExtension(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    switch (ext) {
        case 'py': return 'python';
        case 'js': return 'javascript';
        case 'json': return 'application/json';
        case 'html': return 'htmlmixed';
        case 'css': return 'css';
        case 'cpp': case 'cc': return 'text/x-c++src';
        case 'c': return 'text/x-csrc';
        case 'sh': return 'shell';
        case 'md': return 'markdown';
        default: return 'plaintext';
    }
}

async function saveFile() {
  if (!selectedFilePath) {
    showToast("⚠️ No file selected.", 4000);
    return;
  }

  const content = codeMirrorEditor.getValue();

  try {
    const res = await fetch('/writefile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: selectedFilePath, content })
    });

    if (res.ok) {
      originalContent = content;              // mark as clean
      updateEditorButtons();                  // disable buttons
      showToast('✅ File saved successfully');
    } else {
      const err = await res.text();
      showToast(`❌ Save failed: ${err}`, 5000);
    }
  } catch (err) {
    console.error("Save error:", err);
    showToast('❌ Save failed: Network error', 5000);
  }
}


// === Toolbar functionality ===
function setupToolbar() {
    document.getElementById('btnUndo').addEventListener('click', () => {
        codeMirrorEditor.undo();
    });

    document.getElementById('btnRedo').addEventListener('click', () => {
        codeMirrorEditor.redo();
    });

    document.getElementById('btnUpload').addEventListener('click', () => {
        showUploadDialog({
          title: 'Upload a pipeline package built with Palette or Edgematic',
          accept: '.mpk',
          uploadUrl: '/upload/mpk'
        });
      });

      document.getElementById('btnSave').addEventListener('click', saveFile);
}

function setupPlayButton() {
  const btnPlay = document.getElementById('btnPlay');
  const rocketIcon = document.getElementById('rocketIcon');
  if (!btnPlay || !rocketIcon) {
    console.warn('btnPlay or rocketIcon not found');
    return;
  }

  btnPlay.addEventListener('click', async () => {
    const folder = document.getElementById('folderFilter').value;
    if (folder === '__all__') return;

    const isCurrentlyRunning = btnPlay.classList.contains('running');

    try {
      if (!isCurrentlyRunning) {
        // Clear logs on start
        ['gst_app', 'EV74', 'syslog'].forEach(id => {
          const el = document.getElementById(`logOutput-${id}`);
          if (el) el.textContent = '';
        });
      }

      const gstDebug = localStorage.getItem('gst_debug');

      // Reset the log display
      if (!isCurrentlyRunning) {
        document.getElementById('logOutput-gst_app').innerHTML = '';
        document.getElementById('logOutput-EV74').textContent = '';
        document.getElementById('logOutput-syslog').textContent = '';
      }

      const res = await fetch(isCurrentlyRunning ? `/stop` : `/start/${folder}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: isCurrentlyRunning
          ? null
          : JSON.stringify({
              gst_debug: gstDebug
            })
      });

      if (!res.ok) {
        const msg = await res.text();
        console.warn('Start/Stop failed:', msg);
        return;
      }

      // Always show the log panel
      showLogPanel();

      if (!isCurrentlyRunning) {
        showToast("✅ Requested to start application.", 2000);
        stopLogPolling();
      } else {
        showToast("✅ Requested to stop application.", 2000);
        startLogPolling();
      }

    } catch (err) {
      console.error('Start/Stop error:', err);
    }
  });
}

function showLogPanel() {
    document.getElementById('logOverlay').classList.remove('hidden');
    startLogPolling();
}


function hideLogPanel() {
    document.getElementById('logOverlay').style.display = 'none';
    stopLogPolling();
}

function startLogPolling() {
    if (logInterval) return;
    logInterval = setInterval(fetchLogs, 2000);
}

function stopLogPolling() {
    if (logInterval) {
        clearInterval(logInterval);
        logInterval = null;
    }
}

async function fetchLogs() {
  try {
    const ts = Date.now(); // cache-busting timestamp

    const gstRes = await fetch(`/gstlogs?folder=${encodeURIComponent(selectedFolder.name)}&ts=${ts}`);
    const evRes = await fetch(`/logs/EV74?ts=${ts}`);
    const sysRes = await fetch(`/logs/syslog?ts=${ts}`);

    const gstText = await gstRes.text();
    const evText = await evRes.text();
    const sysText = await sysRes.text();

    const ansiUp = new AnsiUp();

    document.getElementById('logOutput-gst_app').innerHTML = ansiUp.ansi_to_html(gstText);
    document.getElementById('logOutput-EV74').textContent = evText;
    document.getElementById('logOutput-syslog').textContent = sysText;
  } catch (err) {
    console.error("Log fetch error:", err);
  }
}


const resizer = document.querySelector('.log-resizer');
const logOverlay = document.querySelector('.log-overlay');

let isDragging = false;
resizer?.addEventListener('mousedown', () => isDragging = true);
document.addEventListener('mouseup', () => isDragging = false);

document.addEventListener('mousemove', (e) => {
  if (!isDragging || logOverlay?.classList.contains('minimized')) return;

  const minHeight = 100;
  const bottomToolbarHeight = 80; // Adjust to match actual toolbar height
  const maxHeight = window.innerHeight - bottomToolbarHeight;

  let newHeight = window.innerHeight - e.clientY;
  newHeight = Math.max(minHeight, Math.min(maxHeight, newHeight));

  logOverlay.style.height = `${newHeight}px`;
});


document.querySelectorAll('.log-tab').forEach(button => {
  button.addEventListener('click', () => {
    const target = button.getAttribute('data-log');

    // Deactivate all tabs and outputs
    document.querySelectorAll('.log-tab').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.log-output').forEach(out => out.classList.remove('active'));

    // Activate selected
    button.classList.add('active');
    document.getElementById(`logOutput-${target}`).classList.add('active');
  });
});


let isMinimized = false;
let previousHeight = '30%'; // Default starting height

const overlay = document.getElementById('logOverlay');
const logContent = document.getElementById('logContent');
const btnToggleLogs = document.getElementById('btnToggleLogs');

// Restore on click anywhere in minimized bar
overlay.addEventListener('click', () => {
    if (isMinimized) {
        overlay.classList.remove('minimized');
        overlay.style.height = previousHeight;
        isMinimized = false;
        btnToggleLogs.textContent = '🗕';
    }
});

const restoreBtn = document.getElementById('btnRestoreLogs');

function minimizeLogOverlay() {
    overlay.classList.add('minimized');
    isMinimized = true;
    restoreBtn.style.display = 'block';
}

function restoreLogOverlay() {
    overlay.classList.remove('minimized');
    overlay.style.height = previousHeight;
    isMinimized = false;
    restoreBtn.style.display = 'none';
    btnToggleLogsIcon.src = "/static/icons/minimize.png";
}

btnToggleLogs.addEventListener('click', (e) => {
    e.stopPropagation();
    if (!isMinimized) {
        previousHeight = overlay.style.height || '30%';
        minimizeLogOverlay();
    } else {
        restoreLogOverlay();
    }
});

restoreBtn.addEventListener('click', restoreLogOverlay);

function updateEditorButtons() {
    const current = codeMirrorEditor.getValue();
    const isDirty = current !== originalContent;

    const btnSave = document.getElementById('btnSave');
    const btnUndo = document.getElementById('btnUndo');
    const btnRedo = document.getElementById('btnRedo');

    btnSave.disabled = !isDirty;
    btnUndo.disabled = !codeMirrorEditor.historySize().undo;
    btnRedo.disabled = !codeMirrorEditor.historySize().redo;
}