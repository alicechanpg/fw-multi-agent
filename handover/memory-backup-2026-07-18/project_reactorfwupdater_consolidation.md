---
name: project_reactorfwupdater_consolidation
description: ReactorFwUpdater 是 Calvin 7/3 AI-coding 指示下選定的 Fable 治理整理目標；已完成
metadata: 
  node_type: memory
  type: project
  originSessionId: 5478b7d1-f3c9-4d30-ba24-bf7bb13251a4
---

回應 Calvin 2026-07-03 於 Slack #ai-coding-agents 的指示（挑 1–2 個最重要 repo 請 Fable 整理，落實 substrate / agentic 治理），FW 團隊選定 **ReactorFwUpdater** 為目標並於 2026-07-09 完成。

**為何選它**：近三個月最活躍（44 commits）卻先前無 CLAUDE.md/.claude/agent 治理層（僅一份過時的大寫 Doc/）。

**Fable 產出**：`CLAUDE.md` + `docs/ARCHITECTURE.md`（state machine 重建，HEAD 5bca52c）+ `docs/firmware-bundle.md`。每條附 file:line/commit 證據。已發 **PR #11**（Positive-LLC/ReactorFwUpdater，base main，assign Alice，branch `docs/agentic-governance-claude-md`，只含這 3 檔，additive）；**Alice 自己 merge**。

**與公司 stack 的連結（重點）**：目前**零連結**——這批只是獨立 markdown。連結機制：reactor-fw 靠 `.claude/platform-origin.json` → **pg-fw-agent-dev**（Lio L1 平台）同步治理；pg-fw-agent-dev 正在導入 **pg-stack dev-pack**（Nathan PR #63/#57）。ReactorFwUpdater 無 `.claude/`、未接入。要接公司 stack = 走 pg-fw-agent-dev/pg-stack（Nathan），但 Alice 明確表示**不要 block 在 Nathan**，PR 先獨立落地。

**歸檔**：專屬 ticket **FWP-819**（任務，指派 Alice，label reactor / component Firmware，Relates FWP-744）；FWP-744 也加了 comment（#91751）；Drive 成果摘要 = https://docs.google.com/document/d/1yrK2EtUCaj34z0vNWUBQ2rlkF2sBglDb0ACaTSRjbG0/edit （建在 My Drive root，尚未確認搬進 FW team 共享資料夾）。

**不重複做的（已查證）**：reactor-fw 已由 Lio L1 harness 治理；reactor-esp32（pg-reactor-esp32-wifi-bt）L2 harness 是 Alice 3 月建的、Lio 只做韌體且 2025-12-24 後未動；spark-esp32 在 GitHub 無獨立 repo（新一代 Spark 無線走 Airoha AB1585/1595 非 ESP32）。下一候選：pg-reactor-esp32（Teo 主導，需協調）。

**Fable 揪出的 repo 問題**：既有 Doc/ 過時（log 章節、version gate 位置、state 圖）；`Subprocess` 全域 64KB buffer + 120s timeout 是所有 shell-out 共同限制；FWP-814（Spark 併入）有未 commit WIP，schema 與 products.json 不一致。相關 [[project_fwp744_reactor_updater]]。
