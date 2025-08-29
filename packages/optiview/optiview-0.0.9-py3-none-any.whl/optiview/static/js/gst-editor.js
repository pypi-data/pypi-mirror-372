let currentHighlightMarkers = [];

CodeMirror.defineMode("gstreamer", function() {
  return {
    token: function(stream) {
      // Highlight placeholders like <RTSP_SRC_LOCATION_1>
      if (stream.match(/<([A-Z0-9_]+)>/)) {
        return "placeholder-param";  // Add custom CSS class
      }

      // Highlight plugin names after "!"
      if (stream.match(/!\s+([a-zA-Z0-9_-]+)/, false)) {
        stream.match(/!\s+/); // Skip "! "
        if (stream.match(/sima[a-zA-Z0-9_-]*/)) {
          return "plugin-sima";  // 🔴 custom style for sima plugins
        } else if (stream.match(/[a-zA-Z0-9_-]+/)) {
          return "plugin-bold";  // regular plugins
        }
      }

      // Highlight quoted caps
      if (stream.match(/'[^']*'/)) {
        return "quoted-caps";
      }

      stream.next(); // Advance if no match
      return null;
    }

  };
});

function extractGstString(raw) {
  const marker = '--gst-string="';
  const startIndex = raw.indexOf(marker);
  if (startIndex === -1) return null;

  const start = startIndex + marker.length;
  const end = raw.lastIndexOf('"');
  if (end <= start) return null;

  return raw.slice(start, end).trim();
}

function formatGstPipeline(gstString) {
  const elements = gstString.trim().split(/\s*!\s*/);
  const lines = [];
  let indent = 0;

  for (let i = 0; i < elements.length; i++) {
    const el = elements[i];

    // Branch pad reference (e.g., t.)
    if (/^\w+\./.test(el)) {
      lines.push('  '.repeat(indent) + el);
      continue;
    }

    // Tee declaration (e.g., tee name=t)
    if (/^tee name=/.test(el)) {
      lines.push('  '.repeat(indent) + el); // ← no ! here
      indent += 1;
      continue;
    }

    // First element — no prefix
    const prefix = i === 0 ? '' : '! ';
    lines.push('  '.repeat(indent) + prefix + el);
  }

  return lines.join('\n');
}


function flattenGstPipeline(multiline) {
  return multiline
    .split('\n')
    .map(line => line.trim().replace(/^! /, '').replace(/^/, '').replace(/\\$/, ''))
    .filter(Boolean)
    .join(' ! ');
}

let gstEditorInstance;

document.getElementById('btnGstEdit').addEventListener('click', () => {
  const text = codeMirrorEditor.getValue();

  try {
    const json = JSON.parse(text);
    const applications = json?.applications || [];

    for (const app of applications) {
      for (const pipeline of app?.pipelines || []) {
        const gstRaw = pipeline?.gst;
        if (gstRaw && typeof gstRaw === 'string') {
          const gstRaw = pipeline.gst;
          const unescapedGstRaw = gstRaw.replace(/\\"/g, '"');
          const gstString = extractGstString(unescapedGstRaw);
          if (gstString) {
            const formatted = formatGstPipeline(gstString);

            // Show modal
            const dialog = document.getElementById('gstEditDialog');
            dialog.classList.remove('hidden');

            if (!gstEditorInstance) {
              gstEditorInstance = CodeMirror.fromTextArea(document.getElementById('gstEditor'), {
                lineNumbers: true,
                theme: document.documentElement.dataset.theme === 'dark' ? 'material' : 'default',
                mode: 'gstreamer',
                lineWrapping: true
              });
              gstEditorInstance.setSize("100%", "100%");
            }

            gstEditorInstance.setValue(formatted);
            updateDynamicTooltips();

            function replaceGstStringCommand(gstRaw, newGstString) {
              const prefix = '--gst-string="';
              const start = gstRaw.indexOf(prefix);
              if (start === -1) return gstRaw;

              // Find the last quote in the entire string — assumes it's the end of --gst-string
              const end = gstRaw.lastIndexOf('"');
              if (end <= start) return gstRaw;

              const before = gstRaw.slice(0, start + prefix.length);
              const after = gstRaw.slice(end); // Includes the closing quote

              console.log("📦 Original gst-string content:", gstRaw.slice(start + prefix.length, end));
              console.log("🆕 New gst-string to insert:", newGstString);

              return `${before}${newGstString}${after}`;
            }

            // Hook Save
            document.getElementById('gstEditSave').onclick = async () => {
              const flat = flattenGstPipeline(gstEditorInstance.getValue());
              console.log(flat);
              console.log(gstRaw);

              const updatedGst = replaceGstStringCommand(gstRaw, flat);
              pipeline.gst = updatedGst;

              console.log(pipeline.gst);

              codeMirrorEditor.setValue(JSON.stringify(json, null, 2));
              document.getElementById('gstEditDialog').classList.add('hidden');
              showToast('✅ GStreamer pipeline updated successfully');

              await saveFile();
            };

            // Hook Cancel
            document.getElementById('gstEditCancel').onclick = () => {
              document.getElementById('gstEditDialog').classList.add('hidden');
            };

            return;
          }
        }
      }
    }

    showToast("⚠️ No valid --gst-string found in file.");
  } catch (err) {
    console.error("gstEdit error:", err);
    showToast("❌ Invalid JSON structure.");
  }
});

gstEditorInstance = CodeMirror.fromTextArea(document.getElementById('gstEditor'), {
  lineNumbers: true,
  theme: document.documentElement.dataset.theme === 'dark' ? 'material' : 'default',
  mode: 'gstreamer',
  lineWrapping: true
});
gstEditorInstance.setSize("100%", "100%");

gstEditorInstance.on('cursorActivity', async () => {
  let keyword = gstEditorInstance.getSelection().trim();

  currentHighlightMarkers.forEach(marker => marker.clear());
  currentHighlightMarkers = [];

  let selected = gstEditorInstance.getSelection().trim();

  // If user has selected a word
  if (selected.length >= 2 && /^[a-zA-Z0-9_-]+$/.test(selected)) {
    const cursor = gstEditorInstance.getCursor();
    const regex = new RegExp(`\\b${selected}\\b`, 'g');

    const doc = gstEditorInstance.getDoc();
    const fullText = doc.getValue();
    let match;
    while ((match = regex.exec(fullText)) !== null) {
      const start = doc.posFromIndex(match.index);
      const end = doc.posFromIndex(match.index + selected.length);

      const marker = doc.markText(start, end, {
        className: 'cm-highlight-selection'
      });

      currentHighlightMarkers.push(marker);
    }
  }

  // Fallback: get word under cursor
  if (!keyword) {
    const cursor = gstEditorInstance.getCursor();
    const wordRange = gstEditorInstance.findWordAt(cursor);
    keyword = gstEditorInstance.getRange(wordRange.anchor, wordRange.head).trim();
  }

  // Clean and validate keyword
  keyword = keyword.replace(/[^a-zA-Z0-9_]/g, '');

  if (keyword.length >= 3) {
    try {
      const appName = (JSON.parse(codeMirrorEditor.getValue())?.applications?.[0]?.name) || '';
      const res = await fetch(`/gsthelp/${keyword}?app=${encodeURIComponent(appName)}`);      
      if (res.ok) {
        const helpText = await res.text();
        showHelpPanel(keyword, `<pre>${escapeHtml(helpText)}</pre>`);
      } else {
        showDefaultHelpMessage();
      }
    } catch (err) {
      console.warn("Help fetch failed:", err);
      showDefaultHelpMessage();
    }
  } else {
    showDefaultHelpMessage();
  }
});

function showHelpPanel(title, rawText) {
  document.getElementById('helpTitle').textContent = title;
  const helpContent = document.getElementById('helpContent');

  const linked = rawText.replace(/(https?:\/\/[^\s]+)/g, url =>
    `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
  );
  helpContent.innerHTML = `<pre>${linked}</pre>`;
  document.getElementById('helpPanel').scrollTo({ top: 0, behavior: 'smooth' });
}


function showDefaultHelpMessage() {
  document.getElementById('helpTitle').textContent = 'GStreamer Help';
  document.getElementById('helpContent').innerHTML = `
    <div class="help-placeholder">
      <p>Click or select a supported GStreamer plugin name to view help.</p>
    </div>`;
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, s => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[s]));
}

document.getElementById('gstEditSave').onclick = () => {
  try {
    const flat = flattenGstPipeline(gstEditorInstance.getValue());
    const text = codeMirrorEditor.getValue();
    const json = JSON.parse(text);

    const applications = json?.applications || [];
    let updated = false;

    for (const app of applications) {
      for (const pipeline of app?.pipelines || []) {
        const gstRaw = pipeline?.gst;
        if (gstRaw && typeof gstRaw === 'string') {
          // Replace only the gst-string argument inside the gst line
          const updatedGst = gstRaw.replace(
            /--gst-string="([^"]+)"/,
            `--gst-string="${flat}"`
          );
          pipeline.gst = updatedGst;
          updated = true;
        }
      }
    }

    if (updated) {
      const updatedJson = JSON.stringify(json, null, 2);
      codeMirrorEditor.setValue(updatedJson);
      document.getElementById('gstEditDialog').classList.add('hidden');
      showToast('✅ GStreamer pipeline updated successfully');
    } else {
      showToast("⚠️ No --gst-string found to update.");
    }

  } catch (err) {
    console.error("Save failed:", err);
    showToast("❌ Failed to save GStreamer pipeline.", 4000);
  }
};

async function updateDynamicTooltips() {
  try {
    const res = await fetch('/remotedevkit/cfg');
    if (!res.ok) throw new Error('Failed to fetch devkit config');
    const cfg = await res.json();
    const remoteIp = cfg['remote-devkit']?.ip || '';

    // Get client IP using WebRTC trick (fallback-friendly)
    const clientIp = await detectLocalIp();

    // Determine message based on devkit installation
    let udpHostTooltip;
    if (!remoteIp || remoteIp === '127.0.0.1') {
      udpHostTooltip = 'UDP host destination IP.\n\nIf you wish to use locally installed OptiView to render video. Use 127.0.0.1 as the IP address.';
    } else {
      udpHostTooltip = `UDP host destination IP.\n\nIf you wish to use remotely installed OptiView to render video. Use the IP address of the OptiView machine (${clientIp}) as the destination.`;
    }

    // Inject into the placeholder map
    placeholderTooltipOverrides['UDP_HOST'] = udpHostTooltip;

    // Refresh tooltips in editor
    attachPlaceholderTooltips();

  } catch (err) {
    console.error('⚠️ Failed to update UDP_HOST_1 tooltip:', err);
  }
}

const placeholderTooltipOverrides = {
  'UDP_HOST': 'UDP host destination IP.\n\nIf you wish to use OptiView to render video, use the IP address of where OptiView is running from.',
  'UDP_PORT': 'UDP destination port.\n\nIf you wish to use OptiView to render video, use port 9000 to 9015.',
  'RTSP_SRC_LOCATION': 'RTSP stream source URL for camera.\n\nIf you wish to use OptiView as RTSP source, start the OptiView media source, then copy and paste the RTSP URL here.',
};

function getTooltipForPlaceholder(key) {
  // Match base patterns using regex
  if (/^RTSP_SRC_LOCATION_\d+$/.test(key)) {
    return 'RTSP stream source URL for camera.\n\nIf you wish to use OptiView as RTSP source, start the OptiView media source, then copy and paste the RTSP URL here.';
  }

  if (/^UDP_HOST_\d+$/.test(key)) {
    return placeholderTooltipOverrides['UDP_HOST'] || `UDP host destination IP.\n\nReplace with the IP where OptiView is running.`;
  }

  if (/^UDP_PORT_\d+$/.test(key)) {
    return placeholderTooltipOverrides['UDP_PORT'] || `UDP destination port.\n\nReplace with a valid port (9000–9015 for OptiView).`;
  }

  // Default fallback
  return `Placeholder: ${key}\n\nReplace this with real value.`;
}

function attachPlaceholderTooltips() {
  const wrapper = gstEditorInstance.getWrapperElement();
  const placeholders = wrapper.querySelectorAll('.cm-placeholder-param');

  placeholders.forEach(el => {
    if (el.classList.contains('processed')) return;
    el.classList.add('processed');

    const rawText = el.textContent.replace(/[<>]/g, '');
    const tooltip = getTooltipForPlaceholder(rawText);

    el.title = tooltip;
    el.style.cursor = 'pointer';
    el.addEventListener('click', () => showPlaceholderDialog(el, rawText));
  });
}

async function detectLocalIp() {
  try {
    const res = await fetch('/server-ip');
    if (!res.ok) throw new Error('Failed to fetch server IP');
    const { ip } = await res.json();
    return ip || 'unknown';
  } catch (err) {
    console.error('⚠️ Failed to detect server IP from backend:', err);
    return 'unknown';
  }
}

function showPlaceholderDialog(el, paramName) {
  const modal = document.getElementById("placeholderEditorModal");
  const input = document.getElementById("placeholderEditorInput");
  const saveBtn = document.getElementById("placeholderEditorSave");
  const cancelBtn = document.getElementById("placeholderEditorCancel");
  const desc = document.getElementById("placeholderEditorDesc"); // ✅ fix: reference to desc

  const tooltip = getTooltipForPlaceholder(paramName);
  desc.textContent = tooltip;
  input.value = "";

  modal.classList.remove("hidden");
  input.focus();

  function cleanup() {
    modal.classList.add("hidden");
    saveBtn.removeEventListener("click", onConfirm);
    cancelBtn.removeEventListener("click", onCancel);
  }

  function onConfirm() {
    const newText = input.value.trim();
    if (newText) {
      const cm = gstEditorInstance;
      const pos = cm.coordsChar(el.getBoundingClientRect());
      cm.replaceRange(newText, pos, {
        line: pos.line,
        ch: pos.ch + paramName.length + 2, // includes <>
      });

      // 🔁 Re-attach tooltips to updated placeholder elements
      setTimeout(attachPlaceholderTooltips, 0); // Defer to ensure DOM update
    }
    cleanup();
  }

  function onCancel() {
    cleanup();
  }

  saveBtn.addEventListener("click", onConfirm);
  cancelBtn.addEventListener("click", onCancel);
}

// document.getElementById('gstEditVisualize').onclick = async () => {
//   try {
//     const flat = flattenGstPipeline(gstEditorInstance.getValue());
//     const appName = (JSON.parse(codeMirrorEditor.getValue())?.applications?.[0]?.name) || ''; 
//     const response = await fetch('/analyze-pipeline', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ pipeline: flat, file: encodeURIComponent(appName) })
//     });

//     if (!response.ok) {
//       const err = await response.json();
//       throw new Error(err.error || 'Server error');
//     }

//     const blob = await response.blob();
//     const url = URL.createObjectURL(blob);

//     // Either download the file or preview it (e.g., in a modal)
//     const a = document.createElement('a');
//     a.href = url;
//     a.download = 'pipeline.dot';
//     document.body.appendChild(a);
//     a.click();
//     a.remove();

//     showToast('✅ DOT graph downloaded');

//   } catch (err) {
//     console.error('Visualization failed:', err);
//     showToast(`❌ Visualization failed: ${err.message || err}`, 4000);
//   }
// };
