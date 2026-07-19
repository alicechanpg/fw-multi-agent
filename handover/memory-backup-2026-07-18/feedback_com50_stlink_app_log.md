---
name: COM50 STLink VCP 可讀 App log
description: STLink VCP (COM50) 可以讀到 Bootloader 和 App 兩階段的 log，不是只有 Bootloader
type: feedback
---

COM50 (STLink VCP, VID 0483/PID 374F) 可以讀到 App log，不是只有 Bootloader。

**Why:** 2026-04-13 Alice 確認 STLink VCP 可以讀 Reactor App 階段的 debug log。之前只抓到 Bootloader 9 行是抓取邏輯的問題，不是硬體限制。

**How to apply:** 抓 boot log 時用 COM50 (STLink VCP) 即可，不需要另外接 USB-to-Serial 線。如果只抓到 Bootloader，問題在 script 不在 port。
