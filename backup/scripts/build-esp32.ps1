# ESP32 Build Script - Run in clean Windows environment
# Usage: powershell -ExecutionPolicy Bypass -File build-esp32.ps1 [-Clean]

param(
    [switch]$Clean
)

# Remove MSYS/MinGW environment variables that ESP-IDF checks
$env:MSYSTEM = $null
$env:MSYSTEM_CARCH = $null
$env:MSYSTEM_CHOST = $null
$env:MSYSTEM_PREFIX = $null
$env:MINGW_CHOST = $null
$env:MINGW_PACKAGE_PREFIX = $null
$env:MINGW_PREFIX = $null

# Clean PATH from MSYS/MinGW entries
$cleanPath = ($env:PATH -split ';' | Where-Object {
    $_ -notmatch 'mingw|msys|git.usr.bin|Git\\usr\\bin'
}) -join ';'
$env:PATH = $cleanPath

$ESP32_PROJECT = "D:\mybot\git\pg-reactor-esp32-wifi-bt"
$IDF_PATH = "C:\Users\alice\esp\esp-idf"
$IDF_PYTHON_ENV = "C:\Users\alice\.espressif\python_env\idf5.0_py3.11_env"

Write-Host "Building ESP32 firmware..." -ForegroundColor Yellow
Write-Host "Project: $ESP32_PROJECT"

Set-Location $ESP32_PROJECT

# Set up ESP-IDF environment manually
$env:IDF_PATH = $IDF_PATH

# Add ESP-IDF Python env to PATH first
$env:PATH = "$IDF_PYTHON_ENV\Scripts;$env:PATH"

# Source ESP-IDF tools
Write-Host "Loading ESP-IDF environment..."
& "$IDF_PATH\export.ps1"

# Clean build if requested
if ($Clean) {
    Write-Host "Running fullclean..." -ForegroundColor Yellow
    & "$IDF_PYTHON_ENV\Scripts\python.exe" "$IDF_PATH\tools\idf.py" fullclean
}

# Build using the correct Python
Write-Host "Running idf.py build..."
& "$IDF_PYTHON_ENV\Scripts\python.exe" "$IDF_PATH\tools\idf.py" build

# If build failed due to project mismatch, try fullclean and rebuild
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed, trying fullclean..." -ForegroundColor Yellow
    & "$IDF_PYTHON_ENV\Scripts\python.exe" "$IDF_PATH\tools\idf.py" fullclean
    & "$IDF_PYTHON_ENV\Scripts\python.exe" "$IDF_PATH\tools\idf.py" build
}

exit $LASTEXITCODE
