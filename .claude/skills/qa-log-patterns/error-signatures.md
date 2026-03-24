# Error Signatures (跨平台)

QA 自動偵測用的錯誤特徵碼。任何一個匹配都需要記錄並調查。

## 通用錯誤 Regex

### 致命錯誤 (測試立即 FAIL)
```regex
(?i)hardfault
(?i)stack\s*overflow
(?i)heap\s*(overflow|exhausted|full)
(?i)assert(ion)?\s*fail
(?i)panic
(?i)abort
(?i)allocation\s*fail
```

### 嚴重錯誤 (需要調查)
```regex
(?i)(fatal|critical)\s*error
(?i)corrupt(ed|ion)?
(?i)watchdog\s*reset
(?i)timeout.*(?!Normal)
f_open\s+FAIL
```

### 一般錯誤 (記錄)
```regex
(?i)\bfail\b(?!.*safe|.*Normal)
(?i)\berror\b
(?i)\binvalid\b
```

### 排除項 (false positive)
這些包含 "fail" 但不是錯誤：
```
pop_hwcmd_result_from_que fail     ← ESP32 開機時偶發, SPI 尚未就緒
bt ack : fail                      ← BT 偶爾一次失敗可接受 (連續 3+ 次才是問題)
```

---

## STM32 專屬錯誤

### I2C 通訊
```regex
AKM7755.*(?:error|fail|timeout)
AW9523.*(?:error|fail)
AW21036.*(?:error|fail)
TPA6130.*(?:error|fail)
```

### 音頻系統
```regex
SAI.*(?:error|overrun|underrun)
DMA.*(?:error|transfer)
audio.*(?:error|fail|timeout)
codec.*(?:error|fail)
```

### 檔案系統
```regex
f_open\s+FAIL\(\d+\)
DataManager.*(?:error|fail)
file_mount.*fail
```

### FreeRTOS
```regex
(?i)stack\s*overflow.*task
(?i)malloc\s*fail
vApplicationStackOverflowHook
```

### SPI (ESP32 通訊)
```regex
SPI.*(?:error|timeout|fail)
spi_command.*fail
```

---

## ESP32 專屬錯誤

### 系統
```regex
(?i)guru\s*meditation
(?i)core\s*\d+\s*panic
(?i)abort\(\)
(?i)backtrace
Brownout detector was triggered
```

### WiFi/BLE
```regex
(?i)wifi.*(?:error|fail|disconnect)
(?i)ble.*(?:error|fail|disconnect)
(?i)gatt.*error
```

### OTA
```regex
(?i)ota.*(?:error|fail|abort)
(?i)firmware.*(?:error|corrupt|invalid)
(?i)partition.*(?:error|invalid)
```

### SPI (STM32 通訊)
```regex
SPI.*(?:error|timeout)
spi_command.*fail
(?i)slave.*not\s*respond
```

---

## 效能異常偵測

### STM32 Boot 階段超時
```python
# 從 log timestamp 計算各階段耗時
phases = {
    "bootloader": ("Bootloader_version", "Jump to APP code", 500),    # max ms
    "system_init": ("Reset Source", "Starting FreeRTOS", 400),
    "app_start": ("RUNNING_MODE : APP_DEBUG", "ADC baseline stabilization", 1000),
    "hw_detect": ("DETECT EVENT: GUITAR", "POWER ON", 800),
    "codec_init": ("hp_amp_version", "audio chips init are done", 1200),
    "preset_load": ("power_on_sequence_4", "Temp preset restored", 3000),
    "final_init": ("UUID mapping", "USB commander init", 2500),
}
total_boot_max = 12000  # 12 seconds
```

### DSP 效能
```python
timing_limits = {
    "rearrange_amp_signal_chain": 50,      # max ms
    "create_signal_chain_create": 100,      # max ms
    "create_signal_chain_mute_wait": 150,   # max ms
}
```
