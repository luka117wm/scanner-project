/**
 * Three.js вьюер: облако точек + режимы Orient / Denoise / Repair.
 * Экспортирует { loadPLY, setMode, setViewMode, fitCamera }.
 */
import * as THREE from 'three';
import { OrbitControls }     from 'three/addons/controls/OrbitControls.js';
import { PLYLoader }         from 'three/addons/loaders/PLYLoader.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';

// ── Инициализация ──────────────────────────────────────────────────────────────
const viewport = document.getElementById('viewport');
const canvas   = document.getElementById('canvas');
const selRect  = document.getElementById('sel-rect');

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);   // прозрачный — фон CSS
renderer.autoClear = true;

const scene  = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.0001, 10000);
camera.position.set(0, 0, 2);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;

// Освещение для меша
const _dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
_dirLight.position.set(0.5, 1, 0.5).normalize();
scene.add(new THREE.AmbientLight(0xffffff, 0.4), _dirLight);

// ── Состояние сцены ───────────────────────────────────────────────────────────
let pointsObj     = null;
let meshObj       = null;
let edgesObj      = null;
let transformCtrl = null;
let currentMode   = 'view';
let _viewMode     = 'points';

// ── Состояние Denoise ──────────────────────────────────────────────────────────
const dn = {
  originalColors:  null,
  selectedIndices: [],
  dragging:        false,
  startX:          0,
  startY:          0,
};

// ── Resize ────────────────────────────────────────────────────────────────────
function resize() {
  const w = viewport.clientWidth, h = viewport.clientHeight;
  if (w < 1 || h < 1) return;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(viewport);
resize();

// ── Axes canvas (2D overlay) ───────────────────────────────────────────────────
const axesCanvas = document.getElementById('axesCanvas');
const axesCtx    = axesCanvas?.getContext('2d');

function _drawAxes() {
  if (!axesCtx) return;
  const W = axesCanvas.width, H = axesCanvas.height;
  const cx = W / 2, cy = H / 2;
  const len = W * 0.33;

  axesCtx.clearRect(0, 0, W, H);

  // Background circle
  axesCtx.beginPath();
  axesCtx.arc(cx, cy, cx - 1, 0, Math.PI * 2);
  const isDark = document.documentElement.dataset.theme !== 'light';
  axesCtx.fillStyle = isDark ? 'rgba(15,18,24,0.70)' : 'rgba(245,243,238,0.75)';
  axesCtx.fill();
  axesCtx.strokeStyle = isDark ? 'rgba(255,255,255,0.09)' : 'rgba(0,0,0,0.10)';
  axesCtx.lineWidth = 1;
  axesCtx.stroke();

  // Camera rotation (pure rotation, no translation)
  const mat = new THREE.Matrix4().extractRotation(camera.matrixWorldInverse);

  const AXES = [
    { dir: new THREE.Vector3(1, 0, 0), color: '#e57373', label: 'X' },
    { dir: new THREE.Vector3(0, 1, 0), color: '#5fcf80', label: 'Y' },
    { dir: new THREE.Vector3(0, 0, 1), color: '#7aa2ff', label: 'Z' },
  ];

  const projected = AXES.map(ax => {
    const v = ax.dir.clone().applyMatrix4(mat);
    return { ...ax, px: cx + v.x * len, py: cy - v.y * len, depth: v.z };
  });

  // Sort: draw back first
  projected.sort((a, b) => a.depth - b.depth);

  for (const { color, label, px, py, depth } of projected) {
    const alpha = 0.35 + (depth + 1) * 0.32;   // dim when pointing away

    // Line
    axesCtx.beginPath();
    axesCtx.moveTo(cx, cy);
    axesCtx.lineTo(px, py);
    axesCtx.strokeStyle = color;
    axesCtx.lineWidth = 2;
    axesCtx.globalAlpha = alpha;
    axesCtx.stroke();

    // Arrowhead dot
    axesCtx.beginPath();
    axesCtx.arc(px, py, 3.5, 0, Math.PI * 2);
    axesCtx.fillStyle = color;
    axesCtx.fill();

    // Label
    const lx = cx + (px - cx) * 1.4;
    const ly = cy + (py - cy) * 1.4;
    axesCtx.font = 'bold 9px JetBrains Mono, Courier New, monospace';
    axesCtx.textAlign = 'center';
    axesCtx.textBaseline = 'middle';
    axesCtx.fillStyle = color;
    axesCtx.fillText(label, lx, ly);
  }

  axesCtx.globalAlpha = 1.0;
}

// ── Info chip ─────────────────────────────────────────────────────────────────
function _updatePtsChip() {
  const chip   = document.getElementById('ptsChip');
  const ptsEl  = document.getElementById('ptsCount');
  const obj    = pointsObj || meshObj;
  if (!obj || !chip) return;

  const geo = obj.geometry;
  let count = 0;
  if (obj instanceof THREE.Points) {
    count = geo.attributes.position?.count ?? 0;
  } else {
    count = geo.index ? geo.index.count / 3 : (geo.attributes.position?.count ?? 0) / 3;
  }
  const label = obj instanceof THREE.Points ? `Точек: ${count.toLocaleString('ru')}` : `Граней: ${Math.round(count).toLocaleString('ru')}`;
  ptsEl.textContent   = count.toLocaleString('ru');
  chip.querySelector('b').previousSibling.textContent = obj instanceof THREE.Points ? 'Точек: ' : 'Граней: ';
  chip.style.display  = '';
}

// ── Рендер-лупп ───────────────────────────────────────────────────────────────
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
  _drawAxes();
}
animate();

// ── Утилиты ────────────────────────────────────────────────────────────────────
function _fitCameraToObject(obj) {
  const box    = new THREE.Box3().setFromObject(obj);
  const center = box.getCenter(new THREE.Vector3());
  const diag   = box.getSize(new THREE.Vector3()).length();
  camera.position.copy(center).add(new THREE.Vector3(0, 0, diag * 1.6));
  controls.target.copy(center);
  controls.update();
}

export function fitCamera() {
  const obj = meshObj || pointsObj;
  if (obj) _fitCameraToObject(obj);
}

function _disposeObject(obj) {
  if (!obj) return;
  scene.remove(obj);
  obj.geometry?.dispose();
  (Array.isArray(obj.material) ? obj.material : [obj.material]).forEach(m => m?.dispose());
}

function _showLayer(layer) {
  if (pointsObj) pointsObj.visible = (layer === 'points');
  if (meshObj)   meshObj.visible   = (layer === 'mesh');
  if (edgesObj)  edgesObj.visible  = true;
}

function _applyViewMode() {
  if (!meshObj) return;
  const mat = meshObj.material;
  mat.wireframe = (_viewMode === 'wire');
  mat.needsUpdate = true;
}

function _disposeEdges() {
  if (!edgesObj) return;
  scene.remove(edgesObj);
  edgesObj.geometry?.dispose();
  edgesObj.material?.dispose();
  edgesObj = null;
}

const $ = (id) => document.getElementById(id);

// ── Публичный: setViewMode ────────────────────────────────────────────────────
export function setViewMode(mode) {
  _viewMode = mode;
  if (mode === 'points') {
    _showLayer('points');
  } else if (mode === 'solid' || mode === 'wire') {
    if (meshObj) { _showLayer('mesh'); _applyViewMode(); }
    else if (pointsObj) _showLayer('points');
  }
}

// ── Загрузка PLY: облако точек ─────────────────────────────────────────────────
export async function loadPLY(url) {
  const geometry = await new PLYLoader().loadAsync(url);
  _disposeObject(pointsObj);

  const hasColor = !!geometry.attributes.color;
  const mat = new THREE.PointsMaterial({
    vertexColors:    hasColor,
    ...(hasColor ? {} : { color: 0xd0d4dc }),
    size:            0.002,
    sizeAttenuation: true,
  });

  pointsObj = new THREE.Points(geometry, mat);
  scene.add(pointsObj);

  const box = new THREE.Box3().setFromObject(pointsObj);
  mat.size  = Math.max(box.getSize(new THREE.Vector3()).length() * 0.002, 1e-5);

  _fitCameraToObject(pointsObj);
  $('hint').style.display = 'none';

  if (currentMode === 'denoise') {
    _initDenoiseColors();
  } else if (currentMode !== 'orient') {
    _showLayer('points');
  }
  _updatePtsChip();
}

// ── Загрузка PLY: меш ─────────────────────────────────────────────────────────
async function _loadMesh(url) {
  const geometry = await new PLYLoader().loadAsync(url);
  geometry.computeVertexNormals();
  _disposeObject(meshObj);

  meshObj = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({
    color: 0x8ecae6,
    side:  THREE.DoubleSide,
    wireframe: _viewMode === 'wire',
  }));
  scene.add(meshObj);
  _fitCameraToObject(meshObj);
  $('hint').style.display = 'none';
  _updatePtsChip();
  return meshObj;
}

// ═══════════════════════════════════════════════════════════════════════════════
// ORIENT
// ═══════════════════════════════════════════════════════════════════════════════

async function _enterOrient() {
  const mesh = await _loadMesh('/api/result/oriented');
  if (currentMode !== 'orient') return;
  _showLayer('mesh');

  if (!transformCtrl) {
    transformCtrl = new TransformControls(camera, renderer.domElement);
    transformCtrl.addEventListener('dragging-changed', (e) => {
      controls.enabled = !e.value;
    });
    scene.add(transformCtrl);
  }
  transformCtrl.attach(mesh);
  transformCtrl.setMode('rotate');

  $('orient-tools').classList.add('visible');
  _setupOrientButtons(mesh);
}

function _exitOrient() {
  if (transformCtrl) transformCtrl.detach();
  $('orient-tools').classList.remove('visible');
}

function _setupOrientButtons(mesh) {
  const setActiveOt = (id) => {
    document.querySelectorAll('#orient-tools .ot-btn').forEach(b => b.classList.remove('active'));
    $(id)?.classList.add('active');
  };

  $('otRotate').onclick    = () => { transformCtrl.setMode('rotate');    setActiveOt('otRotate'); };
  $('otTranslate').onclick = () => { transformCtrl.setMode('translate'); setActiveOt('otTranslate'); };

  const AXES = { otX: [1,0,0], otY: [0,1,0], otZ: [0,0,1] };
  for (const [id, ax] of Object.entries(AXES)) {
    $(id).onclick = () => {
      mesh.quaternion.premultiply(
        new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(...ax), Math.PI / 2)
      );
    };
  }

  $('otAuto').onclick = async () => {
    $('otAuto').disabled = true;
    try {
      const r = await fetch('/api/edit/auto-orient', { method: 'POST' });
      if (r.ok) { const m = await _loadMesh('/api/result/oriented?' + Date.now()); transformCtrl.attach(m); }
    } finally { $('otAuto').disabled = false; }
  };

  $('otApply').onclick = async () => {
    $('otApply').disabled = true;
    $('otApply').textContent = '...';
    try {
      mesh.updateMatrix();
      const r = await fetch('/api/edit/apply-transform', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ matrix: Array.from(mesh.matrix.elements) }),
      });
      if (r.ok) { const m = await _loadMesh('/api/result/oriented?' + Date.now()); transformCtrl.attach(m); }
    } finally {
      $('otApply').disabled = false;
      $('otApply').textContent = 'Применить ✓';
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// DENOISE
// ═══════════════════════════════════════════════════════════════════════════════

function _enterDenoise() {
  if (!pointsObj) return;
  _showLayer('points');
  _initDenoiseColors();

  canvas.addEventListener('mousedown', _dnMouseDown);
  canvas.addEventListener('mousemove', _dnMouseMove);
  canvas.addEventListener('mouseup',   _dnMouseUp);

  $('denoise-tools').classList.add('visible');
  _setupDenoiseButtons();
}

function _exitDenoise() {
  canvas.removeEventListener('mousedown', _dnMouseDown);
  canvas.removeEventListener('mousemove', _dnMouseMove);
  canvas.removeEventListener('mouseup',   _dnMouseUp);
  _restoreDenoiseColors();
  dn.selectedIndices = [];
  selRect.style.display = 'none';
  $('denoise-tools').classList.remove('visible');
  controls.enabled = true;
}

function _initDenoiseColors() {
  if (!pointsObj) return;
  const geo = pointsObj.geometry;
  if (!geo.attributes.color) {
    const n   = geo.attributes.position.count;
    const buf = new Float32Array(n * 3).fill(1);
    geo.setAttribute('color', new THREE.BufferAttribute(buf, 3));
    pointsObj.material.vertexColors = true;
    pointsObj.material.needsUpdate  = true;
  }
  dn.originalColors  = geo.attributes.color.array.slice();
  dn.selectedIndices = [];
  _updateDnCount();
}

function _restoreDenoiseColors() {
  if (!pointsObj || !dn.originalColors) return;
  const arr = pointsObj.geometry.attributes.color?.array;
  if (arr) { arr.set(dn.originalColors); pointsObj.geometry.attributes.color.needsUpdate = true; }
}

function _applySelectionColors() {
  if (!pointsObj) return;
  const arr = pointsObj.geometry.attributes.color?.array;
  if (!arr) return;
  arr.set(dn.originalColors);
  for (const i of dn.selectedIndices) { arr[i*3]=1.0; arr[i*3+1]=0.15; arr[i*3+2]=0.15; }
  pointsObj.geometry.attributes.color.needsUpdate = true;
}

function _updateDnCount() {
  const n = dn.selectedIndices.length;
  $('dnCount').textContent = n > 0 ? `${n.toLocaleString('ru')} точек выделено` : 'Shift+drag — выделить точки';
  $('dnDelete').disabled = (n === 0);
}

function _dnMouseDown(e) {
  if (!e.shiftKey) return;
  e.preventDefault();
  dn.dragging = true;
  dn.startX   = e.offsetX;
  dn.startY   = e.offsetY;
  controls.enabled = false;
  Object.assign(selRect.style, {
    display: 'block', left: e.offsetX+'px', top: e.offsetY+'px', width:'0', height:'0',
  });
}

function _dnMouseMove(e) {
  if (!dn.dragging) return;
  const x0=dn.startX, y0=dn.startY, x1=e.offsetX, y1=e.offsetY;
  Object.assign(selRect.style, {
    left: Math.min(x0,x1)+'px', top: Math.min(y0,y1)+'px',
    width: Math.abs(x1-x0)+'px', height: Math.abs(y1-y0)+'px',
  });
}

function _dnMouseUp(e) {
  if (!dn.dragging) return;
  dn.dragging = false;
  controls.enabled = true;
  selRect.style.display = 'none';
  const x0=dn.startX, y0=dn.startY, x1=e.offsetX, y1=e.offsetY;
  if (Math.abs(x1-x0)<4 && Math.abs(y1-y0)<4) return;
  const w=canvas.clientWidth, h=canvas.clientHeight;
  const ndcX0=(Math.min(x0,x1)/w)*2-1, ndcX1=(Math.max(x0,x1)/w)*2-1;
  const ndcY0=-(Math.max(y0,y1)/h)*2+1, ndcY1=-(Math.min(y0,y1)/h)*2+1;
  const found = _findPointsInRect(ndcX0, ndcY0, ndcX1, ndcY1);
  const set = new Set(dn.selectedIndices);
  found.forEach(i => set.add(i));
  dn.selectedIndices = Array.from(set);
  _applySelectionColors();
  _updateDnCount();
}

function _findPointsInRect(ndcX0, ndcY0, ndcX1, ndcY1) {
  if (!pointsObj) return [];
  const pos      = pointsObj.geometry.attributes.position;
  const viewProj = new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  const pt  = new THREE.Vector4();
  const out = [];
  for (let i=0; i<pos.count; i++) {
    pt.set(pos.getX(i), pos.getY(i), pos.getZ(i), 1).applyMatrix4(viewProj);
    if (pt.w <= 0) continue;
    const nx=pt.x/pt.w, ny=pt.y/pt.w;
    if (nx>=ndcX0 && nx<=ndcX1 && ny>=ndcY0 && ny<=ndcY1) out.push(i);
  }
  return out;
}

function _setupDenoiseButtons() {
  $('dnDelete').onclick = async () => {
    if (!dn.selectedIndices.length) return;
    $('dnDelete').disabled = true;
    const prev = $('dnDelete').textContent;
    $('dnDelete').textContent = '...';
    try {
      const r = await fetch('/api/edit/delete-points', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ indices: dn.selectedIndices }),
      });
      if (!r.ok) throw new Error(await r.text());
      const data = await r.json();
      await loadPLY('/api/result/ply?' + Date.now());
      $('dnCount').textContent = `Осталось: ${data.remaining.toLocaleString('ru')} точек`;
    } catch (err) {
      $('dnCount').textContent = `Ошибка: ${err.message}`;
    } finally {
      $('dnDelete').disabled  = false;
      $('dnDelete').textContent = prev;
    }
  };

  $('dnClear').onclick = () => {
    dn.selectedIndices = [];
    _restoreDenoiseColors();
    _updateDnCount();
  };

  $('dnRemesh').onclick = async () => {
    const r = await fetch('/api/edit/remesh', { method: 'POST' });
    if (r.ok) {
      document.dispatchEvent(new CustomEvent('remesh-started'));
      $('dnRemesh').disabled = true;
      $('dnCount').textContent = 'Идёт пересчёт меша...';
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// REPAIR
// ═══════════════════════════════════════════════════════════════════════════════

async function _enterRepair() {
  await _loadMesh('/api/result/oriented');
  if (currentMode !== 'repair') return;
  _disposeEdges();
  _showLayer('mesh');

  const infoEl = $('rpInfo');
  infoEl.textContent = 'Загрузка...';

  try {
    const r = await fetch('/api/edit/mesh-info');
    if (!r.ok) throw new Error(`mesh-info: ${r.status}`);
    const info = await r.json();
    const wt = info.is_watertight ? 'Да' : 'Нет';
    infoEl.textContent = `V:${info.vertices.toLocaleString()} F:${info.faces.toLocaleString()} | Дыры:${info.open_edges} | WT:${wt}`;

    if (info.open_edges > 0) {
      const er = await fetch('/api/result/boundary-edges');
      if (er.ok) { const { edges } = await er.json(); _showBoundaryEdges(edges); }
    }
  } catch (e) {
    infoEl.textContent = `Ошибка: ${e.message}`;
  }

  $('repair-tools').classList.add('visible');
  _setupRepairButtons();
}

function _exitRepair() {
  _disposeEdges();
  $('repair-tools').classList.remove('visible');
}

function _showBoundaryEdges(edges) {
  _disposeEdges();
  if (!edges?.length) return;
  const positions = new Float32Array(edges.length * 6);
  for (let i=0; i<edges.length; i++) {
    const e = edges[i];
    positions[i*6]=e[0]; positions[i*6+1]=e[1]; positions[i*6+2]=e[2];
    positions[i*6+3]=e[3]; positions[i*6+4]=e[4]; positions[i*6+5]=e[5];
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  edgesObj = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: 0xff4444 }));
  scene.add(edgesObj);
}

function _setupRepairButtons() {
  $('rpFillHoles').onclick = async () => {
    $('rpFillHoles').disabled = true;
    $('rpFillHoles').textContent = '...';
    try {
      const r = await fetch('/api/edit/fill-holes', { method: 'POST' });
      if (!r.ok) throw new Error(await r.text());
      await _enterRepair();
    } catch (e) {
      $('rpInfo').textContent = `Ошибка: ${e.message}`;
    } finally {
      $('rpFillHoles').disabled = false;
      $('rpFillHoles').textContent = 'Закрыть дыры';
    }
  };

  $('rpSmooth').onclick = async () => {
    $('rpSmooth').disabled = true;
    $('rpSmooth').textContent = '...';
    try {
      const r = await fetch('/api/edit/smooth?iterations=3', { method: 'POST' });
      if (!r.ok) throw new Error(await r.text());
      await _enterRepair();
    } catch (e) {
      $('rpInfo').textContent = `Ошибка: ${e.message}`;
    } finally {
      $('rpSmooth').disabled = false;
      $('rpSmooth').textContent = 'Smooth ×3';
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// ПУБЛИЧНЫЙ API
// ═══════════════════════════════════════════════════════════════════════════════

export function setMode(mode) {
  if (currentMode === 'orient'  && mode !== 'orient')  _exitOrient();
  if (currentMode === 'denoise' && mode !== 'denoise') _exitDenoise();
  if (currentMode === 'repair'  && mode !== 'repair')  _exitRepair();

  currentMode = mode;

  if      (mode === 'orient')  _enterOrient();
  else if (mode === 'denoise') _enterDenoise();
  else if (mode === 'repair')  _enterRepair();
  else if (mode === 'view')    _showLayer('points');
}
