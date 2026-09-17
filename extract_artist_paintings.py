#!/usr/bin/env python3
"""
Extract All Original High-Resolution Paintings by Claude Monet, Vincent van Gogh,
and the Top 5 Historic Celebrity Masters:
- Claude Monet (Impressionism pioneer)
- Vincent van Gogh (Post-Impressionism icon)
- Leonardo da Vinci (High Renaissance master)
- Michelangelo (High Renaissance master)
- Pablo Picasso (Modern/Cubism giant)
- Rembrandt van Rijn (Dutch Golden Age master)
- Salvador Dalí (Surrealism legend)
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

CELEBRITY_ARTISTS = [
    {"slug": "claude-monet", "name": "Claude Monet"},
    {"slug": "vincent-van-gogh", "name": "Vincent van Gogh"},
    {"slug": "leonardo-da-vinci", "name": "Leonardo da Vinci"},
    {"slug": "michelangelo", "name": "Michelangelo"},
    {"slug": "pablo-picasso", "name": "Pablo Picasso"},
    {"slug": "rembrandt", "name": "Rembrandt"},
    {"slug": "salvador-dali", "name": "Salvador Dali"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Referer": "https://www.wikiart.org/",
}


def clean_image_url(url: str) -> str:
    """Strip CDN thumbnail/downscale modifiers to retrieve original master scans."""
    if not url:
        return ""
    return url.split("!")[0]


def sanitize_filename(name: str, max_len: int = 45) -> str:
    """Sanitize string for clean filenames."""
    if not name:
        return "untitled"
    sanitized = re.sub(r'[\\/*?:"<>|#\x00-\x1f]', "", name)
    sanitized = re.sub(r"\s+", "_", sanitized).strip("._-")
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len].rstrip("._-")
    return sanitized or "untitled"


def fetch_artist_catalog(artist_slug: str) -> list:
    """Fetch complete catalog of all paintings by the artist from WikiArt."""
    api_url = f"https://www.wikiart.org/en/App/Painting/PaintingsByArtist?artistUrl={artist_slug}&json=2"
    req = urllib.request.Request(api_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data or []
    except Exception as e:
        print(f"    [!] Error fetching catalog for {artist_slug}: {e}")
        return []


def download_image(item: dict, dest_dir: Path, timeout: int = 45) -> dict:
    """Download a single high-resolution image with resume capability."""
    url = item["high_res_url"]
    filename = item["filename"]
    filepath = dest_dir / filename

    if filepath.exists() and filepath.stat().st_size > 10_000:
        item["file_size_bytes"] = filepath.stat().st_size
        return {"status": "SKIPPED", "filename": filename, "size": filepath.stat().st_size}

    if not url:
        return {"status": "FAILED", "filename": filename, "error": "No URL"}

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            filepath.write_bytes(content)
            item["file_size_bytes"] = len(content)
            return {"status": "DOWNLOADED", "filename": filename, "size": len(content)}
    except Exception as e:
        return {"status": "FAILED", "filename": filename, "error": str(e)}


def process_artist(artist_info: dict, root_output: Path, max_per_artist: int, workers: int, metadata_only: bool) -> dict:
    slug = artist_info["slug"]
    name = artist_info["name"]

    print("\n" + "-" * 70)
    print(f"[*] Querying catalog for: {name} ({slug})...")
    raw_items = fetch_artist_catalog(slug)
    total_found = len(raw_items)

    if not raw_items:
        print(f"    [!] No artworks found for {slug}.")
        return {"artist": name, "total": 0, "downloaded": 0, "skipped": 0, "failed": 0}

    folder_name = sanitize_filename(name, 35)
    artist_dir = root_output / folder_name
    artist_dir.mkdir(parents=True, exist_ok=True)

    items_to_process = raw_items if max_per_artist <= 0 else raw_items[:max_per_artist]
    print(f"    Catalog contains {total_found} works. Processing {len(items_to_process)} items...")

    catalog = []
    for idx, p in enumerate(items_to_process, 1):
        title = p.get("title") or "Untitled"
        year = str(p.get("yearAsString") or p.get("completitionYear") or "")
        w = int(p.get("width") or 0)
        h = int(p.get("height") or 0)
        raw_img = p.get("image") or ""
        clean_url = clean_image_url(raw_img)
        mp = round((w * h) / 1_000_000, 2)

        ext = Path(urllib.parse.urlparse(clean_url).path).suffix or ".jpg"
        if ext.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"

        safe_title = sanitize_filename(title, 40)
        filename = f"{idx:04d}_{safe_title}_{w}x{h}{ext}"

        item_obj = {
            "index": idx,
            "artist": name,
            "artist_slug": slug,
            "title": title,
            "year": year,
            "width": w,
            "height": h,
            "megapixels": mp,
            "high_res_url": clean_url,
            "filename": filename,
            "file_size_bytes": 0
        }
        catalog.append(item_obj)

    # Export artist metadata JSON & CSV
    json_path = artist_dir / "metadata.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    csv_path = artist_dir / "metadata.csv"
    fieldnames = ["index", "artist", "artist_slug", "title", "year", "width", "height", "megapixels", "high_res_url", "filename", "file_size_bytes"]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(catalog)

    print(f"    Metadata saved to: {json_path}")

    if metadata_only:
        return {"artist": name, "total": len(catalog), "downloaded": 0, "skipped": 0, "failed": 0, "items": catalog}

    print(f"    Downloading {len(catalog)} high-resolution images into: {artist_dir}...")
    downloaded = 0
    skipped = 0
    failed = 0
    completed = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(download_image, item, artist_dir): item for item in catalog}
        for future in as_completed(futures):
            res = future.result()
            completed += 1
            if res["status"] == "DOWNLOADED":
                downloaded += 1
            elif res["status"] == "SKIPPED":
                skipped += 1
            else:
                failed += 1

            if completed % 25 == 0 or completed == len(catalog):
                pct = (completed / len(catalog)) * 100
                print(f"    Progress: {completed}/{len(catalog)} ({pct:.1f}%) [Downloaded: {downloaded}, Skipped: {skipped}, Failed: {failed}]")

    # Update metadata with downloaded file sizes
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(catalog)

    print(f"    [OK] Finished {name}: {downloaded} downloaded, {skipped} skipped, {failed} failed.")
    return {"artist": name, "total": len(catalog), "downloaded": downloaded, "skipped": skipped, "failed": failed, "items": catalog}


def main():
    parser = argparse.ArgumentParser(description="Extract all paintings by Monet, Van Gogh, and celebrity masters.")
    parser.add_argument("--output-dir", type=str, default="artist_paintings", help="Output root folder")
    parser.add_argument("--max-per-artist", type=int, default=0, help="Max paintings per artist (0 = ALL)")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent download workers")
    parser.add_argument("--metadata-only", action="store_true", help="Compile metadata catalogs without downloading images")
    args = parser.parse_args()

    root_output = Path(args.output_dir)
    root_output.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("CELEBRITY MASTER ARTISTS - HIGH RESOLUTION CATALOG EXTRACTOR")
    print("=" * 70)
    print(f"Artists ({len(CELEBRITY_ARTISTS)}): {', '.join(a['name'] for a in CELEBRITY_ARTISTS)}")
    print(f"Output Root : {root_output.resolve()}")
    print(f"Per-Artist  : {'ALL' if args.max_per_artist <= 0 else args.max_per_artist}")
    print(f"Workers     : {args.workers}")
    print(f"MetadataOnly: {args.metadata_only}\n")

    master_catalog = []
    stats = []

    for a in CELEBRITY_ARTISTS:
        res = process_artist(a, root_output, args.max_per_artist, args.workers, args.metadata_only)
        stats.append(res)
        if "items" in res:
            master_catalog.extend(res["items"])

    # Export master catalog
    master_json = root_output / "all_celebrity_artists_catalog.json"
    with open(master_json, "w", encoding="utf-8") as f:
        json.dump(master_catalog, f, indent=2, ensure_ascii=False)

    master_csv = root_output / "all_celebrity_artists_catalog.csv"
    if master_catalog:
        fieldnames = list(master_catalog[0].keys())
        with open(master_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(master_catalog)

    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)
    total_art = sum(s["total"] for s in stats)
    total_dl = sum(s["downloaded"] for s in stats)
    total_sk = sum(s["skipped"] for s in stats)
    total_fl = sum(s["failed"] for s in stats)

    for s in stats:
        print(f"  {s['artist']:<25}: {s['total']:>5} works (Downloaded: {s['downloaded']:>4}, Skipped: {s['skipped']:>4}, Failed: {s['failed']:>2})")
    print("-" * 70)
    print(f"  TOTAL ARTWORKS IDENTIFIED: {total_art}")
    print(f"  TOTAL DOWNLOADED         : {total_dl}")
    print(f"  TOTAL SKIPPED (EXISTING) : {total_sk}")
    print(f"  TOTAL FAILED             : {total_fl}")
    print(f"  Master Catalog JSON      : {master_json}")
    print(f"  Master Catalog CSV       : {master_csv}")
    print("=" * 70)


if __name__ == "__main__":
    main()
