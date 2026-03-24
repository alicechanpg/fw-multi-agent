# ESP32 Flash Script
# Usage: powershell -ExecutionPolicy Bypass -File flash-esp32.ps1 [-Port COM19]

param(
    [string]$Port = ""
)

$ESP32_BUILD = "D:\mybot\git\pg-reactor-esp32-wifi-bt\build"
$ESPTOOL = "D:\mybot\git\tool\esptool-v4.5.1-win64\esptool.exe"

# Auto-detect ESP32 port if not specified
if (-not $Port) {
    Write-Host "Auto-detecting ESP32 port..." -ForegroundColor Yellow
    $ports = python -c "import serial.tools.list_ports; [print(f'{p.device}') for p in serial.tools.list_ports.comports() if p.vid == 0x303a]" 2>$null
    if ($ports) {
        $Port = $ports.Trim()
        Write-Host "Found ESP32 on $Port" -ForegroundColor Green
    } else {
        Write-Error "ESP32 not found. Please specify -Port parameter."
        exit 1
    }
}

# Check files exist
$bootloader = "$ESP32_BUILD\bootloader\bootloader.bin"
$app = "$ESP32_BUILD\wifi_and_bt_core_on_esp32.bin"
$partition = "$ESP32_BUILD\partition_table\partition-table.bin"
$ota = "$ESP32_BUILD\ota_data_initial.bin"

if (-not (Test-Path $bootloader)) { Write-Error "Bootloader not found: $bootloader"; exit 1 }
if (-not (Test-Path $app)) { Write-Error "App not found: $app"; exit 1 }
if (-not (Test-Path $partition)) { Write-Error "Partition table not found: $partition"; exit 1 }
if (-not (Test-Path $ota)) { Write-Error "OTA data not found: $ota"; exit 1 }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ESP32 Flash" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Port: $Port"
Write-Host "Build: $ESP32_BUILD"
Write-Host ""

Write-Host "Flashing ESP32..." -ForegroundColor Yellow

$flashArgs = @(
    "-p", $Port,
    "-b", "460800",
    "--before", "default_reset",
    "--after", "hard_reset",
    "--chip", "esp32s3",
    "write_flash",
    "--flash_mode", "dio",
    "--flash_freq", "80m",
    "--flash_size", "4MB",
    "0x0", $bootloader,
    "0x8000", $partition,
    "0xd000", $ota,
    "0x10000", $app
)

& $ESPTOOL @flashArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "ESP32 Flash completed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
} else {
    Write-Error "ESP32 Flash failed with exit code: $LASTEXITCODE"
    exit 1
}
