---
name: 不要反覆搜尋已知資訊
description: Jenkins token、DFU 參數等已記錄在 memory 的資訊，直接用不要每次重找
type: feedback
---

不要每次都重新搜尋已經知道的資訊（如 Jenkins token 路徑、DFU 燒錄參數）。直接從 memory 讀取使用。

**Why:** 用戶覺得每次都要重新找 Jenkins token、DFU 指令參數等已知資訊非常沒效率，浪費大量時間。這些資訊已經記錄在 memory 中。

**How to apply:**
1. 燒錄、下載 Jenkins artifact 等操作前，先讀 `reference_dfu_flash.md` 取得所有需要的參數
2. 不要再用 Grep/Slack 搜尋 Jenkins token — 直接讀 `D:\mybot\git\tool\.jenkins-token`
3. 不要再問 DFU 參數 — 直接用 `dfu-util.exe -s 0x90000000:leave:mass-erase:force -d ",295d:0504" -D <file>`
4. 有 script 就用 script — `flash-dfu-stm32.ps1`, `flash-esp32.ps1`
