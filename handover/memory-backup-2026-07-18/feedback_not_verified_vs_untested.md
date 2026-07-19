---
name: feedback_not_verified_vs_untested
description: 「我沒驗證到」≠「這件事沒發生」——回報(尤其對外記錄)不可把「我這邊沒看到」寫成「沒做/未驗證」
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2e3aafce-65f5-45a1-8488-7a83a6e73825
---

回報一件事的狀態時，**嚴格區分「我（在這個 session / 用我的工具）沒驗證到」和「這件事客觀上沒發生 / 未被驗證」**。前者是我的可見範圍限制，後者是對世界的斷言 —— 不可混為一談，尤其寫進**對外/共用記錄（JIRA、Slack、PR）**時。

**Why:** 2026-07-16 我在 JIRA FWP-814 comment 92293 寫「on-device verification for Spark LIVE / EDGE is still pending」，語氣像是「LIVE/EDGE 沒實機測過」。但實情是**用戶早就在 branch 上實機測過了，只是我這個 session 只看得到 Reactor 100 + Spark 2**。用戶回「edge live 在 branch 測過了」後我得補 comment 92294 更正。我把「我沒看到」誤述成「還沒做」，在共用記錄上造成不實印象。

**How to apply:**
- 措辭改成歸因到自己的可見範圍：「我在本 session 未驗證 / 這邊硬體看不到」，不要寫成「尚未驗證 / pending / 沒做」。
- 狀態類事實（測過沒、部署了沒、誰做了沒）**先問掌握第一手的人（用戶/tester）**，不要用「我沒看到」當預設值填空。
- 這是 [[feedback_evidence_based]] 的延伸：沒證據時標「待驗證」是對的，但別把「我無證據」升級成「事實為否」。
