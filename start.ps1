$isSSLCertGenerated = Test-Path -Path ".\backend\cert.pem"
$isEnvConfigured = Test-Path -Path ".\backend\.env"

# Check for SSL certificates
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
        Write-Host "You can try installing the dependencies manually:" -ForegroundColor Yellow
        Write-Host "python -m pip install pyopenssl cryptography --only-binary=:all:" -ForegroundColor Yellow
        exit 1
    }
}

# Check for .env file
if (-not $isEnvConfigured) {
    Write-Host "ERROR: .env file not found in the backend directory!" -ForegroundColor Red
    Write-Host "Please create a .env file based on .env.example" -ForegroundColor Red
    exit 1
}

# Start MongoDB (assumes MongoDB is installed and in PATH)
Write-Host "Checking MongoDB status..." -ForegroundColor Yellow
$mongoService = Get-Service -Name MongoDB -ErrorAction SilentlyContinue
if ($null -eq $mongoService) {
    Write-Host "MongoDB service not found. Please make sure MongoDB is installed." -ForegroundColor Red
    Write-Host "You can download MongoDB from: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
} else {
    if ($mongoService.Status -ne "Running") {
        Write-Host "Starting MongoDB service..." -ForegroundColor Yellow
        Start-Service -Name MongoDB
        Write-Host "MongoDB service started!" -ForegroundColor Green
    } else {
        Write-Host "MongoDB service is already running!" -ForegroundColor Green
    }
}

# Create test data
Write-Host "Creating test data..." -ForegroundColor Yellow
Set-Location -Path ".\backend"
python create_test_data.py
Set-Location -Path ".."

# Start backend and frontend in separate terminals
Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '.\backend'; python run.py"

Write-Host "Starting frontend development server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '.\frontend'; npm start"

Write-Host ""
Write-Host "Application started!" -ForegroundColor Green
Write-Host "Backend: https://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Test user: test@example.com / password123" -ForegroundColor Cyan
