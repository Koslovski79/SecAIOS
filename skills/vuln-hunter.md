# VULN HUNTER

Vulnerability analysis phase - Find and validate security vulnerabilities.

## Phase: 3

## Tools

- nuclei - Vulnerability scanning
- nikto - Web vulnerability scanner
- sqlmap - SQL injection testing
- commix - Command injection
- x8 - HTTP parameter pollution
- gitleaks - Secret detection
- trufflehog - Secret detection

## Workflow

### Automated Scanning
```
nuclei -u <target> -severity critical,high,medium
nuclei -ut
nikto -h <target>
```

### Manual Testing
```
sqlmap -u <target> --batch --level 5
commix --url <target>
```

### Secret Detection
```
gitleaks detect --source=<repo>
trufflehog filesystem <path>
```

## Priority Targets

1. CVEs for known versions (from enumeration)
2. SQL injection
3. XSS (reflected/stored/DOM)
4. Command injection
5. Authentication bypass
6. IDOR
7. Secrets in code/config

## Output

Handoff to Exploitation:
- Vulnerability table with severity
- Exploitability status
- Available POCs
- Recommended exploits

## CVSS Priority

| Severity | Score | Action |
|----------|-------|--------|
| Critical | 9.0-10.0 | Immediate |
| High | 7.0-8.9 | Priority |
| Medium | 4.0-6.9 | Standard |
| Low | 0.1-3.9 | Document |

## Key Findings to Document

- CVE/issue name
- CVSS score
- Description
- Impact
- Exploitability