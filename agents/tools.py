import subprocess
import json
import re
import os
from typing import Any, Dict, List, Optional

class ToolRegistry:
    def __init__(self):
        self.tools = {
            'run_nmap': self.run_nmap,
            'run_nikto': self.run_nikto,
            'run_gobuster': self.run_gobuster,
            'curl_head': self.curl_head,
            'curl_get': self.curl_get,
            'run_subfinder': self.run_subfinder,
            'run_whois': self.run_whois,
            'check_http_methods': self.check_http_methods,
            'run_nuclei': self.run_nuclei,
        }
    
    def get_tool_schemas(self) -> List[Dict]:
        schemas = []
        for name, func in self.tools.items():
            schemas.append({
                'type': 'function',
                'function': {
                    'name': name,
                    'description': func.__doc__ or f'Run {name}',
                    'parameters': func.__annotations__.get('return', {'type': 'object', 'properties': {}})
                }
            })
        return schemas

    def execute_tool(self, tool_name: str, arguments: Dict) -> str:
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            result = self.tools[tool_name](**arguments)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def run_nmap(self, target: str, ports: str = "1-1000", flags: str = "-sV") -> str:
        """Scan target with nmap. Useful for discovering open ports and services."""
        cmd = f"nmap {flags} -p {ports} {target} -oG -"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Nmap scan timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    def run_nikto(self, target: str, port: str = "80") -> str:
        """Run nikto web vulnerability scanner against target."""
        cmd = f"nikto -h {target} -p {port}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
            return f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Nikto scan timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    def run_gobuster(self, target: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", threads: int = "10") -> str:
        """Directory/file enumeration using gobuster."""
        cmd = f"gobuster dir -u {target} -w {wordlist} -t {threads}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Gobuster scan timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    def curl_head(self, url: str) -> str:
        """Send HEAD request to URL. Useful for checking HTTP headers and server info."""
        cmd = f"curl -s -I {url}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {str(e)}"

    def curl_get(self, url: str, follow_redirects: bool = True) -> str:
        """Send GET request to URL and retrieve response body."""
        redirect_flag = "-L" if follow_redirects else "-s"
        cmd = f"curl {redirect_flag} {url}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return f"Response:\n{result.stdout[:5000]}"
        except Exception as e:
            return f"Error: {str(e)}"

    def run_subfinder(self, domain: str) -> str:
        """Passive subdomain enumeration using subfinder."""
        cmd = f"subfinder -d {domain} -silent"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            return f"Subdomains:\n{result.stdout}"
        except Exception as e:
            return f"Error: {str(e)}"

    def run_whois(self, domain: str) -> str:
        """Perform whois lookup on domain."""
        cmd = f"whois {domain}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout[:5000]
        except Exception as e:
            return f"Error: {str(e)}"

    def check_http_methods(self, url: str) -> str:
        """Check allowed HTTP methods (OPTIONS) on target."""
        cmd = f"curl -s -X OPTIONS {url} -I"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {str(e)}"

    def run_nuclei(self, target: str, severity: str = "medium,high,critical") -> str:
        """Run nuclei vulnerability scanner with specified severity levels."""
        cmd = f"nuclei -u {target} -severity {severity} -silent"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
            return f"Findings:\n{result.stdout}\n\nErrors:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Nuclei scan timed out"
        except Exception as e:
            return f"Error: {str(e)}"


TOOL_REGISTRY = ToolRegistry()


NMAP_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_nmap",
        "description": "Scan target with nmap. Useful for discovering open ports and services. Returns grepable output with open ports and service versions.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target IP address or hostname"},
                "ports": {"type": "string", "description": "Port range to scan (default: 1-1000)", "default": "1-1000"},
                "flags": {"type": "string", "description": "Additional nmap flags (default: -sV)", "default": "-sV"}
            },
            "required": ["target"]
        }
    }
}

NIKTO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_nikto",
        "description": "Run nikto web vulnerability scanner. Checks for dangerous files, outdated server versions, and specific issues.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target URL or IP"},
                "port": {"type": "string", "description": "Port to scan (default: 80)", "default": "80"}
            },
            "required": ["target"]
        }
    }
}

GOBUSTER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_gobuster",
        "description": "Directory and file enumeration. Discovers hidden directories and files on web servers.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target URL"},
                "wordlist": {"type": "string", "description": "Path to wordlist", "default": "/usr/share/wordlists/dirb/common.txt"},
                "threads": {"type": "string", "description": "Number of threads (default: 10)", "default": "10"}
            },
            "required": ["target"]
        }
    }
}

CURL_HEAD_SCHEMA = {
    "type": "function",
    "function": {
        "name": "curl_head",
        "description": "Send HEAD request to get HTTP headers. Reveals server type, cookies, security headers, caching policies.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target URL"}
            },
            "required": ["url"]
        }
    }
}

CURL_GET_SCHEMA = {
    "type": "function",
    "function": {
        "name": "curl_get",
        "description": "Send GET request to retrieve full page content. Use for analyzing page structure, finding hidden params.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target URL"},
                "follow_redirects": {"type": "boolean", "description": "Follow redirects (default: true)", "default": True}
            },
            "required": ["url"]
        }
    }
}

SUBFINDER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_subfinder",
        "description": "Passive subdomain enumeration. Uses multiple DNS sources to discover subdomains without touching target.",
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Target domain (e.g., example.com)"}
            },
            "required": ["domain"]
        }
    }
}

WHOIS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_whois",
        "description": "Perform whois lookup to get domain registration info, nameservers, and contact details.",
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Target domain"}
            },
            "required": ["domain"]
        }
    }
}

HTTP_METHODS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "check_http_methods",
        "description": "Check which HTTP methods are allowed (OPTIONS). Useful for finding potentially dangerous methods like PUT, DELETE.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target URL"}
            },
            "required": ["url"]
        }
    }
}

NUCLEI_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_nuclei",
        "description": "Run nuclei vulnerability scanner with templates. Fast, template-based vulnerability detection.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target URL"},
                "severity": {"type": "string", "description": "Severity levels to scan (default: medium,high,critical)", "default": "medium,high,critical"}
            },
            "required": ["target"]
        }
    }
}


TOOL_SCHEMAS = [
    NMAP_SCHEMA,
    NIKTO_SCHEMA,
    GOBUSTER_SCHEMA,
    CURL_HEAD_SCHEMA,
    CURL_GET_SCHEMA,
    SUBFINDER_SCHEMA,
    WHOIS_SCHEMA,
    HTTP_METHODS_SCHEMA,
    NUCLEI_SCHEMA,
]