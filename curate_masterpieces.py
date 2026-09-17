#!/usr/bin/env python3
"""
Ultra-HD Celebrity Masterpieces Curator Engine.
==============================================
Identifies, validates, and curates the undisputed crown jewels across the 13 Celebrity Masters:
  - Sandro Botticelli   (Birth of Venus, Primavera, Mystical Nativity)
  - Leonardo da Vinci   (Mona Lisa, Last Supper, Lady with an Ermine, Vitruvian Man)
  - Michelangelo        (Creation of Adam, Last Judgement, Libyan Sibyl)
  - Caravaggio          (Calling of St. Matthew, Judith, Bacchus, David)
  - Rembrandt van Rijn  (Night Watch, Anatomy Lesson, Self-Portraits)
  - Johannes Vermeer    (Girl with a Pearl Earring, Art of Painting, Milkmaid)
  - Claude Monet        (Impression Sunrise, Water Lilies, Japanese Bridge)
  - Vincent van Gogh    (Starry Night, Sunflowers, Potato Eaters)
  - Edvard Munch        (The Scream, Madonna, Dance of Life, Sick Child)
  - Gustav Klimt        (The Kiss, Adele Bloch-Bauer, Judith, Emilie Flöge)
  - Pablo Picasso       (Guernica, Old Blind Guitarist, Dora Maar, Self-Portrait)
  - Salvador Dalí       (Persistence of Memory, Great Masturbator, Swans Reflecting Elephants)
  - Frida Kahlo         (The Two Fridas, Broken Column, Viva la Vida, Henry Ford Hospital)

Cross-references both artist directories and popular paintings archives to select the
highest resolution scan available (up to 45.80 Megapixels).
"""

import os
import sys
import re
import json
import csv
import shutil
import argparse
from pathlib import Path

# Masterpiece definitions with glob search patterns and historical metadata
MASTERPIECE_SIGNATURES = [
    # 1. Sandro Botticelli
    {"artist": "Sandro Botticelli", "slug": "Sandro_Botticelli", "title": "The Birth of Venus", "patterns": ["*Birth_of_Venus*", "*The_Birth_of_Venus*"], "year": "1485–1486", "museum": "Uffizi Gallery, Florence"},
    {"artist": "Sandro Botticelli", "slug": "Sandro_Botticelli", "title": "The Spring (Primavera)", "patterns": ["*The_Spring*", "*Primavera*"], "year": "1477–1482", "museum": "Uffizi Gallery, Florence"},
    {"artist": "Sandro Botticelli", "slug": "Sandro_Botticelli", "title": "The Mystical Nativity", "patterns": ["*The_Mystical_Nativity*"], "year": "1500", "museum": "National Gallery, London"},
    {"artist": "Sandro Botticelli", "slug": "Sandro_Botticelli", "title": "The Story of Nastagio Degli Onesti", "patterns": ["*Story_of_Nastagio_Degli_Onesti*"], "year": "1483", "museum": "Museo del Prado, Madrid"},
    {"artist": "Sandro Botticelli", "slug": "Sandro_Botticelli", "title": "Calumny of Apelles", "patterns": ["*Calumny_of_Apelles*"], "year": "1494–1495", "museum": "Uffizi Gallery, Florence"},

    # 2. Leonardo da Vinci
    {"artist": "Leonardo da Vinci", "slug": "Leonardo_da_Vinci", "title": "Mona Lisa", "patterns": ["*Mona_Lisa*"], "year": "1503–1519", "museum": "Musée du Louvre, Paris"},
    {"artist": "Leonardo da Vinci", "slug": "Leonardo_da_Vinci", "title": "The Last Supper", "patterns": ["*The_Last_Supper*"], "year": "1495–1498", "museum": "Santa Maria delle Grazie, Milan"},
    {"artist": "Leonardo da Vinci", "slug": "Leonardo_da_Vinci", "title": "Lady with an Ermine", "patterns": ["*Lady_with_an_Ermine*"], "year": "1489–1490", "museum": "Czartoryski Museum, Kraków"},
    {"artist": "Leonardo da Vinci", "slug": "Leonardo_da_Vinci", "title": "Vitruvian Man", "patterns": ["*proportions_of_the_human_figure*", "*Vitruvian*"], "year": "1490", "museum": "Gallerie dell'Accademia, Venice"},
    {"artist": "Leonardo da Vinci", "slug": "Leonardo_da_Vinci", "title": "Portrait of Ginevra de' Benci", "patterns": ["*Ginevra*"], "year": "1474–1478", "museum": "National Gallery of Art, Washington D.C."},
    {"artist": "Leonardo da Vinci", "slug": "Leonardo_da_Vinci", "title": "Annunciation", "patterns": ["*Annunciation*"], "year": "1472–1475", "museum": "Uffizi Gallery, Florence"},
    {"artist": "Leonardo da Vinci", "slug": "Leonardo_da_Vinci", "title": "The Virgin and Child with St. Anne", "patterns": ["*Virgin_and_Child_with_St._Anne*"], "year": "1503–1519", "museum": "Musée du Louvre, Paris"},
    {"artist": "Leonardo da Vinci", "slug": "Leonardo_da_Vinci", "title": "St. John the Baptist", "patterns": ["*John_the_Baptist*"], "year": "1513–1516", "museum": "Musée du Louvre, Paris"},

    # 3. Michelangelo
    {"artist": "Michelangelo", "slug": "Michelangelo", "title": "The Creation of Adam", "patterns": ["*Creation_of_Adam*"], "year": "1512", "museum": "Sistine Chapel, Vatican Museums"},
    {"artist": "Michelangelo", "slug": "Michelangelo", "title": "The Last Judgement", "patterns": ["*The_Last_Judgement*"], "year": "1536–1541", "museum": "Sistine Chapel, Vatican Museums"},
    {"artist": "Michelangelo", "slug": "Michelangelo", "title": "Sistine Chapel: The Flood", "patterns": ["*The_Flood*"], "year": "1508–1512", "museum": "Sistine Chapel, Vatican Museums"},
    {"artist": "Michelangelo", "slug": "Michelangelo", "title": "Sistine Chapel: Libyan Sibyl", "patterns": ["*Libyan_Sibyl*"], "year": "1511", "museum": "Sistine Chapel, Vatican Museums"},
    {"artist": "Michelangelo", "slug": "Michelangelo", "title": "Sistine Chapel: Cumaean Sibyl", "patterns": ["*Cumaean_Sibyl*"], "year": "1510", "museum": "Sistine Chapel, Vatican Museums"},
    {"artist": "Michelangelo", "slug": "Michelangelo", "title": "Sistine Chapel: David and Goliath", "patterns": ["*David_and_Goliath*"], "year": "1509", "museum": "Sistine Chapel, Vatican Museums"},
    {"artist": "Michelangelo", "slug": "Michelangelo", "title": "The Entombment", "patterns": ["*The_Entombment*"], "year": "1500–1501", "museum": "National Gallery, London"},
    {"artist": "Michelangelo", "slug": "Michelangelo", "title": "Pieta (Studies)", "patterns": ["*Pieta*"], "year": "1498–1540", "museum": "St. Peter's Basilica, Vatican"},

    # 4. Caravaggio
    {"artist": "Caravaggio", "slug": "Caravaggio", "title": "The Calling of Saint Matthew", "patterns": ["*Calling_of_Saint_Matthew*", "*The_Calling_of_Saint_Matthew*"], "year": "1599–1600", "museum": "San Luigi dei Francesi, Rome"},
    {"artist": "Caravaggio", "slug": "Caravaggio", "title": "The Martyrdom of Saint Matthew", "patterns": ["*The_Martyrdom_of_Saint_Matthew*"], "year": "1599–1600", "museum": "San Luigi dei Francesi, Rome"},
    {"artist": "Caravaggio", "slug": "Caravaggio", "title": "Judith Beheading Holofernes", "patterns": ["*Judith_Beheading_Holofernes*", "*Judith*"], "year": "1598–1599", "museum": "Gallerie Nazionali d'Arte Antica, Rome"},
    {"artist": "Caravaggio", "slug": "Caravaggio", "title": "Bacchus", "patterns": ["*Bacchus*"], "year": "1595", "museum": "Uffizi Gallery, Florence"},
    {"artist": "Caravaggio", "slug": "Caravaggio", "title": "David with the Head of Goliath", "patterns": ["*David_with_the_Head_of_Goliath*", "*David*"], "year": "1609–1610", "museum": "Borghese Gallery, Rome"},

    # 5. Rembrandt van Rijn
    {"artist": "Rembrandt", "slug": "Rembrandt", "title": "The Night Watch", "patterns": ["*The_Nightwatch*", "*Night_Watch*"], "year": "1642", "museum": "Rijksmuseum, Amsterdam"},
    {"artist": "Rembrandt", "slug": "Rembrandt", "title": "The Anatomy Lesson of Dr. Nicolaes Tulp", "patterns": ["*Anatomy_Lesson_of_Dr._Nicolaes_Tulp*"], "year": "1632", "museum": "Mauritshuis, The Hague"},
    {"artist": "Rembrandt", "slug": "Rembrandt", "title": "The Storm on the Sea of Galilee", "patterns": ["*Storm_on_the_Sea_of_Galilee*"], "year": "1633", "museum": "Isabella Stewart Gardner Museum, Boston"},
    {"artist": "Rembrandt", "slug": "Rembrandt", "title": "Self-Portrait at the Age of 63", "patterns": ["*Self-portrait_in_at_the_Age_of_63*"], "year": "1669", "museum": "National Gallery, London"},
    {"artist": "Rembrandt", "slug": "Rembrandt", "title": "Self-Portrait at the Age of 34", "patterns": ["*Self-portrait_at_the_Age_of_34*"], "year": "1640", "museum": "National Gallery, London"},
    {"artist": "Rembrandt", "slug": "Rembrandt", "title": "Portrait of Saskia van Uylenburgh", "patterns": ["*Portrait_of_Saskia_van_Uylenburgh*"], "year": "1635", "museum": "National Gallery of Art, Washington D.C."},
    {"artist": "Rembrandt", "slug": "Rembrandt", "title": "Self-Portrait in Studio Attire", "patterns": ["*Self-portrait_in_studio_attire*"], "year": "1655", "museum": "Kunsthistorisches Museum, Vienna"},

    # 6. Johannes Vermeer
    {"artist": "Johannes Vermeer", "slug": "Johannes_Vermeer", "title": "Girl with a Pearl Earring", "patterns": ["*Girl_with_a_Pearl_Earring*"], "year": "1665", "museum": "Mauritshuis, The Hague"},
    {"artist": "Johannes Vermeer", "slug": "Johannes_Vermeer", "title": "The Milkmaid", "patterns": ["*The_Milkmaid*", "*milkmaid*"], "year": "1657–1658", "museum": "Rijksmuseum, Amsterdam"},
    {"artist": "Johannes Vermeer", "slug": "Johannes_Vermeer", "title": "The Art of Painting", "patterns": ["*The_Art_of_Painting*", "*Allegory_of_Painting*"], "year": "1666–1668", "museum": "Kunsthistorisches Museum, Vienna"},
    {"artist": "Johannes Vermeer", "slug": "Johannes_Vermeer", "title": "The Astronomer", "patterns": ["*The_astronomer*"], "year": "1668", "museum": "Musée du Louvre, Paris"},
    {"artist": "Johannes Vermeer", "slug": "Johannes_Vermeer", "title": "Young Woman with a Pearl Necklace", "patterns": ["*Young_Woman_with_a_Pearl_Necklace*"], "year": "1662–1664", "museum": "Gemäldegalerie, Berlin"},

    # 7. Claude Monet
    {"artist": "Claude Monet", "slug": "Claude_Monet", "title": "Impression, Sunrise", "patterns": ["*Impression,_sunrise*"], "year": "1872", "museum": "Musée Marmottan Monet, Paris"},
    {"artist": "Claude Monet", "slug": "Claude_Monet", "title": "Water Lilies (The Clouds)", "patterns": ["*Water_Lilies,_The_Clouds*", "*Water_Lilies*"], "year": "1903", "museum": "Musée de l'Orangerie, Paris"},
    {"artist": "Claude Monet", "slug": "Claude_Monet", "title": "The Japanese Bridge (Water-Lily Pond)", "patterns": ["*The_Japanese_Bridge*(The_Water-Lily*"], "year": "1899", "museum": "National Gallery of Art, Washington D.C."},
    {"artist": "Claude Monet", "slug": "Claude_Monet", "title": "Camille Monet and a Child in the Garden", "patterns": ["*Camille_Monet_and_a_Child*"], "year": "1875", "museum": "Museum of Fine Arts, Boston"},
    {"artist": "Claude Monet", "slug": "Claude_Monet", "title": "Women in the Garden", "patterns": ["*Women_in_the_garden*"], "year": "1866", "museum": "Musée d'Orsay, Paris"},
    {"artist": "Claude Monet", "slug": "Claude_Monet", "title": "Waterloo Bridge, Sunlight Effect", "patterns": ["*Waterloo_Bridge,_Sunlight_Effect*"], "year": "1903", "museum": "Art Institute of Chicago"},
    {"artist": "Claude Monet", "slug": "Claude_Monet", "title": "The Water Lily Pond and Bridge", "patterns": ["*The_Water_Lily_Pond_and_Bridge*"], "year": "1900", "museum": "Princeton University Art Museum"},

    # 8. Vincent van Gogh
    {"artist": "Vincent van Gogh", "slug": "Vincent_van_Gogh", "title": "The Starry Night", "patterns": ["*The_Starry_Night*"], "year": "1889", "museum": "Museum of Modern Art, New York"},
    {"artist": "Vincent van Gogh", "slug": "Vincent_van_Gogh", "title": "Still Life: Vase with Fifteen Sunflowers", "patterns": ["*Vase_with_Fifteen_Sunf*", "*Sunflowers*"], "year": "1888", "museum": "National Gallery, London"},
    {"artist": "Vincent van Gogh", "slug": "Vincent_van_Gogh", "title": "The Potato Eaters", "patterns": ["*The_Potato_Eaters*"], "year": "1885", "museum": "Van Gogh Museum, Amsterdam"},
    {"artist": "Vincent van Gogh", "slug": "Vincent_van_Gogh", "title": "Peasant Woman Lifting Potatoes", "patterns": ["*Peasant_Woman_Lifting_Potatoes*"], "year": "1885", "museum": "Van Gogh Museum, Amsterdam"},
    {"artist": "Vincent van Gogh", "slug": "Vincent_van_Gogh", "title": "Still Life with Three Birds' Nests", "patterns": ["*Still_Life_with_Three_Birds_Nests*"], "year": "1885", "museum": "Kröller-Müller Museum"},
    {"artist": "Vincent van Gogh", "slug": "Vincent_van_Gogh", "title": "Portrait of a Woman with a Red Ribbon", "patterns": ["*Portrait_of_a_Woman_with_a_Red_Ribbon*"], "year": "1885", "museum": "Van Gogh Museum, Amsterdam"},

    # 9. Edvard Munch
    {"artist": "Edvard Munch", "slug": "Edvard_Munch", "title": "The Scream", "patterns": ["*The_Scream*"], "year": "1893", "museum": "National Gallery of Norway, Oslo"},
    {"artist": "Edvard Munch", "slug": "Edvard_Munch", "title": "Madonna", "patterns": ["*Madonna*"], "year": "1894", "museum": "Munch Museum, Oslo"},
    {"artist": "Edvard Munch", "slug": "Edvard_Munch", "title": "The Dance of Life", "patterns": ["*The_Dance_of_Life*", "*Dance_of_Life*"], "year": "1899–1900", "museum": "National Gallery of Norway, Oslo"},
    {"artist": "Edvard Munch", "slug": "Edvard_Munch", "title": "The Sick Child", "patterns": ["*The_Sick_Child*", "*Sick_Child*"], "year": "1907", "museum": "Tate Modern, London"},
    {"artist": "Edvard Munch", "slug": "Edvard_Munch", "title": "Eye in Eye", "patterns": ["*Eye_in_Eye*"], "year": "1894", "museum": "Munch Museum, Oslo"},

    # 10. Gustav Klimt
    {"artist": "Gustav Klimt", "slug": "Gustav_Klimt", "title": "The Kiss", "patterns": ["*The_Kiss*"], "year": "1907–1908", "museum": "Österreichische Galerie Belvedere, Vienna"},
    {"artist": "Gustav Klimt", "slug": "Gustav_Klimt", "title": "Portrait of Adele Bloch-Bauer I", "patterns": ["*Adele_Bloch-Bauer*"], "year": "1907", "museum": "Neue Galerie, New York"},
    {"artist": "Gustav Klimt", "slug": "Gustav_Klimt", "title": "Judith and the Head of Holofernes", "patterns": ["*Judith*"], "year": "1901", "museum": "Österreichische Galerie Belvedere, Vienna"},
    {"artist": "Gustav Klimt", "slug": "Gustav_Klimt", "title": "Portrait of Emilie Flöge", "patterns": ["*Portrait_of_Emilie*"], "year": "1902", "museum": "Wien Museum, Vienna"},
    {"artist": "Gustav Klimt", "slug": "Gustav_Klimt", "title": "The Dancer", "patterns": ["*The_dancer*"], "year": "1916–1918", "museum": "Neue Galerie, New York"},

    # 11. Pablo Picasso
    {"artist": "Pablo Picasso", "slug": "Pablo_Picasso", "title": "Guernica", "patterns": ["*Guernica*"], "year": "1937", "museum": "Museo Reina Sofía, Madrid"},
    {"artist": "Pablo Picasso", "slug": "Pablo_Picasso", "title": "The Old Blind Guitarist", "patterns": ["*The_old_blind_guitarist*"], "year": "1903", "museum": "Art Institute of Chicago"},
    {"artist": "Pablo Picasso", "slug": "Pablo_Picasso", "title": "Self-Portrait (1907)", "patterns": ["*Self-Portrait*"], "year": "1907", "museum": "National Gallery, Prague"},
    {"artist": "Pablo Picasso", "slug": "Pablo_Picasso", "title": "Portrait of Dora Maar", "patterns": ["*Portrait_of_Dora_Maar*"], "year": "1937", "museum": "Musée Picasso, Paris"},
    {"artist": "Pablo Picasso", "slug": "Pablo_Picasso", "title": "Child with a Dove", "patterns": ["*Child_with_dove*"], "year": "1901", "museum": "National Gallery, London"},

    # 12. Salvador Dalí
    {"artist": "Salvador Dali", "slug": "Salvador_Dali", "title": "The Persistence of Memory", "patterns": ["*The_Persistence_of_Memory*"], "year": "1931", "museum": "Museum of Modern Art, New York"},
    {"artist": "Salvador Dali", "slug": "Salvador_Dali", "title": "The Great Masturbator", "patterns": ["*The_Great_Masturbator*"], "year": "1929", "museum": "Museo Reina Sofía, Madrid"},
    {"artist": "Salvador Dali", "slug": "Salvador_Dali", "title": "Swans Reflecting Elephants", "patterns": ["*Swans_Reflecting_Elephants*"], "year": "1937", "museum": "Private Collection"},
    {"artist": "Salvador Dali", "slug": "Salvador_Dali", "title": "The Metamorphosis of Narcissus", "patterns": ["*The_Metamorphosis_of_Narcissus*"], "year": "1937", "museum": "Tate Modern, London"},
    {"artist": "Salvador Dali", "slug": "Salvador_Dali", "title": "The Temptation of St. Anthony", "patterns": ["*The_Temptation_of_St._Anthony*"], "year": "1946", "museum": "Royal Museums of Fine Arts of Belgium"},
    {"artist": "Salvador Dali", "slug": "Salvador_Dali", "title": "Crucifixion (Corpus Hypercubicus)", "patterns": ["*Crucifixion_(Corpus_Hypercubicus)*"], "year": "1954", "museum": "Metropolitan Museum of Art, New York"},
    {"artist": "Salvador Dali", "slug": "Salvador_Dali", "title": "Galatea of the Spheres", "patterns": ["*Galatea_of_the_Spheres*"], "year": "1952", "museum": "Dalí Theatre and Museum, Figueres"},
    {"artist": "Salvador Dali", "slug": "Salvador_Dali", "title": "The Disintegration of the Persistence of Memory", "patterns": ["*Disintegration_of_the_Persisten*"], "year": "1954", "museum": "Salvador Dalí Museum, St. Petersburg, FL"},

    # 13. Frida Kahlo
    {"artist": "Frida Kahlo", "slug": "Frida_Kahlo", "title": "The Two Fridas", "patterns": ["*The_Two_Fridas*"], "year": "1939", "museum": "Museo de Arte Moderno, Mexico City"},
    {"artist": "Frida Kahlo", "slug": "Frida_Kahlo", "title": "The Broken Column", "patterns": ["*The_Broken_Column*"], "year": "1944", "museum": "Museo Dolores Olmedo, Mexico City"},
    {"artist": "Frida Kahlo", "slug": "Frida_Kahlo", "title": "Viva la Vida, Watermelons", "patterns": ["*Viva_la_Vida*"], "year": "1954", "museum": "Frida Kahlo Museum, Mexico City"},
    {"artist": "Frida Kahlo", "slug": "Frida_Kahlo", "title": "Henry Ford Hospital", "patterns": ["*Henry_Ford_Hospital*"], "year": "1932", "museum": "Museo Dolores Olmedo, Mexico City"},
    {"artist": "Frida Kahlo", "slug": "Frida_Kahlo", "title": "My Birth", "patterns": ["*My_Birth*"], "year": "1932", "museum": "Private Collection"},
]


def sanitize_filename(name: str, max_len: int = 40) -> str:
    """Sanitize string for cross-platform file naming."""
    sanitized = re.sub(r'[\\/*?:"<>|#\x00-\x1f]', "", name)
    sanitized = re.sub(r"\s+", "_", sanitized).strip("._-")
    return sanitized[:max_len].rstrip("._-") or "untitled"


def curate_masterpieces(source_dir: Path, top100_dir: Path, output_dir: Path) -> list:
    """
    Finds each masterpiece in local directories, selects the highest resolution file,
    copies it to the output directory, and generates JSON/CSV metadata.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    curated_list = []

    print("=" * 75)
    print(" CURATING TOP CELEBRATED MASTERPIECES ACROSS 13 MASTERS")
    print("=" * 75)
    print(f"Artist Source   : {source_dir}")
    print(f"Popular Source  : {top100_dir}")
    print(f"Curated Output  : {output_dir}\n")

    for idx, sig in enumerate(MASTERPIECE_SIGNATURES, start=1):
        found_file = None
        candidates = []

        # Search in top100 folder
        if top100_dir.exists():
            for pat in sig["patterns"]:
                for match in top100_dir.glob(pat):
                    if match.is_file() and match.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                        candidates.append(match)

        # Search in artist specific folder
        artist_folder = source_dir / sig["slug"]
        if artist_folder.exists():
            for pat in sig["patterns"]:
                for match in artist_folder.glob(pat):
                    if match.is_file() and match.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                        candidates.append(match)

        if candidates:
            # Sort by file size descending to choose the highest resolution / quality scan
            candidates.sort(key=lambda p: p.stat().st_size, reverse=True)
            found_file = candidates[0]

        if found_file:
            clean_artist = sanitize_filename(sig["artist"].replace(" ", "_"), 25)
            clean_title = sanitize_filename(sig["title"].replace(" ", "_"), 35)
            ext = found_file.suffix.lower()
            dest_name = f"{idx:02d}_{clean_artist}_-_{clean_title}{ext}"
            dest_path = output_dir / dest_name

            # Copy file
            shutil.copy2(found_file, dest_path)
            file_size = dest_path.stat().st_size
            size_mb = round(file_size / 1048576.0, 2)

            # Parse dimensions from filename if present
            w, h, mp = 0, 0, 0.0
            dim_match = re.search(r"(\d+)x(\d+)", found_file.name)
            if dim_match:
                w = int(dim_match.group(1))
                h = int(dim_match.group(2))
                mp = round((w * h) / 1000000.0, 2)

            item = {
                "CuratedIndex": idx,
                "Artist": sig["artist"],
                "Title": sig["title"],
                "Year": sig["year"],
                "Museum": sig["museum"],
                "Width": w,
                "Height": h,
                "Megapixels": mp,
                "FileSizeBytes": file_size,
                "FileSizeMB": size_mb,
                "FileName": dest_name,
                "SourcePath": str(found_file.resolve()),
            }
            curated_list.append(item)
            print(f"  [{idx:02d}] Curated: {sig['artist']} — \"{sig['title']}\" ({size_mb} MB, {w}x{h})")
        else:
            print(f"  [--] Not found: {sig['artist']} — \"{sig['title']}\"")

    # Export metadata
    json_path = output_dir / "curated_masterpieces.json"
    csv_path = output_dir / "curated_masterpieces.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(curated_list, f, indent=4, ensure_ascii=False)

    if curated_list:
        keys = list(curated_list[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(curated_list)

    print("\n" + "=" * 75)
    print(" CURATION COMPLETE")
    print("=" * 75)
    print(f"Total Curated Masterpieces : {len(curated_list)}")
    print(f"JSON Database              : {json_path}")
    print(f"CSV Database               : {csv_path}")
    print("=" * 75)
    return curated_list


def main():
    parser = argparse.ArgumentParser(
        description="Curate top celebrity masterpieces into a premier high-res collection.",
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default="./artist_paintings",
        help="Relative path to artist archives directory (default: './artist_paintings').",
    )
    parser.add_argument(
        "--top100-dir",
        type=str,
        default="./paintings_output",
        help="Relative path to popular paintings directory (default: './paintings_output').",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./artist_paintings/Top_Celebrity_Masterpieces",
        help="Relative path to curated output directory.",
    )

    args = parser.parse_args()
    source_dir = Path(args.source_dir).resolve()
    top100_dir = Path(args.top100_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    curate_masterpieces(source_dir, top100_dir, output_dir)


if __name__ == "__main__":
    main()
