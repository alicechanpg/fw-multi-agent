---
name: reference-dfu-bootloader-repos
description: 各產品真正的 DFU bootloader = *-external-loader repo（非 app fw、非 ExtMemLoader .stldr）；兩段式啟動 Loader→App，DFU-mode LED 由 bootloader 驅動
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2e3aafce-65f5-45a1-8488-7a83a6e73825
---

**真正的 DFU bootloader（進 DFU、驅動 DFU-mode LED 的那段）= 各產品的 `*-external-loader` repo**（用戶 2026-07-16 強調「external-loader 才是 bootloader」）。**不是** app fw repo，也**不是** STM32CubeProgrammer 用的 `ExtMemLoader/*.stldr`（那只是燒外部 QSPI flash 的 flashloader）。

## 兩段式啟動

Loader（bootloader = external-loader repo）→ jump to Application（app fw repo）。**App fw 不驅動 DFU-mode LED；bootloader 才是。** 例：spark-ii-fw README 明載 loader 是獨立專案；app 的 `enter_fw_update_mode` 只關 audio/input，無任何 LED 呼叫。

## 各產品 bootloader repo 對照

| 產品 | app fw repo | **bootloader (external-loader) repo** | 本機有? |
|------|-------------|----------------------------------------|---------|
| Reactor 50/100 | reactor-fw | **reactor-external-loader**（`/Boot`：Core/Source/USB_DEVICE） | ✅ 本機 |
| Spark LIVE / EDGE | spark-pedal-fw | **spark-pedal-external-loader**（Core/Src, Source/） | ✅ 本機 |
| Spark 2 (gen2) | spark-ii-fw | **spark-speaker-gen2-external-loader**（GitLab `jamup-speaker` group，需 clone） | ❌ 需用 [[reference_dfu_flash]] 的 gitlab-token clone |

（另 `g1x-bootloader` 是舊 STM32F4 平台 bootloader，與上述 H7/H750 產品不同代。）

## DFU-mode LED ground truth（用戶實機觀察）

- **Reactor**：WiFi LED + BLE LED 一起 blink **白（white）**。⚠️ **與本機 source 衝突**：`reactor-external-loader/Boot` 只驅動單顆 **Power LED (PD10, net `LED_UPDATE`)** active-low ~500ms 慢閃（`main.c:195-199,439-465`、`tim.c:44-46`），無 wifi/ble/白色邏輯 → 疑本機 repo 為舊版（memory 記量產版 0.1.0.39 / local 0.1.0.0），或 wifi+ble 白由 ESP32/他處驅動。**以實機觀察為準**，source 待對齊。
- **Spark 2**：power button 閃**紅（blink red）**。bootloader 在 GitLab `spark-speaker-gen2-external-loader`（本機無，clone 驗證中）。
- **Spark LIVE / EDGE**：查 `spark-pedal-external-loader`（進行中）

→ 影響 ReactorFwUpdater 的 manual-DFU 指示文字：LED 說明**應 per-product**，不能一句 spark 通用（我先前把 spark 分支改成 "Wi-Fi LED and Bluetooth LED blink" 對 Spark 2 是錯的，Spark 2 應為 power button 紅閃）。見 [[project_fwp814_spark_integration]]。

相關：[[reference_pg_usb_hub_architecture]]、[[reference_reactor_extmemloader_stldr]]（那個是 .stldr，別混淆）、[[reference_dfu_flash]]
