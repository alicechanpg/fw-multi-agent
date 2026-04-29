# Session Handover (mybot) — 2026-04-02 13:30

## Done
- **FWP-698 Bypass CAB SIM — 完成**
  - Code 實作：double tap encoder toggle, peach LED, 持久化, preset 隔離
  - Ziv push 了 LED/click 修正 + 新 DSP lib（2 commits on branch）
  - Pull Ziv 的更新，GCC 10.3 build 成功
  - 發現 external loader 問題：必須用 `W25Q32JV_STM32H750.stldr`（不是 QSPI_H750XB_W25Q32_flashloader.stldr）
  - 實機測試全部通過：bypass toggle、LED peach、聲音變化、preset 不受影響
  - Peach LED 調色：120,45,25 → 85,12,12（減少偏白/黃）
  - DSP team + SW PM 確認聲音 OK
  - Preset 隔離分析完成（code review 確認 BLE 傳 preset 是讀 file 不是 live dump）
  - JIRA 更新完成，等 Ziv merge
- **Bootloader 修復**
  - 昨天 `-e all` 擦掉 bootloader，今天用 Jenkins 版本燒回
  - 確認 bootloader 正常（Jump to APP code）
- **External loader 根因**
  - `QSPI_H750XB_W25Q32_flashloader.stldr` 寫入後 app HardFault
  - `W25Q32JV_STM32H750.stldr` 才是正確的 loader
  - 已更新 JIRA 和 handover 記錄

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| FWP-698 MR merge | 等 Ziv | Ziv merge branch 到 develop |
| Peach LED 最終確認 | 85,12,12 測試中 | PM 最終確認顏色 |
| FWP-749 Mac 環境 | Plan 已寫 | 等拿到 Mac |
| Jenkins token | 過期，無 admin 權限 | 找 Teo/Ziv 幫忙 |

## Environment
- spark-pedal-fw: `feature/FWP-698-bypass-cab-sim` @ 248a6d1 (Ziv's latest)
- 本機未 commit 的改動：user_config.h (APP_DEBUG), AudioService.cpp (ASV_DEBUG), LedService.h (peach 85,12,12)
- Internal flash: Jenkins bootloader (spark-pedal-external-loader.bin)
- External flash: FWP-698 debug build (GCC 10.3)
- spark-pedal-external-loader: develop @ 9e34cdc (已 clone + build)
- Hardware: Spark Pedal 已接 ST-Link V3, COM50 @ 921600

## Notes for next session
### ST-Link Flash 正確指令
```bash
# 正確的 external loader（重要！）
STM32_Programmer_CLI -c port=SWD -el W25Q32JV_STM32H750.stldr -d spark-pedal-fw.bin 0x90000000 -rst

# 不要用這個（會 HardFault）！
# STM32_Programmer_CLI -c port=SWD -el QSPI_H750XB_W25Q32_flashloader.stldr ...

# 不要用 -e all（會擦掉 bootloader）！
```

### Build 流程（本機）
1. CubeIDE 1.16.1 headless 產生 Makefile（.cproject 需改成 12.3）
2. `find . -name "*.mk" -exec sed -i 's/ -fcyclomatic-complexity//g' {} \;`
3. GCC 10.3: `export PATH="/c/ST/gcc-arm-none-eabi-10.3-2021.10/bin:$PATH"`
4. `make -j8 all`

### Ziv Slack 訊息重點
- branch 更新到最新就可以測試
- 需要確認：1) cab bypass 聲音 OK? 2) 會不會影響 preset?
- 兩個都已確認 OK
- DSP owner: Jason

### 群組 DM
- Channel: C0AQ3S8S4DU（Alice + Ziv + Teo）
