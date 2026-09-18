# 🏛️ Pantheon: Open Cultural Heritage & Fine Art Exhibition Engine

A high-performance, cross-platform research toolkit and interactive museum exhibition engine for historic public-domain fine art. Built with **Python 3 / `uv`** for headless Linux, macOS, and WSL 2, alongside native **Windows PowerShell 5.1 / .NET `System.Net.Http`** automation. Pairs structured multi-thousand-work datasets with visual web applications: true-scale physical visualizers, a 3.0× curator's detail loupe, and a 10-milestone chronological guided tour.

---

## 🏛️ Collections & Research Scope

### 1. Career Catalogs of 10 Historic Public Domain Titans (5,105 Artworks)
Archived into: [`artist_paintings/`](file:///c:/agy/art/artist_paintings)  
Each master's directory contains image assets alongside synchronized, standardized `metadata.json` and `metadata.csv` databases (100% verified worldwide public domain):
1. **Sandro Botticelli**: 137 works (Early Italian Renaissance)
2. **Leonardo da Vinci**: 205 works (High Renaissance)
3. **Michelangelo Buonarroti**: 183 works (High Renaissance / Sistine Frescoes)
4. **Caravaggio**: 105 works (Baroque / Tenebrism)
5. **Rembrandt van Rijn**: 767 works (Dutch Golden Age)
6. **Johannes Vermeer**: 44 works (Dutch Golden Age Luminism)
7. **Claude Monet**: 1,367 works (Impressionism)
8. **Vincent van Gogh**: 1,932 works (Post-Impressionism)
9. **Edvard Munch**: 196 works (Expressionism / Symbolism)
10. **Gustav Klimt**: 169 works (Vienna Secession)

### 2. The Crown Jewels Suite (60 Curated Masterpieces)
Curated into: [`artist_paintings/Top_Celebrity_Masterpieces/`](file:///c:/agy/art/artist_paintings/Top_Celebrity_Masterpieces)  
Isolates 60 universally recognized landmarks (*Mona Lisa*, *The Starry Night*, *The Creation of Adam*, *The Night Watch*, *The Art of Painting*, *The Kiss*, *The Scream*, *The Birth of Venus*, *The Last Supper*, *Impression, Sunrise*, *The Milkmaid*) complete with physical dimensions, museum provenance, and resolution metrics.

### 3. Historical Popularity Catalog (Top 100 Paintings)
Archived into: [`paintings_output/`](file:///c:/agy/art/paintings_output)  
Cross-references cultural archives with global public recognition rankings, indexing master captures up to 8,533 px wide.

---

## ⚡ Archival Resolution Engine

To preserve genuine **museum-grade inspection fidelity**:
1. **Full-Resolution Source Selection**: Ingest pipelines parse catalog records across multiple image variants, selecting `max(width * height)` to preserve uncompressed archival master captures.
2. **High-Resolution Masterpieces in Collection**:
   * *The Art of Painting* (Vermeer): **6,209 × 7,377 px** (45.80 Megapixels)
   * *Mona Lisa* (Da Vinci): **5,000 × 7,452 px** (37.26 Megapixels)
   * *The Garden of Earthly Delights* (Bosch): **8,533 × 4,325 px** (36.90 Megapixels)
   * *Las Meninas* (Velázquez): **5,000 × 5,754 px** (28.77 Megapixels)
   * *The Last Judgement* (Michelangelo): **4,579 × 5,764 px** (26.39 Megapixels)
   * *Impression, Sunrise* (Monet): **5,773 × 4,478 px** (25.85 Megapixels)
   * *The Kiss* (Klimt): **5,000 × 5,017 px** (25.08 Megapixels)

---

## 🐧 Linux / WSL 2 / Cross-Platform Quickstart (`uv`)

The pipeline includes a PEP 621 compliant [`pyproject.toml`](file:///c:/agy/art/pyproject.toml) and zero-dependency standard library Python scripts tested on **Ubuntu 24.04 (WSL 2)**, Debian, macOS, and Linux servers.

### 1. Install `uv` (Fastest Python Package & Project Manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 2. Run CLI Commands with `uv`
No manual virtual environment management needed; `uv` manages execution environments automatically:

#### Download Single Artist (Full Catalog or Batched):
```bash
# Ingest all works for Johannes Vermeer
uv run extract_artist.py --artist johannes-vermeer

# Ingest first 50 works for Vincent van Gogh
uv run extract_artist.py --artist vincent-van-gogh --batch-size 50 --offset 0

# Fetch metadata only (no image downloads)
uv run extract_artist.py --artist gustav-klimt --metadata-only

# Ingest all 10 historic masters sequentially with rate throttling
uv run extract_artist.py --all --max-workers 8
```

#### Curate Top Masterpieces:
```bash
# Re-scan library and curate the top 60 crown jewels
uv run curate_masterpieces.py
```

#### Extract Top Popular Paintings:
```bash
# Ingest top 100 popular paintings
uv run extract_paintings.py --count 100 --max-workers 8
```

### 3. Entry-Point CLI Shortcuts
If installed in editable mode via `uv pip install -e .` or `pip install -e .`:
* `pantheon-artist --artist leonardo-da-vinci` (or `art-artist`)
* `pantheon-curate` (or `art-curate`)
* `pantheon-popular --count 100` (or `art-popular`)

---

## 🪟 Windows PowerShell Automation

For Windows environments without Python installed, native PowerShell 5.1+ scripts provide multi-threaded .NET `HttpClient` ingestion:

### 1. Single-Artist Batch Downloader (`batch_extract_artist.ps1`)
```powershell
# Ingest items 1 to 50 for Johannes Vermeer:
powershell -ExecutionPolicy Bypass -File batch_extract_artist.ps1 -Artist "johannes-vermeer" -BatchSize 50 -Offset 0

# Ingest items 101 to 200 for Vincent van Gogh:
powershell -ExecutionPolicy Bypass -File batch_extract_artist.ps1 -Artist "vincent-van-gogh" -BatchSize 100 -Offset 100
```

### 2. Multi-Artist Full Catalog Extractor (`extract_artist_paintings.ps1`)
```powershell
powershell -ExecutionPolicy Bypass -File extract_artist_paintings.ps1 `
    -Artists "johannes-vermeer,caravaggio,gustav-klimt,edvard-munch,sandro-botticelli" `
    -OutputDir "artist_paintings"
```

### 3. Masterpiece Curator (`curate_top_masterpieces.ps1`)
```powershell
powershell -ExecutionPolicy Bypass -File curate_top_masterpieces.ps1
```

### 4. Popular Paintings Extractor (`extract_paintings.ps1`)
```powershell
powershell -ExecutionPolicy Bypass -File extract_paintings.ps1 -Count 100
```

---

## 🌐 Live Web Exhibition (GitHub Pages)

The repository includes a museum-grade interactive web application configured for static hosting on **GitHub Pages**:

* **Live Exhibition URL**: **[`https://lgtkgtv.github.io/pantheon-art/`](https://lgtkgtv.github.io/pantheon-art/)**
* **Local Offline Viewing**: Open `index.html` directly in any modern browser, or run a local web server via `uv run python3 -m http.server 8080`.

### 🎨 Key Exhibition Capabilities
1. **🎧 The 5-Minute Guided Tour (Story Mode)**:
   * 1-tap automated chronological narrative journey through **10 landmark turning points** in art history (1485 &rarr; 1908) across the 10 historic titans from Botticelli to Klimt.
   * Features bite-sized 2-sentence evolutionary story cards, breakthrough badges, segmented progress indicators, and timed auto-play slideshow.
2. **🖼️ "Real-Life Size" on Museum Wall Visualizer**:
   * Solves digital scale distortion by displaying framed artworks on an architectural gallery wall beside an accurate human silhouette (175 cm / 5'9").
   * Visually reveals why intimate portraits like *Mona Lisa* (30 in) contrast dramatically with colossal monumental canvases like *The Night Watch* (14 ft) or *The Last Judgement* (45 ft).
3. **🔬 Interactive Curator's Detail Loupe (3.0× Ultra-HD)**:
   * Circular 180×180px high-magnification lens with museum gold rim.
   * Tracks cursor dynamically on desktop (shortcut `L`) and follows touch contacts with an ergonomic **-65px vertical offset** on mobile so fingers never obstruct the inspection area.
4. **👑 Curated Horizontal Discovery Shelves**:
   * Frictionless visual browsing with smooth desktop left/right chevrons (`‹` and `›`) and mobile touch flicking:
   * Shelves for **The Crown Jewels**, **Ultra-HD Scans (20+ MP)**, **Masters of Shadow & Light**, and **The Plein-Air Revolution**.
5. **📱 Mobile-First Bottom Sheet & Gestures**:
   * On mobile viewports, paintings slide up in an ergonomic bottom sheet with drag handle. Dragging down smoothly tracks touch and dismisses upon passing 80px threshold.
6. **🏛️ 500-Year Timeline with Progressive Disclosure**:
   * Zero text overload: each master features a 1-sentence poetic punchline, technical innovation tags, and an expandable scholar drawer.

---

## 🛡️ Engineering Hygiene & Data Pipeline Design

1. **Client-Side Disk Caching**: Before dispatching network requests, local disk files are verified in `< 1ms` (`file.stat().st_size > 10000`). If a valid file exists, the network request is skipped to conserve bandwidth and prevent redundant server load.
2. **Standard HTTP Client Configuration**: Both Python (`urllib.request`) and PowerShell (`System.Net.Http.HttpClient`) routines send explicit, well-formed request headers with descriptive User-Agent identification and polite thread pools (`max-workers 8`).
3. **Cross-Platform Portability**: Python scripts use standard POSIX-compliant relative pathing (`pathlib.Path`), ensuring identical execution across Linux, WSL 2, and native Windows.
4. **Standardized Metadata Schemas**: Extraction pipelines output both UTF-8 CSV and JSON databases containing titles, creation years, museum collections, pixel dimensions, megapixels, and file sizes.

---

## 📜 Provenance, Legal Context & Ethical Sourcing

> [!NOTE]
> For the complete, master-by-master statutory and case-law analysis, read our formal [**docs/LEGAL_REVIEW.md**](docs/LEGAL_REVIEW.md).

### 1. 100% Verified Worldwide Public Domain Purity
Pantheon’s curated catalog of 60 landmark masterworks and 5,105 artist works adheres to absolute public-domain standards:
* **100% Global Public Domain (60 works / 100%)**: Masterworks created between 1470 and 1918 by artists deceased for more than 70 years (Botticelli, Da Vinci, Michelangelo, Caravaggio, Rembrandt, Vermeer, Monet, Van Gogh, Munch, and Klimt). These works reside irrevocably in the worldwide public domain across all jurisdictions.
* **Proactive Estate Exclusion**: Mid-20th-century artists whose copyrights remain active or litigious (Pablo Picasso, Salvador Dalí, Frida Kahlo) are deliberately excluded from the public exhibition catalog to guarantee a zero-liability, legally impeccable research and educational platform.

### 2. Digital Photographic Reproductions & Legal Doctrine
A cornerstone of digital art preservation is the principle that faithful two-dimensional photographic reproductions of public domain paintings do not create new copyright:
* **United States**: In ***The Bridgeman Art Library, Ltd. v. Corel Corp.*** (36 F. Supp. 2d 191, S.D.N.Y. 1999), affirmed in *Meshwerks v. Toyota* (2008), the court ruled that slavish photographic reproductions of 2D public-domain artworks lack creative originality and are not copyrightable.
* **European Union**: **Article 14 of Directive (EU) 2019/790 (CDSM Directive)** explicitly mandates that upon copyright expiration of a visual art work, reproduction materials are not subject to copyright or related rights unless they constitute an author's own intellectual creation.
* **United Kingdom**: The UK Intellectual Property Office **Copyright Notice 1/2014** confirmed that creating accurate photographs of two-dimensional artworks does not satisfy the originality requirement.

### 3. Architecture, Decoupling & The Server Test
Pantheon maintains a strict asset decoupling architecture:
* **Zero Bulk Media in Git**: The repository contains code and metadata only; multi-gigabyte scans are excluded via `.gitignore`.
* **The Server Test (*Perfect 10 v. Amazon*)**: Images are resolved on the client side from decentralized cultural CDNs, avoiding direct reproduction or distribution of copyrighted files on the hosting server.

### 4. Open Access API Roadmap & Curator Inquiries
Pantheon is actively expanding ingestion to institutional **CC0 / Open Access APIs** (Metropolitan Museum of Art, National Gallery of Art, Rijksmuseum, and Wikimedia Commons). For inquiries, attribution updates, or suggestions, please contact **`lgtkgtv@gmail.com`** or open an issue on GitHub. All inquiries receive prompt attention within 24 hours.

---

## 📁 Repository Layout

```text
.
├── index.html                             # Museum-grade exhibition web app (GitHub Pages entry)
├── .nojekyll                              # Bypasses Jekyll for GitHub Pages
├── 404.html                               # Fallback redirect for GitHub Pages
├── assets/                                # Self-hosted UI and social preview assets
│   └── og-preview.jpg                     # Optimized OpenGraph / Twitter social card (1200×754 px)
├── css/
│   └── style.css                          # Museum aesthetics, typography & responsive styling
├── js/
│   ├── catalog-data.js                    # Curated data bundle (60 Masterpieces + 10 Historic Titans)
│   └── app.js                             # Interactive exhibition, search, filters & zoom modal
├── data/
│   └── pantheon_catalog.json              # Canonical JSON dataset for API / web consumption
├── docs/
│   ├── LEGAL_REVIEW.md                    # Comprehensive legal, copyright & attribution audit
│   └── SOFTWARE_SPEC.md                   # Comprehensive system specification & architecture report
│
├── pyproject.toml                         # PEP 621 project configuration for uv / pip
├── README.md                              # Comprehensive technical documentation
├── .gitignore                             # Git ignore rules (excludes multi-GB image files)
│
├── extract_artist.py                      # Cross-platform CLI for artist catalog ingestion
├── curate_masterpieces.py                 # Cross-platform CLI to curate top masterpieces
├── extract_paintings.py                   # Cross-platform CLI for top popular paintings
├── build_catalog_data.py                  # Utility script compiling catalog metadata
│
├── batch_extract_artist.ps1               # Windows PowerShell single-artist batch downloader
├── extract_artist_paintings.ps1           # Windows PowerShell multi-artist extractor
├── curate_top_masterpieces.ps1            # Windows PowerShell crown jewel curator
├── extract_paintings.ps1                  # Windows PowerShell popular paintings extractor
│
├── artist_paintings/                      # 10 Historic Artist directories (5,105 works + metadata)
│   ├── Leonardo_da_Vinci/
│   ├── Vincent_van_Gogh/
│   ├── ...
│   └── Top_Celebrity_Masterpieces/        # 60 Curated Crown Jewels + JSON/CSV
│
└── paintings_output/                      # Top 100 Popular Paintings + JSON/CSV
```
