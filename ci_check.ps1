.\.venv\Scripts\Activate.ps1

Write-Host "🔍 Checking format..."
black . --check

Write-Host "🔬 Running linters..."
flake8 feature_factory

Write-Host "🧪 Running tests..."
pytest -q --tb=short --maxfail=1

Write-Host "📈 Generating coverage..."
coverage run -m pytest
coverage report -m