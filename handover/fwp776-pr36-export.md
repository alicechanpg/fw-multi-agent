# PR #36 — FWP-776: Reactor HW adapter -- data-driven refactor + E2E

**Repo**: Positive-LLC/pg-fw-dev-agent  
**Base**: main  
**Head**: pg-fw-dev-alice  
**Author**: alicechanpg  
**State**: closed  
**Created**: 2026-04-23T04:53:44Z  
**URL**: https://github.com/Positive-LLC/pg-fw-dev-agent/pull/36

## PR Description (body)

## Summary
FWP-776 Reactor HW adapter refactor, **all 6 gates green**. Narrow scope per directive (Reactor only; spark2/mini2/LIVE HW-block deferred — but dispatcher no-regression for them is verified via G6).

## What this PR does
1. **Step 2 (A) data** — `projects/reactor/build-config.yaml`: top-level `hw:`/`build:`/`flash:` blocks per your YAML spec.
2. **Step 2 (B) dispatcher** — `scripts/flash_cli.sh` now consumes `hw:` block and enforces G2 pre-flash voltage gate + G4 post-flash power cycle automatically. Three-state voltage parsing (voltage / `No STM32 target` → 0 / UNKNOWN → fail) per cheat-sheet rehearsal. `-d BIN ADDR` for XIP products (Reactor 0x90000000), `-w ELF` fallback for flash-resident.
3. **Step 2 (C) shell vs hw-adapter/** — went with inline shell in `flash_cli.sh` + `powershell -File $USB_RELAY_PS1` via `hw.relay.script_env`. Per Rule of three, defer `scripts/hw-adapter/` abstraction until a second product (Mini 2 DFU, Spark LIVE) arrives. Ping for toggle.
4. **Commands cleanup** — `.claude/commands/fw-flash.md`: 3 Reactor-specific procedural lines removed; replaced with product-agnostic pointers.
5. **Pre-existing dispatcher bugs found & fixed** (surfaced by executing G1):
   - `build-config.yaml` `build_dir` flat-layout mismatch — commit **9ee92d1**
   - `scripts/build_cli.sh` missing explicit `all` (Reactor Makefile sets `.DEFAULT_GOAL := clean`) — commit **63e1d43**
   - `scripts/build_cli.sh` Git Bash glob not expanding → winget 10.3 picked instead of CubeIDE 12.3 — commit **45ee1ae**

## Gate results (live Reactor HW, Alice machine, 2026-04-23)

| Gate | Action | Result |
|------|--------|--------|
| **G1 Build** | `./scripts/build_cli.sh --product reactor` | Exit 0, 70s, `reactor-fw_Appli.bin` 1,287,224 bytes (1.23 MB), STM32H7R3xx toolchain 12.3.rel1 |
| **G2 Voltage pre-flash** | dispatcher auto from `hw:` block | `V_PRE = 3.28V` (gate ≥ 3.1V) **PASS** |
| **G3 Flash** | `./scripts/flash_cli.sh --product reactor` | Path B ST-Link + `reactor-fw_ExtMemLoader.stldr`, download 22.8s, verify `Download verified successfully` |
| **G4 Power cycle** | dispatcher auto from `hw.power_cycle` | `V_OFF=0.0V` (three-state: "No STM32 target" → symbolic 0) → `V_ON=3.28V` **PASS** |
| **G5 Command agnosticism** | `grep -iE "reactor\|usb relay\|com3\|stldr\|dfu" commands` | 0 Reactor-specific procedural hardcode. Remaining hits: 2× product-list comments (`spark2 \| mini2 \| reactor`), 1× generic `Step R1: Enter Debug/DFU Mode` header, 3× spark2/LIVE hardcode (out-of-scope per narrow directive). **PASS (narrow)** |
| **G6 No regression** | `SPARK2_FW_PATH=D:/mybot/git/spark-ii-fw ./scripts/build_cli.sh --product spark2 --clean` | Exit 0, **64s (real clean rebuild, all TUs compiled)**, `spark-ii-fw.elf` 8,399,244 bytes freshly produced, toolchain GNU Tools for STM32 12.3 (same as Reactor; spark2 Makefile also requires `-fcyclomatic-complexity`). No-`hw:`-block branches short-circuit relay/voltage logic. **PASS (no regression)** |

## Prior HW baseline
Reactor 50 live HW rehearsal 2026-04-22 (ref [comment 87200](https://positivegrid.atlassian.net/browse/FWP-776), flash 23.4s + 3.28V post-cycle). This PR's dispatcher now produces the same pass behavior automatically from `hw:` block — no operator intervention needed.

## Demo 2026-04-24
Cheat sheet (`D:/mybot/handover/demo-cheat-sheet-fwp776.md`) Part 1/2 [ACTION] use direct PowerShell wrapper (`build-stm32.ps1` + `STM32_Programmer_CLI`) to match rehearsal muscle memory. `/fw-build` `/fw-flash` slash commands (post-rebase generic dispatcher) are **also working** after this PR, but the cheat sheet sticks with the rehearsed path to avoid demo-day reshuffle.

## Files
- `projects/reactor/build-config.yaml` (+32 / -1) — `hw:`/`build:`/`flash:` blocks, `build_dir` corrected
- `scripts/flash_cli.sh` (+147 / -7) — `hw:` block consumer, BIN+ADDR for XIP, PGM_CLI glob fix
- `scripts/build_cli.sh` (+28 / -4) — toolchain-preference fix + `all` explicit
- `.claude/commands/fw-flash.md` — 3 Reactor-specific lines removed
- `handover/sessions/2026-04-22-*.md` — session logs (5 new)

Reviewer: Nathan. All gates green; ready for merge.



---

## Reviews (summary-level)

### [COMMENTED] gemini-code-assist[bot] · 2026-04-23T04:55:37Z

## Code Review

This pull request introduces the `mcu-register-lookup` skill for the Reactor project, providing an authoritative STM32H7R3 register reference to prevent agent hallucinations. It also includes a new follow-up backlog, hardware adapter specifications in `build-config.yaml`, and various improvements to build and flash workflows. Feedback was provided regarding a technical inaccuracy in the HardFault decoding hints where `BFAR` is incorrectly suggested for imprecise bus faults, and a concern was raised about hardcoding machine-specific COM ports in shared configuration files.

### [COMMENTED] alicechanpg · 2026-04-23T06:23:46Z



### [COMMENTED] alicechanpg · 2026-04-23T06:23:48Z




---

## Inline code comments (with replies)

### projects/reactor/.claude/skills/mcu-register-lookup/SKILL.md:59 — [gemini-code-assist[bot]] · 2026-04-23T04:55:37Z

![medium](https://www.gstatic.com/codereviewagent/medium-priority.svg)

The hint for `BFSR.IMPRECISERR` suggests verifying the fault address with `BFAR`. However, according to the ARMv7-M Architecture Reference Manual, the `BFAR` register is only valid for precise bus faults (when `BFSR.PRECISERR` is set and `BFSR.BFARVALID` is 1). For imprecise faults, the `BFAR` does not contain the address of the access that caused the fault. This hint should be corrected to avoid misleading debugging efforts.

```suggestion
| BFSR.IMPRECISERR | [10] | Imprecise bus fault | Stale D-Cache on DMA RX / missing invalidate (verify with memory-layout.md) | Cortex-M7 architectural + Reactor heuristic |
```



**Reply — [alicechanpg] · 2026-04-23T06:23:46Z**

Fixed in ba6858c. Kept the core correction (BFAR not valid for imprecise) and added two teaching hooks: the explicit "NOT valid" warning + the `__DSB()` precise-ize technique Reactor team uses in practice. Thanks for catching this — it was real misdirection for agent debugging.




### projects/reactor/build-config.yaml:79 — [gemini-code-assist[bot]] · 2026-04-23T04:55:37Z

![medium](https://www.gstatic.com/codereviewagent/medium-priority.svg)

Hardcoding `port: COM3` in a shared configuration file limits the portability of the build and flash system, as COM port assignments are machine-specific. While other parameters like `script_env` leverage environment variables for local paths, the port remains literal. Consider moving this to a local configuration or providing a mechanism for per-machine overrides.

```yaml
    port: COM3      # Machine-specific; consider moving to local config
```



**Reply — [alicechanpg] · 2026-04-23T06:23:48Z**

Fixed in ba6858c. Added `port_env: RELAY_COM_PORT` with yaml `port: COM3` as Reactor 50 EVB reference default. Dispatcher (`scripts/flash_cli.sh`) resolves env var first, yaml literal fallback with WARN log. Used bash indirect expansion (`${!VAR}`) + regex-validated identifier to avoid eval-based injection.





---

## Issue-level PR comments

### [alicechanpg] · 2026-04-23T06:41:36Z

C:/Program Files/Git/gemini review

### [gemini-code-assist[bot]] · 2026-04-23T06:41:39Z

> [!WARNING]
> You have reached your daily quota limit. Please wait up to 24 hours and I will start processing your requests again!
