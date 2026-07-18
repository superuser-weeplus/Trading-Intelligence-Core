# Trading Intelligence Backend Startup Script (PowerShell)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "      Trading Intelligence Backend Startup Script" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check if backend/.env exists, if not copy from .env.example
$envPath = Join-Path "backend" ".env"
$examplePath = ".env.example"

if (-not (Test-Path $envPath)) {
    Write-Host "[INFO] backend/.env not found." -ForegroundColor Yellow
    if (Test-Path $examplePath) {
        Write-Host "[INFO] Creating backend/.env from .env.example..." -ForegroundColor Yellow
        Copy-Item $examplePath $envPath
        Write-Host "[SUCCESS] Created backend/.env. Please configure it if needed." -ForegroundColor Green
    } else {
        Write-Host "[WARNING] .env.example not found. Please create backend/.env manually." -ForegroundColor Red
    }
}

# 2. Check if virtual environment exists
$venvPath = Join-Path "backend" ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[ERROR] Virtual environment (.venv) not found in backend folder!" -ForegroundColor Red
    Write-Host "Please ensure python virtual environment is set up." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit..."
    exit 1
}

Write-Host "[INFO] Activating virtual environment and starting server..." -ForegroundColor Cyan
Write-Host ""

# 3. Run the backend server
Set-Location backend
. .\.venv\Scripts\Activate.ps1
python run.py
