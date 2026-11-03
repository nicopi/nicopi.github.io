(() => {
  const page = document.querySelector('.talks-page');
  if (!page) return;
  const tools = page.querySelector('.talks-tools');
  const search = page.querySelector('#talks-search');
  const year = page.querySelector('#talks-year');
  const yearNav = page.querySelector('#talks-year-nav');
  const years = [...yearNav.querySelectorAll('[data-talk-year]')];
  const categories = [...page.querySelectorAll('[data-talk-kind]')];
  const entries = [...page.querySelectorAll('.talk-archive-entry')];
  const groups = [...page.querySelectorAll('.talks-year-group')];
  const empty = page.querySelector('.talks-empty');
  const status = page.querySelector('#talks-result-status');
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  let kind = 'all';
  const update = () => {
    const words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let count = 0;
    entries.forEach(entry => {
      const text = normalize(entry.textContent);
      const visible = (kind === 'all' || entry.dataset.kind === kind)
        && (year.value === 'all' || entry.dataset.year === year.value)
        && words.every(word => text.includes(word));
      entry.hidden = !visible;
      if (visible) count++;
    });
    groups.forEach(group => {
      const visible = [...group.querySelectorAll('.talk-archive-entry')].filter(entry => !entry.hidden).length;
      group.hidden = visible === 0;
      group.querySelector('.group-count').textContent = visible;
    });
    categories.forEach(button => {
      const selected = button.dataset.talkKind === kind;
      button.setAttribute('aria-pressed', String(selected));
      button.classList.toggle('selected', selected);
    });
    years.forEach(button => {
      const selected = button.dataset.talkYear === year.value;
      button.setAttribute('aria-pressed', String(selected));
      button.classList.toggle('selected', selected);
    });
    status.textContent = `${count} ${count === 1 ? 'event' : 'events'}`;
    empty.hidden = count > 0;
  };
  search.addEventListener('input', update);
  year.addEventListener('change', update);
  categories.forEach(button => button.addEventListener('click', () => { kind = button.dataset.talkKind; update(); }));
  years.forEach(button => button.addEventListener('click', () => { year.value = button.dataset.talkYear; update(); }));
  page.querySelector('.talks-reset').addEventListener('click', () => {
    kind = 'all'; search.value = ''; year.value = 'all'; update(); search.focus();
  });
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !event.metaKey && !event.ctrlKey && !event.altKey && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) {
      event.preventDefault(); search.focus();
    }
  });
  tools.hidden = false;
  yearNav.hidden = false;
  update();
})();
