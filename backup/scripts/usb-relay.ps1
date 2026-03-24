# LCUS-1 USB Relay Control Script
# Usage: .\usb-relay.ps1 -Action <on|off|pulse> [-Port COM3] [-PulseMs 200]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("on", "off", "pulse")]
    [string]$Action,

    [string]$Port = "COM3",
    [int]$PulseMs = 200
)

# LCUS-1 Protocol: A0 01 XX CS
# XX = 01 (ON), 00 (OFF)
# CS = Checksum (A0 + 01 + XX)
$CMD_ON  = [byte[]]@(0xA0, 0x01, 0x01, 0xA2)
$CMD_OFF = [byte[]]@(0xA0, 0x01, 0x00, 0xA1)

function Send-RelayCommand {
    param([byte[]]$Command, [string]$PortName)

    $serial = New-Object System.IO.Ports.SerialPort $PortName, 9600, "None", 8, "One"
    try {
        $serial.Open()
        $serial.Write($Command, 0, $Command.Length)
        Start-Sleep -Milliseconds 50
    }
    finally {
        if ($serial.IsOpen) { $serial.Close() }
    }
}

switch ($Action) {
    "on" {
        Write-Host "Relay ON (Port: $Port)"
        Send-RelayCommand -Command $CMD_ON -PortName $Port
    }
    "off" {
        Write-Host "Relay OFF (Port: $Port)"
        Send-RelayCommand -Command $CMD_OFF -PortName $Port
    }
    "pulse" {
        Write-Host "Relay PULSE ${PulseMs}ms (Port: $Port)"
        Send-RelayCommand -Command $CMD_ON -PortName $Port
        Start-Sleep -Milliseconds $PulseMs
        Send-RelayCommand -Command $CMD_OFF -PortName $Port
        Write-Host "Reset complete"
    }
}
