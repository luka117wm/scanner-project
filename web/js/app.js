/**
 * app.js — логика UI: выбор папки, запуск сканирования, SSE прогресс, инструменты.
 */
import { loadPLY, setMode } from './viewer.js';

// ── UI-элементы ────────────────────────────────────────────────────────────────
const folderPath    = document.getElementById('folderPath');
const folderBtn     = document.getElementById('folderBtn');
const startBtn      = document.getElementById('startBtn');
const progressFill  = document.getElementById('progressFill');
const progressLabel = document.getElementById('progressLabel');
const logEl         = document.getElementById('log');
const toolBtns      = document.querySelectorAll('.tool-btn');
const exportStl     = document.getElementById('exportStl');
const exportObj     = document.getElementById('exportObj');

let eventSource  = null;
let _activeScanId = null;

// ── Выбор папки ────────────────────────────────────────────────────────────────

// pywebview инжектирует API асинхронно — ждём события готовности
let _pywebviewReady = !!window.pywebview?.api;
window.addEventListener('pywebviewready', () => { _pywebviewReady = true; });

folderBtn.addEventListener('click', async () => {
  if (_pywebviewReady && window.pywebview?.api?.get_folder) {
    const path = await window.pywebview.api.get_folder();
    if (path) folderPath.value = path;
  } else {
    // Браузер: нативный prompt
    const cur  = folderPath.value;
    const path = prompt('Путь к папке с фотографиями:', cur);
    if (path !== null && path.trim()) folderPath.value = path.trim();
  }
});

// Enter в поле пути → старт
folderPath.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') startBtn.click();
});

// ── Запуск сканирования ────────────────────────────────────────────────────────
startBtn.addEventListener('click', () => {
  const dir = folderPath.value.trim();
  if (!dir) {
    addLog('Укажите путь к папке с фотографиями');
    return;
  }
  startScan(dir);
});

async function startScan(imagesDir) {
  setUIState('scanning');
  addLog('Подключение...');

  try {
    const resp = await fetch('/api/scan/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ images_dir: imagesDir }),
    });

    if (resp.status === 409) {
      addLog('Пайплайн уже запущен');
      setUIState('idle');
      return;
    }
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
          await loadHistory();
        })
        .catch((err) => addLog(`Ошибка загрузки PLY: ${err.message}`));
    } else if (data.status === 'error') {
      close_sse();
      addLog(`Ошибка: ${data.error ?? 'unknown'}`);
      setUIState('idle');
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
    toolBtns.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    setMode(btn.dataset.mode);
  });
});

// Remesh — перезапускаем SSE когда viewer сигналит о старте
document.addEventListener('remesh-started', () => {
  setUIState('scanning');
  connectSSE();
});

// Когда после remesh SSE приходит done — разблокируем кнопку Пересчитать
document.addEventListener('remesh-done', () => {
  const btn = document.getElementById('dnRemesh');
  if (btn) btn.disabled = false;
});

// ── Экспорт STL ────────────────────────────────────────────────────────────────
const stlDialog = document.getElementById('stlDialog');

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
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ height_mm, add_base }),
    });
    if (!r.ok) {
      const b = await r.json().catch(() => ({}));
      throw new Error(b.detail ?? `HTTP ${r.status}`);
    }
    addLog('Скачивание model.stl...');
    _triggerDownload('/api/export/download/stl', 'model.stl');
  } catch (err) {
    addLog(`Ошибка STL: ${err.message}`);
  } finally {
    exportStl.disabled = false;
  }
});

// ── Экспорт OBJ + текстура ────────────────────────────────────────────────────
let exportSrc = null;

exportObj.addEventListener('click', async () => {
  const imagesDir = folderPath.value.trim();
  if (!imagesDir) { addLog('Укажите папку с фотографиями'); return; }

  exportObj.disabled = true;
  addLog('Запуск текстурирования...');
  try {
    const r = await fetch('/api/export/obj-texture', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ images_dir: imagesDir }),
    });
    if (r.status === 409) { addLog('Текстурирование уже запущено'); exportObj.disabled = false; return; }
    if (!r.ok) {
      const b = await r.json().catch(() => ({}));
      throw new Error(b.detail ?? `HTTP ${r.status}`);
    }
    _connectExportSSE();
  } catch (err) {
    addLog(`Ошибка OBJ: ${err.message}`);
    exportObj.disabled = false;
  }
});

const _EXPORT_LABELS = {
  tex_undistort: 'Undistort',
  tex_stereo:    'Стерео-глубина',
  tex_fusion:    'Слияние',
  tex_map:       'Маппинг текстуры',
  tex_fallback:  'OBJ (без текстуры)',
  tex_zip:       'Упаковка ZIP',
  done:          'Готово',
};

function _connectExportSSE() {
  if (exportSrc) exportSrc.close();
  exportSrc = new EventSource('/api/export/stream');

  exportSrc.onmessage = (e) => {
    const d     = JSON.parse(e.data);
    const pct   = Math.round((d.progress ?? 0) * 100);
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

  exportSrc.onerror = () => {
    _closeExportSSE();
    addLog('Соединение экспорта прервано');
    exportObj.disabled = false;
  };
}

function _closeExportSSE() {
  if (exportSrc) { exportSrc.close(); exportSrc = null; }
}

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
    if (!scans.length) {
      list.innerHTML = '<div class="scan-item-empty">Нет сканов</div>';
      return;
    }
    list.innerHTML = scans.map(s => {
      const active = s.id === _activeScanId ? ' active' : '';
      const date   = s.created_at ? s.created_at.slice(5, 16).replace('T', ' ') : '';
      const photos = s.n_images   ? `${s.n_images} фото` : '';
      const meta   = [photos, date].filter(Boolean).join(' · ');
      return `<div class="scan-item ${s.status}${active}" data-id="${s.id}">
        <div class="scan-item-name">${s.name}</div>
        <div class="scan-item-meta">${meta}</div>
      </div>`;
    }).join('');

    list.querySelectorAll('.scan-item.done').forEach(el => {
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
  try {
    await loadPLY('/api/result/ply?' + Date.now());
    addLog('Готово');
    await loadHistory();
  } catch (e) { addLog(`Ошибка PLY: ${e.message}`); }
}

// Переключение секции истории
document.getElementById('historyToggle').addEventListener('click', () => {
  const list = document.getElementById('historyList');
  const tog  = document.getElementById('historyToggle');
  const open = list.style.display !== 'none';
  list.style.display = open ? 'none' : '';
  tog.textContent = (open ? 'История сканов ▸' : 'История сканов ▾');
});

// ── Лог пайплайна ────────────────────────────────────────────────────────────────

let _serverLogTimer = null;

async function refreshServerLog() {
  const el = document.getElementById('serverLog');
  if (!el || el.style.display === 'none') return;
  try {
    const { lines } = await fetch('/api/logs?n=300').then(r => r.json());
    const atBottom  = el.scrollHeight - el.scrollTop - el.clientHeight < 30;
    el.textContent  = lines.join('\n');
    if (atBottom) el.scrollTop = el.scrollHeight;
  } catch { /* сервер недоступен */ }
}

document.getElementById('serverLogToggle').addEventListener('click', () => {
  const el  = document.getElementById('serverLog');
  const tog = document.getElementById('serverLogToggle');
  const open = el.style.display !== 'none';
  if (open) {
    el.style.display = 'none';
    tog.textContent  = 'Лог пайплайна ▸';
    clearInterval(_serverLogTimer);
    _serverLogTimer = null;
  } else {
    el.style.display = '';
    tog.textContent  = 'Лог пайплайна ▾';
    refreshServerLog();
    _serverLogTimer = setInterval(refreshServerLog, 3000);
  }
});

// Загрузить историю при старте + восстановить activeScanId из текущего статуса
(async () => {
  try {
    const st = await fetch('/api/status').then(r => r.json());
    _activeScanId = st.scan_id ?? null;
    if (st.images_dir) folderPath.value = st.images_dir;
    if (st.status === 'done') {
      setUIState('done');
      addLog('Загрузка облака...');
      await loadPLY('/api/result/ply?' + Date.now());
      addLog('Готово');
    }
  } catch { /* сервер недоступен */ }
  await loadHistory();
})();

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
  progressFill.style.width = `${Math.round(value * 100)}%`;
  const label = STEP_LABELS[step] ?? step;
  progressLabel.textContent = label ? `${label} — ${Math.round(value * 100)}%` : '—';
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

  startBtn.disabled    = scanning;
  startBtn.textContent = scanning ? 'Обработка...' : 'Начать сканирование';

  toolBtns.forEach((b) => { b.disabled = !done; });
  exportStl.disabled = !done;
  exportObj.disabled = !done;

  if (!scanning) updateProgress(0, '');
}
