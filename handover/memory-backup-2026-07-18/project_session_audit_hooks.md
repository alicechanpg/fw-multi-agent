---
name: project_session_audit_hooks
description: Session audit 由 hooks 自動記錄（不靠 Claude 記得）— audit-log.py + session-digest.py + Stop hook asyncRewake 補寫 handover
metadata:
  node_type: memory
  type: project
  originSessionId: 2e3aafce-65f5-45a1-8488-7a83a6e73825
---

2026-07-16 建立：session 全程記錄改由 **hooks（harness 執行）** 保證，不依賴 Claude 記得寫。設定在 `D:\mybot\.claude\settings.local.json`。

## 為什麼要做（真正的失效原因）

舊的 `Stop` hook `session-handoff.sh` **只是把 `latest-mybot.md` 複製**到 archive，它自己不產生內容。Claude 沒寫 → 就複製一份 3 週前的舊檔（2026-06-24），看起來有交班、其實沒有。**hook 沒壞，是設計上依賴 Claude 的記性。**

（另外：harness 本來就會寫完整 transcript 到 `~/.claude/projects/D--mybot/{session_id}.jsonl`，那才是原始不可跳過的紀錄；缺的是「萃取 + 放到可稽核的地方」。）

## 現在的機制

| Hook | 動作 |
|------|------|
| `UserPromptSubmit` | `audit-log.py` → 記 prompt |
| `PostToolUse`（matcher `Bash\|Edit\|Write\|NotebookEdit\|mcp__.*`）| `audit-log.py` → 記 tool + input 摘要 + **ok/失敗** |
| `Stop` | `session-handoff.sh` → `session-digest.py` 產生 `handover/sessions/mybot/{時間}-audit.md` + git push |

- Trail：`D:\mybot\handover\audit\{session_id}.jsonl`（append-only，一行一事件）
- **Stale 偵測**：`latest-mybot.md` 的 mtime 若早於本 session 第一筆 audit → digest **exit 2** → Stop hook 的 **`asyncRewake: true`** 叫醒 Claude 補寫。寫完 mtime 變新 → 下次 Stop 靜默通過（會收斂，不會無限迴圈）。

## 踩過的雷（改這些腳本時注意）

- **Windows stdin 預設 cp950** → `sys.stdin.read()` 遇到中文 prompt 會 UnicodeDecodeError，被 `except: pass` 吞掉、**整筆靜默消失**。必須用 `sys.stdin.buffer.read().decode('utf-8')`。
- **這台沒有 `jq`**（也沒有 host C++ compiler、沒有 qemu）→ hook 用 python 寫，不要抄 jq 範例。
- 測試時 **Git Bash 的 `echo` 會把 `\\` 吃成 `\`**，讓 JSON 變成非法 → 用 `printf '%s'` 餵測試 payload。
- audit script 契約：**永遠 exit 0、永遠不要往 stdout 亂印**（PostToolUse hook 亂印會干擾被稽核的那個 tool call）。digest 例外：stale 時故意 exit 2。

相關：[[feedback_ai_collab_mode]]、[[feedback_evidence_based]]
