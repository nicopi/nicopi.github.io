(() => {
  const toggle = document.querySelector('#menu-toggle');
  const nav = document.querySelector('#site-nav');
  if (!toggle || !nav) return;

  const close = (restoreFocus = false) => {
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('open');
    if (restoreFocus) toggle.focus();
  };
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') close(true);
  });
  document.addEventListener('click', event => {
    if (!nav.contains(event.target) && !toggle.contains(event.target)) close();
  });
  nav.addEventListener('click', event => { if (event.target.closest('a')) close(); });
  matchMedia('(max-width: 780px)').addEventListener('change', () => close());
})();
