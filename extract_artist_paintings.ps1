<#
.SYNOPSIS
    Extract All Paintings by Historic Public Domain Masters.
.DESCRIPTION
    Queries cultural heritage catalog endpoints, extracts complete catalogs of their works,
    resolves full-resolution master images, organizes them into per-artist subfolders,
    and generates detailed JSON/CSV metadata.
.PARAMETER Artists
    List of artist slugs. Default: 10 Historic Public Domain Titans.
.PARAMETER OutputDir
    Root output directory (default: "artist_paintings").
.PARAMETER MaxPerArtist
    Maximum paintings to download per artist (0 = ALL paintings).
.PARAMETER Concurrency
    Concurrent download worker count (default: 8).
.PARAMETER MetadataOnly
    Compile and export metadata only without downloading image files.
#>

[CmdletBinding()]
param(
    [string[]]$Artists = @(
        'leonardo-da-vinci',
        'michelangelo',
        'rembrandt',
        'claude-monet',
        'vincent-van-gogh',
        'johannes-vermeer',
        'sandro-botticelli',
        'caravaggio',
        'gustav-klimt',
        'edvard-munch'
    ),
    [string]$OutputDir = "artist_paintings",
    [int]$MaxPerArtist = 0,
    [int]$Concurrency = 8,
    [switch]$MetadataOnly
)

if ($Artists.Count -eq 1 -and $Artists[0] -match ',') {
    $Artists = $Artists[0] -split ',' | ForEach-Object { $_.Trim() }
}

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$resolvedRoot = [System.IO.Path]::GetFullPath($OutputDir)
if (-not (Test-Path -Path $resolvedRoot)) {
    New-Item -ItemType Directory -Path $resolvedRoot -Force | Out-Null
}

Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host " CELEBRITY MASTER ARTISTS - FULL CATALOG EXTRACTOR" -ForegroundColor Yellow
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host "Target Artists : $($Artists -join ', ')"
Write-Host "Output Root    : $resolvedRoot"
Write-Host "Max Per Artist : $(if ($MaxPerArtist -eq 0) { 'ALL Works' } else { $MaxPerArtist })"
Write-Host "Metadata Only  : $MetadataOnly"
Write-Host ""

$headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    "Accept"     = "application/json, text/html, */*"
    "Referer"    = "https://www.wikiart.org/"
}

function Sanitize-FileName([string]$name, [int]$maxLen = 45) {
    if ([string]::IsNullOrWhiteSpace($name)) { return "untitled" }
    $invalidChars = [System.IO.Path]::GetInvalidFileNameChars()
    $clean = -join ($name.ToCharArray() | ForEach-Object { if ($invalidChars -contains $_) { '_' } else { $_ } })
    $clean = $clean -replace '\s+', '_' -replace '_+', '_'
    $clean = $clean.Trim('_', '.', ' ')
    if ($clean.Length -gt $maxLen) {
        $clean = $clean.Substring(0, $maxLen).TrimEnd('_', '.')
    }
    if ($clean) { return $clean } else { return "untitled" }
}

function Clean-ImageUrl([string]$url) {
    if ([string]::IsNullOrWhiteSpace($url)) { return "" }
    $exclIdx = $url.IndexOf('!')
    if ($exclIdx -gt 0) {
        return $url.Substring(0, $exclIdx)
    }
    return $url
}

Add-Type -AssemblyName System.Net.Http
$httpClientHandler = [System.Net.Http.HttpClientHandler]::new()
$httpClientHandler.AllowAutoRedirect = $true
$httpClient = [System.Net.Http.HttpClient]::new($httpClientHandler)
$httpClient.Timeout = [TimeSpan]::FromSeconds(60)
$httpClient.DefaultRequestHeaders.Add("User-Agent", $headers["User-Agent"])
$httpClient.DefaultRequestHeaders.Add("Referer", $headers["Referer"])

$masterCatalog = [System.Collections.Generic.List[PSObject]]::new()
$artistStats = [System.Collections.Generic.List[PSObject]]::new()

$totalGrandIdentified = 0
$totalGrandDownloaded = 0
$totalGrandSkipped = 0
$totalGrandFailed = 0

foreach ($slug in $Artists) {
    Write-Host ("-" * 75) -ForegroundColor Gray
    Write-Host "[*] Fetching catalog for artist: $slug..." -ForegroundColor Green
    $apiUrl = "https://www.wikiart.org/en/App/Painting/PaintingsByArtist?artistUrl=$slug&json=2"
    
    $artistPaintings = $null
    try {
        $artistPaintings = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method Get -TimeoutSec 45
    } catch {
        Write-Warning "    Failed to retrieve catalog for ${slug}: $($_.Exception.Message)"
        continue
    }

    if (-not $artistPaintings -or $artistPaintings.Count -eq 0) {
        Write-Warning "    No paintings returned for $slug."
        continue
    }

    $rawCount = $artistPaintings.Count
    $sampleArtistName = $artistPaintings[0].artistName
    if ([string]::IsNullOrWhiteSpace($sampleArtistName)) {
        $sampleArtistName = ($slug -replace '-', ' ')
    }

    $folderSafeArtist = Sanitize-FileName $sampleArtistName 40
    $artistDir = Join-Path $resolvedRoot $folderSafeArtist
    if (-not (Test-Path $artistDir)) {
        New-Item -ItemType Directory -Path $artistDir -Force | Out-Null
    }

    $targetCount = if ($MaxPerArtist -gt 0 -and $MaxPerArtist -lt $rawCount) { $MaxPerArtist } else { $rawCount }
    Write-Host "    Found $rawCount total artworks in catalog. Processing $targetCount items..." -ForegroundColor Yellow

    $curArtistItems = [System.Collections.Generic.List[PSObject]]::new()
    $idx = 1

    for ($i = 0; $i -lt $targetCount; $i++) {
        $p = $artistPaintings[$i]
        $title = if ($p.title) { [string]$p.title } else { "Untitled" }
        $year = if ($p.yearAsString) { [string]$p.yearAsString } elseif ($p.completitionYear) { [string]$p.completitionYear } else { "" }
        $w = if ($p.width) { [int]$p.width } else { 0 }
        $h = if ($p.height) { [int]$p.height } else { 0 }
        $rawImg = if ($p.image) { [string]$p.image } else { "" }
        $cleanUrl = Clean-ImageUrl $rawImg
        $mp = [Math]::Round(($w * $h) / 1000000.0, 2)

        $titleSafe = Sanitize-FileName $title 40
        $ext = ".jpg"
        if ($cleanUrl -match '\.(jpg|jpeg|png|webp)') {
            $ext = [System.IO.Path]::GetExtension(([System.Uri]$cleanUrl).AbsolutePath)
        }
        $filename = ('{0:D4}_{1}_{2}x{3}{4}' -f $idx, $titleSafe, $w, $h, $ext)
        $destPath = Join-Path $artistDir $filename

        $itemObj = [PSCustomObject]@{
            Index          = $idx
            Artist         = $sampleArtistName
            ArtistSlug     = $slug
            Title          = $title
            Year           = $year
            Width          = $w
            Height         = $h
            Megapixels     = $mp
            HighResUrl     = $cleanUrl
            LocalFileName  = $filename
            FileSizeBytes  = 0
        }

        $curArtistItems.Add($itemObj)
        $masterCatalog.Add($itemObj)
        $idx++
    }

    # Save artist metadata
    $artistJson = Join-Path $artistDir "metadata.json"
    $artistCsv  = Join-Path $artistDir "metadata.csv"
    $curArtistItems | ConvertTo-Json -Depth 4 | Out-File -FilePath $artistJson -Encoding utf8
    $curArtistItems | Export-Csv -Path $artistCsv -NoTypeInformation -Encoding utf8

    Write-Host "    Artist metadata saved: $artistJson" -ForegroundColor Gray

    if ($MetadataOnly) {
        $totalGrandIdentified += $curArtistItems.Count
        continue
    }

    # Download images for this artist
    Write-Host "    Downloading images into $artistDir..." -ForegroundColor Green
    $downloaded = 0
    $skipped = 0
    $failed = 0
    $c = 0

    foreach ($item in $curArtistItems) {
        $c++
        $filePath = Join-Path $artistDir $item.LocalFileName

        if (Test-Path -Path $filePath) {
            $existing = (Get-Item $filePath).Length
            if ($existing -gt 10000) {
                $item.FileSizeBytes = $existing
                $skipped++
                continue
            }
        }

        if ([string]::IsNullOrWhiteSpace($item.HighResUrl)) {
            $failed++
            continue
        }

        try {
            $bytes = $httpClient.GetByteArrayAsync($item.HighResUrl).GetAwaiter().GetResult()
            [System.IO.File]::WriteAllBytes($filePath, $bytes)
            $item.FileSizeBytes = $bytes.Length
            $downloaded++
            if (($downloaded % 15 -eq 0) -or ($c -eq $curArtistItems.Count)) {
                $mbSize = [Math]::Round($bytes.Length / 1048576.0, 2)
                $msg = ('    [{0}/{1}] Progress: {2} ({3} MB)' -f $c, $curArtistItems.Count, $item.LocalFileName, $mbSize)
                Write-Host $msg -ForegroundColor Gray
            }
        } catch {
            $failed++
        }
    }

    # Re-save metadata with actual downloaded file sizes
    $curArtistItems | ConvertTo-Json -Depth 4 | Out-File -FilePath $artistJson -Encoding utf8
    $curArtistItems | Export-Csv -Path $artistCsv -NoTypeInformation -Encoding utf8

    Write-Host "    [OK] $sampleArtistName finished: $downloaded downloaded, $skipped skipped, $failed failed." -ForegroundColor Green

    $totalGrandIdentified += $curArtistItems.Count
    $totalGrandDownloaded += $downloaded
    $totalGrandSkipped += $skipped
    $totalGrandFailed += $failed

    $artistStats.Add([PSCustomObject]@{
        Artist      = $sampleArtistName
        CatalogSize = $rawCount
        Processed   = $curArtistItems.Count
        Downloaded  = $downloaded
        Skipped     = $skipped
        Failed      = $failed
    })
}

# Master Catalogs
$masterJson = Join-Path $resolvedRoot "all_celebrity_artists_catalog.json"
$masterCsv  = Join-Path $resolvedRoot "all_celebrity_artists_catalog.csv"
$masterCatalog | ConvertTo-Json -Depth 4 | Out-File -FilePath $masterJson -Encoding utf8
$masterCatalog | Export-Csv -Path $masterCsv -NoTypeInformation -Encoding utf8

$httpClient.Dispose()
$httpClientHandler.Dispose()

Write-Host ""
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host " EXTRACTION SUMMARY ACROSS ALL CELEBRITY ARTISTS" -ForegroundColor Yellow
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host "Total Artworks Cataloged   : $totalGrandIdentified"
Write-Host "New Files Downloaded       : $totalGrandDownloaded"
Write-Host "Already Existed (Skipped)  : $totalGrandSkipped"
Write-Host "Failed Downloads           : $totalGrandFailed"
Write-Host "Combined JSON Database     : $masterJson"
Write-Host "Combined CSV Database      : $masterCsv"
Write-Host ("=" * 75) -ForegroundColor Cyan

if ($artistStats.Count -gt 0) {
    $artistStats | Format-Table -AutoSize
}
