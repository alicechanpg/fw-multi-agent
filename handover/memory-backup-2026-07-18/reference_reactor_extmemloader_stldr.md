---
name: Reactor H7R3 ExtMemLoader stldr 位置
description: STLink 燒 reactor-50-100-fw external NOR @ 0x90000000 需要的 ExtMemLoader stldr 位置和共用情形
type: reference
originSessionId: a24b5d2f-3d02-4ae1-9f2c-89e98777117e
---
要用 STLink (STM32_Programmer_CLI) 燒 Reactor (H7R3 + Winbond NOR @ 0x90000000) external flash，需要對應 chip 的 ExtMemLoader `.stldr`。

## 既存 stldr 位置（**驗證為 H7R3 可用**）

`D:\mybot\git\reactor-fw\ExtMemLoader\Debug\reactor-fw_ExtMemLoader.stldr` (1.8 MB, 2026-03-17 build)

驗證證據：
- `reactor-fw/ExtMemLoader/STM32H7R3I8TX_extmemloader_default.ld` ← H7R3 chip
- `diff -rq reactor-fw/ExtMemLoader/Core reactor-50-100-fw/ExtMemLoader/Core` → identical
- `diff -rq reactor-fw/ExtMemLoader/Drivers vs reactor-50-100-fw/ExtMemLoader/Drivers` → identical
- `diff -rq reactor-fw/ExtMemLoader/Middlewares vs reactor-50-100-fw/ExtMemLoader/Middlewares` → identical

## 不能用的 stldr（H750，chip 不同）

- `D:\mybot\git\spark-ii-fw\W25Q32JV_STM32H750.stldr`
- `D:\mybot\git\spark-pedal-fw\W25Q32JV_STM32H750.stldr`
- `D:\mybot\git\spark-pedal-external-loader\QSPI_H750XB_EN25Q80C_flashloader_CSP.stldr`
- CubeProgrammer 內建 `W25Q*_STM32F7*.stldr`（F7 系列，不是 H7R3）

## 注意

- `reactor-50-100-fw/ExtMemLoader/Debug/` 不存在 — 該 repo 從未 local build 過 ExtMemLoader
- `reactor-fw_ExtMemLoader.stldr` 本身不在 git tracked，是 build artifact (`postbuild.sh` 把 `.elf` 副檔名改成 `.stldr`)
- Downloads 也有 `C:\Users\alice\Downloads\reactor-fw\reactor-fw\ExtMemLoader\Debug\reactor-fw_ExtMemLoader.stldr` 但 build 較舊 (2025-10-08)，優先用 D: 的新版
- `flash-and-reset-stm32.ps1` 內 hardcoded EXT_LOADER 路徑指向 Downloads 舊版，要燒 reactor-50-100-fw 建議**直接 inline call** STM32_Programmer_CLI 用 D: 路徑，不改 script
