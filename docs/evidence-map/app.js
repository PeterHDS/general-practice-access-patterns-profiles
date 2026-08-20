const search = document.getElementById('search');
const domain = document.getElementById('domain');
const support = document.getElementById('support');
const clear = document.getElementById('clear');
const cards = [...document.querySelectorAll('.claim-card')];
const count = document.getElementById('count');
const empty = document.getElementById('empty');

function update() {
  const term = search.value.trim().toLowerCase();
  let visible = 0;
  for (const card of cards) {
    const matches = (!term || card.dataset.search.includes(term))
      && (!domain.value || card.dataset.domain === domain.value)
      && (!support.value || card.dataset.support === support.value);
    card.hidden = !matches;
    visible += Number(matches);
  }
  count.textContent = `${visible} ${visible === 1 ? 'claim' : 'claims'} shown`;
  empty.hidden = visible !== 0;
}

for (const control of [search, domain, support]) {
  control.addEventListener('input', update);
}
clear.addEventListener('click', () => {
  search.value = '';
  domain.value = '';
  support.value = '';
  update();
  search.focus();
});
