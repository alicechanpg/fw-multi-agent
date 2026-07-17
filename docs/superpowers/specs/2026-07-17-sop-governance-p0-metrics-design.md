# SOP Governance System — Design Spec

**Date:** 2026-07-17
**Author:** Alice Chan (with Claude)
**Status:** P0 approved, building

## 1. 終極目標（The vision）

用**企業管理的方式治理雙層 LLM**，形成「測量 → 稽核 → 改善」的閉環，讓便宜的 model 在 SOP 與 source-of-truth 的約束下把事做對，同時整體成本與試誤率持續下降。

三層組織（對照企業）：

| 角色 | 誰 | 對應企業管理 |
|------|-----|------------|
| **做事的人**（不確定就查 source-of-truth / 問使用者） | cheap model | 第一線員工 + SOP 手冊 + poka-yoke（防呆：不確定就停、就問） |
| **每 turn 稽核 + 記錄** | 貴 model (opus) | QA / 主管覆核 |
| **稽核後改整個機制**（改 SOP、改 source-of-truth） | 貴 model (opus) | 管理層持續改善（Kaizen / PDCA） |
| **可評估的指標**（token、試誤率） | 資料層 | KPI dashboard，給使用者 audit |

貴 model 的目標：讓 cheap model 的**試誤率↓、token↓**，同時 SOP 品質↑、成本↓（cost-of-quality / Six Sigma 的精神：用測量驅動改善）。

### 1.1 控制理論基礎（決定 P1–P4 怎麼落地）

安全工程的**控制層級（hierarchy of controls）**依可靠度排序控制手段，最關鍵分野：

- **Engineering control（工程控制）**：機制本身生效，不管行為者當下怎麼想。*Works regardless of what anyone does on a given day.* → **hook / harness / permission gate（有強制力）**。
- **Administrative control（行政控制）**：只有「每一次都選擇遵守」才生效，人會犯錯故不可靠。 → **SOP 文件 / memory / CLAUDE.md rules**。

**harness 不是 SOP，是工程控制。** agent「如同員工一樣不可控制」，所以「必須成立」的規則要做進 harness（強制力），而非寫成 SOP 文字。佐證：現有 memory rule 存在數月仍被違反（行政控制的固有失效）。

**反效果警告（normalization of deviance）**：純加強 enforcement/稽核會把違規趕到地下——停止回報、workaround 變隱形、組織失去「SOP 哪裡不符現實」的洞察。正解：把不遵守當**可用性問題**（「規則在需要的那一刻有沒有在手邊？」）而非紀律問題；改善來自**第一線回饋**。

### 1.2 由此得到的設計原則

1. 能硬做成 hook 的「必須成立」規則 → 一律工程控制（例：對外 URL 送出前 `gh api` 核對、PID 比對 registry）。
2. 不能硬 gate 的（語意對錯）→ 留行政控制，重點是「在對的時機把對的 fact 推到眼前」（可用性），而非加更多規則。
3. opus 改善層（P4）不是懲罰機器：讀 cheap worker 在哪試誤/被糾正，判斷是「規則沒對上現實」或「規則沒在需要時出現」，修**可用性**。
4. KPI 是診斷訊號，**不可當懲罰指標**（否則被 game、偏差轉入地下）。

來源：CDC / SafetyIQ（hierarchy of controls）、Tandm（why workers don't follow procedures）。

## 2. 分解（Decomposition）

一個 spec 塞不下，拆成 5 塊，各自獨立 spec → plan → 實作：

- **P0 — 可評估的 metric 層（本文件）**：量尺。沒有它，後面三層無法評估成效。
- **P1 — source-of-truth + SOP registry**：結構化、原子化、笨 model 也能並排比對的 facts 清單；收攏散在 `memory/reference_*.md` 的硬體 ground-truth；使用者當場講的事實自動記入。（同時評估現有 memory 系統的包袱並提改寫案。）
- **P2 — cheap worker 自檢**：做事層比對 registry，缺/不確定 → 問使用者或記下。
- **P3 — opus 每-turn 稽核**：對照 SOP + registry 給 verdict、更新 metric（精算「試誤/糾正」，取代 P0 的代理指標）。
- **P4 — opus 週期改善**：讀累積稽核，改 SOP/registry 去壓低 P0 的試誤率與 token，閉環。

建置順序：**P0 → P1 → P2/P3 → P4**。管理鐵律：先能量測，才能改善。

---

## 3. P0 詳細設計

### 目的
每個 session 從 harness transcript + audit trail 抽出效率/品質指標，寫進 audit，讓使用者看**跨 session 趨勢**。純測量、read-only、**不呼叫任何 model**。

### 架構（融入現有 hook，不另起爐灶）

```
Stop hook → session-digest.py
   ├─ metrics.compute(transcript, events, queued_count)
   │      ├→ digest 末尾附「## 效率 / Token」段
   │      └→ append handover/audit/metrics.jsonl（一 session 一行）
   └─ 既有 stale-handover 檢查不變

/audit-review → audit-report.py → 讀 metrics.jsonl → 顯示近 N 場 KPI 趨勢
```

### 元件

- **`handover/scripts/metrics.py`**（新）：
  - `compute(transcript_path, events, queued_count) -> dict` — 純函式，**永不 raise**（出錯回傳部分資料）。tokens 來自 transcript；tool/prompt 來自已載入的 audit `events`；interjections 用 digest 已算好的 `queued_count`（不重複 IO）。
  - `render_md(m) -> str` — 產出 digest 用的 markdown 段。
  - `append_record(path, session, m)` — append 一行 JSON 到 metrics.jsonl。
- **`session-digest.py`**（改）：載入 metrics，計算 → append 到 digest 字串 + 寫 metrics.jsonl。整段包在 try/except，**絕不阻斷 Stop hook**。
- **`audit-report.py`**（改）：新增「## 效率 / 成本 趨勢 (KPI)」段，讀 metrics.jsonl 中落在時間窗內的 session，列趨勢表。

### KPI 集合（全部機械可算，無 model）

| 欄位 | 定義 | 意義 |
|------|------|------|
| `out_tokens`, `cache_read`, `cache_create`, `input_tokens` | transcript usage 加總（主線） | 成本主軸 |
| `tokens_by_model` | 依 model 分佔 output | cheap vs opus 分佔（今日全 opus，欄位先備，P2 上線有值） |
| `turns` | 帶 usage 的 assistant 訊息數 | 規模 |
| `prompts` | UserPromptSubmit 數 | 規模 |
| `tool_calls`, `tool_fails`, `fail_rate` | audit trail | 執行品質 |
| `interjections` | 中途插話數（queued_count） | 試誤/導正的**代理指標** |
| `out_per_prompt`, `tools_per_prompt`, `interj_per_prompt` | 正規化 | 讓不同長短 session 可比較 |
| `duration_min` | audit trail 首末 ts | 規模 |

### 誠實標註（寫進機制，不隱瞞）

- `interjections` 是**代理指標 ≠ 已確認糾正**（regex 抓糾正會誤判）。精算留給 P3 opus 稽核。
- **subagent token 不在主 transcript**（sidechain 在各自 task jsonl）→ P0 只算主線，欄位 `subagent_tokens: null（未納入）`。
- `cache_read` 是每輪重讀累加，非唯一 token 量。

### 錯誤處理
- metrics.py 任何一步失敗 → 回傳已算出的部分，缺的欄位留 `None`；digest 照常產出。
- transcript 不存在 / 無 usage → tokens 全 `None`，其餘（來自 audit trail）照算。

### 驗證方式
- 對 7/16 真實 transcript（`2e3aafce`，922 usage 訊息）跑 `metrics.compute`，數字須對上今日手算：out≈1,623k、cache_read≈232M、model=claude-opus-4-8。
- 跑 `session-digest.py` 產一份 digest，確認多出「## 效率/Token」段且格式正確、無 exception。
- 跑 `audit-report.py`，確認多出 KPI 趨勢段。

### 不做（YAGNI）
- 不做即時/per-turn 寫入（P0 是 session 級；per-turn 稽核是 P3）。
- 不做獨立 dashboard / Slack 推送（先寫檔，需要再說）。
- 不呼叫 model（那是 P2/P3）。
- 不動 memory 系統（P1 處理）。
