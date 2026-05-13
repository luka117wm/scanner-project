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

let eventSource = null;

// ── Выбор папки ────────────────────────────────────────────────────────────────
folderBtn.addEventListener('click', async () => {
  // pywebview даёт нативный диалог (фаза 11.G)
  if (window.pywebview?.api?.get_folder) {
    const path = await window.pywebview.api.get_folder();
    if (path) folderPath.value = path;
  } else {
    // В браузере — просто фокус на поле, пользователь вводит путь вручную
    folderPath.focus();
    folderPath.select();
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
        .then(() => addLog('Готово'))
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

exportStl.addEventListener('click', () => {
  // Реализация в фазе 11.F
  console.log('[app] export STL');
});

exportObj.addEventListener('click', () => {
  // Реализация в фазе 11.F
  console.log('[app] export OBJ+tex');
});

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
  const lines = (logEl.textContent || '').split('\n').filter(Boolean);
  lines.push(msg);
  if (lines.length > 5) lines.splice(0, lines.length - 5);
  logEl.textContent = lines.join('\n');
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
