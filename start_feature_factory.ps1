<#
.SYNOPSIS
  Installs deps, activates venv, and kicks off the backfill pipeline.
.PARAMETER DbPath
  Path to your DuckDB file (default: .\data\features.duckdb).
#>
param(
    [string]$DbPath = ".\data\features.duckdb"
)

Write-Host "=== Activating virtual environment ==="
& ".\.venv\Scripts\Activate.ps1"

Write-Host "=== Installing dependencies ==="
pip install -r requirements.txt

Write-Host "=== Starting Feature Factory backfill ($DbPath) ==="
python -m backfill.cli start --db-path $DbPath
