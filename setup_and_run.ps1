$ErrorActionPreference = "Stop"

Write-Host "Starting KlasseDiscordBot setup process..." -ForegroundColor Cyan

# 1. Check if the environment directory exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# 2. Activate the environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1

# 3. Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Execute the bot script
Write-Host "Starting the Discord bot..." -ForegroundColor Green
python main.py
