# Reactor Full Build Pipeline
# Usage: .\trigger-reactor-builds.ps1 [-Branch develop] [-RunningMode RUNNING_MODE_APP]
# Triggers: ESP32 → STM32 50W → STM32 100W → OTA 50W → OTA 100W

param(
    [string]$Branch = "develop",
    [string]$RunningMode = "RUNNING_MODE_APP",
    [switch]$SkipESP32,
    [switch]$SkipOTA,
    [switch]$DryRun
)

$JENKINS_URL = "https://jk-builds.positivegrid.com/jenkins"
$JENKINS_USER = "alice.chan@positivegrid.com"
$JENKINS_TOKEN = $env:JENKINS_TOKEN

if (-not $JENKINS_TOKEN) {
    $tokenFile = Join-Path $PSScriptRoot ".jenkins-token"
    if (Test-Path $tokenFile) {
        $JENKINS_TOKEN = (Get-Content $tokenFile -Raw).Trim()
    } else {
        Write-Error "JENKINS_TOKEN env var not set and .jenkins-token file not found."
        Write-Host "Set it: `$env:JENKINS_TOKEN = 'your-token'" -ForegroundColor Yellow
        Write-Host "Or create: $tokenFile" -ForegroundColor Yellow
        exit 1
    }
}

$AUTH = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${JENKINS_USER}:${JENKINS_TOKEN}"))
$HEADERS = @{ "Authorization" = "Basic $AUTH" }

function Get-Crumb {
    try {
        $resp = Invoke-RestMethod -Uri "$JENKINS_URL/crumbIssuer/api/json" -Headers $HEADERS -ErrorAction SilentlyContinue
        return @{ $resp.crumbRequestField = $resp.crumb }
    } catch {
        return @{}
    }
}

function Trigger-Build {
    param([string]$JobName, [hashtable]$Params, [string]$Label)

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Triggering: $Label" -ForegroundColor Cyan
    Write-Host "Job: $JobName" -ForegroundColor Gray
    Write-Host "Params: $($Params | ConvertTo-Json -Compress)" -ForegroundColor Gray
    Write-Host "========================================" -ForegroundColor Cyan

    if ($DryRun) {
        Write-Host "[DRY RUN] Would trigger $JobName" -ForegroundColor Yellow
        return 0
    }

    $crumb = Get-Crumb
    $allHeaders = $HEADERS + $crumb

    $paramList = ($Params.GetEnumerator() | ForEach-Object { "name=$($_.Key)&value=$($_.Value)" }) -join "&"
    $url = "$JENKINS_URL/job/$JobName/buildWithParameters?$paramList"

    try {
        $resp = Invoke-WebRequest -Uri $url -Method POST -Headers $allHeaders -UseBasicParsing
        if ($resp.StatusCode -eq 201) {
            Write-Host "[OK] Build queued!" -ForegroundColor Green
            $queueUrl = $resp.Headers["Location"]
            return $queueUrl
        } else {
            Write-Host "[WARN] Status: $($resp.StatusCode)" -ForegroundColor Yellow
            return $null
        }
    } catch {
        Write-Error "Failed to trigger $JobName : $_"
        return $null
    }
}

function Wait-ForBuild {
    param([string]$JobName, [string]$Label, [int]$TimeoutMinutes = 15)

    Write-Host "Waiting for $Label to complete..." -ForegroundColor Yellow
    $startTime = Get-Date
    $lastBuildBefore = (Invoke-RestMethod -Uri "$JENKINS_URL/job/$JobName/api/json?tree=lastBuild[number]" -Headers $HEADERS).lastBuild.number

    # Wait for new build to start
    $buildNumber = $null
    while (((Get-Date) - $startTime).TotalMinutes -lt $TimeoutMinutes) {
        Start-Sleep -Seconds 10
        try {
            $current = (Invoke-RestMethod -Uri "$JENKINS_URL/job/$JobName/api/json?tree=lastBuild[number]" -Headers $HEADERS).lastBuild.number
            if ($current -gt $lastBuildBefore) {
                $buildNumber = $current
                Write-Host "Build #$buildNumber started" -ForegroundColor Cyan
                break
            }
        } catch { }
        Write-Host "." -NoNewline
    }

    if (-not $buildNumber) {
        Write-Error "Timeout waiting for $Label to start"
        return $null
    }

    # Wait for build to finish
    while (((Get-Date) - $startTime).TotalMinutes -lt $TimeoutMinutes) {
        Start-Sleep -Seconds 15
        try {
            $buildInfo = Invoke-RestMethod -Uri "$JENKINS_URL/job/$JobName/$buildNumber/api/json?tree=result,duration" -Headers $HEADERS
            if ($buildInfo.result) {
                $duration = [math]::Round($buildInfo.duration / 1000)
                if ($buildInfo.result -eq "SUCCESS") {
                    Write-Host "[PASS] $Label #$buildNumber - ${duration}s" -ForegroundColor Green
                } else {
                    Write-Host "[FAIL] $Label #$buildNumber - $($buildInfo.result)" -ForegroundColor Red
                }
                return @{ Number = $buildNumber; Result = $buildInfo.result }
            }
        } catch { }
        Write-Host "." -NoNewline
    }

    Write-Error "Timeout waiting for $Label #$buildNumber to complete"
    return $null
}

# ============================================================
# Main Pipeline
# ============================================================

Write-Host "`n" -NoNewline
Write-Host "================================================" -ForegroundColor Magenta
Write-Host "  Reactor Full Build Pipeline" -ForegroundColor Magenta
Write-Host "  Branch: $Branch | Mode: $RunningMode" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta

$results = @{}

# Step 1: ESP32
if (-not $SkipESP32) {
    Trigger-Build -JobName "REACTOR_ESP32_FW" -Label "ESP32 FW" -Params @{
        BRANCH = $Branch
        DEVICE_NAME = "Reactor 100"
    }
    $results["ESP32"] = Wait-ForBuild -JobName "REACTOR_ESP32_FW" -Label "ESP32 FW"
    $esp32BuildNo = $results["ESP32"].Number
} else {
    Write-Host "`n[SKIP] ESP32" -ForegroundColor DarkGray
    # Get last successful ESP32 build number
    $esp32BuildNo = (Invoke-RestMethod -Uri "$JENKINS_URL/job/REACTOR_ESP32_FW/api/json?tree=lastSuccessfulBuild[number]" -Headers $HEADERS).lastSuccessfulBuild.number
    Write-Host "Using last successful ESP32 build: #$esp32BuildNo" -ForegroundColor Yellow
}

# Step 2: STM32 100W
Trigger-Build -JobName "REACTOR_AMP_FW" -Label "STM32 100W" -Params @{
    BRANCH = $Branch
    DEVICE_NAME = "Reactor 100"
    USER_RUNNING_MODE = $RunningMode
}
$results["STM32_100W"] = Wait-ForBuild -JobName "REACTOR_AMP_FW" -Label "STM32 100W"
$stm32_100w_BuildNo = $results["STM32_100W"].Number

# Step 3: STM32 50W
Trigger-Build -JobName "REACTOR_AMP_FW" -Label "STM32 50W" -Params @{
    BRANCH = $Branch
    DEVICE_NAME = "Reactor 50"
    USER_RUNNING_MODE = $RunningMode
}
$results["STM32_50W"] = Wait-ForBuild -JobName "REACTOR_AMP_FW" -Label "STM32 50W"
$stm32_50w_BuildNo = $results["STM32_50W"].Number

# Step 4 & 5: OTA builds
if (-not $SkipOTA) {
    # OTA 100W
    Trigger-Build -JobName "Release_Reactor_FW_FOR_OTA" -Label "OTA 100W" -Params @{
        PRODUCT_NAME = "Reactor_100"
        PROJ_NAME = "REACTOR_AMP_FW"
        BUILD_NO = $stm32_100w_BuildNo
        ESP32_BUILD_NO = $esp32BuildNo
        TO_PRODUCTION = "False"
    }
    $results["OTA_100W"] = Wait-ForBuild -JobName "Release_Reactor_FW_FOR_OTA" -Label "OTA 100W"

    # OTA 50W
    Trigger-Build -JobName "Release_Reactor_FW_FOR_OTA" -Label "OTA 50W" -Params @{
        PRODUCT_NAME = "Reactor_50"
        PROJ_NAME = "REACTOR_AMP_FW"
        BUILD_NO = $stm32_50w_BuildNo
        ESP32_BUILD_NO = $esp32BuildNo
        TO_PRODUCTION = "False"
    }
    $results["OTA_50W"] = Wait-ForBuild -JobName "Release_Reactor_FW_FOR_OTA" -Label "OTA 50W"
} else {
    Write-Host "`n[SKIP] OTA builds" -ForegroundColor DarkGray
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "================================================" -ForegroundColor Magenta
Write-Host "  Build Summary" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta

foreach ($key in @("ESP32", "STM32_100W", "STM32_50W", "OTA_100W", "OTA_50W")) {
    if ($results.ContainsKey($key)) {
        $r = $results[$key]
        $color = if ($r.Result -eq "SUCCESS") { "Green" } else { "Red" }
        Write-Host "  $key : #$($r.Number) - $($r.Result)" -ForegroundColor $color
    }
}

Write-Host "================================================" -ForegroundColor Magenta
