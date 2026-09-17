import json
import glob
from pathlib import Path

# Load Curated Masterpieces
with open('artist_paintings/Top_Celebrity_Masterpieces/curated_masterpieces.json', 'r', encoding='utf-8-sig') as f:
    curated = json.load(f)

# Load Top Popular metadata
with open('paintings_output/paintings_metadata.json', 'r', encoding='utf-8-sig') as f:
    popular = json.load(f)

# Build filename to URL lookup map
url_lookup = {}
pop_rank_lookup = {}

for p in popular:
    fname = p.get('LocalFileName') or p.get('FileName')
    url = p.get('HighResUrl') or p.get('image') or p.get('ImageURL')
    rank = p.get('Rank')
    if fname:
        if url: url_lookup[fname] = url
        if rank: pop_rank_lookup[fname] = rank

for meta_file in glob.glob('artist_paintings/*/metadata.json'):
    try:
        with open(meta_file, 'r', encoding='utf-8-sig') as f:
            art_items = json.load(f)
            for a in art_items:
                fname = a.get('LocalFileName') or a.get('FileName')
                url = a.get('HighResUrl') or a.get('ImageURL') or a.get('image')
                if fname and url and fname not in url_lookup:
                    url_lookup[fname] = url
    except Exception as exc:
        pass

# Fallback WikiArt CDN image search helper
# Attach HighResUrl to each curated painting
for item in curated:
    src_file = item.get('SourcePath', '').split('/')[-1]
    item_file = item.get('FileName')
    
    url = url_lookup.get(src_file) or url_lookup.get(item_file)
    if not url:
        # Check by matching title pattern
        for fname, u in url_lookup.items():
            slug_title = item['Title'].lower().replace(' ', '_')[:15]
            if slug_title in fname.lower():
                url = u
                break
    if not url:
        print(f"Unmatched: {item['Artist']} - {item['Title']} ({item['FileName']})")
    item['HighResUrl'] = url or ''
    fname = item["FileName"]
    item['LocalRelativePath'] = f'artist_paintings/Top_Celebrity_Masterpieces/{fname}'

print(f'Total Curated Paintings: {len(curated)}')
matched_urls = sum(1 for x in curated if x['HighResUrl'])
print(f'Paintings with HighResUrl: {matched_urls}/{len(curated)}')

# Now build the full artists dataset
artists_meta = [
    {
        'id': 'botticelli',
        'name': 'Sandro Botticelli',
        'slug': 'sandro-botticelli',
        'lifespan': '1445–1510',
        'epochId': 'renaissance',
        'epochName': 'Early Renaissance Humanism',
        'movement': 'Early Renaissance Florentine Humanism',
        'location': 'Florence, Medici Court',
        'epithet': 'The Poet of Early Renaissance Grace & Myth',
        'whyBelongs': 'Revived classical Greco-Roman mythology, introducing non-religious pagan allegories back into European high art after a millennium of strict medieval dogma. Defined the universal Western archetype of poetic, ethereal female beauty that inspired modern high-fashion aesthetics. The Birth of Venus is among the top 10 most recognized paintings on Earth.',
        'evolutionRole': 'Rejected heavy geometric realism in favor of lyrical contour lines, decorative drapery, and graceful elongation. He bridged the Gothic tradition with Renaissance Neoplatonism, creating harmonious compositions where philosophical ideals of divine love and earthly grace merged into painting.',
        'totalWorksCataloged': 137,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Sandro Botticelli'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/01_Sandro_Botticelli_-_The_Birth_of_Venus.jpg'
    },
    {
        'id': 'davinci',
        'name': 'Leonardo da Vinci',
        'slug': 'leonardo-da-vinci',
        'lifespan': '1452–1519',
        'epochId': 'renaissance',
        'epochName': 'High Renaissance',
        'movement': 'High Renaissance Classicism & Polymath Science',
        'location': 'Florence, Milan, Rome, Amboise (France)',
        'epithet': 'The Universal Polymath of High Renaissance Harmony',
        'whyBelongs': 'The quintessential Renaissance Man—scientist, anatomist, engineer, and painter. Created the single most famous, parodied, analyzed, and valuable visual artwork in recorded human history (Mona Lisa), alongside the masterwork of narrative perspective (The Last Supper).',
        'evolutionRole': 'Elevated painting from a craft guild to an intellectual divine science through anatomical dissection of human cadavers. Pioneered sfumato (imperceptible tonal transitions without harsh outlines) and atmospheric perspective, replacing stiff medieval compositions with dynamic triangular geometry.',
        'totalWorksCataloged': 205,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Leonardo da Vinci'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/06_Leonardo_da_Vinci_-_Mona_Lisa.jpg'
    },
    {
        'id': 'michelangelo',
        'name': 'Michelangelo Buonarroti',
        'slug': 'michelangelo',
        'lifespan': '1475–1564',
        'epochId': 'renaissance',
        'epochName': 'High Renaissance & Proto-Mannerism',
        'movement': 'Monumental Renaissance Classicism',
        'location': 'Florence, Vatican City (Rome)',
        'epithet': 'The Titan of Monumental Human Drama',
        'whyBelongs': 'Master of epic anatomical power; redefined human musculature as the ultimate vessel of divine spiritual torment and glory. Executed the greatest fresco commissions in history across the Sistine Chapel ceiling and altar wall, entirely by his own hand.',
        'evolutionRole': 'Michelangelo viewed the human body as an architectural monument. He discarded passive tranquility in favor of terribilità—an awe-inspiring, tense, brooding power. His figures twist through space with unprecedented kinetic energy, establishing anatomy as the central narrative medium of Western art.',
        'totalWorksCataloged': 183,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Michelangelo'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/14_Michelangelo_-_The_Creation_of_Adam.jpg'
    },
    {
        'id': 'caravaggio',
        'name': 'Caravaggio',
        'slug': 'caravaggio',
        'lifespan': '1571–1610',
        'epochId': 'baroque',
        'epochName': 'The Baroque Revolution',
        'movement': 'Tenebrism & Theatrical Naturalism',
        'location': 'Rome, Naples, Malta, Sicily',
        'epithet': 'The Rebel Pioneer of Chiaroscuro & Street Naturalism',
        'whyBelongs': 'Shattered idealized Renaissance mannerisms by casting prostitutes, beggars, and laborers with dirty feet as apostles and saints. Single-handedly launched the Baroque revolution and inspired Rembrandt, Velázquez, and modern cinematic lighting.',
        'evolutionRole': 'Revolutionized chiaroscuro into dramatic tenebrism—pitch-black voids pierced by razor-sharp diagonal spotlighting. Transformed passive sacred icons into visceral, violent, psychological crime-scene moments that forced the viewer into active spiritual witness.',
        'totalWorksCataloged': 105,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Caravaggio'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/23_Caravaggio_-_The_Martyrdom_of_Saint_Matthew.jpg'
    },
    {
        'id': 'rembrandt',
        'name': 'Rembrandt van Rijn',
        'slug': 'rembrandt',
        'lifespan': '1606–1669',
        'epochId': 'baroque',
        'epochName': 'Dutch Golden Age',
        'movement': 'Dutch Baroque Realism & Psychological Portraiture',
        'location': 'Amsterdam, Dutch Republic',
        'epithet': 'The Supreme Chronicler of the Human Soul',
        'whyBelongs': 'Western art\'s greatest portraitist and printmaker. Documented human fallibility and mortality with unmatched empathy across over 80 unflinching self-portraits spanning ambitious youth to bankrupt old age. The Night Watch revolutionized civic group portraits.',
        'evolutionRole': 'Substituted Italian theatrical perfection with deeply human, tactile, sculpted impasto. Rembrandt handled light not merely as an optical device, but as an emotional medium of introspection and spiritual grace.',
        'totalWorksCataloged': 767,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Rembrandt'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/27_Rembrandt_-_The_Night_Watch.jpg'
    },
    {
        'id': 'vermeer',
        'name': 'Johannes Vermeer',
        'slug': 'johannes-vermeer',
        'lifespan': '1632–1675',
        'epochId': 'baroque',
        'epochName': 'Dutch Golden Age Luminism',
        'movement': 'Dutch Genre Luminism & Precision Realism',
        'location': 'Delft, Dutch Republic',
        'epithet': 'The Master of Light & Quietude',
        'whyBelongs': 'The Sphinx of Delft produced an exceptionally rare, precious jewel-box catalog of only ~35 surviving masterpieces. Girl with a Pearl Earring is revered globally as the \"Dutch Mona Lisa\", and The Art of Painting stands at 45.80 Megapixels as one of history\'s greatest optical triumphs.',
        'evolutionRole': 'Achieved an uncanny photographic photorealism two centuries before the invention of the camera. Employed camera obscura techniques, globular pointillistic specular highlights, and costly genuine lapis lazuli pigment to monumentalize intimate domestic rituals into timeless moments of grace.',
        'totalWorksCataloged': 44,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Johannes Vermeer'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/34_Johannes_Vermeer_-_Girl_with_a_Pearl_Earring.jpg'
    },
    {
        'id': 'monet',
        'name': 'Claude Monet',
        'slug': 'claude-monet',
        'lifespan': '1840–1926',
        'epochId': 'impressionism',
        'epochName': '19th C. Optical Revolution',
        'movement': 'French Impressionism & Plein-Air Luminism',
        'location': 'Paris, Argenteuil, Giverny (France)',
        'epithet': 'The Father of Impressionism & Pure Light',
        'whyBelongs': 'Founder and ideological anchor of French Impressionism. His 1872 painting Impression, Sunrise christened the most influential modern art movement in history. His monumental late Water Lilies installations anticipated 20th-century Abstract Expressionism.',
        'evolutionRole': 'Shattered centuries of dark studio academic painting by taking his easel outdoors (en plein air) to paint light itself rather than physical objects. Deconstructed form into rapid, unblended optical color vibrations that merge on the viewer\'s retina.',
        'totalWorksCataloged': 1367,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Claude Monet'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/39_Claude_Monet_-_Impression,_Sunrise.jpg'
    },
    {
        'id': 'vangogh',
        'name': 'Vincent van Gogh',
        'slug': 'vincent-van-gogh',
        'lifespan': '1853–1890',
        'epochId': 'impressionism',
        'epochName': 'Post-Impressionism',
        'movement': 'Post-Impressionism & Emotional Expressive Impasto',
        'location': 'Netherlands, Paris, Arles, Saint-Rémy, Auvers-sur-Oise',
        'epithet': 'The Torrent of Emotional Color & Spiritual Vision',
        'whyBelongs': 'The archetype of pure, uncompromised artistic devotion. Created over 2,000 artworks in a single feverish decade despite enduring profound mental anguish and extreme poverty. The Starry Night and Sunflowers are among the most celebrated visual monuments of humanity.',
        'evolutionRole': 'Liberated color and brushstrokes from literal representation, turning thick impasto paint into a dynamic direct conductor of psychic ecstasy, despair, and cosmic awe. Van Gogh became the direct spiritual forefather of 20th-century German Expressionism and modern abstract art.',
        'totalWorksCataloged': 1932,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Vincent van Gogh'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/46_Vincent_van_Gogh_-_The_Starry_Night.jpg'
    },
    {
        'id': 'munch',
        'name': 'Edvard Munch',
        'slug': 'edvard-munch',
        'lifespan': '1863–1944',
        'epochId': 'expressionism',
        'epochName': 'Fin-de-Siècle Expressionism',
        'movement': 'Psychological Expressionism & Symbolism',
        'location': 'Kristiania (Oslo), Berlin, Paris',
        'epithet': 'The Herald of Modern Existential Angst',
        'whyBelongs': 'Creator of The Scream, the universal Western shorthand for psychological dread, existential vertigo, and modern angst—second only to the Mona Lisa in global visual recognition.',
        'evolutionRole': 'Radically abandoned traditional naturalism to paint internal psychological states: grief, jealousy, sexual obsession, illness, and despair. Developed fluid, undulating rhythmic contours that visualize internal scream vibrations passing through external nature.',
        'totalWorksCataloged': 196,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Edvard Munch'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/52_Edvard_Munch_-_The_Scream.jpg'
    },
    {
        'id': 'klimt',
        'name': 'Gustav Klimt',
        'slug': 'gustav-klimt',
        'lifespan': '1862–1918',
        'epochId': 'expressionism',
        'epochName': 'Vienna Secession & Golden Phase',
        'movement': 'Vienna Secession, Art Nouveau & Symbolism',
        'location': 'Vienna, Austria-Hungary',
        'epithet': 'The Alchemist of Gold, Sensuality & Secession',
        'whyBelongs': 'Founding president of the revolutionary Vienna Secession. His Golden Phase culminated in The Kiss and Portrait of Adele Bloch-Bauer I, uniting classical eroticism with opulent decorative splendor.',
        'evolutionRole': 'Synthesized Byzantine mosaic gold leaf with Japanese print flat ornamentation, erotic Freudian psychology, and organic Art Nouveau spirals. Dissolved realistic academic depth into shimmering abstract tapestries.',
        'totalWorksCataloged': 169,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Gustav Klimt'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/57_Gustav_Klimt_-_The_Kiss.jpg'
    },
    {
        'id': 'picasso',
        'name': 'Pablo Picasso',
        'slug': 'pablo-picasso',
        'lifespan': '1881–1973',
        'epochId': 'modernism',
        'epochName': '20th Century Avant-Garde',
        'movement': 'Cubism, Blue/Rose Periods, Surrealism, Modernism',
        'location': 'Malaga, Barcelona, Paris, French Riviera',
        'epithet': 'The Demiurge of 20th Century Visual Modernism',
        'whyBelongs': 'The undisputed colossus of modern art. Over seven decades, Picasso dismantled and rebuilt the visual grammar of civilization, traversing Blue, Rose, African, Cubist, Neoclassical, and Surrealist phases.',
        'evolutionRole': 'Co-founded Cubism, obliterating 500 years of Renaissance perspective by shattering three-dimensional space onto a flat surface seen from multiple vantage points simultaneously. Painted Guernica, modern history\'s greatest, most searing condemnation of fascist violence and warfare.',
        'totalWorksCataloged': 1169,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Pablo Picasso'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/62_Pablo_Picasso_-_Guernica.jpg'
    },
    {
        'id': 'dali',
        'name': 'Salvador Dalí',
        'slug': 'salvador-dali',
        'lifespan': '1904–1989',
        'epochId': 'modernism',
        'epochName': 'Surrealism & Dreamscapes',
        'movement': 'Surrealism & Paranoiac-Critical Method',
        'location': 'Figueres, Cadaqués, Paris, New York',
        'epithet': 'The Wizard of Paranoiac-Critical Subconscious Dreams',
        'whyBelongs': 'The definitive face of Surrealism and 20th-century showmanship. His melting watches in The Persistence of Memory became the quintessential modern visualization of the malleability of time, mortality, and the Freudian unconscious.',
        'evolutionRole': 'Pioneered the Paranoiac-Critical method: cultivating irrational subconscious associations, hallucinations, and double-images while executing them with hyper-precise 17th-century Dutch optical miniature technique (\"hand-painted dream photographs\").',
        'totalWorksCataloged': 1178,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Salvador Dali'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/67_Salvador_Dali_-_The_Persistence_of_Memory.jpg'
    },
    {
        'id': 'kahlo',
        'name': 'Frida Kahlo',
        'slug': 'frida-kahlo',
        'lifespan': '1907–1954',
        'epochId': 'modernism',
        'epochName': 'Mexican Modernism & Identity',
        'movement': 'Autobiographical Surrealism & Mexicanidad',
        'location': 'Coyoacán (Mexico City), New York, Paris',
        'epithet': 'The Global Cultural Icon of Resilience & Identity',
        'whyBelongs': 'Has achieved unprecedented global cultural and feminist iconography (\"Fridamania\"). Transmuted profound chronic physical pain, personal heartbreak, and indigenous Mexican heritage into unflinching, mythic autobiographical masterpieces (The Two Fridas, The Broken Column).',
        'evolutionRole': 'Rejected orthodox European Surrealism to paint her direct internal reality (\"I never painted dreams. I painted my own reality\"). Blended traditional Mexican retablo folk devotional painting with raw anatomical, psychological, and matriarchal symbolism.',
        'totalWorksCataloged': 100,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Frida Kahlo'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/75_Frida_Kahlo_-_The_Two_Fridas.jpg'
    }
]

epochs = [
    {
        'id': 'all',
        'name': 'All Eras (1470–1954)',
        'description': 'The complete 500-year evolution across 13 celebrity masters and 78 curated masterpieces.'
    },
    {
        'id': 'renaissance',
        'name': 'Renaissance Humanism (1470–1564)',
        'description': 'Classical revival, sacred geometry, anatomical heroism, and polymath harmony (Botticelli, Da Vinci, Michelangelo).'
    },
    {
        'id': 'baroque',
        'name': 'Baroque & Dutch Golden Age (1595–1675)',
        'description': 'Tenebrist drama, emotional impasto, photographic luminism, and domestic quietude (Caravaggio, Rembrandt, Vermeer).'
    },
    {
        'id': 'impressionism',
        'name': '19th C. Optical Revolution (1872–1893)',
        'description': 'Plein-air atmospheric flux, dissolution of academic contours, and raw emotional impasto (Monet, Van Gogh).'
    },
    {
        'id': 'expressionism',
        'name': 'Expressionism & Secession (1893–1918)',
        'description': 'Psychological angst, decorative gold mosaics, and internal existential vulnerability (Munch, Klimt).'
    },
    {
        'id': 'modernism',
        'name': '20th C. Avant-Garde (1901–1954)',
        'description': 'Cubist perspective deconstruction, Freudian surreal dreamscapes, and raw autobiographical identity (Picasso, Dalí, Kahlo).'
    }
]

# Overall stats
stats = {
    'totalArtists': len(artists_meta),
    'totalCuratedWorks': len(curated),
    'totalIngestedPaintings': 7652,
    'totalIngestedGB': '4.35 GB',
    'peakMegapixels': 45.80,
    'peakPainting': 'The Art of Painting (Johannes Vermeer)',
    'timeSpan': '1470 – 1954 (484 Years)',
    'museumCollectionsCount': len(set(x['Museum'] for x in curated if x.get('Museum'))),
}

# Attach artist id to curated items
artist_slug_to_id = {
    'sandro botticelli': 'botticelli',
    'leonardo da vinci': 'davinci',
    'michelangelo': 'michelangelo',
    'caravaggio': 'caravaggio',
    'rembrandt': 'rembrandt',
    'johannes vermeer': 'vermeer',
    'claude monet': 'monet',
    'vincent van gogh': 'vangogh',
    'edvard munch': 'munch',
    'gustav klimt': 'klimt',
    'pablo picasso': 'picasso',
    'salvador dali': 'dali',
    'frida kahlo': 'kahlo'
}

for item in curated:
    art_norm = item['Artist'].strip().lower()
    item['ArtistId'] = artist_slug_to_id.get(art_norm, 'other')
    # assign epoch
    for a in artists_meta:
        if a['id'] == item['ArtistId']:
            item['EpochId'] = a['epochId']
            break

# Export to JSON
full_data = {
    'stats': stats,
    'epochs': epochs,
    'artists': artists_meta,
    'masterpieces': curated,
    'topPopular': popular[:50]
}

with open('data/pantheon_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(full_data, f, indent=2, ensure_ascii=False)

# Export to js/catalog-data.js as global JS constant
js_content = '/**\n * Pantheon Art History & Masterpiece Catalog\n * Auto-generated dataset for GitHub Pages exhibition\n */\n'
js_content += 'window.PANTHEON_DATA = ' + json.dumps(full_data, indent=2, ensure_ascii=False) + ';\n'

with open('js/catalog-data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print('Successfully generated data/pantheon_catalog.json and js/catalog-data.js')
