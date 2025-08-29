let currentPopupPreviewPath = null;

showSettingsPopup = () => {
    document.getElementById('settingsPopupOverlay').classList.remove('hidden');
    loadPopupMediaFileTree();

    updateHelpText('popup-media-files');
    // ✅ Restore saved GStreamer debug level
    const savedDebugLevel = localStorage.getItem('gst_debug');
    if (savedDebugLevel !== null) {
      const dropdown = document.getElementById('gstDebugLevel');
      if (dropdown) {
        dropdown.value = savedDebugLevel;
      }
    }
  }

document.addEventListener('DOMContentLoaded', () => {
  const btnOpen = document.getElementById('btnSettingsPopup');
  const btnClose = document.getElementById('settingsPopupClose');

  fetch('/envinfo')
    .then(res => res.json())
    .then(env => {
      if (!env.is_sima_board && !env.is_remote_devkit_configured) {
        showSettingsPopup();
        showSettingsTab('popup-remote-devkit');
      }
    })
    .catch(err => console.error('Failed to fetch env info:', err));

  btnOpen.addEventListener('click', () => {
    showSettingsPopup();
  });

  btnClose.addEventListener('click', () => {
    document.getElementById('settingsPopupOverlay').classList.add('hidden');
  });

  // Attach click handlers to all settings tab buttons
  document.querySelectorAll('.settings-tab-link').forEach(button => {
    button.addEventListener('click', () => {
      const tabId = button.getAttribute('data-tab');
      showSettingsTab(tabId);
    });
  });

  // Central tab-switching function
  function showSettingsTab(tabId) {
    // Deactivate all tabs and sections
    document.querySelectorAll('.settings-tab-link').forEach(btn =>
      btn.classList.remove('active')
    );
    document.querySelectorAll('.settings-tab-section').forEach(section =>
      section.classList.remove('active')
    );

    // Activate the selected tab and its section
    document.querySelector(`.settings-tab-link[data-tab="${tabId}"]`)?.classList.add('active');
    document.getElementById(tabId)?.classList.add('active');

    // Trigger tab-specific logic
    switch (tabId) {
      case 'popup-media-files':
        loadPopupMediaFileTree();
        break;
      case 'popup-media-sources':
        loadPopupMediaSources();
        break;
      case 'popup-remote-devkit':
        loadRemoteDevkitConfig();
        break;
    }
  }

  // ✅ Save debug level on change and toast
  const debugDropdown = document.getElementById('gstDebugLevel');
  if (debugDropdown) {
    debugDropdown.addEventListener('change', (e) => {
      const value = e.target.value;
      localStorage.setItem('gst_debug', value);
      showToast(`✅ GStreamer debug level saved: ${value}`);
    });
  }
});

function loadPopupMediaFileTree() {
    const tree = document.getElementById('popupMediaFileTree');
    if (!tree) return;
  
    fetch('/api/media-files')
      .then(res => res.json())
      .then(data => {
        if (!data || data.length === 0) {
          tree.innerHTML = `
            <div class="empty-media-message">
              <button id="popupUploadMediaBtn" class="image-upload-btn">
                <img src="/static/icons/upload.png" alt="Upload" />
              </button>
              <p>No media files found in <code>/data/simaai/optiview/media</code>.</p>
            </div>
          `;
          document.getElementById('popupUploadMediaBtn').onclick = () => {
            showUploadDialog({
              title: 'Upload media (.mp4, .jpg, .zip)',
              accept: '.mp4,.jpg,.jpeg,.png,.zip',
              uploadUrl: '/upload/media',
              onSuccess: () => loadPopupMediaFileTree()
            });
          };
        } else {
          tree.innerHTML = renderPopupFileTree(data);
  
          // Auto-preview the first file if available
          const fileNodes = tree.querySelectorAll('li[data-type="file"]');
          if (fileNodes.length > 0) {
            const firstFilePath = fileNodes[0].getAttribute('data-path');
            previewPopupMediaFile(firstFilePath);
          }
        }
      })
      .catch(err => {
        tree.textContent = '❌ Failed to load media files.';
        console.error(err);
      });
  }
  

function renderPopupFileTree(tree) {
  function renderNode(node) {
    if (node.type === 'folder') {
      return `
        <li data-type="folder" data-path="${node.path}">
          <strong>${node.name}</strong>
          <ul>
            ${(node.children || []).map(renderNode).join('')}
          </ul>
        </li>
      `;
    } else {
      return `
        <li data-type="file" data-path="${node.path}" onclick="previewPopupMediaFile('${node.path}')">
          ${node.name}
        </li>
      `;
    }
  }
  return `<ul>${tree.map(renderNode).join('')}</ul>`;
}

function previewPopupMediaFile(path) {
    const preview = document.getElementById('popupPreviewContent');
    const actionBar = document.getElementById('popupPreviewActions');
    if (!preview || !actionBar) return;
  
    // Highlight selected file
    document.querySelectorAll('#popupMediaFileTree li[data-type="file"]').forEach(li => {
      li.removeAttribute('data-selected');
    });
    const selectedLi = document.querySelector(`#popupMediaFileTree li[data-path="${CSS.escape(path)}"]`);
    if (selectedLi) selectedLi.setAttribute('data-selected', 'true');
  
    currentPopupPreviewPath = path;
    preview.innerHTML = '';
    actionBar.classList.add('hidden');
  
    if (path.toLowerCase().endsWith('.mp4')) {
      preview.innerHTML = `<video controls src="/media/${path}" width="100%"></video>`;
      actionBar.classList.remove('hidden');
    } else if (/\.(jpg|jpeg|png)$/i.test(path)) {
      preview.innerHTML = `<img src="/media/${path}" alt="Preview" style="max-width: 100%" />`;
      actionBar.classList.remove('hidden');
    } else {
      preview.textContent = '📁 File type not previewable';
    }
  
    document.getElementById('popupPreviewDeleteBtn').onclick = () => {
      if (!confirm(`Delete ${path}?`)) return;
  
      fetch('/api/delete-media', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
      }).then(res => {
        if (res.ok) {
          loadPopupMediaFileTree();
          preview.innerHTML = '';
          actionBar.classList.add('hidden');
        } else {
          alert('❌ Failed to delete file.');
        }
      });
    };
  

  document.getElementById('popupPreviewInfoBtn').onclick = async () => {
    try {
      const res = await fetch('/api/media-info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
      });

      if (!res.ok) throw new Error(`Server error: ${res.statusText}`);

      const info = await res.json();
      const tbody = document.getElementById('infoPopupTableBody');
      tbody.innerHTML = '';

      for (const [key, value] of Object.entries(info)) {
        const row = document.createElement('tr');

        const labelCell = document.createElement('td');
        labelCell.className = 'info-label';
        labelCell.textContent = key;

        const valueCell = document.createElement('td');
        valueCell.className = 'info-value';
        valueCell.textContent = value;

        row.appendChild(labelCell);
        row.appendChild(valueCell);
        tbody.appendChild(row);
      }

      document.getElementById('infoOverlay').classList.remove('hidden');
    } catch (err) {
      alert(`Failed to load media info:\n${err.message}`);
    }
  };

  document.getElementById('popupPreviewAssignBtn').onclick = () => {
    const popup = document.getElementById('assign-src-popup');
    const select = document.getElementById('assign-source-select');

    selectedFileToAssign = path;
    select.value = '';
    popup.classList.remove('hidden');
  };
}

// Info popup close
if (document.getElementById('infoPopupClose')) {
  document.getElementById('infoPopupClose').onclick = () => {
    document.getElementById('infoOverlay').classList.add('hidden');
  };
}

function loadPopupMediaSources() {
  const container = document.getElementById('popup-media-source-rows');
  if (!container) return;

  container.innerHTML = '';

  if (typeof renderMediaSources === 'function') {
    renderMediaSources('popup-media-source-rows'); 
  } else {
    console.warn('renderMediaSources() not defined — make sure mediasrc.js is loaded.');
  }
}

const helpTextMap = {
    'popup-media-files': 'Browse and manage your uploaded media files.',
    'popup-media-sources': 'Media sources are used for RTSP streaming to feed into the ML pipeline. Click on the number icon to copy the RTSP URL.',
    'popup-launch-options': 'Configure launch options for your ML pipline',
    'popup-remote-devkit': 'Connect to a remote DevKit device for debugging'
  };
  
async function updateHelpText(tabId) {
  let helpMessage = helpTextMap[tabId] || 'Select a tab to get started.';

  if (tabId === 'popup-media-files') {
    try {
      const res = await fetch('/system/tools');
      const tools = await res.json();
      const missing = [];
      if (!tools.ffmpeg) missing.push('FFMPEG');
      if (!tools.gstreamer) missing.push('GStreamer');

      if (missing.length > 0) {
        helpMessage += ` Please install ${missing.join(' and ')} on your OptiView machine.`;
      }
    } catch (err) {
      console.warn('Failed to check system tools:', err);
    }
  }

  document.getElementById('settingsPopupHelpText').textContent = helpMessage;
}

document.querySelectorAll('.settings-tab-link').forEach(button => {
  button.addEventListener('click', async () => {
    const tabId = button.getAttribute('data-tab');

    document.querySelectorAll('.settings-tab-link').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.settings-tab-section').forEach(section => section.classList.remove('active'));

    button.classList.add('active');
    document.getElementById(tabId).classList.add('active');

    if (tabId === 'popup-media-files') {
      loadPopupMediaFileTree();
    } else if (tabId === 'popup-media-sources') {
      loadPopupMediaSources();
    }

    await updateHelpText(tabId);  // <- now shared
  });
});



document.getElementById('popupPreviewUploadBtn').onclick = () => {
    showUploadDialog({
      title: 'Upload media (.mp4, .jpg, .zip)',
      accept: '.mp4,.jpg,.jpeg,.png,.zip',
      uploadUrl: '/upload/media',
      onSuccess: () => {
        loadPopupMediaFileTree();
      }
    });
  };

document.getElementById('testSaveBtn').addEventListener('click', async function () {
  const ip = document.getElementById('devkitIp').value.trim();
  const password = document.getElementById('rootPassword').value;

  if (!ip || !password) {
    showToast("⚠️ Please enter both IP address and root password.");
    return;
  }

  try {
    const response = await fetch('/remotedevkit/cfg', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ip, rootPassword: password })
    });

    const result = await response.json();

    if (response.ok) {
      showToast("✅ Configuration saved and test passed, refresh page to see remote devkit projects.");
    } else {
      showToast("❌ " + (result.message || "Failed to save configuration."));
    }

  } catch (error) {
    console.error('Test & Save failed:', error);
    showToast("❌ Network or server error occurred.");
  }
});

document.getElementById('clearSaveBtn').addEventListener('click', async function () {
  const ipInput = document.getElementById('devkitIp');
  const passwordInput = document.getElementById('rootPassword');

  // Set values
  ipInput.value = '127.0.0.1';
  passwordInput.value = '';

  try {
    const response = await fetch('/remotedevkit/cfg', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ip: '127.0.0.1', rootPassword: '' })
    });

    const result = await response.json();

    if (response.ok) {
      showToast("✅ Configuration reset to localhost.");
    } else {
      showToast("❌ " + (result.message || "Failed to reset configuration."));
    }
  } catch (error) {
    console.error('Clear & Save failed:', error);
    showToast("❌ Network or server error occurred.");
  }
});

async function loadRemoteDevkitConfig() {
  try {
    const res = await fetch('/remotedevkit/cfg');
    if (!res.ok) throw new Error("Failed to load config");

    const config = await res.json();
    const devkit = config["remote-devkit"];
    if (!devkit) return;

    const ipInput = document.getElementById('devkitIp');
    const passwordInput = document.getElementById('rootPassword');

    if (ipInput) ipInput.value = devkit.ip || '';
    if (passwordInput) passwordInput.value = '**********';
  } catch (err) {
    console.warn("⚠️ Could not load remote devkit config:", err);
  }
}
