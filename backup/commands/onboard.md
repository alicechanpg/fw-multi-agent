Onboard a new project as an L2 agent system.

## Usage

```
/onboard <project-path>
```

**Examples:**
- `/onboard C:\Projects\my-firmware`
- `/onboard ../pg-dsp-research`
- `/onboard .` (current directory)

## What Happens

1. **Project Analyzer** (Sonnet) scans the project:
   - Detects tech stack (MCU, RTOS, DSP, languages, frameworks)
   - Identifies existing structure (build files, config, tests)
   - Discovers modules and products
   - Checks for existing .claude/ content
   - Detects system language from comments and docs

2. **Confirmation prompt** with detection results:
   ```
   ┌─ Analysis Results ─────────────────────────┐
   │ Project: my-firmware-agent                 │
   │ Language: 中文 (detected from system)      │
   │ Tech Stack: ARM CM55 + FreeRTOS + DSP      │
   │ Skills: build, rtos, audio, bt, dsp (5)    │
   │ Agents: builder, debugger, analyzer (3)    │
   └────────────────────────────────────────────┘

   ? Confirm generation? [Y/Modify/Cancel]
   ```

3. **L2 Generator** (Sonnet) creates the structure:
   - CLAUDE.md (entry point)
   - SPEC.md (source of truth)
   - skills/ directory with domain knowledge
   - .claude/agents/ with specialized agents
   - .claude/commands/ with project commands
   - .claude/rules/ with architecture rules
   - memory/ structure
   - .gitignore (sensitive paths)

4. **Auto-validation** ensures compliance

## Detection Capabilities

| Category | Auto-Detected |
|----------|---------------|
| MCU/CPU | ARM, Xtensa, RISC-V, x86 |
| RTOS | FreeRTOS, Zephyr, ThreadX, bare-metal |
| Build | Make, CMake, Ninja, IDE projects |
| Languages | C, C++, Rust, Python, TypeScript |
| Modules | Audio, Bluetooth, DSP, USB, WiFi |
| Products | Reference designs, variants |

## Options

User can modify at confirmation:
- Project name and skill prefix
- Documentation language
- Skills to generate
- Agents to include
- Sensitivity level

## Prerequisites

1. Project path must exist
2. Write access to create .claude/ directory

## Modes

| Mode | Condition | Behavior |
|------|-----------|----------|
| **Create Mode** | No .claude/ exists | Generate full structure from scratch |
| **Integration Mode** | .claude/ exists | Preserve existing, convert to L2 format |

## Next Steps

After onboarding:
1. Navigate to project directory
2. Open Claude in that workspace
3. Use generated commands and agents
