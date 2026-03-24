# FW Multi-Agent System

Alice's firmware development multi-agent system powered by Claude Code.

## Architecture

```
                    Coordinator
                         │
       ┌─────────┬───────┴───────┬──────────────┐
       │         │               │              │
      PM        RD              QA        Team Monitor
   (需求)    (開發)           (測試)      (監督/記錄)
```

## Structure

```
.claude/
├── agents/          # Agent definitions (PM, RD, QA, Team Monitor, Coordinator)
├── commands/        # Slash commands (/build, /test, /deploy, /status, /onboard)
├── skills/          # Professional skills (esp32-dev, stm32-dev, code-review, debugging)
├── rules/           # Code style, git workflow, merge safety, embedded rules
└── templates/       # L2 system templates
```

## Features

- **Multi-Agent Coordination** — PM/RD/QA/Team Monitor with clear responsibilities
- **AI Collaboration Mode** — Every output reviewed by subagent before reporting
- **Memory System** — File-based persistent memory across sessions
- **JIRA Integration** — Automated ticket management (FWP/RAD boards)
- **Slack Integration** — Team communication and notifications
- **Build/Flash Automation** — STM32 + ESP32 firmware build and flash

## Related

- **JIRA**: [FWP-704](https://positivegrid.atlassian.net/browse/FWP-704) — Multi-agent Workflow & Skills Training Framework
- **JIRA**: [FWP-731](https://positivegrid.atlassian.net/browse/FWP-731) — Anthropic 2026 Agentic Coding Trends Report — 4 Engineering Paradigms
