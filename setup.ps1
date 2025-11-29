# Setup Script
# Run this script to set up the development environment

Write-Host "🚀 Setting up Python Candlestick Data Downloader..." -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists. Skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  venv\Scripts\activate" -ForegroundColor White
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" -m pip install --upgrade pip
& "venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host "✅ Core dependencies installed" -ForegroundColor Green
Write-Host ""

# Ask about dev dependencies
$installDev = Read-Host "Do you want to install development dependencies? (y/n)"
if ($installDev -eq "y" -or $installDev -eq "Y") {
    Write-Host "Installing development dependencies..." -ForegroundColor Yellow
    & "venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
    Write-Host "✅ Development dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Create data directory
Write-Host "Creating data directory..." -ForegroundColor Yellow
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "✅ Data directory created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Data directory already exists" -ForegroundColor Yellow
}
Write-Host ""

# Run tests if dev dependencies installed
if ($installDev -eq "y" -or $installDev -eq "Y") {
    Write-Host "Running tests..." -ForegroundColor Yellow
    & "venv\Scripts\python.exe" -m pytest tests/ -v
    Write-Host ""
}

# Success message
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Activate virtual environment: venv\Scripts\activate" -ForegroundColor White
Write-Host "  2. Run examples: python examples\usage_examples.py" -ForegroundColor White
Write-Host "  3. Try CLI: python examples\cli.py AAPL --period 1mo --show" -ForegroundColor White
Write-Host "  4. Read docs: README.md" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🎉" -ForegroundColor Green
