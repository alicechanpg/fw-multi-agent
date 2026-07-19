---
name: Windows bash paths must use forward slashes
description: In bash commands and shell scripts on Windows, always use forward slashes (D:/mybot/) not backslashes (D:\mybot\)
type: feedback
---

在 bash 指令、shell script、command 定義檔的 bash code block 裡，路徑一律用 forward slash `/`。

**Why:** 2026-03-24 用戶在新 session 跑 /restore 時，`cd D:\mybot\fw-multi-agent` 被 bash 解讀為 `D:mybotfw-multi-agent`（反斜線被吃掉），導致 No such file or directory。

**How to apply:**
- 所有 bash 指令：`D:/mybot/` 不是 `D:\mybot\`
- command .md 裡的 bash code block：用 `/`
- shell script (.sh)：用 `/`
- Read/Write/Edit 等 Claude 工具的 file_path 參數：反斜線 OK（那是 Claude 內部處理）
- 只有 bash 執行環境需要 forward slash
