# Build and Flash All Script
# Usage: powershell -ExecutionPolicy Bypass -File build-and-flash-all.ps1
#
# Order: ESP32 build -> ESP32 flash -> STM32 build -> STM32 flash
# Log windows will be opened after flashing

param(
    [switch]$SkipESP32,
    [switch]$SkipSTM32,
    [switch]$NoLog
)

$TOOL_DIR = "D:\mybot\git\tool"
$LOG_DIR = "$TOOL_DIR\logs"

# Baud rates
$ESP32_BAUD = 115200
$STM32_BAUD = 921600

# Ensure log directory exists
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# Kill existing log windows
Write-Host "Closing existing log windows..." -ForegroundColor Yellow
Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne $PID } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

$success = $true

# ========================================
# ESP32
# ========================================
if (-not $SkipESP32) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "ESP32 Build & Flash" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # Build ESP32
    Write-Host "[1/2] Building ESP32..." -ForegroundColor Yellow
    & powershell -ExecutionPolicy Bypass -File "$TOOL_DIR\build-esp32.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "ESP32 build failed!"
        $success = $false
    } else {
        Write-Host "[1/2] ESP32 build completed!" -ForegroundColor Green

        # Flash ESP32
        Write-Host "[2/2] Flashing ESP32..." -ForegroundColor Yellow
        & powershell -ExecutionPolicy Bypass -File "$TOOL_DIR\flash-esp32.ps1"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "ESP32 flash failed!"
            $success = $false
        } else {
            Write-Host "[2/2] ESP32 flash completed!" -ForegroundColor Green
        }
    }
}

# ========================================
# STM32
# ========================================
if (-not $SkipSTM32) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "STM32 Build & Flash" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # Build STM32
    Write-Host "[1/2] Building STM32..." -ForegroundColor Yellow
    & powershell -ExecutionPolicy Bypass -File "$TOOL_DIR\build-stm32.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "STM32 build failed!"
        $success = $false
    } else {
        Write-Host "[1/2] STM32 build completed!" -ForegroundColor Green

        # Flash STM32
        Write-Host "[2/2] Flashing STM32..." -ForegroundColor Yellow
        & powershell -ExecutionPolicy Bypass -File "$TOOL_DIR\flash-and-reset-stm32.ps1"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "STM32 flash failed!"
            $success = $false
        } else {
            Write-Host "[2/2] STM32 flash completed!" -ForegroundColor Green
        }
    }
}

# ========================================
# Open Log Windows
# ========================================
if (-not $NoLog -and $success) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Opening Log Windows" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    if (-not $SkipSTM32) {
        Write-Host "Opening STM32 log (COM4, $STM32_BAUD)..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList '-ExecutionPolicy', 'Bypass', '-File', "$TOOL_DIR\serial-logger.ps1", '-PortName', 'COM4', '-BaudRate', $STM32_BAUD, '-LogFile', "$LOG_DIR\stm32_log.txt", '-Title', 'STM32-LOG-COM4'
    }

    if (-not $SkipESP32) {
        Write-Host "Opening ESP32 log (COM19, $ESP32_BAUD)..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList '-ExecutionPolicy', 'Bypass', '-File', "$TOOL_DIR\serial-logger.ps1", '-PortName', 'COM19', '-BaudRate', $ESP32_BAUD, '-LogFile', "$LOG_DIR\esp32_log.txt", '-Title', 'ESP32-LOG-COM19'
    }
}

# ========================================
# Summary
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($success) {
    Write-Host "All Done!" -ForegroundColor Green
} else {
    Write-Host "Completed with errors" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

if ($success) { exit 0 } else { exit 1 }
