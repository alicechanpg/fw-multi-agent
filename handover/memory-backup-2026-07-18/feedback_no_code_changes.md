---
name: feedback-no-code-changes
description: 不自己修「跟主題無關」的 bug；修任何 bug 一定要 report（2026-07-07 更新）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 247ba5b7-a279-418a-8d0e-deada3f6119a
---

規則放寬（2026-07-07）：原本「不自己修 code」改為「**不自己修跟主題無關的 bug**」，且「**修 bug 一定要 report**」。

**Why:** 跟主題有關的 bug 本來就是任務的一部分，該修；但用戶要知道每個改動改了什麼、為什麼改，所以修 bug 一定要回報清楚。跟主題無關的 bug 不要順手改（drive-by fix）。
**How to apply:** 
- **跟當前主題有關的 bug**：可以修，但**一定要 report**（改哪裡、改什麼、為什麼）。改 code 屬 L1，仍需兩輪 self-review。
- **跟主題無關的 bug**：不要自己改，回報就好，讓用戶決定
- Build error：回報位置和建議，讓用戶決定（不自行改）
- 用戶明確說「你改」「請改」→ 可以改
- Migration/cherry-pick 作業：只搬不改
