# STM32 Bootloader Build Script
# Usage: powershell -ExecutionPolicy Bypass -File build-bootloader.ps1 [-Clean] [-ReactorVersion <50|100>] [-PatchVersion]
#
# Examples:
#   .\build-bootloader.ps1                          # Incremental build, 100W (default)
#   .\build-bootloader.ps1 -Clean                   # Clean build
#   .\build-bootloader.ps1 -ReactorVersion 50       # Build for 50W
#   .\build-bootloader.ps1 -PatchVersion            # Patch version.h with git commit count
#   .\build-bootloader.ps1 -Clean -ReactorVersion 50 -PatchVersion  # Full release build

param(
    [switch]$Clean,
    [ValidateSet("50", "100")]
    [string]$ReactorVersion = "100",
    [switch]$PatchVersion
)

$STM32_IDE = "C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\stm32cubeide.exe"
$STM32_WORKSPACE = "D:\mybot\git\tool\stm32-workspace-bootloader"
$STM32_PROJECT_PATH = "D:\mybot\git\reactor-external-loader"
$STM32_PROJECT = "reactor-external-loader_Boot"
$STM32_CONFIG = "Debug"
$STM32_BIN = "D:\mybot\git\reactor-external-loader\Boot\Debug\reactor-external-loader_Boot.bin"

$VERSION_H = "$STM32_PROJECT_PATH\Boot\Source\Common\config\version.h"
$USER_CONFIG_H = "$STM32_PROJECT_PATH\Boot\Source\Common\config\user_config.h"

# --- Version patching (changes stay in repo, use git to manage) ---
if ($PatchVersion) {
    Write-Host "Patching version.h with git commit count..." -ForegroundColor Yellow
    $versionContent = Get-Content $VERSION_H -Raw

    Push-Location $STM32_PROJECT_PATH
    $commitCount = (git rev-list --count HEAD 2>$null)
    Pop-Location

    if ($commitCount) {
        $patched = $versionContent -replace '#define GIT_COMMIT_COUNT\s+\d+', "#define GIT_COMMIT_COUNT $commitCount"
        Set-Content -Path $VERSION_H -Value $patched -NoNewline
        Write-Host "  GIT_COMMIT_COUNT = $commitCount" -ForegroundColor Cyan
    } else {
        Write-Warning "Could not get git commit count, skipping version patch"
    }
}

if ($ReactorVersion -eq "50") {
    Write-Host "Patching user_config.h for Reactor 50W..." -ForegroundColor Yellow
    $userConfigContent = Get-Content $USER_CONFIG_H -Raw

    $patched = $userConfigContent -replace '#define USER_CONFIG_REACTOR_VERSION\s+REACTOR_\d+W', '#define USER_CONFIG_REACTOR_VERSION REACTOR_50W'
    Set-Content -Path $USER_CONFIG_H -Value $patched -NoNewline
    Write-Host "  USER_CONFIG_REACTOR_VERSION = REACTOR_50W" -ForegroundColor Cyan
}

# --- Build ---
Write-Host ""
Write-Host "Building STM32 Bootloader..." -ForegroundColor Yellow
Write-Host "Project: $STM32_PROJECT_PATH"
Write-Host "Configuration: $STM32_CONFIG"
Write-Host "Reactor: ${ReactorVersion}W"

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

# Build arguments
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

# Check if build succeeded
$buildSuccess = $false
if (Test-Path $STM32_BIN) {
    $binInfo = Get-Item $STM32_BIN
    $wasUpdated = ($beforeTime -eq $null) -or ($binInfo.LastWriteTime -gt $beforeTime)

    if ($wasUpdated) {
        Write-Host "Binary UPDATED: $STM32_BIN" -ForegroundColor Green
        $buildSuccess = $true
    } else {
        Write-Host "Binary unchanged (build may have failed)" -ForegroundColor Yellow
    }
    Write-Host "Size: $($binInfo.Length) bytes"
    Write-Host "Modified: $($binInfo.LastWriteTime)"
} else {
    Write-Host "Binary not found after build." -ForegroundColor Red

    # First build often fails due to -importAll corrupting .cproject, retry with clean
    if (-not $Clean) {
        Write-Host ""
        Write-Host "First build may fail due to importAll issue. Retrying with cleanBuild..." -ForegroundColor Yellow

        $retryArgs = @(
            "--launcher.suppressErrors",
            "-nosplash",
            "-application", "org.eclipse.cdt.managedbuilder.core.headlessbuild",
            "-data", $STM32_WORKSPACE,
            "-cleanBuild", "$STM32_PROJECT/$STM32_CONFIG"
        )

        $process = Start-Process -FilePath $STM32_IDE -ArgumentList $retryArgs -NoNewWindow -Wait -PassThru
        Write-Host "Retry build exit code: $($process.ExitCode)"

        if (Test-Path $STM32_BIN) {
            $binInfo = Get-Item $STM32_BIN
            Write-Host "Binary CREATED after retry: $STM32_BIN" -ForegroundColor Green
            Write-Host "Size: $($binInfo.Length) bytes"
            $buildSuccess = $true
        } else {
            Write-Error "Build failed even after retry!"
        }
    }
}

# --- Rename output binary ---
if ($buildSuccess) {
    # Read version info
    $versionContent = Get-Content $VERSION_H -Raw
    $major = [regex]::Match($versionContent, '#define MAJOR_VERSION\s+(\d+)').Groups[1].Value
    $minor = [regex]::Match($versionContent, '#define MINOR_VERSION\s+(\d+)').Groups[1].Value
    $commits = [regex]::Match($versionContent, '#define GIT_COMMIT_COUNT\s+(\d+)').Groups[1].Value

    $outputName = "reactor${ReactorVersion}-bootloader-${major}.${minor}.0.${commits}.bin"
    $outputPath = Join-Path (Split-Path $STM32_BIN) $outputName

    Copy-Item $STM32_BIN $outputPath -Force
    Write-Host ""
    Write-Host "Output: $outputPath" -ForegroundColor Green
}

if ($buildSuccess) {
    exit 0
} else {
    exit 1
}
