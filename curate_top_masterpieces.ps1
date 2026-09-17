<#
.SYNOPSIS
    Curate Top Celebrated Masterpieces for the 7 Celebrity Masters.
.DESCRIPTION
    Selects, cross-references, and organizes the highest-resolution, most iconic
    paintings by Claude Monet, Vincent van Gogh, Leonardo da Vinci, Michelangelo,
    Rembrandt, Salvador Dali, and Pablo Picasso into a premier curated collection.
#>

[CmdletBinding()]
param(
    [string]$SourceDir = "artist_paintings",
    [string]$Top100Dir = "paintings_output",
    [string]$OutputDir = "artist_paintings\Top_Celebrity_Masterpieces"
)

$ErrorActionPreference = "Continue"

$resolvedSource = [System.IO.Path]::GetFullPath($SourceDir)
$resolvedTop100 = [System.IO.Path]::GetFullPath($Top100Dir)
$resolvedOut    = [System.IO.Path]::GetFullPath($OutputDir)

if (-not (Test-Path $resolvedOut)) {
    New-Item -ItemType Directory -Path $resolvedOut -Force | Out-Null
}

Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host " CURATING TOP CELEBRATED MASTERPIECES ACROSS 7 CELEBRITY MASTERS" -ForegroundColor Yellow
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host "Source Artist Dir : $resolvedSource"
Write-Host "Top 100 Source    : $resolvedTop100"
Write-Host "Curated Output    : $resolvedOut"
Write-Host ""

# Masterpiece dictionary defining key search patterns & historical metadata
$masterpieceSignatures = @(
    # Leonardo da Vinci
    @{ Artist = "Leonardo da Vinci"; Slug = "Leonardo_da_Vinci"; Title = "Mona Lisa"; Patterns = @("*Mona_Lisa*"); Year = "1503-1519"; Museum = "Musée du Louvre, Paris" },
    @{ Artist = "Leonardo da Vinci"; Slug = "Leonardo_da_Vinci"; Title = "The Last Supper"; Patterns = @("*The_Last_Supper*"); Year = "1495-1498"; Museum = "Santa Maria delle Grazie, Milan" },
    @{ Artist = "Leonardo da Vinci"; Slug = "Leonardo_da_Vinci"; Title = "Lady with an Ermine"; Patterns = @("*Lady_with_an_Ermine*"); Year = "1489-1490"; Museum = "Czartoryski Museum, Kraków" },
    @{ Artist = "Leonardo da Vinci"; Slug = "Leonardo_da_Vinci"; Title = "Vitruvian Man"; Patterns = @("*proportions_of_the_human_figure*", "*Vitruvian*"); Year = "1490"; Museum = "Gallerie dell'Accademia, Venice" },
    @{ Artist = "Leonardo da Vinci"; Slug = "Leonardo_da_Vinci"; Title = "Portrait of Ginevra de' Benci"; Patterns = @("*Ginevra*"); Year = "1474-1478"; Museum = "National Gallery of Art, Washington D.C." },
    @{ Artist = "Leonardo da Vinci"; Slug = "Leonardo_da_Vinci"; Title = "Annunciation"; Patterns = @("*Annunciation*"); Year = "1472-1475"; Museum = "Uffizi Gallery, Florence" },
    @{ Artist = "Leonardo da Vinci"; Slug = "Leonardo_da_Vinci"; Title = "The Virgin and Child with St. Anne"; Patterns = @("*Virgin_and_Child_with_St._Anne*"); Year = "1503-1519"; Museum = "Musée du Louvre, Paris" },
    @{ Artist = "Leonardo da Vinci"; Slug = "Leonardo_da_Vinci"; Title = "St. John the Baptist"; Patterns = @("*John_the_Baptist*"); Year = "1513-1516"; Museum = "Musée du Louvre, Paris" },

    # Michelangelo
    @{ Artist = "Michelangelo"; Slug = "Michelangelo"; Title = "The Creation of Adam"; Patterns = @("*Creation_of_Adam*"); Year = "1512"; Museum = "Sistine Chapel, Vatican Museums" },
    @{ Artist = "Michelangelo"; Slug = "Michelangelo"; Title = "The Last Judgement"; Patterns = @("*The_Last_Judgement*"); Year = "1536-1541"; Museum = "Sistine Chapel, Vatican Museums" },
    @{ Artist = "Michelangelo"; Slug = "Michelangelo"; Title = "Sistine Chapel: The Flood"; Patterns = @("*The_Flood*"); Year = "1508-1512"; Museum = "Sistine Chapel, Vatican Museums" },
    @{ Artist = "Michelangelo"; Slug = "Michelangelo"; Title = "Sistine Chapel: Libyan Sibyl"; Patterns = @("*Libyan_Sibyl*"); Year = "1511"; Museum = "Sistine Chapel, Vatican Museums" },
    @{ Artist = "Michelangelo"; Slug = "Michelangelo"; Title = "Sistine Chapel: Cumaean Sibyl"; Patterns = @("*Cumaean_Sibyl*"); Year = "1510"; Museum = "Sistine Chapel, Vatican Museums" },
    @{ Artist = "Michelangelo"; Slug = "Michelangelo"; Title = "Sistine Chapel: David and Goliath"; Patterns = @("*David_and_Goliath*"); Year = "1509"; Museum = "Sistine Chapel, Vatican Museums" },
    @{ Artist = "Michelangelo"; Slug = "Michelangelo"; Title = "The Entombment"; Patterns = @("*The_Entombment*"); Year = "1500-1501"; Museum = "National Gallery, London" },
    @{ Artist = "Michelangelo"; Slug = "Michelangelo"; Title = "Pieta (Studies)"; Patterns = @("*Pieta*"); Year = "1498-1540"; Museum = "St. Peter's Basilica / Vatican" },

    # Rembrandt van Rijn
    @{ Artist = "Rembrandt"; Slug = "Rembrandt"; Title = "The Night Watch"; Patterns = @("*The_Nightwatch*", "*Night_Watch*"); Year = "1642"; Museum = "Rijksmuseum, Amsterdam" },
    @{ Artist = "Rembrandt"; Slug = "Rembrandt"; Title = "The Anatomy Lesson of Dr. Nicolaes Tulp"; Patterns = @("*The_Anatomy_Lesson_of_Dr._Nicolaes_Tulp*"); Year = "1632"; Museum = "Mauritshuis, The Hague" },
    @{ Artist = "Rembrandt"; Slug = "Rembrandt"; Title = "The Storm on the Sea of Galilee"; Patterns = @("*Storm_on_the_Sea_of_Galilee*"); Year = "1633"; Museum = "Isabella Stewart Gardner Museum" },
    @{ Artist = "Rembrandt"; Slug = "Rembrandt"; Title = "Self-Portrait at the Age of 63"; Patterns = @("*Self-portrait_in_at_the_Age_of_63*"); Year = "1669"; Museum = "National Gallery, London" },
    @{ Artist = "Rembrandt"; Slug = "Rembrandt"; Title = "Self-Portrait at the Age of 34"; Patterns = @("*Self-portrait_at_the_Age_of_34*"); Year = "1640"; Museum = "National Gallery, London" },
    @{ Artist = "Rembrandt"; Slug = "Rembrandt"; Title = "Portrait of Saskia van Uylenburgh"; Patterns = @("*Portrait_of_Saskia_van_Uylenburgh*"); Year = "1635"; Museum = "National Gallery of Art, Washington" },
    @{ Artist = "Rembrandt"; Slug = "Rembrandt"; Title = "Self-Portrait in Studio Attire"; Patterns = @("*Self-portrait_in_studio_attire*"); Year = "1655"; Museum = "Kunsthistorisches Museum, Vienna" },

    # Salvador Dali
    @{ Artist = "Salvador Dali"; Slug = "Salvador_Dali"; Title = "The Persistence of Memory"; Patterns = @("*The_Persistence_of_Memory*"); Year = "1931"; Museum = "Museum of Modern Art, New York" },
    @{ Artist = "Salvador Dali"; Slug = "Salvador_Dali"; Title = "The Great Masturbator"; Patterns = @("*The_Great_Masturbator*"); Year = "1929"; Museum = "Museo Reina Sofía, Madrid" },
    @{ Artist = "Salvador Dali"; Slug = "Salvador_Dali"; Title = "Swans Reflecting Elephants"; Patterns = @("*Swans_Reflecting_Elephants*"); Year = "1937"; Museum = "Private Collection" },
    @{ Artist = "Salvador Dali"; Slug = "Salvador_Dali"; Title = "The Metamorphosis of Narcissus"; Patterns = @("*The_Metamorphosis_of_Narcissus*"); Year = "1937"; Museum = "Tate Modern, London" },
    @{ Artist = "Salvador Dali"; Slug = "Salvador_Dali"; Title = "The Temptation of St. Anthony"; Patterns = @("*The_Temptation_of_St._Anthony*"); Year = "1946"; Museum = "Royal Museums of Fine Arts of Belgium" },
    @{ Artist = "Salvador Dali"; Slug = "Salvador_Dali"; Title = "Crucifixion (Corpus Hypercubicus)"; Patterns = @("*Crucifixion_(Corpus_Hypercubicus)*"); Year = "1954"; Museum = "Metropolitan Museum of Art, New York" },
    @{ Artist = "Salvador Dali"; Slug = "Salvador_Dali"; Title = "Galatea of the Spheres"; Patterns = @("*Galatea_of_the_Spheres*"); Year = "1952"; Museum = "Dalí Theatre and Museum, Figueres" },
    @{ Artist = "Salvador Dali"; Slug = "Salvador_Dali"; Title = "The Disintegration of the Persistence of Memory"; Patterns = @("*Disintegration_of_the_Persisten*"); Year = "1954"; Museum = "Salvador Dalí Museum, St. Petersburg, FL" },

    # Claude Monet
    @{ Artist = "Claude Monet"; Slug = "Claude_Monet"; Title = "Impression, Sunrise"; Patterns = @("*Impression,_sunrise*"); Year = "1872"; Museum = "Musée Marmottan Monet, Paris" },
    @{ Artist = "Claude Monet"; Slug = "Claude_Monet"; Title = "Water Lilies (The Clouds)"; Patterns = @("*Water_Lilies,_The_Clouds*", "*Water_Lilies*"); Year = "1903"; Museum = "Musée de l'Orangerie, Paris" },
    @{ Artist = "Claude Monet"; Slug = "Claude_Monet"; Title = "The Japanese Bridge (Water-Lily Pond)"; Patterns = @("*The_Japanese_Bridge*(The_Water-Lily*"); Year = "1899"; Museum = "National Gallery of Art, Washington" },
    @{ Artist = "Claude Monet"; Slug = "Claude_Monet"; Title = "Camille Monet and a Child in the Garden"; Patterns = @("*Camille_Monet_and_a_Child*"); Year = "1875"; Museum = "Museum of Fine Arts, Boston" },
    @{ Artist = "Claude Monet"; Slug = "Claude_Monet"; Title = "Women in the Garden"; Patterns = @("*Women_in_the_garden*"); Year = "1866"; Museum = "Musée d'Orsay, Paris" },
    @{ Artist = "Claude Monet"; Slug = "Claude_Monet"; Title = "Waterloo Bridge, Sunlight Effect"; Patterns = @("*Waterloo_Bridge,_Sunlight_Effect*"); Year = "1903"; Museum = "Art Institute of Chicago" },
    @{ Artist = "Claude Monet"; Slug = "Claude_Monet"; Title = "The Water Lily Pond and Bridge"; Patterns = @("*The_Water_Lily_Pond_and_Bridge*"); Year = "1900"; Museum = "Princeton University Art Museum" },

    # Vincent van Gogh
    @{ Artist = "Vincent van Gogh"; Slug = "Vincent_van_Gogh"; Title = "The Starry Night"; Patterns = @("*The_Starry_Night*"); Year = "1889"; Museum = "Museum of Modern Art, New York" },
    @{ Artist = "Vincent van Gogh"; Slug = "Vincent_van_Gogh"; Title = "Still Life: Vase with Fifteen Sunflowers"; Patterns = @("*Vase_with_Fifteen_Sunf*", "*Sunflowers*"); Year = "1888"; Museum = "National Gallery, London" },
    @{ Artist = "Vincent van Gogh"; Slug = "Vincent_van_Gogh"; Title = "The Potato Eaters"; Patterns = @("*The_Potato_Eaters*"); Year = "1885"; Museum = "Van Gogh Museum, Amsterdam" },
    @{ Artist = "Vincent van Gogh"; Slug = "Vincent_van_Gogh"; Title = "Peasant Woman Lifting Potatoes"; Patterns = @("*Peasant_Woman_Lifting_Potatoes*"); Year = "1885"; Museum = "Van Gogh Museum, Amsterdam" },
    @{ Artist = "Vincent van Gogh"; Slug = "Vincent_van_Gogh"; Title = "Still Life with Three Birds' Nests"; Patterns = @("*Still_Life_with_Three_Birds_Nests*"); Year = "1885"; Museum = "Kröller-Müller Museum" },
    @{ Artist = "Vincent van Gogh"; Slug = "Vincent_van_Gogh"; Title = "Portrait of a Woman with a Red Ribbon"; Patterns = @("*Portrait_of_a_Woman_with_a_Red_Ribbon*"); Year = "1885"; Museum = "Van Gogh Museum, Amsterdam" },

    # Pablo Picasso
    @{ Artist = "Pablo Picasso"; Slug = "Pablo_Picasso"; Title = "Guernica"; Patterns = @("*Guernica*"); Year = "1937"; Museum = "Museo Reina Sofía, Madrid" },
    @{ Artist = "Pablo Picasso"; Slug = "Pablo_Picasso"; Title = "The Old Blind Guitarist"; Patterns = @("*The_old_blind_guitarist*"); Year = "1903"; Museum = "Art Institute of Chicago" },
    @{ Artist = "Pablo Picasso"; Slug = "Pablo_Picasso"; Title = "Self-Portrait (1907)"; Patterns = @("*Self-Portrait*"); Year = "1907"; Museum = "National Gallery, Prague" },
    @{ Artist = "Pablo Picasso"; Slug = "Pablo_Picasso"; Title = "Portrait of Dora Maar"; Patterns = @("*Portrait_of_Dora_Maar*"); Year = "1937"; Museum = "Musée Picasso, Paris" },
    @{ Artist = "Pablo Picasso"; Slug = "Pablo_Picasso"; Title = "Child with a Dove"; Patterns = @("*Child_with_dove*"); Year = "1901"; Museum = "National Gallery, London" },

    # Johannes Vermeer
    @{ Artist = "Johannes Vermeer"; Slug = "Johannes_Vermeer"; Title = "Girl with a Pearl Earring"; Patterns = @("*Girl_with_a_Pearl_Earring*"); Year = "1665"; Museum = "Mauritshuis, The Hague" },
    @{ Artist = "Johannes Vermeer"; Slug = "Johannes_Vermeer"; Title = "The Milkmaid"; Patterns = @("*The_Milkmaid*", "*milkmaid*"); Year = "1657-1658"; Museum = "Rijksmuseum, Amsterdam" },
    @{ Artist = "Johannes Vermeer"; Slug = "Johannes_Vermeer"; Title = "The Art of Painting"; Patterns = @("*The_Art_of_Painting*", "*Allegory_of_Painting*"); Year = "1666-1668"; Museum = "Kunsthistorisches Museum, Vienna" },
    @{ Artist = "Johannes Vermeer"; Slug = "Johannes_Vermeer"; Title = "The Astronomer"; Patterns = @("*The_astronomer*"); Year = "1668"; Museum = "Musée du Louvre, Paris" },
    @{ Artist = "Johannes Vermeer"; Slug = "Johannes_Vermeer"; Title = "Young Woman with a Pearl Necklace"; Patterns = @("*Young_Woman_with_a_Pearl_Necklace*"); Year = "1662-1664"; Museum = "Gemäldegalerie, Berlin" },

    # Frida Kahlo
    @{ Artist = "Frida Kahlo"; Slug = "Frida_Kahlo"; Title = "The Two Fridas"; Patterns = @("*The_Two_Fridas*"); Year = "1939"; Museum = "Museo de Arte Moderno, Mexico City" },
    @{ Artist = "Frida Kahlo"; Slug = "Frida_Kahlo"; Title = "The Broken Column"; Patterns = @("*The_Broken_Column*"); Year = "1944"; Museum = "Museo Dolores Olmedo, Mexico City" },
    @{ Artist = "Frida Kahlo"; Slug = "Frida_Kahlo"; Title = "Viva la Vida, Watermelons"; Patterns = @("*Viva_la_Vida*"); Year = "1954"; Museum = "Frida Kahlo Museum, Mexico City" },
    @{ Artist = "Frida Kahlo"; Slug = "Frida_Kahlo"; Title = "Henry Ford Hospital"; Patterns = @("*Henry_Ford_Hospital*"); Year = "1932"; Museum = "Museo Dolores Olmedo, Mexico City" },
    @{ Artist = "Frida Kahlo"; Slug = "Frida_Kahlo"; Title = "My Birth"; Patterns = @("*My_Birth*"); Year = "1932"; Museum = "Private Collection" },

    # Caravaggio
    @{ Artist = "Caravaggio"; Slug = "Caravaggio"; Title = "The Calling of Saint Matthew"; Patterns = @("*The_Calling_of_Saint_Matthew*", "*Calling_of_Saint_Matthew*"); Year = "1599-1600"; Museum = "San Luigi dei Francesi, Rome" },
    @{ Artist = "Caravaggio"; Slug = "Caravaggio"; Title = "The Martyrdom of Saint Matthew"; Patterns = @("*The_Martyrdom_of_Saint_Matthew*"); Year = "1599-1600"; Museum = "San Luigi dei Francesi, Rome" },
    @{ Artist = "Caravaggio"; Slug = "Caravaggio"; Title = "Judith Beheading Holofernes"; Patterns = @("*Judith_Beheading_Holofernes*", "*Judith*"); Year = "1598-1599"; Museum = "Gallerie Nazionali d'Arte Antica, Rome" },
    @{ Artist = "Caravaggio"; Slug = "Caravaggio"; Title = "Bacchus"; Patterns = @("*Bacchus*"); Year = "1595"; Museum = "Uffizi Gallery, Florence" },
    @{ Artist = "Caravaggio"; Slug = "Caravaggio"; Title = "David with the Head of Goliath"; Patterns = @("*David_with_the_Head_of_Goliath*", "*David*"); Year = "1609-1610"; Museum = "Borghese Gallery, Rome" },

    # Gustav Klimt
    @{ Artist = "Gustav Klimt"; Slug = "Gustav_Klimt"; Title = "The Kiss"; Patterns = @("*The_Kiss*"); Year = "1907-1908"; Museum = "Österreichische Galerie Belvedere, Vienna" },
    @{ Artist = "Gustav Klimt"; Slug = "Gustav_Klimt"; Title = "Portrait of Adele Bloch-Bauer I"; Patterns = @("*Adele_Bloch-Bauer*"); Year = "1907"; Museum = "Neue Galerie, New York" },
    @{ Artist = "Gustav Klimt"; Slug = "Gustav_Klimt"; Title = "Judith and the Head of Holofernes"; Patterns = @("*Judith*"); Year = "1901"; Museum = "Österreichische Galerie Belvedere, Vienna" },
    @{ Artist = "Gustav Klimt"; Slug = "Gustav_Klimt"; Title = "Portrait of Emilie Flöge"; Patterns = @("*Portrait_of_Emilie*"); Year = "1902"; Museum = "Wien Museum, Vienna" },
    @{ Artist = "Gustav Klimt"; Slug = "Gustav_Klimt"; Title = "The Dancer"; Patterns = @("*The_dancer*"); Year = "1916-1918"; Museum = "Neue Galerie, New York" },

    # Edvard Munch
    @{ Artist = "Edvard Munch"; Slug = "Edvard_Munch"; Title = "The Scream"; Patterns = @("*The_Scream*"); Year = "1893"; Museum = "National Gallery of Norway, Oslo" },
    @{ Artist = "Edvard Munch"; Slug = "Edvard_Munch"; Title = "Madonna"; Patterns = @("*Madonna*"); Year = "1894"; Museum = "Munch Museum, Oslo" },
    @{ Artist = "Edvard Munch"; Slug = "Edvard_Munch"; Title = "The Dance of Life"; Patterns = @("*The_Dance_of_Life*", "*Dance_of_Life*"); Year = "1899-1900"; Museum = "National Gallery of Norway, Oslo" },
    @{ Artist = "Edvard Munch"; Slug = "Edvard_Munch"; Title = "The Sick Child"; Patterns = @("*The_Sick_Child*", "*Sick_Child*"); Year = "1907"; Museum = "Tate Modern, London" },
    @{ Artist = "Edvard Munch"; Slug = "Edvard_Munch"; Title = "Eye in Eye"; Patterns = @("*Eye_in_Eye*"); Year = "1894"; Museum = "Munch Museum, Oslo" },

    # Sandro Botticelli
    @{ Artist = "Sandro Botticelli"; Slug = "Sandro_Botticelli"; Title = "The Birth of Venus"; Patterns = @("*The_Birth_of_Venus*", "*Birth_of_Venus*"); Year = "1485-1486"; Museum = "Uffizi Gallery, Florence" },
    @{ Artist = "Sandro Botticelli"; Slug = "Sandro_Botticelli"; Title = "The Spring (Primavera)"; Patterns = @("*The_Spring*", "*Primavera*"); Year = "1477-1482"; Museum = "Uffizi Gallery, Florence" },
    @{ Artist = "Sandro Botticelli"; Slug = "Sandro_Botticelli"; Title = "The Mystical Nativity"; Patterns = @("*The_Mystical_Nativity*"); Year = "1500"; Museum = "National Gallery, London" },
    @{ Artist = "Sandro Botticelli"; Slug = "Sandro_Botticelli"; Title = "The Story of Nastagio Degli Onesti"; Patterns = @("*The_Story_of_Nastagio_Degli_Onesti*"); Year = "1483"; Museum = "Museo del Prado, Madrid" },
    @{ Artist = "Sandro Botticelli"; Slug = "Sandro_Botticelli"; Title = "Calumny of Apelles"; Patterns = @("*Calumny_of_Apelles*"); Year = "1494-1495"; Museum = "Uffizi Gallery, Florence" }
)

$curatedList = [System.Collections.Generic.List[PSObject]]::new()
$curatedIndex = 1

foreach ($m in $masterpieceSignatures) {
    $foundFile = $null
    
    # Check 1: In top100 folder
    foreach ($pat in $m.Patterns) {
        $matches = Get-ChildItem -Path $resolvedTop100 -Filter $pat -ErrorAction SilentlyContinue
        if ($matches -and $matches.Count -gt 0) {
            $foundFile = $matches[0]
            break
        }
    }

    # Check 2: In artist specific folder
    if (-not $foundFile) {
        $artistFolder = Join-Path $resolvedSource $m.Slug
        if (Test-Path $artistFolder) {
            foreach ($pat in $m.Patterns) {
                $matches = Get-ChildItem -Path $artistFolder -Filter $pat -ErrorAction SilentlyContinue
                if ($matches -and $matches.Count -gt 0) {
                    # Pick largest file if multiple
                    $foundFile = $matches | Sort-Object Length -Descending | Select-Object -First 1
                    break
                }
            }
        }
    }

    if ($foundFile) {
        $cleanArtist = ($m.Artist -replace '\s+', '_')
        $cleanTitle  = ($m.Title -replace '[^\w\-]', '_') -replace '_+', '_'
        $ext = $foundFile.Extension
        $destFileName = ('{0:D2}_{1}_-_{2}{3}' -f $curatedIndex, $cleanArtist, $cleanTitle, $ext)
        $destPath = Join-Path $resolvedOut $destFileName

        Copy-Item -LiteralPath $foundFile.FullName -Destination $destPath -Force

        $itemSize = (Get-Item $destPath).Length
        $sizeMB = [Math]::Round($itemSize / 1048576.0, 2)

        # Extract resolution from filename if present
        $w = 0
        $h = 0
        $mp = 0.0
        if ($foundFile.Name -match '(\d+)x(\d+)') {
            $w = [int]$matches[1]
            $h = [int]$matches[2]
            $mp = [Math]::Round(($w * $h) / 1000000.0, 2)
        }

        $obj = [PSCustomObject]@{
            CuratedIndex  = $curatedIndex
            Artist        = $m.Artist
            Title         = $m.Title
            Year          = $m.Year
            Museum        = $m.Museum
            Width         = $w
            Height        = $h
            Megapixels    = $mp
            FileSizeBytes = $itemSize
            FileSizeMB    = $sizeMB
            FileName      = $destFileName
            SourcePath    = $foundFile.FullName
        }

        $curatedList.Add($obj)
        Write-Host ('  [{0:D2}] Curated: {1} - "{2}" ({3} MB, {4}x{5})' -f $curatedIndex, $m.Artist, $m.Title, $sizeMB, $w, $h) -ForegroundColor Green
        $curatedIndex++
    } else {
        Write-Host ('  [--] Not yet downloaded: {0} - "{1}"' -f $m.Artist, $m.Title) -ForegroundColor Gray
    }
}

$jsonOut = Join-Path $resolvedOut "curated_masterpieces.json"
$csvOut  = Join-Path $resolvedOut "curated_masterpieces.csv"

$curatedList | ConvertTo-Json -Depth 4 | Out-File -FilePath $jsonOut -Encoding utf8
$curatedList | Export-Csv -Path $csvOut -NoTypeInformation -Encoding utf8

Write-Host ""
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host " CURATION COMPLETE" -ForegroundColor Yellow
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host "Total Curated Masterpieces : $($curatedList.Count)"
Write-Host "JSON Database              : $jsonOut"
Write-Host "CSV Database               : $csvOut"
Write-Host ("=" * 75) -ForegroundColor Cyan
