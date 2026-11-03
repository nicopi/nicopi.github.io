(() => {
  const page = document.querySelector('.patents-page');
  if (!page) return;
  const buttons = [...page.querySelectorAll('[data-patent-year]')];
  const select = page.querySelector('#patents-year');
  const groups = [...page.querySelectorAll('.patent-year-group')];
  const update = year => {
    groups.forEach(group => { group.hidden = year !== 'all' && group.dataset.year !== year; });
    buttons.forEach(button => {
      const selected = button.dataset.patentYear === year;
      button.classList.toggle('selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    select.value = year;
  };
  buttons.forEach(button => button.addEventListener('click', () => update(button.dataset.patentYear)));
  select.addEventListener('change', () => update(select.value));
})();
