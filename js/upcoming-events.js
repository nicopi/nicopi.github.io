(() => {
  const update = () => {
    const now = Date.now();
    document.querySelectorAll('[data-upcoming-until]').forEach(element => {
      const end = Date.parse(element.dataset.upcomingUntil);
      if (!Number.isFinite(end) || now <= end) return;
      if (element.classList.contains('upcoming-talks')) element.hidden = true;
      else if (element.classList.contains('upcoming-badge')) element.textContent = 'Talk';
    });
  };
  update();
  window.addEventListener('pageshow', update);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') update();
  });
})();
