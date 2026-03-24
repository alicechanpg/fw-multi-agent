# STM32 Boot Log Pattern

基於 Reactor 100W 實際開機 log 建立 (2026-02-25 抓取)。
總開機時間: ~6 秒 (416 行 log)。

## Boot 階段總覽

| # | 階段 | 正常耗時 | 警告 | 錯誤 |
|---|------|----------|------|------|
| 1 | Bootloader | 200-300ms | >500ms | >1000ms |
| 2 | System Init | 150-250ms | >400ms | >800ms |
| 3 | App Start | 600-800ms | >1000ms | >1500ms |
| 4 | Hardware Detection | 400-600ms | >800ms | >1200ms |
| 5 | Audio Codec Init | 500-800ms | >1200ms | >2000ms |
| 6 | Preset Load | 1200-2000ms | >3000ms | >5000ms |
| 7 | Final Init | 1500-2000ms | >2500ms | >4000ms |
| **Total** | **全部** | **4-8s** | **8-12s** | **>12s** |

---

## Phase 1: Bootloader (~230ms)

### MUST_HAVE
```
Reactor 100w Bootloader_version: X.X.X.X
RUNNING_MODE : LOADER_DEBUG
Jump to APP code (4MB NOR)
```

### 正常行為
```
sd_nand_fw_info.length = 0          ← 無 OTA bin, 正常
A illegal app bin length found      ← SD-NAND 無 firmware, 正常 (非 OTA 情境)
FW_upgrade_check 1                  ← 檢查 OTA 升級
FW_upgrade_check 2                  ← 第二次檢查
```

### WARNING
- `sd_nand_fw_info.length > 0` 且有版本資訊 → 有 OTA bin 等待燒錄
- Bootloader 版本與預期不符

### ERROR_SIGNATURE
- 無 `Bootloader_version` 輸出 → Bootloader 損壞
- 無 `Jump to APP code` → 卡在 bootloader
- 出現 `RUNNING_MODE : LOADER_RELEASE` 但非 production build

---

## Phase 2: System Init (~210ms)

### MUST_HAVE
```
=== Reset Source Analysis ===
Reset Cause: External Pin Reset
=== IWDG Watchdog Status ===
IWDG Configuration: 750ms timeout
System Initialization Complete
Starting FreeRTOS scheduler...
```

### 正常參數
```
IWDG Prescaler: 32
IWDG Reload Value: 750
Feeding Strategy: AudioService (every ~102ms)
```

### WARNING
- `Reset Cause` 非 `External Pin Reset`:
  - `Software Reset` → 軟體觸發重啟
  - `Window Watchdog Reset` → WWDG timeout
  - `Independent Watchdog Reset` → **IWDG timeout, 可能有 task 卡住**
  - `Power-On Reset` → 斷電重啟
  - `Brown-Out Reset` → 電壓不足

### ERROR_SIGNATURE
- 無 `System Initialization Complete`
- 無 `Starting FreeRTOS scheduler`
- IWDG timeout 值異常 (非 750ms)

---

## Phase 3: App Start (~700ms)

### MUST_HAVE
```
RUNNING_MODE : APP_DEBUG
Reactor 100w fw_version: X.X.X.X
[WATCHDOG] Normal system startup (not watchdog reset)
DataManager: Initialization
DataManager: Mutex initialization successful
DataManager: file_mount - File system mounted successfully
[FWP-552] ADC[0] baseline initialized
[FWP-552] ADC[7] baseline initialized
[FWP-679] ADC baseline stabilization complete, events enabled
[AmpPresetManager] Static DSP modules initialized
DebouncedSwitchManager: Initialized
```

### 正常 ADC 通道 (8 個)
| Index | Name | 典型初始值 |
|-------|------|-----------|
| 0 | GAIN | 0.13 |
| 1 | (unnamed) | ~0.00 |
| 2 | SPEAKER | 0.32 |
| 3 | (unnamed) | ~0.00 |
| 4 | AMP_MODE | 0.79 |
| 5 | MASTER | 0.11 |
| 6 | LEVEL | 1.00 |
| 7 | TREBLE | 0.02 |

每個 ADC 通道做 2 輪 baseline (loop 2 → loop 1 → complete)。

### WARNING
- `[WATCHDOG] Watchdog reset detected!` → 上次是 watchdog reset, 要查根因
- ADC baseline 值與歷史差異太大 → 硬體可能有問題
- `DataManager: file_mount` 後沒出現 `successfully` → 檔案系統問題

### ERROR_SIGNATURE
- `DataManager: Mutex initialization` 失敗
- `file_mount` 失敗
- ADC baseline init 不完整 (少於 8 通道)
- 超過 1000ms 未完成此階段

---

## Phase 4: Hardware Detection (~540ms)

### MUST_HAVE
```
---- Send DETECT EVENT: GUITAR, plug
---- Send DETECT EVENT: POWER_SWITCH, power on
[ ***** POWER ON ***** ]
power_on_sequence_1 ...
power_on_sequence_2 ...
power_on_sequence_3 ...
```

### 正常的 DETECT EVENT 序列 (桌面測試, 只接 USB + Guitar)
```
GUITAR:      plug        ← 吉他線接著
POWER_AMP:   unplug      ← 無外接 power amp
HEADPHONE:   unplug      ← 無耳機
LINEOUT:     unplug      ← 無 line out
FX_SEND:     unplug      ← 無 FX send
FX_RETURN:   unplug      ← 無 FX return
TRS_PEDAL:   plug        ← TRS pedal 接著 (或 unplug)
USB_VBUS:    plug        ← USB 供電
```

### WARNING
- `GUITAR: unplug` → 吉他未插，測試可能不完整
- `USB_VBUS: unplug` → 非 USB 供電，用電池
- `power_on_sequence` 中間有中斷

### ERROR_SIGNATURE
- `POWER_SWITCH: power on` 未出現
- `power_on_sequence` 序列不完整 (缺 1, 2, 或 3)
- 無 `[ ***** POWER ON ***** ]`

---

## Phase 5: Audio Codec Init (~660ms)

### MUST_HAVE
```
[HP] hp_amp_version = 2
AKM7755 read ctrl reg 0xc0:0x2d        ← 第一個 register
AKM7755 read ctrl reg 0xdb:0x00        ← 最後一個 register
[Audio] audio chips init are done.
```

### 正常的 AKM7755 初始化序列
```
AKM7755 set guitar return mix input vol 63
AKM7755 set usb power amp mix input vol 63
AKM7755 set bt input vol 63
AKM7755 set hp line out vol 0          ← 開機先靜音
AKM7755 set amp vol 0                  ← 開機先靜音
AKM7755 guitar mute on                 ← 開機先 mute
AKM7755 return mute on
AKM7755 usb power amp mute on
AKM7755 set master eq bypass on
```

### 關鍵 Register 檢查 (正常值)
| Register | 正常值 | 說明 |
|----------|--------|------|
| 0xc0 | 0x2d | Control reg 1 |
| 0xc1 | 0x01 | Control reg 2 |
| 0xc4 | 0x48 | Sampling rate config |
| 0xca | 0x81 | Power control |

### WARNING
- HP amp version 非 2
- Register 讀取值與正常值不同

### ERROR_SIGNATURE
- `AKM7755 read ctrl reg` 少於 24 個 → I2C 通訊問題
- 無 `audio chips init are done` → Codec 初始化卡住
- Register 值全部為 0x00 或 0xFF → I2C bus 錯誤

---

## Phase 6: Preset Load (~1.6s)

### MUST_HAVE
```
power_on_sequence_4 ...
power_on_sequence_5 ...
[BOOT] Temp preset found
[TIMING] create_signal_chain_from_preset:
Temp preset restored successfully
```

### DSP 模組載入序列 (預期 10+ 模組)
```
[LOAD_PRESET] Module: bias.noisegate      ← Noise Gate (靜態)
[LOAD_PRESET] Module: 4kComp              ← Compressor (動態分配)
[LOAD_PRESET] Module: DistortionOCD       ← Distortion (動態分配)
[LOAD_PRESET] Module: JimiWah             ← Wah (靜態)
[LOAD_PRESET] Module: GuitarEQ7           ← EQ (靜態)
[LOAD_PRESET] Module: Amp.Preamp          ← Preamp (靜態, 145 params)
[LOAD_PRESET] Module: Amp.Tonestack       ← Tonestack (靜態, 4 params)
[LOAD_PRESET] Module: Amp.Poweramp        ← Power Amp (靜態, 110 params)
[LOAD_PRESET] Module: Amp.Transformer     ← Transformer (靜態, 11 params)
[LOAD_PRESET] Module: Tremolo             ← Mod (動態分配)
[LOAD_PRESET] Module: DelayDM2            ← Delay (動態分配)
[LOAD_PRESET] Module: MonoReverb          ← Reverb (靜態)
[LOAD_PRESET] Module: EffectLoop          ← FX Loop (靜態)
```

### 效能 KPI
| 指標 | 正常 | 可接受 | 過慢 |
|------|------|--------|------|
| rearrange_amp_signal_chain | <20ms | <50ms | >50ms |
| create_signal_chain (create) | <50ms | <100ms | >100ms |
| create_signal_chain (mute_wait) | <80ms | <150ms | >150ms |
| 總參數數 | ~374 | - | <100 (模組缺失) |
| 總模組數 | ~10 | 8+ | <8 (模組缺失) |

### WARNING
- `[AP] allocating FX object` → 動態分配 (正常, 但頻繁分配注意記憶體)
- 模組 active=0 → 效果關閉 (正常, 使用者設定)
- `[BOOT] Temp preset found, enabling 100 series mode` → AI Switch 模式

### ERROR_SIGNATURE
- 無 `Temp preset restored` → Preset 載入失敗
- `create_signal_chain` >200ms → DSP pipeline 太慢
- 模組數 <8 → 有模組載入失敗
- 出現 `FX allocation failed` → Heap 不足

---

## Phase 7: Final Init (~1.7s)

### MUST_HAVE
```
[AudioService] Dynamic amp UUID mapping initialized
[ACR] set_all_audio_mute: UNMUTE
USB commander init ...
```

### 正常序列
```
[FWP-679] initialize_amp_data_id_mapping: SUCCESS
[FWP-679] _amp_category_uuids[0-5]= ...         ← 6 個 amp category
---- Send Slide Switch EVENT: 256 val 17
set power OUTPUT_SPEAKER_25W
bt ack : success
bt switch to BT mode
bt enter pairing mode
bt mac : XX XX XX XX XX XX
wifi_status 0
AKM7755 amp mute off                             ← 最終 unmute
[ACR] set_all_audio_mute: UNMUTE                  ← 系統 unmute
USB commander init ...
```

### WARNING
- `bt ack : fail` → BT 命令失敗 (偶爾發生, 可重試)
- `wifi_status 0` → WiFi 未連線 (可能正常)
- `[FX_LOOP LED] WARNING: toggleFXLoop not found in switch profile!` → FX Loop 開關未配置

### ERROR_SIGNATURE
- `amp_data_id_mapping` 失敗
- BT 初始化全部失敗 (連續 `bt ack : fail`)
- Audio UNMUTE 未執行 → 設備無聲
- 無 `USB commander init` → USB 功能異常

---

## 自動化測試 Regex

### 關鍵成功標記 (全部必須匹配)
```regex
Bootloader_version:\s+\d+\.\d+\.\d+\.\d+
Jump to APP code
Starting FreeRTOS scheduler
fw_version:\s+\d+\.\d+\.\d+\.\d+
DataManager:.*mounted successfully
ADC baseline stabilization complete
POWER ON
audio chips init are done
Temp preset restored
set_all_audio_mute: UNMUTE
USB commander init
```

### 錯誤偵測 (任一匹配即為異常)
```regex
(?i)(fail|error|timeout|corrupt|invalid|assert|hardfault|panic|stack overflow)
(?!.*Normal system startup).*[Ww]atchdog [Rr]eset
allocation failed
f_open FAIL
```

### 效能提取
```regex
\[TIMING\] rearrange_amp_signal_chain:\s+(\d+)\s+ms
\[TIMING\] create_signal_chain_from_preset:.*create=(\d+)\s+ms.*?(\d+)\s+params.*?(\d+)\s+modules
```
