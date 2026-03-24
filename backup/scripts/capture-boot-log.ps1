# Capture Boot Log Script
# Builds, flashes, and captures boot logs from both MCUs
# Usage: powershell -ExecutionPolicy Bypass -File capture-boot-log.ps1 [-SkipBuild] [-CaptureSeconds 45]

param(
    [switch]$SkipBuild,
    [switch]$SkipESP32,
    [switch]$SkipSTM32,
    [int]$CaptureSeconds = 45,
    [string]$ESP32Port = "COM19",
    [int]$ESP32Baud = 115200,
    [string]$STM32Port = "COM4",
    [int]$STM32Baud = 921600,
    [string]$RelayPort = "COM3"
)

$TOOL_DIR = "D:\mybot\git\tool"
$LOG_DIR = "$TOOL_DIR\logs"
$Timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'

# Log files with timestamp to avoid overwriting
$ESP32_LOG = "$LOG_DIR\esp32_boot_$Timestamp.txt"
$STM32_LOG = "$LOG_DIR\stm32_boot_$Timestamp.txt"

# Ensure log directory exists
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# ========================================
# Helper: Check COM port availability
# ========================================
function Test-ComPort {
    param([string]$Port, [string]$Label)
    try {
        $serial = New-Object System.IO.Ports.SerialPort $Port
        $serial.Open()
        $serial.Close()
        Write-Host "  [OK] $Label ($Port) available" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  [FAIL] $Label ($Port) not available: $_" -ForegroundColor Red
        return $false
    }
}

# ========================================
# Step 0: Pre-flight check
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pre-flight Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$allOk = $true
if (-not $SkipSTM32) {
    if (-not (Test-ComPort $STM32Port "STM32")) { $allOk = $false }
    if (-not (Test-ComPort $RelayPort "USB Relay")) { $allOk = $false }
}
if (-not $SkipESP32) {
    if (-not (Test-ComPort $ESP32Port "ESP32")) { $allOk = $false }
}

if (-not $allOk) {
    Write-Error "Pre-flight check failed. Fix COM port issues and retry."
    exit 1
}
Write-Host ""

# ========================================
# Step 1: Build (optional)
# ========================================
if (-not $SkipBuild) {
    if (-not $SkipESP32) {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "[Build] ESP32" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        & powershell -ExecutionPolicy Bypass -File "$TOOL_DIR\build-esp32.ps1"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "ESP32 build failed!"
            exit 1
        }
        Write-Host ""
    }

    if (-not $SkipSTM32) {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "[Build] STM32" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        & powershell -ExecutionPolicy Bypass -File "$TOOL_DIR\build-stm32.ps1"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "STM32 build failed!"
            exit 1
        }
        Write-Host ""
    }
}

# ========================================
# Step 2: Start serial loggers BEFORE flash
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[Logger] Starting serial capture" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$loggerProcesses = @()

if (-not $SkipSTM32) {
    Write-Host "  STM32: $STM32Port @ $STM32Baud -> $STM32_LOG"
    $p = Start-Process powershell -ArgumentList @(
        '-ExecutionPolicy', 'Bypass', '-File', "$TOOL_DIR\serial-logger.ps1",
        '-PortName', $STM32Port, '-BaudRate', $STM32Baud,
        '-LogFile', $STM32_LOG, '-Title', 'CAPTURE-STM32'
    ) -PassThru -WindowStyle Minimized
    $loggerProcesses += $p
    Write-Host "  STM32 logger PID: $($p.Id)" -ForegroundColor Gray
}

if (-not $SkipESP32) {
    Write-Host "  ESP32: $ESP32Port @ $ESP32Baud -> $ESP32_LOG"
    $p = Start-Process powershell -ArgumentList @(
        '-ExecutionPolicy', 'Bypass', '-File', "$TOOL_DIR\serial-logger.ps1",
        '-PortName', $ESP32Port, '-BaudRate', $ESP32Baud,
        '-LogFile', $ESP32_LOG, '-Title', 'CAPTURE-ESP32'
    ) -PassThru -WindowStyle Minimized
    $loggerProcesses += $p
    Write-Host "  ESP32 logger PID: $($p.Id)" -ForegroundColor Gray
}

# Wait for loggers to stabilize
Start-Sleep -Seconds 2
Write-Host "  Loggers started." -ForegroundColor Green
Write-Host ""

# ========================================
# Step 3: Flash
# ========================================
if (-not $SkipESP32) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "[Flash] ESP32" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # Must close ESP32 logger briefly for flash (uses same COM port)
    $esp32Logger = $loggerProcesses | Where-Object { $_.Id -eq $loggerProcesses[-1].Id }
    if ($esp32Logger -and -not $esp32Logger.HasExited) {
        Write-Host "  Pausing ESP32 logger for flash..." -ForegroundColor Yellow
        Stop-Process -Id $esp32Logger.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }

    & powershell -ExecutionPolicy Bypass -File "$TOOL_DIR\flash-esp32.ps1" -Port $ESP32Port
    if ($LASTEXITCODE -ne 0) {
        Write-Error "ESP32 flash failed!"
        # Cleanup loggers
        $loggerProcesses | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
        exit 1
    }

    # Restart ESP32 logger after flash
    Start-Sleep -Seconds 1
    Write-Host "  Restarting ESP32 logger..." -ForegroundColor Yellow
    $p = Start-Process powershell -ArgumentList @(
        '-ExecutionPolicy', 'Bypass', '-File', "$TOOL_DIR\serial-logger.ps1",
        '-PortName', $ESP32Port, '-BaudRate', $ESP32Baud,
        '-LogFile', $ESP32_LOG, '-Title', 'CAPTURE-ESP32'
    ) -PassThru -WindowStyle Minimized
    # Update the list
    $loggerProcesses = @($loggerProcesses[0]) + @($p)
    Write-Host ""
}

if (-not $SkipSTM32) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "[Flash] STM32 (SWD - does not use COM4)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # STM32 flash uses SWD (not COM4), and relay uses COM3
    # Need to temporarily free COM3 if logger is using it (it shouldn't be)
    & powershell -ExecutionPolicy Bypass -File "$TOOL_DIR\flash-and-reset-stm32.ps1" -RelayPort $RelayPort
    if ($LASTEXITCODE -ne 0) {
        Write-Error "STM32 flash failed!"
        $loggerProcesses | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
        exit 1
    }
    Write-Host ""
}

# ========================================
# Step 4: Capture boot log
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[Capture] Waiting $CaptureSeconds seconds for boot log..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

for ($i = $CaptureSeconds; $i -gt 0; $i -= 5) {
    $remaining = [Math]::Min($i, 5)
    Write-Host "  $i seconds remaining..." -ForegroundColor Gray
    Start-Sleep -Seconds $remaining
}

Write-Host "  Capture complete!" -ForegroundColor Green
Write-Host ""

# ========================================
# Step 5: Stop loggers
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[Cleanup] Stopping loggers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$loggerProcesses | ForEach-Object {
    if (-not $_.HasExited) {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  Stopped PID $($_.Id)" -ForegroundColor Gray
    }
}

Start-Sleep -Seconds 1

# ========================================
# Summary
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Boot Log Capture Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

if (-not $SkipSTM32 -and (Test-Path $STM32_LOG)) {
    $stm32Lines = (Get-Content $STM32_LOG | Measure-Object).Count
    Write-Host "  STM32: $STM32_LOG ($stm32Lines lines)"
} else {
    Write-Host "  STM32: (skipped or no log)" -ForegroundColor Yellow
}

if (-not $SkipESP32 -and (Test-Path $ESP32_LOG)) {
    $esp32Lines = (Get-Content $ESP32_LOG | Measure-Object).Count
    Write-Host "  ESP32: $ESP32_LOG ($esp32Lines lines)"
} else {
    Write-Host "  ESP32: (skipped or no log)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Log files are ready for analysis." -ForegroundColor Cyan
exit 0
