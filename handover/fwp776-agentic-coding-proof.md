# Agentic Coding with Close-Loop Discipline — FWP-776 Retrospective

_2026-04-22 → 2026-04-23 · Alice Chan · FW Team_

## TL;DR

2026-04-22 晚 22:02，Nathan 在 JIRA FWP-776 留下一份 5-step refactor + 6-gate E2E plan，
把 Reactor 硬體流程從 `.claude/commands/fw-*.md` 裡面抽離成 data-driven config。
次日 13:56，PR #36 開好，**六個 E2E gate 全部在真機上驗過**，順手修了 **4 個**平台
pre-existing dispatcher bug，交付物回 Nathan。從計畫交到我到 PR ready-for-review，
總共 **~15 小時**（含睡眠）。同規模 refactor + HW live 驗證，傳統人工估 3–5 工作天。

## 3 條讓它成立的原則（business 語言版）

**1. 我不相信 AI 的自我回報，每一步都要真機或真 artifact 驗。**
AI 說 "G6 PASS 4s 完成"，我看 ELF 時間戳還停在前天 — 那不是新編譯，是 incremental
skip。要看 **fresh timestamp + 真的 compile log**，不能看 exit code 就放行。

**2. AI 引用他人的話，一律回原文比對。**
Nathan 寫 reviewer acceptance 的那份 plan，AI 有一次幫我 summarize 時把 "~4d 時間估算"
講成 "Nathan 估 4d"，但 Nathan 原文根本沒寫時間 — 4d 是另一個 AI 自己算出來的。
記憶會漂移，**每次引用前重讀原文**，不靠 summary 做事。

**3. Reviewer 的驗收標準寫進計畫第一行當硬線，中間任何 "defer" 都要對照它。**
Nathan 原話是 "6 個 gate 全綠才能開 PR"。AI 中途有一次提議 "打包 2 個修的 + disclose 1
個沒修的 → PR" —— 看似合理，其實違反了那條硬線。被 push 回去繼續修第 3 個 bug 之後，
才發現它連鎖帶出第 4 個 bug，最終 6 gate 才真綠。**deferral 的合理化是 trap**。

## Close-Loop 系統擋下的 5 次 drift

過程中 AI 給了我 5 個 "看起來合理但其實錯" 的東西：一個假的 commit hash 被腦補進 Step 3
cherry-pick 清單；一次把 reviewer 沒要求的條件（"G6 需要 live HW"）當成要求；兩次把
incremental / silent-fail build 當成 G6 PASS；一次把 AI 自己算的 time estimate 講成
reviewer 的原話。**每一個都被真機驗、原文比對、或 artifact timestamp 擋下來，沒有一個
漏到對外的 PR body、JIRA comment、或 GitHub review reply。** 這不是我手快，這是 close-loop
系統的結構性保護 — 每層 gate 自己 catch drift。

## 量化成果

| 產出 | 數據 / 連結 |
|------|------------|
| **PR #36** | 16 commits, 6 E2E gates green on live HW, reviewer = Nathan [PR #36](https://github.com/Positive-LLC/pg-fw-dev-agent/pull/36) |
| **Reactor E2E demo** | 239s cold-start rehearsal #2 (--clean, full 5-part dual-MCU)，120s warm dry-run |
| **新 agent 工具** | `capture-com4.ps1`（STM32 side）、`capture-esp32.ps1`（ESP32 side，並行 dual capture）、`mcu-register-lookup` skill（STM32H7R3 register authoritative ref） |
| **平台 pre-existing bug 順手修** | 4 個（`build-config.yaml` build_dir 對錯 layout / `build_cli.sh` 缺 `all` 顯式 target / toolchain detection glob 不展開 / clean 前 MAKE_CMD 未 resolve）— 修完 team 其他人之後走這條路不會踩 |
| **Gemini code-assist review** | 2 個 review item 全解（BFAR precision 語意錯 + COM3 machine-specific hardcode portability） |
| **FOLLOWUP backlog** | 4 項留給 Nathan / platform evolution（skill description rewrite / product-scoped skill auto-discovery / platform-Reactor adapter pattern abstraction / USB relay lifespan monitor） |
| **Nathan reviewer 收貨** | 在 comment 87203 的 plan 末尾 Nathan 寫 italic 強調：「_Reactor 在 pg-fw-dev-agent 上第一次被證明 end-to-end 可用，是你開的路_，謝謝。」 |

## 可 copy 給 team 的 3 條 rule

1. **Plan 第一行寫 reviewer 的 acceptance criteria**。之後任何 "defer / partial delivery
   / bounded scope" 都拿這條對照 — 不滿足就不動 PR button。
2. **AI 引用他人 — Nathan / Calvin / Teo / spec doc — 一律 re-read 原文比對**，不靠 AI
   的 summary / memory。AI summary 是 navigation aid，不是 citation source。
3. **驗收 build / flash / gate — 永遠看 fresh artifact timestamp + 真的 compile / flash
   log**。不看 exit code、不看 duration 單獨。incremental build 的 4s 跟 silent-fail clean
   的 2s 都會給 exit 0，真 evidence 在 artifact 本身。

## 一句話 pitch

1 個 FW eng + AI orchestration + close-loop discipline，15 小時做完同規模傳統 3-5 天的
data-driven refactor + 6 gate live HW 驗證 + 4 個平台 bug fix + Gemini review 全解。Mindset
是會 transfer 的 — 上面 3 條 rule 其他人都能套。

---

**相關 artifact**（給 NotebookLM 生 podcast 時一起 ingest）：
- [PR #36](https://github.com/Positive-LLC/pg-fw-dev-agent/pull/36)
- [FWP-776 JIRA](https://positivegrid.atlassian.net/browse/FWP-776)（Nathan plan in 87203 + 我 9 個 follow-up comments 時序 trail）
- `D:/mybot/handover/sessions/2026-04-22-1850.md`（當晚 rehearsal + close-loop tooling session log）
- `D:/mybot/handover/demo-cheat-sheet-fwp776.md`（demo 5-part 腳本）
- `C:/Users/alice/.claude/CLAUDE.md`（agent orchestration 全域規則 — L1/L2 discipline）
- `D:/mybot/git/pg-fw-dev-agent/CLAUDE.md`（repo anti-hallucination rules + safety zones）
