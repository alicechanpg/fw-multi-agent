---
name: production-stm32-no-log
description: Production STM32 firmware 沒有 UART log 輸出，OTA 後 debug log 消失
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 24198985-e1cc-4060-b427-b889433b98b6
---

Production 版本 STM32 firmware 沒有 UART log 輸出。OTA 下載的是 production binary，安裝後 STM32 從 APP_DEBUG 變成 RUNNING_MODE_APP，UART 完全靜默。

**Why:** OTA stress test 用 S3 URL 下載 production firmware → 第一次 OTA 成功後 STM32 就變 release mode → test script 靠 UART 偵測 "transfer done" 的方式失效 → 之後所有 run 都 timeout。

**How to apply:**
- OTA stress test 必須用 local HTTP server + debug firmware binary，不能直接用 S3 production URL
- 或者改 test script 用 ESP32 serial 偵測結果（ESP32 不受 STM32 OTA 影響）
- 跑完 OTA test 後記得燒回 debug firmware（[[reflash-debug-after-ota]]）
