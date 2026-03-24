param(
    [string]$Port = "COM18",
    [int]$Baud = 115200,
    [int]$TimeoutSec = 20
)

Write-Host "Monitoring $Port @ $Baud baud..." -ForegroundColor Yellow

$serialPort = New-Object System.IO.Ports.SerialPort($Port, $Baud)
$serialPort.ReadTimeout = 2000
$serialPort.DtrEnable = $false
$serialPort.RtsEnable = $false

try {
    $serialPort.Open()

    # Reset ESP32 into normal boot (not download mode)
    # RTS = EN (active low reset), DTR = GPIO0 (low = download mode)
    # We want: pull EN low (reset), keep GPIO0 high (normal boot), then release EN
    Write-Host "Resetting ESP32 (normal boot)..." -ForegroundColor Yellow
    $serialPort.DtrEnable = $false   # GPIO0 HIGH (normal boot)
    $serialPort.RtsEnable = $true    # EN LOW (reset)
    Start-Sleep -Milliseconds 100
    $serialPort.RtsEnable = $false   # EN HIGH (release reset)
    Start-Sleep -Milliseconds 500

    Write-Host "--- Capturing boot log ---" -ForegroundColor Cyan
    $start = Get-Date

    while (((Get-Date) - $start).TotalSeconds -lt $TimeoutSec) {
        try {
            $line = $serialPort.ReadLine()
            Write-Host $line
        } catch [System.TimeoutException] {
            # Read timeout, continue
        }
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
} finally {
    if ($serialPort.IsOpen) {
        $serialPort.Close()
    }
    Write-Host "`n--- Monitor ended ---" -ForegroundColor Yellow
}
