# PowerShell Script to Verify and Fix RO/RO Monitor Installation
# Run this in PowerShell: .\fix_installation.ps1

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "RO/RO Monitor Installation Verification & Fix" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Host "ERROR: main.py not found in current directory!" -ForegroundColor Red
    Write-Host "Please navigate to the project root directory first." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Found main.py" -ForegroundColor Green

# Check roro_monitor folder
if (-not (Test-Path "roro_monitor")) {
    Write-Host "ERROR: roro_monitor folder not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found roro_monitor folder" -ForegroundColor Green

# List of required folders
$requiredFolders = @(
    "roro_monitor\config",
    "roro_monitor\data",
    "roro_monitor\engine",
    "roro_monitor\pillars",
    "roro_monitor\dashboard",
    "roro_monitor\indicators",
    "roro_monitor\backtest",
    "roro_monitor\tests"
)

Write-Host ""
Write-Host "Checking folder structure..." -ForegroundColor Yellow

$missingFolders = @()
foreach ($folder in $requiredFolders) {
    if (Test-Path $folder) {
        Write-Host "  ✓ $folder" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $folder (MISSING)" -ForegroundColor Red
        $missingFolders += $folder
    }
}

# List of required Python files in data folder
$dataFiles = @(
    "roro_monitor\data\__init__.py",
    "roro_monitor\data\cache.py",
    "roro_monitor\data\fetcher.py"
)

Write-Host ""
Write-Host "Checking critical data module files..." -ForegroundColor Yellow

$missingFiles = @()
foreach ($file in $dataFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "  ✓ $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (MISSING)" -ForegroundColor Red
        $missingFiles += $file
    }
}

# Summary
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan

if ($missingFolders.Count -eq 0 -and $missingFiles.Count -eq 0) {
    Write-Host "SUCCESS: All files and folders present!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Install dependencies: pip install -r requirements.txt"
    Write-Host "  2. Run analysis: python main.py analyze"
    Write-Host ""
} else {
    Write-Host "ISSUES FOUND!" -ForegroundColor Red
    Write-Host ""

    if ($missingFolders.Count -gt 0) {
        Write-Host "Missing folders:" -ForegroundColor Red
        foreach ($folder in $missingFolders) {
            Write-Host "  - $folder"
        }
    }

    if ($missingFiles.Count -gt 0) {
        Write-Host "Missing files:" -ForegroundColor Red
        foreach ($file in $missingFiles) {
            Write-Host "  - $file"
        }
    }

    Write-Host ""
    Write-Host "SOLUTIONS:" -ForegroundColor Yellow
    Write-Host "1. Try: git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w"
    Write-Host "2. Or: git reset --hard origin/claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w"
    Write-Host "3. If that fails, clone a fresh copy of the repository"
}

Write-Host "=" * 60 -ForegroundColor Cyan

# Test Python import
Write-Host ""
Write-Host "Testing Python imports..." -ForegroundColor Yellow

$testScript = @"
import sys
import os
sys.path.insert(0, '.')

try:
    import roro_monitor
    print('✓ roro_monitor package imported')

    from roro_monitor.data import DataFetcher
    print('✓ DataFetcher imported successfully')

    from roro_monitor.config import settings
    print('✓ Settings imported successfully')

    print('\n✓ ALL IMPORTS SUCCESSFUL - System ready!')
    sys.exit(0)

except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
"@

$testScript | python 2>&1 | ForEach-Object {
    if ($_ -match "✓") {
        Write-Host $_ -ForegroundColor Green
    } elseif ($_ -match "✗") {
        Write-Host $_ -ForegroundColor Red
    } else {
        Write-Host $_
    }
}

Write-Host ""
