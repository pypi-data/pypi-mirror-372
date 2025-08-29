function buildPagination() {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
  
    for (let i = 0; i < pageCount; i++) {
      const btn = document.createElement('div');
      btn.className = 'page-btn';
      btn.textContent = i + 1;
      if (i === currentPage) btn.classList.add('active');
      btn.addEventListener('click', () => {
        currentPage = i;
        showPage(i);
      });
      pagination.appendChild(btn);
    }
  }
  
  function showPage(page) {
    const start = page * visiblePerPage;
    const end = start + visiblePerPage;
  
    Array.from(videoGrid.children).forEach((tile, i) => {
      tile.style.display = i >= start && i < end ? 'block' : 'none';
    });
  
    // Update active state
    const buttons = document.querySelectorAll('#pagination .page-btn');
    buttons.forEach((btn, i) => {
      btn.classList.toggle('active', i === page);
    });
  
    updateLayout();
  }
  