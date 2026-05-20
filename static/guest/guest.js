// =========================================================
// SEASONAL GUEST PAGE JAVASCRIPT
// =========================================================

// Season Configuration
const SEASONS = {
  spring: {
    name: 'Bahor',
    icon: '🌸',
    description: 'Tabiat uyg\'onadi, gullar ochiladi va yangi boshlanishlar kuni.',
    temp: '18°C',
    humidity: '65%',
    daylight: '12h',
    colors: ['#ff6b6b', '#4ecdc4', '#ffe66d', '#95e1d3'],
    background: 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=1920&q=80',
    audio: 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'
  },
  summer: {
    name: 'Yoz',
    icon: '☀️',
    description: 'Quyosh nurlari, issiq kunlar va dengiz dam olish vaqti.',
    temp: '28°C',
    humidity: '45%',
    daylight: '15h',
    colors: ['#ff6b6b', '#ffd93d', '#6bcf7f', '#4d96ff'],
    background: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1920&q=80',
    audio: 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'
  },
  autumn: {
    name: 'Kuz',
    icon: '🍂',
    description: 'Barglar sariqlashadi, havo salqinlashadi va hosil yig\'im-terim vaqti.',
    temp: '15°C',
    humidity: '70%',
    daylight: '10h',
    colors: ['#d4a574', '#e76f51', '#f4a261', '#2a9d8f'],
    background: 'https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?w=1920&q=80',
    audio: 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'
  },
  winter: {
    name: 'Qish',
    icon: '❄️',
    description: 'Qor yog\'adi, havo sovuq va issiq ocha atrofida oilaviy vaqtlar.',
    temp: '2°C',
    humidity: '80%',
    daylight: '8h',
    colors: ['#a8d8ea', '#aa96da', '#fcbad3', '#ffffd2'],
    background: 'https://images.unsplash.com/photo-1517685352747-0e1f2022e8eb?w=1920&q=80',
    audio: 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'
  }
};

// Current State
let state = {
  season: 'spring',
  blur: 5,
  brightness: 30,
  effectsIntensity: 70,
  overlayColor: 'none',
  overlayOpacity: 0,
  volume: 50,
  soundOn: false,
  currentBackgroundIndex: 0
};

// DOM Elements
const seasonBg = document.getElementById('season-bg');
const seasonVideo = document.getElementById('season-video');
const colorOverlay = document.getElementById('color-overlay');
const effectsCanvas = document.getElementById('effects-canvas');
const loadingOverlay = document.getElementById('loading-overlay');
const seasonAudio = document.getElementById('season-audio');
const panel = document.getElementById('panel');
const toast = document.getElementById('toast');

// =========================================================
// SEASON DETECTION
// =========================================================
function detectSeason() {
  const month = new Date().getMonth() + 1; // 1-12
  
  if (month >= 3 && month <= 5) {
    return 'spring';
  } else if (month >= 6 && month <= 8) {
    return 'summer';
  } else if (month >= 9 && month <= 11) {
    return 'autumn';
  } else {
    return 'winter';
  }
}

// =========================================================
// SEASON APPLICATION
// =========================================================
function applySeason(season) {
  state.season = season;
  const seasonData = SEASONS[season];
  
  // Update body class
  document.body.className = `season-${season}`;
  
  // Update season badge
  document.getElementById('season-icon').textContent = seasonData.icon;
  document.getElementById('season-name').textContent = seasonData.name;
  
  // Update season info widget
  document.getElementById('season-info-icon').textContent = seasonData.icon;
  document.getElementById('season-info-title').textContent = `${seasonData.name} Fasli`;
  document.getElementById('season-info-description').textContent = seasonData.description;
  document.getElementById('season-temp').textContent = seasonData.temp;
  document.getElementById('season-humidity').textContent = seasonData.humidity;
  document.getElementById('season-daylight').textContent = seasonData.daylight;
  
  // Update background
  setBackground(seasonData.background);
  
  // Update audio
  seasonAudio.src = seasonData.audio;
  
  // Update color options with season colors
  updateColorOptions(seasonData.colors);
  
  console.log(`Season applied: ${season}`);
}

// =========================================================
// BACKGROUND MANAGEMENT
// =========================================================
function setBackground(url) {
  showLoader('Yuklanmoqda...');
  
  seasonBg.onload = () => {
    hideLoader();
    initEffects();
  };
  
  seasonBg.onerror = () => {
    hideLoader();
    showToast('❌ Rasm yuklanmadi', 'error');
  };
  
  seasonBg.src = url;
}

// =========================================================
// EFFECTS CANVAS (Simplified Particle System)
// =========================================================
let effectsInitialized = false;
let animationId = null;

function initEffects() {
  if (effectsInitialized) return;
  
  const canvas = effectsCanvas;
  const ctx = canvas.getContext('2d');
  
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  effectsInitialized = true;
  animateEffects();
}

function animateEffects() {
  const canvas = effectsCanvas;
  const ctx = canvas.getContext('2d');
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  const season = state.season;
  const intensity = state.effectsIntensity / 100;
  
  // Draw season-specific effects
  if (season === 'spring') {
    drawPetals(ctx, canvas, intensity);
  } else if (season === 'summer') {
    drawSunRays(ctx, canvas, intensity);
  } else if (season === 'autumn') {
    drawLeaves(ctx, canvas, intensity);
  } else if (season === 'winter') {
    drawSnowflakes(ctx, canvas, intensity);
  }
  
  animationId = requestAnimationFrame(animateEffects);
}

// Spring: Falling petals
let petals = [];
function drawPetals(ctx, canvas, intensity) {
  if (petals.length < 50 * intensity) {
    petals.push({
      x: Math.random() * canvas.width,
      y: -10,
      size: Math.random() * 5 + 3,
      speedX: Math.random() * 2 - 1,
      speedY: Math.random() * 1 + 0.5,
      rotation: Math.random() * 360,
      color: SEASONS.spring.colors[Math.floor(Math.random() * SEASONS.spring.colors.length)]
    });
  }
  
  petals.forEach((petal, index) => {
    petal.x += petal.speedX;
    petal.y += petal.speedY;
    petal.rotation += 1;
    
    ctx.save();
    ctx.translate(petal.x, petal.y);
    ctx.rotate(petal.rotation * Math.PI / 180);
    ctx.fillStyle = petal.color;
    ctx.globalAlpha = 0.6;
    ctx.beginPath();
    ctx.ellipse(0, 0, petal.size, petal.size / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    
    if (petal.y > canvas.height) {
      petals.splice(index, 1);
    }
  });
}

// Summer: Sun rays
let rayAngle = 0;
function drawSunRays(ctx, canvas, intensity) {
  rayAngle += 0.005;
  
  const centerX = canvas.width * 0.8;
  const centerY = canvas.height * 0.2;
  
  ctx.save();
  ctx.translate(centerX, centerY);
  ctx.rotate(rayAngle);
  
  for (let i = 0; i < 12; i++) {
    ctx.rotate(Math.PI / 6);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    const gradient = ctx.createLinearGradient(0, 0, 200, 0);
    gradient.addColorStop(0, `rgba(255, 215, 0, ${0.3 * intensity})`);
    gradient.addColorStop(1, 'rgba(255, 215, 0, 0)');
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 30;
    ctx.lineTo(200, 0);
    ctx.stroke();
  }
  
  ctx.restore();
}

// Autumn: Falling leaves
let leaves = [];
function drawLeaves(ctx, canvas, intensity) {
  if (leaves.length < 40 * intensity) {
    leaves.push({
      x: Math.random() * canvas.width,
      y: -10,
      size: Math.random() * 8 + 5,
      speedX: Math.random() * 2 - 1,
      speedY: Math.random() * 1.5 + 0.5,
      rotation: Math.random() * 360,
      color: SEASONS.autumn.colors[Math.floor(Math.random() * SEASONS.autumn.colors.length)]
    });
  }
  
  leaves.forEach((leaf, index) => {
    leaf.x += leaf.speedX + Math.sin(leaf.y / 50) * 0.5;
    leaf.y += leaf.speedY;
    leaf.rotation += 2;
    
    ctx.save();
    ctx.translate(leaf.x, leaf.y);
    ctx.rotate(leaf.rotation * Math.PI / 180);
    ctx.fillStyle = leaf.color;
    ctx.globalAlpha = 0.7;
    ctx.beginPath();
    ctx.moveTo(0, -leaf.size);
    ctx.lineTo(leaf.size / 2, 0);
    ctx.lineTo(0, leaf.size);
    ctx.lineTo(-leaf.size / 2, 0);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
    
    if (leaf.y > canvas.height) {
      leaves.splice(index, 1);
    }
  });
}

// Winter: Snowflakes
let snowflakes = [];
function drawSnowflakes(ctx, canvas, intensity) {
  if (snowflakes.length < 100 * intensity) {
    snowflakes.push({
      x: Math.random() * canvas.width,
      y: -10,
      size: Math.random() * 3 + 1,
      speedX: Math.random() * 1 - 0.5,
      speedY: Math.random() * 1 + 0.5
    });
  }
  
  snowflakes.forEach((flake, index) => {
    flake.x += flake.speedX;
    flake.y += flake.speedY;
    
    ctx.fillStyle = 'white';
    ctx.globalAlpha = 0.8;
    ctx.beginPath();
    ctx.arc(flake.x, flake.y, flake.size, 0, Math.PI * 2);
    ctx.fill();
    
    if (flake.y > canvas.height) {
      snowflakes.splice(index, 1);
    }
  });
}

// =========================================================
// DATE TIME WIDGET
// =========================================================
function updateDateTime() {
  const now = new Date();
  
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');
  
  document.getElementById('time-display').textContent = `${hours}:${minutes}`;
  document.getElementById('time-seconds').textContent = seconds;
  
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const dateStr = now.toLocaleDateString('uz-UZ', options);
  
  const dateParts = dateStr.split(', ');
  document.getElementById('date-display').textContent = dateParts.slice(1).join(', ');
  document.getElementById('day-display').textContent = dateParts[0];
}

// =========================================================
// SETTINGS PANEL
// =========================================================
function togglePanel(forceState) {
  const shouldOpen = typeof forceState === 'boolean' ? forceState : !panel.classList.contains('open');
  
  if (shouldOpen) {
    panel.classList.add('open');
    document.body.classList.add('panel-active');
    panel.setAttribute('aria-hidden', 'false');
  } else {
    panel.classList.remove('open');
    document.body.classList.remove('panel-active');
    panel.setAttribute('aria-hidden', 'true');
  }
}

function updateFilters() {
  const filter = `blur(${state.blur}px) brightness(${state.brightness / 100})`;
  seasonBg.style.filter = filter;
  seasonVideo.style.filter = filter;
  effectsCanvas.style.opacity = state.effectsIntensity / 100;
  
  if (state.overlayColor !== 'none' && state.overlayOpacity > 0) {
    colorOverlay.style.backgroundColor = state.overlayColor;
    colorOverlay.style.opacity = state.overlayOpacity / 100;
  } else {
    colorOverlay.style.opacity = 0;
  }
}

function updateColorOptions(seasonColors) {
  const colorOptions = document.getElementById('color-options');
  colorOptions.innerHTML = '';
  
  // Add "none" option
  const noneBtn = document.createElement('button');
  noneBtn.className = 'color-btn none active';
  noneBtn.dataset.color = 'none';
  noneBtn.title = 'Yo\'q';
  noneBtn.setAttribute('role', 'radio');
  noneBtn.setAttribute('aria-checked', 'true');
  noneBtn.addEventListener('click', () => selectColor(noneBtn));
  colorOptions.appendChild(noneBtn);
  
  // Add season-specific colors
  seasonColors.forEach(color => {
    const btn = document.createElement('button');
    btn.className = 'color-btn';
    btn.dataset.color = color;
    btn.style.background = color;
    btn.title = color;
    btn.setAttribute('role', 'radio');
    btn.setAttribute('aria-checked', 'false');
    btn.addEventListener('click', () => selectColor(btn));
    colorOptions.appendChild(btn);
  });
}

function selectColor(btn) {
  document.querySelectorAll('.color-btn').forEach(b => {
    b.classList.remove('active');
    b.setAttribute('aria-checked', 'false');
  });
  btn.classList.add('active');
  btn.setAttribute('aria-checked', 'true');
  state.overlayColor = btn.dataset.color;
  
  if (state.overlayColor === 'none') {
    state.overlayOpacity = 0;
    document.getElementById('overlay-range').value = 0;
    document.getElementById('overlay-val').textContent = '0%';
  } else if (state.overlayOpacity === 0) {
    state.overlayOpacity = 30;
    document.getElementById('overlay-range').value = 30;
    document.getElementById('overlay-val').textContent = '30%';
  }
  
  updateFilters();
}

// =========================================================
// AUDIO CONTROL
// =========================================================
function setSound(on) {
  state.soundOn = !!on;
  
  const soundBtn = document.getElementById('btn-sound');
  const soundToggle = document.getElementById('sound-toggle');
  
  soundBtn.classList.toggle('active', state.soundOn);
  soundBtn.textContent = state.soundOn ? '🔊' : '🔇';
  soundBtn.setAttribute('aria-pressed', state.soundOn);
  
  soundToggle.textContent = state.soundOn ? '🔊' : '🔇';
  soundToggle.setAttribute('aria-pressed', state.soundOn);
  
  if (state.soundOn) {
    seasonAudio.volume = state.volume / 100;
    seasonAudio.play().catch(() => {
      state.soundOn = false;
      syncSoundUI();
      showToast('🔇 Avtomatik ovoz bloklandi - yoqish uchun bosing', 'info');
    });
  } else {
    seasonAudio.pause();
  }
}

function syncSoundUI() {
  const soundBtn = document.getElementById('btn-sound');
  const soundToggle = document.getElementById('sound-toggle');
  
  soundBtn.classList.toggle('active', state.soundOn);
  soundBtn.textContent = state.soundOn ? '🔊' : '🔇';
  soundToggle.textContent = state.soundOn ? '🔊' : '🔇';
}

// =========================================================
// FULLSCREEN
// =========================================================
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => {
      showToast('❌ To\'liq ekran ishlamaydi', 'error');
    });
  } else {
    document.exitFullscreen();
  }
}

// =========================================================
// UTILITY FUNCTIONS
// =========================================================
function showToast(message, type = 'info') {
  toast.textContent = message;
  toast.className = 'toast show';
  if (type === 'error') toast.classList.add('error');
  if (type === 'success') toast.classList.add('success');
  setTimeout(() => toast.classList.remove('show', 'error', 'success'), 2500);
}

function showLoader(text = 'Yuklanmoqda...') {
  loadingOverlay.querySelector('.loader-text').textContent = text;
  loadingOverlay.classList.add('active');
}

function hideLoader() {
  loadingOverlay.classList.remove('active');
}

// =========================================================
// LOCAL STORAGE
// =========================================================
function saveToLocalStorage() {
  try {
    const saveData = {
      season: state.season,
      blur: state.blur,
      brightness: state.brightness,
      effectsIntensity: state.effectsIntensity,
      overlayColor: state.overlayColor,
      overlayOpacity: state.overlayOpacity,
      volume: state.volume,
      soundOn: state.soundOn
    };
    
    localStorage.setItem('guestSettings', JSON.stringify(saveData));
    showToast('✓ Sozlamalar saqlandi', 'success');
  } catch (e) {
    showToast('❌ Sozlamalar saqlanmadi', 'error');
  }
}

function loadFromLocalStorage() {
  try {
    const saved = localStorage.getItem('guestSettings');
    if (saved) {
      const data = JSON.parse(saved);
      
      state.blur = data.blur || 5;
      state.brightness = data.brightness || 30;
      state.effectsIntensity = data.effectsIntensity || 70;
      state.overlayColor = data.overlayColor || 'none';
      state.overlayOpacity = data.overlayOpacity || 0;
      state.volume = data.volume || 50;
      state.soundOn = data.soundOn || false;
      
      return true;
    }
  } catch (e) {
    console.warn('LocalStorage o\'qish xatosi:', e);
  }
  return false;
}

function resetToDefaults() {
  state.blur = 5;
  state.brightness = 30;
  state.effectsIntensity = 70;
  state.overlayColor = 'none';
  state.overlayOpacity = 0;
  state.volume = 50;
  state.soundOn = false;
  
  applyStateToUI();
  updateFilters();
  syncSoundUI();
  
  try {
    localStorage.removeItem('guestSettings');
  } catch (e) {}
  
  showToast('✓ Standartga qaytarildi', 'success');
}

function applyStateToUI() {
  document.getElementById('blur-range').value = state.blur;
  document.getElementById('blur-val').textContent = state.blur + 'px';
  
  document.getElementById('brightness-range').value = state.brightness;
  document.getElementById('brightness-val').textContent = state.brightness + '%';
  
  document.getElementById('effects-range').value = state.effectsIntensity;
  document.getElementById('effects-val').textContent = state.effectsIntensity + '%';
  
  document.getElementById('overlay-range').value = state.overlayOpacity;
  document.getElementById('overlay-val').textContent = state.overlayOpacity + '%';
  
  document.getElementById('volume-range').value = state.volume;
  document.getElementById('volume-val').textContent = state.volume + '%';
  
  document.querySelectorAll('.color-btn').forEach(btn => {
    const isActive = btn.dataset.color === state.overlayColor;
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-checked', isActive);
  });
  
  updateFilters();
  syncSoundUI();
  
  if (seasonAudio) {
    seasonAudio.volume = state.volume / 100;
  }
}

// =========================================================
// PRESET BACKGROUNDS
// =========================================================
function createPresets() {
  const presetGrid = document.getElementById('preset-grid');
  const backgrounds = {
    'Bahor': SEASONS.spring.background,
    'Yoz': SEASONS.summer.background,
    'Kuz': SEASONS.autumn.background,
    'Qish': SEASONS.winter.background
  };
  
  Object.entries(backgrounds).forEach(([label, url], index) => {
    const item = document.createElement('div');
    item.className = 'preset-item' + (index === 0 ? ' active' : '');
    item.dataset.label = label;
    item.style.backgroundImage = `url(${url})`;
    item.setAttribute('role', 'option');
    item.setAttribute('aria-selected', index === 0);
    item.setAttribute('tabindex', '0');
    
    item.addEventListener('click', () => {
      document.querySelectorAll('.preset-item').forEach(el => {
        el.classList.remove('active');
        el.setAttribute('aria-selected', 'false');
      });
      item.classList.add('active');
      item.setAttribute('aria-selected', 'true');
      setBackground(url);
    });
    
    presetGrid.appendChild(item);
  });
}

// =========================================================
// INITIALIZATION
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
  // Detect and apply season
  const currentSeason = detectSeason();
  
  // Load from localStorage if available
  loadFromLocalStorage();
  
  // Apply season
  applySeason(currentSeason);
  
  // Create presets
  createPresets();
  
  // Apply state to UI
  applyStateToUI();
  
  // Start datetime updates
  updateDateTime();
  setInterval(updateDateTime, 1000);
  
  // Setup event listeners
  setupEventListeners();
  
  // Handle window resize
  window.addEventListener('resize', () => {
    effectsCanvas.width = window.innerWidth;
    effectsCanvas.height = window.innerHeight;
  });
  
  console.log('Guest page initialized');
});

function setupEventListeners() {
  // Settings button
  document.getElementById('btn-settings').addEventListener('click', (e) => {
    e.stopPropagation();
    togglePanel();
  });
  
  // Close panel button
  document.getElementById('panel-close').addEventListener('click', () => {
    togglePanel(false);
  });
  
  // Click outside panel to close
  document.addEventListener('click', (e) => {
    if (window.innerWidth > 480 && !panel.contains(e.target) && !e.target.closest('.ui-btn') && panel.classList.contains('open')) {
      togglePanel(false);
    }
  });
  
  // Sound controls
  document.getElementById('btn-sound').addEventListener('click', () => setSound(!state.soundOn));
  document.getElementById('sound-toggle').addEventListener('click', () => setSound(!state.soundOn));
  
  // Fullscreen button
  document.getElementById('btn-fullscreen').addEventListener('click', toggleFullscreen);
  
  // Sliders
  document.getElementById('blur-range').addEventListener('input', (e) => {
    state.blur = parseInt(e.target.value);
    document.getElementById('blur-val').textContent = state.blur + 'px';
    updateFilters();
  });
  
  document.getElementById('brightness-range').addEventListener('input', (e) => {
    state.brightness = parseInt(e.target.value);
    document.getElementById('brightness-val').textContent = state.brightness + '%';
    updateFilters();
  });
  
  document.getElementById('effects-range').addEventListener('input', (e) => {
    state.effectsIntensity = parseInt(e.target.value);
    document.getElementById('effects-val').textContent = state.effectsIntensity + '%';
    updateFilters();
  });
  
  document.getElementById('overlay-range').addEventListener('input', (e) => {
    state.overlayOpacity = parseInt(e.target.value);
    document.getElementById('overlay-val').textContent = state.overlayOpacity + '%';
    updateFilters();
  });
  
  document.getElementById('volume-range').addEventListener('input', (e) => {
    state.volume = parseInt(e.target.value);
    document.getElementById('volume-val').textContent = state.volume + '%';
    seasonAudio.volume = state.volume / 100;
  });
  
  // Save and reset buttons
  document.getElementById('btn-save').addEventListener('click', saveToLocalStorage);
  document.getElementById('btn-reset').addEventListener('click', () => {
    if (confirm('Barcha sozlamalar standartga qaytariladi. Davom etasizmi?')) {
      resetToDefaults();
    }
  });
  
  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      togglePanel(false);
    }
    if (e.key === 's' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      setSound(!state.soundOn);
    }
    if (e.key === 'f' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      toggleFullscreen();
    }
    if (e.key === 'p' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      togglePanel();
    }
  });
}
