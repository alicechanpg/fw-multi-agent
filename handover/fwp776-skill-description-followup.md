# FWP-776 FOLLOWUP-1: reactor-* skill descriptions rewrite

> 給 Alice 印出來慢慢看的白話版

---

## 5 個 reactor-* skill — 白話表

| # | 檔名 | 現在的 description（原文） | 白話 — 這個 skill 是幫 Agent 理解什麼？ |
|---|---|---|---|
| 1 | `reactor-build` | Reactor STM32H7R3 build system — STM32CubeIDE, CLI build, toolchain, linker, post-CubeMX patches | 怎麼 **build** Reactor firmware（用 CubeIDE、命令列、toolchain 設定、linker、CubeMX 之後手改的 patch） |
| 2 | `reactor-debug` | Reactor debug & crash analysis — HardFault, watchdog, stack overflow, UART, OpenOCD, factory tests | 怎麼 **debug** Reactor 當機 / 崩潰（HardFault、watchdog、stack 溢位、UART log、OpenOCD、工廠測試） |
| 3 | `reactor-dsp` | Reactor audio/DSP pipeline — signal chain, 100+ FX modules, preset format, real-time protections | Reactor 的 **音訊 / DSP** 架構（訊號鏈、100+ 音效模組、preset 格式、即時保護） |
| 4 | `reactor-hardware` | Reactor STM32H7R3 peripherals — SAI, SPI, I2C, SDMMC, DMA, MPU, cache configuration | Reactor MCU 的 **周邊硬體**（SAI 音訊、SPI、I2C、SD 卡、DMA、MPU、快取設定） |
| 5 | `reactor-rtos` | Reactor FreeRTOS architecture — 24 tasks, mutexes, queues, heap management, stack safety | Reactor 的 **FreeRTOS 架構**（24 個 task、mutex、queue、heap 管理、stack 安全） |

---

## 為什麼要 rewrite —— 共通的毛病

**這 5 個 description 全部在寫「skill 裡有什麼東西」，但 Agent 需要的是「什麼時候該用我」。**

| ❌ 現況（功能列表式） | ✅ 理想（觸發條件式） |
|---|---|
| `STM32CubeIDE, CLI build, toolchain, linker, post-CubeMX patches` | `Use when building Reactor firmware, debugging build errors, or modifying toolchain/linker config.` |
| Agent 看：「這個 skill 裡有一堆東西」（但不知道什麼時候觸發） | Agent 看：「user 在 build → trigger 這個」（明確） |

---

## 具體後果

| 問題 | 實際發生什麼 |
|---|---|
| 描述太 vague，沒講觸發條件 | 該 trigger 沒 trigger（user 問 linker 錯誤，Agent 不知道 reactor-build 有寫） |
| 詞彙重疊（build 跟 hardware 都提到「STM32H7R3」、「toolchain」）| Agent 搞不清楚用哪個 |
| 沒說「不該用的情境」 | Agent 在不該用時也 trigger，造成 noise |

---

## FOLLOWUP-1 要做的事

把這 5 張標籤從**功能列表** → 改成**觸發條件**，像：

**改前：**
```
reactor-build: STM32CubeIDE, CLI build, toolchain, linker, post-CubeMX patches
```

**改後：**
```
reactor-build: Use when building Reactor firmware, resolving build errors,
modifying toolchain or linker config, or integrating post-CubeMX hand-patches.
Do NOT use for hardware peripheral config (use reactor-hardware) or
RTOS task debugging (use reactor-rtos).
```

這樣 Agent 讀了就知道何時該 trigger、何時不該。

然後順便整理成「skill description 撰寫指南」，未來 Spark 2 寫 skill 都照這個標準。

---

## Skill / Adapter 是什麼（再複習）

### Skill
- = Agent 可以呼叫的「**專業知識包**」
- 每個 skill 有一個 `SKILL.md`（使用說明 + 觸發條件）
- **Description** = 標籤，告訴 Agent「**什麼時候該用我**」

### Adapter
- **Platform**（`pg-agent-dev`）= **通用遙控器**（Calvin 造的）
- **Product**（Reactor）= **特定廠牌的電視**
- **Adapter** = **讓通用遙控器能操作這台電視的轉接頭**（你寫的）

### FWP-776 的 3 個 FOLLOWUP
- **FOLLOWUP-1** = 修 5 個 skill 的標籤（功能列表 → 觸發條件）
- **FOLLOWUP-2** = 修 Agent 切 product 時認錯工具箱的 bug
- **FOLLOWUP-3** = 把 Reactor adapter 從一塊大餅拆成一層一層

---

## 如果有人問，白話應對

| 誰問 | 怎麼答 |
|---|---|
| **同事隨口問** | 「三個技術債清理，demo 裡抓到的：1. skill 說明不夠準要改 2. loader 切 product 有 bug 3. adapter 寫得太糾結要拆乾淨」 |
| **Nathan 問 own 嗎** | 「我 propose 我來 own，scope/時程先對一下。FOLLOWUP-2 先跟你跟 Calvin align 方向再動」 |
| **Calvin 問 impact** | 「F1 降低 Agent mis-trigger；F2 解 cross-product 污染；F3 是 adapter 內部 tech debt」 |
| **Teo 問為什麼提** | 「都是 FWP-776 demo 時自己 surface 的技術債，不想留坑給後面」 |
| **Teo 問為什麼你 own** | 「demo 我交付過，pattern 在腦袋裡最清楚，但 ownership 怎麼分 scope/時程可以跟你對」 |
| **有人問 F3 為什麼不讓 Spark 2 reuse** | 「Spark 2 是 Nathan own，他知道 Spark 2 pattern。我先把 Reactor 自己拆乾淨，reuse 的事讓 Nathan 決定」 |

---

## 底線記住三句

1. 「**技術債清理**」—— 把所有 FOLLOWUP 都 frame 成這個
2. 「**scope / 時程可以對一下**」—— 留空間給別人決定
3. 「**不主動 claim Spark 2 / 其他 product**」—— 這是 Teo 最敏感的線
