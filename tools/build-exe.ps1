$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) { $pythonCommand = Get-Command py -ErrorAction SilentlyContinue }
if (-not $pythonCommand) { throw 'Python 3.10 or later was not found on PATH.' }

Push-Location $projectRoot
try {
    & $pythonCommand.Source -c 'import PyInstaller' 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller is missing. Run: python -m pip install pyinstaller' }
    & $pythonCommand.Source -m PyInstaller --noconfirm --clean --onefile --name Myapp --paths src Myapp.py
    if ($LASTEXITCODE -ne 0) { throw 'EXE build failed.' }
    Write-Host "Built $projectRoot\dist\Myapp.exe"
}
finally {
    Pop-Location
}
