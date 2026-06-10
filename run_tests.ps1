<#
.SYNOPSIS
  Activates venv and runs your test suite.
#>
Write-Host "=== Activating virtual environment ==="
& ".\.venv\Scripts\Activate.ps1"

Write-Host "=== Running pytest ==="
pytest -q --disable-warnings --maxfail=1
