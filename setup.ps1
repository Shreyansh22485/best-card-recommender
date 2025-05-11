# Setup script for the Best Card Recommender project
# This script will install all dependencies and prepare the environment

# Check Python version
$pythonVersion = python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.8 or later." -ForegroundColor Red
    exit 1
}

Write-Host "Using $pythonVersion" -ForegroundColor Cyan

# Check if nodejs is installed
$nodeVersion = node --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Node.js is not installed or not in PATH. Please install Node.js 14 or later." -ForegroundColor Red
    exit 1
}

Write-Host "Using Node.js $nodeVersion" -ForegroundColor Cyan

# Check if MongoDB is installed
$mongoDBStatus = Get-Service -Name MongoDB -ErrorAction SilentlyContinue
if ($null -eq $mongoDBStatus) {
    Write-Host "MongoDB service not found. Please make sure MongoDB is installed." -ForegroundColor Red
    Write-Host "You can download MongoDB from: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
} else {
    Write-Host "MongoDB service found: $($mongoDBStatus.Status)" -ForegroundColor Green
}

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
Set-Location -Path ".\backend"
python -m pip install -r requirements.txt --only-binary=:all: --upgrade
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install all backend dependencies. Trying individual installations..." -ForegroundColor Yellow
    
    # Try installing the most critical packages individually
    python -m pip install fastapi uvicorn pymongo pydantic python-dotenv --only-binary=:all: --upgrade
    python -m pip install python-jose passlib bcrypt --only-binary=:all: --upgrade
    python -m pip install pyyaml python-multipart httpx --only-binary=:all: --upgrade
    python -m pip install PyPDF2 pytest --only-binary=:all: --upgrade
    python -m pip install cryptography pyopenssl --only-binary=:all: --upgrade
    
    # Try one more time with the Google packages, which might be more problematic
    python -m pip install google-auth-oauthlib google-api-python-client google-auth-httplib2 --only-binary=:all: --upgrade
}
Set-Location -Path ".."

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location -Path ".\frontend"
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install frontend dependencies. Please check your Node.js installation." -ForegroundColor Red
    Set-Location -Path ".."
    exit 1
}
Set-Location -Path ".."

# Generate SSL certificates if they don't exist
$isSSLCertGenerated = Test-Path -Path ".\backend\cert.pem"
if (-not $isSSLCertGenerated) {
    Write-Host "Generating SSL certificates..." -ForegroundColor Yellow
    Set-Location -Path ".\backend"
    
    # Try the primary method first
    try {
        python generate_cert.py
        if (-not (Test-Path -Path "cert.pem")) {
            throw "Certificate generation failed"
        }
    } catch {
        Write-Host "Primary certificate generation failed, trying alternative method..." -ForegroundColor Yellow
        # Try alternative method
        python generate_cert_alt.py
    }
    
    Set-Location -Path ".."
    
    if (Test-Path -Path ".\backend\cert.pem") {
        Write-Host "SSL certificates generated!" -ForegroundColor Green
    } else {
        Write-Host "Failed to generate SSL certificates. Please check your Python installation and dependencies." -ForegroundColor Red
        exit 1
    }
}

# Create .env file if it doesn't exist
$isEnvConfigured = Test-Path -Path ".\backend\.env"
if (-not $isEnvConfigured) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item -Path ".\backend\.env.example" -Destination ".\backend\.env"
    Write-Host "Created .env file. Please edit it with your actual credentials." -ForegroundColor Green
}

# Create test data
Write-Host "Creating test data..." -ForegroundColor Yellow
Set-Location -Path ".\backend"
python create_test_data.py
Set-Location -Path ".."

Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "To start the application, run: .\start.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test user credentials:" -ForegroundColor Cyan
Write-Host "  Email: test@example.com" -ForegroundColor White
Write-Host "  Password: password123" -ForegroundColor White
