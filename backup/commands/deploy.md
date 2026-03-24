# /deploy - 部署流程

執行 Build → Test → Flash。

## 使用方式

```
/deploy esp32
/deploy stm32
/deploy esp32 --skip-test
```

## 執行內容

1. Build firmware
2. 執行 unit test
3. Flash 到裝置

### ESP32 Flash

```powershell
cd D:\mybot\git\pg-reactor-esp32-wifi-bt
idf.py -p COM3 flash
```

### STM32 Flash

```powershell
cd D:\mybot\git\reactor-50-100-fw
# 使用 ST-Link
```

## 參數

| 參數 | 說明 |
|------|------|
| `esp32` | 部署 ESP32 |
| `stm32` | 部署 STM32 |
| `--skip-test` | 跳過測試 |
| `--port COM3` | 指定 COM port |
