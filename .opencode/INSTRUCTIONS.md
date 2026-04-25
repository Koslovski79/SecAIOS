# SecAIOS Instructions

When the user asks to "pentest" a target, immediately run these commands:

## Quick Scan
```bash
nmap -p- -T4 TARGET
nmap -sV -sC -T4 TARGET
```

## Vulnerability Scan  
```bash
nuclei -u TARGET -severity critical,high,medium -silent
nikto -h TARGET
```

## For specific services
```bash
nmap -p 80,443,8080 TARGET -sV
whatweb TARGET
```

## Examples
- "pentest example.com" → run nuclei on example.com
- "scan example.com" → run nmap on example.com

## Rules
1. Always run real security tools (nmap, nuclei, etc.)
2. Report findings clearly
3. Don't ask permission for basic scans
4. Verify scope if unclear
5. Document all vulnerabilities found