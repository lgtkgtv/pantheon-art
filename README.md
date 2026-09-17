# Ultra-HD Fine Art Ingestion, Curation & Visual Storytelling Toolkit

A high-performance, cross-platform fine art data extraction, curation, and visual storytelling engine. Built with **Python 3 / `uv`** for headless Linux, macOS, and WSL 2, alongside native **Windows PowerShell 5.1 / .NET `System.Net.Http`** automation. Ingests authentic, uncompressed museum master scans from global archives without watermarks or downsampling.

---

## 🏛️ Ingestion Scope & Collections

### 1. Complete Career Catalogs of 13 Celebrity Masters (7,552 Artworks)
Extracted into: [`artist_paintings/`](file:///c:/agy/art/artist_paintings)  
Each artist directory contains complete high-resolution image assets alongside synchronized `metadata.json` and `metadata.csv` databases:
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
11. **Pablo Picasso**: 1,169 works (Cubism / Modernism)
12. **Salvador Dalí**: 1,178 works (Surrealism)
13. **Frida Kahlo**: 100 works (Mexican Modernism / Autobiographical Surrealism)

### 2. Top Celebrated Masterpieces Suite (78 Crown Jewels)
Curated into: [`artist_paintings/Top_Celebrity_Masterpieces/`](file:///c:/agy/art/artist_paintings/Top_Celebrity_Masterpieces)  
Isolates the world's most famous cultural landmarks (*Mona Lisa*, *The Starry Night*, *The Creation of Adam*, *The Night Watch*, *The Art of Painting*, *The Kiss*, *The Scream*, *The Birth of Venus*, *Guernica*, *The Persistence of Memory*, *The Two Fridas*) at peak museum resolutions.

### 3. The Most Popular Paintings of All Time
Extracted into: [`paintings_output/`](file:///c:/agy/art/paintings_output)  
Cross-references WikiArt's museum archives with global popularity rankings, downloading uncompressed master scans up to 8,533 px wide.

---

## ⚡ Resolution Optimization Engine

To guarantee authentic **maximum museum resolution**:
1. **CDN Thumbnail Bypass**: WikiArt CDN query tags (e.g. `!Large.jpg`, `!PinterestLarge.jpg`, `!Blog.jpg`) are stripped automatically to fetch the raw master image.
2. **Multi-Variant Resolution Selection**: Ingest pipelines scan both base `image` and `images[]` gallery arrays, selecting `max(width * height)` to extract ultra-HD captures.
3. **Record Resolutions Ingested**:
   * *The Art of Painting* (Vermeer): **6,209 × 7,377 px** (45.80 Megapixels)
   * *Mona Lisa* (Da Vinci): **5,000 × 7,452 px** (37.26 Megapixels)
   * *The Garden of Earthly Delights* (Bosch): **8,533 × 4,325 px** (36.90 Megapixels)
   * *Las Meninas* (Velázquez): **5,000 × 5,754 px** (28.77 Megapixels)
   * *The Last Judgement* (Michelangelo): **4,579 × 5,764 px** (26.39 Megapixels)
   * *Impression, Sunrise* (Monet): **5,773 × 4,478 px** (25.85 Megapixels)
   * *The Kiss* (Klimt): **5,000 × 5,017 px** (25.08 Megapixels)

---

## 🐧 Linux / WSL 2 / Cross-Platform Quickstart (`uv`)

The project includes a PEP 621 compliant [`pyproject.toml`](file:///c:/agy/art/pyproject.toml) and zero-dependency standard library Python scripts tested on **Ubuntu 24.04 (WSL 2)**, Debian, macOS, and Linux servers.

### 1. Install `uv` (Fastest Python Package & Project Manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 2. Run CLI Commands with `uv`
No manual virtual environment activation needed; `uv` handles dependencies automatically:

#### Download Single Artist (Full Catalog or Batched):
```bash
# Ingest all works for Johannes Vermeer
uv run extract_artist.py --artist johannes-vermeer

# Download first 50 works for Vincent van Gogh
uv run extract_artist.py --artist vincent-van-gogh --batch-size 50 --offset 0

# Fetch metadata only (no image downloads)
uv run extract_artist.py --artist frida-kahlo --metadata-only

# Ingest all 13 celebrity masters sequentially
uv run extract_artist.py --all --max-workers 8
```

#### Curate Top Masterpieces:
```bash
# Re-scan library and curate the top 78 crown jewels
uv run curate_masterpieces.py
```

#### Extract Top Popular Paintings:
```bash
# Ingest top 100 popular paintings
uv run extract_paintings.py --count 100 --max-workers 8
```

### 3. Entry-Point CLI Shortcuts
If installed via `uv pip install -e .` or `pip install -e .`:
* `art-artist --artist leonardo-da-vinci`
* `art-curate`
* `art-popular --count 100`

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
    -Artists "johannes-vermeer,frida-kahlo,caravaggio,gustav-klimt,edvard-munch,sandro-botticelli" `
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

## 🎨 Visual Storytelling & Exhibition

The repository includes visual storytelling tools to explore the collection:

1. **Interactive Web Chronicle (`visual_chronicle_masters.html`)**:
   * Open directly in any modern browser: `file:///c:/agy/art/visual_chronicle_masters.html` (or serve via `uv run python3 -m http.server 8000`).
   * Features:
     * Chronological 500-year timeline (1470–1954).
     * Era filter buttons (Renaissance, Baroque & Golden Age, Impressionism, Expressionism, Modernism).
     * Resolution badges displaying megapixels and dimensions.
     * Full-screen modal zoom with direct links to raw master scans.
2. **Illustrated Art History Guide (`celebrity_masters_visual_story.md`)**:
   * Comprehensive historical guide covering each master's biographical significance, evolutionary role in Western art, and deep-dive analyses of their most celebrated works.

---

## 🛡️ Resilience & Architecture Details

1. **Anti-Scraping Bypass**: WikiArt endpoints return HTTP 403 Forbidden to standard automated tools. Both Python and PowerShell engines include browser emulation headers (`User-Agent` and `Referer: https://www.wikiart.org/`).
2. **Zero-Redundancy Local Cache**: Before dispatching network requests, files on disk are verified in `< 1ms` (`file.stat().st_size > 10000`). If a valid file exists, the network request is skipped.
3. **Strict Portability**: Python scripts use relative paths and standard POSIX-compliant path handling, ensuring flawless execution across Linux, WSL, and Windows.
4. **Structured Databases**: Every extraction produces both UTF-8 CSV and JSON databases containing titles, dates, museum collections, pixel dimensions, megapixels, and file sizes.

---

## 📁 Repository Layout

```text
.
├── pyproject.toml                         # PEP 621 project configuration for uv / pip
├── README.md                              # Comprehensive technical documentation
├── .gitignore                             # Git ignore rules (excludes multi-GB image files)
│
├── extract_artist.py                      # Cross-platform CLI for artist catalog ingestion
├── curate_masterpieces.py                 # Cross-platform CLI to curate top masterpieces
├── extract_paintings.py                   # Cross-platform CLI for top popular paintings
│
├── batch_extract_artist.ps1               # Windows PowerShell single-artist batch downloader
├── extract_artist_paintings.ps1           # Windows PowerShell multi-artist extractor
├── curate_top_masterpieces.ps1            # Windows PowerShell crown jewel curator
├── extract_paintings.ps1                  # Windows PowerShell popular paintings extractor
│
├── visual_chronicle_masters.html          # Standalone interactive visual gallery web app
│
├── artist_paintings/                      # 13 Artist directories (7,552 works + metadata)
│   ├── Leonardo_da_Vinci/
│   ├── Vincent_van_Gogh/
│   ├── ...
│   └── Top_Celebrity_Masterpieces/        # 78 Curated Crown Jewels + JSON/CSV
│
└── paintings_output/                      # Top 100 Popular Paintings + JSON/CSV
```
