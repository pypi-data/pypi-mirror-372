function showUploadDialog({ title, accept, uploadUrl, onSuccess }) {
    const dialog = document.getElementById('uploadDialog');
    const titleEl = document.getElementById('uploadTitle');
    const fileInput = document.getElementById('uploadInput');
    const progress = document.getElementById('uploadProgress');
    const status = document.getElementById('uploadStatus');
    const cancelBtn = document.getElementById('uploadCancel');
  
    // Reset UI
    titleEl.textContent = title || 'Upload File';
    fileInput.value = '';
    fileInput.accept = accept || '*/*';
    progress.value = 0;
    progress.classList.add('hidden');
    status.textContent = '';
    dialog.classList.remove('hidden');
  
    cancelBtn.onclick = () => {
      dialog.classList.add('hidden');
    };
  
    fileInput.onchange = async () => {
      const file = fileInput.files[0];
      if (!file) return;
  
      const formData = new FormData();
      formData.append('file', file);
  
      progress.value = 0;
      progress.classList.remove('hidden');
      status.textContent = 'Uploading...';
      fileInput.disabled = true;
  
      let fakeProgress = 0;
      const progressTimer = setInterval(() => {
        if (fakeProgress < 90) {
          fakeProgress += 5;
          progress.value = fakeProgress;
        }
      }, 150);
  
      try {
        const res = await fetch(uploadUrl, {
          method: 'POST',
          body: formData
        });
  
        clearInterval(progressTimer);
        progress.value = 100;
  
        if (!res.ok) {
          status.textContent = `Upload failed: ${res.statusText}`;
          return;
        }
  
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        status.textContent = '';
  
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.trim().split('\n');
          if (lines.length > 0) {
            status.textContent = lines[lines.length - 1];
          }
        }

      } catch (err) {
        clearInterval(progressTimer);
        status.textContent = 'Upload error: ' + err.message;
      } finally {
        fileInput.disabled = false;
        if (typeof onSuccess === 'function') {
            onSuccess();
        }
      }
    };
  }
  