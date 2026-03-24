# Session Handoff Protocol

> Context Window = RAM, Filesystem = Disk, JIRA = per-task, GitHub = full session log

## Architecture Diagram

```mermaid
flowchart TD
    subgraph START["Session Start"]
        A[git pull fw-multi-agent] --> B[Scan latest-*.md]
        B --> C{Sessions found?}
        C -->|Multiple| D[Show menu + New Work option]
        C -->|One| E[Ask to restore]
        C -->|None| F[Start new work]
        D --> G[User selects]
        E --> G
        F --> I
        G --> H["Read latest + JIRA comment + checklist\n(via terminal-map.json)"]
        H --> I[Show summary, begin work]
    end

    subgraph RUN["Session Running"]
        I --> J["Important action\ncommit / push / build / flash / JIRA"]
        J --> K["Update latest-{id}.md locally"]
        K --> J
    end

    subgraph END_["Session End"]
        K --> L["User says: handover / done / quit"]
        L --> M["Write session log\nsessions/{id}/YYYY-MM-DD-HHmm.md\n+ update latest-{id}.md"]
        M --> N[git add + commit + push GitHub]
        N --> O["Update main JIRA ticket\n(lookup via terminal-map.json)"]
        O --> P["Update other related JIRA tickets\n(touched during session)"]
    end

    subgraph STORAGE["Storage Layer"]
        direction LR
        S1["GitHub\nfw-multi-agent repo\n(source of truth)"]
        S2["Local Disk\nD:\\mybot\\handover\\"]
        S3["JIRA\nper-task brief record"]
        S4["terminal-map.json\nterminal to JIRA mapping"]
    end
```

## Terminal Map

| Terminal | Working Dir | JIRA Tracker |
|----------|------------|--------------|
| reactor-fw | `D:\mybot\git\reactor-fw` | FWP-737 |
| reactor-50-100-fw | `D:\mybot\git\reactor-50-100-fw` | FWP-737 |
| esp32 | `D:\mybot\git\pg-reactor-esp32-wifi-bt` | FWP-738 |
| mybot | `D:\mybot` | FWP-739 |
| fw-multi-agent | `D:\mybot\fw-multi-agent` | FWP-739 |

## Lifecycle

1. **Start**: `git pull` -> scan `latest-*.md` -> present restore menu (or "New Work")
2. **Running**: update `latest-{id}.md` on every important action
3. **End**: write session log -> push GitHub -> update JIRA comments

## Key Principles

1. Code must be in mergeable state at session end
2. Never rely on context window -- write important info to disk
3. JIRA comments are brief; GitHub has full logs
4. Each terminal is independent
5. `git pull` on start, `git push` on end -- GitHub is source of truth
