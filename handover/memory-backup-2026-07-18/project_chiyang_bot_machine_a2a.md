---
name: project_chiyang_bot_machine_a2a
description: Chiyang 的 bot machine / A2A 計畫 — reactor-app-bot 現況、FW 能力缺口、Alice 已承諾全力支援
metadata: 
  node_type: memory
  type: project
  originSessionId: 530214ed-26de-4bd0-9704-882c8e95dc6f
---

**Chiyang（App Manager，U07T2RJMXB8）的「bot machine / A2A」計畫**，Alice 已承諾全力支援（2026-03-26 DM `D07UPG8JT0E`，permalink p1774482079690799）。

## 計畫內容（2026-03-26 DM 原話）
- 「建立一台 **bot machine**，各團隊都到那台 enable 自己團隊的 agentic workflow，大家的 agent 就能一起工作溝通」
- 目的：**A2A 環境**——「之後的開發能看到 Agent 2 Agent 方式進行，**人再進去看**」
- 範圍：先 Reactor，Spark 為未來主力準備；Alice 答應多採購 2 顆板子給 Chiyang、STM32 log 需 STLink
- 這就是「大家加入建構 bot、互相擁有 source code」邀請的出處

## 落地現況
- **reactor-app-bot**（bot user `U0AMUE0P97D`）：Chiyang 建置維運，住在私有頻道 **#reactor-bot-小天地**（`C0AMYQ2AWNA`，2026-03-21 建，原名 bottest）。能力：每日 08:57 RAD standup report、Channel Monitor（監聽訊息→提案開 JIRA ticket 附 Approve/Reject 按鈕）、被 @ 才答（讀 iOS/Android code + JIRA）。主動訊息集中發到此頻道（Chiyang 定的規則）。同 thread = 同一個 claude code session（聊久會 compact）。
- **spark-sw-bot**（`U0AT35V9P2B`）：在 #spark-sprint，支援 "add X as system owner" 指令；bot 只在被加入的 channel 可用。
- 第一次 E2E（2026-03-28「Reactor Root Agent — AgentCard Phase 0」）就自動派工：iOS 給 Bo、FW 給 Alice。

## ⭐ 關鍵缺口（Chiyang 自評，2026-07 前後）
「reactor-app-bot **對 firmware 的應對能力很弱**……沒相關 context、jira、gitlab，也沒累積 memory，**我覺得它有一半是胡謅的 XD**」
→ **我們的 FW agent 系統正好補這塊**：FW source（reactor-fw/spark-mini-ii）、flash rig（STLink/DFU/USB relay）、serial log、Jenkins、fact registry（anti-胡謅）。它強 App/JIRA 側、我們強 FW 側。

## 下一步（待 Alice 點頭）
跟 Chiyang 要 reactor-app-bot 的 source/架設方式（計畫本意就是互相共享），把 FW agent 接進 A2A 環境——bot 遇到 FW 問題轉給我們，不自己猜。

## 其他相關
- Alice 曾協助 Chiyang 查 Spark 2 硬體規格（SDRAM 32MB ISSI / NOR 4MB W25Q32 / SDNAND 256MB / STM32H750IBT6，schematic 在 Drive folder `1VpecNgDkibW2vCNRM2M2UP2zVxBkJMHj`）與 reactor stldr 解析——即 FW agent 已實際在 DM 裡當過 Chiyang 的 FW 支援。
- 相關 [[reference_pg_usb_hub_architecture]]、[[project_scrum_digest_routine]]（standup 與我們 digest 的重疊已解決：我們的已關）。PG 全局 bot 生態（Friday/n8n/pg-stack）見 2026-07-18 research。
