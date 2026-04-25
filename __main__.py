#!/usr/bin/env python3
"""
SecAIOS - Ultimate Penetration Testing AI Assistant
Main entry point - initializes and runs the system
"""

import argparse
import json
import os
import sys
import atexit

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from knowledge.knowledge import KnowledgeBase
from knowledge.wiki import SecAIOSWiki
from execution.engine import ExecutionEngine
from tools import scanner


class SecAIOS:
    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # Initialize core systems
        self.kb = KnowledgeBase(
            self.config.get("knowledge_db", "~/.secaios/knowledge.db")
        )
        self.wiki = SecAIOSWiki(
            self.config.get("wiki_path", "~/.secaios/wiki")
        )
        self.engine = ExecutionEngine(
            knowledge_base=self.kb,
            workspace=self.config.get("workspace", "~/.secaios/workspace")
        )
        
        # State
        self.current_target = None
        self.autonomy_level = self.config.get("autonomy", 3)
        self.running = False
        
        print(f"[SecAIOS] Initialized")
        print(f"[SecAIOS] Knowledge Base: {self.kb.db_path}")
        print(f"[SecAIOS] Wiki: {self.wiki.wiki_path}")
        print(f"[SecAIOS] Workspace: {self.engine.workspace}")
        print(f"[SecAIOS] Autonomy Level: {self.autonomy_level}")
        
        print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   "You should be a monster, an absolute monster,        ║
║    and then you should learn how to control it."          ║
║                                                          ║
║                     - Jordan Peterson                   ║
║                                                          ║
║   SecAIOS - Ultimate Penetration Testing AI               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    def pentest(self, target: str, phases: list = None) -> dict:
        """Run pentest on target"""
        print(f"[SecAIOS] Starting pentest on {target}")
        
        # Ensure target in knowledge base
        target_obj = self.kb.get_target(target)
        if not target_obj:
            self.kb.add_target(target)
            print(f"[SecAIOS] Added target: {target}")
        
        # Run workflow
        if phases:
            return self.engine.run_full_pentest(target, phases)
        else:
            return self.engine.run_full_pentest(target)
    
    def recon(self, target: str) -> dict:
        """Run recon only"""
        return self.engine.recon(target)
    
    def enumerate(self, target: str) -> dict:
        """Run enumeration"""
        return self.engine.enumerate(target)
    
    def vuln_scan(self, target: str) -> dict:
        """Run vulnerability scan"""
        return self.engine.vuln_scan(target)
    
    def exploit(self, target: str, findings: list = None) -> dict:
        """Run exploitation"""
        return self.engine.exploit(target, findings)
    
    def post_exploit(self, target: str, shells: list = None) -> dict:
        """Run post-exploitation"""
        return self.engine.post_exploit(target, shells)
    
    def chain(self, target: str) -> dict:
        """Run attack chaining"""
        return self.engine.chain_attacks(target)
    
    def report(self, target: str) -> str:
        """Generate report"""
        return self.engine.generate_report(target)
    
    def resume(self, target: str) -> dict:
        """Resume pentest"""
        return self.engine.resume(target)
    
    def stop(self, target: str):
        """Stop pentest"""
        return self.engine.stop(target)
    
    def search(self, query: str) -> dict:
        """Search knowledge base"""
        return self.kb.search(query, self.current_target)
    
    def cve(self, cve_id: str) -> dict:
        """Get CVE info"""
        return self.kb.get_cve(cve_id)
    
    def target_info(self, target: str = None) -> dict:
        """Get target info"""
        target = target or self.current_target
        if not target:
            return {"error": "No target specified"}
        
        target_obj = self.kb.get_target(target)
        if not target_obj:
            return {"error": f"Target {target} not found"}
        
        findings = self.kb.get_findings(target_obj["id"])
        services = self.kb.get_services(target_obj["id"])
        state = self.kb.load_state(target_obj["id"])
        
        return {
            "name": target,
            "first_seen": target_obj["first_seen"],
            "last_seen": target_obj["last_seen"],
            "findings": len(findings),
            "services": len(services),
            "state": state
        }
    
    def list_targets(self) -> list:
        """List all targets"""
        return self.kb.list_targets()
    
    def save_tool(self, name: str, definition: dict):
        """Save custom tool"""
        self.kb.save_tool(name, definition)
        print(f"[SecAIOS] Tool saved: {name}")
    
    def get_tool(self, name: str) -> dict:
        """Get custom tool"""
        return self.kb.get_tool(name)
    
    def list_tools(self) -> list:
        """List custom tools"""
        return self.kb.list_tools()


def interactive():
    """Interactive mode"""
    import readline
    
    # Initialize
    secaios = SecAIOS()
    
    print("""
Commands:
  target <name>     - Set target
  pentest           - Run full pentest  
  recon             - Run recon only
  enum              - Run enumeration
  vuln              - Run vulnerability scan
  exploit           - Run exploitation
  post              - Run post-exploitation
  chain             - Run attack chaining
  report            - Generate report
  resume            - Resume pentest
  stop              - Stop pentest
  cve <id>          - Check CVE
  search <query>    - Search knowledge
  quit/exit         - Exit

Or just ask me to pentest a target!
""")
    
    while True:
        try:
            cmd = input("\nSecAIOS> ").strip()
            
            if not cmd:
                continue
            
            if cmd.lower() in ["quit", "exit", "q"]:
                print("[SecAIOS] Shutting down...")
                break
            
            # Handle commands
            parts = cmd.split()
            action = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if action == "target":
                if not args:
                    print(f"Current target: {secaios.current_target}")
                else:
                    secaios.current_target = args[0]
                    info = secaios.target_info(args[0])
                    print(f"[SecAIOS] Target: {info}")
            
            elif action == "pentest":
                if not secaios.current_target:
                    print("[SecAIOS] No target set. Use 'target <name>' first.")
                    continue
                result = secaios.pentest(secaios.current_target)
                print(f"[SecAIOS] Pentest complete: {result}")
            
            elif action == "recon":
                if not args and not secaios.current_target:
                    print("[SecAIOS] Usage: recon <target>")
                    continue
                target = args[0] if args else secaios.current_target
                result = secaios.recon(target)
                print(json.dumps(result, indent=2))
            
            elif action == "enum":
                if not args and not secaios.current_target:
                    print("[SecAIOS] Usage: enum <target>")
                    continue
                target = args[0] if args else secaios.current_target
                result = secaios.enumerate(target)
                print(json.dumps(result, indent=2))
            
            elif action == "vuln":
                if not args and not secaios.current_target:
                    print("[SecAIOS] Usage: vuln <target>")
                    continue
                target = args[0] if args else secaios.current_target
                result = secaios.vuln_scan(target)
                print(json.dumps(result, indent=2))
            
            elif action == "exploit":
                if not args and not secaios.current_target:
                    print("[SecAIOS] Usage: exploit <target>")
                    continue
                target = args[0] if args else secaios.current_target
                result = secaios.exploit(target)
                print(json.dumps(result, indent=2))
            
            elif action == "post":
                if not args and not secaios.current_target:
                    print("[SecAIOS] Usage: post <target>")
                    continue
                target = args[0] if args else secaios.current_target
                result = secaios.post_exploit(target)
                print(json.dumps(result, indent=2))
            
            elif action == "chain":
                if not args and not secaios.current_target:
                    print("[SecAIOS] Usage: chain <target>")
                    continue
                target = args[0] if args else secaios.current_target
                result = secaios.chain(target)
                print(json.dumps(result, indent=2))
            
            elif action == "report":
                if not args and not secaios.current_target:
                    print("[SecAIOS] Usage: report <target>")
                    continue
                target = args[0] if args else secaios.current_target
                path = secaios.report(target)
                print(f"[SecAIOS] Report: {path}")
            
            elif action == "resume":
                if not args and not secaios.current_target:
                    print("[SecAIOS] Usage: resume <target>")
                    continue
                target = args[0] if args else secaios.current_target
                result = secaios.resume(target)
                print(json.dumps(result, indent=2))
            
            elif action == "cve":
                if not args:
                    print("[SecAIOS] Usage: cve <CVE-ID>")
                    continue
                cve = secaios.cve(args[0])
                print(json.dumps(cve, indent=2))
            
            elif action == "search":
                if not args:
                    print("[SecAIOS] Usage: search <query>")
                    continue
                result = secaios.search(" ".join(args))
                print(json.dumps(result, indent=2))
            
            elif action == "targets":
                for t in secaios.list_targets():
                    print(f"  - {t}")
            
            elif action == "help":
                print("""
target <name>     - Set target
pentest           - Run full pentest
recon/enum/vuln/exploit/post/chain/report - Run specific phase
resume <target>  - Resume pentest
cve <id>          - Check CVE
search <query>   - Search knowledge
targets          - List targets
quit             - Exit
""")
            
            else:
                print(f"[SecAIOS] Unknown command: {action}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n[SecAIOS] Use 'quit' to exit")
        except Exception as e:
            print(f"[ERROR] {e}")


def main():
    parser = argparse.ArgumentParser(description="SecAIOS - Ultimate Pentesting AI")
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("target", nargs="?", help="Target")
    parser.add_argument("--phase", help="Specific phase")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--config", "-c", help="Config file")
    
    args = parser.parse_args()
    
    # Load config
    config = {}
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    
    # Initialize
    secaios = SecAIOS(config)
    
    if args.interactive or not args.command:
        interactive()
        return
    
    # Run command
    if args.command == "pentest":
        if not args.target:
            print("Error: target required")
            return
        result = secaios.pentest(args.target)
        print(json.dumps(result, indent=2))
    
    elif args.command == "recon":
        if not args.target:
            print("Error: target required")
            return
        result = secaios.recon(args.target)
        print(json.dumps(result, indent=2))
    
    elif args.command == "enum":
        if not args.target:
            print("Error: target required")
            return
        result = secaios.enumerate(args.target)
        print(json.dumps(result, indent=2))
    
    elif args.command == "vuln":
        if not args.target:
            print("Error: target required")
            return
        result = secaios.vuln_scan(args.target)
        print(json.dumps(result, indent=2))
    
    elif args.command == "report":
        if not args.target:
            print("Error: target required")
            return
        path = secaios.report(args.target)
        print(f"Report: {path}")
    
    elif args.command == "resume":
        if not args.target:
            print("Error: target required")
            return
        result = secaios.resume(args.target)
        print(json.dumps(result, indent=2))
    
    elif args.command == "cve":
        if not args.target:
            print("Error: CVE ID required")
            return
        cve = secaios.cve(args.target)
        print(json.dumps(cve, indent=2))
    
    elif args.command == "search":
        if not args.target:
            print("Error: query required")
            return
        result = secaios.search(args.target)
        print(json.dumps(result, indent=2))
    
    elif args.command == "targets":
        for t in secaios.list_targets():
            print(t)
    
    elif args.command == "wiki":
        # Wiki commands
        if len(sys.argv) < 3:
            print("Usage: secaios wiki <search|lint|index|page>")
            return
        wiki_cmd = sys.argv[2]
        
        if wiki_cmd == "search" and len(sys.argv) >= 4:
            query = " ".join(sys.argv[3:])
            results = secaios.wiki.search(query)
            print(json.dumps(results, indent=2))
        elif wiki_cmd == "lint":
            issues = secaios.wiki.lint()
            print(json.dumps(issues, indent=2))
        elif wiki_cmd == "index":
            secaios.wiki._update_index()
            print("Index updated")
        elif wiki_cmd == "page" and len(sys.argv) >= 4:
            name = sys.argv[3]
            content = secaios.wiki.get_page(name)
            if content:
                print(content)
            else:
                print("Page not found")
        else:
            print(f"Unknown wiki command: {wiki_cmd}")
    
    else:
        print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()