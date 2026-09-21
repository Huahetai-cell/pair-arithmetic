$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
    throw 'Python 3.10 or later was not found on PATH.'
}

Push-Location $projectRoot
try {
    $env:PYTHONPATH = Join-Path $projectRoot 'src'
    & $pythonCommand.Source -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed; performance report was not generated.' }
    & $pythonCommand.Source tools/performance.py
    if ($LASTEXITCODE -ne 0) { throw 'Performance report generation failed.' }
    Write-Host 'Generated CSV, cProfile data, two PNG charts, and report.md in docs/performance.'
}
finally {
    Pop-Location
}
