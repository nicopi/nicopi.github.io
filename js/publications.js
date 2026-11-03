(() => {
  const page = document.querySelector('.publications-page');
  if (!page) return;

  const search = page.querySelector('#search');
  const sort = page.querySelector('#sort');
  const mobileYear = page.querySelector('#mobile-year');
  const results = page.querySelector('#results');
  const empty = page.querySelector('#empty-state');
  const resultCount = page.querySelector('#result-count');
  const yearButtons = [...page.querySelectorAll('#year-nav [data-year]')];
  const typeButtons = [...page.querySelectorAll('.type-filters [data-type]')];
  const groups = [...results.querySelectorAll('.year-group')];
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/\s+/g, ' ').trim();
  const state = { query: '', year: 'all', type: 'all', sort: 'newest' };
  const papers = [...results.querySelectorAll('.paper')].map(element => {
    const year = element.closest('.year-group').dataset.year;
    const type = element.dataset.type;
    const searchable = normalize([
      element.querySelector('h3').textContent,
      element.querySelector('.paper-venue').textContent,
      element.querySelector('.authors-text').textContent,
      year,
      type,
    ].join(' '));
    return { element, year, type, searchable };
  });

  function refreshAuthors() {
    papers.forEach(({ element }) => {
      if (element.hidden || element.closest('.year-group').hidden) return;
      const text = element.querySelector('.authors-text');
      const button = element.querySelector('.authors-toggle');
      const expanded = text.classList.contains('expanded');
      const visible = expanded || text.scrollWidth > text.clientWidth + 1;
      button.hidden = !visible;
      button.classList.toggle('visible', visible);
    });
  }

  function update() {
    const words = normalize(state.query).split(' ').filter(Boolean);
    let count = 0;
    papers.forEach(paper => {
      const matchesType = state.type === 'all' || (state.type === 'other'
        ? !['Journal', 'Conference', 'Preprint'].includes(paper.type)
        : state.type === paper.type);
      const visible = (state.year === 'all' || paper.year === state.year)
        && matchesType && words.every(word => paper.searchable.includes(word));
      paper.element.hidden = !visible;
      if (visible) count++;
    });
    groups.forEach(group => {
      const visible = [...group.querySelectorAll('.paper')].filter(paper => !paper.hidden).length;
      group.hidden = visible === 0;
      group.querySelector('.group-count').textContent = String(visible);
    });
    [...groups].sort((a, b) => state.sort === 'newest'
      ? Number(b.dataset.year) - Number(a.dataset.year)
      : Number(a.dataset.year) - Number(b.dataset.year))
      .forEach(group => results.append(group));
    yearButtons.forEach(button => {
      const selected = button.dataset.year === state.year;
      button.classList.toggle('selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    typeButtons.forEach(button => {
      const selected = button.dataset.type === state.type;
      button.classList.toggle('selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    mobileYear.value = state.year;
    resultCount.textContent = `${count} ${count === 1 ? 'publication' : 'publications'}`;
    empty.hidden = count > 0;
    requestAnimationFrame(refreshAuthors);
  }

  search.addEventListener('input', () => { state.query = search.value; update(); });
  sort.addEventListener('change', () => { state.sort = sort.value; update(); });
  mobileYear.addEventListener('change', () => { state.year = mobileYear.value; update(); });
  yearButtons.forEach(button => button.addEventListener('click', () => {
    state.year = button.dataset.year;
    update();
  }));
  typeButtons.forEach(button => button.addEventListener('click', () => {
    state.type = button.dataset.type;
    update();
  }));
  page.querySelector('#reset-filters').addEventListener('click', () => {
    Object.assign(state, { query: '', year: 'all', type: 'all', sort: 'newest' });
    search.value = '';
    sort.value = 'newest';
    update();
    search.focus();
  });
  results.addEventListener('click', event => {
    const abstractButton = event.target.closest('.abstract-button');
    if (abstractButton) {
      const disclosure = document.getElementById(abstractButton.getAttribute('aria-controls'));
      disclosure.open = !disclosure.open;
      abstractButton.setAttribute('aria-expanded', String(disclosure.open));
      return;
    }
    const button = event.target.closest('.authors-toggle');
    if (!button) return;
    const target = document.getElementById(button.getAttribute('aria-controls'));
    const expanded = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(expanded));
    target.classList.toggle('expanded', expanded);
    button.textContent = expanded ? 'Fewer authors' : 'All authors';
    button.setAttribute('aria-label', `${expanded ? 'Collapse' : 'Show all'} authors: ${button.closest('.paper').querySelector('h3').textContent}`);
    refreshAuthors();
  });
  page.querySelectorAll('.abstract-button').forEach(button => {
    const disclosure = document.getElementById(button.getAttribute('aria-controls'));
    disclosure.addEventListener('toggle', () => {
      button.setAttribute('aria-expanded', String(disclosure.open));
    });
    disclosure.querySelector('.abstract-summary').hidden = true;
    button.hidden = false;
  });
  document.addEventListener('keydown', event => {
    const active = document.activeElement;
    if (event.key === '/' && !event.metaKey && !event.ctrlKey && !event.altKey
      && !['INPUT', 'TEXTAREA', 'SELECT'].includes(active.tagName) && !active.isContentEditable) {
      event.preventDefault();
      search.focus();
    }
  });
  window.addEventListener('resize', refreshAuthors);
  if (document.fonts) document.fonts.ready.then(refreshAuthors);
  page.classList.add('enhanced');
  page.querySelector('.toolbar').hidden = false;
  page.querySelector('#year-nav').hidden = false;
  update();
})();
