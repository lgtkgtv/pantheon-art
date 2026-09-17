/**
 * PANTHEON: Master Art Gallery & 500-Year History Engine
 * Vanilla ES6 JavaScript for GitHub Pages & Local Hosting
 */

(function() {
  'use strict';

  // Verify catalog data is loaded
  const data = window.PANTHEON_DATA;
  if (!data) {
    console.error('PANTHEON_DATA catalog failed to load.');
    return;
  }

  // Application State
  const state = {
    activeEpoch: 'all',
    activeArtist: 'all',
    searchQuery: '',
    sortBy: 'chronological',
    activeView: 'gallery',
    filteredMasterpieces: [],
    modalIndex: -1,
    zoomScale: 1.0
  };

  // DOM Cache
  const dom = {
    galleryGrid: document.getElementById('galleryGrid'),
    historyTimeline: document.getElementById('historyTimeline'),
    artistsGrid: document.getElementById('artistsGrid'),
    epochButtons: document.querySelectorAll('.epoch-filter-btn'),
    artistFilter: document.getElementById('artistFilter'),
    sortSelect: document.getElementById('sortSelect'),
    searchInput: document.getElementById('searchInput'),
    searchClearBtn: document.getElementById('searchClearBtn'),
    galleryCountBadge: document.getElementById('galleryCountBadge'),
    noResultsNotice: document.getElementById('noResultsNotice'),
    // Modal
    lightboxModal: document.getElementById('lightboxModal'),
    modalImage: document.getElementById('modalImage'),
    modalTitle: document.getElementById('modalTitle'),
    modalArtist: document.getElementById('modalArtist'),
    modalYear: document.getElementById('modalYear'),
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
    zoomResetBtn: document.getElementById('zoomResetBtn'),
    zoomContainer: document.getElementById('zoomContainer')
  };

  // Helper: Image Source Resolver with Graceful Fallback
  function resolveImgSrc(item) {
    if (window.location.protocol.startsWith('http')) {
      return item.HighResUrl || item.LocalRelativePath;
    }
    return item.LocalRelativePath || item.HighResUrl;
  }

  // Populate Artist Dropdown Filter
  function initArtistFilter() {
    if (!dom.artistFilter) return;
    dom.artistFilter.innerHTML = '<option value="all">All 13 Masters (All Catalogs)</option>';
    data.artists.forEach(a => {
      const opt = document.createElement('option');
      opt.value = a.id;
      opt.textContent = `${a.name} (${a.lifespan})`;
      dom.artistFilter.appendChild(opt);
    });
  }

  // Filter & Sort Logic
  function applyFilters() {
    let list = [...data.masterpieces];

    // Filter: Epoch
    if (state.activeEpoch !== 'all') {
      list = list.filter(item => item.EpochId === state.activeEpoch);
    }

    // Filter: Artist
    if (state.activeArtist !== 'all') {
      list = list.filter(item => item.ArtistId === state.activeArtist);
    }

    // Filter: Search Query
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

    // Sorting
    if (state.sortBy === 'chronological') {
      list.sort((a, b) => {
        const yearA = parseInt(a.Year.split('–')[0].replace(/[^0-9]/g, '')) || 0;
        const yearB = parseInt(b.Year.split('–')[0].replace(/[^0-9]/g, '')) || 0;
        return yearA - yearB;
      });
    } else if (state.sortBy === 'megapixels') {
      list.sort((a, b) => (b.Megapixels || 0) - (a.Megapixels || 0));
    } else if (state.sortBy === 'title') {
      list.sort((a, b) => a.Title.localeCompare(b.Title));
    } else if (state.sortBy === 'filesize') {
      list.sort((a, b) => (b.FileSizeBytes || 0) - (a.FileSizeBytes || 0));
    }

    state.filteredMasterpieces = list;
    renderGallery();
  }

  // Render Masterpiece Cards in Gallery Grid
  function renderGallery() {
    if (!dom.galleryGrid) return;
    dom.galleryGrid.innerHTML = '';

    const list = state.filteredMasterpieces;
    if (dom.galleryCountBadge) {
      dom.galleryCountBadge.textContent = `${list.length} of ${data.masterpieces.length} Masterpieces`;
    }

    if (list.length === 0) {
      if (dom.noResultsNotice) dom.noResultsNotice.classList.remove('hidden');
      return;
    }
    if (dom.noResultsNotice) dom.noResultsNotice.classList.add('hidden');

    const fragment = document.createDocumentFragment();

    list.forEach((item, index) => {
      const card = document.createElement('article');
      card.className = 'group relative bg-slate-900/80 border border-slate-800 hover:border-amber-500/50 rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl hover:shadow-amber-500/10 transition-all duration-300 flex flex-col cursor-pointer';
      
      const isUltraRes = item.Megapixels >= 20.0;
      const mpBadgeClass = isUltraRes 
        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 animate-pulse' 
        : 'bg-amber-500/20 text-amber-300 border-amber-500/40';

      const imgSrc = resolveImgSrc(item);

      card.innerHTML = `
        <div class="img-container aspect-[4/3] w-full relative overflow-hidden bg-slate-950 flex items-center justify-center">
          <img 
            src="${imgSrc}" 
            alt="${item.Title} by ${item.Artist}" 
            loading="lazy" 
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
            onerror="if (this.src !== '${item.HighResUrl}') { this.src = '${item.HighResUrl}'; }"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent opacity-80 group-hover:opacity-60 transition-opacity"></div>
          
          <div class="absolute top-3 left-3 flex flex-wrap gap-1.5 z-10">
            <span class="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold border backdrop-blur-md ${mpBadgeClass}">
              ${item.Megapixels.toFixed(2)} MP
            </span>
          </div>

          <div class="absolute top-3 right-3 z-10">
            <span class="px-2 py-0.5 rounded-md text-[11px] font-mono bg-black/60 backdrop-blur-md text-slate-300 border border-slate-700/50">
              ${item.Width} × ${item.Height}
            </span>
          </div>

          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-20">
            <span class="bg-amber-500 text-slate-950 px-3.5 py-1.5 rounded-full text-xs font-bold font-sans tracking-wide shadow-xl flex items-center gap-1.5 transform group-hover:scale-105 transition-transform">
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

      card.addEventListener('click', () => openModal(index));
      fragment.appendChild(card);
    });

    dom.galleryGrid.appendChild(fragment);
  }

  // Render 500-Year Art History Chronological Timeline
  function renderHistoryTimeline() {
    if (!dom.historyTimeline) return;
    dom.historyTimeline.innerHTML = '';

    const timelineContainer = document.createElement('div');
    timelineContainer.className = 'relative space-y-16';

    data.artists.forEach((artist) => {
      const artistWorks = data.masterpieces.filter(m => m.ArtistId === artist.id);

      const section = document.createElement('section');
      section.id = `artist-${artist.id}`;
      section.className = 'relative rounded-3xl bg-slate-900/60 border border-slate-800 p-6 sm:p-8 backdrop-blur-md shadow-xl hover:border-amber-500/30 transition-all duration-300';

      const epochClass = `badge-${artist.epochId}`;

      let thumbnailsHtml = '';
      if (artistWorks.length > 0) {
        thumbnailsHtml = `
          <div class="mt-6 pt-6 border-t border-slate-800">
            <h4 class="text-xs font-mono font-semibold uppercase tracking-widest text-amber-400 mb-3 flex items-center gap-2">
              <span>🎨</span> Crown Jewel Works in Collection (${artistWorks.length})
            </h4>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              ${artistWorks.map(w => `
                <div class="group relative rounded-xl overflow-hidden border border-slate-800 bg-slate-950 aspect-[4/3] cursor-pointer hover:border-amber-400 transition-all" onclick="window.openMasterpieceModal('${w.FileName}')">
                  <img src="${resolveImgSrc(w)}" alt="${w.Title}" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" onerror="if (this.src !== '${w.HighResUrl}') { this.src = '${w.HighResUrl}'; }" />
                  <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent flex flex-col justify-end p-2">
                    <p class="text-white text-[11px] font-bold line-clamp-1 group-hover:text-amber-300 transition-colors">${w.Title}</p>
                    <p class="text-slate-400 text-[9px] font-mono">${w.Megapixels.toFixed(1)} MP &bull; ${w.Year}</p>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }

      section.innerHTML = `
        <div class="flex flex-col lg:flex-row gap-6 items-start justify-between">
          <div class="flex-1">
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span class="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold ${epochClass}">
                ${artist.epochName}
              </span>
              <span class="text-xs font-mono text-slate-400 bg-slate-800/60 px-2.5 py-0.5 rounded-full border border-slate-700/50">
                ${artist.lifespan}
              </span>
              <span class="text-xs font-sans text-amber-300/80">
                📍 ${artist.location}
              </span>
            </div>

            <h3 class="font-monumental text-2xl sm:text-3xl font-bold text-white tracking-wide mt-1">
              ${artist.name}
            </h3>
            <p class="font-editorial italic text-base sm:text-lg text-amber-300/90 mt-1 mb-4">
              ${artist.epithet}
            </p>

            <div class="grid md:grid-cols-2 gap-4 my-4">
              <div class="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4">
                <h5 class="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <span>👑</span> Why They Belong
                </h5>
                <p class="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
                  ${artist.whyBelongs}
                </p>
              </div>

              <div class="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4">
                <h5 class="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <span>⚡</span> Role in Evolution of Art
                </h5>
                <p class="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
                  ${artist.evolutionRole}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3 mt-4">
              <button onclick="window.filterByArtistAndScroll('${artist.id}')" class="text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 px-4 py-2 rounded-xl transition-all shadow-md hover:shadow-amber-500/20 flex items-center gap-1.5">
                <span>🏛️</span> View ${artistWorks.length} Masterpieces in Gallery
              </button>
              <span class="text-xs font-mono text-slate-400">
                Total Catalog Ingested: <strong class="text-white">${artist.totalWorksCataloged} works</strong>
              </span>
            </div>
          </div>
        </div>

        ${thumbnailsHtml}
      `;

      timelineContainer.appendChild(section);
    });

    dom.historyTimeline.appendChild(timelineContainer);
  }

  // Render Artist Cards Grid in Artists Section
  function renderArtistsGrid() {
    if (!dom.artistsGrid) return;
    dom.artistsGrid.innerHTML = '';

    const fragment = document.createDocumentFragment();

    data.artists.forEach(artist => {
      const works = data.masterpieces.filter(m => m.ArtistId === artist.id);
      const card = document.createElement('div');
      card.className = 'bg-slate-900/80 border border-slate-800 hover:border-amber-500/50 rounded-2xl p-5 shadow-lg flex flex-col justify-between transition-all duration-300 hover:shadow-xl hover:shadow-amber-500/10';

      card.innerHTML = `
        <div>
          <div class="flex items-center justify-between text-xs font-mono mb-2">
            <span class="badge-${artist.epochId} px-2 py-0.5 rounded-full text-[10px] font-bold uppercase">${artist.epochName.split(' ')[0]}</span>
            <span class="text-slate-400">${artist.lifespan}</span>
          </div>
          <h4 class="font-monumental text-lg font-bold text-white mb-1">${artist.name}</h4>
          <p class="font-editorial text-xs italic text-amber-300/80 mb-3">${artist.epithet}</p>
          <p class="text-xs text-slate-300 line-clamp-3 leading-relaxed mb-4">${artist.whyBelongs}</p>
        </div>

        <div class="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
          <span class="font-mono text-slate-400">
            <strong>${artist.totalWorksCataloged}</strong> Ingested
          </span>
          <button onclick="window.filterByArtistAndScroll('${artist.id}')" class="text-amber-400 hover:text-amber-300 font-bold flex items-center gap-1">
            Explore (${works.length}) &rarr;
          </button>
        </div>
      `;

      fragment.appendChild(card);
    });

    dom.artistsGrid.appendChild(fragment);
  }

  // Lightbox Modal Functions
  function openModal(index) {
    const list = state.filteredMasterpieces;
    if (index < 0 || index >= list.length) return;

    state.modalIndex = index;
    state.zoomScale = 1.0;
    updateModalContent();

    dom.lightboxModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    dom.lightboxModal.classList.add('hidden');
    document.body.style.overflow = '';
    state.modalIndex = -1;
    state.zoomScale = 1.0;
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

  // Global helper to open modal by filename
  window.openMasterpieceModal = function(fileName) {
    const idx = state.filteredMasterpieces.findIndex(m => m.FileName === fileName);
    if (idx !== -1) {
      openModal(idx);
    } else {
      state.activeEpoch = 'all';
      state.activeArtist = 'all';
      state.searchQuery = '';
      applyFilters();
      const newIdx = state.filteredMasterpieces.findIndex(m => m.FileName === fileName);
      if (newIdx !== -1) openModal(newIdx);
    }
  };

  // Global helper to filter by artist and scroll to gallery
  window.filterByArtistAndScroll = function(artistId) {
    state.activeArtist = artistId;
    if (dom.artistFilter) dom.artistFilter.value = artistId;
    applyFilters();
    const gallerySection = document.getElementById('gallery');
    if (gallerySection) {
      gallerySection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Setup Event Listeners
  function initEvents() {
    dom.epochButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        dom.epochButtons.forEach(b => {
          b.classList.remove('bg-amber-500', 'text-slate-950', 'font-bold');
          b.classList.add('bg-slate-800', 'text-slate-300');
        });
        btn.classList.remove('bg-slate-800', 'text-slate-300');
        btn.classList.add('bg-amber-500', 'text-slate-950', 'font-bold');

        state.activeEpoch = btn.dataset.epoch;
        applyFilters();
      });
    });

    if (dom.artistFilter) {
      dom.artistFilter.addEventListener('change', (e) => {
        state.activeArtist = e.target.value;
        applyFilters();
      });
    }

    if (dom.sortSelect) {
      dom.sortSelect.addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        applyFilters();
      });
    }

    if (dom.searchInput) {
      let timeout = null;
      dom.searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          state.searchQuery = e.target.value;
          if (dom.searchClearBtn) {
            dom.searchClearBtn.classList.toggle('hidden', !state.searchQuery);
          }
          applyFilters();
        }, 150);
      });
    }

    if (dom.searchClearBtn) {
      dom.searchClearBtn.addEventListener('click', () => {
        dom.searchInput.value = '';
        state.searchQuery = '';
        dom.searchClearBtn.classList.add('hidden');
        applyFilters();
      });
    }

    if (dom.modalCloseBtn) dom.modalCloseBtn.addEventListener('click', closeModal);
    if (dom.modalPrevBtn) dom.modalPrevBtn.addEventListener('click', () => stepModal(-1));
    if (dom.modalNextBtn) dom.modalNextBtn.addEventListener('click', () => stepModal(1));

    if (dom.zoomInBtn) dom.zoomInBtn.addEventListener('click', () => adjustZoom(0.3));
    if (dom.zoomOutBtn) dom.zoomOutBtn.addEventListener('click', () => adjustZoom(-0.3));
    if (dom.zoomResetBtn) dom.zoomResetBtn.addEventListener('click', resetZoom);

    if (dom.lightboxModal) {
      dom.lightboxModal.addEventListener('click', (e) => {
        if (e.target === dom.lightboxModal) closeModal();
      });
    }

    window.addEventListener('keydown', (e) => {
      if (dom.lightboxModal.classList.contains('hidden')) return;

      if (e.key === 'Escape') closeModal();
      else if (e.key === 'ArrowLeft') stepModal(-1);
      else if (e.key === 'ArrowRight') stepModal(1);
      else if (e.key === '+' || e.key === '=') adjustZoom(0.2);
      else if (e.key === '-') adjustZoom(-0.2);
      else if (e.key === '0') resetZoom();
    });
  }

  function init() {
    initArtistFilter();
    initEvents();
    state.filteredMasterpieces = [...data.masterpieces];
    renderGallery();
    renderHistoryTimeline();
    renderArtistsGrid();
    console.log('Pantheon exhibition initialized successfully.');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
