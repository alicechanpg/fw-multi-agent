---
name: Reactor STLink flash 完整指令
description: STLink (STM32_Programmer_CLI) 燒 reactor-50-100-fw external NOR @ 0x90000000 的指令模式
type: reference
originSessionId: a24b5d2f-3d02-4ae1-9f2c-89e98777117e
---
## 指令模式

```powershell
$prog = "C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.1.400.202404281720\tools\bin\STM32_Programmer_CLI.exe"
$bin = "D:\mybot\git\reactor-50-100-fw\Appli\Debug\reactor-fw_Appli.bin"
$extLoader = "D:\mybot\git\reactor-fw\ExtMemLoader\Debug\reactor-fw_ExtMemLoader.stldr"

& $prog -c port=SWD ap=1 mode=UR -el "$extLoader" -d "$bin" 0x90000000 -v
```

## 關鍵要素

- `port=SWD ap=1` — H7R3 用 AP 1（M7 core），不是 default AP 0
- `mode=UR` — Under Reset，比 HOTPLUG 可靠（不依賴 MCU responsive state）
- `-el <stldr>` — 必須帶 ExtMemLoader (H7R3 + Winbond)，不然寫不到 0x90000000
- `0x90000000` — Reactor external XSPI NOR base address
- `-v` — verify after write
- **不要帶 `--mass-erase`** — `-el` 配 stldr 已自動 erase external NOR sectors，加 mass-erase 會誤擦 internal flash 上的 bootloader

## 驗證 success 訊號

```
Device ID    : 0x485
Revision ID  : Rev B
Device name  : STM32H7RSxx     ← H7R3 family confirmed
...
Erasing external memory sectors [0 315]
File download complete
Time elapsed: 00:00:23.557
Download verified successfully
```

## 後續流程

STLink mode=UR 燒完後 STM32 處於 reset 釋放狀態，會自動 boot。但 ESP32 EN 由 STM32 控制，**最穩做法是 USB Relay power cycle**（`off → on`）再進行 ESP32 燒錄或 boot log 抓取。

flash-and-reset-stm32.ps1 已內建這流程但 hardcoded 舊 stldr 路徑指向 Downloads，建議直接 inline call STM32_Programmer_CLI 用 D: 路徑。

## STM32 boot log 期望

開 COM4 (STLink VCP) @ 921600 看到：
```
Reactor 50w Bootloader_version: 0.1.0.39
RUNNING_MODE : LOADER_DEBUG  
Jump to APP code (4MB NOR)

RUNNING_MODE : APP_DEBUG       ← debug build only
Reactor 100w fw_version: 0.1.x.x   ← debug build only, label "100w" is generic regardless of R50/R100
```

**Release build (RUNNING_MODE_APP) 不輸出 UART**，"Jump to APP code" 後 silent 是正常的。
