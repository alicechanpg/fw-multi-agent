---
name: FWP-744 ReactorFwUpdater 環境建置
description: ReactorFwUpdater 專案的 build 環境、Jenkins jobs、patch 狀態
type: project
---

FWP-744: ReactorFwUpdater — Apply Teo's patch & 環境建置

**Why:** Teo 3/11 交辦、3/17 提供 patch，UI 改版未完成暫用 patch 方式提供。

**How to apply:** 處理此 ticket 或相關 build 時參考。

## Repo
- Path: `D:\mybot\git\ReactorFwUpdater`
- Branch: dev @ 86e3027
- GitHub: Positive-LLC/ReactorFwUpdater

## Build 需求
- CMake 3.22+（已裝 4.3.0 via pip）
- VS2022 BuildTools + C++ workload（**未裝，需 admin 權限**）
- VS2019 BuildTools 已有但缺 C++ workload
- MSYS2 MinGW64 gcc 壞了（0xC0000139 DLL issue），不可用

## Teo's Patch (3/17)
- reactor-new-assets.tar → 解壓到 repo（新 reactor 圖片取代 spark_live_*）
- reactor-ui-updates.patch → git apply
- 來源：Slack DM with Teo (2026-03-17 10:42)
- 狀態：**未 apply**（需手動從 Slack 下載）

## Jenkins Jobs
- REACTOR_FW_UPDATER_WIN: Build#29 SUCCESS（參數: BRANCH, PRODUCT, MCU_BUILD, ESP_BUILD, SIGN）
- REACTOR_FW_UPDATER_OSX: Build#33 SUCCESS
- SPARK_LIVE_FW_UPDATER_WIN/OSX: Build#117/#124（原始 codebase，多產品分支）
- RIFF_FW_UPDATER_WIN/OSX: 2021 年停止維護

## Scripts Created
- `setup_env.ps1` — 安裝 VS2022 BuildTools（需 admin 執行）
- `build_local.bat` — 本地 build（VS2022 generator）
- `apply_and_build.bat` — 一鍵 apply patch + build
