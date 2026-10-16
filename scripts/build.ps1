param([string]$SourceRom = '', [string]$TitleConfig = 'config/title.json')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    New-Item -ItemType Directory -Path (Join-Path $projectRoot 'build') -Force | Out-Null
    $sourceArgs = @()
    if ($SourceRom) { $sourceArgs = @('--source', $SourceRom) }
    & python scripts/extract_title_png.py @sourceArgs
    if ($LASTEXITCODE -ne 0) { throw 'Title extraction/source verification failed' }
    $titleSpec = Get-Content -Raw -Encoding UTF8 -LiteralPath $TitleConfig | ConvertFrom-Json
    $logoArtifact = if ($titleSpec.logo_artifact_id) { $titleSpec.logo_artifact_id } else { $titleSpec.build_id }
    & python scripts/convert_generated_title.py --input $titleSpec.generated_path --name $logoArtifact
    if ($LASTEXITCODE -ne 0) { throw 'NES conversion/tile budget failed' }
    & python scripts/build_title.py @sourceArgs --config $TitleConfig
    if ($LASTEXITCODE -ne 0) { throw 'Build/Expected Write/IPS verification failed' }
} finally { Pop-Location }
