# Ultra-HD Fine Art Ingestion & Curation Toolkit

A high-performance fine art data extraction and curation engine built for Windows PowerShell 5.1 / .NET `System.Net.Http` and Python. Ingests authentic, uncompressed museum master scans from global archives without watermarks or downsampling.

---

## 🏛️ Ingestion Scope & Collections

### 1. The 500 Most Popular Paintings of All Time
* Extracted into: [`paintings_output/`](file:///c:/agy/art/paintings_output)
* Includes the top historical rankings, cross-referencing WikiArt's museum archives with 1st-Art-Gallery.

### 2. Complete Career Catalogs of 13 Celebrity Masters (7,552 Artworks)
* Extracted into: [`artist_paintings/`](file:///c:/agy/art/artist_paintings)
* Individual subdirectories with dedicated `metadata.json` and `metadata.csv` files:
  1. **Leonardo da Vinci**: 205 works (High Renaissance)
  2. **Michelangelo**: 183 works (High Renaissance)
  3. **Sandro Botticelli**: 137 works (Early Renaissance)
  4. **Caravaggio**: 105 works (Baroque / Tenebrism)
  5. **Rembrandt van Rijn**: 767 works (Dutch Golden Age)
  6. **Johannes Vermeer**: 44 works (Dutch Golden Age)
  7. **Claude Monet**: 1,367 works (Impressionism)
  8. **Vincent van Gogh**: 1,932 works (Post-Impressionism)
  9. **Edvard Munch**: 196 works (Expressionism)
  10. **Gustav Klimt**: 169 works (Vienna Secession)
  11. **Pablo Picasso**: 1,169 works (Cubism / Modernism)
  12. **Salvador Dalí**: 1,178 works (Surrealism)
  13. **Frida Kahlo**: 100 works (Mexican Modernism)

### 3. Option C: Top Celebrated Masterpieces Suite (79 Crown Jewels)
* Curated into: [`artist_paintings/Top_Celebrity_Masterpieces/`](file:///c:/agy/art/artist_paintings/Top_Celebrity_Masterpieces)
* Isolates the world's most famous paintings (*Mona Lisa*, *The Starry Night*, *The Creation of Adam*, *The Night Watch*, *The Art of Painting*, *The Kiss*, *The Scream*, *The Birth of Venus*, *Guernica*, *The Persistence of Memory*, *The Two Fridas*) at maximum available resolution.

---

## ⚡ Resolution Optimization Engine

To guarantee authentic **maximum museum resolution**:
1. **CDN Thumbnail Bypass**: WikiArt CDN query tags (e.g. `!Large.jpg`, `!PinterestLarge.jpg`) are stripped automatically to fetch the raw master image.
2. **Multi-Variant Resolution Resolution**: For popular rankings, the script selects `max(width * height)` between base `image` and `images[]` gallery arrays.
3. **Record Resolutions Ingested**:
   * *The Art of Painting* (Vermeer): **6,209 × 7,377 px** (45.80 Megapixels)
   * *Mona Lisa* (Da Vinci): **5,000 × 7,452 px** (37.26 Megapixels)
   * *The Garden of Earthly Delights* (Bosch): **8,533 × 4,325 px** (36.90 Megapixels)
   * *Las Meninas* (Velázquez): **5,000 × 5,754 px** (28.77 Megapixels)
   * *The Last Judgement* (Michelangelo): **4,579 × 5,764 px** (26.39 Megapixels)
   * *Impression, Sunrise* (Monet): **5,773 × 4,478 px** (25.85 Megapixels)
   * *The Kiss* (Klimt): **5,000 × 5,017 px** (25.08 Megapixels)

---

## 🚀 Available Scripts & Usage

### 1. Modular Single-Artist Batch Downloader (`batch_extract_artist.ps1`)
Download an artist in custom batches with offsets:
```powershell
# Download items 1 to 50 for Johannes Vermeer:
powershell -ExecutionPolicy Bypass -File batch_extract_artist.ps1 -Artist "johannes-vermeer" -BatchSize 50 -Offset 0

# Download items 101 to 200 for Vincent van Gogh:
powershell -ExecutionPolicy Bypass -File batch_extract_artist.ps1 -Artist "vincent-van-gogh" -BatchSize 100 -Offset 100
```

### 2. Multi-Artist Full Catalog Extractor (`extract_artist_paintings.ps1`)
Ingest complete artist catalogs automatically:
```powershell
powershell -ExecutionPolicy Bypass -File extract_artist_paintings.ps1 `
    -Artists "johannes-vermeer,frida-kahlo,caravaggio,gustav-klimt,edvard-munch,sandro-botticelli" `
    -OutputDir "artist_paintings"
```

### 3. Top Masterpiece Curator (`curate_top_masterpieces.ps1`)
Re-scan the library and curate the top crown jewels across all 13 masters:
```powershell
powershell -ExecutionPolicy Bypass -File curate_top_masterpieces.ps1
```

### 4. Top 500 Popular Paintings Extractor (`extract_paintings.ps1`)
```powershell
powershell -ExecutionPolicy Bypass -File extract_paintings.ps1 -Count 500
```

---

## 🛡️ Resilience & Caching
* **Instant Resume**: Before issuing network calls, files on disk are verified in `< 1ms`. If a valid file exists, the network call is skipped.
* **Header & Timeout Handling**: Built with .NET `HttpClient` with persistent keep-alive and auto-redirect handling.
* **Encoding & Schema**: Metadata is output in UTF-8 JSON and CSV for spreadsheet and database ingestion.
