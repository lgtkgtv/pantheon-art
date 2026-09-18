import json
import glob
import re
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

# Attach HighResUrl and local relative paths to each curated painting
for item in curated:
    src_file = item.get('SourcePath', '').split('/')[-1]
    item_file = item.get('FileName')
    
    url = url_lookup.get(src_file) or url_lookup.get(item_file)
    if not url:
        for fname, u in url_lookup.items():
            slug_title = item['Title'].lower().replace(' ', '_')[:15]
            if slug_title in fname.lower():
                url = u
                break
    item['HighResUrl'] = url or ''
    fname = item["FileName"]
    item['LocalRelativePath'] = f'artist_paintings/Top_Celebrity_Masterpieces/{fname}'

# Crown jewel title matcher
crown_jewel_titles = {
    'the birth of venus', 'the spring (primavera)', 'mona lisa', 'the last supper',
    'lady with an ermine', 'the creation of adam', 'the last judgement',
    'the calling of saint matthew', 'the martyrdom of saint matthew', 'judith beheading holofernes',
    'the night watch', 'the anatomy lesson of dr. nicolaes tulp', 'girl with a pearl earring',
    'the milkmaid', 'the art of painting', 'impression, sunrise', 'water lilies (the clouds)',
    'the japanese bridge (water-lily pond)', 'the starry night', 'still life: vase with fifteen sunflowers',
    'the potato eaters', 'the scream', 'madonna', 'the kiss', 'portrait of adele bloch-bauer i',
    'guernica', 'the old blind guitarist', 'the persistence of memory', 'the great masturbator',
    'swans reflecting elephants', 'the two fridas', 'the broken column', 'viva la vida, watermelons'
}

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
    title_norm = item['Title'].strip().lower()
    item['isCrownJewel'] = title_norm in crown_jewel_titles or item.get('Megapixels', 0) >= 20.0
    item['isUltraRes'] = item.get('Megapixels', 0) >= 15.0

# Canonical Physical Dimensions Table (cm width, cm height, architectural type)
physical_dims = {
    'the birth of venus': (278.9, 172.5, 'Grand Mythological Canvas'),
    'the spring (primavera)': (314.0, 203.0, 'Grand Allegorical Masterpiece'),
    'the mystical nativity': (75.0, 108.5, 'Devotional Panel'),
    'the story of nastagio degli onesti': (138.0, 83.0, 'Spalliera Wedding Panel'),
    'calumny of apelles': (91.0, 62.0, 'Classical Allegory'),
    'pallas and the centaur': (147.5, 207.0, 'Philosophical Allegory'),
    'mona lisa': (53.0, 77.0, 'Intimate Poplar Panel'),
    'the last supper': (880.0, 460.0, 'Monumental Convent Refectory Fresco'),
    'lady with an ermine': (39.0, 54.0, 'Intimate Walnut Panel'),
    'virgin of the rocks': (122.0, 199.0, 'Altar Panel'),
    'the annunciation': (217.0, 98.0, 'Early Masterwork'),
    'saint john the baptist': (57.0, 69.0, 'Final Walnut Masterwork'),
    'the creation of adam': (570.0, 280.0, 'Sistine Chapel Ceiling Fresco'),
    'the last judgement': (1220.0, 1370.0, 'Colossal Sistine Altar Wall'),
    'the fall of man and expulsion': (570.0, 280.0, 'Sistine Chapel Ceiling Fresco'),
    'the creation of eve': (380.0, 170.0, 'Sistine Chapel Ceiling Fresco'),
    'the prophet jeremiah': (380.0, 390.0, 'Sistine Ceiling Prophet'),
    'doni tondo': (120.0, 120.0, 'Holy Family Circular Tondo'),
    'the calling of saint matthew': (340.0, 322.0, 'Monumental Contarelli Chapel Canvas'),
    'the martyrdom of saint matthew': (343.0, 323.0, 'Dramatic Action Tenebrism'),
    'judith beheading holofernes': (195.0, 145.0, 'Visceral Dramatic Canvas'),
    'the entombment of christ': (203.0, 300.0, 'Monumental Altar Canvas'),
    'bacchus': (85.0, 95.0, 'Sensual Youth Portrait'),
    'david with the head of goliath': (101.0, 125.0, 'Dark Tragic Self-Portrait'),
    'the night watch': (437.0, 363.0, 'Colossal Civic Guard Canvas'),
    'the anatomy lesson of dr. nicolaes tulp': (216.5, 169.5, 'Dynamic Guild Portrait'),
    'the storm on the sea of galilee': (128.0, 160.0, 'Dramatic Seascape (Stolen)'),
    'the return of the prodigal son': (205.0, 262.0, 'Spiritual Monumental Canvas'),
    'self-portrait with two circles': (94.0, 114.0, 'Late Psychological Masterpiece'),
    'the jewish bride': (166.5, 121.5, 'Golden Impasto Tenderness'),
    'girl with a pearl earring': (39.0, 44.5, 'Intimate Domestic Tronie'),
    'the milkmaid': (41.0, 45.5, 'Intimate Sacred Stillness'),
    'the art of painting': (100.0, 120.0, 'Full-Scale Studio Allegory'),
    'the astronomer': (45.0, 50.0, 'Enlightenment Intellectual'),
    'the geographer': (46.5, 53.0, 'Scientific Curiosity Study'),
    'view of delft': (117.5, 96.5, 'Luminous Optical Cityscape'),
    'impression, sunrise': (63.0, 48.0, 'Plein-Air Harbor Study'),
    'water lilies (the clouds)': (1275.0, 200.0, 'Panoramic Curved Mural Installation'),
    'the japanese bridge (water-lily pond)': (101.0, 89.0, 'Giverny Garden Canvas'),
    'woman with a parasol': (81.0, 100.0, 'Fleeting Optical Portrait'),
    'poppies': (65.0, 50.0, 'Summer Meadow Impression'),
    'rouen cathedral, west façade, sunlight': (73.0, 100.0, 'Atmospheric Light Series'),
    'the starry night': (92.1, 73.7, 'Intimate Cosmic Vision'),
    'still life: vase with fifteen sunflowers': (73.0, 92.1, 'Vibrant Chrome Yellow Still Life'),
    'the potato eaters': (114.0, 82.0, 'Raw Peasant Earthiness'),
    'cafe terrace at night': (65.3, 80.7, 'Luminous Nocturne Scene'),
    'wheatfield with crows': (103.0, 50.5, 'Turbulent Final Horizon'),
    'the yellow house': (91.5, 72.0, 'Sunlit Arles Sanctuary'),
    'the scream': (73.5, 91.0, 'Cardboard Tempera & Pastel Icon'),
    'madonna': (71.0, 90.0, 'Sensual Symbolist Icon'),
    'the dance of life': (190.5, 125.0, 'Grand Allegory of Love & Loss'),
    'vampire': (109.0, 91.0, 'Psychological Symbolism'),
    'jealousy': (100.0, 67.0, 'Claustrophobic Melodrama'),
    'anxiety': (74.0, 94.0, 'Crowd Modern Alienation'),
    'the kiss': (180.0, 180.0, 'Square Gold Leaf Masterpiece'),
    'portrait of adele bloch-bauer i': (138.0, 138.0, 'Golden Viennese Portrait'),
    'judith and the head of holofernes': (42.0, 84.0, 'Decadent Femme Fatale'),
    'danaë': (110.0, 77.0, 'Golden Erotic Myth'),
    'the tree of life, stoclet frieze': (195.0, 102.0, 'Art Nouveau Mosaic Mural'),
    'the virgin': (200.0, 190.0, 'Late Colorful Swirling Canvas'),
    'guernica': (776.6, 349.3, 'Colossal Anti-War Monumental Canvas'),
    'les demoiselles d\'avignon': (233.7, 243.9, 'Revolutionary Proto-Cubist Canvas'),
    'the old blind guitarist': (82.6, 122.9, 'Blue Period Melancholy'),
    'three musicians': (222.9, 200.7, 'Synthetic Cubist Masterwork'),
    'the weeping woman': (50.0, 60.0, 'Shattered Modern Grief'),
    'girl before a mirror': (130.2, 162.3, 'Surrealist Psychological Portrait'),
    'the persistence of memory': (33.0, 24.1, 'Intimate Surrealist Miniature'),
    'swans reflecting elephants': (77.5, 51.5, 'Double-Image Paranoiac Canvas'),
    'the great masturbator': (150.0, 110.0, 'Freudian Dream Landscape'),
    'the temptation of st. anthony': (119.5, 89.5, 'Spidery Surrealist Mirage'),
    'dream caused by the flight of a bee': (40.5, 51.0, 'Photographic Dream Realism'),
    'metamorphosis of narcissus': (78.0, 51.2, 'Double-Image Transformation'),
    'the two fridas': (173.0, 173.5, 'Square Double Self-Portrait'),
    'the broken column': (30.5, 39.8, 'Intimate Autobiographical Icon'),
    'self-portrait with thorn necklace and hummingbird': (47.0, 61.2, 'Indigenous Mexican Iconography'),
    'the wounded deer': (30.0, 22.4, 'Surrealist Suffering Allegory'),
    'viva la vida, watermelons': (72.0, 59.5, 'Final Defiant Celebration of Life'),
    'henry ford hospital': (38.0, 30.5, 'Visceral Sheet Metal Panel')
}

for item in curated:
    title_key = item['Title'].strip().lower()
    dim_entry = None
    for k, v in physical_dims.items():
        if k in title_key or title_key in k:
            dim_entry = v
            break
    if not dim_entry:
        aspect = item['Width'] / max(1, item['Height'])
        h_cm = 90.0
        w_cm = round(h_cm * aspect, 1)
        dim_entry = (w_cm, h_cm, 'Museum Master Canvas')
    
    w_cm, h_cm, p_type = dim_entry
    w_in = round(w_cm / 2.54, 1)
    h_in = round(h_cm / 2.54, 1)
    item['physicalWidthCm'] = w_cm
    item['physicalHeightCm'] = h_cm
    item['physicalType'] = p_type
    
    if w_cm >= 400 or h_cm >= 400:
        w_ft = round(w_cm / 30.48, 1)
        h_ft = round(h_cm / 30.48, 1)
        item['physicalDimensionsStr'] = f'{w_cm:g} × {h_cm:g} cm ({w_ft} × {h_ft} ft) • {p_type}'
    else:
        item['physicalDimensionsStr'] = f'{w_cm:g} × {h_cm:g} cm ({w_in:g} × {h_in:g} in) • {p_type}'

    # Legal Rights & Provenance Classification
    y_raw = str(item.get('Year', ''))
    y_matches = re.findall(r'\b(1[4-9]\d{2}|20\d{2})\b', y_raw)
    y_val = int(y_matches[0]) if y_matches else 1900
    a_val = item.get('ArtistId', '')

    if a_val in ['picasso', 'dali', 'kahlo']:
        if a_val == 'picasso' and y_val < 1929:
            item['rightsStatus'] = 'us_public_domain'
            item['rightsStatement'] = 'Public Domain in US (Published Pre-1929); © Succession Picasso in EU'
            item['rightsBadge'] = 'US Public Domain'
            item['rightsHolder'] = 'Succession Picasso / ADAGP'
        elif a_val == 'picasso':
            item['rightsStatus'] = 'estate_protected'
            item['rightsStatement'] = '© Succession Picasso / Artists Rights Society (ARS), New York • Educational Fair Use Preview'
            item['rightsBadge'] = '© Estate Protected'
            item['rightsHolder'] = 'Succession Picasso / Artists Rights Society (ARS), New York'
        elif a_val == 'dali':
            item['rightsStatus'] = 'estate_protected'
            item['rightsStatement'] = '© Fundació Gala-Salvador Dalí / VEGAP / ARS, New York • Educational Fair Use Preview'
            item['rightsBadge'] = '© Estate Protected'
            item['rightsHolder'] = 'Fundació Gala-Salvador Dalí / VEGAP / Artists Rights Society (ARS), New York'
        else: # kahlo
            item['rightsStatus'] = 'estate_protected'
            item['rightsStatement'] = '© Banco de México Diego Rivera & Frida Kahlo Museums Trust • Educational Fair Use Preview'
            item['rightsBadge'] = '© Estate Protected'
            item['rightsHolder'] = 'Banco de México Diego Rivera & Frida Kahlo Museums Trust'
    else:
        item['rightsStatus'] = 'public_domain'
        item['rightsStatement'] = '🏛️ Public Domain Worldwide (Public Domain Mark 1.0)'
        item['rightsBadge'] = 'Public Domain'
        item['rightsHolder'] = 'Public Domain'

print(f'Total Curated Paintings: {len(curated)}')
matched_urls = sum(1 for x in curated if x['HighResUrl'])
print(f'Paintings with HighResUrl: {matched_urls}/{len(curated)}')

# Full artists dataset with concise taglines and innovations
artists_meta = [
    {
        'id': 'botticelli',
        'name': 'Sandro Botticelli',
        'slug': 'sandro-botticelli',
        'lifespan': '1445–1510',
        'epochId': 'renaissance',
        'epochName': 'Early Renaissance',
        'movement': 'Early Renaissance Florentine Humanism',
        'location': 'Florence, Medici Court',
        'epithet': 'The Poet of Early Renaissance Grace & Myth',
        'tagline': 'The poet of Medici Florence who revived classical pagan mythology and ethereal Renaissance grace.',
        'innovations': ['Mythological Revival', 'Lyrical Line', 'Neoplatonic Allegory'],
        'whyBelongs': 'Revived classical Greco-Roman mythology, introducing non-religious pagan allegories back into European high art after a millennium of strict medieval dogma. Defined the universal Western archetype of poetic, ethereal female beauty that inspired modern high-fashion aesthetics.',
        'evolutionRole': 'Rejected heavy geometric realism in favor of lyrical contour lines, decorative drapery, and graceful elongation. Bridged the Gothic tradition with Renaissance Neoplatonism, creating harmonious compositions where divine love and earthly grace merged.',
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
        'tagline': 'The universal polymath who dissolved rigid outlines into atmospheric sfumato and elevated painting to divine science.',
        'innovations': ['Sfumato Glazing', 'Pyramidal Geometry', 'Atmospheric Depth'],
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
        'tagline': 'The titan who sculpted spiritual torment, heroic defiance, and monumental power into human anatomy.',
        'innovations': ['Terribilità Dynamism', 'Anatomical Heroism', 'Sistine Fresco Mastery'],
        'whyBelongs': 'Master of epic anatomical power; redefined human musculature as the ultimate vessel of divine spiritual torment and glory. Executed the greatest fresco commissions in history across the Sistine Chapel ceiling and altar wall, entirely by his own hand.',
        'evolutionRole': 'Michelangelo viewed the human body as an architectural monument. Discarded passive tranquility in favor of terribilità—an awe-inspiring, brooding power. His figures twist through space with unprecedented kinetic energy, establishing anatomy as the central narrative medium of Western art.',
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
        'tagline': 'The outlaw genius who dragged biblical saints into dark Roman alleys under razor-sharp theatrical spotlights.',
        'innovations': ['Dramatic Tenebrism', 'Street Naturalism', 'Cinematic Contrast'],
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
        'tagline': 'The supreme chronicler of the human soul who sculpted warm golden light out of rich, atmospheric shadows.',
        'innovations': ['Sculpted Impasto', 'Psychological Introspection', 'Civic Action Staging'],
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
        'tagline': 'The optical poet of Delft who immortalized quiet domestic daylight with camera obscura perfection.',
        'innovations': ['Photographic Luminism', 'Pointillist Highlights', 'Lapis Lazuli Depth'],
        'whyBelongs': 'The Sphinx of Delft produced an exceptionally rare, precious jewel-box catalog of only ~35 surviving masterpieces. Girl with a Pearl Earring is revered globally as the \"Dutch Mona Lisa\", and The Art of Painting stands at 45.80 Megapixels as one of history\'s greatest optical triumphs.',
        'evolutionRole': 'Achieved an uncanny photographic photorealism two centuries before the camera. Employed camera obscura techniques, globular pointillistic specular highlights, and costly genuine lapis lazuli pigment to monumentalize intimate domestic rituals into timeless moments of grace.',
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
        'tagline': 'The father of Impressionism who dissolved solid forms into fleeting, vibrant optical vibrations of light.',
        'innovations': ['En Plein Air', 'Retinal Color Vibration', 'Lyrical Seriality'],
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
        'tagline': 'The torrent of raw passion who transformed thick, swirling paint into pure spiritual ecstasy and cosmic wonder.',
        'innovations': ['Expressive Impasto', 'Symbolic Emotion in Color', 'Dynamic Brush Rhythms'],
        'whyBelongs': 'The archetype of pure, uncompromised artistic devotion. Created over 2,000 artworks in a single feverish decade despite enduring profound mental anguish and extreme poverty. The Starry Night and Sunflowers are among the most celebrated visual monuments of humanity.',
        'evolutionRole': 'Liberated color and brushstrokes from literal representation, turning thick impasto paint into a dynamic direct conductor of psychic ecstasy, despair, and cosmic awe. Van Gogh became the direct spiritual forefather of German Expressionism and modern abstract art.',
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
        'tagline': 'The chronicler of existential vertigo who gave visual voice to the silent scream passing through modern nature.',
        'innovations': ['Psychic Interiority', 'Wavy Symbolic Contours', 'The Frieze of Life'],
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
        'epochName': 'Vienna Secession',
        'movement': 'Vienna Secession, Art Nouveau & Symbolism',
        'location': 'Vienna, Austria-Hungary',
        'epithet': 'The Alchemist of Gold, Sensuality & Secession',
        'tagline': 'The Vienna Secession visionary who wove erotic intimacy, Byzantine gold leaf, and modern decorative abstraction.',
        'innovations': ['Golden Leaf Mosaics', 'Symbolist Eroticism', 'Secession Modernism'],
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
        'movement': 'Cubism, Blue/Rose Periods, Modernism',
        'location': 'Malaga, Barcelona, Paris, French Riviera',
        'epithet': 'The Demiurge of 20th Century Visual Modernism',
        'tagline': 'The demiurge of the modern avant-garde who shattered 500 years of Renaissance perspective into Cubist planes.',
        'innovations': ['Cubist Perspective', 'Multifaceted Planes', 'Radical Stylistic Reinvention'],
        'whyBelongs': 'The undisputed colossus of modern art. Over seven decades, Picasso dismantled and rebuilt the visual grammar of civilization, traversing Blue, Rose, African, Cubist, Neoclassical, and Surrealist phases.',
        'evolutionRole': 'Co-founded Cubism, obliterating 500 years of Renaissance perspective by shattering three-dimensional space onto a flat surface seen from multiple vantage points simultaneously. Painted Guernica, modern history\'s greatest, most searing condemnation of fascist warfare.',
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
        'tagline': 'The wizard of the subconscious who rendered irrational, delirious dreamscapes with hyper-precise optical realism.',
        'innovations': ['Paranoiac-Critical Method', 'Double Imagery', 'Dream Photographs'],
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
        'epochName': 'Mexican Modernism',
        'movement': 'Autobiographical Surrealism & Mexicanidad',
        'location': 'Coyoacán (Mexico City), New York, Paris',
        'epithet': 'The Global Cultural Icon of Resilience & Identity',
        'tagline': 'The global icon of resilience who painted not dreams, but the raw, mythic reality of her own beating heart.',
        'innovations': ['Autobiographical Surrealism', 'Mexicanidad Folk Heritage', 'Unflinching Vulnerability'],
        'whyBelongs': 'Has achieved unprecedented global cultural and feminist iconography (\"Fridamania\"). Transmuted profound chronic physical pain, personal heartbreak, and indigenous Mexican heritage into unflinching, mythic autobiographical masterpieces (The Two Fridas, The Broken Column).',
        'evolutionRole': 'Rejected orthodox European Surrealism to paint her direct internal reality (\"I never painted dreams. I painted my own reality\"). Blended traditional Mexican retablo folk devotional painting with raw anatomical, psychological, and matriarchal symbolism.',
        'totalWorksCataloged': 100,
        'curatedCount': sum(1 for c in curated if c['Artist'] == 'Frida Kahlo'),
        'heroImage': 'artist_paintings/Top_Celebrity_Masterpieces/75_Frida_Kahlo_-_The_Two_Fridas.jpg'
    }
]

# Curated Spotlight Masterpieces for Hero rotation
spotlight_candidates = [
    '06_Leonardo_da_Vinci_-_Mona_Lisa.jpg',
    '36_Johannes_Vermeer_-_The_Art_of_Painting.jpg',
    '46_Vincent_van_Gogh_-_The_Starry_Night.jpg',
    '57_Gustav_Klimt_-_The_Kiss.jpg',
    '14_Michelangelo_-_The_Creation_of_Adam.jpg',
    '34_Johannes_Vermeer_-_Girl_with_a_Pearl_Earring.jpg',
    '39_Claude_Monet_-_Impression,_Sunrise.jpg',
    '75_Frida_Kahlo_-_The_Two_Fridas.jpg'
]

spotlights = []
for c in curated:
    if c['FileName'] in spotlight_candidates:
        spotlights.append(c)

epochs = [
    {'id': 'all', 'name': 'All Eras (1470–1954)', 'short': 'All Eras'},
    {'id': 'renaissance', 'name': 'Renaissance Humanism (1470–1564)', 'short': 'Renaissance'},
    {'id': 'baroque', 'name': 'Baroque & Dutch Golden Age (1595–1675)', 'short': 'Baroque'},
    {'id': 'impressionism', 'name': '19th C. Impressionism (1872–1893)', 'short': 'Impressionism'},
    {'id': 'expressionism', 'name': 'Expressionism & Secession (1893–1918)', 'short': 'Expressionism'},
    {'id': 'modernism', 'name': '20th C. Modernism (1901–1954)', 'short': 'Modernism'}
]

# Assign epoch IDs to curated items
for item in curated:
    for a in artists_meta:
        if a['id'] == item['ArtistId']:
            item['EpochId'] = a['epochId']
            break

# The 5-Minute Guided Tour: 10 Turning Points in 500 Years of Art History
guided_tour = [
    {
        'step': 1,
        'year': '1485',
        'epoch': 'Early Renaissance',
        'artist': 'Sandro Botticelli',
        'title': 'The Birth of Venus',
        'fileName': '01_Sandro_Botticelli_-_The_Birth_of_Venus.jpg',
        'headline': 'The Rebirth of Myth & Classical Beauty',
        'story': 'After a thousand years of medieval gloom, Botticelli resurrected classical poetry and graceful lyrical contours. The goddess of love floats ashore on a giant seashell, inaugurating the Italian Renaissance.',
        'breakthrough': 'Humanist revival of pagan mythology & lyrical anatomy'
    },
    {
        'step': 2,
        'year': '1503',
        'epoch': 'High Renaissance',
        'artist': 'Leonardo da Vinci',
        'title': 'Mona Lisa',
        'fileName': '06_Leonardo_da_Vinci_-_Mona_Lisa.jpg',
        'headline': 'The Invention of Living Sfumato Shadows',
        'story': 'Leonardo banished harsh medieval outlines, blending layers of translucent glaze like smoke ("sfumato"). The result was a living, breathing presence whose shifting smile redefined human psychology in art.',
        'breakthrough': 'Sfumato (smoke-like soft shading) & psychological presence'
    },
    {
        'step': 3,
        'year': '1512',
        'epoch': 'High Renaissance',
        'artist': 'Michelangelo',
        'title': 'The Creation of Adam',
        'fileName': '14_Michelangelo_-_The_Creation_of_Adam.jpg',
        'headline': 'Anatomical Grandeur & The Divine Spark',
        'story': 'Suspended on scaffolding beneath the Vatican ceiling, Michelangelo sculpted God and man in paint. The near-touch of two fingertips charged the Sistine Chapel with electrifying human potential.',
        'breakthrough': 'Sculptural monumentality & heroic human anatomy'
    },
    {
        'step': 4,
        'year': '1600',
        'epoch': 'Baroque',
        'artist': 'Caravaggio',
        'title': 'The Calling of Saint Matthew',
        'fileName': '22_Caravaggio_-_The_Calling_of_Saint_Matthew.jpg',
        'headline': 'Theatrical Tenebrism: Miracles in Gritty Tavern Light',
        'story': 'Caravaggio dragged sacred art off divine pedestals and into dusty Roman taverns. A harsh, cinematic beam of light pierces pitch darkness, capturing the exact second of divine awakening.',
        'breakthrough': 'Tenebrism (violent light vs. shadow) & street realism'
    },
    {
        'step': 5,
        'year': '1642',
        'epoch': 'Dutch Golden Age',
        'artist': 'Rembrandt van Rijn',
        'title': 'The Night Watch',
        'fileName': '27_Rembrandt_-_The_Night_Watch.jpg',
        'headline': 'Explosive Motion & Golden Dutch Impasto',
        'story': 'Refusing to paint a stiff, orderly military lineup, Rembrandt threw the Amsterdam civic guard into kinetic chaos. Thick golden impasto catches the light as the captain marches forward right off the canvas.',
        'breakthrough': 'Dynamic group action & golden psychological impasto'
    },
    {
        'step': 6,
        'year': '1665',
        'epoch': 'Dutch Golden Age',
        'artist': 'Johannes Vermeer',
        'title': 'Girl with a Pearl Earring',
        'fileName': '34_Johannes_Vermeer_-_Girl_with_a_Pearl_Earring.jpg',
        'headline': 'Sacred Domestic Stillness & Pure Lapis Lazuli',
        'story': 'Working quietly in Delft, Vermeer elevated quiet moments into timeless sacraments. With a single glistening highlight on a teardrop pearl and liquid highlights on parting lips, he captured eternity in an instant.',
        'breakthrough': 'Optical camera-obscura fidelity & luminous stillness'
    },
    {
        'step': 7,
        'year': '1872',
        'epoch': 'Impressionism',
        'artist': 'Claude Monet',
        'title': 'Impression, Sunrise',
        'fileName': '39_Claude_Monet_-_Impression,_Sunrise.jpg',
        'headline': 'The Plein-Air Revolution: Painting Fleeting Sunlight',
        'story': 'Stepping out of stuffy academic studios onto the misty harbor of Le Havre, Monet captured the orange sun bleeding into morning fog with rapid, broken brushstrokes. Critics coined "Impressionism" as an insult; it launched modern art.',
        'breakthrough': 'Plein-air painting, optical vibration, & pure atmospheric light'
    },
    {
        'step': 8,
        'year': '1889',
        'epoch': 'Post-Impressionism',
        'artist': 'Vincent van Gogh',
        'title': 'The Starry Night',
        'fileName': '46_Vincent_van_Gogh_-_The_Starry_Night.jpg',
        'headline': 'Painting Emotion Instead of Reality',
        'story': 'Gazing from his asylum window in Saint-Rémy, Van Gogh didn\'t paint the night sky as it appeared—he painted the cosmic vortex of his soul. Swirling impasto rhythms transformed painting from observation into raw spiritual expression.',
        'breakthrough': 'Post-Impressionist subjective emotion through rhythmic impasto'
    },
    {
        'step': 9,
        'year': '1893',
        'epoch': 'Expressionism',
        'artist': 'Edvard Munch',
        'title': 'The Scream',
        'fileName': '52_Edvard_Munch_-_The_Scream.jpg',
        'headline': 'The Birth of Expressionism & Modern Anxiety',
        'story': 'Walking across a bridge at sunset, Munch sensed "an infinite scream passing through nature." The blood-red sky, melting contours, and sexless skull-like figure captured the existential dread of modern civilization.',
        'breakthrough': 'Psychic symbolism & the birth of 20th-century Expressionism'
    },
    {
        'step': 10,
        'year': '1937',
        'epoch': 'Modernism / Cubism',
        'artist': 'Pablo Picasso',
        'title': 'Guernica',
        'fileName': '62_Pablo_Picasso_-_Guernica.jpg',
        'headline': 'Cubism Unleashed: The Ultimate Anti-War Scream',
        'story': 'Horrified by the saturation bombing of a defenseless Basque town, Picasso shattered physical space into monochromatic black, white, and grey geometric knives. The screaming horse and weeping mother became humanity\'s universal protest against cruelty.',
        'breakthrough': 'Synthetic Cubism weaponized into monumental political protest'
    }
]

# Attach resolved image URLs to guided tour stops with strict validation
for stop in guided_tour:
    matched = None
    for item in curated:
        if item['FileName'] == stop['fileName']:
            matched = item
            break
    if not matched:
        for item in curated:
            if stop['title'].lower() in item['Title'].lower():
                matched = item
                stop['fileName'] = item['FileName']
                break
    if not matched or not matched.get('HighResUrl'):
        raise ValueError(f"CRITICAL: Failed to resolve HighResUrl for tour milestone: {stop['title']}")
    
    stop['HighResUrl'] = matched['HighResUrl']
    stop['LocalRelativePath'] = matched['LocalRelativePath']
    stop['Megapixels'] = matched['Megapixels']
    stop['Museum'] = matched['Museum']
    stop['physicalDimensionsStr'] = matched.get('physicalDimensionsStr', '')


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

full_data = {
    'stats': stats,
    'epochs': epochs,
    'spotlights': spotlights,
    'guidedTour': guided_tour,
    'artists': artists_meta,
    'masterpieces': curated,
    'topPopular': popular[:50]
}

with open('data/pantheon_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(full_data, f, indent=2, ensure_ascii=False)

js_content = '/**\n * Pantheon Art History & Masterpiece Catalog\n * Auto-generated dataset for GitHub Pages exhibition\n */\n'
js_content += 'window.PANTHEON_DATA = ' + json.dumps(full_data, indent=2, ensure_ascii=False) + ';\n'

with open('js/catalog-data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print('Successfully re-compiled data/pantheon_catalog.json and js/catalog-data.js with Physical Dimensions and Guided Tour!')

