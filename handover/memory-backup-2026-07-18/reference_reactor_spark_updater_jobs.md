---
name: reference_reactor_spark_updater_jobs
description: "Jenkins updater jobs — REACTOR_SPARK_FW_UPDATER_* (unified all) vs REACTOR_FW_UPDATER_* (reactor-only), and their version params"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5103f5c6-c8c2-43fd-89b9-2e0d0c162bd0
---

Two separate ReactorFwUpdater Jenkins job families — don't confuse them:

- **`REACTOR_SPARK_FW_UPDATER_WIN_OSX`** — the **unified Reactor+Spark** build (`PRODUCT=all`, window title "Reactor Spark Firmware Updater", bundles R50/R100 + Spark 2/LIVE/EDGE). Triggers `REACTOR_SPARK_FW_UPDATER_OSX` for Mac when `TRIGGER_OSX=true`. **This is the job for the FWP-814 unified updater.**
- **`REACTOR_FW_UPDATER_WIN_OSX`** — older **reactor-only** (`PRODUCT=reactor`, "Reactor Firmware Updater", R50+R100 only, no Spark). Its BRANCH Choice list does NOT include `feature/FWP-814-audio-anchor`. (I mis-picked this one first — the Spark unified work needs the `_SPARK_` job.)

`PRODUCT` is hardcoded in each job's script (not a build param).

### REACTOR_SPARK_FW_UPDATER_WIN_OSX params (after 2026-07-13 change)
`BRANCH` (Choice; includes `feature/FWP-814-audio-anchor`, the default), `MCU_VERSION`, `ESP_VERSION` (Reactor R50/R100 shared), `SPARK2_MCU`, `SPARK2_ESP`, `SPARKLIVE_MCU`, `SPARKLIVE_ESP`, `SPARKEDGE_MCU`, `SPARKEDGE_ESP`, `SIGN` (default true; false for verification builds), `TRIGGER_OSX` (default true). The `_OSX` job mirrors these (minus SIGN/TRIGGER_OSX, plus NOTARIZE/TRIGGERED_BY_WIN).

- **All version fields default BLANK. Blank = resolve to the latest build of that firmware job** (`resolve_build` picks the newest artifact whose filename matches the pattern; empty version → matches any → newest).
- WIN forwards the 6 Spark version values to the OSX job via its OSX-trigger curl, so Win/Mac bundle the same versions.
- Build description reads the **actually-resolved** versions from the downloaded artifact filenames (so blank fields still show real versions, not blank).
- Latest bundled versions as of 2026-07-13: Reactor R50/R100 = MCU 0.1.4.171 / ESP rev686; Spark2 = 2.7.2.200 / rev490; SparkLIVE = 2.9.4.209 / rev498; SparkEDGE = 2.10.1.86 / rev498. These match PositiveGrid's official public firmware versions.

See also [[reference_jenkins_speaker_fw_tool]], [[project_fwp814_spark_integration]], [[project_fwp744_reactor_updater]].
