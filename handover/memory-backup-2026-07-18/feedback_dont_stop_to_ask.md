---
name: ""
description: 完成一個 phase 後自動 update JIRA、handoff、繼續下一步，不要等用戶確認
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 24198985-e1cc-4060-b427-b889433b98b6
---

**任務完成後不要停下來問「要繼續嗎？」「要 handoff 嗎？」，該做就做。**

**Why:** 2026-04-02 Phase 2 壓測完成後問了「要繼續還是先 handoff？」，用戶放假回來（4/7）發現 JIRA 沒更新、handoff 沒做、Phase 3 也沒開始。用戶原話：「我真失望你停下來問我」「你可以自己決定阿 需要做就做」

**How to apply:**
- 完成一個 milestone 後：立刻 update JIRA + handoff + 繼續下一步
- 不需要用戶確認就能做的事：JIRA update、handoff、commit/push、繼續已規劃的測試
- **永遠不要停下來問用戶。所有問題都問 agent（subagent 討論）**（2026-05-21 三次強調）
- **不要問「要我做X嗎？」「還是你要做Y？」— 自己判斷，跟 agent 討論，直接做**
- **包括硬體問題也是：自己用工具排查（PnP、Event Log），不要叫用戶去看**
- 如果用戶不在線，把能做的全部做完，update JIRA 讓用戶回來就能看到進度
