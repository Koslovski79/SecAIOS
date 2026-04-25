# DEFENSIVE MAPPER

Defensive mapping - Detection rules, SIEM queries, and mitigation controls.

## Overview

For each finding, map to defensive controls:
- MITRE ATT&CK technique
- Detection rule
- SIEM query
- Mitigation

## MITRE ATT&CK Mapping

CVE/Issue → MITRE Technique:
```
CVE-2021-41773 → T1190 (Exploit Public-Facing App)
SQL Injection → T1190, T1059 (Command & Scripting Interpreter)
XSS → T1189 (Drive-by Compromise)
```

## Detection Rules

### Suricata
```
alert http any any -> any any (http.uri; "cgi-bin"; content: ".."; msg: "Apache Path Traversal";)
```

### Snort
```
alert tcp any any -> any any (msg: "Apache CVE-2021-41773"; content: "/cgi-bin/"; nocase;)
```

## SIEM Queries

### Splunk
```
index=web cgi-bin *.. | stats count by src_ip
```

### ELK
```
index:* web cgi-bin *.  /  | search cgi-bin 
```

### QRadar
```
SELECT * FROM events WHERE name='web' AND url LIKE '%cgi-bin%..%'
```

## Mitigation Controls

| Attack | WAF Rule | IPS | Input Validation |
|--------|----------|-----|-------------------|
| SQLi | Block UNION | Drop ' | Parameterized queries |
| XSS | Script filter | Drop | Output encoding |
| RCE | Block cmd chars | Drop | No shell execution |
| Path | Block ../ | Drop | Canonicalize path |

## Output

Include in report:
- MITRE ATT&CK mapping
- Detection rule examples
- SIEM queries
- Mitigation recommendations

## Key Principles

1. Blue team perspective
2. Actionable detection rules
3. Complete query examples
4. Prioritized mitigations