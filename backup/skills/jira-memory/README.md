# JIRA Memory Skill

Agent 開發/分析任務前，先搜 JIRA 取得歷史知識。

## 使用時機

**每個 agent 在開始任務前都應該搜 JIRA：**
- PM：分析需求前，搜相關歷史 issue
- RD：開發/debug 前，搜相關 root cause 和 solution
- QA：寫 TC 前，搜相關測試失敗歷史

## 搜尋規則

1. **限定 FWP 專案**：所有搜尋都加 `project = FWP`
2. **用關鍵字搜尋**：根據任務內容提取關鍵字
3. **結果精簡**：只看 summary + status + labels + 最新 comment
4. **沒找到就跳過**：不要卡在搜尋上，找不到就直接開工

## 搜尋方式

使用 `mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql` 工具：

```
cloudId: positivegrid.atlassian.net
jql: project = FWP AND text ~ "關鍵字" ORDER BY updated DESC
maxResults: 5
```

### 關鍵字提取規則

從任務描述中提取：
- **模組名稱**：SPI, WiFi, Bluetooth, OTA, MIDI, DSP, ADC, PWM
- **功能名稱**：Expression Pedal, Tuner, Effect Loop, Looper
- **錯誤類型**：timeout, crash, fail, error, retry
- **晶片相關**：ESP32, STM32, dual-chip

### 搜尋範例

| 任務 | JQL |
|------|-----|
| Debug SPI 問題 | `project = FWP AND text ~ "SPI" ORDER BY updated DESC` |
| 實作 BT 功能 | `project = FWP AND text ~ "bluetooth" ORDER BY updated DESC` |
| OTA 相關 | `project = FWP AND text ~ "OTA" ORDER BY updated DESC` |
| 特定 issue | `project = FWP AND key = FWP-XXX` |

### 進階搜尋（有標籤時）

```
project = FWP AND labels = "ai-root-cause" AND text ~ "SPI"
project = FWP AND labels = "ai-verified" AND text ~ "bluetooth"
```

## 搜尋後行動

1. **有相關歷史** → 摘要列出，作為開發/分析的參考
2. **沒有相關歷史** → 直接開始任務
3. **任務完成後** → 建議加標籤和 comment 回寫（optional）

## 回寫 JIRA（任務完成後）

使用 `mcp__claude_ai_Atlassian__addCommentToJiraIssue` 回寫：

```
cloudId: positivegrid.atlassian.net
issueIdOrKey: FWP-XXX
commentBody: |
  ## AI 開發記錄
  - **任務**: [描述]
  - **Root Cause**: [如果是 debug]
  - **Solution**: [解決方案]
  - **相關檔案**: [修改的檔案]
```
