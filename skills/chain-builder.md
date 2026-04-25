# CHAIN BUILDER

Attack chaining phase - Combine vulnerabilities into multi-stage attack paths.

## Phase: 6

## Concept

Attack chains combine individual vulnerabilities into maximum-impact paths:

```
SQLi → File Write → RCE → Root → Domain Admin
  │         │         │       │         │
  └─────────┴─────────┴───────┴─────────
              Chain: Complete Domain Compromise
```

## Workflow

### Path Mapping
1. List all available access (from post-ex)
2. Identify paths to high-value targets
3. Calculate chain probability
4. Execute chains

### Chain Types

| Chain ID | Path | Impact |
|---------|------|--------|
| CH01 | Web vuln → RCE → Root | Server comp |
| CH02 | User creds → AD → Domain | Domain comp |
| CH03 | XSS → Admin → RCE | Full comp |
| CH04 | VPN → Internal → pivoting | Network |

## Execution

### Chain 01: Web → Domain Admin
```
1. SQLi gives webapp user
2. File write via INTO OUTFILE
3. RCE via webshell
4. linpeas → sudo → root
5. DCSync → domain admin
```

### Chain 02: User to Root
```
1. XSS steals session
2. Admin access
3. Upload RCE
4. Privilege escalation
```

## Output

Handoff to Reporting:
- Chains executed (success/failure)
- Systems compromised
- Business impact
- Data access achieved

## Key Principles

1. Always have fallback path
2. Document each step
3. Calculate business impact
4. Get approval before chains