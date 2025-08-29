function showToast(message, duration = 5000) {
    let container = document.getElementById('toast-container');
  
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }
  
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
  
    container.appendChild(toast);
  
    // Force reflow to enable transition
    requestAnimationFrame(() => {
      toast.classList.add('visible');
    });
  
    setTimeout(() => {
      toast.classList.remove('visible');
      toast.addEventListener('transitionend', () => toast.remove());
    }, duration);
  }
  