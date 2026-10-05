import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { buildTable, defaultFilters, toCSV } from '../web/results.mjs';

const read = async name => JSON.parse(await readFile(new URL(`../data/university_entrance/${name}.json`, import.meta.url), 'utf8'));
const data = { overall: await read('overall_comparison'), course: await read('course_accuracy_comparison') };

test('both full tables preserve all source rows', () => {
  assert.equal(buildTable(data, 'overall', defaultFilters('overall'), 'TR').rows.length, 10);
  assert.equal(buildTable(data, 'course', defaultFilters('course'), 'TR').rows.length, 12);
});
test('model and accuracy filters compose and numeric sorting uses source precision', () => {
  const filters = { ...defaultFilters('overall'), models: ['qwen3.8:27b', 'muse-glimmer:30b', 'gemma3:27b'], minimum: 80 };
  const table = buildTable(data, 'overall', filters, 'EN');
  assert.deepEqual(table.rows.map(row => row[1]), ['muse-glimmer:30b', 'qwen3.8:27b']);
  assert.equal(table.columns.some(column => column.key === 'Questions'), false);
  filters.minimum = 89.7447;
  assert.equal(buildTable(data, 'overall', filters, 'EN').rows.length, 0);
});
test('course filter and model column selection match the source record', () => {
  const filters = { ...defaultFilters('course'), models: ['qwen3.8:27b'], courses: ['BİYOLOJİ'] };
  const table = buildTable(data, 'course', filters, 'TR');
  assert.equal(table.columns.length, 3);
  assert.deepEqual(table.rows, [['Biyoloji', 247, data.course[0]['Exp 3: qwen3.8:27b']]]);
});
test('course sorting follows translated names and directions', () => {
  const filters = { ...defaultFilters('course'), courses: ['GEOMETRİ', 'KİMYA'] };
  assert.deepEqual(buildTable(data, 'course', filters, 'EN').rows.map(row => row[0]), ['Chemistry', 'Geometry']);
  filters.direction = 'desc';
  assert.deepEqual(buildTable(data, 'course', filters, 'EN').rows.map(row => row[0]), ['Geometry', 'Chemistry']);
});
test('no results retains localized headers and a valid CSV', () => {
  const table = buildTable(data, 'overall', { ...defaultFilters('overall'), minimum: 100 }, 'TR');
  assert.equal(table.rows.length, 0);
  assert.match(toCSV(table), /"Doğruluk \(%\)"/);
  assert.equal(toCSV(table).split('\r\n').length, 2);
});
test('CSV contains localized filtered rows and correctly escaped cells', () => {
  const table = buildTable(data, 'course', { ...defaultFilters('course'), models: ['qwen3.8:27b'], courses: ['BİYOLOJİ'] }, 'EN');
  assert.match(toCSV(table), /"Biology","247","95.14"/);
  assert.equal(toCSV({columns:[{label:'A"B',rate:false}],rows:[['x,"y\nz']]}), '\uFEFF"A""B"\r\n"x,""y\nz"\r\n');
});
test('switching display language does not change or mutate numeric results', () => {
  const before = JSON.stringify(data);
  const filters = defaultFilters('overall');
  assert.deepEqual(buildTable(data, 'overall', filters, 'TR').rows, buildTable(data, 'overall', filters, 'EN').rows);
  assert.equal(JSON.stringify(data), before);
});
