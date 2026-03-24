# /build - Build Firmware

Build ESP32 或 STM32 firmware。

## 使用方式

```
/build esp32
/build stm32
/build all
```

## 執行內容

### ESP32 Build

```powershell
cd D:\mybot\git\pg-reactor-esp32-wifi-bt
idf.py build
```

### STM32 Build

```powershell
cd D:\mybot\git\reactor-50-100-fw
# 使用 STM32CubeMX 或 make
```

## 參數

| 參數 | 說明 |
|------|------|
| `esp32` | Build ESP32 專案 |
| `stm32` | Build STM32 專案 |
| `all` | Build 所有專案 |
