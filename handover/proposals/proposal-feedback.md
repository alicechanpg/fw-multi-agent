# Fact/Rule Split Proposal — 7 memory files

Read-only review. No memory files were modified. Nothing was written to the registry.

---

### feedback_always_capture_log.md
**建議:** rule-only
**事實:** 無 — 檔案核心是行為指令（flash 後自動抓 log，不要問）。內文提到的 `COM4, 921600, 60秒` 是執行這條規則時的參數範例，不是獨立、可驗證的世界事實陳述；COM4 本身已知會因重插而變（見其他 memory），921600 baud 沒有被當作獨立聲明提出，只是操作細節的一部分。

**守則（留在 SOP）:** Flash + power cycle 完成後，一律自動啟動 serial logger（不需詢問使用者）。
**不確定的地方:** `COM4, 921600, 60秒` 是否該被拆成獨立事實（例如「STM32 debug serial baud = 921600」）見仁見智——我判斷它在本檔案中只是規則的執行參數，不是被陳述為值得單獨記錄的世界事實，所以沒有提出 JSON。如果 reviewer 認為 baud rate 本身值得存，需要另外從更明確的來源確認。

---

### feedback_check_hardware_pid.md
**建議:** split

**事實:**
```json
{"key": "COM:USB_RELAY", "scope": "Reactor rig", "fact": "USB Relay serial adapter enumerated as COM3 (observed value; must be re-probed, not cached).", "source": "feedback_check_hardware_pid.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": true, "probe": "Get-PnpDevice -Class Ports, match the USB Relay adapter's VID/PID", "confidence": "reported"}
```
> 出處原文: "USB Relay: COM3"

```json
{"key": "COM:STLINK", "scope": "Reactor rig", "fact": "STLink debug probe enumerated as COM50 (observed value; must be re-probed, not cached).", "source": "feedback_check_hardware_pid.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": true, "probe": "Get-PnpDevice -Class Ports, match STLink VCP VID/PID", "confidence": "reported"}
```
> 出處原文: "STLink: COM50"

```json
{"key": "COM:ESP32", "scope": "Reactor", "fact": "ESP32 enumerated as COM19 (observed value; must be re-probed, not cached).", "source": "feedback_check_hardware_pid.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": true, "probe": "python -c \"import serial.tools.list_ports; ...\" matching ESP32 VID, or Get-PnpDevice -Class Ports", "confidence": "reported"}
```
> 出處原文: "ESP32: COM19"

**守則（留在 SOP）:** 不要停下來問用戶「硬體接好了嗎」，改用 `Get-PnpDevice -Class Ports` 或 `python serial.tools.list_ports` 自行查 PID/VID 確認後直接動作。
**不確定的地方:** 這三個 COM 號碼本身已經跟目前 MEMORY.md 的 COM Port 表衝突（MEMORY 記的是 STLink=COM4、ESP32=COM7，這裡是 COM50/COM19），正好印證「Port 號碼會因重插而變」——這三筆數字很可能已經過期。我仍照 schema 要求把它們列成 `volatile:true` + `probe` 的 fact，但真正該存的「事實」其實是識別方法（VID/PID + 指令），不是這次觀察到的號碼本身；是否要保留這三個具體號碼、或只留 probe 方法不留舊值，建議 reviewer 決定。

---

### feedback_flash_reset.md
**建議:** split

**事實:**
```json
{"key": "FLASH:POWER_CYCLE_REQUIRED", "scope": "STM32H7R3", "fact": "After writing STM32 external NOR flash, a full power cycle (not just a soft reset) is required for the MCU to correctly load the new firmware.", "source": "feedback_flash_reset.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "NOR Flash 寫入後 MCU 需要完整 power cycle 才能正確載入新 firmware。只靠 soft reset 不夠，要斷電重啟。"

**守則（留在 SOP）:** 每次 flash STM32 後執行完整 power cycle（USB Relay off → 等 1 秒 → on），不要只用 pulse；`flash-and-reset-stm32.ps1` 目前用 pulse 但 Alice 偏好 off→1s→on。
**不確定的地方:** 檔案沒有明講這條 NOR Flash 規則適用於哪個具體 chip/產品，我依照「USB Relay COM3 = Reactor rig」的脈絡假設 scope 是 STM32H7R3（reactor-fw），這是推論不是檔案明文陳述，請 reviewer 確認 scope 是否正確。另外「pulse 不足夠」這件事本身檔案並未證實——只說了 Alice 偏好 off→1s→on，這段我歸類為守則（偏好），不是事實。

---

### feedback_power_cycle_when_no_com.md
**建議:** split

**事實:**
```json
{"key": "ESP32:EN_PIN_CONTROL", "scope": "Reactor", "fact": "On Reactor, the ESP32's EN (enable) pin is controlled by the STM32; the ESP32 does not power on / enumerate until the STM32 has booted.", "source": "feedback_power_cycle_when_no_com.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "Reactor 的 ESP32 EN pin 由 STM32 控制，STM32 開機後 ESP32 才會出現。"

**守則（留在 SOP）:** flash ESP32 前若 COM19（ESP32 port）找不到，先用 USB Relay (COM3) 做 power cycle、等 port 出現再 flash，不要停下來問用戶手動上電。
**不確定的地方:** 無。這條事實與 MEMORY.md 已存在的 `reference_reactor_esp32_power.md` 內容一致，但本檔案本身沒有展示驗證步驟（沒有 schematic 或量測輸出），所以 confidence 標 `reported` 而非 `verified`。

---

### feedback_production_stm32_no_log.md
**建議:** split

**事實:**
```json
{"key": "UART:PRODUCTION_MODE", "scope": "Reactor", "fact": "STM32 firmware running in production/release mode (RUNNING_MODE_APP) outputs no UART log; only APP_DEBUG-mode builds output UART logs.", "source": "feedback_production_stm32_no_log.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "Production 版本 STM32 firmware 沒有 UART log 輸出... STM32 從 APP_DEBUG 變成 RUNNING_MODE_APP，UART 完全靜默。"

```json
{"key": "OTA:MODE_TRANSITION", "scope": "Reactor", "fact": "Installing an OTA-delivered production firmware binary switches the STM32 from APP_DEBUG mode to RUNNING_MODE_APP.", "source": "feedback_production_stm32_no_log.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "OTA 下載的是 production binary，安裝後 STM32 從 APP_DEBUG 變成 RUNNING_MODE_APP"

**守則（留在 SOP）:** OTA stress test 必須用 local HTTP server + debug firmware binary（不能直接用 S3 production URL），或改用 ESP32 serial 偵測結果；跑完 OTA test 後要記得燒回 debug firmware。
**不確定的地方:** 這兩筆事實是從同一句因果敘述拆出來的（沒有 UART log ← production mode；mode 切換 ← OTA 安裝了 production binary）。它們在檔案裡是同一次除錯推論的一部分，沒有獨立的驗證證據（例如實際 UART capture 對照），信心標記為 `reported` 而非 `verified`，如果 reviewer 認為這是同一件事、該合併成一筆也合理，我把它拆開是因為兩句話描述的是不同機制（fw mode 本身的行為 vs. OTA 造成的狀態轉換）。

---

### feedback_stm32h7_chip_isolation.md
**建議:** split（這份檔案事實最多）

**事實:**
```json
{"key": "CHIP:GENERATION", "scope": "STM32H7R3", "fact": "STM32H7R3 is part of the H7Rx family, a chip series introduced in 2024, distinct from the older H7Bx family.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "H7Rx 是 2024 新系列，H750 是舊 H7Bx 家族"

```json
{"key": "CHIP:GENERATION", "scope": "STM32H750", "fact": "STM32H750 belongs to the older H7Bx chip family.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "H7Rx 是 2024 新系列，H750 是舊 H7Bx 家族"

```json
{"key": "CHIP:DIFFERENCES", "scope": "STM32H7R3", "fact": "STM32H7R3 differs materially from STM32H750 in memory map, clock tree, XIP-from-external-flash behavior, peripheral set, and cache behavior, despite superficial ~90% similarity.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "Memory map、clock tree、XIP-from-external-flash、peripheral set、Cache 行為都有質性差異" / "「看似相似 90% 重疊」是錯覺"

```json
{"key": "CHIP:MCU", "scope": "reactor-fw", "fact": "The reactor-fw repo targets STM32H7R3, verified via the STM32H7R3I8TX_extmemloader linker script and an identical ExtMemLoader source tree vs reactor-50-100-fw.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "驗證 `STM32H7R3I8TX_extmemloader_*.ld` + `diff -rq reactor-fw/ExtMemLoader/Core reactor-50-100-fw/ExtMemLoader/Core` 全 identical → 兩 repo 同 chip 同 ExtMemLoader source"

```json
{"key": "CHIP:MCU", "scope": "reactor-50-100-fw", "fact": "The reactor-50-100-fw repo targets STM32H7R3 (same chip as reactor-fw), verified via matching linker script naming and identical ExtMemLoader source.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "`D:\\mybot\\git\\reactor-fw\\` 跟 `D:\\mybot\\git\\reactor-50-100-fw\\` 都是 H7R3（不是 H750）"

```json
{"key": "CHIP:MCU", "scope": "Reactor 50/100", "fact": "Reactor 50/100 uses STM32H7R3.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "STM32H7R3（Reactor 50/100）跟 STM32H750（Mini2, Spark 2, Spark Pedal）必須當作完全不同的 chip 處理"

```json
{"key": "CHIP:MCU", "scope": "Spark MINI 2", "fact": "Spark MINI 2 (Mini2) uses STM32H750.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "STM32H750（Mini2, Spark 2, Spark Pedal）"

```json
{"key": "CHIP:MCU", "scope": "Spark 2", "fact": "Spark 2 uses STM32H750.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "STM32H750（Mini2, Spark 2, Spark Pedal）"

```json
{"key": "CHIP:MCU", "scope": "Spark Pedal", "fact": "Spark Pedal uses STM32H750.", "source": "feedback_stm32h7_chip_isolation.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "STM32H750（Mini2, Spark 2, Spark Pedal）"

**守則（留在 SOP）:** Agent skill/context/rules 不跨 chip family 共享；chip-specific skill 放 product 層不放 repo 層；不可從 repo 名字或年份猜 chip family，套用前一定要驗證 `.ld`/`.ioc`（例如 grep `STM32H7R3xx`/`STM32H750`）。
**不確定的地方:** (1) `CHIP:MCU`/`Reactor 50/100` 與 `CHIP:MCU`/`reactor-fw`、`reactor-50-100-fw` 三筆內容重疊（產品層 vs repo 層說的是同一件事），是否該保留全部三筆或只留 repo 層的兩筆（更精確、且有驗證證據），請 reviewer 決定。(2) `CHIP:DIFFERENCES` 這筆把 memory map/clock tree/XIP/peripheral/cache 五個面向合成一句話，嚴格說可以再拆成 5 筆更原子的事實，但檔案本身是當一句話敘述，我保留原樣未強拆，flag 給 reviewer 判斷。(3) Mini2/Spark 2/Spark Pedal 三筆的 confidence 我都標 `reported`（檔案裡沒有針對這三個產品個別做過 diff/grep 驗證，只有 reactor-fw/reactor-50-100-fw 有展示驗證過程）。

---

### feedback_stop_searching_known_info.md
**建議:** split

**事實:**
```json
{"key": "ENV:JENKINS_TOKEN_PATH", "scope": "mybot workspace", "fact": "The Jenkins API token file is located at D:\\mybot\\git\\tool\\.jenkins-token.", "source": "feedback_stop_searching_known_info.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "不要再用 Grep/Slack 搜尋 Jenkins token — 直接讀 `D:\\mybot\\git\\tool\\.jenkins-token`"

**事實（存疑，是否要收錄請 reviewer 決定）:**
```json
{"key": "USB:DFU_PARAMS", "scope": "Reactor", "fact": "Reactor DFU flashing uses base address 0x90000000 and enumerates as USB PID 295d:0504 (dfu-util -s 0x90000000:leave:mass-erase:force -d \",295d:0504\").", "source": "feedback_stop_searching_known_info.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "不要問 DFU 參數 — 直接用 `dfu-util.exe -s 0x90000000:leave:mass-erase:force -d \",295d:0504\" -D <file>`"

**守則（留在 SOP）:** 已記錄在 memory 的資訊（Jenkins token、DFU 參數等）不要每次重新搜尋，直接讀 memory/reference 檔案或用既有 script（`flash-dfu-stm32.ps1`, `flash-esp32.ps1`）。
**不確定的地方:** DFU 那筆事實本身在檔案裡是「拿既有 reference（`reference_dfu_flash.md`，不在本次 7 個檔案內）舉的例子」，用來示範「別再問，直接用」這條行為規則，不是這個檔案第一手陳述的新事實——很可能只是複誦另一份 reference 檔的內容。是否要為了這個複誦例子單獨開一筆 fact（可能造成跟 `reference_dfu_flash.md` 未來的重複記錄），我沒有把握，所以列為存疑候選，交給 reviewer 判斷是否收錄或改為只在 `reference_dfu_flash.md` 那邊記一次。

---

## 統計
- 檔案數: 7
- 判定 rule-only（無事實）: 1（feedback_always_capture_log.md）
- 判定 split（事實+守則）: 6
- 提出的事實記錄總數: 18（含 2 筆標示「存疑」的候選：check_hardware_pid 的三筆 COM volatile 值本身已知可能過期、以及 stop_searching_known_info 的 DFU 參數複誦例）
