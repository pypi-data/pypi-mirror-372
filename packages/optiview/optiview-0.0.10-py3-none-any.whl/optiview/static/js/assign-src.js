// assign-src.js
let selectedFileToAssign = null;

document.addEventListener('DOMContentLoaded', () => {
  const popup = document.getElementById('assign-src-popup');
  const select = document.getElementById('assign-source-select');
  const saveBtn = document.getElementById('assign-save-btn');
  const cancelBtn = document.getElementById('assign-cancel-btn');

  // Assign buttons in media rows
  document.querySelectorAll('.assign-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const row = btn.closest('.media-source-row');
      const dropdown = row.querySelector('.media-file-dropdown');
      selectedFileToAssign = dropdown.value;

      if (!selectedFileToAssign) {
        alert('Please select a media file first.');
        return;
      }

      // Reset dropdown and button state, then show popup
      select.value = '';
      saveBtn.disabled = true;
      popup.classList.remove('hidden');
    });
  });

  // Enable Assign button when a valid source is selected
  select.addEventListener('change', () => {
    saveBtn.disabled = !select.value;
  });

  cancelBtn.addEventListener('click', () => {
    popup.classList.add('hidden');
    selectedFileToAssign = null;
  });

  saveBtn.addEventListener('click', async () => {
    const sourceIndex = select.value;
    if (!sourceIndex) return;

    try {
      const res = await fetch('/mediasrc/assign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file: selectedFileToAssign,
          index: parseInt(sourceIndex)
        })
      });

      if (!res.ok) {
        const error = await res.json();
        alert(`❌ Failed to assign media: ${error.error || res.statusText}`);
        return;
      }

      // Hide popup and reset state
      popup.classList.add('hidden');
      selectedFileToAssign = null;
    } catch (err) {
      console.error('Assign request failed:', err);
      alert('❌ Could not assign media. Check your network or backend.');
    }
  });
});
