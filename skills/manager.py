"""
SecAIOS Skills System
Dynamic tool/skills loading based on context (like Agent Zero)
"""

import os
import json
import re
from typing import Dict, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Skill:
    name: str
    description: str
    triggers: List[str]
    prompt: str
    tools: List[str]
    category: str = "general"

class SkillsManager:
    """
    Skills system that loads relevant tools based on context.
    Similar to Agent Zero's SKILL.md system.
    """
    
    def __init__(self, skills_dir: str = "./skills"):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        self._load_skills()
    
    def _load_skills(self):
        """Load all skills from the skills directory"""
        
        skills_dir = Path(self.skills_dir)
        if not skills_dir.exists():
            skills_dir = Path(__file__).parent.parent / "skills"
            if not skills_dir.exists():
                print(f"Skills directory not found: {self.skills_dir}")
                return
        
        for skill_file in skills_dir.glob("**/*.md"):
            try:
                skill = self._parse_skill_file(skill_file)
                if skill:
                    self.skills[skill.name] = skill
                    print(f"Loaded skill: {skill.name}")
            except Exception as e:
                print(f"Failed to load skill {skill_file}: {e}")
    
    def _parse_skill_file(self, file_path: Path) -> Optional[Skill]:
        """Parse a SKILL.md file"""
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        name = file_path.stem.replace('-', ' ').replace('_', ' ').title()
        
        description = ""
        triggers = []
        prompt_parts = []
        tools = []
        
        lines = content.split('\n')
        in_prompt = False
        in_tools = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('## Description'):
                continue
            elif line.startswith('## Triggers'):
                continue
            elif line.startswith('## Prompt'):
                in_prompt = True
                in_tools = False
                continue
            elif line.startswith('## Tools'):
                in_tools = True
                in_prompt = False
                continue
            elif line.startswith('#'):
                in_prompt = False
                in_tools = False
            
            if not line:
                continue
            
            if not in_prompt and not in_tools:
                description += line + " "
            elif in_prompt:
                prompt_parts.append(line)
            elif in_tools:
                if line.startswith('-') or line.startswith('*'):
                    tool = line.lstrip('-* ').strip()
                    if tool:
                        tools.append(tool)
        
        for word in name.lower().split():
            if word not in [w.lower() for w in triggers]:
                triggers.append(word)
        
        for tool in tools:
            for word in tool.lower().split():
                if word not in triggers:
                    triggers.append(word)
        
        prompt = '\n'.join(prompt_parts)
        
        if not prompt:
            prompt = f"You are a {name} expert. Use the available tools to help with {name.lower()} tasks."
        
        return Skill(
            name=name,
            description=description.strip(),
            triggers=list(set(triggers)),
            prompt=prompt,
            tools=tools,
            category=file_path.parent.name if file_path.parent.name != 'skills' else 'general'
        )
    
    def get_relevant_skills(self, query: str) -> List[Skill]:
        """Get skills relevant to a query"""
        
        query_lower = query.lower()
        relevant = []
        
        for skill in self.skills.values():
            for trigger in skill.triggers:
                if trigger.lower() in query_lower:
                    relevant.append(skill)
                    break
        
        if not relevant:
            relevant = list(self.skills.values())[:3]
        
        return relevant
    
    def build_skill_prompt(self, skills: List[Skill]) -> str:
        """Build a prompt from relevant skills"""
        
        if not skills:
            return ""
        
        prompt_parts = ["=== RELEVANT SKILLS ==="]
        
        for skill in skills:
            prompt_parts.append(f"\n## {skill.name}")
            prompt_parts.append(f"Description: {skill.description}")
            prompt_parts.append(f"Instructions: {skill.prompt}")
            if skill.tools:
                prompt_parts.append(f"Available tools: {', '.join(skill.tools)}")
        
        return '\n'.join(prompt_parts)
    
    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """Get a specific skill by name"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict]:
        """List all available skills"""
        return [
            {
                'name': s.name,
                'description': s.description,
                'category': s.category,
                'triggers': s.triggers[:5]
            }
            for s in self.skills.values()
        ]


# Built-in skills for pentesting

BUILTIN_SKILLS = {
    'nmap': Skill(
        name='Nmap Scanner',
        description='Network port scanner and service detection',
        triggers=['scan', 'port', 'nmap', 'network', 'recon'],
        prompt="""You are a network scanning expert using nmap.

Guidelines:
- Always use appropriate nmap flags for the goal
- Common scans: nmap -sV -p- for full port scan
- For evasion: nmap -sS -f -D for stealth
- Output formats: -oG (grepable), -oX (XML), -oN (normal)
- Service version detection: -sV
- OS detection: -O (requires root)

Always analyze and explain the results.""",
        tools=['nmap', 'rustscan'],
        category='reconnaissance'
    ),
    'nikto': Skill(
        name='Nikto Scanner',
        description='Web vulnerability scanner',
        triggers=['nikto', 'vuln', 'web', 'scan', 'http'],
        prompt="""You are a web vulnerability scanning expert using Nikto.

Guidelines:
- Basic scan: nikto -h target
- Specify port: -p 80,443
- Tuning options: -Tuning 1 (interesting)
- Save output: -o results.xml
- Scan multiple ports: -p 1-1000

Analyze findings and prioritize by severity.""",
        tools=['nikto'],
        category='vulnerability-scanning'
    ),
    'gobuster': Skill(
        name='Gobuster Directory Scanner',
        description='Directory and file enumeration',
        triggers=['gobuster', 'directory', 'dirb', 'enum', 'hidden', 'files'],
        prompt="""You are a directory enumeration expert using gobuster.

Guidelines:
- Basic dir scan: gobuster dir -u URL -w wordlist
- DNS subdomain enum: gobuster dns -d domain -w wordlist
- Fuzzy enum: gobuster fuzz -u URL -w wordlist
- Common wordlists: /usr/share/wordlists/dirb/common.txt
- Thread count: -t 50 for speed
- Add extensions: -x .php,.html,.txt

Report found directories and their responses.""",
        tools=['gobuster', 'dirb', 'ffuf'],
        category='reconnaissance'
    ),
    'sqlmap': Skill(
        name='SQLMap SQL Injection',
        description='Automated SQL injection detection and exploitation',
        triggers=['sqlmap', 'sql', 'injection', 'sqli', 'database'],
        prompt="""You are a SQL injection expert using sqlmap.

Guidelines:
- Basic test: sqlmap -u "URL"
- Specify parameter: -p param
- List databases: --dbs
- Dump table: --tables -D dbname
- Get shell: --os-shell
- Risk levels: --risk=1 (default), --risk=3 (highest)
- Threading: --threads=5

IMPORTANT: Only use on authorized targets. Document all findings.""",
        tools=['sqlmap'],
        category='exploitation'
    ),
    'xss': Skill(
        name='XSS Attack',
        description='Cross-site scripting detection and exploitation',
        triggers=['xss', 'cross-site', 'scripting', 'javascript', 'alert'],
        prompt="""You are an XSS vulnerability expert.

Common payloads:
- <script>alert(1)</script>
- <img src=x onerror=alert(1)>
- <svg onload=alert(1)>
- ',alert(1),'
- "><script>alert(1)</script>

Testing approach:
1. Find input points
2. Test basic payloads
3. Test filter bypasses
4. Test context-specific payloads
5. Document PoC

Report findings with PoC and impact.""",
        tools=['curl', 'kxss', 'dalfox'],
        category='exploitation'
    ),
    'subdomain': Skill(
        name='Subdomain Enumeration',
        description='Discover subdomains and DNS information',
        triggers=['subdomain', 'subdomains', 'dns', 'enum', 'whois'],
        prompt="""You are a subdomain enumeration expert.

Tools and techniques:
- subfinder -d domain -silent
- amass enum -d domain
- assetfinder --subs-only domain
- DNS brute force with wordlists
- Certificate transparency logs (crt.sh)
- DNS zone transfers (if possible)

Always verify discovered subdomains are active.""",
        tools=['subfinder', 'amass', 'assetfinder', 'dnsenum'],
        category='reconnaissance'
    ),
    'nuclei': Skill(
        name='Nuclei Vulnerability Scanner',
        description='Template-based vulnerability scanning',
        triggers=['nuclei', 'template', 'cve', 'poc'],
        prompt="""You are a nuclei vulnerability scanning expert.

Guidelines:
- Basic scan: nuclei -u URL
- Severity filter: -severity critical,high,medium
- Update templates: -update
- JSON output: -json -o results.json
- Custom templates: -t templates/
- Rate limiting: -rate-limit 150

Templates cover CVEs, misconfigurations, and more.""",
        tools=['nuclei'],
        category='vulnerability-scanning'
    ),
    'curl': Skill(
        name='Curl HTTP Testing',
        description='HTTP request testing and analysis',
        triggers=['curl', 'http', 'request', 'headers', 'method'],
        prompt="""You are an HTTP testing expert using curl.

Common uses:
- GET: curl -s URL
- POST: curl -X POST -d "data" URL
- Headers: curl -I URL
- Cookies: curl -b "cookie" URL
- Auth: curl -u user:pass URL
- Follow redirects: curl -L URL
- Verbose: curl -v URL

Use curl to test endpoints, headers, and authentication.""",
        tools=['curl', 'wget'],
        category='testing'
    ),
    'hydra': Skill(
        name='Hydra Password Attack',
        description='Online password cracking tool',
        triggers=['hydra', 'brute', 'password', 'crack', 'login'],
        prompt="""You are a password attack expert using Hydra.

Guidelines:
- HTTP POST: hydra -L users.txt -P pass.txt target.com http-post-form "/login:user=^USER^&pass=^PASS^:F=incorrect"
- SSH: hydra -L users.txt -P pass.txt ssh://target.com
- FTP: hydra -L users.txt -P pass.txt ftp://target.com
- Parallel: -t 4 for speed

IMPORTANT: Only use on authorized targets.""",
        tools=['hydra', 'medusa'],
        category='exploitation'
    ),
    'api': Skill(
        name='API Security Testing',
        description='REST and SOAP API security testing',
        triggers=['api', 'rest', 'json', 'graphql', 'swagger'],
        prompt="""You are an API security testing expert.

Testing approach:
1. Enumerate endpoints
2. Test HTTP methods (GET, POST, PUT, DELETE)
3. Test authentication bypass
4. Test IDOR vulnerabilities
5. Test for SQLi in parameters
6. Test rate limiting
7. Check for sensitive data exposure

Tools: curl, Postman, Burp Suite, graphql-voyager""",
        tools=['curl', 'jq'],
        category='exploitation'
    ),
}


SKILLS_MANAGER = SkillsManager()


for name, skill in BUILTIN_SKILLS.items():
    SKILLS_MANAGER.skills[name] = skill