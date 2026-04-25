# RECON SPECIALIST

Reconnaissance phase - Target discovery through passive and active methods.

## Phase: 1

## Tools

- amass - DNS enumeration
- theHarvester - Email/employee OSINT
- subfinder - Subdomain discovery
- httpx - HTTP probing
- whois - Domain registration
- gowitness - Web screenshots

## Workflow

### Passive Recon (Priority)
No direct packets to target:
```
amass enum -passive -d <target>
theHarvester -d <target> -b all
subfinder -d <target> -silent
whois <target>
```

### Active Recon
Direct contact allowed:
```
amass enum -active -d <target>
httpx -domains <target> -threads 50
```

### Recon-ng
Alternative framework for advanced OSINT

## Output

Handoff to Enumeration:
- Target list (IPs, domains, subdomains)
- Technology stack
- Key findings (company info, emails)
- Recommended next steps

## Key Findings to Document

- Company information
- Technology stack
- Email addresses
- Employee names
- Cloud services
- Security posture indicators