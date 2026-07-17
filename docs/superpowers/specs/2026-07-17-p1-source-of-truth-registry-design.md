# P1 — Source-of-Truth Registry (capture-first) — Design Spec

**Date:** 2026-07-17
**Author:** Alice Chan (with Claude)
**Status:** 設計已核可，待寫實作計畫
**Parent:** `2026-07-17-sop-governance-p0-metrics-design.md`（全系統藍圖 + §7 稽核 v2 修正）

## 1. 目的

建立**結構化、原子化、機械可查**的事實庫，讓 cheap model 與 hooks 能以確定性 key 查找真相；並把「捕捉使用者講的事實」做成一等公民流程。

**P1 只做事實（source-of-truth）**。行為守則（SOP）不在此範圍。

## 2. 兩個改變前提的實測發現

### 2.1 這是「溫啟動」，不是冷啟動
稽核最大疑慮是「registry 空 → 使用者被永久課稅」。**盤點證明事實已被捕捉過**：`memory/reference_*.md` 14 檔 + 3 個錯置在 feedback 的（`com19`/`com50`/`check_hardware_pid`）已含真實硬體 ground-truth。
→ **頭部事實已在手**，P1 主要是**遷移**而非從零問起。冷啟動的稅過去幾個月已由使用者繳掉。

### 2.2 問題是 long-tail，但事實是 head-heavy（28 session／1120 則 prompt 實測）
| 證據（regex 自動抽取，無選擇偏差） | 跨 ≥2 session 重現率 |
|---|---|
| JIRA ticket（＝「問題/主題」代理） | **22%**（18 個裡 4 個）→ 每次都是新問題 |
| PID/VID（＝「硬體事實」代理） | **71%**（21 個裡 15 個），90% 提及來自會重現的 |

→ **永遠不問同一個問題，但一直需要同一批事實。** capture ROI 成立，但必須 **key 在事實上，不是 key 在問題上**。核心事實約 **50 個實體** → registry 是「一張表」，不是知識庫。

> 誠實標註：實體重現 ≠ 同一條事實被重複需要（代理指標）。keyword 類（90%）因清單為人工挑選、有選擇偏差，**不採信為論據**。COM port 樣本僅 5 次，無訊號。

## 3. Schema

`handover/registry/facts.jsonl` — 一行一條原子事實。

```json
{"key":"PID:295D:0501","scope":"Reactor","fact":"295D:0501 = Actions BT Audio chip，不是 MCU",
 "source":"reference_reactor_usb_pid_chip_map.md｜實機驗證","owner":"alice",
 "captured":"2026-07-17","ttl":null,"volatile":false,"confidence":"verified"}
```

| 欄位 | 用途 | 對應稽核要求 |
|---|---|---|
| `key` | 確定性查找鍵（如 `PID:295D:0501`） | 檢索機械化——笨 model 不用「選」fact；miss → 硬升級 |
| `scope` | **事實識別碼的一部分**：`(key, scope)` 兩者合起來才識別一筆事實，不只是描述性標籤 | 防 **H7R3/H750 跨情境誤用**（既有教訓） |
| `fact` | 單一原子陳述 | 可並排比對 |
| `source` | provenance | 可回溯，防毒化 |
| `owner` | 負責人 | 稽核要求：事實要有主 |
| `ttl` | 到期日（null=長青） | 過期 → **強制升級**，不靜默使用 |
| `volatile` | true = **永不快取為真相** | COM port 等高變動事實必須現場探測 |
| `confidence` | verified / reported / assumed | 不可把推測當已驗證 |

**格式決策**
- **JSONL 而非 markdown**：hooks 與 cheap model 需要確定性 key 查找，markdown 做不到。
- **JSONL 而非 SQLite**：稽核要求「registry diff 需人審 + 可回滾」——二進位檔無法 `git diff` / PR review。

**volatile 事實的存法**：不存值，存**探測指令**。
例：`{"key":"COM:ESP32","volatile":true,"fact":"ESP32 的 COM 號會變，不可假設","probe":"Get-PnpDevice 查 VID 303A","source":"..."}`
→ 直接解掉盤點發現的 **COM7 vs COM19 三處衝突**（COM 號本來就不該當常數存）。

## 4. 捕捉流程（核心；貴 model 只在這裡動）

稽核結論：**opus 判斷力放在「捕捉當下」**（存一次、之後每次重用都省），而非事後抽查（成本永遠重複，且一次抽查 ≈ 直接用 opus 做完整件事）。

```
使用者講事實 / 糾正
   ▼
opus 擷取成 schema（原子化 + 定 scope/key）
   ▼
opus 自驗（比對現有 registry、檢查 scope 是否足夠、confidence 是否誠實）
   ├── 一般 → 存入
   └── 觸發回問使用者的條件（僅這三種，避免 approval fatigue）：
        1. 與現有事實**衝突**
        2. **高風險域**（刷韌體 / PID / DFU / 不可逆動作相關）
        3. opus 自驗**信心不足 / scope 不明**
   ▼
週報 digest：本週新增/修改的事實，供使用者事後抽看
```

## 5. 檢索

- **確定性 key 查找**（不做語意比對——笨 model 選錯 fact 也會通過檢查）。
- **miss → 硬升級**，不准即興發揮。
- `ttl` 過期 → 視同 miss。
- `volatile:true` → 不回傳值，回傳 probe 指令。

## 6. 遷移（registry 取代 memory 的事實檔）

**決策**：registry 為單一真相；`reference_*.md` 遷移後刪除，`MEMORY.md` 改指向 registry。理由：兩份真相分歧正是 COM7/COM19 衝突的成因。

**⚠️ 安全前提**：`C:\Users\alice\.claude\projects\D--mybot\memory\` **不在 git 版控**——刪除不可回復。

必須依序：
1. **先備份**整個 memory/ 到 `fw-multi-agent`（可回復）
2. 逐檔**完整讀取**後遷移（不可只讀 description）
3. **驗證無遺漏**：每個來源檔的每條事實都能在 registry 找到對應 key（產出對照表）
4. 驗證通過**才刪**原檔，並更新 MEMORY.md 指向 registry

**遷移範圍（P1 v1）——逐檔分流，不是全搬**
`reference_*` 共 14 檔，但**並非全部都是長青硬體事實**（例：`reference_google_drive_visibility` 比較像偏好註記）。遷移前每檔先分流：

| 分流 | 處置 |
|---|---|
| 長青硬體/工具事實（PID map、USB hub 架構、DFU bootloader repos、DFU flash、esp32 power、extmemloader、stlink flash、updater bundle、spark2 boot、relay pulse 等） | → registry |
| 錯置在 feedback 的事實（`check_hardware_pid`、`com19_means_esp32_on`、`com50_stlink_app_log`、`production_stm32_no_log`） | → registry（COM 類一律 `volatile:true`） |
| 混合型（`feedback_stm32h7_chip_isolation`：H7R3≠H750 是事實／anti-hallucination 優先是守則） | → 拆分：事實進 registry、守則留 SOP |
| 非事實類（偏好、可見性註記、時效性 job 參數） | → 留在 memory，不遷 |

分流結果需列表給使用者確認後才執行刪除。

## 7. 不做（YAGNI）

- **不做 hook 強制**（檢索/升級的強制力＝P2）
- **不做 opus 事後稽核**（P3）
- **不做 SOP 整併**（feedback_* 的 7 併 1 / 3 併 1 是守則清理，另案）
- 不遷 `project_*`（多為時效性狀態，非長青事實）
- 不做語意檢索

## 8. 風險

| 風險 | 緩解 |
|---|---|
| **遷移遺漏/誤譯事實**（不可回復） | 先備份 → 逐條對照表驗證 → 才刪 |
| **registry poisoning**（存錯比沒存更糟） | 存入當下驗證；conflict/高風險/低信心 → 回問使用者；`source`+`confidence` 可回溯 |
| **單點故障**（一筆錯，全體一起錯） | `ttl` + `owner` + 定期 reality-reconciliation；volatile 不快取 |
| **approval fatigue** | 回問條件嚴格限縮為三種；其餘走週報事後抽看 |
| **只加不刪 → 肥大** | `ttl` 到期清理；P4 改善層負責精簡 |

## 9. 驗收標準

1. `facts.jsonl` 存在且每行符合 schema（parser 驗證通過）。
2. 種子遷移完成：對照表顯示**來源檔每條事實皆有對應 key**，無遺漏。
3. COM 類事實以 `volatile:true` + probe 存在，registry 內**不存在** COM 號常數。
4. 確定性查找可用：查找以 `(key, scope)` 為準；`key` 命中多個 `scope` 時回傳 `ambiguous`（不猜哪一筆），不提供 `scope` 且只命中一筆才回傳事實；miss 回傳明確 miss（不猜）。
5. 原 `reference_*.md` 已備份且刪除，`MEMORY.md` 指向 registry。
6. `scope` 欄位能區隔 H7R3 / H750（抽驗不會跨情境誤用）。
