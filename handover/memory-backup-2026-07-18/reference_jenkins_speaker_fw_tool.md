---
name: Jenkins JAMUP_SPEAKER_FW_TOOL_WIN 參數
description: Spark MINI/GO/40/NEO updater build job 的正確參數和注意事項
type: reference
originSessionId: 96c15cdc-a1a3-4ab9-93a5-dd71363036c3
---
## Jenkins Job: JAMUP_SPEAKER_FW_TOOL_WIN

URL: `https://jk-builds.positivegrid.com/jenkins/job/JAMUP_SPEAKER_FW_TOOL_WIN/`

### 參數

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `BRANCH` | Choice | `master` | Git branch |
| `BUILD_TARGET` | Choice | **`Spark_GO`** | 產品選擇，必須明確指定！ |
| `FORCE_VERSION_NUMBER` | String | (空) | 強制版本號 |

### BUILD_TARGET 選項
- `Spark_GO` (預設)
- `Spark_MINI`
- `Spark_40`
- `Spark_NEO`

### 重要注意事項

1. **BUILD_TARGET 預設是 Spark_GO，不是 Spark_MINI！** 不傳這個參數會 build 錯產品。
2. **參數必須用 POST body 傳**，不能用 query string（ChoiceParameter 不吃 query string）。
3. **signtool cert 已過期**（2026-04 確認），build 會 FAILURE 但 artifact 仍會上傳到 S3。MIS 已被通知。

### 正確觸發方式（PowerShell）

```powershell
$body = @{
    BRANCH = "fix/STFS-491-spark-mini-win25h2"
    BUILD_TARGET = "Spark_MINI"
    FORCE_VERSION_NUMBER = ""
}
Invoke-WebRequest -Uri "$jenkinsUrl/job/JAMUP_SPEAKER_FW_TOOL_WIN/buildWithParameters" `
    -Method POST -Headers $HEADERS -Body $body `
    -MaximumRedirection 5 -AllowInsecureRedirect -SkipHttpErrorCheck
```

### Artifact 下載

上傳到 S3: `https://positivegrid-builds.s3.amazonaws.com/JAMUP_SPEAKER_FW_TOOL_WIN/{buildNo}/artifacts/`
檔名格式: `Spark_MINI_Firmware_Updater_Win-{buildNo}.zip` 或 `Spark_GO_Firmware_Updater_Win.zip`
