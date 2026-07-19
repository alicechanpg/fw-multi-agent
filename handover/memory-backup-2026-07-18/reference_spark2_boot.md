---
name: Spark 系列需要手動開機（Spark 2、Spark GO）
description: Spark 2 和 Spark GO 不會自動開機，flash 完或 power cycle 後需要手動按開機鍵。Reactor 上電自動開機
type: reference
originSessionId: f96e60f1-b99d-493e-b5c9-bf7c2dc26924
---
Spark 2 和 Spark GO 需要**手動按開機鍵**才能啟動。

跟 Reactor 不同（Reactor 上電自動開機），Spark 系列有獨立的 power button。

Flash STM32/GD32 或 ESP32 後，裝置會 reset 但不會自動開機，需要按 power button。
Power cycle（拔插電源）後也需要手動按開機鍵。
JLink soft reset (`r` + `go`) 不等於 power cycle，USB 可能不會重新 enumerate。

**2026-05-05 教訓：** Spark GO flash bootloader 後只做 JLink reset + USB 拔插，忘記按 power button，導致 USB 一直沒 enumerate，誤以為 STFS-491 bootloader 有問題。
