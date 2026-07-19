---
name: 不推測用證據（與 AI 討論同等重要）
description: 【鐵律】技術分析必須基於 source code 證據（file:line），不可把推測當結論回報。說「應該」之前必須先用工具驗證。重要性等同「必須先跟 subagent 討論」
type: feedback
originSessionId: 96c15cdc-a1a3-4ab9-93a5-dd71363036c3
---
技術分析不可推測，每個結論必須附 file:line 證據。**重要性等同「必須先跟 subagent 討論」，兩者都是鐵律。**

**Why:** (1) Subagent 曾錯誤宣稱 RTT code 造成 MSP 變化（2026-05-02 STFS-491 分析），實際上 GD32 clean build 也是相同 MSP，差異是 chip 造成的。(2) 2026-05-05 flash app 後說「應該正常開機」但實際 checksum 驗證失敗，裝置卡在 bootloader。用戶明確說：「我不想再聽到應該，用證據說話」。

**How to apply:**
- 說「應該」之前 → 先用工具驗證（JLink dump、grep、git diff、binary compare）
- 每個技術結論必須包含：結論（一句話）、信心等級（已驗證/高度相關/待驗證）、證據（file:line 或工具輸出）、驗證方法
- 不可以只 verify binary 寫入就宣稱「checksum 會過」— 要實際算 checksum 驗證
- Rule 檔在 `.claude/rules/evidence-based-analysis.md`
