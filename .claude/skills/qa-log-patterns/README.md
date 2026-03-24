# QA Log Patterns

QA 預期 Log 模式，用於驗證系統各操作是否正常。

## 檔案清單

| 檔案 | 內容 |
|------|------|
| `stm32-boot.md` | STM32 開機 log 的 7 個階段、關鍵檢查點、效能指標 |
| `esp32-boot.md` | ESP32 開機 log pattern (待完善) |
| `error-signatures.md` | 跨平台錯誤特徵碼和 regex pattern |

## 使用方法

QA Agent 在驗證開機流程時，參照這些 pattern 比對實際 log，確認：
1. 所有 MUST_HAVE 訊息都出現
2. 各階段耗時在正常範圍內
3. 無 ERROR_SIGNATURE 出現
4. WARNING 項目已記錄並評估
