Get-CimInstance Win32_PnPEntity |
    Where-Object { $_.Name -like "*COM*" -or $_.Name -like "*Serial*" -or $_.Name -like "*CH340*" } |
    Select-Object Name, DeviceID |
    Format-Table -AutoSize
