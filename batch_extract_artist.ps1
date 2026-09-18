<#
.SYNOPSIS
    Single-Artist Batch Downloader with Offset & Chunking Controls.
.DESCRIPTION
    Extracts paintings for one specific artist in defined batches (e.g. 50, 100, 200)
    with resume capability, uncompressed CDN resolution, and local JSON/CSV metadata.
.EXAMPLE
    .\batch_extract_artist.ps1 -Artist "vincent-van-gogh" -BatchSize 100 -Offset 0
    .\batch_extract_artist.ps1 -Artist "claude-monet" -BatchSize 50 -Offset 100
    .\batch_extract_artist.ps1 -Artist "johannes-vermeer" -BatchSize 50
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Artist = "vincent-van-gogh",

    [Parameter(Mandatory=$false)]
    [int]$BatchSize = 100,

    [Parameter(Mandatory=$false)]
    [int]$Offset = 0,

    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "artist_paintings"
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$resolvedRoot = [System.IO.Path]::GetFullPath($OutputDir)
if (-not (Test-Path -Path $resolvedRoot)) {
    New-Item -ItemType Directory -Path $resolvedRoot -Force | Out-Null
}

$headers = @{
    "User-Agent" = "PantheonFineArt/2.3 (https://github.com/lgtkgtv/pantheon-art; cultural preservation research)"
    "Accept"     = "application/json, image/*, */*"
}

function Sanitize-FileName([string]$name, [int]$maxLen = 40) {
    if ([string]::IsNullOrWhiteSpace($name)) { return "untitled" }
    $invalidChars = [System.IO.Path]::GetInvalidFileNameChars()
    $clean = -join ($name.ToCharArray() | ForEach-Object { if ($invalidChars -contains $_) { '_' } else { $_ } })
    $clean = $clean -replace '\s+', '_' -replace '_+', '_'
    $clean = $clean.Trim('_', '.', ' ')
    if ($clean.Length -gt $maxLen) {
        $clean = $clean.Substring(0, $maxLen).TrimEnd('_', '.')
    }
    return if ($clean) { $clean } else { "untitled" }
}

function Clean-ImageUrl([string]$url) {
    if ([string]::IsNullOrWhiteSpace($url)) { return "" }
    $exclIdx = $url.IndexOf('!')
    if ($exclIdx -gt 0) {
        return $url.Substring(0, $exclIdx)
    }
    return $url
}

Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host " SINGLE-ARTIST BATCH EXTRACTOR" -ForegroundColor Yellow
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host "Target Artist  : $Artist"
Write-Host "Batch Offset   : $Offset"
Write-Host "Batch Size     : $BatchSize"
Write-Host "Output Root    : $resolvedRoot"
Write-Host ""

$apiUrl = "https://www.wikiart.org/en/App/Painting/PaintingsByArtist?artistUrl=$Artist&json=2"
Write-Host "[*] Fetching catalog from WikiArt..." -ForegroundColor Green

$catalog = $null
try {
    $catalog = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method Get -TimeoutSec 45
} catch {
    Write-Error "Failed to retrieve catalog for ${Artist}: $($_.Exception.Message)"
    exit 1
}

if (-not $catalog -or $catalog.Count -eq 0) {
    Write-Warning "No paintings found in catalog for $Artist."
    exit 0
}

$totalInCatalog = $catalog.Count
$artistName = if ($catalog[0].artistName) { $catalog[0].artistName } else { ($Artist -replace '-', ' ') }
$folderSafe = Sanitize-FileName $artistName 40
$targetDir = Join-Path $resolvedRoot $folderSafe
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

$startIdx = [Math]::Max(0, $Offset)
$takeCount = if ($BatchSize -gt 0) { $BatchSize } else { $totalInCatalog }
$endIdx = [Math]::Min($totalInCatalog, ($startIdx + $takeCount))
$batchCount = $endIdx - $startIdx

Write-Host "Catalog Total  : $totalInCatalog paintings by $artistName" -ForegroundColor Cyan
Write-Host "Batch Range    : Items $($startIdx + 1) to $endIdx ($batchCount items)" -ForegroundColor Yellow
Write-Host "Folder         : $targetDir" -ForegroundColor Gray
Write-Host ""

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
$batchItems = [System.Collections.Generic.List[PSObject]]::new()

for ($i = $startIdx; $i -lt $endIdx; $i++) {
    $itemNum = $i + 1
    $p = $catalog[$i]
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
    $filename = ('{0:D4}_{1}_{2}x{3}{4}' -f $itemNum, $titleSafe, $w, $h, $ext)
    $destPath = Join-Path $targetDir $filename

    $obj = [PSCustomObject]@{
        Index          = $itemNum
        Artist         = $artistName
        ArtistSlug     = $Artist
        Title          = $title
        Year           = $year
        Width          = $w
        Height         = $h
        Megapixels     = $mp
        HighResUrl     = $cleanUrl
        LocalFileName  = $filename
        FileSizeBytes  = 0
    }

    if (Test-Path -Path $destPath) {
        $existing = (Get-Item $destPath).Length
        if ($existing -gt 10000) {
            $obj.FileSizeBytes = $existing
            $batchItems.Add($obj)
            $skipped++
            continue
        }
    }

    if ([string]::IsNullOrWhiteSpace($cleanUrl)) {
        $failed++
        $batchItems.Add($obj)
        continue
    }

    try {
        $bytes = $httpClient.GetByteArrayAsync($cleanUrl).GetAwaiter().GetResult()
        [System.IO.File]::WriteAllBytes($destPath, $bytes)
        $obj.FileSizeBytes = $bytes.Length
        $downloaded++
        $mb = [Math]::Round($bytes.Length / 1048576.0, 2)
        Write-Host ('[{0}/{1}] Saved: {2} ({3} MB)' -f ($i - $startIdx + 1), $batchCount, $filename, $mb) -ForegroundColor Gray
    } catch {
        $failed++
        Write-Warning ('Failed: ' + $filename)
    }

    $batchItems.Add($obj)
}

$httpClient.Dispose()
$httpClientHandler.Dispose()

$metaJson = Join-Path $targetDir ("batch_meta_{0}_to_{1}.json" -f ($startIdx + 1), $endIdx)
$batchItems | ConvertTo-Json -Depth 4 | Out-File -FilePath $metaJson -Encoding utf8

Write-Host ""
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host " BATCH DOWNLOAD COMPLETE" -ForegroundColor Yellow
Write-Host ("=" * 75) -ForegroundColor Cyan
Write-Host "Artist                 : $artistName"
Write-Host "Range Processed        : $($startIdx + 1) to $endIdx"
Write-Host "Downloaded             : $downloaded"
Write-Host "Already Existed        : $skipped"
Write-Host "Failed                 : $failed"
Write-Host "Batch Metadata Saved   : $metaJson"
Write-Host ("=" * 75) -ForegroundColor Cyan
