# SecAIOS - Ultimate Cybersecurity AI Operating System

> "You should be a monster, an absolute monster, and then you should learn how to control it." — Jordan Peterson

The ultimate AI-powered penetration testing system that combines the warrior mindset with guardian discipline.

## Philosophy

**Warrior Mindset** — Find EVERY vulnerability, exploit EVERY weakness, chain EVERY attack path
**Guardian Discipline** — Verify consent, stay within scope, document EVERYTHING, clean up after
**Control** — Restraint is a choice, not a limitation

This is what makes SecAIOS different: we CHOSE restraint because we CAN be a monster.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SecAIOS Core                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │     Knowledge Layer (LLM Wiki)              │   │
│  │  - raw/ (immutable sources)               │   │
│  │  - wiki/ (LLM-generated pages)          │   │
│  │  - index.md (catalog)                   │   │
│  │  - log.md (activity)                    │   │
│  └─────────────────────────────────────────────┘   │
│                         │                           │
│  ┌─────────────────────────────────────────────┐   │
│  │     Execution Engine                     │   │
│  │  - Parallel tool execution                │   │
│  │  - Workflow orchestration                │   │
│  │  - State management                    │   │
│  └─────────────────────────────────────────────┘   │
│                         │                           │
│  ┌─────────────────────────────────────────────┐   │
│  │     Tools Suite                            │   │
│  │  - Scanner wrappers (nmap, nuclei, etc.) │   │
│  │  - Post-exploitation                     │   │
│  │  - Reporting                            │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Workflow Phases

```
RECON → ENUMERATION → VULN ANALYSIS → EXPLOITATION → POST-EXPLOIT → ATTACK CHAIN → REPORTING
(Discovery)    (Services)    (Findings)    (POC)        (Pivoting)     (Combine)    (Docs)
```

---

## Features

### Core Systems
| System | Description |
|--------|-------------|
| **Knowledge Base** | SQLite persistence (targets, findings, CVEs, credentials) |
| **LLM Wiki** | Karpathy pattern - knowledge compounds over time |
| **Execution Engine** | Parallel execution, workflow orchestration, state management |
| **Tool Suite** | 15+ scanner wrappers |

### Skills (11)
| Skill | Phase | Description |
|-------|-------|-------------|
| pentest | Orchestrator | Main workflow coordinator |
| recon | 1 | Passive + active discovery |
| enumeration | 2 | Service detection |
| vuln-hunter | 3 | Vulnerability scanning |
| exploit-developer | 4 | POC development |
| post-exploiter | 5 | Privesc, pivoting, persistence |
| chain-builder | 6 | Attack chaining |
| report-writer | 7 | Professional reporting |
| continuous-monitor | Enhanced | Ongoing scanning |
| defensive-mapper | Enhanced | MITRE ATT&CK mapping |
| tool-crafter | Enhanced | Custom tool creation |

### Capabilities
- **Parallel Execution** — Run multiple tools simultaneously
- **Attack Chaining** — Combine vulnerabilities for max impact
- **Post-Exploitation** — Full privesc, lateral movement, persistence
- **LLM Wiki** — Knowledge compounds (Karpathy pattern)
- **State Management** — Save, resume, continue pentests
- **Professional Reporting** — Markdown + HTML output

---

## Quick Start

### Installation

```bash
# Clone or download SecAIOS
cd OpenAIOS

# Install dependencies
pip install -r requirements.txt

# Run interactive mode
python __main__.py -i

# Or run a command
python __main__.py pentest target.com
```

### Commands

```bash
# Full pentest
python __main__.py pentest target.com

# Specific phase
python __main__.py recon target.com
python __main__.py vuln target.com

# Generate report
python __main__.py report target.com

# Resume interrupted pentest
python __main__.py resume target.com

# Wiki operations
python __main__.py wiki search "keyword"
python __main__.py wiki lint
python __main__.py wiki index
```

---

## Directory Structure

```
OpenAIOS/
├── __main__.py              # Main entry point
├── config.yaml              # Configuration
├── opencode.json           # Agent definitions
│
├── knowledge/
│   ├── knowledge.py       # SQLite knowledge base
│   ├── wiki.py           # LLM Wiki (Karpathy pattern)
│   └── __init__.py
│
├── execution/
│   ├── engine.py          # Parallel execution, workflow
│   └── __init__.py
│
├── tools/
│   ├── scanner.py       # 15+ tool wrappers
│   └── __init__.py
│
├── skills/
│   ├── pentest.md       # Main orchestrator
│   ├── recon.md       # Phase 1
│   ├── enumeration.md # Phase 2
│   ├── vuln-hunter.md # Phase 3
│   ├── exploit-developer.md # Phase 4
│   ├── post-exploiter.md # Phase 5
│   ├── chain-builder.md # Phase 6
│   ├── report-writer.md # Phase 7
│   └── README.md      # Skills index
│
├── agents/
│   ├── ultima.md      # Ultimate agent definition
│   └── pentester.md # Pentester agent
│
└── docs/
    ├── workflows.md          # Full workflow docs
    ├── workflow-orchestrator.md # Orchestrator docs
    ├── ultima-spec.md      # Ultimate spec
    └── background-agents.md
```

---

## System Mantra

```
"Everyone says, 'Well, you should be harmless, virtuous, you shouldn't do anyone any harm, 
you should sheath your competitive instinct. You shouldn't try to win. You don't want to be 
too aggressive. You don't want to be too assertive. No. Wrong. You should be a monster, an 
absolute monster, and then you should learn how to control it. It's better to be a warrior in a 
garden than a gardener in a war." - Jordan Peterson
```

This is the core philosophy. We find EVERY vulnerability (be the monster), but operate with strict consent, scope, and ethics (the control).

---

## LLM Wiki Pattern

Implements Andrej Karpathy's LLM Wiki:

```
wiki/
├── raw/           # Immutable sources (scan results)
├── wiki/          # LLM-generated pages
│   ├── target-com.md
│   ├── CVE-2021-41773.md
│   └── sql-injection.md
├── index.md      # Catalog
└── log.md      # Activity log
```

**Key insight**: Knowledge COMPOUNDS — doesn't re-derive each session.

---

## Tool Suite

### Recon
- amass, theHarvester, subfinder, httpx

### Enumeration
- nmap, whatweb, wpscan, sslscan

### Vulnerability
- nuclei, nikto, sqlmap, commix, gitleaks

### Post-Exploitation
- linpeas, winPEAS, mimikatz, pspy

### Utilities
- check_port, resolve_hostname, get_banner

---

## Configuration

Edit `config.yaml`:

```yaml
# Execution
autonomy: 3          # 1=ask everything, 4=full auto
parallel_tasks: 5     # Max parallel tools
timeout: 300          # Default timeout

# Knowledge
knowledge_db: ~/.secaios/knowledge.db
wiki_path: ~/.secaios/wiki

# Tools
nuclei:
  severity: critical,high,medium
  templates_update: true

nmap:
  default_args: -sV -sC
  timing: T4
```

---

## Integration Points

### OpenCode
Load as skill:
```markdown
Use skills/recon.md for reconnaissance phase
Use skills/vuln-hunter.md for vulnerability scanning
Use skills/pentest.md as main orchestrator
```

### Telegram
Run bot: `python execution/telegram/opencode_bot.py`

### Background Agents
Install: `ocx add kdco/background-agents`

---

## Contributing

1. Add skills to `skills/` directory
2. Add tool wrappers to `tools/scanner.py`
3. Update this README
4. Document in `docs/`

---

## Credits

- **Jordan Peterson** — System mantra
- **Andrej Karpathy** — LLM Wiki pattern
- **OpenCode** — Core agent technology
- **Community** — Tools and techniques

---

> **The monster is in the control.** — SecAIOS

License: MIT
Version: 1.0.0