---
name: STM32H7R3 vs STM32H750 完全隔離
description: 兩個 chip 必須當完全不同處理，不共用 register/skill/context。Anti-hallucination 優先於 DRY
type: feedback
originSessionId: 2b1e3496-81ac-4a60-899d-d9f9522807b0
---
STM32H7R3（Reactor 50/100）跟 STM32H750（Mini2, Spark 2, Spark Pedal）必須當作完全不同的 chip 處理。

**Why**：
- H7Rx 是 2024 新系列，H750 是舊 H7Bx 家族
- Memory map、clock tree、XIP-from-external-flash、peripheral set、Cache 行為都有質性差異
- 「看似相似 90% 重疊」是錯覺，10% 差異足以造成幻覺錯誤
- Anti-Hallucination 原則優先於 DRY

**How to apply**：
- Agent skill / context / rules 不跨 chip family 共享
- `mcu-register-lookup` / clock-tree / memory-layout 等 chip-specific skills 放 **product 層**（`projects/<product>/.claude/skills/`），不放 repo 層
- 即使 register name 相同也獨立維護（寧可 duplicate）
- Reactor skill 不提 Spark 2，Spark 2 skill 不提 Reactor
- Agent 載入 skill 前，從 `product.yaml` 確認 target chip
- **不要從 repo 名字猜 chip family** — 必須驗證 `.ld` linker script 或 `.ioc` MCU define。例如 `D:\mybot\git\reactor-fw\` 跟 `D:\mybot\git\reactor-50-100-fw\` **都是 H7R3**（不是 H750），雖然名字裡沒 H7R3。verify 用 `find <repo>/Appli -name "STM32H*.ld"` 或 grep `STM32H7R3xx`/`STM32H750`

**背景**：
- 2026-04-21 Alice 教學時糾正我把 STM32H7R3 跟 STM32H750「register set 90% 重疊」當成可共享的假設。她身為 FW 總監明確否決：「當完全沒關係比較好」。這是 domain expert override infra designer 的範例。
- 2026-04-29 我犯了反向錯誤：把 `reactor-fw` 當成 H750 拒絕用它的 `.stldr`。Alice 糾正後驗證 `STM32H7R3I8TX_extmemloader_*.ld` + `diff -rq reactor-fw/ExtMemLoader/Core reactor-50-100-fw/ExtMemLoader/Core` 全 identical → 兩 repo 同 chip 同 ExtMemLoader source。教訓：rule 是對的，但**套用前先驗證**，不要從 repo 名/年份猜。
