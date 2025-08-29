async function getDynamicRtspBase() {
  try {
    const res = await fetch('/remotedevkit/cfg');
    if (!res.ok) throw new Error('Failed to fetch devkit config');
    const cfg = await res.json();
    const remoteIp = cfg['remote-devkit']?.ip || '';

    if (!remoteIp || remoteIp === '127.0.0.1') {
      return 'rtsp://127.0.0.1:8554';
    }

    // Get the client IP (local machine IP as seen from the browser)
    const clientIp = await detectLocalIp();
    return `rtsp://${clientIp}:8554`;

  } catch (err) {
    console.error('⚠️ Failed to calculate dynamic RTSP base:', err);
    return 'rtsp://127.0.0.1:8554'; // fallback
  }
}


async function fetchMediaSources() {
  const res = await fetch('/mediasrc');
  return res.json();
}

async function fetchVideoFiles() {
  const res = await fetch('/mediasrc/videos');
  return res.json();
}

async function enumerateCameraOptions() {
  const devices = await navigator.mediaDevices.enumerateDevices();
  const cameras = devices.filter(d => d.kind === 'videoinput');
  const cameraOptions = [];

  // For now disable local camera enumeration
  // for (const cam of cameras) {
  //   const shortId = cam.deviceId.slice(0, 6);
  //   try {
  //     const stream = await navigator.mediaDevices.getUserMedia({
  //       video: { deviceId: cam.deviceId, width: { ideal: 1280 }, height: { ideal: 720 } }
  //     });
  //     const track = stream.getVideoTracks()[0];
  //     const { width, height } = track.getSettings();
  //     cameraOptions.push({
  //       label: `${cam.label || 'Camera'} (${width}x${height})`,
  //       value: cam.deviceId, // use full deviceId as value
  //       display: `camera:${shortId}`, // used only for showing user
  //       fullDeviceId: cam.deviceId
  //     });
  //     track.stop();
  //   } catch (err) {
  //     console.warn(`Could not access camera ${cam.label}:`, err);
  //   }
  // }

  return cameraOptions;
}

async function renderMediaSources(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const [sources, videoFiles, cameraOptions] = await Promise.all([
    fetchMediaSources(),
    fetchVideoFiles(),
    enumerateCameraOptions()
  ]);

  const MAX_ITEMS = 8;
  const limitedSources = Array.from({ length: MAX_ITEMS }, (_, i) => {
    const source = sources.find(s => s.index === i + 1);
    return source || { index: i + 1, file: '', state: 'stopped' };
  });

  container.innerHTML = '';
  container.classList.add('media-grid');
  container.style.display = 'grid';
  container.style.gridTemplateColumns = 'repeat(2, 1fr)';
  container.style.gridTemplateRows = 'repeat(4, auto)';
  container.style.gap = '1rem';

  for (let src of limitedSources) {
    let { index, file, state } = src;

    const gridItem = document.createElement('div');
    gridItem.className = 'media-grid-item';
    gridItem.dataset.index = index;

    const previewWrapper = document.createElement('div');
    previewWrapper.className = 'media-preview-wrapper';

    const previewElement = document.createElement('video');
    previewElement.className = 'media-source-preview';
    previewElement.muted = true;
    previewElement.autoplay = true;
    previewElement.playsInline = true;
    previewElement.controls = false;
    previewElement.style.width = '100%';
    previewElement.style.height = 'auto';

    if (file) {
      if (file.startsWith('camera:')) {
        const fullId = file.slice(7); // skip 'camera:'
        const cam = cameraOptions.find(c => c.fullDeviceId === fullId);
        if (cam) {
          try {
            const stream = await navigator.mediaDevices.getUserMedia({
              video: { deviceId: { exact: cam.fullDeviceId } }
            });
            previewElement.srcObject = stream;
          } catch (err) {
            console.warn('Camera preview failed:', err);
          }
        }
      } else {
        previewElement.src = `/media/${file}`;
        if (state === 'playing') {
          previewElement.loop = true;
          setTimeout(() => previewElement.play().catch(() => { }), 100);
        }
      }
    } else {
      previewElement.style.backgroundColor = '#ddd';
    }

    const iconBtn = document.createElement('button');
    iconBtn.className = 'icon-btn';
    iconBtn.title = file ? `Copy RTSP for Source ${index}` : 'Assign a file first';
    iconBtn.disabled = !file;
    iconBtn.style.border = 'none';
    iconBtn.style.background = 'none';

    const iconImg = document.createElement('img');
    iconImg.src = `/static/icons/number_${index}.png`;
    iconImg.alt = `Source ${index}`;
    iconImg.style.width = '20px';
    iconImg.style.height = '20px';
    iconImg.style.filter = 'invert(1)';
    iconBtn.appendChild(iconImg);

    iconBtn.addEventListener('click', async () => {
      if (!file) return;
      const RTSP_BASE = await getDynamicRtspBase();
      const rtspUrl = `${RTSP_BASE}/src${index}`;
      try {
        if (navigator.clipboard?.writeText) {
          await navigator.clipboard.writeText(rtspUrl);
        } else {
          const tempInput = document.createElement('input');
          tempInput.value = rtspUrl;
          document.body.appendChild(tempInput);
          tempInput.select();
          document.execCommand('copy');
          document.body.removeChild(tempInput);
        }
        showToast(`✅ RTSP URL copied: ${rtspUrl}`);
      } catch (err) {
        console.error('Clipboard copy failed:', err);
        alert('❌ Failed to copy RTSP URL.');
      }
    });

    const dropdown = document.createElement('select');
    dropdown.className = 'media-file-dropdown';
    dropdown.style.border = 'none';
    dropdown.style.borderBottom = '1px solid #ccc';
    dropdown.style.background = 'transparent';
    dropdown.style.padding = '0.3rem 0.4rem';
    dropdown.style.fontSize = '0.85rem';
    dropdown.style.fontFamily = 'Roboto Condensed, sans-serif';
    dropdown.style.color = 'lightblue';
    dropdown.style.appearance = 'none';
    dropdown.style.maxWidth = '180px';

    // dropdown.innerHTML = '<option value="">Not assigned</option>' +
    //   '<optgroup label="Video Files">' +
    //   videoFiles.map(v => `<option value="${v}" ${file === v ? 'selected' : ''}>${v}</option>`).join('') +
    //   '</optgroup>' +
    //   '<optgroup label="Cameras">' +
    //   cameraOptions.map(cam => {
    //     const isSelected = file === `camera:${cam.fullDeviceId.slice(0, 6)}`;
    //     return `<option value="camera:${cam.fullDeviceId}"`
    //           + (isSelected ? ' selected' : '')
    //           + `>${cam.label}</option>`;
    //   }).join('')
    //   + '</optgroup>';

    dropdown.innerHTML = '<option value="">Not assigned</option>' +
      '<optgroup label="Video Files">' +
      videoFiles.map(v => `<option value="${v}" ${file === v ? 'selected' : ''}>${v}</option>`).join('') +
      '</optgroup>';


    dropdown.addEventListener('change', async () => {
      const newFile = dropdown.value;
      try {
        await fetch('/mediasrc/assign', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ index, file: newFile })
        });
        showToast(`✅ Source ${index} updated to ${newFile || 'unassigned'}`);
        renderMediaSources(containerId);
      } catch (err) {
        console.error(err);
        alert('❌ Failed to assign media file.');
      }
    });

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'icon-btn';
    toggleBtn.title = state === 'playing' ? 'Stop stream' : 'Start stream';
    toggleBtn.disabled = !file;
    toggleBtn.style.border = 'none';
    toggleBtn.style.background = 'none';

    const toggleImg = document.createElement('img');
    toggleImg.src = state === 'playing'
      ? '/static/icons/stop-streaming.png'
      : '/static/icons/start-streaming.png';
    toggleImg.alt = toggleBtn.title;
    toggleImg.style.filter = 'invert(1)';
    toggleBtn.appendChild(toggleImg);

    toggleBtn.addEventListener('click', async () => {
      if (file?.startsWith('camera:')) {
        if (toggleBtn.dataset.webrtcActive === 'true') {
          toggleBtn._webrtcPC?.close();
          toggleBtn._webrtcStream?.getTracks().forEach(t => t.stop());
          toggleBtn._webrtcPC = null;
          toggleBtn._webrtcStream = null;
          toggleBtn.dataset.webrtcActive = 'false';
          toggleImg.src = '/static/icons/start-streaming.png';
          toggleBtn.title = 'Start stream';
          showToast('🛑 Camera streaming stopped');
          return;
        }

        try {
          const cam = cameraOptions.find(c => c.value === file);
          if (!cam) return;

          const stream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: { exact: cam.fullDeviceId }, width: { ideal: 1280 }, height: { ideal: 720 } }
          });

          const pc = new RTCPeerConnection();
          toggleBtn._webrtcPC = pc;
          toggleBtn._webrtcStream = stream;
          stream.getTracks().forEach(track => pc.addTrack(track, stream));

          const offer = await pc.createOffer();
          await pc.setLocalDescription(offer);

          const targetOrigin = location.origin.replace(/:\d+/, ':8081');
          const udpPort = 7001 + index - 1;
          const res = await fetch(`${targetOrigin}/reverse-offer?port=${udpPort}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(offer)
          });

          const answer = await res.json();
          await pc.setRemoteDescription(answer);

          toggleBtn.dataset.webrtcActive = 'true';
          toggleImg.src = '/static/icons/stop-streaming.png';
          toggleBtn.title = 'Stop stream';
          showToast('✅ Camera streaming started');
        } catch (err) {
          console.error('Camera streaming failed:', err);
          alert('❌ Failed to start camera streaming.');
        }
        return;
      }
      toggleBtn.disabled = true;
      const isPlaying = state === 'playing';
      const endpoint = isPlaying ? '/mediasrc/stop' : '/mediasrc/start';

      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ index })
        });

        if (!res.ok) {
          const error = await res.json();
          alert(`❌ ${error.error || 'Failed to toggle source.'}`);
          toggleBtn.disabled = false;
          return;
        }

        showToast(`✅ Streaming ${isPlaying ? 'stopped' : 'started'}`);
        renderMediaSources(containerId);
      } catch (err) {
        console.error(err);
        alert('❌ Network error while toggling source.');
      }
    });

    const controls = document.createElement('div');
    controls.className = 'media-controls';
    controls.style.position = 'relative';
    controls.style.zIndex = '10';
    controls.style.display = 'flex';
    controls.style.gap = '0.5rem';
    controls.style.alignItems = 'center';
    controls.style.background = 'rgba(0, 0, 0, 0.5)';
    controls.style.padding = '0.4rem';
    controls.style.borderRadius = '4px';
    controls.style.color = 'white';
    controls.appendChild(iconBtn);
    controls.appendChild(dropdown);
    controls.appendChild(toggleBtn);

    previewElement.style.zIndex = '1';
    previewElement.style.position = 'relative';
    previewWrapper.appendChild(previewElement);
    gridItem.appendChild(previewWrapper);
    gridItem.appendChild(controls);
    container.appendChild(gridItem);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  renderMediaSources('media-source-rows');
});