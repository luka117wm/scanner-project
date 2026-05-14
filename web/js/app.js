/**
 * app.js — логика UI: тема, качество, папка, сканирование, SSE прогресс, экспорт.
 */
import { loadPLY, setMode, setViewMode, fitCamera } from './viewer.js';

// ── UI-элементы ────────────────────────────────────────────────────────────────
const folderPath    = document.getElementById('folderPath');
const folderBtn     = document.getElementById('folderBtn');
const startBtn      = document.getElementById('startBtn');
const startLabel    = document.getElementById('startLabel');
const progressFill  = document.getElementById('progressFill');
const progressLabel = document.getElementById('progressLabel');
const progressPct   = document.getElementById('progressPct');
const logEl         = document.getElementById('log');
const toolBtns      = document.querySelectorAll('.tool-btn');
const exportStl     = document.getElementById('exportStl');
const exportObj     = document.getElementById('exportObj');
const stlDialog     = document.getElementById('stlDialog');

let eventSource   = null;
let _activeScanId = null;
let _selectedQ    = 'medium';

// ── Тема ───────────────────────────────────────────────────────────────────────
document.getElementById('themeSeg').querySelectorAll('button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.getElementById('themeSeg').querySelectorAll('button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    document.documentElement.dataset.theme = btn.dataset.themeSet;
  });
});

// ── Режим просмотра (topbar) ───────────────────────────────────────────────────
document.getElementById('viewSeg').querySelectorAll('button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.getElementById('viewSeg').querySelectorAll('button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    setViewMode(btn.dataset.view);
  });
});

// ── Кнопки вьюпорта ───────────────────────────────────────────────────────────
document.getElementById('vt-fit').addEventListener('click', fitCamera);

// ── Качество ───────────────────────────────────────────────────────────────────
document.getElementById('qualitySelector').querySelectorAll('.q-card').forEach(card => {
  card.addEventListener('click', () => {
    document.getElementById('qualitySelector').querySelectorAll('.q-card').forEach(c => c.classList.remove('on'));
    card.classList.add('on');
    _selectedQ = card.dataset.q;
  });
});

// ── Правая панель — табы ───────────────────────────────────────────────────────
let _logPolling = null;

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('on'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('on'));
    tab.classList.add('on');
    const panel = document.querySelector(`.tab-panel[data-panel="${tab.dataset.tab}"]`);
    if (panel) panel.classList.add('on');

    if (tab.dataset.tab === 'log') {
      refreshServerLog();
      if (!_logPolling) _logPolling = setInterval(refreshServerLog, 3000);
    } else {
      clearInterval(_logPolling);
      _logPolling = null;
    }
  });
});

// ── Фильтр лога ────────────────────────────────────────────────────────────────
let _logLines = [];
document.getElementById('logFilter').addEventListener('input', (e) => {
  _renderServerLog(e.target.value.trim());
});

async function refreshServerLog() {
  const el = document.getElementById('serverLog');
  if (!el) return;
  const panel = el.closest('.tab-panel');
  if (!panel?.classList.contains('on')) return;
  try {
    const { lines } = await fetch('/api/logs?n=400').then(r => r.json());
    _logLines = lines;
    _renderServerLog(document.getElementById('logFilter')?.value?.trim() ?? '');
  } catch { /* недоступен */ }
}

function _renderServerLog(filter) {
  const el = document.getElementById('serverLog');
  if (!el) return;
  const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
  const shown = filter
    ? _logLines.filter(l => l.toLowerCase().includes(filter.toLowerCase()))
    : _logLines;
  el.textContent = shown.join('\n');
  if (atBottom) el.scrollTop = el.scrollHeight;
}

// ── Выбор папки ────────────────────────────────────────────────────────────────
let _pywebviewReady = !!window.pywebview?.api;
window.addEventListener('pywebviewready', () => { _pywebviewReady = true; });

folderBtn.addEventListener('click', async () => {
  if (_pywebviewReady && window.pywebview?.api?.get_folder) {
    const path = await window.pywebview.api.get_folder();
    if (path) folderPath.value = path;
  } else {
    const path = prompt('Путь к папке с фотографиями:', folderPath.value);
    if (path !== null && path.trim()) folderPath.value = path.trim();
  }
});

folderPath.addEventListener('keydown', (e) => { if (e.key === 'Enter') startBtn.click(); });

// ── Запуск сканирования ────────────────────────────────────────────────────────
startBtn.addEventListener('click', () => {
  const dir = folderPath.value.trim();
  if (!dir) { addLog('Укажите путь к папке с фотографиями'); return; }
  startScan(dir);
});

async function startScan(imagesDir) {
  setUIState('scanning');
  _resetStages();
  addLog('Подключение...');

  try {
    const resp = await fetch('/api/scan/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ images_dir: imagesDir, quality: _selectedQ }),
    });

    if (resp.status === 409) { addLog('Пайплайн уже запущен'); setUIState('idle'); return; }
    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      throw new Error(body.detail ?? `HTTP ${resp.status}`);
    }

    addLog('Запущено');
    connectSSE();
  } catch (err) {
    addLog(`Ошибка: ${err.message}`);
    setUIState('idle');
  }
}

// ── SSE прогресс ───────────────────────────────────────────────────────────────
function connectSSE() {
  if (eventSource) eventSource.close();
  eventSource = new EventSource('/api/scan/stream');

  eventSource.onmessage = (e) => {
    const data = JSON.parse(e.data);
    updateProgress(data.progress ?? 0, data.step ?? '');
    _updateStages(data.step, data.progress);

    if (data.status === 'done') {
      close_sse();
      setUIState('done');
      addLog('Загружаю облако точек...');
      document.dispatchEvent(new CustomEvent('remesh-done'));
      loadPLY('/api/result/ply')
        .then(async () => {
          addLog('Готово');
          const st = await fetch('/api/status').then(r => r.json()).catch(() => ({}));
          _activeScanId = st.scan_id ?? null;
          if (st.images_dir) folderPath.value = st.images_dir;
          _setStatus('done', `Скан #${_activeScanId ?? '?'}`);
          _markAllStagesDone();
          await loadHistory();
        })
        .catch((err) => addLog(`Ошибка загрузки PLY: ${err.message}`));
    } else if (data.status === 'error') {
      close_sse();
      addLog(`Ошибка: ${data.error ?? 'unknown'}`);
      setUIState('idle');
      _setStatus('error', 'Ошибка пайплайна');
    }
  };

  eventSource.onerror = () => {
    close_sse();
    addLog('Соединение прервано');
    setUIState('idle');
  };
}

function close_sse() {
  if (eventSource) { eventSource.close(); eventSource = null; }
}

// ── Кнопки инструментов ────────────────────────────────────────────────────────
toolBtns.forEach((btn) => {
  btn.addEventListener('click', () => {
    toolBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    setMode(btn.dataset.mode);
  });
});

document.addEventListener('remesh-started', () => {
  setUIState('scanning');
  connectSSE();
});
document.addEventListener('remesh-done', () => {
  const btn = document.getElementById('dnRemesh');
  if (btn) btn.disabled = false;
});

// ── Экспорт STL ────────────────────────────────────────────────────────────────
exportStl.addEventListener('click', () => stlDialog.showModal());
document.getElementById('dlgCancel').addEventListener('click', () => stlDialog.close());

document.getElementById('dlgExport').addEventListener('click', async () => {
  const height_mm = parseFloat(document.getElementById('dlgHeight').value) || 100;
  const add_base  = document.getElementById('dlgBase').checked;
  stlDialog.close();

  exportStl.disabled = true;
  addLog('Генерация STL...');
  try {
    const r = await fetch('/api/export/stl', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ height_mm, add_base }),
    });
    if (!r.ok) { const b = await r.json().catch(() => ({})); throw new Error(b.detail ?? `HTTP ${r.status}`); }
    addLog('Скачивание model.stl...');
    _triggerDownload('/api/export/download/stl', 'model.stl');
  } catch (err) {
    addLog(`Ошибка STL: ${err.message}`);
  } finally {
    exportStl.disabled = false;
  }
});

// ── Экспорт OBJ ────────────────────────────────────────────────────────────────
let exportSrc = null;

exportObj.addEventListener('click', async () => {
  const imagesDir = folderPath.value.trim();
  if (!imagesDir) { addLog('Укажите папку с фотографиями'); return; }

  exportObj.disabled = true;
  addLog('Запуск текстурирования...');
  try {
    const r = await fetch('/api/export/obj-texture', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ images_dir: imagesDir }),
    });
    if (r.status === 409) { addLog('Текстурирование уже запущено'); exportObj.disabled = false; return; }
    if (!r.ok) { const b = await r.json().catch(() => ({})); throw new Error(b.detail ?? `HTTP ${r.status}`); }
    _connectExportSSE();
  } catch (err) {
    addLog(`Ошибка OBJ: ${err.message}`);
    exportObj.disabled = false;
  }
});

const _EXPORT_LABELS = {
  tex_undistort: 'Undistort', tex_stereo: 'Стерео-глубина',
  tex_fusion: 'Слияние',     tex_map: 'Маппинг текстуры',
  tex_fallback: 'OBJ (без текстуры)', tex_zip: 'Упаковка ZIP', done: 'Готово',
};

function _connectExportSSE() {
  if (exportSrc) exportSrc.close();
  exportSrc = new EventSource('/api/export/stream');
  exportSrc.onmessage = (e) => {
    const d = JSON.parse(e.data);
    const pct = Math.round((d.progress ?? 0) * 100);
    const label = _EXPORT_LABELS[d.step] ?? d.step;
    if (label) addLog(`${label}${pct ? ' ' + pct + '%' : ''}`);
    if (d.status === 'done') {
      _closeExportSSE();
      addLog('Скачивание texture_export.zip...');
      _triggerDownload('/api/export/download/obj', 'texture_export.zip');
      exportObj.disabled = false;
    } else if (d.status === 'error') {
      _closeExportSSE();
      addLog(`Ошибка текстуры: ${d.error ?? 'unknown'}`);
      exportObj.disabled = false;
    }
  };
  exportSrc.onerror = () => { _closeExportSSE(); addLog('Соединение экспорта прервано'); exportObj.disabled = false; };
}
function _closeExportSSE() { if (exportSrc) { exportSrc.close(); exportSrc = null; } }

function _triggerDownload(url, filename) {
  const a = Object.assign(document.createElement('a'), { href: url, download: filename });
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// ── История сканов ─────────────────────────────────────────────────────────────
async function loadHistory() {
  const list = document.getElementById('historyList');
  try {
    const scans = await fetch('/api/scans').then(r => r.json());

    const countEl = document.getElementById('historyCount');
    if (countEl) countEl.textContent = scans.length;

    if (!scans.length) {
      list.innerHTML = '<div class="scan-empty">Нет сканов</div>';
      return;
    }

    list.innerHTML = scans.map(s => {
      const active = s.id === _activeScanId ? ' active' : '';
      const date   = s.created_at ? s.created_at.slice(5, 16).replace('T', ' ') : '';
      const photos = s.n_images   ? `${s.n_images} фото` : '';
      const meta   = [photos, date].filter(Boolean).join(' · ');
      const statusClass = s.status === 'done' ? 'ok' : s.status === 'error' ? 'fail' : '';
      const statusText  = s.status === 'done' ? 'DONE' : s.status === 'error' ? 'FAIL' : s.status;

      return `<div class="scan-card${s.status === 'done' ? '' : ' undone'}${active}" data-id="${s.id}">
        <div class="scan-thumb"></div>
        <div>
          <div class="scan-name">${s.name}</div>
          <div class="scan-meta">${meta}</div>
        </div>
        <span class="scan-status ${statusClass}">${statusText}</span>
      </div>`;
    }).join('');

    list.querySelectorAll('.scan-card:not(.undone)').forEach(el => {
      el.addEventListener('click', () => _loadScan(parseInt(el.dataset.id)));
    });
  } catch { /* сервер недоступен */ }
}

async function _loadScan(id) {
  const r = await fetch(`/api/scans/${id}/load`, { method: 'POST' });
  if (!r.ok) { addLog('Не удалось загрузить скан'); return; }
  const data = await r.json();
  if (data.images_dir) folderPath.value = data.images_dir;
  _activeScanId = id;
  setUIState('done');
  addLog('Загрузка облака...');
  _setStatus('done', `Скан #${id}`);
  try {
    await loadPLY('/api/result/ply?' + Date.now());
    addLog('Готово');
    await loadHistory();
  } catch (e) { addLog(`Ошибка PLY: ${e.message}`); }
}

// ── Stages helpers ─────────────────────────────────────────────────────────────
const _STAGE_MAP = {
  extract_frames: 'stg-extract',
  colmap:         'stg-colmap',
  point_cloud:    'stg-colmap',
  poisson:        'stg-mesh',
  mesh_repair:    'stg-mesh',
  print_prep:     'stg-mesh',
  export:         'stg-export',
  done:           'stg-export',
};

let _activeStage = null;

function _resetStages() {
  document.querySelectorAll('.stage-row').forEach(row => {
    row.className = 'stage-row';
    const pct = row.querySelector('.stage-pct');
    if (pct) pct.textContent = '—';
  });
  _activeStage = null;
}

function _updateStages(step, progress) {
  const stageId = _STAGE_MAP[step];
  if (!stageId) return;

  const stageEl = document.getElementById(stageId);
  if (!stageEl) return;

  if (_activeStage && _activeStage !== stageId) {
    const prev = document.getElementById(_activeStage);
    if (prev) { prev.className = 'stage-row s-done'; const p = prev.querySelector('.stage-pct'); if (p) p.textContent = '100%'; }
  }

  _activeStage = stageId;
  stageEl.className = 'stage-row s-now';
  const pct = stageEl.querySelector('.stage-pct');
  if (pct) pct.textContent = step === 'done' ? '100%' : Math.round(progress * 100) + '%';
}

function _markAllStagesDone() {
  document.querySelectorAll('.stage-row').forEach(row => {
    row.className = 'stage-row s-done';
    const p = row.querySelector('.stage-pct'); if (p) p.textContent = '100%';
  });
}

// ── Statusbar ──────────────────────────────────────────────────────────────────
function _setStatus(state, text) {
  const dot  = document.getElementById('statusDot');
  const span = document.getElementById('statusText');
  if (dot) {
    dot.className = 'status-dot';
    if (state === 'running') dot.classList.add('running');
    if (state === 'error')   dot.classList.add('error');
  }
  if (span) span.textContent = text ?? 'Готов';
}

// ── Вспомогательные ────────────────────────────────────────────────────────────
const STEP_LABELS = {
  extract_frames: 'Извлечение кадров',
  colmap:         'COLMAP',
  point_cloud:    'Облако точек',
  poisson:        'Poisson mesh',
  mesh_repair:    'Ремонт меша',
  print_prep:     'Подготовка к печати',
  export:         'Экспорт',
  done:           'Готово',
};

function updateProgress(value, step) {
  const pct = Math.round(value * 100);
  progressFill.style.width = `${pct}%`;
  const label = STEP_LABELS[step] ?? step;
  progressLabel.textContent = label || '—';
  progressPct.textContent   = label ? `${pct}%` : '';
}

function addLog(msg) {
  const ts    = new Date().toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const lines = (logEl.textContent || '').split('\n').filter(Boolean);
  lines.push(`[${ts}] ${msg}`);
  if (lines.length > 20) lines.splice(0, lines.length - 20);
  logEl.textContent = lines.join('\n');
  logEl.scrollTop   = logEl.scrollHeight;
}

function setUIState(state) {
  const scanning = state === 'scanning';
  const done     = state === 'done';

  startBtn.disabled = scanning;
  startBtn.classList.toggle('idle', !scanning);
  startLabel.textContent = scanning ? 'Обработка...' : 'Начать сканирование';

  toolBtns.forEach(b => { b.disabled = !done; });
  exportStl.disabled = !done;
  exportObj.disabled = !done;

  if (!scanning) updateProgress(0, '');

  if (scanning) _setStatus('running', 'Обработка...');
  else if (!done) _setStatus('idle', 'Готов');
}

// ── Инициализация ──────────────────────────────────────────────────────────────
(async () => {
  try {
    const st = await fetch('/api/status').then(r => r.json());
    _activeScanId = st.scan_id ?? null;
    if (st.images_dir) folderPath.value = st.images_dir;
    if (st.status === 'done') {
      setUIState('done');
      _setStatus('done', `Скан #${_activeScanId ?? '?'}`);
      addLog('Загрузка облака...');
      await loadPLY('/api/result/ply?' + Date.now());
      addLog('Готово');
    }
  } catch { /* сервер недоступен */ }
  await loadHistory();
})();
