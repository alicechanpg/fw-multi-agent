# Workload 分布量測 v2（修正 word-boundary bug）

語料：28 session／1120 則真人 prompt

## 總體

- 實體總數 70；跨≥2 session 重現 **45（64%）**；一次性 25
- 提及數中來自「會重現實體」：**2821/2896 = 97.4%**

## 依類別（關鍵：事實 vs 工單）

| 類別 | 實體數 | 跨≥2 session | 重現率 | 提及數 | 可回收提及% |
|---|---|---|---|---|---|
| PID/VID | 21 | 15 | 71% | 175 | 90% |
| COM port | 2 | 0 | 0% | 5 | 0% |
| keyword | 29 | 26 | 90% | 2578 | 99% |
| JIRA ticket | 18 | 4 | 22% | 138 | 76% |

## Top 15 實體（依 session 數）
| 實體 | session 數 | 提及數 |
|---|---|---|
| `keyword:build` | 15 | 281 |
| `keyword:jira` | 14 | 228 |
| `keyword:esp32` | 13 | 211 |
| `keyword:reactor` | 12 | 267 |
| `keyword:branch` | 10 | 147 |
| `keyword:updater` | 10 | 105 |
| `keyword:stm32` | 10 | 35 |
| `keyword:jenkins` | 9 | 154 |
| `keyword:firmware` | 9 | 114 |
| `keyword:memory` | 8 | 40 |
| `keyword:dfu` | 7 | 194 |
| `keyword:cdc` | 7 | 119 |
| `keyword:ble` | 7 | 115 |
| `keyword:github` | 7 | 56 |
| `keyword:flash` | 7 | 35 |

## JIRA ticket 重現情形（問題是不是 long-tail 的直接證據）
| ticket | session 數 |
|---|---|
| `FWP-814` | 6 |
| `RAD-1476` | 4 |
| `RAD-1393` | 3 |
| `FWP-739` | 3 |
| `FWPP-814` | 1 |
| `FWP-722` | 1 |
| `CDP-32` | 1 |
| `FWP-764` | 1 |
| `BV-01` | 1 |
| `BV-08` | 1 |