# Session Handoff Protocol (Auto)

> Context Window = RAM, Filesystem = Disk, JIRA = per-task, GitHub = full session log
> Repo: https://github.com/alicechanpg/fw-multi-agent

## Terminal Map

讀取 `D:\mybot\handover\terminal-map.json` 取得 terminal 對應的 JIRA ticket 和 latest 檔名。

## Session 開始時（自動）

### Step 1: 從 GitHub 拉最新 handover
```bash
cd D:\mybot\fw-multi-agent && git pull
```

### Step 2: 列出所有可 restore 的 session
掃描 `D:\mybot\fw-multi-agent\handover\latest-*.md`，呈現選單：
```
📋 可 restore 的 session：
1. reactor-fw (2026-03-24 12:00) — RAD-966 等 Teo merge
2. esp32 (2026-03-23 18:30) — WiFi reconnect 測試中
3. mybot (2026-03-24 11:00) — FWP-731 research
0. 跳過，開始新工作

要 restore 哪個？
```

### Step 3: 用戶選擇後
- 讀取該 `latest-{id}.md` 的完整內容
- 讀取對應的 JIRA ticket（從 terminal-map.json 查）最新 comment
- 如果有 `handover/checklist/` 下相關的 checklist，也讀取
- 回報摘要：上次做到哪、未完成的事、建議這次從哪開始

### 如果只有一個 session
直接問「要 restore reactor-fw 的 session 嗎？」不用列選單。

### 如果沒有任何 session
跳過，正常開始。

## Session 進行中（自動）

每完成一個 **重要動作**（commit, push, MR, JIRA 更新, build, flash）時：
- 更新本地 `D:\mybot\handover\latest-{terminal-id}.md` 的對應項目
- 即使突然斷線也不會丟失狀態

## Session 結束時（自動）

當用戶說「交班」「handover」「重開機」「結束」「下班」或任何暗示 session 結束的話時：

### Step 1: 寫 session 日誌到本地
```
D:\mybot\handover\sessions\{terminal-id}\YYYY-MM-DD-HHmm.md
D:\mybot\handover\latest-{terminal-id}.md
```

### Step 2: Push 到 GitHub
```bash
cd D:\mybot\fw-multi-agent
cp -r D:\mybot\handover\sessions\ handover\sessions\
cp D:\mybot\handover\latest-*.md handover\
cp D:\mybot\handover\terminal-map.json handover\
git add handover/
git commit -m "session({terminal-id}): YYYY-MM-DD HHmm handover"
git push
```

### Step 3: 更新 JIRA
查 terminal-map.json 找到對應的 JIRA ticket，加 comment：
```
🤖 Session Handover ({terminal-id}) — YYYY-MM-DD HH:mm

Done:
- [本次完成的事]

Next:
- [下一步]

Env: branch={branch}, hw={relay on/off}
```

同時，對每個本次有動到的**其他** JIRA ticket（如 RAD-966），也加簡短 comment。

## 交班日誌格式

```markdown
# Session Handover ({terminal-id}) — YYYY-MM-DD HH:mm

## 本次完成
- [每項一行]

## 未完成 / 進行中
| 項目 | 狀態 | 下一步 |
|------|------|--------|

## 環境狀態
- 當前 branch: ...
- 硬體狀態: ...

## 給下個 session 的備註
[任何需要注意的事]
```

## Feature Checklist（大型任務用）

`D:\mybot\handover\checklist\{JIRA-ID}.json`:
```json
{
  "task": "FWP-XXX: description",
  "created": "2026-03-24",
  "terminal": "reactor-fw",
  "steps": [
    {"id": 1, "desc": "步驟描述", "done": false},
    {"id": 2, "desc": "步驟描述", "done": true}
  ],
  "current_step": 1
}
```

## 多 Terminal 注意事項
- 每個 terminal 只更新自己的 `latest-{id}.md`
- Git push 前先 pull（避免多 terminal 同時 push conflict）
- JIRA comment 標註 terminal ID
- 同一個 JIRA ticket 可能被多個 terminal 更新

## 原則
1. 每個 session 結束時 code 必須是「可 merge」狀態
2. 不依賴 context window — 重要資訊都寫磁碟
3. JIRA comment 簡短，GitHub 完整
4. 每個 terminal 獨立，不互相干擾
5. 開機先 git pull，關機先 git push — GitHub 是 source of truth
