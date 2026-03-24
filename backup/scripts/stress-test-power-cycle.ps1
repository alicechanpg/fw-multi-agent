# NOR Flash Power Cycle Stress Test
# Usage: .\stress-test-power-cycle.ps1 [-CycleCount 1000] [-DfuBin <path>] [-FuzzyTest]
#
# Tests for NOR flash FW loss by repeatedly power cycling via USB relay
# while monitoring boot log for flash corruption.
#
# Key concept:
#   - Bootloader is in INTERNAL flash (0x08000000) → always boots, always prints log
#   - APP FW is in NOR flash (0x90000000) → this is what gets lost
#   - Bootloader checks NOR flash health and reports via serial
#   - If NOR flash corrupted → auto DFU re-flash → continue testing
#
# Fuzzy mode: randomizes ON/OFF timing to find the exact power-off timing
# that triggers flash corruption.
#   .\stress-test-power-cycle.ps1 -FuzzyTest -FuzzyOnMin 500 -FuzzyOnMax 15000
#
# Status file: writes stress-test-status.json on FAIL, every 1000 OK, NO_LOG, COMPLETE
# for external monitoring / JIRA auto-update.
#
# Ref: FWP-717, Reactor NOR Flash FW 丟失 (掉電保護)

param(
    [int]$CycleCount = 0,  # 0 = infinite (run until Ctrl+C)
    [string]$DfuBin = "",
    [string]$SerialPort = "COM4",
    [int]$SerialBaud = 921600,
    [string]$RelayPort = "COM3",
    [int]$PowerOnMs = 8000,
    [int]$PowerOffMs = 500,
    [switch]$FuzzyTest,
    [int]$FuzzyOnMin = 500,
    [int]$FuzzyOnMax = 15000,
    [int]$FuzzyOffMin = 200,
    [int]$FuzzyOffMax = 1000,
    [int]$FuzzyRunMin = 100,     # After DFU 100%, how long before power cut (ms)
    [int]$FuzzyRunMax = 1000,
    [int]$DfuWaitSec = 5,
    [switch]$SkipInitialDfu,
    [string]$JiraIssue = "FWP-717"  # Auto-post failures to JIRA
)

$DFU_UTIL = "C:\Users\alice\Downloads\dfu-util-0.11-binaries.tar\dfu-util-0.11-binaries\win64\dfu-util.exe"
$DFU_ADDR = "0x90000000:leave:mass-erase:force"
$DFU_DEVICE = "295d:0502"  # Reactor USB DFU VID:PID (avoid picking up laptop camera DFU)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$relayScript = Join-Path $scriptDir "usb-relay.ps1"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logFile = Join-Path $scriptDir "stress-test-$timestamp.log"
$statusFile = Join-Path $scriptDir "stress-test-status.json"
$random = New-Object System.Random

function Write-Status {
    param(
        [string]$Event,
        [int]$Cycle,
        [int]$OkCount,
        [int]$FailCount,
        [int]$NoLogCount,
        [string]$FlashStatus = "",
        [string]$BootLog = "",
        [int]$ActualOnMs = 0,
        [int]$ActualOffMs = 0
    )
    $status = @{
        event = $Event
        cycle = $Cycle
        totalCycles = if ($CycleCount -eq 0) { "infinite" } else { $CycleCount }
        okCount = $OkCount
        failCount = $FailCount
        noLogCount = $NoLogCount
        flashStatus = $FlashStatus
        bootLog = if ($BootLog.Length -gt 2000) { $BootLog.Substring(0, 2000) + "...(truncated)" } else { $BootLog }
        actualPowerOnMs = $ActualOnMs
        actualPowerOffMs = $ActualOffMs
        fuzzyTest = [bool]$FuzzyTest
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffzzz")
        logFile = $logFile
    }
    $status | ConvertTo-Json -Depth 3 | Set-Content $statusFile -Encoding UTF8
    Write-Log "  >> Status file updated: $Event" "Magenta"
}

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $line = "[$ts] $Message"
    Write-Host $line -ForegroundColor $Color
    $line | Out-File -Append $logFile
}

# === JIRA auto-comment on failure ===
function Post-JiraFailure {
    param(
        [int]$Cycle,
        [string]$FlashStatus,
        [string]$BootLog,
        [int]$OkCount,
        [int]$FailCount,
        [int]$NoLogCount
    )
    if (-not $JiraIssue) { return }

    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $truncLog = if ($BootLog.Length -gt 1500) { $BootLog.Substring(0, 1500) + "...(truncated)" } else { $BootLog }
    $body = @"
{noformat}
[STRESS TEST FAILURE] $ts
Cycle: $Cycle | Status: $FlashStatus
OK: $OkCount | FAIL: $FailCount | NO_LOG: $NoLogCount
Log file: $logFile

--- Boot Log ---
$truncLog
{noformat}
"@

    try {
        # Use Atlassian REST API v2 (basic auth via .netrc or token)
        $jiraBase = "https://positivegrid.atlassian.net"
        $cred = "$env:JIRA_USER`:$env:JIRA_TOKEN"
        $base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($cred))
        $headers = @{
            "Authorization" = "Basic $base64"
            "Content-Type"  = "application/json"
        }
        $payload = @{ body = $body } | ConvertTo-Json -Depth 3
        Invoke-RestMethod -Uri "$jiraBase/rest/api/2/issue/$JiraIssue/comment" -Method Post -Headers $headers -Body $payload | Out-Null
        Write-Log "  >> JIRA comment posted to $JiraIssue" "Magenta"
    } catch {
        Write-Log "  >> JIRA post failed: $_ (will write status file instead)" "DarkYellow"
    }
}

# === Resolve DFU binary ===
if (-not $DfuBin -or -not (Test-Path $DfuBin)) {
    $dfuDir = Split-Path $DFU_UTIL
    $latestBin = Get-ChildItem "$dfuDir\reactor100-fw-*.bin" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestBin) {
        $DfuBin = $latestBin.FullName
    } else {
        Write-Log "ERROR: No DFU bin specified and no reactor100-fw-*.bin found" "Red"
        Write-Log "Usage: .\stress-test-power-cycle.ps1 -DfuBin <path-to-fw.bin>" "Yellow"
        exit 1
    }
}

function Invoke-DfuFlash {
    # When NOR flash is corrupted, bootloader auto-enters DFU mode
    # So we just need to run dfu-util (device is already in DFU mode)
    # Note: dfu-util may return exit code 74 even on success because the "leave" option
    # triggers a device reset before get_status completes. We check stdout for "File downloaded successfully".
    param([int]$Attempt = 1)

    Write-Log "  DFU re-flash attempt ${Attempt} - $DfuBin" "Yellow"
    $dfuArgs = "-d $DFU_DEVICE -s $DFU_ADDR -D `"$DfuBin`""
    $tmpOut = [System.IO.Path]::GetTempFileName()
    $tmpErr = [System.IO.Path]::GetTempFileName()
    $process = Start-Process -FilePath $DFU_UTIL -ArgumentList $dfuArgs -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $tmpOut -RedirectStandardError $tmpErr
    $dfuOutput = (Get-Content $tmpOut -Raw) + (Get-Content $tmpErr -Raw)
    Remove-Item $tmpOut, $tmpErr -Force -ErrorAction SilentlyContinue

    if ($dfuOutput -match "File downloaded successfully") {
        Write-Log "  DFU flash OK (exit=$($process.ExitCode))" "Green"
        return $true
    }

    Write-Log "  DFU flash FAILED (exit code: $($process.ExitCode))" "Red"
    Write-Log "  DFU output: $dfuOutput" "DarkGray"
    return $false
}

function Invoke-DfuReadbackVerify {
    # Read back NOR flash via DFU upload and compare with original bin
    # Device must already be in DFU mode (after flash + reboot with STRESS_TEST)
    param([int]$Attempt = 1)

    $readbackFile = Join-Path $scriptDir "stress-test-readback.bin"
    $originalSize = (Get-Item $DfuBin).Length

    Write-Log "  DFU readback attempt ${Attempt} (${originalSize} bytes)..." "Cyan"
    $dfuArgs = "-d $DFU_DEVICE -s 0x90000000:${originalSize} -U `"$readbackFile`""
    $tmpOut = [System.IO.Path]::GetTempFileName()
    $tmpErr = [System.IO.Path]::GetTempFileName()
    $process = Start-Process -FilePath $DFU_UTIL -ArgumentList $dfuArgs -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $tmpOut -RedirectStandardError $tmpErr
    $dfuOutput = (Get-Content $tmpOut -Raw) + (Get-Content $tmpErr -Raw)
    Remove-Item $tmpOut, $tmpErr -Force -ErrorAction SilentlyContinue

    if (-not (Test-Path $readbackFile)) {
        Write-Log "  DFU readback FAILED - no output file" "Red"
        Write-Log "  DFU output: $dfuOutput" "DarkGray"
        return @{ ok = $false; detail = "no readback file" }
    }

    $readbackSize = (Get-Item $readbackFile).Length
    if ($readbackSize -ne $originalSize) {
        Write-Log "  DFU readback SIZE MISMATCH: original=${originalSize} readback=${readbackSize}" "Red"
        return @{ ok = $false; detail = "size mismatch: orig=$originalSize rb=$readbackSize" }
    }

    # Binary compare using file hashes
    $origHash = (Get-FileHash $DfuBin -Algorithm SHA256).Hash
    $rbHash = (Get-FileHash $readbackFile -Algorithm SHA256).Hash

    Remove-Item $readbackFile -Force -ErrorAction SilentlyContinue

    if ($origHash -eq $rbHash) {
        Write-Log "  DFU readback MATCH (SHA256: $($origHash.Substring(0,16))...)" "Green"
        return @{ ok = $true; detail = "SHA256 match" }
    } else {
        Write-Log "  DFU readback MISMATCH!" "Red"
        Write-Log "    Original: $origHash" "Red"
        Write-Log "    Readback: $rbHash" "Red"
        return @{ ok = $false; detail = "SHA256 mismatch: orig=$origHash rb=$rbHash" }
    }
}

# === Step 0: Initial DFU Flash ===
if ($SkipInitialDfu) {
    Write-Log "Skipping initial DFU (NOR flash assumed OK)" "Yellow"
    Write-Log "Auto DFU re-flash will still run on corruption during test" "Yellow"
} else {
    Write-Log "========================================" "Cyan"
    Write-Log "Step 0: Initial DFU Flash" "Cyan"
    Write-Log "========================================" "Cyan"
    Write-Log "Binary: $DfuBin"
    Write-Log "Please put device in DFU mode (hold BT_PAIR + reset), then press Enter..." "Yellow"
    Read-Host

    $initOk = Invoke-DfuFlash -Attempt 1
    if (-not $initOk) {
        Write-Log "ERROR: Initial DFU flash failed, cannot start test" "Red"
        exit 1
    }
}

# === Step 1: Power Cycle Stress Test ===
Write-Log "========================================" "Cyan"
Write-Log "Power Cycle Stress Test" "Cyan"
Write-Log "========================================" "Cyan"
$infiniteMode = ($CycleCount -eq 0)
if ($infiniteMode) {
    Write-Log "Cycles: INFINITE (Ctrl+C to stop)" "Yellow"
} else {
    Write-Log "Cycles: $CycleCount"
}
Write-Log "DFU Bin: $DfuBin"
if ($FuzzyTest) {
    Write-Log "Mode: FUZZY (random timing)" "Yellow"
    Write-Log "  PowerON range:  ${FuzzyOnMin}ms ~ ${FuzzyOnMax}ms"
    Write-Log "  PowerOFF range: ${FuzzyOffMin}ms ~ ${FuzzyOffMax}ms"
} else {
    Write-Log "Power ON: ${PowerOnMs}ms, OFF: ${PowerOffMs}ms"
}
Write-Log "Serial: $SerialPort @ $SerialBaud"
Write-Log "Relay: $RelayPort"
Write-Log "Log: $logFile"
Write-Log "Status: $statusFile"
Write-Log ""

$failCount = 0
$okCount = 0
$noLogCount = 0

$consecutiveNoLog = 0
$DFU_WAIT_PATTERN = "Waiting for DFU connection"
$BOOT_TIMEOUT_MS = 15000  # Max time to wait for bootloader to reach DFU mode
$APP_RUN_MIN_MS = 3000    # Min time to let APP run before power cut (simulate real usage)

# === Step 0.5: Ensure power OFF before starting ===
Write-Log "Ensuring device is powered OFF before test..." "Yellow"
& $relayScript -Action off -Port $RelayPort 2>$null
Start-Sleep -Milliseconds 1000

for ($i = 1; $infiniteMode -or $i -le $CycleCount; $i++) {
    # Determine OFF timing for this cycle (always fuzzy: 1ms ~ 200ms)
    $curOffMs = $random.Next($FuzzyOffMin, $FuzzyOffMax + 1)

    $cycleLabel = if ($infiniteMode) { "Cycle $i (infinite)" } else { "Cycle $i / $CycleCount" }
    Write-Log "--- $cycleLabel ---" "Yellow"

    # === Phase 1: Power OFF (the dangerous cut!) then ON ===
    # Previous cycle left device ON. This OFF is what we're testing — does it corrupt NOR flash?
    & $relayScript -Action off -Port $RelayPort 2>$null
    Write-Log "  POWER OFF (${curOffMs}ms) -- the dangerous cut!" "Red"
    Start-Sleep -Milliseconds $curOffMs

    # Open serial port BEFORE power on
    $serial = $null
    try {
        $serial = New-Object System.IO.Ports.SerialPort $SerialPort, $SerialBaud, "None", 8, "One"
        $serial.ReadTimeout = 500
        $serial.ReadBufferSize = 65536
        $serial.Open()
        $serial.DiscardInBuffer()
    } catch {
        Write-Log "WARNING: Cannot open serial port: $_" "DarkYellow"
    }

    # Power ON and read boot log
    & $relayScript -Action on -Port $RelayPort 2>$null
    $powerOnTime = Get-Date

    # Read serial continuously until we see "Waiting for DFU connection" or timeout
    $bootLog = ""
    $dfuReady = $false
    $elapsed = 0
    while ($elapsed -lt $BOOT_TIMEOUT_MS) {
        Start-Sleep -Milliseconds 200
        $elapsed += 200
        if ($serial -and $serial.IsOpen) {
            try {
                if ($serial.BytesToRead -gt 0) {
                    $bootLog += $serial.ReadExisting()
                }
            } catch {}
        }
        if ($bootLog -match [regex]::Escape($DFU_WAIT_PATTERN)) {
            $dfuReady = $true
            break
        }
    }

    $bootTimeMs = ((Get-Date) - $powerOnTime).TotalMilliseconds

    # === Phase 2: Analyze boot log ===
    $flashStatus = "NO_LOG"
    if ($bootLog -match "NOR FLASH CORRUPTED|ALL 0xFF|FW LOST") {
        $flashStatus = "CORRUPTED"
        $failCount++
    } elseif ($bootLog -match "NOR Flash OK") {
        $flashStatus = "OK"
        $okCount++
    } elseif ($bootLog -match "NOR Flash read FAILED") {
        $flashStatus = "READ_FAIL"
        $failCount++
    } elseif ($bootLog -match "Invalid stack pointer|Invalid reset vector") {
        $flashStatus = "HEADER_BAD"
        $failCount++
    } else {
        $noLogCount++
    }

    # Extract reset reason and boot cycle
    $resetReason = ""
    if ($bootLog -match "Reset flags.*: (0x[0-9A-Fa-f]+)") {
        $resetReason = $Matches[1]
    }
    $bootCycle = ""
    if ($bootLog -match "Boot cycle: (\d+)") {
        $bootCycle = $Matches[1]
    }

    # Log result
    $color = switch ($flashStatus) {
        "OK"        { "Green" }
        "CORRUPTED" { "Red" }
        "READ_FAIL" { "Red" }
        "HEADER_BAD"{ "Red" }
        default     { "DarkGray" }
    }
    Write-Log "  Flash: $flashStatus | Reset: $resetReason | BootCycle: $bootCycle | DFU_ready: $dfuReady (${bootTimeMs}ms) | OK:$okCount FAIL:$failCount NOLOG:$noLogCount" $color

    # === Status file events ===
    if ($flashStatus -eq "CORRUPTED" -or $flashStatus -eq "HEADER_BAD" -or $flashStatus -eq "READ_FAIL") {
        Write-Log "!!! FLASH FAILURE ($flashStatus) at cycle $i !!!" "Red"
        Write-Log "  >>> NOR Flash FW loss REPRODUCED! <<<" "Red"
        Write-Log $bootLog "Red"

        Write-Status -Event "FAIL" -Cycle $i -OkCount $okCount -FailCount $failCount -NoLogCount $noLogCount `
            -FlashStatus $flashStatus -BootLog $bootLog -ActualOnMs ([int]$bootTimeMs) -ActualOffMs $curOffMs

        # Auto-post to JIRA
        Post-JiraFailure -Cycle $i -FlashStatus $flashStatus -BootLog $bootLog `
            -OkCount $okCount -FailCount $failCount -NoLogCount $noLogCount
    }

    if ($flashStatus -eq "NO_LOG") {
        $consecutiveNoLog++
        Write-Log "!!! NO_LOG at cycle $i (${bootTimeMs}ms) - bootloader should always print! !!!" "Red"
        Write-Status -Event "NO_LOG" -Cycle $i -OkCount $okCount -FailCount $failCount -NoLogCount $noLogCount `
            -FlashStatus "NO_LOG" `
            -BootLog "NO BOOT LOG at cycle $i - boot ${bootTimeMs}ms (consecutive:${consecutiveNoLog})" `
            -ActualOnMs ([int]$bootTimeMs) -ActualOffMs $curOffMs
    } else {
        $consecutiveNoLog = 0
    }

    if ($okCount -gt 0 -and ($okCount % 100 -eq 0) -and $flashStatus -eq "OK") {
        Write-Status -Event "MILESTONE" -Cycle $i -OkCount $okCount -FailCount $failCount -NoLogCount $noLogCount `
            -FlashStatus "OK" -ActualOnMs ([int]$bootTimeMs) -ActualOffMs $curOffMs
    }

    # Save boot log to file
    if ($bootLog) {
        "--- Cycle $i (boot:${bootTimeMs}ms off:${curOffMs}ms) ---" | Out-File -Append $logFile -Encoding UTF8
        $bootLog | Out-File -Append $logFile -Encoding UTF8
    }

    # === Phase 3: DFU re-flash (every cycle, regardless of flash health) ===
    if ($serial -and $serial.IsOpen) { try { $serial.Close() } catch {} }

    # Wait for USB DFU device to enumerate (bootloader is in DFU mode but Windows needs time)
    Start-Sleep -Seconds 2

    if (-not $dfuReady) {
        Write-Log "  WARNING: DFU not ready (no '$DFU_WAIT_PATTERN' seen), trying anyway..." "DarkYellow"
        Start-Sleep -Seconds 2
    }

    Write-Log "  DFU flash..." "Cyan"
    $dfuOk = Invoke-DfuFlash -Attempt 1
    if (-not $dfuOk) {
        Write-Log "  DFU retry in 5s..." "Yellow"
        Start-Sleep -Seconds 5
        $dfuOk = Invoke-DfuFlash -Attempt 2
    }
    if (-not $dfuOk) {
        Write-Log "ERROR: DFU flash failed after 2 attempts. Stopping." "Red"
        Write-Status -Event "DFU_FAIL" -Cycle $i -OkCount $okCount -FailCount $failCount -NoLogCount $noLogCount `
            -FlashStatus "DFU_FLASH_FAILED" -ActualOnMs ([int]$bootTimeMs) -ActualOffMs $curOffMs
        exit 1
    }
    Write-Log "  DFU flash OK" "Green"

    # === Phase 4: Fuzzy delay after DFU 100%, then power cut (next cycle) ===
    # The real test: how soon after DFU write can we cut power without corrupting NOR flash?
    $runMs = $random.Next($FuzzyRunMin, $FuzzyRunMax + 1)
    Write-Log "  DFU done — cutting power in ${runMs}ms" "DarkYellow"
    Start-Sleep -Milliseconds $runMs
}

Write-Log "" "Cyan"
Write-Log "========================================" "Cyan"
Write-Log "Stress Test Complete" "Cyan"
Write-Log "========================================" "Cyan"
Write-Log "Total cycles: $($i - 1)"
Write-Log "  OK: $okCount"
Write-Log "  FAIL: $failCount"
Write-Log "  NO LOG: $noLogCount"
Write-Log "Log: $logFile"

if ($failCount -eq 0) {
    Write-Log "Result: PASS - No flash corruption detected" "Green"
} else {
    Write-Log "Result: FAIL - $failCount corruptions found!" "Red"
}

# Write final COMPLETE status
Write-Status -Event "COMPLETE" -Cycle $CycleCount -OkCount $okCount -FailCount $failCount -NoLogCount $noLogCount `
    -FlashStatus $(if ($failCount -eq 0) { "PASS" } else { "FAIL" })
