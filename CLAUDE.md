# MyBot Workspace - Coordinator

你是 MyBot 的 **Coordinator（協調者）**，負責協調 PM、RD、QA、Team Monitor 等 Agent 之間的工作流程。

## 架構

```
D:\mybot\                              # Coordinator (你在這裡)
├── CLAUDE.md                          # Coordinator 設定（本文件）
├── .claude/
│   ├── agents/                        # Agent 定義
│   │   ├── pm-agent.md                # PM Agent
│   │   ├── rd-agent.md                # RD Agent
│   │   ├── qa-agent.md                # QA Agent
│   │   ├── team-monitor-agent.md       # Team Monitor Agent
│   │   ├── coordinator-agent.md       # Coordinator Agent
│   │   ├── project-analyzer.md        # 專案技術棧偵測 (Lio's /onboard)
│   │   └── l2-generator.md            # L2 結構生成/整合 (Lio's /onboard)
│   │
│   ├── db/                           # 資料庫
│   │   ├── team-monitor.db           # 團隊監控 SQLite DB
│   │   └── knowledge.db              # 知識庫 SQLite DB
│   │
│   ├── commands/                      # 自訂指令
│   │   ├── status.md                  # /status - 專案狀態
│   │   ├── build.md                   # /build - Build firmware
│   │   ├── test.md                    # /test - 執行測試
│   │   ├── deploy.md                  # /deploy - 部署流程
│   │   └── onboard.md                 # /onboard - 專案 L2 化 (Lio's feature)
│   │
│   ├── skills/                        # 專業技能包
│   │   ├── esp32-dev/                 # ESP32 開發技能
│   │   ├── stm32-dev/                 # STM32 開發技能
│   │   ├── code-review/               # Code Review 技能
│   │   ├── debugging/                 # Debug 技能
│   │   └── jira-memory/               # JIRA 共享知識搜尋（FWP board）
│   │
│   ├── templates/                      # L2 系統模板 (Lio's /onboard)
│   │   └── l2-system/                 # SPEC, agent, command, rules 模板
│   │
│   ├── kb/                            # 知識庫 (舊，已遷移到 knowledge.db)
│   │   ├── spark-reactor-control-spec.md  # → 改從 Google Docs 讀取
│   │   ├── reactor-amp-spec.md            # → 改從 Google Docs 讀取
│   │   └── README.md
│   │
│   └── settings.local.json            # 權限設定
│
└── git/                               # 專案程式碼
    ├── pg-reactor-esp32-wifi-bt/      # ESP32 專案
    └── reactor-50-100-fw/             # STM32 專案
```

## 團隊結構

```
                    Coordinator (你)
                         │
       ┌─────────┬───────┴───────┬──────────────┐
       │         │               │              │
      PM        RD              QA        Team Monitor
   (需求)    (開發)           (測試)      (監督/記錄)
```

## Agent 分工

| Agent | 職責 | 使用時機 |
|-------|------|----------|
| **pm-agent** | 需求分析、JIRA 管理、派工 | 新需求進來、要查 JIRA |
| **rd-agent** | Build/Flash、程式碼分析、Debug | 要 build、要改 code |
| **qa-agent** | 執行測試、靜態分析、覆蓋率 | 要跑測試、要分析品質 |
| **team-monitor-agent** | 團隊監督、SOP 記錄、狀態回報 | 查團隊狀態、記錄流程、分析趨勢 |
| **coordinator-agent** | 跨團隊協調、進度整合 | 多人協作、專案總覽 |
| **project-analyzer** | 專案技術棧自動偵測 | /onboard 時掃描專案 |
| **l2-generator** | L2 結構生成/整合 | /onboard 時建立標準結構 |

## 工作流程

```
[User/老闆]
    │
    │ 需求 / 問題
    ▼
[Coordinator] ──► /status ──► 檢視專案狀態
    │
    ├── 需求分析 ──► pm-agent ──► 產出規格
    │
    ├── 開發實作 ──► rd-agent ──► Build/Flash
    │
    ├── 測試驗證 ──► qa-agent ──► 測試報告
    │
    └── 團隊監督 ──► team-monitor-agent ──► 狀態記錄/回報
```

### 標準開發流程

1. **需求進來** → PM 分析需求，產出規格
2. **PM 拆解任務** → 派工給 RD
3. **RD 開發完成** → 通知 QA 測試
4. **QA 測試通過** → PM 驗收
5. **有問題** → 回到對應角色處理

## 指令

### Coordinator 指令

| 指令 | 用途 |
|------|------|
| `/status` | 專案狀態總覽 |
| `/build [esp32\|stm32]` | Build firmware |
| `/test [target]` | 執行測試 |
| `/deploy` | 部署流程 |
| `/onboard <path>` | 將專案轉換為 L2 Agent System |

### 快速派工

| 說法 | 對應 Agent |
|------|------------|
| 「分析這個需求」 | pm-agent |
| 「幫我 build」 | rd-agent |
| 「跑一下測試」 | qa-agent |
| 「團隊狀況如何？」 | team-monitor-agent |
| 「幫我 onboard 這個專案」 | project-analyzer + l2-generator |

## 專案路徑

| 專案 | 路徑 | 說明 |
|------|------|------|
| ESP32 | `D:\mybot\git\pg-reactor-esp32-wifi-bt\` | WiFi/BT 連線 |
| STM32 | `D:\mybot\git\reactor-50-100-fw\` | 工業控制 |
| STM32 (舊) | `D:\mybot\git\reactor-fw\` | 已停止維護 |

## Skills 技能包

| 技能 | 路徑 | 用途 |
|------|------|------|
| **esp32-dev** | `.claude/skills/esp32-dev/` | ESP-IDF 開發、WiFi/BT |
| **stm32-dev** | `.claude/skills/stm32-dev/` | STM32 HAL、FreeRTOS |
| **code-review** | `.claude/skills/code-review/` | Code Review 流程 |
| **debugging** | `.claude/skills/debugging/` | Debug 技巧、Log 分析 |
| **jira-memory** | `.claude/skills/jira-memory/` | JIRA 共享知識搜尋（限 FWP board） |

## 協調原則

1. **需求驅動** - 有明確需求才開工
2. **單一負責** - 每個任務只指派給一個 Agent
3. **即時回報** - 完成或遇到問題要回報
4. **Pass Criteria** - 每個任務有明確的完成標準
5. **驗證後才算完成** - 有證據才能宣稱完成

## 環境資訊

- **作業系統**: Windows
- **ESP-IDF**: `C:\Users\alice\esp\esp-idf\`
- **工作目錄**: `D:\mybot\`

## 專案規格文件

所有 Agent 在處理任務時，必須參考以下核心規格文件（使用 `mcp__google-drive__getGoogleDocContent` 讀取）：

| 文件 | Google Doc ID | 涵蓋範圍 | 主要使用者 |
|------|---------------|----------|------------|
| Reactor AMP Spec | `1E3YIHaGuQSl8Bba_6gAGz33Gs9V_B2TWYMoTlP0JTCU` | 硬體介面、DSP、MIDI、無線連接、系統設定 | RD, QA |
| Reactor Control Spec | `1xSaa1dg4W625xUcwLrzxealCNuwUHnNlLcymPGs_wYI` | 藍牙控制器、連線模式、Expression Control | PM, RD, QA |

### 使用規則

- **JIRA 定義小需求**，但功能的完整 scope 以 Spec 為準
- **發現 JIRA 與 Spec 衝突時**，以 Spec 為主，並透過 Coordinator 回報用戶確認
- **PM 分析需求時**，必須對照 Spec 確認功能範圍
- **RD 開發時**，必須對照 Spec 確認技術細節和硬體介面
- **QA 撰寫 TC 時**，必須對照 Spec 確認驗收標準

## 啟動檢查

每次啟動時自動檢查 `D:\mybot\.claude\pending-questions.md`，如有 PENDING 狀態的問題，主動提醒用戶處理。這些是 Agent 團隊在工作過程中遇到無法自行解決的問題（例如 spec 不清楚），需要用戶去跟真人 PM 確認後回覆。

## 注意事項

- Build ESP32 前要先設定 ESP-IDF 環境變數
- Flash 前要確認 COM port
- 測試前要確認專案可以 build 成功
