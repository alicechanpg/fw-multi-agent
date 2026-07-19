---
name: no-guessing-strict
description: 嚴禁在沒有證據的情況下推測原因，用戶強烈要求 — 2026-05-22 再次強調
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 67a63fe7-8980-4227-b783-ca69f7a2639e
---

不要推測！找到證據再說。

**Why:** 用戶在 2026-05-22 debug USB CDC 問題時再次強烈糾正。我在 R50 firmware 沒有 CDC 時推測是「codec 初始化失敗導致系統異常」，完全沒有證據。用戶說：「please stop guess!!! find the evidence before guessing!!!!」

**How to apply:** 
- 觀察到異常行為 → 用工具讀取實際狀態（register dump、log、binary compare）
- 每個結論必須附 file:line 或工具輸出
- 「可能是」「有可能」「我猜」→ 改成「讓我讀取 X 來確認」
- 與 [[evidence-based]] 規則同級，但這條更嚴格：連假說都不要在回報給用戶時提，先驗證

Related: [[feedback_evidence_based]]
