# ENUMERATION SPECIALIST

Enumeration phase - Service detection, version identification, attack surface mapping.

## Phase: 2

## Tools

- nmap - Port scanning
- nmap -sV - Version detection
- whatweb - Tech fingerprinting
- sslscan - SSL analysis
- wpscan - WordPress enumeration
- droopescan - Drupal scanning
- nikto - Web vuln scan

## Workflow

### Port Scanning
```
nmap -p- <target> -oA full
nmap -sU <target> -oA udp
```
### Service Detection
```
nmap -sV -sC -p<ports> <target>
```
### Web Enumeration
```
whatweb <http://target>
wpscan --url <target> --enumerate vp
nikto -h <target>
```
### SSL Analysis
```
sslscan <target>:443
```

## Output

Handoff to Vulnerability Analysis:
- Service table with versions
- Known CVEs for versions
- Attack surface summary
- Technology stack confirmation

## Key Findings to Document

- All open ports
- Service versions
- CVE candidates
- Web technologies
- Authentication mechanisms