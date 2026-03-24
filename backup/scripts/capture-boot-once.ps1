# Quick boot log capture: power cycle + read serial
param(
    [string]$SerialPort = "COM4",
    [int]$SerialBaud = 921600,
    [string]$RelayPort = "COM3",
    [int]$WaitMs = 6000
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$relayScript = Join-Path $scriptDir "usb-relay.ps1"

# Power off first
& $relayScript -Action off -Port $RelayPort 2>$null
Start-Sleep -Milliseconds 500

# Open serial before power on
$serial = New-Object System.IO.Ports.SerialPort $SerialPort, $SerialBaud, "None", 8, "One"
$serial.ReadTimeout = $WaitMs + 3000
$serial.Open()

# Power on
& $relayScript -Action on -Port $RelayPort 2>$null

# Wait for boot
Start-Sleep -Milliseconds $WaitMs

# Read
if ($serial.BytesToRead -gt 0) {
    $log = $serial.ReadExisting()
    Write-Host $log
} else {
    Write-Host "NO DATA from serial"
}

$serial.Close()
