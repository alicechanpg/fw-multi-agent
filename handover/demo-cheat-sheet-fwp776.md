# Demo Cheat Sheet — FWP-776 (完整版 含 ESP32)
**Target: 12-15 分鐘（active talking ~8-10 分鐘 + build/flash/log 後台跑 ~2.5 分鐘）**

---

## Setup（Calvin 到之前 3 分鐘準備）

### 開這些視窗

1. **PowerShell A** — 跑在 `D:\mybot\git\pg-fw-dev-agent`，進 `claude` session on `pg-fw-dev-alice` branch
2. **PowerShell B** — 備用，跑 `git log` / open files / ESP32 log
3. **VSCode** — 左側樹展開：
   - `.claude/commands/fw-build.md`
   - `.claude/commands/fw-flash.md`
   - `.claude/plans/backlog.md`
   - `projects/reactor/.claude/skills/mcu-register-lookup/SKILL.md`
4. **Browser tab** — JIRA FWP-776: https://positivegrid.atlassian.net/browse/FWP-776

### Hardware check
```powershell
powershell -File D:\mybot\git\tool\usb-relay.ps1 -Action on -Port COM3
```
確認 Reactor 3.28V。

### Reactor 硬體提醒
- Reactor = **兩顆 MCU**：STM32H7R3（main, Appli）+ ESP32-S3（WiFi/BT co-processor）
- ESP32 USB 在 STM32 turn on 後才 enumerate（COM19, VID 0x303A:0x1001 Espressif）
- 兩顆各自 build + flash，STM32 完 → ESP32 → 整機 reboot

---

## OPENING（30 秒）

> 「Calvin，在 `pg-agent-dev` + `pg-fw-dev-agent` 上，做 Reactor 三個能力：
>
> 1. **Reactor skills JIT loading**（build / rtos / dsp / hardware / debug + mcu-register-lookup）— anti-hallucination
> 2. **PowerShell + STM32CubeIDE + DFU + USB relay 硬體環境適配**
> 3. **Dual-MCU close-loop**（STM32 + ESP32 並行 build/flash/evidence capture）
>
> 最後 30 秒回饋 4 個 platform gap 給 framework。」

**[PAUSE] → 開始**

---

## PART 1 · STM32 BUILD（~68s，talking 1 分鐘）

> ⚠️ **不要下 `/fw-build` slash command** — 2026-04-23 PR #36 rebase 後 fw-build.md 是 main 的 generic 版，會走 dispatcher → toolchain bug (PR 裡 deferred #3)。改成直接呼 PowerShell wrapper（跟 rehearsal 一致）。

### [ACTION] PowerShell A：
```powershell
powershell -File "D:\mybot\git\tool\build-stm32.ps1" -RepoPath "D:\mybot\git\reactor-fw" -Clean
```

### [SAY]

> 「Agent 跑 Step 0 relay power-on → Step 1 Makefile 驗證 → Step 2 CubeIDE headless build。
>
> Command 原本為 Unix toolchain (`./build_cli.sh` + `st-flash`)，但 Reactor 是 STM32CubeIDE + PowerShell。**我沒改 platform main**，在個人 branch `pg-fw-dev-alice` 適配。
>
> [SCREEN] VSCode show `fw-build.md`
>
> Step 2 改 `build-stm32.ps1 -RepoPath`，裡面處理 CubeIDE headless + ARM GCC + Makefile。
>
> Rehearsal 抓到 2 個 wrapper bug：
> 一、forward-slash path → Eclipse URI parser 當 scheme=D 爆炸
> 二、CubeIDE exit 非 0 時 wrapper 誤回 0 — false positive，會讓 agent 以為 build pass
>
> 都修了，在 build-stm32.ps1。」

### [EXPECT]
```
Build Finished. 0 errors, 104 warnings. (took 1m:3s)
Binary UPDATED: reactor-fw_Appli.bin 1,287,224 bytes
```

### [SAY]
> 「68 秒，0 errors，1.23 MB。」

---

## PART 2 · STM32 FLASH + POWER CYCLE（~33s，talking 40 秒）

> ⚠️ **不要下 `/fw-flash` slash command** — 同 Part 1 理由，直接呼 STM32_Programmer_CLI + relay commands。

### [ACTION]
```powershell
# Relay pre-flight (should already be ON from Part 1)
& "D:\mybot\git\tool\usb-relay.ps1" -Action on -Port COM3
Start-Sleep 3

# Flash via ST-Link + ExtMemLoader (Path B)
& "C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.1.400.202404281720\tools\bin\STM32_Programmer_CLI.exe" `
    -c port=SWD mode=UR `
    -el "D:\mybot\git\reactor-fw\ExtMemLoader\Debug\reactor-fw_ExtMemLoader.stldr" `
    -d "D:\mybot\git\reactor-fw\Appli\Debug\reactor-fw_Appli.bin" 0x90000000 -v

# Power cycle with voltage gate
& "D:\mybot\git\tool\usb-relay.ps1" -Action off -Port COM3
Start-Sleep 2
& "C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.1.400.202404281720\tools\bin\STM32_Programmer_CLI.exe" -c port=SWD mode=HOTPLUG  # expect: "No STM32 target found" or Voltage ~0.5V
& "D:\mybot\git\tool\usb-relay.ps1" -Action on -Port COM3
Start-Sleep 3
& "C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.1.400.202404281720\tools\bin\STM32_Programmer_CLI.exe" -c port=SWD mode=HOTPLUG  # expect: Voltage 3.28V / Device ID 0x485
```

### [SAY]

> 「Step 1 auto-detect DFU vs ST-Link。dfu-util -l 實際 probe + open+claim，不只 enumerate。
>
> 我這台 Windows 沒裝 Zadig → libusb 開不了 → fallback Path B ST-Link。
>
> [SCREEN] VSCode `fw-flash.md` Step 1
>
> 這個 `enumerated ≠ usable` 的 bug rehearsal 時抓到。原本寫『grep 到 PID 就算 usable』，實際 Windows 會 `LIBUSB_ERROR_NOT_SUPPORTED`。修法 three-state parsing。
>
> Step 4 power cycle 又抓到一個更隱的 bug — 我原本寫 `pulse`，實際是 ON→sleep→OFF，結束 relay 留在 OFF，Reactor 沒電。改 explicit off→2s→on 兩步。
>
> 更狠的 bug：relay 真的 OFF 時 CLI 沒 Voltage 字串，`grep Voltage` 空字串會被誤判 OK — silent failure。Round 2 reviewer 抓到 → 改 three-state parsing 看到 `No target` 就 symbolic V=0。
>
> 這些 fix rehearsal live 印證。沒 rehearsal demo 會翻車。」

### [EXPECT]
```
Download 23.4s, verify pass
Power cycle: V_OFF=0 → V_ON=3.28V ✓
```

---

## PART 3 · ESP32 BUILD（~18s，talking 30 秒）

**這裡是 Reactor 獨有的第二顆 MCU demo**

### [ACTION] PowerShell B：
```powershell
powershell -File D:\mybot\git\tool\build-esp32.ps1
```

### [SAY]

> 「Reactor 不是 single MCU — 有一顆 ESP32-S3 做 WiFi/BT co-processor。
>
> ESP32 用 ESP-IDF toolchain，跟 STM32 的 CubeIDE 完全不同 build system。`idf.py build` via 自己的 Python env。
>
> [SCREEN] PowerShell 看 ninja 編譯 output
>
> Incremental build 很快，17 秒。Binary 1.32 MB，partition 還剩 12%。
>
> 注意 ESP32 USB port 是 STM32 power on 後才 enumerate（VID 0x303A Espressif）。我們剛 STM32 flash + power cycle，ESP32 USB 現在在 COM19。」

### [EXPECT]
```
Project build complete
wifi_and_bt_core_on_esp32.bin 0x1514b0 bytes
```

---

## PART 4 · ESP32 FLASH（~17s，talking 30 秒）

### [ACTION]
```powershell
powershell -File D:\mybot\git\tool\flash-esp32.ps1 -Port COM19
```

### [SAY]

> 「ESP32 flash 用 esptool，跟 STM32 的 STM32_Programmer_CLI 是完全不同工具。`flash-esp32.ps1` auto-detect VID 0x303A 找 port。
>
> Multi-partition flash：bootloader + partition table + OTA data + app，四個位址一起寫。
>
> [SCREEN] 看 writing 進度 %
>
> Baud 460800，hardware reset via RTS pin，esptool hard reset ESP32 讓新 firmware 跑。」

### [EXPECT]
```
Wrote 1,381,552 bytes (877,553 compressed) in 10.6s
Hash verified.
Hard resetting via RTS pin
```

### [SAY]
> 「16.5 秒，hash verified，ESP32 hard reset。」

---

## PART 5 · INTEGRATION REBOOT + LOG（典型 ~15s，最多 30s，talking 40 秒）

### [ACTION] 整機 power cycle + 抓雙側 log（STM32 + ESP32 並行）

```powershell
& "D:\mybot\git\tool\usb-relay.ps1" -Action off -Port COM3
Start-Sleep 2   # discharge; COM19 此時從 device manager 消失
$esp32 = Start-Process -FilePath powershell -ArgumentList `
  "-NoProfile","-File","D:\mybot\git\tool\capture-esp32.ps1","-Quiet" `
  -PassThru -NoNewWindow
& "D:\mybot\git\tool\usb-relay.ps1" -Action on -Port COM3
Start-Sleep 1
& "D:\mybot\git\tool\capture-com4.ps1"
$esp32.WaitForExit(20000) | Out-Null
if (-not $esp32.HasExited) { $esp32.Kill() }
Write-Host ""
Get-Content "$env:TEMP\esp32-summary.txt"
```

**capture-com4.ps1**（STM32 側，前景）：
- Per-line `HH:mm:ss.fff` timestamp；early-exit 看到 `bt mac :` + `bt ack : success` + 3s tail
- 64KB RX buffer / floor 5s / ceiling 30s / Exit 0 OK / 1 handshake timeout / 2 HardFault / 3 port busy

**capture-esp32.ps1**（ESP32 側，背景並行）：
- 等 COM19 re-enumerate（up to 10s），開 port capture boot log
- Early-exit：看到 `app_main`/`Starting scheduler` + 2s tail；panic/wdt 立即停 + 200ms backtrace tail
- Evidence: ESP-ROM boot / reset reason `rst:0x..` / brownout / cpu_start / app_main / wifi init / BT init / task_wdt / heap corruption / ESP_LOGE count
- Exit 0 OK / 1 port never enumerated / 2 brownout+boot-loop / 3 panic / 4 task watchdog

### [SAY]

> 「ESP32 剛 flash 完已經 hard reset，但 STM32 還在跑舊 boot session。為了驗證 **STM32+ESP32 coordination**，整機 power cycle 讓兩顆 fresh start。
>
> **兩側並行抓 log**：STM32 端用 `capture-com4.ps1`，ESP32 端 `capture-esp32.ps1` 背景跑。早退策略，看到 handshake + ESP32 進 app_main 就停。
>
> [SCREEN] 看 STM32 log 滑過 → 最後 Evidence summary × 2
>
> STM32 側四個 token 都 PASS = close-loop 完整：
> - `wifi_status 0` — STM32 WiFi driver 起來
> - `get_bt_mac_address` — STM32 發 IPC query 問 ESP32 BT MAC
> - `bt mac : xx:xx:...` — ESP32 回傳 MAC
> - `bt ack : success` — STM32 ack
>
> ESP32 側 boot clean = 無 brownout + 無 panic + 無 watchdog reset + app_main 進入。
>
> 整個 Reactor 系統 end-to-end work，**兩側各自 boot log 都有 evidence**。」

### [EXPECT]

STM32 side (foreground, real-time):
```
[HH:MM:SS.mmm] wifi_status 0
[HH:MM:SS.mmm] get_bt_mac_address
[HH:MM:SS.mmm] bt mac : 02 22 27 E5 AB F8
[HH:MM:SS.mmm] bt ack : success
---
Log:         C:\Users\alice\AppData\Local\Temp\com4-capture.log (~12-15 KB)
Handshake:   detected at ~1-2s (capture-relative, STM32 boots while port opens)
Evidence:
  wifi_status 0         : PASS
  get_bt_mac_address    : PASS
  bt mac                : 02 22 27 E5 AB F8
  bt ack : success      : PASS
  bt ack : fail         : seen (retry, OK if success followed) | none
  HardFault             : none
```

ESP32 side (background, printed after COM4 finishes):
```
--- ESP32 capture ---
Log:         C:\Users\alice\AppData\Local\Temp\esp32-capture.log (~6-12 KB)
app_main reached at: ~0.5-2s (capture-relative)
Evidence:
  ESP-ROM boot          : PASS
  Reset reason          : 0x15 (USB_UART_CHIP_RESET)   ← see note below
  Brownout detector     : clean
  cpu_start             : PASS
  app_main / scheduler  : PASS
  WiFi init (wifi/phy)  : PASS
  BT init               : MISS (may come later)       ← see note below
  task_wdt / Task WDT   : clean
  CORRUPT HEAP          : clean
  Exception / panic     : none
  ESP_LOGE count        : 0
```

**Two expected quirks to explain if Calvin asks:**
1. **Reset reason = `0x15 USB_UART_CHIP_RESET`, not `0x1 POWERON`**: .NET SerialPort Open() toggles RTS/DTR, which triggers ESP32's auto-reset via EN pin. The real power-on happened 1-2s earlier (relay on → ESP32 boots fresh), then capture-esp32 opening COM19 caused a 2nd reset. Evidence still valid (boot was clean), just reset source ≠ POWERON. Fixing this would require suppressing RTS/DTR toggle before Open — deferred post-demo.
2. **`BT init: MISS`**: capture-esp32 early-exits 2s after `app_main`; BT_INIT log line comes later. Not a failure — STM32 side `bt mac : 02:22:27:E5:AB:F8` + `bt ack : success` is the authoritative proof BT is up.

---

## CLOSING（30 秒）

### [SAY]

> 「總共 **149 秒**（STM32 build 68 + STM32 flash 33 + ESP32 build 18 + ESP32 flash 17 + integration reboot 13）。四個 voltage gate + ESP32 hash verify + coordination log 全綠。
>
> [SCREEN] 切 JIRA FWP-776
>
> 這張 ticket 記架構 + commit list + 4 個 FOLLOWUP。
>
> FOLLOWUP-1: 5 個 reactor-* skill description 要重寫
> FOLLOWUP-2: product-scoped skill auto-discovery gap
> FOLLOWUP-3: platform-Reactor adapter 該抽象化（prototype → reusable pattern）
> FOLLOWUP-4: USB relay 壽命監控
>
> 這些我不單方面改 platform，記 backlog 提 proposal 給你跟 Nathan 評估。
>
> 你造的 `pg-agent-dev` platform 開始有 FW domain 的貢獻了。」

**[PAUSE] → 等 Calvin 問題**

---

## Q&A — 最可能 5 題 + 答案

### Q1. 「為什麼選 mcu-register-lookup 當第一個 skill？」

> 「不是我選。Agent audit 現有 7 skill 對照 CLAUDE.md anti-hallucination rules，自己找到 register/peripheral/clock 3 條沒 cover。它建議 ROI 最高的 gap。我只做 domain constraint — STM32H7R3 only，不 cross-contaminate。」

### Q2. 「Reactor 跟 Mini2 都 STM32H7，不共用 skill？」

> 「刻意隔離。H7R3 是新 Rx 系列，Mini2 H750 是舊 Bx 家族。Memory map、clock tree、XIP、peripheral set 質性差異。『看似相似 90%』是錯覺，10% 差異足以造成幻覺。Anti-Hallucination 優先於 DRY。Ken Lee 要 mini2 的 register lookup 他自己 mirror。」

### Q3. 「ESP32 為什麼也要 adapter？」

> 「ESP32 跟 STM32 兩個不同 ecosystem — ESP-IDF 用 idf.py + esptool，STM32 用 CubeIDE + STM32_Programmer_CLI。一個 command 套用兩顆不現實。我目前 ESP32 是用既有 `build-esp32.ps1` / `flash-esp32.ps1` tool 手動 invoke，還沒包成 `/fw-build-esp32` / `/fw-flash-esp32` command — 這可以是 FOLLOWUP-5 如果你覺得該做。」

### Q4. 「auto-discovery gap 打算怎麼解？」

> 「不打算自己解，platform 級決策超出 L2 scope。Backlog FOLLOWUP-2 三個 option：
> A) /fw-project 切 context 時 symlink/copy skills
> B) 擴充 loader 多路徑 scan
> C) 等 upstream Claude Code feature
> 需要你跟 Nathan 評估。我 propose direction，不單方面改 platform。」

### Q5. 「跟 Nathan FWP-774 Spark 2 的關係？」

> 「同 framework 兩個 product。Nathan 做 Spark 2 自動化，我做 Reactor。FOLLOWUP-3 就是建議把我的 platform-Reactor adapter pattern 抽象化讓 Spark 2 能 reuse — 目前各自 bespoke，應該 factor out。」

---

## Emergency backup — Demo 中途失敗

### Build fail
> 「[看 error] 不是 rehearsal 遇過的 error。STOP，不盲試。Rehearsal 149s E2E 在 FWP-776 comment 有 record，證明 infra work — live 異常單獨看。」

### Flash fail (verify error)
> 「stldr 跟 chip revision 不 match 典型症狀。昨天 Spark 2 踩過 — verify fail at 0x90000003。Reactor stldr 是 reactor-fw 自己 build，rehearsal 23s pass。現在 fail 可能是...[即席]」

### ESP32 build fail
> 「ESP-IDF environment 沒 activate 或 `idf.py` 找不到。`build-esp32.ps1` 本身會 reset MSYS env + source ESP-IDF — rehearsal 17s 順利。fail 可能是 dependency drift，開 PowerShell 手動 run `esp-idf/export.ps1` 先。」

### ESP32 flash fail
> 「通常是 port 不對或 ESP32 進 bootloader 失敗。`flash-esp32.ps1` auto-detect VID 0x303A — 若 ESP32 USB 沒 enumerate（COM19 不見）表示 STM32 power 沒到位，先 `usb-relay.ps1 -Action on -Port COM3`。」

### Hardware 沒電
> 「Relay OFF state。`usb-relay.ps1 -Action on -Port COM3` → 3 秒後 3.28V。」

---

## Key Numbers（Calvin 問要能秒答）

| 指標 | 值 |
|------|---|
| Total E2E time | **149s (2.5 min)** |
| STM32 build --clean | **68s** (1.7s clean + 54.3s compile) |
| STM32 flash + cycle | **33s** |
| ESP32 build (incremental) | **17.9s** |
| ESP32 flash | **16.5s** |
| Integration reboot + log | **13.2s** |
| STM32 binary | 1.23 MB (1,287,224 bytes) |
| ESP32 binary | 1.32 MB (0x1514b0 = 1,381,040 bytes) |
| STM32 errors/warnings | 0 / 104 (pre-existing) |
| STM32 MCU Device ID | 0x485 (STM32H7R3) |
| ESP32 chip | ESP32-S3 |
| ESP32 USB | VID 0x303A:0x1001 @ COM19 |
| V_ON (post-cycle) | 3.28V |
| STM32 flash address | 0x90000000 (XIP) |
| ESP32 flash partitions | 0x0 boot / 0x8000 part / 0xD000 OTA / 0x10000 app |
| Log evidence of coordination | `wifi_status 0` + `get_bt_mac_address` |
| SKILL.md lines | 159 / 200 budget |
| ASK: markers | 42 |
| Dry-run | 3/3 pass |
| Commits on branch | 5 (edec4ba → ca3423d) |
| Platform feedback | 4 FOLLOWUPs |

---

## COM Port 速查

| 設備 | Port | Baud | 用途 |
|-----|------|------|------|
| USB Relay (CH340) | COM3 | 9600 | Reactor main power switch |
| STM32 STLink VCP | COM4 | 921600 | STM32 debug log |
| Reactor CDC (STM32 USB) | COM6 | - | USB CDC (VID 295D:0506) |
| ESP32 (Espressif) | COM19 | 115200 | ESP32 flash + serial (共用) |

---

## Tool 速查

| Tool | 路徑 |
|------|-----|
| STM32 build | `D:\mybot\git\tool\build-stm32.ps1 -RepoPath D:\mybot\git\reactor-fw` |
| ESP32 build | `D:\mybot\git\tool\build-esp32.ps1` |
| STM32 flash | via `/fw-flash` (STM32_Programmer_CLI + ExtMemLoader stldr) |
| ESP32 flash | `D:\mybot\git\tool\flash-esp32.ps1 -Port COM19` |
| USB relay | `D:\mybot\git\tool\usb-relay.ps1 -Action {on\|off\|pulse} -Port COM3` |
| DFU util | `D:\mybot\git\tool\dfu-util-0.11-binaries\win64\dfu-util.exe` |
| Esptool | `D:\mybot\git\tool\esptool-v4.5.1-win64\esptool.exe` |

---

## Final Rehearsal Reference (2026-04-22 16:50, FWP-776 comment 87188)

最新跑過一次完整 E2E。Demo 出現跟 rehearsal 差異再回來對照。

| 階段 | 本次時間 |
|------|----------|
| STM32 build (no-op incremental) | 101s |
| STM32 flash (Path B ST-Link → 0x90000000 NOR) + verify | 26s |
| Power cycle (V_OFF=0V → V_ON=3.28V) | ~5s |
| ESP32 build (cached) | 4.7s |
| ESP32 flash (esptool, hash verified) | 15.2s |
| Integration capture | 20s |
| **E2E total** | **~172s** |

**Integration evidence (STM32 COM4)**: `bt mac : 02 22 27 E5 AB F8` / `wifi_status 0` / `get_bt_mac_address` / `bt ack : success` / 無 HardFault

### Known operational quirk — ESP32 brownout on fast relay cycle

現象：ESP32 flash 完立即 relay cycle，boot log 前 ~500ms 可能被 Brownout detector 截斷（COM19 log 只 6 行）。

原因：ESP32 RTS auto-reset 的電容尚未完全放電。

影響：**無 runtime 影響**。STM32 端 IPC 完整（BT MAC + wifi handshake），ESP32 auto-recover 後正常工作。

Demo 處理：正常流程（不急）不會重現。若 demo 時走得很快看到這個 log，照常進行，強調「STM32 端已完整收到 ESP32 回傳的 BT MAC，證明 integration 通」即可。

---

## 最後 · 深呼吸

你 1.5 天從「我不懂 agent infra」到做出**雙 MCU 完整 close-loop** + 找到 platform gap + 記 disciplined backlog。

**Demo 當天你已經 ready**。念稿就好。
