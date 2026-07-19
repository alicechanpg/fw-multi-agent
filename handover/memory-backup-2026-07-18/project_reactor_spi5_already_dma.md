---
name: reactor-spi5-already-dma
description: Reactor (H7R3) SPI5 ESP32 命令路徑已是 GPDMA + non-cacheable buffer，Mini2 SPI6 BDMA fix 不需移植（判定 c，2026-07-18 已驗證）
metadata: 
  node_type: memory
  type: project
  originSessionId: 2217eef5-1511-4bc5-ab5c-2ad4cca7a9de
---

**FWP-833 後續調查結論（2026-07-18，已驗證）**：Spark MINI 2 的 SPI6 IT→BDMA fix（spark-mini-ii-fw PR #51 / commit 758640c）**不需要**移植到 Reactor —— Reactor 的 ESP32 SPI 命令路徑本來就是 DMA。

證據（reactor-fw repo）：
- `Appli/Source/Components/SPI_Command_Master.cpp:148` — 活路徑用 `HAL_SPI_TransmitReceive_DMA`；`:187`/`:212` 的 `_IT` 在 `#if 0` 死碼內；全 Source 無其他活的 HAL_SPI 傳輸點
- `Appli/Core/Src/spi.c:120–168` — GPDMA1 CH7=SPI5_TX、CH6=SPI5_RX，`__HAL_LINKDMA` 連 SPI5
- buffer `:18–19` 在 `.dma_buffer` → linker `RAM_NONCACHEABLEBUFFER` 0x24060000（SRAM4 32KB，`STM32H7R3I8TX_ROMxspi1.ld:59,423`）→ `main.c:259–265` MPU Region4 NOT_CACHEABLE，無需 cache maintenance
- 完成通知 `HAL_SPI_TxRxCpltCallback` 只 set event flag，`DMA_TCEM_BLOCK_TRANSFER` 整塊一次中斷

架構差異：H7R3 **沒有 D3 domain**（Mini2/H750 的 SPI6 只有 BDMA 能服務且只能定址 D3 SRAM，才需要 staging buffer）；H7R3 全部 SPI 由 GPDMA 服務。呼應 [[stm32h7r3-vs-stm32h750-isolation]]。

**過時文件**：`reactor-fw/.claude/rules/embedded/stm32-freertos.md` 寫 non-cacheable 區 0x24071C00/1KB — 實際是 0x24060000/32KB，尚未修正（要走 reactor-fw repo 流程）。

**下個產品檢查清單**（spark-ii-fw / spark-pedal-fw 皆 SPI2）：① grep 活的 `HAL_SPI_Transmit*`（排除 #if 0）② buffer section + linker + MPU ③ DMA request mapping + chip domain 限制 ④ 完成回呼非阻塞。
