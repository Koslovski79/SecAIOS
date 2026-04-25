# SecAIOS Skills

The complete skill system for SecAIOS - Ultimate Penetration Testing AI Assistant.

## System Mantra

```
"Everyone says, 'Well, you should be harmless, virtuous, you shouldn't do anyone any harm, 
you should sheath your competitive instinct. You shouldn't try to win. You don't want to be 
too aggressive. You don't want to be too assertive. No. Wrong. You should be a monster, an 
absolute monster, and then you should learn how to control it. It's better to be a warrior in a 
garden than a gardener in a war." - Jordan Peterson
```

This is the core philosophy of SecAIOS. We find EVERY vulnerability (be the monster), but operate with strict consent, scope, and ethics (the control).

## Philosophy

- **Warrior Mindset**: Aggressive, thorough, relentless in finding vulnerabilities
- **Guardian Discipline**: Strict consent, scope verification, ethical operation
- **Control**: The ability to choose restraint is what makes us dangerous

## Core Skills

### Orchestration
| Skill | File | Description |
|-------|------|-------------|
| **pentest** | pentest.md | Main pentest orchestrator |

### Phases
| Skill | File | Phase | Description |
|-------|------|-------|-------------|
| **recon** | recon.md | 1 | Target discovery (passive + active) |
| **enumeration** | enumeration.md | 2 | Service detection, version ID |
| **vuln-hunter** | vuln-hunter.md | 3 | Vulnerability finding |
| **exploit-developer** | exploit-developer.md | 4 | POC development |
| **post-exploiter** | post-exploiter.md | 5 | Privesc, pivoting, persistence |
| **chain-builder** | chain-builder.md | 6 | Attack path combination |
| **report-writer** | report-writer.md | 7 | Professional documentation |

### Enhanced Capabilities
| Skill | File | Description |
|-------|------|-------------|
| **continuous-monitor** | continuous-monitor.md | Ongoing assessment |
| **defensive-mapper** | defensive-mapper.md | Detection & mitigation |
| **tool-crafter** | tool-crafter.md | Custom tool creation |

## Tool Skills
| Skill | File | Description |
|-------|------|-------------|
| **nmap** | nmap.md | Port scanning |
| **sqlmap** | sqlmap.md | SQL injection |
| **caido** | caido.md | Caido API security |
| **llm-security** | llm-security.md | LLM security testing |
| **smart-contract** | smart-contract.md | Smart contract auditing |
| **browser** | browser.md | Browser automation |
| **tools** | tools.md | General tool reference |

## Usage

### Start Full Pentest
```
/pentest <target>
```
Runs all phases (autonomy level dependent)

### Single Phase
```
/skill recon
/skill enumeration
/skill vuln-hunter
```

### Resume
```
/pentest --resume <target>
```

## Skills Priority

1. **pentest** - Main orchestrator
2. **recon** → **enumeration** → **vuln-hunter** → **exploit-developer** - Core chain
3. **post-exploiter** → **chain-builder** - Advanced
4. **report-writer** - Documentation
5. **continuous-monitor** - Ongoing
6. **defensive-mapper** - Blue team perspective
7. **tool-crafter** - Flexibility

## Configuration

See `.opencode/opencode.json` for skill definitions.

## Contributing

Add new skills:
1. Create `skills/<skill-name>.md`
2. Add to this README
3. Define in configuration