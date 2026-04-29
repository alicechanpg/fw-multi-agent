# Session Handover (mybot) — 2026-04-01 00:00

## Done
- **Spark Pedal FW 環境建置（Teo 指派）：**
  - Clone spark-pedal-fw repo 到 `D:\mybot\git\spark-pedal-fw\` (from GitLab)
  - 處理 4 個 submodule (MsgPack, PGLooper, pg-utilities, PGMetronome) — SSH→HTTPS 轉換成功
  - 觸發 Jenkins SPARK_PEDAL_FW build #6 (BRANCH=develop) — SUCCESS
  - 下載 ARM GCC 10.3-2021.10 到 `C:\ST\gcc-arm-none-eabi-10.3-2021.10\`
  - 本地 build spark-pedal-fw 成功 (GCC 10.3 + make)
    - Output: `D:\mybot\git\spark-pedal-fw\Debug\spark-pedal-fw.bin`
    - Size: text 915KB, data 1.9KB, bss 426KB, total 1.29MB
  - 確認 Spark Pedal ESP32 repo = `wifi-and-bt-core-on-esp32` (已有 clone)
  - 確認 Spark Pedal 完整 FW 三個 repo：
    1. `spark-pedal-fw` (STM32 H750 主控) — 已 clone + build
    2. `wifi-and-bt-core-on-esp32` (ESP32 藍牙/WiFi) — 已有 clone
    3. `spark-pedal-external-loader` (Bootloader) — 尚未 clone

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| ESP32 build for Pedal | 未開始 | 切 develop，用 DEVICE_NAME=Spark PEDAL build |
| Bootloader repo | 未 clone | Clone spark-pedal-external-loader if needed |
| SG-7 實機測試 | Code ready | Build + Flash Spark 2 #1 → 連 Spark 2 #2 測試 |
| FWP-744 VS2022 | setup_env.ps1 已跑 | 確認 VS2022 是否安裝成功 |

## Environment
- mybot: master
- spark-pedal-fw: develop @ a0b8a07
- wifi-and-bt-core-on-esp32: feature/SG-7-smart-guitar-poc @ 0c38d44 (develop available)
- spark-ii-fw: develop
- GCC 10.3 installed: `C:\ST\gcc-arm-none-eabi-10.3-2021.10\`
- Jenkins SPARK_PEDAL_FW Build #6: SUCCESS
- Hardware: N/A (no flash done)

## Notes for next session
- **本地 build spark-pedal-fw 流程：**
  1. `export PATH="/c/ST/gcc-arm-none-eabi-10.3-2021.10/bin:$PATH"`
  2. 先用 CubeIDE headless (暫改 .cproject 到 12.3) 生成 Debug/Makefile
  3. 還原 .cproject，從 subdir.mk 移除 `-fcyclomatic-complexity`
  4. `find . -name "*.o" | sort > objects.list`
  5. 用 CubeIDE 的 make + GCC 10.3 build
- **Make 路徑:** `/c/ST/STM32CubeIDE_1.16.1/STM32CubeIDE/plugins/com.st.stm32cube.ide.mcu.externaltools.make.win32_2.1.300.202402091052/tools/bin/make.exe`
- **GCC 12 vs 10 問題：** GCC 12 移除隱式 header include，submodule 編譯失敗；需用 GCC 10.3
- **Jenkins jobs:**
  - SPARK_PEDAL_FW: BRANCH=develop
  - SPARK_ESP32_FW: BRANCH=develop, DEVICE_NAME=Spark PEDAL
  - SPARK_PEDAL_BOOTLOADER_FW: BRANCH=develop
- **submodule SSH→HTTPS:** `git config url."https://git.positivegrid.com:8443/".insteadOf "git@git.positivegrid.com:8022:"`
- Kevin Huang (PM): U0103Q0MW6A, mikelee: U3HBR7F7U, Teo: U09J2791SR0
