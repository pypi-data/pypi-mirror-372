const videoGrid = document.getElementById('videoGrid');
const noVideoMessage = document.getElementById('noVideoMessage');
const layoutSlider = document.getElementById('layoutSlider');
const layoutLabel = document.getElementById('layoutLabel');

const MAX_CHANNELS = 16;
const EXPECTED_STREAM_COUNT = 16; // Fixed stream count
let currentTrackCount = 0;
let activeTracks = Array(MAX_CHANNELS).fill(null);
let currentPage = 0;
let visiblePerPage = 4; // Default videos per page
let pageCount = 1;

let debounceTimer = null;

const mode = new URLSearchParams(window.location.search).get('mode');
if (mode === 'light' || mode === 'dark') {
  document.documentElement.setAttribute('data-theme', mode);
}

const srcParam = new URLSearchParams(window.location.search).get('src');
const indices = srcParam ? srcParam.split(',').map(x => parseInt(x)) : null;

function updateLayout() {
  const n = Math.min(currentTrackCount, visiblePerPage); // Tiles to show on current page
  if (currentTrackCount === 0) {
    noVideoMessage.style.display = 'block';
    videoGrid.style.gridTemplateColumns = '1fr';
    videoGrid.style.gridTemplateRows = '1fr';
    document.body.classList.remove('single-tile');
    return;
  }
  noVideoMessage.style.display = 'none';
  const cols = Math.ceil(Math.sqrt(n));
  const rows = Math.ceil(n / cols);
  videoGrid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  videoGrid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
  document.body.classList.toggle('single-tile', n === 1);
}

function syncTile(index, tile) {
  while (videoGrid.children.length <= index) {
    const placeholder = document.createElement('div');
    placeholder.className = 'video-tile';
    videoGrid.appendChild(placeholder);
  }
  videoGrid.replaceChild(tile, videoGrid.children[index]);
}

function setupExpectedStreams() {
  videoGrid.innerHTML = '';
  currentTrackCount = 0;
  activeTracks = Array(MAX_CHANNELS).fill(null);

  for (let i = 0; i < EXPECTED_STREAM_COUNT; i++) {
    const placeholder = document.createElement('div');
    placeholder.className = 'video-tile';
    videoGrid.appendChild(placeholder);
  }

  for (let i = 0; i < EXPECTED_STREAM_COUNT; i++) {
    createVideoTile(i);
  }

  updatePagination();
  updateLayout();
}

function updatePagination() {
  pageCount = Math.ceil(currentTrackCount / visiblePerPage) || 1;
  currentPage = Math.min(currentPage, pageCount - 1); // Ensure currentPage is valid
  buildPagination(); // From pagination.js
  showPage(currentPage); // From pagination.js
}

function createVideoTile(index) {
  const pc = new RTCPeerConnection({
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
  });
  pc.addTransceiver('video', { direction: 'recvonly' });

  const metadataChannel = pc.createDataChannel('metadata');
  let messageCount = 0;
  let lastCount = 0;

  metadataChannel.onopen = () => {
    console.log(`📡 Metadata DataChannel open (channel ${index})`);
  };

  const settingsRaw = localStorage.getItem("viewerSettings_global");
  let METADATA_DELAY_MS = 1800;

  try {
    const settings = JSON.parse(settingsRaw);
    if (settings && typeof settings.metadataDelay === "number") {
      METADATA_DELAY_MS = settings.metadataDelay;
    }
  } catch (e) {
    console.warn("Failed to parse viewerSettings_global:", e);
  }

  function renderByType(ctx, canvas, video, index) {
    const now = performance.now();
    const queue = canvas.metadataQueue;

    if (!queue || queue.length === 0) return;

    // Remove old metadata (older than delay * 2)
    while (queue.length > 0 && now - queue[0].timestamp > METADATA_DELAY_MS * 2) {
      queue.shift();
    }

    // Find the best-fit metadata that's at least `METADATA_DELAY_MS` old
    let candidate = null;
    for (let i = queue.length - 1; i >= 0; i--) {
      const entry = queue[i];
      const age = now - entry.timestamp;

      if (age >= METADATA_DELAY_MS) {
        candidate = entry;
        break;
      }
    }

    if (!candidate) return;

    // Use and optionally trim before candidate
    const type = candidate.data?.type;
    const data = candidate.data?.data;
    const strategy = window.drawStrategies[type];

    if (strategy) {
      strategy(ctx, canvas, data, video, index);
    }

    // Optional: cleanup everything older than candidate
    const candidateIndex = queue.indexOf(candidate);
    if (candidateIndex > 0) {
      queue.splice(0, candidateIndex); // keep candidate and newer
    }
  }

  pc.ontrack = (event) => {
    if (event.track.kind === 'video' && !activeTracks[index]) {
      const stream = new MediaStream();
      stream.addTrack(event.track);

      const tile = document.createElement('div');
      tile.className = 'video-tile';
      tile.style.position = 'relative';

      const video = document.createElement('video');
      video.autoplay = true;
      video.playsInline = true;
      video.muted = true;
      video.srcObject = stream;
      video.style.width = '100%';
      video.style.height = '100%';
      video.style.display = 'block';

      const canvas = document.createElement('canvas');
      canvas.style.position = 'absolute';
      canvas.style.left = 0;
      canvas.style.top = 0;
      canvas.style.width = '100%';
      canvas.style.height = '100%';
      canvas.style.pointerEvents = 'none';
      canvas.metadataQueue = [];

      metadataChannel.onmessage = (e) => {
        try {
          const parsed = JSON.parse(e.data);
          canvas.metadataQueue.push({
            timestamp: performance.now(),
            data: parsed
          });

          // Optional cleanup
          if (canvas.metadataQueue.length > 300) {
            canvas.metadataQueue.splice(0, canvas.metadataQueue.length - 20);
          }
        } catch {
          console.warn(`📨 [Invalid JSON] Channel ${index}:`, e.data);
        }
      };

      const bannerWrapper = document.createElement('div');
      bannerWrapper.className = 'tile-banner-wrapper';
      bannerWrapper.style.display = 'flex';
      bannerWrapper.style.justifyContent = 'space-between';
      bannerWrapper.style.alignItems = 'center';
      bannerWrapper.style.position = 'absolute';
      bannerWrapper.style.bottom = '0';
      bannerWrapper.style.left = '0';
      bannerWrapper.style.right = '0';
      bannerWrapper.style.padding = '6px 4px';
      bannerWrapper.style.background = 'rgba(0,0,0,0.6)';
      bannerWrapper.style.fontSize = '12px';
      bannerWrapper.style.color = 'white';

      const bannerText = document.createElement('div');
      bannerText.className = 'tile-banner-text';
      bannerText.textContent = `Channel ${index}`;
      bannerWrapper.appendChild(bannerText);

      const menuBtn = document.createElement('button');
      menuBtn.className = 'channel-menu-button';
      menuBtn.title = 'Settings';
      menuBtn.style.background = 'none';
      menuBtn.style.border = 'none';
      menuBtn.style.padding = '0';
      menuBtn.style.margin = '0';
      menuBtn.style.cursor = 'pointer';


      menuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openSettingsForScope(`channel_${index}`);
      });


      const icon = document.createElement('img');
      icon.src = 'static/icons/menu.png';
      icon.alt = 'Settings';
      icon.className = 'channel-menu-icon';
      icon.style.width = '14px';
      icon.style.height = '14px';
      icon.style.display = 'block';

      menuBtn.appendChild(icon);
      bannerWrapper.appendChild(menuBtn);

      tile.appendChild(video);
      tile.appendChild(canvas);
      tile.appendChild(bannerWrapper);

      syncTile(index, tile);
      activeTracks[index] = tile;
      currentTrackCount++;
      updatePagination();
      updateLayout();

      const ctx = canvas.getContext('2d');
      const updateCanvasSize = () => {
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
      };

      const drawLoop = () => {
        if (video.readyState >= 2) {
          updateCanvasSize();
          renderByType(ctx, canvas, video, index);
        }
        requestAnimationFrame(drawLoop);
      };
      drawLoop();

      setInterval(async () => {
        if (pc.connectionState !== 'connected') return;
        const stats = await pc.getStats();
        stats.forEach(report => {
          if (report.type === 'inbound-rtp' && report.kind === 'video') {
            const fps = report.framesPerSecond?.toFixed(1) ?? 'N/A';
            const width = report.frameWidth ?? '?';
            const height = report.frameHeight ?? '?';
            let bitrate = 0;

            if (!tile.lastBytes) {
              tile.lastBytes = report.bytesReceived;
              tile.lastTimestamp = report.timestamp;
              return;
            }

            const deltaBytes = report.bytesReceived - tile.lastBytes;
            const deltaTime = (report.timestamp - tile.lastTimestamp) / 1000;
            bitrate = ((deltaBytes * 8) / deltaTime / 1000).toFixed(1);

            tile.lastBytes = report.bytesReceived;
            tile.lastTimestamp = report.timestamp;

            bannerText.textContent = `Channel ${index} | ${width}x${height} | ${fps} fps | ${bitrate} kbps | ${lastCount} msgs/sec`;
            lastCount = messageCount;
            messageCount = 0;
          }
        });
      }, 1000);
    }
  };

  pc.createOffer().then(offer => {
    return pc.setLocalDescription(offer).then(() => offer);
  }).then(offer => {
    return fetch(`/offer?channel=${index}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(offer)
    });
  }).then(res => res.json()).then(answer => {
    return pc.setRemoteDescription(answer);
  }).catch(err => {
    console.error(`Channel ${index} error`, err);
    setTimeout(() => createVideoTile(index), 5000);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  // Initialize layout (videos per page)
  const savedLayoutCount = parseInt(localStorage.getItem('layoutCount'), 10);
  const initialLayoutCount = !isNaN(savedLayoutCount) ? savedLayoutCount : parseInt(layoutSlider.value, 10);
  layoutSlider.value = initialLayoutCount;
  layoutLabel.textContent = initialLayoutCount;
  visiblePerPage = initialLayoutCount;

  if (indices) {
    indices.sort((a, b) => a - b).forEach(i => {
      if (!isNaN(i) && i >= 0 && i < MAX_CHANNELS) {
        createVideoTile(i);
      }
    });
    // Fill remaining slots up to EXPECTED_STREAM_COUNT
    for (let i = 0; i < EXPECTED_STREAM_COUNT; i++) {
      if (!activeTracks[i]) {
        const placeholder = document.createElement('div');
        placeholder.className = 'video-tile';
        syncTile(i, placeholder);
      }
    }
    currentTrackCount = indices.length;
    updatePagination();
    updateLayout();
  } else {
    setupExpectedStreams();
  }
});

layoutSlider.addEventListener('input', () => {
  const count = parseInt(layoutSlider.value, 10);
  layoutLabel.textContent = count;
  localStorage.setItem('layoutCount', count);
  visiblePerPage = count;
  updatePagination();
  updateLayout();
});