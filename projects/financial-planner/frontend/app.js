const CATEGORY_COLORS = {
  Groceries:        '#00e676',
  'Dining & Drinking': '#ec407a',
  Subscriptions:    '#448aff',
  Shopping:         '#e040fb',
  Transportation:   '#ffea00',
  Entertainment:    '#00e5ff',
  Housing:          '#ff5252',
  Interest:         '#ef5350',
  Events:           '#ab47bc',
  Other:            '#78909c',
  Uncategorized:    '#ffc107',
};

let allCategories = [];
let currentSort = { key: 'date', dir: 'desc' };
let currentTransactions = [];
let chartInstance = null;

const currencyFormatter = new Intl.NumberFormat('en-CA', {
  style: 'currency',
  currency: 'CAD',
  minimumFractionDigits: 2,
});

// --- Init ---

document.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('refresh-btn').addEventListener('click', scanStatements);
  document.getElementById('month-selector').addEventListener('change', onFilterChange);
  document.getElementById('account-filter').addEventListener('change', onFilterChange);
  document.getElementById('category-filter').addEventListener('change', renderFromCache);
  document.getElementById('type-filter').addEventListener('change', renderFromCache);

  document.querySelectorAll('th.sortable').forEach(th => {
    th.addEventListener('click', () => onSort(th.dataset.sort));
  });

  allCategories = await fetchJSON('/categories');
  await Promise.all([loadMonths(), loadAccounts()]);
  populateCategoryFilter();
  await loadData();
});

// --- API helpers ---

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function selectedMonth() {
  return document.getElementById('month-selector').value;
}

function selectedAccount() {
  return document.getElementById('account-filter').value;
}

function selectedCategory() {
  return document.getElementById('category-filter').value;
}

function selectedType() {
  return document.getElementById('type-filter').value;
}

function populateCategoryFilter() {
  const sel = document.getElementById('category-filter');
  const cats = ['Uncategorized', ...allCategories, 'Payment', 'Interest'];
  cats.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    sel.appendChild(opt);
  });
}

function renderFromCache() {
  let filtered = currentTransactions;
  const cat = selectedCategory();
  const type = selectedType();
  if (cat) filtered = filtered.filter(t => t.category === cat);
  if (type === 'debit') filtered = filtered.filter(t => !t.is_credit);
  if (type === 'credit') filtered = filtered.filter(t => t.is_credit);
  renderTable(filtered);
}

// --- Data loading ---

async function populateSelect(elementId, endpoint, formatter) {
  const data = await fetchJSON(endpoint);
  const sel = document.getElementById(elementId);
  const current = sel.value;

  while (sel.options.length > 1) sel.remove(1);

  data.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item;
    opt.textContent = formatter ? formatter(item) : item;
    sel.appendChild(opt);
  });

  if (current && data.includes(current)) sel.value = current;
  return data;
}

async function loadMonths() {
  const months = await populateSelect('month-selector', '/months', formatMonth);
  // Default to latest month if none selected
  const sel = document.getElementById('month-selector');
  if (!sel.value && months.length > 0) sel.value = months[months.length - 1];
}

async function loadAccounts() {
  await populateSelect('account-filter', '/accounts');
}

async function loadData() {
  const month = selectedMonth();
  const account = selectedAccount();
  const params = new URLSearchParams();
  if (month) params.set('month', month);
  if (account) params.set('account', account);
  const query = params.toString() ? `?${params}` : '';

  document.getElementById('summary-cards').classList.add('loading');

  const [summary, transactions] = await Promise.all([
    fetchJSON(`/summary${query}`),
    fetchJSON(`/transactions${query}`),
  ]);

  document.getElementById('summary-cards').classList.remove('loading');
  currentTransactions = transactions;

  renderSummary(summary);
  renderChart(summary.by_category);
  renderTable(transactions);
}

// --- Scan ---

async function scanStatements() {
  const btn = document.getElementById('refresh-btn');
  btn.classList.add('scanning');
  btn.disabled = true;

  try {
    const result = await fetchJSON('/scan', { method: 'POST' });
    if (result.new_transactions > 0) {
      toast(`Imported ${result.new_transactions} transactions`, 'success');
      await Promise.all([loadMonths(), loadAccounts()]);
      await loadData();
    } else if (result.errors.length > 0) {
      toast(`Errors: ${result.errors.map(e => e.file).join(', ')}`, 'error');
    } else {
      toast('No new statements found', 'success');
    }
  } catch (err) {
    toast(`Scan failed: ${err.message}`, 'error');
  } finally {
    btn.classList.remove('scanning');
    btn.disabled = false;
  }
}

// --- Render: Summary ---

function renderSummary(s) {
  document.getElementById('total-spent').textContent = fmtCurrency(s.total_expenses);
  document.getElementById('total-credits').textContent = fmtCurrency(s.total_credits);
  document.getElementById('net-amount').textContent = fmtCurrency(s.net);
  document.getElementById('txn-count').textContent = s.transaction_count;
}

// --- Render: Chart ---

function renderChart(byCategory) {
  const entries = Object.entries(byCategory)
    .filter(([, v]) => v > 0)
    .sort((a, b) => b[1] - a[1]);

  const labels = entries.map(([k]) => k);
  const data = entries.map(([, v]) => v);
  const colors = labels.map(l => CATEGORY_COLORS[l] || '#555');

  const ctx = document.getElementById('category-chart').getContext('2d');

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderColor: 'transparent',
        borderWidth: 0,
        hoverBorderColor: '#fff',
        hoverBorderWidth: 2,
        spacing: 2,
      }],
    },
    options: {
      cutout: '68%',
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#111114',
          borderColor: '#1e1e24',
          borderWidth: 1,
          titleFont: { family: "'JetBrains Mono'", size: 11 },
          bodyFont: { family: "'JetBrains Mono'", size: 11 },
          padding: 10,
          cornerRadius: 4,
          callbacks: {
            label: ctx => ` ${fmtCurrency(ctx.raw)}`,
          },
        },
      },
    },
  });

  // Custom legend
  const legendEl = document.getElementById('chart-legend');
  legendEl.innerHTML = entries.map(([cat, val]) => `
    <div class="legend-item">
      <span class="legend-label">
        <span class="legend-dot" style="background:${CATEGORY_COLORS[cat] || '#555'}"></span>
        ${cat}
      </span>
      <span class="legend-value">${fmtCurrency(val)}</span>
    </div>
  `).join('');
}

// --- Render: Table ---

function renderTable(transactions) {
  const sorted = sortTransactions(transactions, currentSort.key, currentSort.dir);
  const tbody = document.getElementById('txn-body');
  document.getElementById('table-count').textContent = `${sorted.length} items`;

  if (sorted.length === 0) {
    tbody.innerHTML = `
      <tr><td colspan="4">
        <div class="empty-state">
          <p>No transactions yet</p>
          <p class="hint">Drop PDF statements into data/statements/ and click Scan</p>
        </div>
      </td></tr>`;
    return;
  }

  tbody.innerHTML = sorted.map(t => {
    const isUncat = t.category === 'Uncategorized';
    const isCredit = t.is_credit;

    return `
      <tr class="${isUncat ? 'uncategorized' : ''}">
        <td class="col-date">${formatDate(t.date)}</td>
        <td class="col-vendor">${escapeHtml(t.vendor_name)}</td>
        <td class="col-category">
          <select class="cat-select" data-vendor="${escapeAttr(t.vendor_name)}" aria-label="Category for ${escapeAttr(t.vendor_name)}">
            ${buildCategoryOptions(t.category)}
          </select>
        </td>
        <td class="col-amount ${isCredit ? 'credit' : ''}">${fmtCurrency(t.amount)}</td>
      </tr>`;
  }).join('');

  tbody.addEventListener('change', onCategoryChange);

  // Update sort indicators
  document.querySelectorAll('th.sortable').forEach(th => {
    th.classList.remove('active', 'asc', 'desc');
    if (th.dataset.sort === currentSort.key) {
      th.classList.add('active', currentSort.dir);
    }
  });
}

function buildCategoryOptions(selected) {
  const cats = ['Uncategorized', ...allCategories, 'Payment', 'Interest'];
  return cats.map(c =>
    `<option value="${c}" ${c === selected ? 'selected' : ''}>${c}</option>`
  ).join('');
}

// --- Sorting ---

function onSort(key) {
  if (currentSort.key === key) {
    currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
  } else {
    currentSort.key = key;
    currentSort.dir = key === 'amount' ? 'desc' : 'asc';
  }
  renderFromCache();
}

function sortTransactions(txns, key, dir) {
  const sorted = [...txns];
  const mult = dir === 'asc' ? 1 : -1;

  sorted.sort((a, b) => {
    switch (key) {
      case 'date':
        return mult * a.date.localeCompare(b.date);
      case 'vendor':
        return mult * a.vendor_name.localeCompare(b.vendor_name);
      case 'category':
        return mult * a.category.localeCompare(b.category);
      case 'amount': {
        const aVal = a.is_credit ? -a.amount : a.amount;
        const bVal = b.is_credit ? -b.amount : b.amount;
        return mult * (aVal - bVal);
      }
      default:
        return 0;
    }
  });
  return sorted;
}

// --- Category change ---

async function onCategoryChange(e) {
  if (!e.target.classList.contains('cat-select')) return;

  const vendor = e.target.dataset.vendor;
  const category = e.target.value;

  try {
    await fetchJSON('/categorize', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vendor_name: vendor, category }),
    });
    toast(`${vendor} \u2192 ${category}`, 'success');
    await loadData();
  } catch (err) {
    toast(`Failed to update: ${err.message}`, 'error');
  }
}

// --- Filter changes ---

function onFilterChange() {
  loadData();
}

// --- Toast ---

function toast(msg, type = 'success') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = `toast visible ${type}`;
  clearTimeout(el._timeout);
  el._timeout = setTimeout(() => {
    el.className = 'toast';
  }, 3000);
}

// --- Formatters ---

function fmtCurrency(n) {
  return currencyFormatter.format(n);
}

function formatMonth(ym) {
  const [y, m] = ym.split('-');
  const date = new Date(Number(y), Number(m) - 1);
  return date.toLocaleDateString('en-CA', { month: 'long', year: 'numeric' });
}

function formatDate(iso) {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('en-CA', { month: 'short', day: 'numeric' });
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function escapeAttr(s) {
  return s.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
