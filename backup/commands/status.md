# /status - 專案狀態總覽

檢視 MyBot Workspace 中所有專案和 Agent 的狀態。

## 使用方式

```
/status
/status esp32
/status stm32
```

## 執行內容

1. **專案狀態**
   - 檢查 ESP32 和 STM32 專案的 git 狀態
   - 顯示當前 branch 和最新 commit
   - 顯示是否有未 commit 的修改

2. **Build 狀態**
   - 最近一次 build 結果
   - build 輸出路徑

3. **測試狀態**
   - 最近一次測試結果
   - 測試覆蓋率（如果有）

## 輸出格式

```markdown
# 專案狀態總覽

## ESP32 (pg-reactor-esp32-wifi-bt)
- Branch: main
- Last Commit: abc1234 - "Fix WiFi reconnect"
- Status: Clean / 2 modified
- Last Build: Success (2024-01-20 15:30)

## STM32 (reactor-50-100-fw)
- Branch: develop
- Last Commit: def5678 - "Add preset feature"
- Status: Clean
- Last Build: Success (2024-01-20 14:00)

## 待處理
- [ ] ESP32: WiFi 斷線問題
- [ ] STM32: 新增 preset 功能
```

## 參數

| 參數 | 說明 |
|------|------|
| (無) | 顯示所有專案狀態 |
| `esp32` | 只顯示 ESP32 專案 |
| `stm32` | 只顯示 STM32 專案 |
