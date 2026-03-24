# STM32 Build Script
# Usage: powershell -ExecutionPolicy Bypass -File build-stm32.ps1 [-Clean]

param(
    [switch]$Clean
)

$STM32_IDE = "C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\stm32cubeide.exe"
$STM32_WORKSPACE = "D:\mybot\git\tool\stm32-workspace"
$STM32_PROJECT_PATH = "D:\mybot\git\reactor-50-100-fw"
$STM32_PROJECT = "reactor-fw_Appli"
$STM32_CONFIG = "Debug"
$STM32_BIN = "D:\mybot\git\reactor-50-100-fw\Appli\Debug\reactor-fw_Appli.bin"

Write-Host "Building STM32 firmware..." -ForegroundColor Yellow
Write-Host "Project: $STM32_PROJECT_PATH"
Write-Host "Configuration: $STM32_CONFIG"

# Create workspace directory if not exists
if (-not (Test-Path $STM32_WORKSPACE)) {
    New-Item -ItemType Directory -Path $STM32_WORKSPACE -Force | Out-Null
    Write-Host "Created workspace: $STM32_WORKSPACE"
}

# Record binary timestamp before build
$beforeTime = $null
if (Test-Path $STM32_BIN) {
    $beforeTime = (Get-Item $STM32_BIN).LastWriteTime
}

# Build arguments - import project and build
$buildArgs = @(
    "--launcher.suppressErrors",
    "-nosplash",
    "-application", "org.eclipse.cdt.managedbuilder.core.headlessbuild",
    "-data", $STM32_WORKSPACE,
    "-importAll", $STM32_PROJECT_PATH
)

if ($Clean) {
    $buildArgs += "-cleanBuild"
    $buildArgs += "$STM32_PROJECT/$STM32_CONFIG"
    Write-Host "Mode: Clean Build"
} else {
    $buildArgs += "-build"
    $buildArgs += "$STM32_PROJECT/$STM32_CONFIG"
    Write-Host "Mode: Incremental Build"
}

Write-Host "Running CubeIDE headless build..."

$process = Start-Process -FilePath $STM32_IDE -ArgumentList $buildArgs -NoNewWindow -Wait -PassThru

Write-Host "Build exit code: $($process.ExitCode)"

if (Test-Path $STM32_BIN) {
    $binInfo = Get-Item $STM32_BIN
    $wasUpdated = ($beforeTime -eq $null) -or ($binInfo.LastWriteTime -gt $beforeTime)

    if ($wasUpdated) {
        Write-Host "Binary UPDATED: $STM32_BIN" -ForegroundColor Green
    } else {
        Write-Host "Binary unchanged: $STM32_BIN" -ForegroundColor Yellow
    }
    Write-Host "Size: $($binInfo.Length) bytes"
    Write-Host "Modified: $($binInfo.LastWriteTime)"
    exit 0
} else {
    Write-Error "STM32 binary not found: $STM32_BIN"
    exit 1
}
