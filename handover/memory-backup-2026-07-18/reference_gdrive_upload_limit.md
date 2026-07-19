---
name: reference_gdrive_upload_limit
description: 用 claude.ai Google Drive connector 無法上傳大二進位檔(只收 inline base64);>~140KB 走 Google Doc 轉檔或手動
metadata: 
  node_type: memory
  type: reference
  originSessionId: 530214ed-26de-4bd0-9704-882c8e95dc6f
---

**claude.ai Google Drive connector 的 `mcp__claude_ai_Google_Drive__create_file` 只吃 inline 內容**（`base64Content` / `textContent`），**沒有** file-path / URL / resumable / chunked 上傳。

- 一個 ~1MB 的 PDF → base64 ≈ 1.36M 字元 ≈ **>300K tokens**，塞不進單一 tool call（tool 參數來自模型輸出，per-turn 上限只有幾萬 tokens）→ **大二進位檔無法這樣上傳**。粗略天花板 ≈ **140KB 檔 / 190KB base64**。
- 本機**沒有** rclone / gcloud / gdrive CLI / Google OAuth token（`D:\mybot\git\tool\` 只有 `.gitlab-token`、`.jenkins-token`）→ 沒有 file-based 上傳路徑到使用者的 Drive。

**可行做法：**
1. **要放進 Drive**：把內容做成 **Google Doc**——`create_file` 用 `textContent`=HTML、`contentMimeType:"text/html"`、**不要**設 `disableConversionToGoogleType`（預設會把 text/html 轉成 Google Doc）。HTML 是純文字（幾十 KB）塞得進。**Google Docs 匯入會吃掉多數 CSS**（顏色/callout box 掉），但 heading/table/bold/list/blockquote/inline-image(data-URI) 會留 → 寫 Doc 版要用語意標籤、流程圖改文字或縮到很小的 inline 圖。
2. **只要能手機看的連結**：發 claude.ai **Artifact**（HTML 網頁，可內嵌 data-URI 圖），拿私人 URL。但不在 Drive、不是 PDF 檔。
3. **一定要 PDF 檔進 Drive**：目前只能使用者**手動拖**本機檔進 Drive。

2026-07-17 實例：`AI隊友-每天怎麼運作與review` 1MB PDF 上傳失敗 → 改建 Google Doc（id `1DZ88K2R1GDOFCUpVmzOdfIecicyQAPc5HeVwY-8ugkE`）成功。委派 subagent 做 base64/大字串上傳可把大 payload 留在 subagent context、不炸主 context。相關 [[feedback_verify_urls_before_sending]]。
