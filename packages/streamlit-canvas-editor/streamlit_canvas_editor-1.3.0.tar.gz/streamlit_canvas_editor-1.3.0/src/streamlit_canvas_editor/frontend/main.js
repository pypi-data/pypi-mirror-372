// Canvas Editor - Streamlit Component with Custom Properties
console.log("Canvas Editor initialized");

// ----- State -----
let canvas, ctx;
let canvasContainer, canvasWrapper;
let isDrawing = false, isResizing = false, isDragging = false;
let startX, startY;
let rectangles = [];
let currentRect = null;
let selectedRect = null;
let selectedRectIndex = -1;
let resizeHandle = null;
let dragOffset = { x: 0, y: 0 };
let imageLoaded = false;
let ocrEnabled = false;
let skipNextUpdate = false;
let isProcessingOCR = false;
let currentOCRRequestId = null;
let currentlyProcessingBlockId = null;

let zoomLevel = 1.0;
const ZOOM_MIN = 0.25, ZOOM_MAX = 4.0, ZOOM_STEP = 0.25;

// base drawing buffer size (updated to image size on load)
let baseCanvasWidth = 800;
let baseCanvasHeight = 600;

// pan helpers
let canvasMode = 'draw'; // 'draw' or 'pan'
let isPanning = false;
let panStartClientX = 0, panStartClientY = 0;
let panStartScrollLeft = 0, panStartScrollTop = 0;

let originalRect = null, resizeStartPos = null;

let history = [], historyStep = -1;
const MAX_HISTORY = 50;

const HANDLE_SIZE = 10, HANDLE_HIT_SIZE = 20;
const SELECTED_COLOR = '#FF5722';
const DEFAULT_COLOR = '#F4A460';
const MIN_RECT_SIZE = 30;
const RESIZE_THRESHOLD = 2;

let INSTANCE_ID = null;
let OCR_TIMEOUT_MS = 90000; // default; can be overridden by Python prop

// Color scheme for block types
let blockTypeColors = {
  'Line':'#FFB6C1','Span':'#98FB98','FigureGroup':'#ADD8E6','TableGroup':'#FFFFE0',
  'ListGroup':'#FFC0CB','PictureGroup':'#E0FFFF','Page':'#FFDAB9','Caption':'#98FB98',
  'Code':'#E6E6FA','Figure':'#FFE4C4','Footnote':'#DDA0DD','Form':'#AFEEEE',
  'Equation':'#D3D3D3','Handwriting':'#D3D3D3','TextInlineMath':'#FFDAB9',
  'ListItem':'#FFB6C1','PageFooter':'#D8BFD8','PageHeader':'#90EE90','Picture':'#ADD8E6',
  'SectionHeader':'#DDA0DD','Table':'#DEB887','Text':'#F4A460','TableOfContents':'#BDB76B',
  'Document':'#FFA07A','ComplexRegion':'#FFB6C1','TableCell':'#D8BFD8','Reference':'#90EE90',
  'other':'#A9A9A9'
};

// ----- New flags to avoid autosave on plain clicks -----
let hasPropEdits = false;    // user changed text/type
let hasGeomChange = false;   // draw/resize/drag actually changed geometry
let dragStartPos = null;     // track to detect no-op drags

// ----- Buffered typing -----
let typingTimer = null;
const TYPING_IDLE_MS = 5000;  // save after 5s of no typing

// Scope events to your component root
const getRoot = () => document.getElementById('root') || document.body;

// ----- Helpers -----
function uid() { return `r_${Math.random().toString(36).slice(2)}_${Date.now()}`; }

function getBlockTypeColor(blockType) {
  if (blockTypeColors && blockTypeColors[blockType]) return blockTypeColors[blockType];
  if (blockTypeColors && blockTypeColors['other']) return blockTypeColors['other'];
  return DEFAULT_COLOR;
}

function getLighterColor(hexColor, opacity = 0.15) {
  if (!hexColor || !hexColor.startsWith('#')) hexColor = DEFAULT_COLOR;
  const r = parseInt(hexColor.slice(1,3),16);
  const g = parseInt(hexColor.slice(3,5),16);
  const b = parseInt(hexColor.slice(5,7),16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// Layout-based zoom: scale via CSS width/height (not transforms)
function applyZoomCss() {
  const cssW = Math.max(1, Math.round(baseCanvasWidth  * zoomLevel));
  const cssH = Math.max(1, Math.round(baseCanvasHeight * zoomLevel));
  canvas.style.width  = cssW + 'px';
  canvas.style.height = cssH + 'px';
  if (canvasContainer) {
    canvasContainer.style.width  = canvas.style.width;
    canvasContainer.style.height = canvas.style.height;
  }
}

// ----- ID MANAGEMENT (top-to-bottom renumbering) -----
function ensureUids() {
  rectangles.forEach(r => { if (!r._uid) r._uid = uid(); });
}

function renumberBlockIds(preserveSelection = true) {
  ensureUids();
  const selUid = preserveSelection && selectedRect ? selectedRect._uid : null;

  // sort by y then x for ordering
  const sorted = rectangles.slice().sort((a, b) => {
    if (a.y === b.y) return a.x - b.x;
    return a.y - b.y;
  });

  const idMap = new Map();
  sorted.forEach((r, i) => idMap.set(r._uid, `block_${i + 1}`));

  rectangles.forEach(r => { r.Block_ID = idMap.get(r._uid); });

  // keep selection by uid
  if (selUid) {
    selectedRectIndex = rectangles.findIndex(r => r._uid === selUid);
    selectedRect = selectedRectIndex >= 0 ? rectangles[selectedRectIndex] : null;
  }

  // update Block ID field in panel if open
  const blockIdField = document.getElementById('content-id');
  if (blockIdField && selectedRect) blockIdField.value = selectedRect.Block_ID;

  redrawCanvas();
}

// ----- Init -----
function initCanvas() {
  canvas = document.getElementById('drawing-canvas');
  canvasContainer = document.getElementById('canvas-container');
  canvasWrapper = document.getElementById('canvas-wrapper');

  if (!canvas || !canvasContainer || !canvasWrapper) {
    console.error("Canvas elements not found!");
    return;
  }

  ctx = canvas.getContext('2d');
  canvas.width = baseCanvasWidth;
  canvas.height = baseCanvasHeight;
  applyZoomCss();

  setupEventListeners();
  redrawCanvas();
  updateStatus("Ready to draw");
  updateZoomDisplay();
  saveHistory();
}

function setupEventListeners() {
  // Canvas mouse
  canvas.addEventListener('mousedown', handleMouseDown);
  canvas.addEventListener('mousemove', handleMouseMove);
  canvas.addEventListener('mouseup', handleMouseUp);
  canvas.addEventListener('mouseout', handleMouseOut);

  // Zoom wheel: ctrl/cmd + wheel zooms, plain wheel scrolls wrapper
  canvasWrapper.addEventListener('wheel', handleWheel, { passive: false });

  // Keyboard (iframe-scoped)
  document.addEventListener('keydown', handleKeyDown);

  // Delegated clicks (scope to our root)
  document.addEventListener('click', function(e) {
    if (!getRoot().contains(e.target)) return;
    const targetId = e.target.id;
    const closestButtonId = e.target.closest('button')?.id;

    if (targetId === 'save-properties') {
      e.preventDefault(); saveProperties();
    } else if (targetId === 'close-panel') {
      e.preventDefault(); hidePropertiesPanel();
    } else if (targetId === 'reset-properties') {
      e.preventDefault(); resetProperties();
    } else if (targetId === 'ocr-btn' || closestButtonId === 'ocr-btn') {
      e.preventDefault(); e.stopPropagation(); performOCR();
    } else if (targetId === 'undo-btn') {
      undo();
    } else if (targetId === 'redo-btn') {
      redo();
    } else if (targetId === 'zoom-in-btn') {
      zoomIn();
    } else if (targetId === 'zoom-out-btn') {
      zoomOut();
    } else if (targetId === 'zoom-reset-btn') {
      zoomReset();
    } else if (targetId === 'pan-mode-btn') {
      setCanvasMode('pan');
    } else if (targetId === 'draw-mode-btn') {
      setCanvasMode('draw');
    }
  });

  // Change events (rare): commit immediately
  document.addEventListener('change', function(e) {
    if (!getRoot().contains(e.target)) return;
    if (e.target && e.target.id === 'block-type') {
      hasPropEdits = true;          // actual property change
      autoSaveProperties();
      const blockType = e.target.value;
      if (blockType) updatePanelTheme(blockType);
    }
  });

  // Input events: buffer typing, push on idle/blur
  document.addEventListener('input', function(e) {
    if (!getRoot().contains(e.target)) return;
    if (e.target && (e.target.id === 'text-content' || e.target.id === 'text-id')) {
      hasPropEdits = true;

      // keep local model in sync instantly (no Streamlit push yet)
      if (selectedRect && selectedRectIndex >= 0) {
        if (e.target.id === 'text-content') selectedRect.Text_Content = e.target.value;
        else selectedRect.Text_ID = e.target.value;
        rectangles[selectedRectIndex] = selectedRect;
      }

      if (typingTimer) clearTimeout(typingTimer);
      typingTimer = setTimeout(flushTypingChanges, TYPING_IDLE_MS);
    }
  });

  // Flush on blur too
  document.addEventListener('blur', function(e) {
    if (!getRoot().contains(e.target)) return;
    if (e.target && (e.target.id === 'text-content' || e.target.id === 'text-id')) {
      flushTypingChanges();
    }
  }, true);
}

// Debounce for legacy paths (kept but not used for typing)
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    const later = () => { clearTimeout(timeout); func.apply(this, args); };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
const debouncedAutoSave = debounce(autoSaveProperties, 250);

// ----- OCR -----
function performOCR() {
  if (!ocrEnabled) {
    updateStatus("OCR disabled");
    return;
  }
  if (!selectedRect || selectedRectIndex < 0) {
    updateStatus("Cannot perform OCR: no selection");
    return;
  }
  if (isProcessingOCR) {
    updateStatus(`OCR already running on ${currentlyProcessingBlockId || 'another block'}...`);
    return;
  }

  currentOCRRequestId = `ocr_${Date.now()}_${selectedRectIndex}`;
  currentlyProcessingBlockId = selectedRect.Block_ID;

  const ocrBtn = document.getElementById('ocr-btn');
  if (ocrBtn) {
    ocrBtn.classList.add('loading');
    ocrBtn.disabled = true;
    ocrBtn.innerHTML = '<span class="ocr-icon">⏳</span> Processing...';
  }

  isProcessingOCR = true;
  updateStatus(`Running OCR for ${selectedRect.Block_ID}...`);

  const ocrRequest = {
    rect_index: selectedRectIndex,
    bbox: rectToBbox(selectedRect),
    request_id: currentOCRRequestId,
    _instance_id: INSTANCE_ID,
  };

  const data = {
    _instance_id: INSTANCE_ID,
    rectangles: rectangles.map(packRect),
    selected_index: selectedRectIndex,
    canvas_width: canvas.width,
    canvas_height: canvas.height,
    zoom_level: zoomLevel,
    ocr_request: ocrRequest,
  };

  Streamlit.setComponentValue(data);

  setTimeout(() => {
    if (isProcessingOCR && currentOCRRequestId === ocrRequest.request_id) {
      resetOCRButton();
      isProcessingOCR = false;
      currentOCRRequestId = null;
      currentlyProcessingBlockId = null;
      updateStatus("OCR timeout - please try again");
    }
  }, OCR_TIMEOUT_MS);
}

function resetOCRButton() {
  const ocrBtn = document.getElementById('ocr-btn');
  if (ocrBtn) {
    ocrBtn.classList.remove('loading');
    ocrBtn.disabled = false;
    ocrBtn.innerHTML = '<span class="ocr-icon">🔍</span> OCR';
  }
}

function packRect(rect) {
  return {
    Block_ID: rect.Block_ID,
    Block_Type: rect.Block_Type || 'Text',
    Text_Content: rect.Text_Content || '',
    Text_ID: rect.Text_ID || '',
    Boundary_Boxes: rectToBbox(rect),
    x: Math.round(rect.x), y: Math.round(rect.y),
    width: Math.round(rect.width), height: Math.round(rect.height),
  };
}

function sendDataToStreamlit() {
  if (isProcessingOCR) { return; }
  skipNextUpdate = true;

  const data = {
    _instance_id: INSTANCE_ID,
    rectangles: rectangles.map(packRect),
    selected_index: selectedRectIndex,
    canvas_width: canvas.width,
    canvas_height: canvas.height,
    zoom_level: zoomLevel,
  };

  Streamlit.setComponentValue(data);
}

// ----- Panel theme -----
function updatePanelTheme(blockType) {
  const panel = document.getElementById('properties-panel');
  if (!panel) return;

  const panelHeader = panel.querySelector('.panel-header');
  const saveBtn = panel.querySelector('.save-btn');
  const propertySections = panel.querySelectorAll('.property-section');

  const blockColor = getBlockTypeColor(blockType);
  const lightBgColor = getLighterColor(blockColor, 0.15);

  panel.style.background = `linear-gradient(to bottom, ${lightBgColor}, ${getLighterColor(blockColor, 0.05)})`;

  if (panelHeader) {
    panelHeader.style.background = `linear-gradient(135deg, ${blockColor} 0%, ${blockColor}dd 100%)`;
    panelHeader.style.color = '#ffffff';
  }
  if (saveBtn) {
    saveBtn.style.background = `linear-gradient(135deg, ${blockColor} 0%, ${blockColor}dd 100%)`;
    saveBtn.style.color = '#ffffff';
    saveBtn.onmouseover = function() {
      this.style.boxShadow = `0 4px 12px ${getLighterColor(blockColor, 0.4)}`;
      this.style.transform = 'translateY(-1px)';
    };
    saveBtn.onmouseout = function() {
      this.style.boxShadow = '';
      this.style.transform = '';
    };
  }

  propertySections.forEach(section => {
    section.style.background = getLighterColor(blockColor, 0.1);
    section.style.borderLeft = `3px solid ${blockColor}`;
    section.style.paddingLeft = '15px';
    section.style.marginBottom = '10px';
    section.style.borderRadius = '4px';
  });

  panel.style.border = `2px solid ${blockColor}`;
  panel.style.borderRadius = '8px';

  const inputs = panel.querySelectorAll('input, select, textarea');
  inputs.forEach(input => {
    const focusHandler = function() {
      this.style.borderColor = blockColor;
      this.style.boxShadow = `0 0 0 3px ${getLighterColor(blockColor, 0.2)}`;
    };
    const blurHandler = function() {
      this.style.borderColor = getLighterColor(blockColor, 0.3);
      this.style.boxShadow = '';
    };
    input.removeEventListener('focus', input._focusHandler);
    input.removeEventListener('blur', input._blurHandler);
    input._focusHandler = focusHandler;
    input._blurHandler = blurHandler;
    input.addEventListener('focus', focusHandler);
    input.addEventListener('blur', blurHandler);
    input.style.borderColor = getLighterColor(blockColor, 0.3);
  });

  let colorBar = panel.querySelector('.color-indicator-bar');
  if (!colorBar) {
    colorBar = document.createElement('div');
    colorBar.className = 'color-indicator-bar';
    panel.insertBefore(colorBar, panel.firstChild);
  }
  colorBar.style.cssText = `
    width: 100%;
    height: 4px;
    background: ${blockColor};
    border-radius: 8px 8px 0 0;
    margin-bottom: -4px;
  `;
}

// ----- Properties panel -----
function showPropertiesPanel(rect) {
  const panel = document.getElementById('properties-panel');
  if (!panel || !rect) return;

  panel.style.display = 'flex';
  const panelTitle = panel.querySelector('.panel-title');
  if (panelTitle) {
    if (isProcessingOCR && currentlyProcessingBlockId) {
      if (currentlyProcessingBlockId === rect.Block_ID) {
        panelTitle.innerHTML = `📝 Properties - <span style="color: #ff9800;">Processing OCR...</span>`;
      } else {
        panelTitle.innerHTML = `📝 Properties - <span style="color: #f44336;">OCR busy on ${currentlyProcessingBlockId}</span>`;
      }
    } else {
      panelTitle.innerHTML = '📝 Rectangle Properties';
    }
  }

  const blockIdField = document.getElementById('content-id');
  const blockTypeField = document.getElementById('block-type');
  const textContentField = document.getElementById('text-content');
  const textIdField = document.getElementById('text-id');

  if (blockIdField) {
    blockIdField.value = rect.Block_ID;
    blockIdField.readOnly = true;
    blockIdField.style.background = '#e9ecef';
    blockIdField.style.cursor = 'not-allowed';
  }
  const blockType = rect.Block_Type || 'Text';
  if (blockTypeField) blockTypeField.value = blockType;
  if (textContentField) textContentField.value = rect.Text_Content || '';
  if (textIdField) textIdField.value = rect.Text_ID || '';

  hasPropEdits = false; // opening is not an edit

  updateBoundaryBoxDisplay();

  const ocrBtn = document.getElementById('ocr-btn');
  if (ocrBtn) {
    if (ocrEnabled) {
      ocrBtn.style.display = 'inline-flex';
      if (isProcessingOCR) {
        ocrBtn.classList.add('loading');
        ocrBtn.disabled = true;
        if (currentlyProcessingBlockId === rect.Block_ID) {
          ocrBtn.innerHTML = '<span class="ocr-icon">⏳</span> Processing...';
        } else {
          ocrBtn.innerHTML = `<span class="ocr-icon">⏳</span> Busy (${currentlyProcessingBlockId})`;
        }
      } else {
        resetOCRButton();
      }
    } else {
      ocrBtn.style.display = 'none';
    }
  }

  updatePanelTheme(blockType);
}

function hidePropertiesPanel() {
  const panel = document.getElementById('properties-panel');
  if (!panel) return;
  panel.style.display = 'none';
  panel.style.background = '';
  const panelHeader = panel.querySelector('.panel-header');
  if (panelHeader) panelHeader.style.background = '';
  const saveBtn = panel.querySelector('.save-btn');
  if (saveBtn) {
    saveBtn.style.background = '';
    saveBtn.onmouseover = null;
    saveBtn.onmouseout = null;
  }
  const propertySections = panel.querySelectorAll('.property-section');
  propertySections.forEach(s => { s.style.background = ''; s.style.borderLeft = ''; });
  hasPropEdits = false;
}

function saveProperties(addToHistory = true) {
  if (selectedRect && selectedRectIndex >= 0) {
    const blockTypeElement = document.getElementById('block-type');
    const textContentElement = document.getElementById('text-content');
    const textIdElement = document.getElementById('text-id');

    if (blockTypeElement) selectedRect.Block_Type = blockTypeElement.value;
    if (textContentElement) selectedRect.Text_Content = textContentElement.value;
    if (textIdElement) selectedRect.Text_ID = textIdElement.value;

    selectedRect.Boundary_Boxes = rectToBbox(selectedRect);
    rectangles[selectedRectIndex] = selectedRect;

    if (addToHistory) saveHistory();
    renumberBlockIds();
    redrawCanvas();
    sendDataToStreamlit();
    updateStatus(`Properties saved for ${selectedRect.Block_ID}`);
  }
}

function autoSaveProperties() {
  // only autosave if there were actual property edits
  if (selectedRect && selectedRectIndex >= 0 && hasPropEdits) {
    saveProperties(false);
    hasPropEdits = false;
  }
}

// Flush buffered typing to Streamlit (idle/blur)
function flushTypingChanges() {
  if (typingTimer) { clearTimeout(typingTimer); typingTimer = null; }
  if (!selectedRect || selectedRectIndex < 0) return;
  if (!hasPropEdits) return;

  saveProperties(false);   // commit locally
  hasPropEdits = false;
  sendDataToStreamlit();   // single push
  updateStatus(`Saved edits for ${selectedRect.Block_ID}`);
}

// ---- Reset Content ----
function resetProperties() {
  if (!selectedRect || selectedRectIndex < 0) {
    updateStatus("No selected rectangle to reset");
    return;
  }
  const blockTypeField   = document.getElementById('block-type');
  const textContentField = document.getElementById('text-content');
  const textIdField      = document.getElementById('text-id');

  if (textContentField) textContentField.value = '';
  if (textIdField)      textIdField.value      = '';
  if (blockTypeField)   blockTypeField.value   = 'Text';

  selectedRect.Text_Content   = '';
  selectedRect.Text_ID        = '';
  selectedRect.Block_Type     = 'Text';
  selectedRect.Boundary_Boxes = rectToBbox(selectedRect);

  rectangles[selectedRectIndex] = selectedRect;

  saveHistory();
  updateBoundaryBoxDisplay();
  updatePanelTheme('Text');
  renumberBlockIds();
  redrawCanvas();
  sendDataToStreamlit();
  updateStatus(`Content reset for ${selectedRect.Block_ID}`);
}

// ----- Zoom / pan / mouse -----
function zoomIn(){ setZoom(zoomLevel + ZOOM_STEP); }
function zoomOut(){ setZoom(zoomLevel - ZOOM_STEP); }

function zoomReset(){
  zoomLevel = 1.0;
  applyZoomCss();
  centerCanvas();
  updateZoomDisplay();
  updateStatus("Zoom reset to 100%");
}

function setZoom(newZoom){
  newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, newZoom));
  if (newZoom === zoomLevel) return;

  const rect = canvasWrapper.getBoundingClientRect();
  const centerX = rect.width / 2;
  const centerY = rect.height / 2;
  const preX = (canvasWrapper.scrollLeft + centerX) / zoomLevel;
  const preY = (canvasWrapper.scrollTop  + centerY) / zoomLevel;

  zoomLevel = newZoom;
  applyZoomCss();

  canvasWrapper.scrollLeft = preX * zoomLevel - centerX;
  canvasWrapper.scrollTop  = preY * zoomLevel - centerY;

  updateZoomDisplay();
  updateZoomButtons();
}

function handleWheel(e){
  if (e.ctrlKey || e.metaKey) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
    setZoom(zoomLevel + delta);
  }
}

function updateZoomDisplay(){
  const elem = document.getElementById('zoom-level');
  if (elem) elem.textContent = `${Math.round(zoomLevel * 100)}%`;
}
function updateZoomButtons(){
  const zin = document.getElementById('zoom-in-btn');
  const zout= document.getElementById('zoom-out-btn');
  if (zin) zin.disabled  = zoomLevel >= ZOOM_MAX;
  if (zout) zout.disabled = zoomLevel <= ZOOM_MIN;
}
function centerCanvas(){
  const cssW = baseCanvasWidth  * zoomLevel;
  const cssH = baseCanvasHeight * zoomLevel;
  const wrapperWidth = canvasWrapper.clientWidth;
  const wrapperHeight = canvasWrapper.clientHeight;
  canvasWrapper.scrollLeft = Math.max(0, (cssW - wrapperWidth) / 2);
  canvasWrapper.scrollTop  = Math.max(0, (cssH - wrapperHeight) / 2);
}

function getMousePos(e){
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  return { x: (e.clientX - rect.left) * scaleX, y: (e.clientY - rect.top) * scaleY };
}

function handleMouseDown(e){
  const pos = getMousePos(e);

  if (selectedRect) {
    const handle = getResizeHandle(pos.x, pos.y, selectedRect);
    if (handle) {
      isResizing = true;
      resizeHandle = handle;
      resizeStartPos = { x: pos.x, y: pos.y };
      originalRect = { x: selectedRect.x, y: selectedRect.y, width: selectedRect.width, height: selectedRect.height };
      updateStatus(`Resizing: ${selectedRect.Block_ID}`);
      return;
    }
  }

  let clickedRect = null;
  let clickedIndex = -1;
  for (let i = rectangles.length - 1; i >= 0; i--) {
    if (isPointInRect(pos.x, pos.y, rectangles[i])) { clickedRect = rectangles[i]; clickedIndex = i; break; }
  }

  if (clickedRect) {
    // Pure selection shouldn't trigger autosave later
    hasPropEdits = false;
    hasGeomChange = false;

    selectedRect = clickedRect;
    selectedRectIndex = clickedIndex;
    hidePropertiesPanel();
    setTimeout(() => showPropertiesPanel(clickedRect), 10);
    isDragging = true;
    dragStartPos = { x: clickedRect.x, y: clickedRect.y };
    dragOffset.x = pos.x - clickedRect.x;
    dragOffset.y = pos.y - clickedRect.y;
    updateStatus(`Selected: ${clickedRect.Block_ID || 'Rectangle'}`);
    redrawCanvas();
    return;
  }

  if (canvasMode === 'pan') {
    isPanning = true;
    panStartClientX = e.clientX;
    panStartClientY = e.clientY;
    panStartScrollLeft = canvasWrapper.scrollLeft;
    panStartScrollTop  = canvasWrapper.scrollTop;
    canvas.classList.add('panning');
    canvas.style.cursor = 'grabbing';
    updateStatus('Panning canvas...');
    selectedRect = null;
    selectedRectIndex = -1;
    hidePropertiesPanel();
    redrawCanvas();
  } else {
    selectedRect = null;
    selectedRectIndex = -1;
    hidePropertiesPanel();
    isDrawing = true;
    startX = pos.x;
    startY = pos.y;
    currentRect = {
      _uid: uid(),
      x: startX, y: startY, width: 0, height: 0,
      Block_ID: 'block_temp',
      Block_Type: 'Text', Text_Content: '', Text_ID: '', Boundary_Boxes: [0,0,0,0]
    };
    updateStatus("Drawing new rectangle...");
  }
}

function handleMouseMove(e){
  const pos = getMousePos(e);

  if (isPanning) {
    const dx = e.clientX - panStartClientX;
    const dy = e.clientY - panStartClientY;
    canvasWrapper.scrollLeft = panStartScrollLeft - dx;
    canvasWrapper.scrollTop  = panStartScrollTop  - dy;
    return;
  }

  updateCursor(pos);

  if (isDrawing && currentRect) {
    currentRect.width = pos.x - startX;
    currentRect.height= pos.y - startY;
    redrawCanvas();
    drawRectangle(currentRect, true);
    updateStatus(`Drawing: ${Math.round(Math.abs(currentRect.width))} × ${Math.round(Math.abs(currentRect.height))}`);
  } else if (isResizing && selectedRect && originalRect && resizeStartPos) {
    resizeRectangle(pos);
  } else if (isDragging && selectedRect) {
    dragRectangle(pos);
  }
}

function handleMouseUp(e){
  if (isPanning) {
    isPanning = false;
    canvas.classList.remove('panning');
    canvas.style.cursor = canvasMode === 'pan' ? 'grab' : 'crosshair';
    updateStatus(canvasMode === 'pan' ? 'Pan mode' : 'Draw mode');
    return;
  }
  if (isDrawing) finalizeDrawing();
  else if (isResizing) finalizeResize();
  else if (isDragging) finalizeDrag();
}

function handleMouseOut(e){
  const rect = canvas.getBoundingClientRect();
  if (e.clientX < rect.left - 50 || e.clientX > rect.right + 50 ||
      e.clientY < rect.top  - 50 || e.clientY > rect.bottom + 50) {
    if (isDrawing || isResizing || isDragging) handleMouseUp(e);
  }
}

function handleKeyDown(e){
  if (e.ctrlKey || e.metaKey) {
    if (e.key === '=' || e.key === '+') { e.preventDefault(); zoomIn(); }
    else if (e.key === '-' || e.key === '_') { e.preventDefault(); zoomOut(); }
    else if (e.key === '0') { e.preventDefault(); zoomReset(); }
  }
  if ((e.key === 'Delete' || e.key === 'Backspace') && selectedRect && !e.target.matches('input, textarea')) {
    deleteSelectedRectangle();
  } else if (e.ctrlKey && e.key === 'z' && !e.shiftKey) {
    e.preventDefault(); undo();
  } else if (e.ctrlKey && (e.key === 'y' || (e.shiftKey && e.key === 'Z'))) {
    e.preventDefault(); redo();
  } else if (e.key === 'Escape') {
    selectedRect = null; selectedRectIndex = -1; hidePropertiesPanel(); redrawCanvas(); updateStatus("Selection cleared");
  }
  if (e.key.toLowerCase() === 'v') { e.preventDefault(); setCanvasMode('pan'); }
  else if (e.key.toLowerCase() === 'd') { e.preventDefault(); setCanvasMode('draw'); }
}

// ----- Geometry & drawing -----
function setCanvasMode(mode){
  canvasMode = mode;
  const panBtn = document.getElementById('pan-mode-btn');
  const drawBtn= document.getElementById('draw-mode-btn');
  if (mode === 'pan') {
    panBtn?.classList.add('active'); drawBtn?.classList.remove('active');
    updateStatus('Pan mode - Drag empty space to pan, click boxes to select');
  } else {
    panBtn?.classList.remove('active'); drawBtn?.classList.add('active');
    updateStatus('Draw mode - Click and drag to draw rectangles');
  }
  isDrawing = false; isPanning = false; currentRect = null;
}

function isPointInRect(x,y,rect){ return x >= rect.x && x <= rect.x + rect.width && y >= rect.y && y <= rect.y + rect.height; }
function getHandlePositions(rect){
  return [
    { x: rect.x, y: rect.y, type: 'nw' },
    { x: rect.x + rect.width, y: rect.y, type: 'ne' },
    { x: rect.x + rect.width, y: rect.y + rect.height, type: 'se' },
    { x: rect.x, y: rect.y + rect.height, type: 'sw' },
  ];
}
function getResizeHandle(x,y,rect){
  const handles = getHandlePositions(rect);
  for (let h of handles) {
    const dx = x - h.x, dy = y - h.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist <= HANDLE_HIT_SIZE) return h.type;
  }
  return null;
}
function updateCursor(pos){
  if (canvasMode === 'pan') {
    if (selectedRect && getResizeHandle(pos.x, pos.y, selectedRect)) {
      const handle = getResizeHandle(pos.x, pos.y, selectedRect);
      const cursors = { nw:'nw-resize', ne:'ne-resize', se:'se-resize', sw:'sw-resize' };
      canvas.style.cursor = cursors[handle];
    } else if (rectangles.some(r=>isPointInRect(pos.x,pos.y,r))) {
      canvas.style.cursor = 'pointer';
    } else {
      canvas.style.cursor = 'grab';
    }
    return;
  }
  if (selectedRect && getResizeHandle(pos.x, pos.y, selectedRect)) {
    const handle = getResizeHandle(pos.x, pos.y, selectedRect);
    const cursors = { nw:'nw-resize', ne:'ne-resize', se:'se-resize' , sw:'sw-resize' };
    canvas.style.cursor = cursors[handle];
  } else if (rectangles.some(r=>isPointInRect(pos.x,pos.y,r))) {
    canvas.style.cursor = 'move';
  } else {
    canvas.style.cursor = 'crosshair';
  }
}

function drawRectangle(rect, isTemporary=false, isSelected=false){
  const color = isSelected ? SELECTED_COLOR : getBlockTypeColor(rect.Block_Type||'Text');
  ctx.strokeStyle = color;
  ctx.lineWidth = isSelected ? 3 : 2;
  ctx.setLineDash(isTemporary ? [5,5] : []);
  ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);

  ctx.globalAlpha = isSelected ? 0.15 : 0.08;
  ctx.fillStyle = color;
  ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
  ctx.globalAlpha = 1.0;
  ctx.setLineDash([]);

  if (!isTemporary && rect.Block_ID) drawBlockId(rect, isSelected);
  if (isSelected && !isTemporary) drawResizeHandles(rect);
}
function drawBlockId(rect, isSelected){
  const color = isSelected ? SELECTED_COLOR : getBlockTypeColor(rect.Block_Type||'Text');
  const idText = rect.Block_ID || '';
  ctx.font = '11px Arial';
  const metrics = ctx.measureText(idText);
  const padding = 4, margin = 5;
  let idX = rect.x + rect.width + margin;
  let idY = Math.max(0, rect.y);

  const boxW = metrics.width + padding*2;
  if (idX + boxW > canvas.width - 1) {
    idX = Math.max(0, rect.x - margin - boxW);
  }
  if (idY < 0) idY = 0;
  if (idY + 16 > canvas.height) idY = canvas.height - 16;

  ctx.fillStyle = 'rgba(255,255,255,0.95)';
  ctx.fillRect(idX, idY, boxW, 16);
  ctx.strokeStyle = color; ctx.lineWidth = 1;
  ctx.strokeRect(idX, idY, boxW, 16);
  ctx.fillStyle = color; ctx.textBaseline = 'top';
  ctx.fillText(idText, idX + padding, idY + 2);
}
function drawResizeHandles(rect){
  const handles = getHandlePositions(rect);
  handles.forEach(h=>{
    ctx.fillStyle = 'rgba(0,0,0,0)';
    ctx.fillRect(h.x - HANDLE_HIT_SIZE/2, h.y - HANDLE_HIT_SIZE/2, HANDLE_HIT_SIZE, HANDLE_HIT_SIZE);
    ctx.fillStyle = '#fff'; ctx.strokeStyle = SELECTED_COLOR; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.rect(h.x - HANDLE_SIZE/2, h.y - HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE);
    ctx.fill(); ctx.stroke();
  });
}

function redrawCanvas(){
  if (!canvas || !ctx) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (window.backgroundImage && imageLoaded) ctx.drawImage(window.backgroundImage, 0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = '#e0e0e0'; ctx.lineWidth = 1; ctx.strokeRect(0, 0, canvas.width, canvas.height);
  rectangles.forEach((r, idx)=> drawRectangle(r, false, idx === selectedRectIndex));
}

function rectToBbox(rect){ return [Math.round(rect.x), Math.round(rect.y), Math.round(rect.x + rect.width), Math.round(rect.y + rect.height)]; }
function bboxToRect(b){ return { x:b[0], y:b[1], width:b[2]-b[0], height:b[3]-b[1] }; }

// ----- Boundary box display -----
function updateBoundaryBoxDisplay(){
  if (!selectedRect) return;
  const bbox = rectToBbox(selectedRect);
  const x0 = document.getElementById('bbox-x0'); if (x0) x0.value = bbox[0];
  const y0 = document.getElementById('bbox-y0'); if (y0) y0.value = bbox[1];
  const x1 = document.getElementById('bbox-x1'); if (x1) x1.value = bbox[2];
  const y1 = document.getElementById('bbox-y1'); if (y1) y1.value = bbox[3];
  const sizeDisplay = document.getElementById('size-display');
  if (sizeDisplay) sizeDisplay.textContent = `Size: ${bbox[2]-bbox[0]} × ${bbox[3]-bbox[1]}`;
}

// ----- finalize ops -----
function finalizeDrawing(){
  isDrawing = false;
  if (currentRect && (Math.abs(currentRect.width) > MIN_RECT_SIZE && Math.abs(currentRect.height) > MIN_RECT_SIZE)) {
    if (currentRect.width < 0) { currentRect.x += currentRect.width; currentRect.width = Math.abs(currentRect.width); }
    if (currentRect.height< 0) { currentRect.y += currentRect.height; currentRect.height= Math.abs(currentRect.height); }
    currentRect.Boundary_Boxes = rectToBbox(currentRect);
    rectangles.push(currentRect);
    saveHistory();
    renumberBlockIds();
    hasGeomChange = true;
    sendDataToStreamlit();
    updateStatus(`Created: ${currentRect.Block_ID}`);
  }
  currentRect = null;
  redrawCanvas();
}

function resizeRectangle(pos){
  if (!originalRect || !resizeStartPos) return;
  const dx = pos.x - resizeStartPos.x;
  const dy = pos.y - resizeStartPos.y;
  if (Math.abs(dx) < RESIZE_THRESHOLD && Math.abs(dy) < RESIZE_THRESHOLD) return;

  let {x,y,width,height} = originalRect;
  switch (resizeHandle) {
    case 'nw':
      x = Math.min(originalRect.x + originalRect.width - MIN_RECT_SIZE, originalRect.x + dx);
      y = Math.min(originalRect.y + originalRect.height- MIN_RECT_SIZE, originalRect.y + dy);
      width  = originalRect.width  - (x - originalRect.x);
      height = originalRect.height - (y - originalRect.y);
      break;
    case 'ne':
      y = Math.min(originalRect.y + originalRect.height- MIN_RECT_SIZE, originalRect.y + dy);
      width  = Math.max(MIN_RECT_SIZE, originalRect.width + dx);
      height = originalRect.height - (y - originalRect.y);
      break;
    case 'se':
      width  = Math.max(MIN_RECT_SIZE, originalRect.width + dx);
      height = Math.max(MIN_RECT_SIZE, originalRect.height+ dy);
      break;
    case 'sw':
      x = Math.min(originalRect.x + originalRect.width - MIN_RECT_SIZE, originalRect.x + dx);
      width  = originalRect.width - (x - originalRect.x);
      height = Math.max(MIN_RECT_SIZE, originalRect.height+ dy);
      break;
  }
  selectedRect.x = x; selectedRect.y = y; selectedRect.width = width; selectedRect.height = height;
  rectangles[selectedRectIndex] = selectedRect;
  updateBoundaryBoxDisplay();
  redrawCanvas();
  updateStatus(`Resizing: ${Math.round(width)} × ${Math.round(height)}`);
}

function finalizeResize(){
  if (!isResizing) return;
  isResizing = false; resizeHandle = null;
  originalRect = null; resizeStartPos = null;

  if (selectedRect.width < MIN_RECT_SIZE) selectedRect.width = MIN_RECT_SIZE;
  if (selectedRect.height< MIN_RECT_SIZE) selectedRect.height= MIN_RECT_SIZE;

  if (selectedRect.x < 0) selectedRect.x = 0;
  if (selectedRect.y < 0) selectedRect.y = 0;
  if (selectedRect.x + selectedRect.width > canvas.width)  selectedRect.x = canvas.width  - selectedRect.width;
  if (selectedRect.y + selectedRect.height> canvas.height) selectedRect.y = canvas.height - selectedRect.height;

  selectedRect.Boundary_Boxes = rectToBbox(selectedRect);
  updateBoundaryBoxDisplay();
  saveHistory();
  renumberBlockIds();
  hasGeomChange = true;
  sendDataToStreamlit();
  redrawCanvas();
  updateStatus(`Resized: ${selectedRect.Block_ID}`);
}

function dragRectangle(pos){
  const newX = Math.max(0, Math.min(canvas.width  - selectedRect.width,  pos.x - dragOffset.x));
  const newY = Math.max(0, Math.min(canvas.height - selectedRect.height, pos.y - dragOffset.y));
  if (newX !== selectedRect.x || newY !== selectedRect.y) {
    selectedRect.x = newX;
    selectedRect.y = newY;
    rectangles[selectedRectIndex] = selectedRect;
    updateBoundaryBoxDisplay();
    redrawCanvas();
    updateStatus(`Moving: ${selectedRect.Block_ID}`);
  }
}

function finalizeDrag(){
  if (!isDragging) return;
  isDragging = false;

  // If nothing actually moved, treat as pure selection (no save/send/renumber)
  if (dragStartPos &&
      selectedRect &&
      selectedRect.x === dragStartPos.x &&
      selectedRect.y === dragStartPos.y) {
    dragStartPos = null;
    updateStatus(`Selected: ${selectedRect.Block_ID}`);
    redrawCanvas();
    return;
  }
  dragStartPos = null;

  selectedRect.Boundary_Boxes = rectToBbox(selectedRect);
  updateBoundaryBoxDisplay();
  saveHistory();
  renumberBlockIds();
  hasGeomChange = true;
  sendDataToStreamlit();
  updateStatus(`Moved: ${selectedRect.Block_ID}`);
  redrawCanvas();
}

function deleteSelectedRectangle(){
  if (selectedRectIndex >= 0) {
    const deletedId = rectangles[selectedRectIndex].Block_ID;
    rectangles.splice(selectedRectIndex, 1);
    selectedRect = null; selectedRectIndex = -1;
    hidePropertiesPanel();
    saveHistory();
    renumberBlockIds();
    hasGeomChange = true;
    redrawCanvas();
    sendDataToStreamlit();
    updateStatus(`Deleted: ${deletedId}`);
  }
}

// ----- History -----
function saveHistory(){
  historyStep++;
  if (historyStep < history.length) history = history.slice(0, historyStep);
  history.push(JSON.parse(JSON.stringify(rectangles)));
  if (history.length > MAX_HISTORY) { history.shift(); historyStep--; }
  updateHistoryButtons();
}
function undo(){
  if (historyStep > 0) {
    historyStep--;
    rectangles = JSON.parse(JSON.stringify(history[historyStep]));
    ensureUids();
    selectedRect = null; selectedRectIndex = -1;
    hidePropertiesPanel();
    renumberBlockIds(false);
    redrawCanvas(); sendDataToStreamlit();
    updateStatus("Undo performed"); updateHistoryButtons();
  }
}
function redo(){
  if (historyStep < history.length - 1) {
    historyStep++;
    rectangles = JSON.parse(JSON.stringify(history[historyStep]));
    ensureUids();
    selectedRect = null; selectedRectIndex = -1;
    hidePropertiesPanel();
    renumberBlockIds(false);
    redrawCanvas(); sendDataToStreamlit();
    updateStatus("Redo performed"); updateHistoryButtons();
  }
}
function updateHistoryButtons(){
  const undoBtn = document.getElementById('undo-btn');
  const redoBtn = document.getElementById('redo-btn');
  if (undoBtn) undoBtn.disabled = historyStep <= 0;
  if (redoBtn) redoBtn.disabled = historyStep >= history.length - 1;
}

// ----- Status -----
function updateStatus(text){
  const el = document.getElementById('status-info');
  if (el) el.textContent = text;
}

// ----- Image load -----
function loadImage(imageData){
  const img = new Image();
  img.onload = function(){
    baseCanvasWidth  = img.width;
    baseCanvasHeight = img.height;
    canvas.width  = img.width;
    canvas.height = img.height;
    applyZoomCss();

    window.backgroundImage = img; imageLoaded = true;
    redrawCanvas(); centerCanvas();
    Streamlit.setFrameHeight(Math.max(600, Math.min(900, img.height + 150)));
    updateStatus(`Image loaded: ${img.width}x${img.height}`);
  };
  img.src = imageData;
}

// ----- RENDER HANDLER -----
function onRender(event){
  const data = event.detail.args || {};
  if (!window.__rendered) { initCanvas(); window.__rendered = true; }

  // Instance, timeout, ocr flag
  if (!INSTANCE_ID && data._instance_id) INSTANCE_ID = data._instance_id;
  if (typeof data.ocr_timeout_ms === 'number' && data.ocr_timeout_ms > 0) {
    OCR_TIMEOUT_MS = data.ocr_timeout_ms;
  }
  if (typeof data.ocr_enabled !== 'undefined') ocrEnabled = !!data.ocr_enabled;

  // Load image once
  if (data.image_data && !imageLoaded) loadImage(data.image_data);

  // Handle OCR response (only for this instance)
  if (data.ocr_response && typeof data.ocr_response.text !== 'undefined') {
    const r = data.ocr_response;
    if (!r._instance_id || r._instance_id !== INSTANCE_ID) return;

    const ocrText = r.text;
    const rectIndex = r.rect_index;
    const requestId = r.request_id;

    if (requestId === currentOCRRequestId) {
      if (rectIndex >= 0 && rectIndex < rectangles.length) {
        rectangles[rectIndex].Text_Content = ocrText;
        if (rectIndex === selectedRectIndex) {
          selectedRect.Text_Content = ocrText;
          const textContentElement = document.getElementById('text-content');
          if (textContentElement) textContentElement.value = ocrText;
          resetOCRButton();
        }
        isProcessingOCR = false;
        currentOCRRequestId = null;
        currentlyProcessingBlockId = null;
        redrawCanvas();
        saveHistory();
        hasPropEdits = false;
        updateStatus(`OCR completed for ${rectangles[rectIndex].Block_ID}`);
        sendDataToStreamlit();
      }
    }
    return;
  }

  // General rectangle updates from Python (ignore immediate echo)
  if (Array.isArray(data.rectangles)) {
    if (skipNextUpdate) { skipNextUpdate = false; return; }

    // Build our internal rectangles but IGNORE incoming Block_IDs:
    const incoming = data.rectangles.map(r => ({
      _uid: uid(),
      x: r.x || 0, y: r.y || 0, width: r.width || 100, height: r.height || 50,
      Block_ID: 'block_temp',
      Block_Type: r.Block_Type || 'Text',
      Text_Content: r.Text_Content || '',
      Text_ID: r.Text_ID || '',
      Boundary_Boxes: r.Boundary_Boxes || [0,0,100,50],
    }));

    const newRectsStr = JSON.stringify(incoming.map(packRect));
    const curRectsStr = JSON.stringify(rectangles.map(packRect));
    if (newRectsStr !== curRectsStr) {
      rectangles = incoming;
      if (typeof data.selected_index === 'number') {
        selectedRectIndex = data.selected_index;
        selectedRect = rectangles[selectedRectIndex] || null;
      } else {
        selectedRectIndex = -1;
        selectedRect = null;
      }
      renumberBlockIds(false);
      redrawCanvas();
      updateStatus(`Loaded ${rectangles.length} rectangles`);
    }
  }

  // Allow Python to update the color map
  if (data.block_type_colors) {
    blockTypeColors = data.block_type_colors;
  }
}

// Streamlit bridge
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
Streamlit.setFrameHeight(700);

// DOM ready fallback
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (!window.__rendered) { initCanvas(); window.__rendered = true; }
  });
} else if (!window.__rendered) {
  initCanvas(); window.__rendered = true;
}
