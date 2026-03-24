param(
    [string]$PortName,
    [int]$BaudRate,
    [string]$LogFile,
    [string]$Title = ""
)

# Set window title if specified
if ($Title) {
    $host.UI.RawUI.WindowTitle = $Title
}

$port = New-Object System.IO.Ports.SerialPort $PortName, $BaudRate, "None", 8, "One"
$port.ReadTimeout = 1000

try {
    $port.Open()
    Write-Host "Listening on $PortName at $BaudRate baud, logging to $LogFile"
    if ($Title) { Write-Host "Window Title: $Title" }
    while ($true) {
        try {
            $line = $port.ReadLine()
            $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff'
            $logLine = "[$timestamp] $line"
            Add-Content -Path $LogFile -Value $logLine
            Write-Host $logLine
        } catch [System.TimeoutException] { }
    }
} finally {
    if ($port.IsOpen) { $port.Close() }
}
