import { courseLabel, headerLabel } from './i18n.mjs';

export const RATE_COLUMNS = new Set(['Accuracy', 'Valid-answer rate', 'Accuracy among valid predictions']);
export function defaultFilters(tab) {
  return { models: [], courses: [], minimum: 0, sort: tab === 'overall' ? 'Accuracy' : 'Course', direction: tab === 'overall' ? 'desc' : 'asc' };
}
export function experimentColumn(row) {
  return `Exp ${row.Experiment}: ${row.Model}`;
}
export function sortColumns(data, tab) {
  return tab === 'overall'
    ? Object.keys(data.overall[0]).filter(key => key !== 'Questions')
    : ['Course', 'Questions', ...data.overall.map(experimentColumn)];
}
export function buildTable(data, tab, filters, language) {
  const rates = tab === 'overall' ? RATE_COLUMNS : new Set(data.overall.map(experimentColumn));
  let columns = sortColumns(data, tab);
  let rows;
  if (tab === 'overall') {
    rows = data.overall.filter(row => (!filters.models.length || filters.models.includes(row.Model)) && row.Accuracy >= filters.minimum / 100);
  } else {
    const visible = new Set(data.overall.filter(row => !filters.models.length || filters.models.includes(row.Model)).map(experimentColumn));
    columns = columns.filter(key => key === 'Course' || key === 'Questions' || visible.has(key));
    rows = data.course.filter(row => !filters.courses.length || filters.courses.includes(row.Course));
  }
  const collator = new Intl.Collator(language === 'TR' ? 'tr' : 'en', { sensitivity: 'base', numeric: true });
  rows = [...rows].sort((a, b) => {
    let av = a[filters.sort], bv = b[filters.sort];
    if (filters.sort === 'Course') {
      av = courseLabel(av, language); bv = courseLabel(bv, language);
    }
    const comparison = typeof av === 'number' && typeof bv === 'number' ? av - bv : collator.compare(String(av), String(bv));
    return filters.direction === 'asc' ? comparison : -comparison;
  });
  return {
    columns: columns.map(key => ({ key, label: headerLabel(key, language, rates.has(key)), rate: rates.has(key), numeric: key !== 'Model' && key !== 'Course' })),
    rows: rows.map(row => columns.map(key => key === 'Course' ? courseLabel(row[key], language) : row[key])),
  };
}
export function cellText(value, column, language) {
  if (typeof value !== 'number') return String(value ?? '');
  return new Intl.NumberFormat(language === 'TR' ? 'tr-TR' : 'en-US', column.rate
    ? { style: 'percent', minimumFractionDigits: 2, maximumFractionDigits: 2 }
    : { maximumFractionDigits: 0 }).format(value);
}
export function toCSV(table) {
  const quote = value => `"${String(value ?? '').replaceAll('"', '""')}"`;
  return '\uFEFF' + [
    table.columns.map(column => quote(column.label)).join(','),
    ...table.rows.map(row => row.map((value, index) => quote(table.columns[index].rate ? (value * 100).toFixed(2) : value)).join(',')),
  ].join('\r\n') + '\r\n';
}
