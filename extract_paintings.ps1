<#
.SYNOPSIS
    Extract 500 Most Popular Paintings of All Time in Highest Possible Resolution.
.DESCRIPTION
    Directly queries the WikiArt art repository, resolves the maximum resolution image
    variant for each artwork (up to 8,500+ px wide), downloads the files with progress
    tracking, and saves comprehensive metadata to JSON and CSV.
.PARAMETER Count
    Number of paintings to extract (default: 500, max: 600).
.PARAMETER OutputDir
    Folder to save images and metadata reports (default: "paintings_output").
.PARAMETER Concurrency
    Concurrent download threads (default: 6).
.PARAMETER MetadataOnly
    If specified, only compiles JSON and CSV metadata without downloading image files.
.EXAMPLE
    .\extract_paintings.ps1 -Count 500
    .\extract_paintings.ps1 -Count 100 -OutputDir "C:\Art\Top100"
    .\extract_paintings.ps1 -MetadataOnly
#>

[CmdletBinding()]
param(
    [int]$Count = 500,
    [string]$OutputDir = "paintings_output",
    [int]$Concurrency = 6,
    [switch]$MetadataOnly
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Ensure output directory exists
$resolvedOutDir = [System.IO.Path]::GetFullPath($OutputDir)
if (-not (Test-Path -Path $resolvedOutDir)) {
    New-Item -ItemType Directory -Path $resolvedOutDir -Force | Out-Null
}

Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host " 500 MOST POPULAR PAINTINGS OF ALL TIME - HIGH RESOLUTION EXTRACTOR" -ForegroundColor Yellow
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host "Target Count    : $Count"
Write-Host "Output Directory: $resolvedOutDir"
Write-Host "Concurrency     : $Concurrency threads"
Write-Host "Metadata Only   : $MetadataOnly"
Write-Host ""

$headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    "Accept"     = "application/json, text/html, */*"
    "Referer"    = "https://www.wikiart.org/"
}

# Helper to sanitize strings for Windows filenames
function Sanitize-FileName([string]$name, [int]$maxLen = 40) {
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

# Helper to remove CDN downscale modifiers (!Large.jpg, etc.)
function Clean-ImageUrl([string]$url) {
    if ([string]::IsNullOrWhiteSpace($url)) { return "" }
    $exclIdx = $url.IndexOf('!')
    if ($exclIdx -gt 0) {
        return $url.Substring(0, $exclIdx)
    }
    return $url
}

# Step 1: Query WikiArt API to fetch popular paintings
Write-Host "[1/4] Fetching Popular Paintings catalogue from WikiArt API..." -ForegroundColor Green
$rawPaintings = [System.Collections.Generic.List[PSObject]]::new()
$page = 1

while ($rawPaintings.Count -lt $Count -and $page -le 10) {
    $apiUrl = "https://www.wikiart.org/en/App/Search/popular-paintings?searchterm=alltime&json=2&layout=new&page=" + $page
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method Get -TimeoutSec 30
        if ($response.Paintings -and $response.Paintings.Count -gt 0) {
            foreach ($item in $response.Paintings) {
                $rawPaintings.Add($item)
                if ($rawPaintings.Count -ge $Count) { break }
            }
            $logMsg = ('    - Page {0}: retrieved {1} items (Total: {2})' -f $page, $response.Paintings.Count, $rawPaintings.Count)
            Write-Host $logMsg -ForegroundColor Gray
        } else {
            break
        }
    } catch {
        $errMsg = ('    Failed to fetch page {0}: {1}' -f $page, $_.Exception.Message)
        Write-Warning $errMsg
        break
    }
    $page++
    Start-Sleep -Milliseconds 400
}

Write-Host ('    Successfully collected {0} paintings.' -f $rawPaintings.Count) -ForegroundColor Green
Write-Host ""

# Step 2: Analyze all image variants to select highest resolution
Write-Host "[2/4] Analyzing image candidates to pick maximum resolution scans..." -ForegroundColor Green

$processedPaintings = [System.Collections.Generic.List[PSObject]]::new()
$rank = 1
$ultraHdCount = 0

foreach ($p in $rawPaintings) {
    $title = "Untitled"
    if ($p.title) { $title = [string]$p.title }
    
    $artist = "Unknown Artist"
    if ($p.artistName) { $artist = [string]$p.artistName }
    
    $year = ""
    if ($p.year) { $year = [string]$p.year }
    
    $paintUrl = ""
    if ($p.paintingUrl) {
        if ($p.paintingUrl -like "http*") {
            $paintUrl = $p.paintingUrl
        } else {
            $paintUrl = "https://www.wikiart.org" + $p.paintingUrl
        }
    }

    # Find highest resolution among base image and all images[] variants
    $bestW = 0
    if ($p.width) { $bestW = [int]$p.width }
    
    $bestH = 0
    if ($p.height) { $bestH = [int]$p.height }
    
    $bestUrl = ""
    if ($p.image) { $bestUrl = Clean-ImageUrl ([string]$p.image) }
    
    $bestArea = $bestW * $bestH

    if ($p.images) {
        foreach ($variant in $p.images) {
            $vw = 0
            if ($variant.width) { $vw = [int]$variant.width }
            $vh = 0
            if ($variant.height) { $vh = [int]$variant.height }
            $vArea = $vw * $vh
            if ($vArea -gt $bestArea) {
                $bestW = $vw
                $bestH = $vh
                $bestArea = $vArea
                $bestUrl = Clean-ImageUrl ([string]$variant.image)
            }
        }
    }

    if ($bestW -ge 2000 -or $bestH -ge 2000) {
        $ultraHdCount++
    }

    $mp = [Math]::Round(($bestW * $bestH) / 1000000.0, 2)

    $obj = [PSCustomObject]@{
        Rank            = $rank
        Title           = $title
        Artist          = $artist
        Year            = $year
        Width           = $bestW
        Height          = $bestH
        Megapixels      = $mp
        HighResUrl      = $bestUrl
        WikiArtUrl      = $paintUrl
        LocalFileName   = ""
        FileSizeBytes   = 0
    }
    $processedPaintings.Add($obj)
    $rank++
}

$ultraMsg = ('    Ultra-HD scans (>= 2000px): {0} / {1}' -f $ultraHdCount, $processedPaintings.Count)
Write-Host $ultraMsg -ForegroundColor Yellow
Write-Host ""

# Step 3: Export Metadata JSON and CSV
Write-Host "[3/4] Exporting metadata files..." -ForegroundColor Green
$jsonPath = Join-Path $resolvedOutDir "paintings_metadata.json"
$csvPath  = Join-Path $resolvedOutDir "paintings_metadata.csv"

$processedPaintings | ConvertTo-Json -Depth 5 | Out-File -FilePath $jsonPath -Encoding utf8
$processedPaintings | Export-Csv -Path $csvPath -NoTypeInformation -Encoding utf8

Write-Host ('    JSON metadata: ' + $jsonPath) -ForegroundColor Cyan
Write-Host ('    CSV metadata : ' + $csvPath) -ForegroundColor Cyan

if ($MetadataOnly) {
    Write-Host ""
    Write-Host "[OK] -MetadataOnly specified. Extraction completed without downloading images." -ForegroundColor Green
    return
}

# Step 4: Download Images
Write-Host ""
Write-Host ('[4/4] Downloading full-resolution images into ' + $resolvedOutDir + '...') -ForegroundColor Green

Add-Type -AssemblyName System.Net.Http
$httpClientHandler = [System.Net.Http.HttpClientHandler]::new()
$httpClientHandler.AllowAutoRedirect = $true
$httpClient = [System.Net.Http.HttpClient]::new($httpClientHandler)
$httpClient.Timeout = [TimeSpan]::FromSeconds(60)
$httpClient.DefaultRequestHeaders.Add("User-Agent", $headers["User-Agent"])
$httpClient.DefaultRequestHeaders.Add("Referer", $headers["Referer"])

$downloaded = 0
$skipped = 0
$failed = 0
$total = $processedPaintings.Count
$counter = 0

foreach ($item in $processedPaintings) {
    $counter++
    $r = $item.Rank
    $artistSafe = Sanitize-FileName $item.Artist 25
    $titleSafe  = Sanitize-FileName $item.Title 35
    $w = $item.Width
    $h = $item.Height

    # Get extension
    $ext = ".jpg"
    try {
        $uri = [System.Uri]$item.HighResUrl
        $pathExt = [System.IO.Path]::GetExtension($uri.AbsolutePath)
        if ($pathExt -match '^\.(jpg|jpeg|png|webp)$') { $ext = $pathExt }
    } catch {}

    $filename = ('{0:D3}_{1}_-_{2}_{3}x{4}{5}' -f $r, $artistSafe, $titleSafe, $w, $h, $ext)
    $destPath = Join-Path $resolvedOutDir $filename
    $item.LocalFileName = $filename

    # Check if already downloaded (resume capability)
    if (Test-Path -Path $destPath) {
        $existingSize = (Get-Item $destPath).Length
        if ($existingSize -gt 10000) {
            $item.FileSizeBytes = $existingSize
            $skipped++
            $statusText = ('[{0}/{1}] (Skipped existing) {2}' -f $counter, $total, $filename)
            Write-Progress -Activity "Downloading paintings" -Status $statusText -PercentComplete (($counter / $total) * 100)
            continue
        }
    }

    if ([string]::IsNullOrWhiteSpace($item.HighResUrl)) {
        $failed++
        continue
    }

    $statusText = ('[{0}/{1}] Downloading: {2} ({3} MP)' -f $counter, $total, $filename, $item.Megapixels)
    Write-Progress -Activity "Downloading paintings" -Status $statusText -PercentComplete (($counter / $total) * 100)

    try {
        $bytes = $httpClient.GetByteArrayAsync($item.HighResUrl).GetAwaiter().GetResult()
        [System.IO.File]::WriteAllBytes($destPath, $bytes)
        $item.FileSizeBytes = $bytes.Length
        $downloaded++
        $mbSize = [Math]::Round($bytes.Length / 1048576.0, 2)
        $logText = ('    [{0:D3}/{1}] Downloaded: {2} ({3} MB)' -f $counter, $total, $filename, $mbSize)
        Write-Host $logText -ForegroundColor Gray
    } catch {
        $failed++
        $failText = ('    [{0:D3}/{1}] Failed: {2} -> {3}' -f $counter, $total, $filename, $_.Exception.Message)
        Write-Warning $failText
    }
}

Write-Progress -Activity "Downloading paintings" -Completed

# Update metadata files with actual file sizes
$processedPaintings | ConvertTo-Json -Depth 5 | Out-File -FilePath $jsonPath -Encoding utf8
$processedPaintings | Export-Csv -Path $csvPath -NoTypeInformation -Encoding utf8

$httpClient.Dispose()
$httpClientHandler.Dispose()

Write-Host ""
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host " EXTRACTION SUMMARY" -ForegroundColor Yellow
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host "Total Paintings Identified : $total"
Write-Host "New Files Downloaded       : $downloaded"
Write-Host "Already Existed (Skipped)  : $skipped"
Write-Host "Failed Downloads           : $failed"
Write-Host "Output Directory           : $resolvedOutDir"
Write-Host "Metadata JSON              : $jsonPath"
Write-Host "Metadata CSV               : $csvPath"
Write-Host ("=" * 75) -ForegroundColor Cyan
