param([string]$SourceRom = '', [string]$OutputRom = '')
$ErrorActionPreference = 'Stop'
function Get-BytesHash([byte[]]$Data) {
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash($Data))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose() }
}
try {
    if (-not $SourceRom) { throw 'Usage: drag an original Japanese NES ROM onto apply.cmd, or pass input and optional output paths.' }
    $meta = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $PSScriptRoot 'release_report.json') | ConvertFrom-Json
    $sourcePath = (Resolve-Path -LiteralPath $SourceRom).ProviderPath
    if (-not $OutputRom) { $OutputRom = Join-Path $PSScriptRoot $meta.output_filename }
    $outputPath = [IO.Path]::GetFullPath($OutputRom)
    if ([StringComparer]::OrdinalIgnoreCase.Equals($sourcePath, $outputPath)) { throw 'Output must differ from the original ROM.' }
    if (Test-Path -LiteralPath $outputPath) { throw 'Output already exists. Choose a new output path; no file was overwritten.' }
    [byte[]]$original = [IO.File]::ReadAllBytes($sourcePath)
    if ($original.Length -ne $meta.source.size -or (Get-BytesHash $original) -ne $meta.source.sha256) { throw 'Unsupported source ROM. The original Japanese revision and SHA-256 must match README_KO.txt.' }
    [byte[]]$patch = [IO.File]::ReadAllBytes((Join-Path $PSScriptRoot $meta.patch.filename))
    if ((Get-BytesHash $patch) -ne $meta.patch.sha256) { throw 'Patch SHA-256 mismatch. Extract the release ZIP again.' }
    if ([Text.Encoding]::ASCII.GetString($patch, 0, 5) -ne 'PATCH') { throw 'Invalid IPS signature.' }
    [byte[]]$target = $original.Clone()
    $cursor = 5
    while ($true) {
        if ($cursor + 3 -gt $patch.Length) { throw 'Truncated IPS record.' }
        if ($patch[$cursor] -eq 0x45 -and $patch[$cursor+1] -eq 0x4F -and $patch[$cursor+2] -eq 0x46) {
            $cursor += 3
            if ($cursor -ne $patch.Length) { throw 'Unexpected IPS tail.' }
            break
        }
        if ($cursor + 5 -gt $patch.Length) { throw 'Truncated IPS header.' }
        $offset = [int]$patch[$cursor] * 65536 + [int]$patch[$cursor+1] * 256 + [int]$patch[$cursor+2]
        $length = [int]$patch[$cursor+3] * 256 + [int]$patch[$cursor+4]
        $cursor += 5
        if ($length -eq 0) {
            if ($cursor + 3 -gt $patch.Length) { throw 'Truncated IPS RLE.' }
            $length = [int]$patch[$cursor] * 256 + [int]$patch[$cursor+1]
            $value = $patch[$cursor+2]; $cursor += 3
            if ($length -eq 0 -or $offset + $length -gt $target.Length) { throw 'Invalid IPS RLE range.' }
            for ($i = 0; $i -lt $length; $i++) { $target[$offset+$i] = $value }
        } else {
            if ($cursor + $length -gt $patch.Length -or $offset + $length -gt $target.Length) { throw 'Invalid IPS literal range.' }
            [Array]::Copy($patch, $cursor, $target, $offset, $length); $cursor += $length
        }
    }
    if ($target.Length -ne $meta.target.size -or (Get-BytesHash $target) -ne $meta.target.sha256) { throw 'Output SHA-256 mismatch; no ROM was written.' }
    $stream = [IO.File]::Open($outputPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($target, 0, $target.Length); $stream.Flush() } finally { $stream.Dispose() }
    if ((Get-BytesHash ([IO.File]::ReadAllBytes($outputPath))) -ne $meta.target.sha256) { throw 'Written output verification failed.' }
    Write-Host ('PASS v' + $meta.version + ': ' + $outputPath)
    Write-Host ('SHA-256: ' + $meta.target.sha256)
    exit 0
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
