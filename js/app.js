/**
 * PANTHEON: Fine Art Exhibition & 500-Year History Engine
 * Minimalist, Intuitive, Visual-First Architecture
 * Phase 2: Curator's Detail Loupe, Mobile Bottom Sheet, & Curated Shelves
 */

(function() {
  'use strict';

  const data = window.PANTHEON_DATA;
  if (!data) {
    console.error('PANTHEON_DATA catalog failed to load.');
    return;
  }

  // Application State
  const state = {
    activeEpoch: 'all',
    searchQuery: '',
    currentView: 'gallery', // 'gallery' | 'timeline'
    spotlightIndex: 0,
    spotlightTimer: null,
    filteredMasterpieces: [],
    modalIndex: -1,
    zoomScale: 1.0,
    loupeActive: false,
    isDraggingSheet: false,
    sheetStartY: 0,
    sheetCurrentDeltaY: 0
  };

  // Magnification constant for Curator's Detail Loupe
  const LOUPE_ZOOM = 3.0;

  // DOM Elements Cache
  const dom = {
    // Spotlight Hero
    heroBg: document.getElementById('heroBg'),
    heroTitle: document.getElementById('heroTitle'),
    heroMeta: document.getElementById('heroMeta'),
    heroMpBadge: document.getElementById('heroMpBadge'),
    heroMuseum: document.getElementById('heroMuseum'),
    heroInspectBtn: document.getElementById('heroInspectBtn'),
    heroPrevBtn: document.getElementById('heroPrevBtn'),
    heroNextBtn: document.getElementById('heroNextBtn'),
    heroDots: document.getElementById('heroDots'),
    // Sticky Floating Nav & Controls
    tabGallery: document.getElementById('tabGallery'),
    tabTimeline: document.getElementById('tabTimeline'),
    epochPills: document.querySelectorAll('.epoch-pill'),
    searchInput: document.getElementById('searchInput'),
    searchClearBtn: document.getElementById('searchClearBtn'),
    // Views
    shelvesSection: document.getElementById('shelvesSection'),
    gallerySection: document.getElementById('gallerySection'),
    timelineSection: document.getElementById('timelineSection'),
    galleryGrid: document.getElementById('galleryGrid'),
    timelineContainer: document.getElementById('timelineContainer'),
    galleryCountBadge: document.getElementById('galleryCountBadge'),
    noResultsNotice: document.getElementById('noResultsNotice'),
    // Lightbox / Bottom Sheet
    lightboxModal: document.getElementById('lightboxModal'),
    modalSheetContainer: document.querySelector('.modal-sheet-container'),
    sheetHandleZone: document.getElementById('sheetHandleZone'),
    modalHeader: document.querySelector('.modal-sheet-container .h-14'),
    zoomContainer: document.getElementById('zoomContainer'),
    curatorLoupe: document.getElementById('curatorLoupe'),
    loupeToggleBtn: document.getElementById('loupeToggleBtn'),
    modalImage: document.getElementById('modalImage'),
    modalTitle: document.getElementById('modalTitle'),
    modalArtist: document.getElementById('modalArtist'),
    modalMuseum: document.getElementById('modalMuseum'),
    modalRes: document.getElementById('modalRes'),
    modalMp: document.getElementById('modalMp'),
    modalSize: document.getElementById('modalSize'),
    modalRawLink: document.getElementById('modalRawLink'),
    modalPrevBtn: document.getElementById('modalPrevBtn'),
    modalNextBtn: document.getElementById('modalNextBtn'),
    modalCloseBtn: document.getElementById('modalCloseBtn'),
    zoomInBtn: document.getElementById('zoomInBtn'),
    zoomOutBtn: document.getElementById('zoomOutBtn'),
    zoomResetBtn: document.getElementById('zoomResetBtn')
  };

  // Helper: Image Source Resolver
  function resolveImgSrc(item) {
    if (window.location.protocol.startsWith('http')) {
      return item.HighResUrl || item.LocalRelativePath;
    }
    return item.LocalRelativePath || item.HighResUrl;
  }

  // =========================================================================
  // 1. SPOTLIGHT HERO ENGINE
  // =========================================================================
  function initSpotlightHero() {
    const spotlights = data.spotlights && data.spotlights.length > 0 
      ? data.spotlights 
      : data.masterpieces.slice(0, 5);

    function renderSpotlight(index, animate = true) {
      const item = spotlights[index];
      if (!item) return;

      state.spotlightIndex = index;

      if (dom.heroBg) {
        if (animate) dom.heroBg.style.opacity = '0.3';
        setTimeout(() => {
          dom.heroBg.src = resolveImgSrc(item);
          dom.heroBg.style.opacity = '1';
        }, animate ? 200 : 0);
      }

      if (dom.heroTitle) dom.heroTitle.textContent = item.Title;
      if (dom.heroMeta) dom.heroMeta.textContent = `${item.Artist} (${item.Year})`;
      if (dom.heroMuseum) dom.heroMuseum.textContent = item.Museum || 'Museum Collection';
      if (dom.heroMpBadge) dom.heroMpBadge.textContent = `${item.Megapixels.toFixed(1)} MP`;

      if (dom.heroInspectBtn) {
        dom.heroInspectBtn.onclick = () => window.openMasterpieceModal(item.FileName);
      }

      // Update dots
      if (dom.heroDots) {
        dom.heroDots.innerHTML = '';
        spotlights.forEach((_, i) => {
          const dot = document.createElement('button');
          dot.className = `w-2 h-2 rounded-full transition-all ${i === index ? 'bg-amber-400 w-6' : 'bg-slate-600 hover:bg-slate-400'}`;
          dot.onclick = () => {
            renderSpotlight(i);
            resetSpotlightTimer();
          };
          dom.heroDots.appendChild(dot);
        });
      }
    }

    function nextSpotlight() {
      const nextIdx = (state.spotlightIndex + 1) % spotlights.length;
      renderSpotlight(nextIdx);
    }

    function prevSpotlight() {
      const prevIdx = (state.spotlightIndex - 1 + spotlights.length) % spotlights.length;
      renderSpotlight(prevIdx);
    }

    function resetSpotlightTimer() {
      if (state.spotlightTimer) clearInterval(state.spotlightTimer);
      state.spotlightTimer = setInterval(nextSpotlight, 6500);
    }

    if (dom.heroNextBtn) dom.heroNextBtn.onclick = () => { nextSpotlight(); resetSpotlightTimer(); };
    if (dom.heroPrevBtn) dom.heroPrevBtn.onclick = () => { prevSpotlight(); resetSpotlightTimer(); };

    renderSpotlight(0, false);
    resetSpotlightTimer();
  }

  // =========================================================================
  // 2. CURATED HORIZONTAL SHELVES ENGINE
  // =========================================================================
  function renderCuratedShelves() {
    if (!dom.shelvesSection) return;

    const shelves = [
      {
        id: 'shelf-crown-jewels',
        title: '👑 The Crown Jewels of Art History',
        subtitle: 'The universally recognized masterworks defining half a millennium of artistic genius.',
        items: data.masterpieces.filter(m => m.isCrownJewel).slice(0, 12)
      },
      {
        id: 'shelf-ultra-res',
        title: '🔬 Ultra-HD Museum Scans (20+ Megapixels)',
        subtitle: 'Peak resolution master captures—inspect microscopic brushstrokes, impasto, and cracked glaze.',
        items: data.masterpieces.filter(m => m.Megapixels >= 20.0)
      },
      {
        id: 'shelf-shadow-light',
        title: '🕯️ Masters of Shadow & Light (Baroque)',
        subtitle: 'The dramatic tenebrism of Caravaggio & the golden psychological impasto of Rembrandt.',
        items: data.masterpieces.filter(m => m.ArtistId === 'caravaggio' || m.ArtistId === 'rembrandt')
      },
      {
        id: 'shelf-impressionism',
        title: '🌸 The Plein-Air Revolution (Impressionism)',
        subtitle: 'Claude Monet’s fleeting optical vibrations & Vincent van Gogh’s raw emotional swirls.',
        items: data.masterpieces.filter(m => m.ArtistId === 'monet' || m.ArtistId === 'vangogh').slice(0, 12)
      }
    ];

    dom.shelvesSection.innerHTML = '';

    shelves.forEach((shelf, idx) => {
      const block = document.createElement('div');
      block.className = 'space-y-3';

      block.innerHTML = `
        <div class="flex items-end justify-between px-1">
          <div>
            <h3 class="font-monumental text-lg sm:text-xl font-bold text-white flex items-center gap-2">
              ${shelf.title}
            </h3>
            <p class="font-editorial text-xs sm:text-sm text-slate-400 italic mt-0.5">${shelf.subtitle}</p>
          </div>
          <div class="hidden sm:flex items-center gap-1.5 flex-shrink-0">
            <button 
              onclick="window.scrollShelf('${shelf.id}', -420)" 
              title="Scroll Left" 
              class="w-7 h-7 rounded-full bg-slate-800/90 hover:bg-amber-500 hover:text-slate-950 text-slate-300 text-xs flex items-center justify-center border border-slate-700 transition shadow cursor-pointer select-none"
            >
              &#10094;
            </button>
            <button 
              onclick="window.scrollShelf('${shelf.id}', 420)" 
              title="Scroll Right" 
              class="w-7 h-7 rounded-full bg-slate-800/90 hover:bg-amber-500 hover:text-slate-950 text-slate-300 text-xs flex items-center justify-center border border-slate-700 transition shadow cursor-pointer select-none"
            >
              &#10095;
            </button>
          </div>
        </div>
        
        <div id="${shelf.id}" class="flex gap-4 overflow-x-auto no-scrollbar shelf-snap py-2 px-1 scroll-smooth">
          ${shelf.items.map(item => `
            <div 
              class="group flex-shrink-0 w-60 sm:w-72 bg-slate-900/80 border border-slate-800 hover:border-amber-400/50 rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer flex flex-col"
              onclick="window.openMasterpieceModal('${item.FileName}')"
            >
              <div class="aspect-[4/3] w-full relative overflow-hidden bg-slate-950">
                <img 
                  src="${resolveImgSrc(item)}" 
                  alt="${item.Title}" 
                  loading="lazy" 
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
                  onerror="if (this.src !== '${item.HighResUrl}') { this.src = '${item.HighResUrl}'; }"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-75 group-hover:opacity-40 transition-opacity"></div>
                <span class="absolute top-2.5 left-2.5 px-2 py-0.5 rounded-md text-[10px] font-mono font-bold ${item.Megapixels >= 20.0 ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 animate-pulse' : 'bg-amber-500/20 text-amber-300 border-amber-500/30'} backdrop-blur-md border">
                  ${item.Megapixels.toFixed(1)} MP
                </span>
                <span class="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-md text-[10px] font-mono bg-black/60 text-slate-300 backdrop-blur-md">
                  ${item.Year}
                </span>
                <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-20">
                  <span class="bg-amber-500 text-slate-950 px-3 py-1 rounded-full text-xs font-bold shadow-xl">
                    🔍 Inspect Loupe
                  </span>
                </div>
              </div>
              <div class="p-3 flex-1 flex flex-col justify-between">
                <div>
                  <p class="text-[11px] font-mono text-amber-400/90 truncate">${item.Artist}</p>
                  <h4 class="font-editorial text-sm font-bold text-white group-hover:text-amber-300 transition-colors line-clamp-1 mt-0.5">${item.Title}</h4>
                </div>
                <p class="text-[10px] text-slate-400 truncate mt-2">🏛️ ${item.Museum || 'Museum Collection'}</p>
              </div>
            </div>
          `).join('')}
        </div>
      `;

      dom.shelvesSection.appendChild(block);
    });
  }

  // Horizontal Shelf Smooth Scroll
  window.scrollShelf = function(shelfId, offset) {
    const el = document.getElementById(shelfId);
    if (el) {
      el.scrollBy({ left: offset, behavior: 'smooth' });
    }
  };

  // =========================================================================
  // 3. MASTER GALLERY ENGINE (Grid View)
  // =========================================================================
  function applyFilters() {
    let list = [...data.masterpieces];

    // Epoch filter
    if (state.activeEpoch !== 'all') {
      list = list.filter(item => item.EpochId === state.activeEpoch);
    }

    // Search query filter
    if (state.searchQuery.trim()) {
      const q = state.searchQuery.toLowerCase().trim();
      list = list.filter(item => {
        return (
          item.Title.toLowerCase().includes(q) ||
          item.Artist.toLowerCase().includes(q) ||
          (item.Museum && item.Museum.toLowerCase().includes(q)) ||
          item.Year.toLowerCase().includes(q)
        );
      });
    }

    state.filteredMasterpieces = list;
    renderGallery();
  }

  function renderGallery() {
    if (!dom.galleryGrid) return;
    dom.galleryGrid.innerHTML = '';

    const list = state.filteredMasterpieces;
    if (dom.galleryCountBadge) {
      dom.galleryCountBadge.textContent = `${list.length} Works`;
    }

    if (list.length === 0) {
      if (dom.noResultsNotice) dom.noResultsNotice.classList.remove('hidden');
      return;
    }
    if (dom.noResultsNotice) dom.noResultsNotice.classList.add('hidden');

    const fragment = document.createDocumentFragment();

    list.forEach((item, index) => {
      const card = document.createElement('article');
      card.className = 'group relative bg-slate-900/70 border border-slate-800 hover:border-amber-500/50 rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 flex flex-col cursor-pointer';

      const isUltraRes = item.Megapixels >= 20.0;
      const badgeColor = isUltraRes 
        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 animate-pulse' 
        : 'bg-amber-500/20 text-amber-300 border-amber-500/40';

      card.innerHTML = `
        <div class="img-container aspect-[4/3] w-full relative overflow-hidden bg-slate-950 flex items-center justify-center">
          <img 
            src="${resolveImgSrc(item)}" 
            alt="${item.Title}" 
            loading="lazy" 
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
            onerror="if (this.src !== '${item.HighResUrl}') { this.src = '${item.HighResUrl}'; }"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent opacity-75 group-hover:opacity-50 transition-opacity"></div>
          
          <div class="absolute top-3 left-3 flex gap-1.5 z-10">
            <span class="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold border backdrop-blur-md ${badgeColor}">
              ${item.Megapixels.toFixed(1)} MP
            </span>
          </div>

          <div class="absolute top-3 right-3 z-10">
            <span class="px-2 py-0.5 rounded-md text-[10px] font-mono bg-black/60 backdrop-blur-md text-slate-300 border border-slate-700/50">
              ${item.Width} × ${item.Height}
            </span>
          </div>

          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-20">
            <span class="bg-amber-500 text-slate-950 px-3.5 py-1.5 rounded-full text-xs font-bold shadow-xl">
              🔍 Inspect High-Res
            </span>
          </div>
        </div>

        <div class="p-4 flex-1 flex flex-col justify-between bg-slate-900/90">
          <div>
            <div class="flex items-center justify-between text-xs text-amber-400/90 font-mono mb-1">
              <span>${item.Artist}</span>
              <span>${item.Year}</span>
            </div>
            <h3 class="font-editorial text-base font-bold text-slate-100 leading-snug group-hover:text-amber-300 transition-colors line-clamp-2">
              ${item.Title}
            </h3>
          </div>
          
          <div class="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-sans">
            <span class="truncate max-w-[200px]" title="${item.Museum || 'Museum Collection'}">
              🏛️ ${item.Museum || 'Museum Collection'}
            </span>
            <span class="font-mono text-slate-500">${item.FileSizeMB} MB</span>
          </div>
        </div>
      `;

      card.onclick = () => openModal(index);
      fragment.appendChild(card);
    });

    dom.galleryGrid.appendChild(fragment);
  }

  // =========================================================================
  // 4. TIMELINE WITH CURATOR MICRO-PLAQUES & PROGRESSIVE DISCLOSURE
  // =========================================================================
  function renderTimeline() {
    if (!dom.timelineContainer) return;
    dom.timelineContainer.innerHTML = '';

    const list = data.artists;
    const fragment = document.createDocumentFragment();

    list.forEach((artist) => {
      const works = data.masterpieces.filter(m => m.ArtistId === artist.id);

      const section = document.createElement('article');
      section.className = 'relative bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8 backdrop-blur-md hover:border-amber-400/30 transition-all';

      // Innovations chips
      const innovationPills = (artist.innovations || []).map(inv => `
        <span class="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
          ✦ ${inv}
        </span>
      `).join('');

      // Signature Works Horizontal Reel
      const worksReel = works.map(w => `
        <div 
          class="flex-shrink-0 w-44 sm:w-52 group rounded-xl overflow-hidden border border-slate-800 bg-slate-950 aspect-[4/3] cursor-pointer hover:border-amber-400 transition-all"
          onclick="window.openMasterpieceModal('${w.FileName}')"
        >
          <div class="relative w-full h-full">
            <img src="${resolveImgSrc(w)}" alt="${w.Title}" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" onerror="if (this.src !== '${w.HighResUrl}') { this.src = '${w.HighResUrl}'; }" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent flex flex-col justify-end p-2.5">
              <p class="text-white text-xs font-bold line-clamp-1 group-hover:text-amber-300 transition-colors">${w.Title}</p>
              <p class="text-slate-400 text-[10px] font-mono">${w.Megapixels.toFixed(1)} MP &bull; ${w.Year}</p>
            </div>
          </div>
        </div>
      `).join('');

      section.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div class="flex items-center gap-2">
            <span class="badge-${artist.epochId} px-3 py-0.5 rounded-full text-xs font-mono font-semibold">
              ${artist.epochName}
            </span>
            <span class="text-xs font-mono text-slate-400">
              ${artist.lifespan}
            </span>
          </div>
          <span class="text-xs text-slate-400 font-sans">
            📍 ${artist.location}
          </span>
        </div>

        <!-- Master Name & Punchy Micro-Plaque Tagline -->
        <h3 class="font-monumental text-2xl sm:text-3xl font-bold text-white mt-1">
          ${artist.name}
        </h3>
        <p class="font-editorial italic text-base sm:text-lg text-amber-300/90 mt-1 max-w-3xl leading-relaxed">
          "${artist.tagline || artist.epithet}"
        </p>

        <!-- Technical Innovation Chips -->
        <div class="flex flex-wrap gap-2 mt-3 mb-5">
          ${innovationPills}
        </div>

        <!-- Horizontal Signature Works Reel -->
        <div class="my-4">
          <h5 class="text-xs font-mono uppercase tracking-widest text-slate-400 mb-2.5">
            Key Masterworks in Collection (${works.length})
          </h5>
          <div class="flex gap-3 overflow-x-auto no-scrollbar shelf-snap py-1">
            ${worksReel}
          </div>
        </div>

        <!-- Progressive Disclosure: Expandable Curator Drawer -->
        <div class="mt-4 pt-4 border-t border-slate-800/80">
          <button 
            class="curator-toggle-btn text-xs font-semibold text-amber-400 hover:text-amber-300 flex items-center gap-1.5 transition-colors focus:outline-none cursor-pointer"
            onclick="window.toggleCuratorDrawer(this)"
          >
            <span>📖</span>
            <span class="btn-text">Read Curator's Historical Analysis</span>
            <span class="chevron">▾</span>
          </button>
          
          <div class="curator-drawer mt-3 grid sm:grid-cols-2 gap-4 text-xs text-slate-300 leading-relaxed font-sans">
            <div class="bg-slate-950/70 border border-slate-800 p-4 rounded-xl">
              <strong class="text-amber-400 block font-mono uppercase tracking-wider mb-1">👑 Why They Belong:</strong>
              ${artist.whyBelongs}
            </div>
            <div class="bg-slate-950/70 border border-slate-800 p-4 rounded-xl">
              <strong class="text-cyan-400 block font-mono uppercase tracking-wider mb-1">⚡ Evolutionary Role:</strong>
              ${artist.evolutionRole}
            </div>
          </div>
        </div>
      `;

      fragment.appendChild(section);
    });

    dom.timelineContainer.appendChild(fragment);
  }

  // Toggle Curator Note Drawer (Accordion)
  window.toggleCuratorDrawer = function(btn) {
    const drawer = btn.parentElement.querySelector('.curator-drawer');
    const chevron = btn.querySelector('.chevron');
    const btnText = btn.querySelector('.btn-text');

    if (!drawer) return;

    const isOpen = drawer.classList.contains('open');
    if (isOpen) {
      drawer.classList.remove('open');
      chevron.textContent = '▾';
      btnText.textContent = "Read Curator's Historical Analysis";
    } else {
      drawer.classList.add('open');
      chevron.textContent = '▴';
      btnText.textContent = "Close Curator's Analysis";
    }
  };

  // =========================================================================
  // 5. LIGHTBOX MODAL & MOBILE BOTTOM SHEET
  // =========================================================================
  function openModal(index) {
    const list = state.filteredMasterpieces;
    if (index < 0 || index >= list.length) return;

    state.modalIndex = index;
    state.zoomScale = 1.0;
    deactivateLoupe();
    updateModalContent();

    dom.lightboxModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Reset bottom sheet transform
    if (dom.modalSheetContainer) {
      dom.modalSheetContainer.style.transform = '';
    }
  }

  function closeModal() {
    deactivateLoupe();
    dom.lightboxModal.classList.add('hidden');
    document.body.style.overflow = '';
    state.modalIndex = -1;
    state.zoomScale = 1.0;
    if (dom.modalSheetContainer) {
      dom.modalSheetContainer.style.transform = '';
    }
  }

  function updateModalContent() {
    const item = state.filteredMasterpieces[state.modalIndex];
    if (!item) return;

    const imgSrc = resolveImgSrc(item);
    dom.modalImage.src = imgSrc;
    dom.modalImage.onerror = () => {
      if (dom.modalImage.src !== item.HighResUrl) {
        dom.modalImage.src = item.HighResUrl;
      }
    };

    dom.modalImage.style.transform = `scale(${state.zoomScale})`;

    dom.modalTitle.textContent = item.Title;
    dom.modalArtist.textContent = `${item.Artist} (${item.Year})`;
    dom.modalMuseum.textContent = item.Museum || 'Museum Collection';
    dom.modalRes.textContent = `${item.Width} × ${item.Height} px`;
    dom.modalMp.textContent = `${item.Megapixels.toFixed(2)} MP`;
    dom.modalSize.textContent = `${item.FileSizeMB} MB`;

    dom.modalRawLink.href = item.HighResUrl || item.LocalRelativePath;

    // Refresh loupe if active
    if (state.loupeActive) {
      dom.curatorLoupe.style.backgroundImage = `url('${item.HighResUrl || imgSrc}')`;
    }
  }

  function stepModal(dir) {
    const list = state.filteredMasterpieces;
    const newIdx = state.modalIndex + dir;
    if (newIdx >= 0 && newIdx < list.length) {
      state.modalIndex = newIdx;
      state.zoomScale = 1.0;
      updateModalContent();
    }
  }

  function adjustZoom(delta) {
    state.zoomScale = Math.max(0.5, Math.min(4.0, state.zoomScale + delta));
    if (dom.modalImage) {
      dom.modalImage.style.transform = `scale(${state.zoomScale})`;
    }
  }

  function resetZoom() {
    state.zoomScale = 1.0;
    if (dom.modalImage) {
      dom.modalImage.style.transform = `scale(1.0)`;
    }
  }

  window.openMasterpieceModal = function(fileName) {
    const idx = state.filteredMasterpieces.findIndex(m => m.FileName === fileName);
    if (idx !== -1) {
      openModal(idx);
    } else {
      state.activeEpoch = 'all';
      state.searchQuery = '';
      applyFilters();
      const newIdx = state.filteredMasterpieces.findIndex(m => m.FileName === fileName);
      if (newIdx !== -1) openModal(newIdx);
    }
  };

  // =========================================================================
  // 6. CURATOR'S DETAIL LOUPE ENGINE (3.0× Magnification)
  // =========================================================================
  function toggleLoupe() {
    if (state.loupeActive) {
      deactivateLoupe();
    } else {
      activateLoupe();
    }
  }

  function activateLoupe() {
    state.loupeActive = true;
    if (dom.loupeToggleBtn) {
      dom.loupeToggleBtn.classList.add('bg-amber-500', 'text-slate-950', 'font-bold', 'border-amber-400');
      dom.loupeToggleBtn.classList.remove('bg-slate-800', 'text-slate-300');
    }
    if (dom.zoomContainer) dom.zoomContainer.classList.add('loupe-active-canvas');
    if (dom.modalImage) dom.modalImage.classList.add('loupe-active-canvas');

    const item = state.filteredMasterpieces[state.modalIndex];
    if (item && dom.curatorLoupe) {
      const highRes = item.HighResUrl || resolveImgSrc(item);
      dom.curatorLoupe.style.backgroundImage = `url('${highRes}')`;
    }
  }

  function deactivateLoupe() {
    state.loupeActive = false;
    if (dom.loupeToggleBtn) {
      dom.loupeToggleBtn.classList.remove('bg-amber-500', 'text-slate-950', 'font-bold', 'border-amber-400');
      dom.loupeToggleBtn.classList.add('bg-slate-800', 'text-slate-300');
    }
    if (dom.zoomContainer) dom.zoomContainer.classList.remove('loupe-active-canvas');
    if (dom.modalImage) dom.modalImage.classList.remove('loupe-active-canvas');
    if (dom.curatorLoupe) dom.curatorLoupe.classList.remove('active');
  }

  function handleLoupeMove(e) {
    if (!state.loupeActive || !dom.curatorLoupe || !dom.modalImage || !dom.zoomContainer) return;

    const imgRect = dom.modalImage.getBoundingClientRect();
    const containerRect = dom.zoomContainer.getBoundingClientRect();

    const isTouch = !!e.touches;
    const clientX = isTouch ? e.touches[0].clientX : e.clientX;
    const clientY = isTouch ? e.touches[0].clientY : e.clientY;

    // Check bounds: within artwork image with a small tolerance
    if (
      clientX < imgRect.left - 5 || 
      clientX > imgRect.right + 5 || 
      clientY < imgRect.top - 5 || 
      clientY > imgRect.bottom + 5
    ) {
      dom.curatorLoupe.classList.remove('active');
      return;
    }

    dom.curatorLoupe.classList.add('active');

    // On mobile touch: position loupe 65px above finger contact so thumb doesn't obscure magnification!
    const offsetY = isTouch ? -65 : 0;
    const loupeX = clientX - containerRect.left;
    const loupeY = clientY - containerRect.top + offsetY;

    dom.curatorLoupe.style.left = `${loupeX}px`;
    dom.curatorLoupe.style.top = `${loupeY}px`;

    // High resolution background calculations
    const bgW = imgRect.width * LOUPE_ZOOM;
    const bgH = imgRect.height * LOUPE_ZOOM;
    dom.curatorLoupe.style.backgroundSize = `${bgW}px ${bgH}px`;

    const normX = Math.max(0, Math.min(1, (clientX - imgRect.left) / imgRect.width));
    const normY = Math.max(0, Math.min(1, (clientY - imgRect.top) / imgRect.height));

    const bgPosX = -(normX * bgW - 90);
    const bgPosY = -(normY * bgH - 90);
    dom.curatorLoupe.style.backgroundPosition = `${bgPosX}px ${bgPosY}px`;
  }

  // =========================================================================
  // 7. MOBILE BOTTOM SHEET TOUCH SWIPE GESTURES
  // =========================================================================
  function initMobileSheetGestures() {
    const handleZone = dom.sheetHandleZone;
    const header = dom.modalHeader;
    const sheet = dom.modalSheetContainer;
    if (!sheet) return;

    function onTouchStart(e) {
      if (window.innerWidth > 768) return; // Desktop uses standard modal
      state.isDraggingSheet = true;
      state.sheetStartY = e.touches[0].clientY;
      state.sheetCurrentDeltaY = 0;
      sheet.style.transition = 'none';
    }

    function onTouchMove(e) {
      if (!state.isDraggingSheet) return;
      const currentY = e.touches[0].clientY;
      const deltaY = currentY - state.sheetStartY;

      if (deltaY > 0) {
        // Dragging downwards
        state.sheetCurrentDeltaY = deltaY;
        sheet.style.transform = `translateY(${deltaY}px)`;
      } else {
        // Slight resistance when pulling upwards
        sheet.style.transform = `translateY(${deltaY * 0.15}px)`;
      }
    }

    function onTouchEnd(e) {
      if (!state.isDraggingSheet) return;
      state.isDraggingSheet = false;
      sheet.style.transition = 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)';

      if (state.sheetCurrentDeltaY > 80) {
        // Threshold passed -> Dismiss bottom sheet
        sheet.style.transform = 'translateY(100%)';
        setTimeout(() => {
          closeModal();
          sheet.style.transform = '';
        }, 220);
      } else {
        // Snap back to open position
        sheet.style.transform = 'translateY(0)';
      }
      state.sheetCurrentDeltaY = 0;
    }

    if (handleZone) {
      handleZone.addEventListener('touchstart', onTouchStart, { passive: true });
      handleZone.addEventListener('touchmove', onTouchMove, { passive: true });
      handleZone.addEventListener('touchend', onTouchEnd, { passive: true });
    }

    if (header) {
      header.addEventListener('touchstart', onTouchStart, { passive: true });
      header.addEventListener('touchmove', onTouchMove, { passive: true });
      header.addEventListener('touchend', onTouchEnd, { passive: true });
    }
  }

  // =========================================================================
  // 8. EVENT LISTENERS & INITIALIZATION
  // =========================================================================
  function initEvents() {
    // View tabs: Gallery vs Timeline
    if (dom.tabGallery) {
      dom.tabGallery.onclick = () => switchView('gallery');
    }
    if (dom.tabTimeline) {
      dom.tabTimeline.onclick = () => switchView('timeline');
    }

    // Epoch filter pills
    dom.epochPills.forEach(pill => {
      pill.onclick = () => {
        dom.epochPills.forEach(p => {
          p.classList.remove('bg-amber-500', 'text-slate-950', 'font-bold');
          p.classList.add('bg-slate-800/80', 'text-slate-300');
        });
        pill.classList.remove('bg-slate-800/80', 'text-slate-300');
        pill.classList.add('bg-amber-500', 'text-slate-950', 'font-bold');

        state.activeEpoch = pill.dataset.epoch;
        applyFilters();
      };
    });

    // Search input (debounced)
    if (dom.searchInput) {
      let timeout = null;
      dom.searchInput.oninput = (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          state.searchQuery = e.target.value;
          if (dom.searchClearBtn) {
            dom.searchClearBtn.classList.toggle('hidden', !state.searchQuery);
          }
          applyFilters();
        }, 150);
      };
    }

    if (dom.searchClearBtn) {
      dom.searchClearBtn.onclick = () => {
        dom.searchInput.value = '';
        state.searchQuery = '';
        dom.searchClearBtn.classList.add('hidden');
        applyFilters();
      };
    }

    // Modal controls
    if (dom.modalCloseBtn) dom.modalCloseBtn.onclick = closeModal;
    if (dom.modalPrevBtn) dom.modalPrevBtn.onclick = () => stepModal(-1);
    if (dom.modalNextBtn) dom.modalNextBtn.onclick = () => stepModal(1);
    if (dom.zoomInBtn) dom.zoomInBtn.onclick = () => adjustZoom(0.3);
    if (dom.zoomOutBtn) dom.zoomOutBtn.onclick = () => adjustZoom(-0.3);
    if (dom.zoomResetBtn) dom.zoomResetBtn.onclick = resetZoom;

    // Loupe toggle
    if (dom.loupeToggleBtn) {
      dom.loupeToggleBtn.onclick = toggleLoupe;
    }

    // Loupe cursor & touch tracking
    if (dom.zoomContainer) {
      dom.zoomContainer.addEventListener('mousemove', handleLoupeMove);
      dom.zoomContainer.addEventListener('touchmove', handleLoupeMove, { passive: true });
      dom.zoomContainer.addEventListener('mouseleave', () => {
        if (dom.curatorLoupe) dom.curatorLoupe.classList.remove('active');
      });
      dom.zoomContainer.addEventListener('touchend', () => {
        if (dom.curatorLoupe) dom.curatorLoupe.classList.remove('active');
      });
    }

    if (dom.lightboxModal) {
      dom.lightboxModal.onclick = (e) => {
        if (e.target === dom.lightboxModal) closeModal();
      };
    }

    // Mobile bottom sheet drag-to-dismiss gesture
    initMobileSheetGestures();

    // Keyboard shortcuts
    window.onkeydown = (e) => {
      if (dom.lightboxModal.classList.contains('hidden')) return;
      if (e.key === 'Escape') closeModal();
      else if (e.key === 'ArrowLeft') stepModal(-1);
      else if (e.key === 'ArrowRight') stepModal(1);
      else if (e.key === '+' || e.key === '=') adjustZoom(0.2);
      else if (e.key === '-') adjustZoom(-0.2);
      else if (e.key === '0') resetZoom();
      else if (e.key === 'l' || e.key === 'L') toggleLoupe();
    };
  }

  function switchView(view) {
    state.currentView = view;
    if (view === 'gallery') {
      dom.tabGallery.classList.add('bg-amber-500', 'text-slate-950', 'font-bold');
      dom.tabGallery.classList.remove('text-slate-400', 'hover:text-white');
      dom.tabTimeline.classList.remove('bg-amber-500', 'text-slate-950', 'font-bold');
      dom.tabTimeline.classList.add('text-slate-400', 'hover:text-white');

      dom.gallerySection.classList.remove('hidden');
      dom.timelineSection.classList.add('hidden');
    } else {
      dom.tabTimeline.classList.add('bg-amber-500', 'text-slate-950', 'font-bold');
      dom.tabTimeline.classList.remove('text-slate-400', 'hover:text-white');
      dom.tabGallery.classList.remove('bg-amber-500', 'text-slate-950', 'font-bold');
      dom.tabGallery.classList.add('text-slate-400', 'hover:text-white');

      dom.gallerySection.classList.add('hidden');
      dom.timelineSection.classList.remove('hidden');
    }
  }

  function init() {
    initSpotlightHero();
    renderCuratedShelves();
    state.filteredMasterpieces = [...data.masterpieces];
    renderGallery();
    renderTimeline();
    initEvents();
    console.log('Pantheon exhibition initialized with Phase 2 capabilities.');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
