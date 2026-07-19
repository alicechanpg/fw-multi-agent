---
name: project-fwp791-test-params
description: "FWP-791 OTA reproduction test parameters — burst+stall approach, esp_http_client_read blocking behavior, TLS_TIMEOUT=7000ms"
metadata: 
  node_type: memory
  type: project
  originSessionId: 24198985-e1cc-4060-b427-b889433b98b6
---

## FWP-791 OTA Reproduction Test Parameters (2026-05-19)

### ESP32 HTTP Client 行為（決定 server 參數的關鍵）

- `esp_http_client_read(client, buffer, BUFFSIZE=1536)` 是 **blocking loop**
- 內部 loop 持續呼叫 `esp_transport_read()` 直到填滿 1536 bytes 或 timeout
- `config.timeout_ms = TLS_TIMEOUT = 7000`（7 秒）
- **只有 server delay > 7s 才能讓 transport_read timeout → return partial data**
- Source: `esp_http_client.c:1040-1120`, `app_https_fw_ota.cpp:17,419,460`

### Server 參數（經過迭代得出）

**最終可行方案：**
```bash
python throttle_server.py --https --port 8443 --mode burst --burst-size 10 --stall-sec 8 --chunk-size 127 --target stm32
```

| 參數 | 值 | 原因 |
|------|-----|------|
| `--chunk-size 127` | 127B | **必須！** 奇數，不整除 512 也不整除 1536。10×127=1270 < BUFFSIZE(1536) → partial read |
| `--burst-size 10` | 10 chunks | 每輪送 10×127=1270 bytes |
| `--stall-sec 8` | 8 秒 | > TLS_TIMEOUT(7s) → 觸發 transport_read timeout |
| `--target stm32` | stm32 | 只影響 STM32 FW，ESP32 OTA 全速通過 |
| `--https` | HTTPS | 必須用 HTTPS（production 用 HTTPS） |

### 為什麼這樣設

1. **chunk-size 127**：burst 10×127=1270 bytes。ESP32 讀到 1270 bytes（ridx=1270），接著 transport_read 等更多 data，7 秒後 timeout → return 1270。1270 % 512 = 246，產生 small SPI chunk
2. **stall-sec 8**：必須 > 7 秒（TLS_TIMEOUT）才能觸發 transport_read timeout
3. **chunk-size 1536 不行**：10×1536=15360 = 10×BUFFSIZE → ESP32 剛好讀完 10 個 full buffer → 第 11 次 ridx=0 → timeout → return error（不是 partial data）

### 失敗的嘗試

1. **--small-chunk-after 50 --small-chunk-size 127 --small-chunk-delay-ms 50** → 不行，esp_http_client_read blocking loop 在 7s timeout 內把所有小 chunk 合併成 full buffer
2. **--kbps 5 --chunk-size 128** → 不確定性，TCP/TLS buffering 有時合併有時不合併
3. **--mode burst --burst-size 10 --stall-sec 8（chunk-size=1536 default）** → ridx=0 at timeout → return TLS_NORMAL_ERROR → retry → 不產生 partial read

### ESP32 Test Firmware 設定

- `ENABLE_APP_CMD_SIMULATION=1` — 開機自動觸發 OTA
- `OTA_LOCAL_SERVER="https://192.168.11.55:8443"` — 指向 local test server
- SPI debug logs: chunk size, timing, send count, fail summary
- Source: `app_https_fw_ota.cpp:15,32,526-553`

### ESP32 Binary 版本檢查技巧（2026-05-19 發現）

**問題**：ESP32 先 OTA 自己（下載 `esp32_fw_reactor100.bin`），成功後變 production FW → 喪失 auto-OTA 能力
**解法**：用 test firmware binary 替換 `esp32_fw_reactor100.bin`
- ESP32 版本檢查（`app_https_fw_ota.cpp:274-282`）偵測到版本相同 → 跳過自己的 OTA → give semaphore → STM32 OTA 正常進行
- 如果 `esp32_fw_reactor100.bin` 不存在或下載失敗 → ESP32 OTA task 永久掛起（`vTaskDelay(portMAX_DELAY)`） → STM32 OTA 永遠不會開始
- **不能刪除 ESP32 binary！** 必須保留一個有效的 binary 才能讓 ESP32 pass through 到 STM32 OTA
- `CONFIG_EXAMPLE_SKIP_VERSION_CHECK` 預設未定義 → 版本檢查啟用

### Bug A Underflow 數學推導（2026-05-19）

- 每次 HTTP read 返回 1270 bytes（burst 10 × chunk 127）
- ESP32 拆成 3 SPI packets: 512 + 512 + 246 bytes
- STM32 每收 1 packet → `img_pkts -= 1`
- 宣告 `img_pkts = 2406`（1,231,368 / 512 = 2405.01 → ceil = 2406）
- 2406 packets 在 802 HTTP reads 後耗盡（802 × 3 = 2406）
- 此時已傳 802 × 1270 = 1,018,540 bytes（82.7%）
- 還剩 212,828 bytes → 下一個 packet 使 `img_pkts = -1` → **UNDERFLOW → result=1 → state=15**
- **觸發點：~83% progress，SPI#~2407**

### COM Port

- COM4: STM32 debug serial (921600 baud)
- COM19: ESP32 debug serial (115200 baud)
- COM19 flash 和 serial 共用，flash 前要停 logger

Related: [[project-fwp791-ota-analysis]]
