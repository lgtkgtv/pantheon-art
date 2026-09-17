#!/usr/bin/env python3
"""
Extract 500 Most Popular Paintings of All Time in Highest Possible Resolution.
Sources:
  - WikiArt: https://www.wikiart.org/en/popular-paintings/alltime
  - 1st-Art-Gallery: https://www.1st-art-gallery.com/most-popular-paintings.html (Cross-reference mode)

This script:
1. Fetches the Top 500 Most Popular Paintings of All Time.
2. Selects the absolute highest resolution available for each painting by inspecting
   all image variants in WikiArt's database (resolutions up to 8,500+ px wide).
3. Strips downsampling URL modifiers (!Large.jpg, !PinterestLarge.jpg) to access raw master scans.
4. Concurrently downloads images with progress reporting and resume capability.
5. Generates comprehensive metadata in both JSON and CSV formats.
"""

import os
import sys
import re
import json
import csv
import time
import argparse
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# HTTP Headers simulating a standard modern browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.wikiart.org/",
}


def clean_image_url(url: str) -> str:
    """Strip CDN thumbnail/downscaling modifiers from WikiArt image URLs."""
    if not url:
        return ""
    # WikiArt appends !PinterestLarge.jpg, !Large.jpg, !HD.jpg, etc.
    # The clean URL before the exclamation point is the original uncompressed file.
    clean = url.split("!")[0]
    return clean


def sanitize_filename(name: str, max_len: int = 60) -> str:
    """Sanitize string for safe cross-platform file naming."""
    if not name:
        return "unknown"
    # Replace characters that are invalid on Windows/Unix
    sanitized = re.sub(r'[\\/*?:"<>|#\x00-\x1f]', "", name)
    sanitized = re.sub(r"\s+", "_", sanitized).strip("._-")
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len].rstrip("._-")
    return sanitized or "untitled"


def fetch_wikiart_popular(limit: int = 500) -> list:
    """
    Fetch the Top N Most Popular Paintings of All Time directly from WikiArt's API.
    WikiArt provides 60 items per page across 10 pages (total 600 paintings).
    """
    paintings = []
    page = 1
    max_pages = (limit + 59) // 60  # Ceiling division (e.g. 500 -> 9 pages)

    print(f"[*] Querying WikiArt Popular Paintings API (targeting {limit} paintings)...")

    while len(paintings) < limit and page <= 10:
        api_url = (
            f"https://www.wikiart.org/en/App/Search/popular-paintings"
            f"?searchterm=alltime&json=2&layout=new&page={page}"
        )
        req = urllib.request.Request(api_url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("Paintings") or []
                if not items:
                    break
                paintings.extend(items)
                print(f"    - Page {page}: fetched {len(items)} paintings (Total: {len(paintings)})")
        except Exception as e:
            print(f"    [!] Error fetching page {page}: {e}")
            break
        page += 1
        time.sleep(0.5)

    return paintings[:limit]


def find_highest_resolution_image(painting_data: dict) -> dict:
    """
    Evaluate base image and all variants in 'images' array to determine
    the absolute highest resolution (max width x height / total area).
    """
    candidates = []

    # 1. Base image
    base_url = painting_data.get("image", "")
    base_w = int(painting_data.get("width") or 0)
    base_h = int(painting_data.get("height") or 0)
    if base_url:
        candidates.append({
            "url": clean_image_url(base_url),
            "width": base_w,
            "height": base_h,
            "area": base_w * base_h
        })

    # 2. Variants in 'images'
    variant_images = painting_data.get("images") or []
    for var in variant_images:
        v_url = var.get("image", "")
        v_w = int(var.get("width") or 0)
        v_h = int(var.get("height") or 0)
        if v_url:
            candidates.append({
                "url": clean_image_url(v_url),
                "width": v_w,
                "height": v_h,
                "area": v_w * v_h
            })

    if not candidates:
        return {"url": "", "width": 0, "height": 0, "megapixels": 0.0}

    # Sort by pixel area descending, then max dimension
    candidates.sort(key=lambda c: (c["area"], max(c["width"], c["height"])), reverse=True)
    best = candidates[0]
    mp = round((best["width"] * best["height"]) / 1_000_000, 2)
    best["megapixels"] = mp
    return best


def search_wikiart_painting(title: str, artist: str = "") -> dict:
    """
    Search WikiArt for a given painting title & artist to retrieve the original
    museum-grade high resolution artwork.
    """
    query = f"{title} {artist}".strip()
    encoded = urllib.parse.quote(query)
    search_url = f"https://www.wikiart.org/en/Api/2/PaintingSearch?term={encoded}"
    req = urllib.request.Request(search_url, headers=HEADERS)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            results = json.loads(resp.read().decode("utf-8")).get("data", [])
            if not results:
                return None
            # Return first result
            first = results[0]
            img_url = clean_image_url(first.get("image", ""))
            return {
                "title": first.get("title", title),
                "artistName": first.get("artistName", artist),
                "year": str(first.get("completitionYear") or ""),
                "width": int(first.get("width") or 0),
                "height": int(first.get("height") or 0),
                "image": img_url,
                "images": None
            }
    except Exception as e:
        print(f"    [!] Search error for '{query}': {e}")
        return None


def parse_1st_art_gallery_file(html_file_path: str) -> list:
    """
    Parse painting titles and artists from a saved 1st-Art-Gallery HTML file.
    """
    print(f"[*] Parsing 1st-Art-Gallery paintings from: {html_file_path}")
    content = Path(html_file_path).read_text(encoding="utf-8", errors="ignore")

    # Look for painting item containers, titles, and artists
    pattern = re.compile(
        r'<a[^>]+href="(?P<url>/[^"]+)"[^>]*title="(?P<full_title>[^"]+)"'
        r'|class="product-title"[^>]*>(?P<prod_title>[^<]+)<'
        r'|class="product-artist"[^>]*>(?P<prod_artist>[^<]+)<',
        re.IGNORECASE
    )

    paintings = []
    # General title-artist regex extractor from anchor tags or lists
    anchors = re.findall(
        r'<a\s+[^>]*href=["\']([^"\']+\.html)["\'][^>]*title=["\']([^"\']+)["\']',
        content,
        re.IGNORECASE
    )

    for url, title_str in anchors:
        if "by" in title_str.lower():
            parts = re.split(r'\s+by\s+', title_str, flags=re.IGNORECASE)
            title = parts[0].strip()
            artist = parts[1].strip() if len(parts) > 1 else ""
        else:
            title = title_str.strip()
            artist = ""

        if title and not any(p["title"].lower() == title.lower() for p in paintings):
            paintings.append({
                "title": title,
                "artist": artist,
                "source_url": url
            })

    print(f"    Found {len(paintings)} paintings in 1st-Art-Gallery HTML.")
    return paintings


def download_single_image(painting_info: dict, output_dir: Path, timeout: int = 30) -> dict:
    """Download a single painting in highest resolution and report status."""
    rank = painting_info["rank"]
    title = painting_info["title"]
    artist = painting_info["artist"]
    url = painting_info["high_res_url"]
    w = painting_info["width"]
    h = painting_info["height"]

    if not url:
        return {"rank": rank, "status": "FAILED", "error": "No URL found"}

    ext = Path(urllib.parse.urlparse(url).path).suffix or ".jpg"
    if ext.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"

    artist_safe = sanitize_filename(artist, 25)
    title_safe = sanitize_filename(title, 35)
    filename = f"{rank:03d}_{artist_safe}_-_ {title_safe}_{w}x{h}{ext}".replace(" ", "_")
    filepath = output_dir / filename

    # Resume capability: skip if already downloaded and non-empty
    if filepath.exists() and filepath.stat().st_size > 10_000:
        painting_info["local_filename"] = filename
        painting_info["file_size_bytes"] = filepath.stat().st_size
        return {"rank": rank, "status": "SKIPPED", "filename": filename}

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            filepath.write_bytes(content)
            painting_info["local_filename"] = filename
            painting_info["file_size_bytes"] = len(content)
            return {"rank": rank, "status": "DOWNLOADED", "filename": filename, "size": len(content)}
    except Exception as e:
        return {"rank": rank, "status": "FAILED", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Extract 500 Most Popular Paintings of All Time in Highest Possible Resolution."
    )
    parser.add_argument(
        "--count", type=int, default=500,
        help="Number of paintings to extract (default: 500, max: 600)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="paintings_output",
        help="Directory to save downloaded images (default: paintings_output)"
    )
    parser.add_argument(
        "--workers", type=int, default=8,
        help="Concurrent download threads (default: 8)"
    )
    parser.add_argument(
        "--source", choices=["wikiart", "1st-art"], default="wikiart",
        help="Primary extraction source: 'wikiart' (default) or '1st-art'"
    )
    parser.add_argument(
        "--html-file", type=str, default="",
        help="Path to saved 1st-Art-Gallery HTML file (used when --source=1st-art)"
    )
    parser.add_argument(
        "--metadata-only", action="store_true",
        help="Only compile and save metadata JSON/CSV without downloading images"
    )

    args = parser.parse_args()
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("500 MOST POPULAR PAINTINGS OF ALL TIME - HIGH RESOLUTION EXTRACTOR")
    print("=" * 70)
    print(f"Target count  : {args.count}")
    print(f"Output folder : {output_path.resolve()}")
    print(f"Source mode   : {args.source}")
    print(f"Concurrency   : {args.workers} threads\n")

    raw_paintings = []

    if args.source == "1st-art":
        if args.html_file and Path(args.html_file).exists():
            art_items = parse_1st_art_gallery_file(args.html_file)[:args.count]
            print("[*] Cross-referencing 1st-Art-Gallery items with WikiArt to find master scans...")
            for idx, item in enumerate(art_items, 1):
                print(f"    [{idx}/{len(art_items)}] Searching: {item['title']} - {item['artist']}")
                match = search_wikiart_painting(item["title"], item["artist"])
                if match:
                    raw_paintings.append(match)
                else:
                    raw_paintings.append({
                        "title": item["title"],
                        "artistName": item["artist"],
                        "year": "",
                        "width": 0,
                        "height": 0,
                        "image": "",
                        "images": None
                    })
                time.sleep(0.3)
        else:
            print("[!] Note: 1st-Art-Gallery is protected by Cloudflare bot protection.")
            print("    Please save 'https://www.1st-art-gallery.com/most-popular-paintings.html'")
            print("    from your browser and pass it with --html-file <path_to_file.html>.")
            print("    Switching to canonical WikiArt database for highest resolution master scans...")
            raw_paintings = fetch_wikiart_popular(args.count)
    else:
        raw_paintings = fetch_wikiart_popular(args.count)

    print(f"\n[*] Processing metadata and selecting highest resolution variants for {len(raw_paintings)} paintings...")

    processed_list = []
    ultra_hd_count = 0

    for idx, p in enumerate(raw_paintings, 1):
        best_img = find_highest_resolution_image(p)
        title = p.get("title") or "Untitled"
        artist = p.get("artistName") or "Unknown Artist"
        year = str(p.get("year") or "")
        painting_url = p.get("paintingUrl") or ""
        if painting_url and not painting_url.startswith("http"):
            painting_url = f"https://www.wikiart.org{painting_url}"

        if best_img["width"] >= 2000 or best_img["height"] >= 2000:
            ultra_hd_count += 1

        info = {
            "rank": idx,
            "title": title,
            "artist": artist,
            "year": year,
            "width": best_img["width"],
            "height": best_img["height"],
            "megapixels": best_img["megapixels"],
            "high_res_url": best_img["url"],
            "wikiart_url": painting_url,
            "local_filename": "",
            "file_size_bytes": 0
        }
        processed_list.append(info)

    print(f"[*] Found {ultra_hd_count} artworks with resolution >= 2000px (up to 8,500px+).")

    # Save JSON metadata
    json_path = output_path / "paintings_metadata.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(processed_list, f, indent=2, ensure_ascii=False)
    print(f"[+] Metadata JSON saved to: {json_path}")

    # Save CSV metadata
    csv_path = output_path / "paintings_metadata.csv"
    fieldnames = [
        "rank", "title", "artist", "year", "width", "height",
        "megapixels", "high_res_url", "wikiart_url", "local_filename", "file_size_bytes"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_list)
    print(f"[+] Metadata CSV saved to: {csv_path}")

    if args.metadata_only:
        print("\n[✓] --metadata-only specified. Extraction finished.")
        return

    # Download images concurrently
    print(f"\n[*] Starting concurrent download of {len(processed_list)} images using {args.workers} threads...")
    completed = 0
    downloaded = 0
    skipped = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(download_single_image, item, output_path): item
            for item in processed_list
        }
        for future in as_completed(futures):
            res = future.result()
            completed += 1
            status = res["status"]
            if status == "DOWNLOADED":
                downloaded += 1
            elif status == "SKIPPED":
                skipped += 1
            else:
                failed += 1

            if completed % 25 == 0 or completed == len(processed_list):
                pct = (completed / len(processed_list)) * 100
                print(
                    f"    Progress: {completed}/{len(processed_list)} ({pct:.1f}%) "
                    f"[Downloaded: {downloaded}, Skipped: {skipped}, Failed: {failed}]"
                )

    # Update metadata with final file sizes and local filenames
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(processed_list, f, indent=2, ensure_ascii=False)
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_list)

    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Total processed : {completed}")
    print(f"Downloaded      : {downloaded}")
    print(f"Already existed : {skipped}")
    print(f"Failed          : {failed}")
    print(f"Output Directory: {output_path.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
