---
name: USB Relay pulse 在這個 rig 留 OFF state
description: usb-relay.ps1 -Action pulse 結束後 device 是斷電狀態，要 -Action on 才能恢復
type: reference
originSessionId: a24b5d2f-3d02-4ae1-9f2c-89e98777117e
---
`D:\mybot\git\tool\usb-relay.ps1 -Action pulse -Port COM3` 的行為：

```
ON 200ms → OFF
```

最終 state = **OFF (device 斷電)**。

## 在 Alice rig 上實測 (2026-04-29)

- pulse 後 COM6 (Reactor CDC) + COM19 (ESP32) 全部消失
- COM4 (STLink VCP) 不受影響（USB 直接接 PC，不過 relay）
- COM3 (USB Relay 自己) 不受影響

## How to apply

- **要做 reset 後 device 通電**：`pulse` 後再呼一次 `-Action on`，或直接用 `off → sleep → on` 兩步驟
- **clean cold boot**：`-Action off` → `Start-Sleep 800ms` → `-Action on`
- **不要假設 pulse = power cycle 後通電**，這個 rig 接法不是

## 推測 wiring

Relay 接法是 「ON = device 通電」（normally open）：
- ON  → relay closed → device 通電
- OFF → relay open → device 斷電
- pulse(ON-OFF) = 通電 200ms 後又斷電 = 結果斷電

## 相關 script

`flash-and-reset-stm32.ps1` 結尾是 `usb-relay -Action pulse`，意味著 STLink 燒完後 device 會留斷電 — 跑 boot test 前要記得補 `-Action on`。
