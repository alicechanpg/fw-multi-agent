# STM32 Flash and Reset Script
# Usage: .\flash-and-reset-stm32.ps1 [-BinFile <path>] [-RelayPort COM3] [-ResetPulseMs 200]

param(
    [string]$BinFile = "D:\mybot\git\reactor-50-100-fw\Appli\Debug\reactor-fw_Appli.bin",
    [string]$RelayPort = "COM3",
    [int]$ResetPulseMs = 200
)

$PROGRAMMER = "C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.1.400.202404281720\tools\bin\STM32_Programmer_CLI.exe"
$EXT_LOADER = "C:\Users\alice\Downloads\reactor-fw\reactor-fw\ExtMemLoader\Debug\reactor-fw_ExtMemLoader.stldr"
$FLASH_ADDR = "0x90000000"

# Check files exist
if (-not (Test-Path $BinFile)) {
    Write-Error "Firmware file not found: $BinFile"
    exit 1
}
if (-not (Test-Path $PROGRAMMER)) {
    Write-Error "STM32_Programmer_CLI not found: $PROGRAMMER"
    exit 1
}
if (-not (Test-Path $EXT_LOADER)) {
    Write-Error "External loader not found: $EXT_LOADER"
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STM32 Flash and Reset" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firmware: $BinFile"
Write-Host "Relay Port: $RelayPort"
Write-Host ""

# Step 1: Flash
Write-Host "[1/2] Flashing firmware..." -ForegroundColor Yellow
$flashArgs = @(
    "-c", "port=SWD", "ap=1", "mode=UR",
    "-el", "`"$EXT_LOADER`"",
    "-d", "`"$BinFile`"", $FLASH_ADDR,
    "-v"
)

$process = Start-Process -FilePath $PROGRAMMER -ArgumentList $flashArgs -NoNewWindow -Wait -PassThru

if ($process.ExitCode -ne 0) {
    Write-Error "Flash failed with exit code: $($process.ExitCode)"
    exit 1
}

Write-Host "[1/2] Flash completed successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Reset via USB Relay
Write-Host "[2/2] Resetting STM32 via USB Relay..." -ForegroundColor Yellow

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$relayScript = Join-Path $scriptDir "usb-relay.ps1"

if (Test-Path $relayScript) {
    & $relayScript -Action pulse -Port $RelayPort -PulseMs $ResetPulseMs
    Write-Host "[2/2] Reset completed!" -ForegroundColor Green
} else {
    Write-Error "Relay script not found: $relayScript"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
