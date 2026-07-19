# Agentic 101 — 給 Alice 的超簡單入門

> 寫給十年資深 firmware engineer 的速成單（~10 分鐘讀完）
> 目標：明天跟 Calvin 對話不卡名詞 + 知道自己在哪層

---

## 1. 你現在在哪裡（30 秒版）

```
L1: pg-agent-dev (Calvin)    — 蓋 agent 系統的「地基」
    ↓
L2: pg-fw-dev-agent (Nathan) — Firmware 專用的 framework
    ↓
L3: pg-fw-dev-alice (你)     — Reactor 產品的適配
```

類比（熟悉的東西）：
- **L1 = 作業系統**（Windows）
- **L2 = 裝在 OS 上的 framework**（像 STM32 HAL）
- **L3 = 你這個 product 的 port layer**（把 HAL 綁到 Reactor 硬體）

---

## 2. 你這 1.5 天做了什麼（L3）

1. 寫一包 Reactor 專屬 skill（`mcu-register-lookup`）— STM32H7R3 register 知識包
2. 在 Nathan 的 L2 指令 (`/fw-build` `/fw-flash`) 上**加 Reactor 硬體環境適配**（PowerShell + USB relay + DFU auto-detect + voltage gate）
3. 記 5 個 platform gap 做 backlog（`.claude/plans/backlog.md`）— 提 proposal 給 Nathan

**你的 branch**: `pg-fw-dev-alice` (on Nathan 的 repo)
**你的 JIRA**: FWP-776

---

## 3. 必懂 10 個名詞

> 先講概念（LLM = 像 ChatGPT 那種大模型），名詞由內而外排。

### 3.1 Tool Calling（工具呼叫）
LLM 本來只會講話。**Tool calling = 讓 LLM 能下指令**（讀檔、跑 shell、call API）。這是 agent 的根本能力。

### 3.2 Agent
= 會用工具的 LLM。你給**目標**，他自己跑迴圈達成。
類比：懂技術的外包同事。

### 3.3 Subagent
= Agent 派出去的「外包同事」，做完子任務回報主 agent。
為什麼要派：主對話不會被雜訊塞爆，context 清爽。

### 3.4 CLAUDE.md
= 每個 repo 的規則手冊。Agent 每次自動讀。
類比：repo 的 `.editorconfig` + README 合體，但 agent 真的照著做。

### 3.5 Memory
= 跨 session 保存的筆記（你的在 `C:\Users\alice\.claude\projects\D--mybot\memory\`）。
Agent 自動讀。你的偏好、組織架構、專案狀態都放這。

### 3.6 Skill
= 一包專業知識 + **何時使用的說明**。Agent 根據 `description:` 自動決定要不要載入。
類比：handbook 會自己翻開在對的一頁，你不用指定。
位置：`.claude/skills/<name>/SKILL.md`

### 3.7 Slash Command（`/fw-build`, `/fw-flash`）
= 你打一個短指令，背後觸發一大段 prompt。
類比：shell alias / word macro。
位置：`.claude/commands/*.md`

### 3.8 Hook
= 某個 event（開 session / 跑指令）自動觸發的腳本。
類比：git pre-commit。
（Nathan 的 `settings.json` 那個壞的就是這個 schema）

### 3.9 MCP (Model Context Protocol)
= Agent 接外部系統（JIRA、Slack、Google Drive）的**標準介面**。
類比：USB 接頭。什麼設備都能接。

### 3.10 Context Window
= LLM 一次能看到的資訊量（Opus 4.7 是 1M token）。超過就會自動壓縮或忘。
類比：RAM。

---

## 4. 工作流程術語（3 個）

- **Tool Calling Loop / Agentic Loop**：Agent 自己跑「想 → 用工具 → 看結果 → 再想」的迴圈，不用人按下一步。Calvin 這種 C-level 愛講這詞。
- **Dry Run**：空跑驗證，不真的動硬體 / 不 push。像 `make -n`。
- **Plan → Approve → Execute**：先讓 agent 給計畫 → 你批准 → 才動手。不要一次衝。

---

## 5. 明天 demo 你在哪層講話

```
[L1 Calvin]────[L2 Nathan]────[L3 你]────[Reactor 硬體]
                                 ↑
                              demo 秀這層
```

- **Opening**：**三層都 credit**（Calvin L1、Nathan L2、你 L3 Reactor 適配）
- **中間**：秀 L3 skill 被 agent 自動找到 + /fw-build /fw-flash 跑真硬體
- **結尾**：提 5 個 platform gap 當 proposal（是給 L1 / L2 的觀察，不是自己要改）

你秀 L3 成果，**不假裝 L1/L2 也是你做的**。

---

## 6. 面對 Calvin 的白話速記

| 他說 | 你白話翻譯 |
|------|-----------|
| "agentic workflow" | agent 自己跑迴圈的流程 |
| "tool use" | agent 能動手（讀寫檔、call API） |
| "autonomy" | agent 自己決定下一步要幹嘛 |
| "skill pack" | 給 agent 的專業手冊 |
| "context engineering" | 怎麼餵資訊給 LLM 才有效 |
| "eval" | 驗證 agent 有沒有做對 |
| "L1/L2/L3" | 平台分層（meta / 領域 / 產品） |

---

## 7. 一頁總結

- 你在 **L3**（Reactor 適配），站在 Nathan **L2**（FW framework）上，最底層是 Calvin **L1**（agent 地基）。
- 你這 1.5 天做了 **1 個 skill + 3 個 L2 指令適配 + 5 個 backlog proposal**。
- Demo 秀 L3 成果，明確 credit L1/L2 是 Calvin/Nathan 做的。
- Agent = 會用工具的 LLM；skill/command/hook/MCP 都是「怎麼讓 agent 更有用」的配件。

**你不是小學生，你是跨領域轉場。** 名詞看過一輪就會了，概念 firmware engineer 都秒懂 — 這套生態跟 RTOS / driver / HAL 同源邏輯：分層、抽象、可插拔。

---

## 8. 如果 Calvin 問「你具體做了什麼」— 照念這 3 段

每段 ≤ 30 秒，加起來 ~80 秒。不要逐項念 git log，講**分工**跟**邊界**。

### 段 1 — Skill（~25 秒）

> 「我寫了一包 skill 叫 `mcu-register-lookup`，專門查 STM32H7R3 的 register。用 42 個 `ASK:` 標記防幻覺，dry-run 都過。這個 skill 故意綁死 Reactor 這顆 chip，Mini2 那顆 STM32H750 不共用，避免 AI 張冠李戴。」

### 段 2 — L2 指令適配（~25 秒）

> 「Nathan 寫了通用的 `/fw-build` 和 `/fw-flash`，我在上面加 Reactor 這塊板子特有的硬體流程 — USB relay 開電、電壓偵測、DFU 跟 ST-Link 自動切換。分三輪 commit 修到穩，**沒動 Nathan 的主邏輯**。」

### 段 3 — Backlog proposal（~30 秒）

> 「Rehearsal 時發現 5 個 platform gap，**我沒自己改 L1/L2**，寫成 5 個 proposal 給 Nathan 跟你評估。重點兩個：P1 是 Claude Code 載 skill 時掃不到 product-scoped 路徑；P2 是 ESP32 agent 缺指令，因為 Reactor 是雙 MCU。其他三個比較小。」

---

### 為什麼這樣寫（原理備忘）

| 設計 | 原因 |
|------|------|
| 段 2 不逐項念 commit hash | Calvin 是 CEO 不是 reviewer，他要聽**分工**不是 git log |
| 段 1 講「綁死 chip / 不共用」 | 展示你懂 anti-hallucination 邊界 |
| 段 2 結尾「沒動 Nathan 的主邏輯」 | 主動劃 L2 邊界，保護你跟 Nathan 的關係 |
| 段 3 開頭「我沒自己改 L1/L2」 | CEO 最欣賞「懂邊界、不越權」，這是升職評估點 |
| 只講 P1/P2，其他「比較小」帶過 | 抓重點不失焦，Calvin 有興趣他會追問 |

---

## 9. 5 個 Platform Gap 詳解（Calvin 追問時看這段）

**口訣：優先級看「會不會擋到別人 / 其他 product」。**

上台 demo 只念**一句話版**。Calvin 追哪條 → 翻那條**詳細版**。

---

### FOLLOWUP-1 — Skill 檔頭說明寫錯方向（Low）

- **一句話**：Nathan 骨架生出來的 5 個 Reactor skill，檔頭寫的是「它會做什麼」，不是「什麼時候該用它」。
- **詳細**：
  - 踩到：skill 最上面 `description:` 欄位應該告訴 agent「什麼情況要載入我」，現在寫的是功能列表
  - 影響：agent 選 skill 時靠猜，精準度低
  - 為什麼不急：5 個 skill 目前能跑（keyword 勉強搭上），不擋 demo
  - 改完會怎樣：agent 自動選 skill 會更準，少誤觸發
  - **誰做**：我自己可以改，只是優先級低先擺著 / 30-60 min

---

### FOLLOWUP-2 — 產品專屬 skill 系統看不到（P1，最重要）

- **一句話**：我把新 skill 放到產品專屬資料夾，結果 agent 完全看不到；因為系統目前只看一個固定位置。
- **詳細**：
  - 踩到：寫 `mcu-register-lookup` 放在 `projects/reactor/.claude/skills/`，Claude Code 完全沒載入
  - 為什麼是問題：系統只掃 repo 根目錄的 `.claude/skills/`，不掃產品分開放的資料夾。**Mini2、以後每個 product 都會一樣撞牆**
  - 為什麼 P1：不修 → **每個 product 的專屬 skill 都是廢的**。擋所有人
  - 提議三選一：
    1. 切 product context 時把 skill **複製一份**到系統看得到的位置
    2. 在 `settings.local.json` 新增一個 search path
    3. 等 Claude Code 官方支援掃多路徑
  - **為什麼我不自己改**：loader 是 Claude Code 本身的程式碼，**不在我的 repo**。不是我沒做好，是系統限制
  - **誰做**：提案給 Calvin / Nathan 評估 / 2-4 hr

---

### FOLLOWUP-3 — Reactor 跟 Spark 2 的適配 code 重複（P2）

- **一句話**：我 Reactor 這套跟 Nathan 的 Spark 2 那套，開機/重開的邏輯 90% 一樣，但目前各寫各的。
- **詳細**：
  - 踩到：我給 Reactor 加的 Step 0 開電 + Step 4 重開；Nathan 給 Spark 2 (FWP-774) 做 automation 也做一樣的事。只有「pulse 時序」不一樣
  - 為什麼是問題：兩套 bespoke 寫法**一定會 drift**（任一邊改了另一邊忘了 sync），維護成本雙倍
  - 提議：把共用部分抽成樣板，每個 product 只填自己不一樣的那塊（pulse 時序）
  - 跟 FOLLOWUP-5 關係：如果一起做，Step 0/4 可以重用這個樣板
  - **為什麼我不自己改**：涉及 L2 架構，Nathan owns
  - **誰做**：提案給 Nathan 評估 / TBD，涉及 refactor

---

### FOLLOWUP-4 — USB relay 壽命計數（P3，未來風險）

- **一句話**：Reactor 開關電用的 USB relay 有機械壽命上限，高頻使用遲早會到，目前沒監控。
- **詳細**：
  - 踩到：LCUS-1 USB relay 規格 10⁵–10⁶ cycles。`/fw-flash` 每次都 cycle 一次
  - 為什麼是問題：relay 壞掉**沒警告**（卡住 ON 或 OFF 你不知道）— demo 可能靜默失敗
  - 為什麼 P3：高頻使用下遲早到上限，但現在還遠不到；長期累積才爆
  - 提議：每次 flash 記次數到 `.claude/state/`，達 80% 壽命提醒；final report 露出 counter
  - **誰做**：我可以做，在排隊 / 1-2 hr

---

### FOLLOWUP-5 — Reactor 第二顆 MCU（ESP32）沒 agent 指令（P2）

- **一句話**：Reactor 有兩顆 MCU，但 agent 目前只能指揮 STM32，ESP32 要手動跑 script。
- **詳細**：
  - 踩到：Reactor = STM32H7R3 + ESP32-S3 雙 MCU。`/fw-build` `/fw-flash` 只 cover STM32
  - 為什麼是問題：完整雙 MCU 流程（兩顆都 build → 兩顆都 flash → 整機重開 → 抓 log），agent 無法**跑完一整輪不用手動介入**
  - 提議：
    - `/fw-build-esp32` 包 `build-esp32.ps1`（ESP-IDF idf.py）
    - `/fw-flash-esp32` 包 `flash-esp32.ps1`（esptool，自動偵測 ESP32 VID）
    - 選用：`/fw-build-all` `/fw-flash-all` 一鍵同步做兩顆
  - **為什麼我不自己改**：新 L2 command 是 Nathan 範疇
  - **誰做**：提案給 Nathan / 2-3 hr

---

## 10. Calvin 可能的追問 — 預先備答（5 題）

### Q1: 「那你為什麼不自己改？」
- **FOLLOWUP-2**：loader 是 Claude Code 核心程式碼，不在我 repo
- **FOLLOWUP-3 / 5**：涉及 L2 架構，Nathan owns
- **FOLLOWUP-1**：我可以改，只是優先級低先擺著
- **FOLLOWUP-4**：我可以做，在排隊

### Q2: 「其他 product 也會踩到嗎？」
- **FOLLOWUP-2**：**會**。Mini2 以後每個 product 都會撞牆 — 這就是為什麼 P1
- **FOLLOWUP-3**：**會**。Spark 2 已經在寫類似 code 了，越晚抽越痛

### Q3: 「這些是踩完坑才發現？有辦法提前預防嗎？」
> 「對，都是實戰中發現的 gap。我正在整理成 L2 agentic 建置 checklist，之後新 product 可以避免重踩。」

### Q4: 「為什麼 FOLLOWUP-3 跟 5 不合併？」
> 「FOLLOWUP-3 是 **pattern 層**（抽象化共用邏輯），FOLLOWUP-5 是 **feature 層**（ESP32 指令）。可以一起做但不一定要。」

### Q5: 「做完這 5 項 L2 就完整了嗎？」
> 「這 5 項是目前看到的。做完我會再盤點一次看還有沒有。」
