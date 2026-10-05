import { text, courseLabel, headerLabel } from './i18n.mjs';
import { buildTable, cellText, defaultFilters, experimentColumn, RATE_COLUMNS, sortColumns, toCSV } from './results.mjs';

const $ = id => document.getElementById(id);
const state = { language: 'TR', benchmark: '', tab: 'overall', catalog: {}, data: null, loading: true, error: false, filters: { overall: defaultFilters('overall'), course: defaultFilters('course') } };
const cache = new Map();
let requestNumber = 0;
const t = (key, values) => text(state.language, key, values);
const currentFilters = () => state.filters[state.tab];
function element(tag, content, className) {
  const node = document.createElement(tag);
  if (content !== undefined) node.textContent = content;
  if (className) node.className = className;
  return node;
}
function options(select, choices, selected) {
  select.replaceChildren(...choices.map(([label, value]) => new Option(label, value)));
  select.value = selected;
}
async function fetchJSON(path) {
  const response = await fetch(new URL(`../data/${path}`, import.meta.url));
  if (!response.ok) throw new Error(`Could not load benchmark data (${response.status}).`);
  return response.json();
}
function renderText() {
  document.documentElement.lang = state.language === 'TR' ? 'tr' : 'en';
  document.title = t('title');
  for (const [id, key] of Object.entries({ title:'title', intro:'intro', 'benchmark-label':'benchmark', 'tab-overall':'overall', 'tab-course':'course_accuracy', 'minimum-label':'minimum', 'order-label':'order', reset:'reset', download:'download', retry:'retry', 'filters-label':'filters', 'table-caption':'results' })) $(id).textContent = t(key);
  $('tabs').setAttribute('aria-label', t('tables'));
  $('table-scroll').setAttribute('aria-label', t('results'));
  $('minimum-number').setAttribute('aria-label', t('minimum'));
  $('error-message').textContent = t('error');
  document.querySelectorAll('[data-language]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.language === state.language)));
  options($('benchmark'), Object.entries(state.catalog).map(([key, entry]) => [entry.titles[state.language], key]), state.benchmark);
  $('benchmark').disabled = !Object.keys(state.catalog).length;
  renderStats();
}
function renderStats() {
  if (!state.data) { $('stats').textContent = state.loading ? t('loading') : ''; return; }
  $('stats').textContent = t('stats', {
    models: state.data.overall.length,
    questions: new Intl.NumberFormat(state.language === 'TR' ? 'tr-TR' : 'en-US').format(state.data.overall[0].Questions),
    courses: state.data.course.length,
  });
}
function multiFilter(containerId, key, labelKey, choices) {
  const host = $(containerId);
  host.replaceChildren();
  const label = element('span', t(labelKey), 'filter-label');
  label.id = `${containerId}-label`;
  const details = element('details', undefined, 'multi');
  const summary = element('summary');
  summary.setAttribute('aria-labelledby', label.id);
  function updateSummary() { summary.textContent = currentFilters()[key].length ? t('selected', { count: currentFilters()[key].length }) : t(key === 'models' ? 'all_models' : 'all_courses'); }
  updateSummary();
  const popup = element('div', undefined, 'multi-popup');
  const search = element('input');
  search.type = 'search'; search.placeholder = t('search'); search.setAttribute('aria-label', `${t(labelKey)} — ${t('search')}`);
  const list = element('div', undefined, 'multi-options');
  for (const [title, value] of choices) {
    const option = element('label');
    const checkbox = element('input');
    checkbox.type = 'checkbox'; checkbox.value = value; checkbox.checked = currentFilters()[key].includes(value);
    checkbox.addEventListener('change', () => {
      currentFilters()[key] = checkbox.checked ? [...currentFilters()[key], value] : currentFilters()[key].filter(item => item !== value);
      updateSummary(); renderTable();
    });
    option.append(checkbox, document.createTextNode(title)); list.append(option);
  }
  search.addEventListener('input', () => {
    const language = state.language === 'TR' ? 'tr' : 'en';
    const term = search.value.toLocaleLowerCase(language);
    for (const option of list.children) option.hidden = !option.textContent.toLocaleLowerCase(language).includes(term);
  });
  details.addEventListener('toggle', () => {
    if (details.open) document.querySelectorAll('.multi').forEach(other => { if (other !== details) other.open = false; });
  });
  popup.append(search, list, element('p', t(key === 'models' ? 'models_help' : 'courses_help'), 'multi-help'));
  details.append(summary, popup); host.append(label, details);
}
function renderControls() {
  const filters = currentFilters();
  document.querySelectorAll('[data-tab]').forEach(button => {
    const active = button.dataset.tab === state.tab;
    button.setAttribute('aria-selected', String(active)); button.tabIndex = active ? 0 : -1;
  });
  $('results-panel').setAttribute('aria-labelledby', `tab-${state.tab}`);
  $('course-filter').hidden = state.tab !== 'course';
  $('accuracy-filter').hidden = state.tab !== 'overall';
  $('sort-label').textContent = t(state.tab === 'overall' ? 'sort' : 'sort_courses');
  options($('order'), [[t('descending'), 'desc'], [t('ascending'), 'asc']], filters.direction);
  $('minimum').value = filters.minimum; $('minimum-number').value = filters.minimum;
  if (!state.data) return;
  multiFilter('model-filter', 'models', 'models', state.data.overall.map(row => [row.Model, row.Model]));
  multiFilter('course-filter', 'courses', 'courses', state.data.course.map(row => [courseLabel(row.Course, state.language), row.Course]));
  const modelLabels = new Map(state.data.overall.map(row => [experimentColumn(row), row.Model]));
  options($('sort'), sortColumns(state.data, state.tab).map(key => [state.tab === 'course' && modelLabels.has(key) ? modelLabels.get(key) : headerLabel(key, state.language, RATE_COLUMNS.has(key)), key]), filters.sort);
}
function renderTable() {
  const table = $('results');
  const head = table.querySelector('thead'); const body = table.querySelector('tbody');
  head.replaceChildren(); body.replaceChildren();
  $('filters').disabled = state.loading || !state.data;
  $('reset').disabled = state.loading || !state.data;
  $('download').disabled = state.loading || !state.data;
  $('error').hidden = !state.error;
  if (!state.data) { $('row-count').textContent = state.loading ? t('loading') : ''; $('empty').hidden = true; return; }
  const result = buildTable(state.data, state.tab, currentFilters(), state.language);
  $('row-count').textContent = state.language === 'EN' && result.rows.length === 1 ? '1 row' : t('rows', { count: result.rows.length });
  $('empty').hidden = result.rows.length !== 0; $('empty').textContent = t('empty');
  const headerRow = element('tr');
  result.columns.forEach(column => {
    const th = element('th', undefined, column.numeric ? 'numeric' : ''); th.scope = 'col';
    const active = currentFilters().sort === column.key;
    th.setAttribute('aria-sort', active ? (currentFilters().direction === 'asc' ? 'ascending' : 'descending') : 'none');
    const button = element('button', column.label); button.type = 'button';
    const arrow = element('span', active ? (currentFilters().direction === 'asc' ? '▲' : '▼') : ''); arrow.setAttribute('aria-hidden', 'true'); button.append(arrow);
    button.addEventListener('click', () => {
      const filters = currentFilters();
      filters.direction = filters.sort === column.key ? (filters.direction === 'asc' ? 'desc' : 'asc') : (column.numeric ? 'desc' : 'asc');
      filters.sort = column.key; $('sort').value = filters.sort; $('order').value = filters.direction; renderTable();
    });
    th.append(button); headerRow.append(th);
  });
  head.append(headerRow);
  const rows = document.createDocumentFragment();
  result.rows.forEach(values => {
    const row = element('tr');
    values.forEach((value, index) => {
      const column = result.columns[index];
      row.append(element('td', cellText(value, column, state.language), column.numeric ? 'numeric' : column.key === 'Model' ? 'model' : ''));
    });
    rows.append(row);
  });
  body.append(rows);
}
function render() { renderText(); renderControls(); renderTable(); }
async function selectBenchmark(id) {
  const request = ++requestNumber;
  state.benchmark = id; state.loading = true; state.error = false; state.data = null;
  state.filters = { overall: defaultFilters('overall'), course: defaultFilters('course') }; render();
  try {
    if (!cache.has(id)) {
      const directory = state.catalog[id].directory.split('/').map(encodeURIComponent).join('/');
      const [overall, course] = await Promise.all([fetchJSON(`${directory}/overall_comparison.json`), fetchJSON(`${directory}/course_accuracy_comparison.json`)]);
      if (!Array.isArray(overall) || !overall.length || !Array.isArray(course) || !course.length) throw new Error('Empty or invalid results.');
      cache.set(id, { overall, course });
    }
    if (request !== requestNumber) return;
    state.data = cache.get(id);
  } catch (error) {
    if (request !== requestNumber) return;
    state.error = true; console.error(error);
  }
  state.loading = false; render();
}
async function start() {
  state.loading = true; state.error = false; render();
  try {
    state.catalog = await fetchJSON('benchmarks.json');
    const first = Object.keys(state.catalog)[0];
    if (!first) throw new Error('The benchmark catalog is empty.');
    await selectBenchmark(first);
  } catch (error) { state.loading = false; state.error = true; console.error(error); render(); }
}
document.querySelectorAll('[data-language]').forEach(button => button.addEventListener('click', () => { state.language = button.dataset.language; render(); }));
document.querySelectorAll('[data-tab]').forEach(button => {
  button.addEventListener('click', () => { state.tab = button.dataset.tab; render(); });
  button.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const tab = event.key === 'Home' ? 'overall' : event.key === 'End' ? 'course' : state.tab === 'overall' ? 'course' : 'overall';
    $(`tab-${tab}`).click(); $(`tab-${tab}`).focus();
  });
});
$('benchmark').addEventListener('change', event => selectBenchmark(event.target.value));
for (const id of ['minimum', 'minimum-number']) $(id).addEventListener('input', event => {
  const value = Math.max(0, Math.min(100, Number(event.target.value) || 0));
  currentFilters().minimum = value; $('minimum').value = value; $('minimum-number').value = value; renderTable();
});
$('sort').addEventListener('change', event => { currentFilters().sort = event.target.value; renderTable(); });
$('order').addEventListener('change', event => { currentFilters().direction = event.target.value; renderTable(); });
$('reset').addEventListener('click', () => { state.filters[state.tab] = defaultFilters(state.tab); renderControls(); renderTable(); });
$('retry').addEventListener('click', () => state.benchmark && state.catalog[state.benchmark] ? selectBenchmark(state.benchmark) : start());
$('download').addEventListener('click', () => {
  const result = buildTable(state.data, state.tab, currentFilters(), state.language);
  const url = URL.createObjectURL(new Blob([toCSV(result)], { type: 'text/csv;charset=utf-8;' }));
  const anchor = element('a'); anchor.href = url; anchor.download = `${state.benchmark}-${state.tab}-${state.language.toLowerCase()}.csv`;
  document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
});
document.addEventListener('click', event => { document.querySelectorAll('.multi[open]').forEach(menu => { if (!menu.contains(event.target)) menu.open = false; }); });
document.addEventListener('keydown', event => { if (event.key === 'Escape') document.querySelectorAll('.multi[open]').forEach(menu => { menu.open = false; menu.querySelector('summary').focus(); }); });
start();
