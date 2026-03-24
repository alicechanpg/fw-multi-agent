# /test - 執行測試

執行 Unit Test 或靜態分析。

## 使用方式

```
/test esp32
/test stm32
/test cppcheck
```

## 執行內容

### Unit Test

```powershell
# ESP32
powershell -ExecutionPolicy Bypass -File "D:\mybot\git\pg-reactor-esp32-wifi-bt\test\scripts\run_unit_tests.ps1"

# STM32
powershell -ExecutionPolicy Bypass -File "D:\mybot\git\reactor-50-100-fw\test\scripts\run_unit_tests.ps1"
```

### 靜態分析

```powershell
cppcheck --enable=all --std=c11 D:\mybot\git\pg-reactor-esp32-wifi-bt\main\
```

## 參數

| 參數 | 說明 |
|------|------|
| `esp32` | 執行 ESP32 測試 |
| `stm32` | 執行 STM32 測試 |
| `cppcheck` | 執行靜態分析 |
