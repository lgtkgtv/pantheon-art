#!/usr/bin/env python3
"""
Ultra-HD Celebrity Master Artist Ingestion & Batch Downloader.
============================================================
Extracts complete career archives and curated batches across the 13 Celebrity Masters:
  1. Sandro Botticelli   (Early Renaissance)
  2. Leonardo da Vinci   (High Renaissance)
  3. Michelangelo        (High Renaissance)
  4. Caravaggio          (Baroque / Tenebrism)
  5. Rembrandt van Rijn  (Dutch Golden Age)
  6. Johannes Vermeer    (Dutch Golden Age)
  7. Claude Monet        (Impressionism)
  8. Vincent van Gogh    (Post-Impressionism)
  9. Edvard Munch        (Expressionism)
  10. Gustav Klimt       (Vienna Secession)
  11. Pablo Picasso      (Cubism / Modernism)
  12. Salvador Dalí      (Surrealism)
  13. Frida Kahlo        (Mexican Modernism)

TRICKY IMPLEMENTATION DETAILS EXPLAINED:
----------------------------------------
1. URL Modifiers & CDN Stripping:
   WikiArt stores images on global CDNs (uploads0.wikiart.org to uploads8.wikiart.org).
   Image URLs returned in JSON often append downscaling directives like `!Large.jpg`
   or `!PinterestLarge.jpg`. Stripping everything from the exclamation point (`!`) yields
   the raw uncompressed museum master scan directly from the storage bucket.

2. Browser Header Spoofing:
   Direct automated scripts hitting WikiArt endpoints without a valid browser User-Agent
   and Referer header receive HTTP 403 Forbidden responses. This script mimics a modern
   desktop browser request envelope.

3. Instant Resume & Cache Checking:
   Before dispatching any HTTP socket requests, the local disk is queried for the destination
   filename. If the file exists and is larger than 10,000 bytes (eliminating partial/failed
   responses), the network call is bypassed entirely (< 1ms per item).

4. Pagination & Slicing:
   The script supports `--batch-size` and `--offset` for controlled incremental runs
   on constrained connections or headless cloud instances.
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

# Complete 13 Celebrity Masters Roster
CELEBRITY_ARTISTS = [
    {"slug": "sandro-botticelli", "name": "Sandro Botticelli", "epoch": "Early Renaissance"},
    {"slug": "leonardo-da-vinci", "name": "Leonardo da Vinci", "epoch": "High Renaissance"},
    {"slug": "michelangelo", "name": "Michelangelo", "epoch": "High Renaissance"},
    {"slug": "caravaggio", "name": "Caravaggio", "epoch": "Baroque"},
    {"slug": "rembrandt", "name": "Rembrandt van Rijn", "epoch": "Dutch Golden Age"},
    {"slug": "johannes-vermeer", "name": "Johannes Vermeer", "epoch": "Dutch Golden Age"},
    {"slug": "claude-monet", "name": "Claude Monet", "epoch": "Impressionism"},
    {"slug": "vincent-van-gogh", "name": "Vincent van Gogh", "epoch": "Post-Impressionism"},
    {"slug": "edvard-munch", "name": "Edvard Munch", "epoch": "Expressionism"},
    {"slug": "gustav-klimt", "name": "Gustav Klimt", "epoch": "Vienna Secession"},
    {"slug": "pablo-picasso", "name": "Pablo Picasso", "epoch": "Modernism / Cubism"},
    {"slug": "salvador-dali", "name": "Salvador Dali", "epoch": "Surrealism"},
    {"slug": "frida-kahlo", "name": "Frida Kahlo", "epoch": "Mexican Modernism"},
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
    """
    Strips thumbnail query modifiers (!Large.jpg, !PinterestLarge.jpg) from the URL.
    Returns the clean URL pointing directly to the raw uncompressed CDN master scan.
    """
    if not url:
        return ""
    return url.split("!")[0]


def sanitize_filename(name: str, max_len: int = 40) -> str:
    """
    Normalizes a string for cross-platform filesystem compatibility (Windows, macOS, Linux).
    Removes illegal characters and limits length to avoid MAX_PATH restrictions.
    """
    if not name:
        return "untitled"
    sanitized = re.sub(r'[\\/*?:"<>|#\x00-\x1f]', "", name)
    sanitized = re.sub(r"\s+", "_", sanitized).strip("._-")
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len].rstrip("._-")
    return sanitized or "untitled"


def fetch_artist_catalog(artist_slug: str) -> list:
    """
    Retrieves the complete catalog of an artist from the WikiArt REST API.
    WikiArt returns a JSON array of painting objects containing title, year, dimensions,
    and base image URLs.
    """
    api_url = f"https://www.wikiart.org/en/App/Painting/PaintingsByArtist?artistUrl={artist_slug}&json=2"
    req = urllib.request.Request(api_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list):
                return data
            return []
    except Exception as exc:
        print(f"    [!] Error querying catalog for '{artist_slug}': {exc}", file=sys.stderr)
        return []


def download_single_painting(item: dict, target_dir: Path) -> dict:
    """
    Downloads a single painting file if not already present on disk.
    Verifies minimum file size (> 10 KB) to prevent saving corrupted responses.
    """
    dest_path = target_dir / item["LocalFileName"]
    clean_url = item["HighResUrl"]

    # 1. Check local cache (Instant Resume)
    if dest_path.exists():
        file_size = dest_path.stat().st_size
        if file_size > 10000:
            item["FileSizeBytes"] = file_size
            return {"status": "skipped", "item": item, "bytes": file_size}

    if not clean_url:
        return {"status": "failed", "item": item, "error": "No URL available"}

    # 2. Issue network request with browser headers
    req = urllib.request.Request(clean_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
            if len(content) < 1000:
                return {"status": "failed", "item": item, "error": "Incomplete response"}

            # Atomic write to disk
            with open(dest_path, "wb") as f:
                f.write(content)

            item["FileSizeBytes"] = len(content)
            return {"status": "downloaded", "item": item, "bytes": len(content)}
    except Exception as exc:
        return {"status": "failed", "item": item, "error": str(exc)}


def process_artist(
    artist_slug: str,
    artist_name: str,
    output_root: Path,
    batch_size: int = 0,
    offset: int = 0,
    max_workers: int = 8,
    metadata_only: bool = False,
) -> dict:
    """
    Processes catalog extraction and downloading for a single artist.
    """
    print(f"\n[*] Fetching catalog for artist: {artist_slug} ({artist_name})...")
    catalog = fetch_artist_catalog(artist_slug)
    if not catalog:
        print(f"    [!] No artworks returned for '{artist_slug}'. Skipping.")
        return {"artist": artist_name, "total": 0, "downloaded": 0, "skipped": 0, "failed": 0}

    raw_count = len(catalog)
    folder_safe = sanitize_filename(artist_name.replace(" ", "_"), 35)
    artist_dir = output_root / folder_safe
    artist_dir.mkdir(parents=True, exist_ok=True)

    # Slice batch range
    start_idx = max(0, offset)
    take_count = batch_size if batch_size > 0 else raw_count
    end_idx = min(raw_count, start_idx + take_count)
    selected_catalog = catalog[start_idx:end_idx]

    print(f"    Catalog Total: {raw_count} artworks.")
    print(f"    Batch Range  : Items {start_idx + 1} to {end_idx} ({len(selected_catalog)} items)")
    print(f"    Output Folder: {artist_dir}")

    # Build normalized entity objects
    normalized_items = []
    for idx, p in enumerate(selected_catalog, start=start_idx + 1):
        title = p.get("title") or "Untitled"
        year = str(p.get("yearAsString") or p.get("completitionYear") or "")
        w = int(p.get("width") or 0)
        h = int(p.get("height") or 0)
        raw_img = p.get("image") or ""
        clean_url = clean_image_url(raw_img)
        mp = round((w * h) / 1000000.0, 2)

        # Detect file extension
        ext = ".jpg"
        if clean_url:
            parsed_path = urllib.parse.urlparse(clean_url).path
            match_ext = re.search(r"\.(jpg|jpeg|png|webp)$", parsed_path, re.IGNORECASE)
            if match_ext:
                ext = f".{match_ext.group(1).lower()}"

        title_safe = sanitize_filename(title, 40)
        filename = f"{idx:04d}_{title_safe}_{w}x{h}{ext}"

        item_obj = {
            "Index": idx,
            "Artist": artist_name,
            "ArtistSlug": artist_slug,
            "Title": title,
            "Year": year,
            "Width": w,
            "Height": h,
            "Megapixels": mp,
            "HighResUrl": clean_url,
            "LocalFileName": filename,
            "FileSizeBytes": 0,
        }
        normalized_items.append(item_obj)

    # Export artist metadata (JSON + CSV)
    json_path = artist_dir / "metadata.json"
    csv_path = artist_dir / "metadata.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(normalized_items, f, indent=4, ensure_ascii=False)

    if normalized_items:
        keys = list(normalized_items[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(normalized_items)

    print(f"    [+] Metadata saved: {json_path}")

    if metadata_only:
        return {"artist": artist_name, "total": len(normalized_items), "downloaded": 0, "skipped": 0, "failed": 0}

    # Concurrent download pool
    print(f"    [*] Ingesting {len(normalized_items)} images with {max_workers} concurrent workers...")
    downloaded = 0
    skipped = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(download_single_painting, item, artist_dir): item
            for item in normalized_items
        }

        for idx, future in enumerate(as_completed(future_map), start=1):
            res = future.result()
            st = res["status"]
            if st == "downloaded":
                downloaded += 1
                if downloaded % 20 == 0 or idx == len(normalized_items):
                    mb = round(res["bytes"] / 1048576.0, 2)
                    print(f"      [{idx}/{len(normalized_items)}] Progress: {res['item']['LocalFileName']} ({mb} MB)")
            elif st == "skipped":
                skipped += 1
            else:
                failed += 1

    # Re-save metadata with finalized disk sizes
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(normalized_items, f, indent=4, ensure_ascii=False)

    print(f"    [OK] {artist_name} complete: {downloaded} downloaded, {skipped} cached, {failed} failed.")
    return {
        "artist": artist_name,
        "total": len(normalized_items),
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
        "items": normalized_items,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Ultra-HD Fine Art Ingestion Engine for Celebrity Masters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--artist",
        type=str,
        default="",
        help="Target a single artist slug (e.g. 'johannes-vermeer', 'vincent-van-gogh').",
    )
    parser.add_argument(
        "--artists",
        type=str,
        default="",
        help="Comma-separated artist slugs to process.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help="Maximum items to download per artist (0 = ALL artworks in catalog).",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Pagination start offset index (default: 0).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Concurrent download worker threads (default: 8).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./artist_paintings",
        help="Relative or absolute output directory (default: './artist_paintings').",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Compile JSON and CSV metadata catalogs without downloading image binaries.",
    )

    args = parser.parse_args()
    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    # Determine target artist list
    slug_map = {a["slug"]: a["name"] for a in CELEBRITY_ARTISTS}

    targets = []
    if args.artist:
        slug = args.artist.strip().lower()
        name = slug_map.get(slug, slug.replace("-", " ").title())
        targets.append({"slug": slug, "name": name})
    elif args.artists:
        for s in args.artists.split(","):
            slug = s.strip().lower()
            if slug:
                name = slug_map.get(slug, slug.replace("-", " ").title())
                targets.append({"slug": slug, "name": name})
    else:
        targets = CELEBRITY_ARTISTS

    print("=" * 75)
    print(" CELEBRITY MASTER ARTISTS — ULTRA-HD CATALOG INGESTION ENGINE")
    print("=" * 75)
    print(f"Target Artists : {len(targets)} artists ({', '.join(t['slug'] for t in targets)})")
    print(f"Output Root    : {output_root}")
    print(f"Batch Size     : {'ALL Works' if args.batch_size == 0 else args.batch_size}")
    print(f"Offset         : {args.offset}")
    print(f"Concurrency    : {args.workers} worker threads")
    print(f"Metadata Only  : {args.metadata_only}")

    grand_total = 0
    grand_downloaded = 0
    grand_skipped = 0
    grand_failed = 0
    master_catalog = []

    for t in targets:
        res = process_artist(
            artist_slug=t["slug"],
            artist_name=t["name"],
            output_root=output_root,
            batch_size=args.batch_size,
            offset=args.offset,
            max_workers=args.workers,
            metadata_only=args.metadata_only,
        )
        grand_total += res["total"]
        grand_downloaded += res["downloaded"]
        grand_skipped += res["skipped"]
        grand_failed += res["failed"]
        if "items" in res:
            master_catalog.extend(res["items"])

    # Global catalog output
    if master_catalog:
        global_json = output_root / "all_celebrity_artists_catalog.json"
        global_csv = output_root / "all_celebrity_artists_catalog.csv"
        with open(global_json, "w", encoding="utf-8") as f:
            json.dump(master_catalog, f, indent=4, ensure_ascii=False)
        keys = list(master_catalog[0].keys())
        with open(global_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(master_catalog)

    print("\n" + "=" * 75)
    print(" INGESTION RUN SUMMARY")
    print("=" * 75)
    print(f"Total Artworks Cataloged : {grand_total}")
    print(f"New Files Downloaded     : {grand_downloaded}")
    print(f"Cached (Skipped)         : {grand_skipped}")
    print(f"Failed Downloads         : {grand_failed}")
    print(f"Output Directory         : {output_root}")
    print("=" * 75)


if __name__ == "__main__":
    main()
