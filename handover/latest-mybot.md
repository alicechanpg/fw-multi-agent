# Session Handover (mybot) — 2026-06-24 09:10

## 本次完成
- FWP-814: Spark LIVE/2/EDGE 加入 ReactorFwUpdater — **第一版（compile-time branching）已完成但架構錯誤**
- Branch `feature/FWP-814-spark-products` 已 push（compile-time `#ifdef SPARK_FLOW`，3 個分開 build）
- 用戶要求改為 **unified build**（`-DPRODUCT=spark`，runtime auto-detect，像 Reactor 支援 R50+R100）
- 寫了新版 design document：`D:\mybot\git\ReactorFwUpdater\docs\FWP-814-spark-unified-design.md`
- JIRA FWP-814 已加 comment：implementation 完成 + icon 需求

## 未完成 / 進行中
| 項目 | 狀態 | 下一步 |
|------|------|--------|
| Unified Spark build | Design doc 完成，待實作 | 照 design doc 在 `feature/skip-esp32-unified` branch 實作 |
| Runtime auto-detect | 設計完成 | 加 `usb::findSparkPid()` 掃 USB PID (0x0222/0x0232/0x0252) |
| `#ifdef` → runtime | 設計完成 | 所有 `#ifdef SPARK_FLOW` 改成 `getProductConfig().isSparkFlow()` |
| App icon | JIRA comment 已寫 | 等設計團隊提供 |

## 環境狀態
- 當前 branch: `feature/skip-esp32-unified`（已切回，準備在此 branch 實作）
- `feature/FWP-814-spark-products` branch 存在但架構錯誤（compile-time），**不要用**
- Firmware 已下載到 `D:\mybot\git\ReactorFwUpdater\Images/` (spark-live, spark-2, spark-edge)
- Assets 已在 `D:\mybot\git\ReactorFwUpdater\Assets/` (spark_*.png)
- Build 環境已驗證：VS2022 + CMake 可 build 所有產品

## 給下個 session 的備註

### 📄 Design Document 位置
**`D:\mybot\git\ReactorFwUpdater\docs\FWP-814-spark-unified-design.md`**

這是 unified Spark build 的完整設計，包含：
- Runtime detection 架構（掃 USB PID 偵測 LIVE/2/EDGE）
- 每個檔案要改什麼（13 個檔案的具體修改說明）
- State machine flow（Spark vs Reactor 對比）
- USB PID 對照表
- Firmware 打包結構

### 關鍵設計決策
1. **NO `#ifdef SPARK_FLOW`** — 全部用 runtime `getProductConfig().isSparkFlow()`
2. **Auto-detect** — `usb::findSparkPid(vid)` 掃 0x0222/0x0232/0x0252，跟 `findBtAudioPid()` 同模式
3. **products.json** 加 "spark" unified entry，`updateFlow: "spark"`
4. **EspWrapper** port-optional：Spark 不傳 `--port`（auto-detect），Reactor 必須傳
5. **DfuWrapper** 用 `config.fwBinName` 取代 hardcoded "mcu-fw.bin"

### 已有的資源（不用重新下載）
- Jenkins firmware: `Images/spark-live/`, `Images/spark-2/`, `Images/spark-edge/`
- Product images: `Assets/spark_*.png`（從 SparkLiveFwUpgradeLauncher 複製）
- App icons: placeholder（等設計團隊）

### 已驗證的事實
- Spark normal-mode PID == DFU PID（已從 SparkLiveFwUpgradeLauncher source 驗證，`dfu-util` 靠 USB class 區分）
- `findBtAudioPid()` 用 libwdi `wdi_create_list` 掃 USB — 同機制可掃 Spark PID
- Reactor unified build 不受影響（`isSparkFlow()` 只在 updateFlow=="spark" 時 true）
