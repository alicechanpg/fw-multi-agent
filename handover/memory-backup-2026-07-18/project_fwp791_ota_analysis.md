---
name: project-fwp791-ota-analysis
description: "FWP-791 OTA state=15 has TWO independent root causes. Bug A: img_pkts underflow (待驗證). Bug B: SDMMC DMA contention (100% reproduced, FWP-796, WIP MR !318). Next: apply Bug B fix then retest Bug A."
metadata: 
  node_type: memory
  type: project
  originSessionId: 24198985-e1cc-4060-b427-b889433b98b6
---

FWP-791 OTA ST_SEND_IMG (state=15) — 兩個獨立 Root Cause (2026-05-19 confirmed).

## Bug A: img_pkts underflow (FWP-791, 待驗證)

- `esp_http_client_read()` (esp_http_client.c:1040-1120) 是 blocking loop，填滿 buffer (1536 bytes) 或 TLS_TIMEOUT (7000ms) 才 return
- Server chunk 太小 + stall > 7s → partial read → STM32 收到不完整 data → img_pkts < 0 → result=1
- 理論觸發點 ~83% progress
- 需要先套用 Bug B fix 後才能測到（Bug B 在 2.2% 就先觸發了）

## Bug B: SDMMC DMA contention (FWP-796, 已驗證 100% 複製)

- OTA 和 FatFS 共用 `hsd1` SDMMC HAL handle 無 mutex
- User 轉 knob → save_temp_preset → SDNAND_write_blocks(&hsd1) 與 OTA DMA 衝突
- `DEBUG_READBACK_IMAGE_FROM_SDNAND` 硬編碼為 1 → production 也會觸發
- Readback verify: `data[0]=01 != rb_data[0]=BC` → result=1 → state=15
- **100% repro**: OTA 進行中轉 knob，at any progress %

## Fix (Bug B)

- **Branch**: `bugfix/FWP-791-ota-sdmmc-lockdown` (from develop af0f028)
- **Commit**: 1609ae5
- **MR**: !318 (WIP) — https://git.positivegrid.com:8443/firmware/reactor-fw/merge_requests/318
- **JIRA**: FWP-796 (linked to FWP-791)
- **方案**: `volatile bool g_ota_in_progress` flag 擋住 file I/O + UI events
- **Safety**: BLE disconnect 清除 + 180s timeout failsafe
- **改了 5 個檔**: DataManager.h/.cpp, BleCmdHandler.cpp, AudioService.cpp, InputService.cpp
- **Stashed**: `stash@{0}` = FWP-791 debug modifications (readback+latency defines)

## Test Server

```
python throttle_server.py --https --port 8443 --mode burst --burst-size 10 --stall-sec 8 --chunk-size 127 --target stm32
```
Server 位於 `D:\mybot\git\tool\ota-server\throttle_server.py`

## Pass/Fail 記錄

- **PASS (對照組)**: SPI#3-#63 (61 sends) 全部 result=0，不操作 UI 時 OTA 穩定
- **FAIL (Bug B)**: SPI#64 result=-5 at 2.2% (26670/1231368 bytes)，轉 knob 觸發

## Next Steps

1. Power cycle STM32（SD-NAND 可能有 corruption）
2. 確認 ESP32 是否需 re-flash（OTA 可能覆蓋 test firmware）
3. 套用 Bug B fix，重新測試 Bug A (目標 ~83% underflow)

Related: [[feedback_evidence_based]], [[feedback_no_code_changes]], [[project_fwp791_test_params]]
