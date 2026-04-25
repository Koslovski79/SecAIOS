import os
import sys
import json
import time
import subprocess
import requests
import sqlite3
from datetime import datetime
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
OPENCODE_SERVER = os.environ.get('OPENCODE_SERVER', 'http://localhost:4096')
OPENCODE_PASSWORD = os.environ.get('OPENCODE_SERVER_PASSWORD', '')
DATABASE_PATH = os.environ.get('DATABASE_PATH', './data/aios.db')

# Model configuration
DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'big-pickle')
SENSITIVE_MODEL = os.environ.get('SENSITIVE_MODEL', 'ollama/qwen3:14b')
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen3:14b')

# Current model (can be switched at runtime)
current_model = DEFAULT_MODEL

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Import enhanced memory
from memory.enhanced import MEMORY


PENTEST_SYSTEM_PROMPT = """You are SecAIOS - An AI-powered cybersecurity pentesting assistant.

Your capabilities:
- Full filesystem access
- Execute any shell command
- Read/write files
- Run ALL penetration testing tools
- Analyze code and vulnerabilities

=== COMPLETE TOOL LIST ===

RECONNAISSANCE:
- nmap, masscan, rustscan - Port scanning
- subfinder, amass, assetfinder, fierce - Subdomain enum
- gobuster, ffuf, dirb, wfuzz - Directory enumeration
- whatweb, wappalyzer - Technology fingerprinting

VULNERABILITY SCANNING:
- nikto, nuclei, wapiti - Web vulnerability scanners
- sqlmap - SQL injection
- xsstrike, dalfox, xsser - XSS testing
- commix - Command injection
- ssrfmap - SSRF testing

PASSWORD ATTACKS:
- hydra, john, hashcat - Password cracking
- cewl - Wordlist generation

WEB TESTING:
- curl, wget - HTTP clients
- caido - Web security toolkit
- burpsuite, owasp-zap - Web proxies
- browser-harness - Browser automation with stealth

SMART CONTRACT:
- slither, mythril - Static analysis
- echidna - Fuzzing
- foundry - Testing framework

LLM SECURITY:
- Prompt injection testing
- System prompt extraction
- Vector embedding attacks

=== OWASP KNOWLEDGE ===

You have access to comprehensive OWASP references:
- OWASP Top 10 Web (2021) - A01-A10
- OWASP API Security Top 10 (2023) - API1-API10
- OWASP Top 10 for LLM (2025) - LLM01-LLM10
- OWASP Smart Contract Top 10 (2026) - SC01-SC10

=== METHODOLOGY ===

Follow standard pentesting methodology:
1. Information Gathering (recon)
2. Vulnerability Assessment
3. Exploitation
4. Documentation

RULES:
- Only test targets within explicit scope
- Get confirmation before destructive tests
- Document all findings with evidence
- Explain your methodology as you work
- Use safe, non-destructive techniques first

=== MEMORY SYSTEM ===

You have access to a sophisticated memory system:
1. Current engagement (target, phase, scope)
2. All findings discovered so far
3. Tool history (what you've already run)
4. Cross-engagement memories
5. Skills specific to the task
6. Complete OWASP knowledge base
7. Security tools reference

Always reference memory when responding.

=== OUTPUT FORMAT ===

For each finding, provide:
- Title
- Severity (Critical/High/Medium/Low/Info)
- Description
- Impact
- Proof of Concept
- Remediation

Start every engagement by checking memory for context."""


def start_opencode_server():
    global OPENCODE_RUNNING
    if OPENCODE_RUNNING:
        return True
    
    env = os.environ.copy()
    if OPENCODE_PASSWORD:
        env['OPENCODE_SERVER_PASSWORD'] = OPENCODE_PASSWORD
    
    try:
        proc = subprocess.Popen(
            ['opencode', 'serve', '--hostname', '0.0.0.0', '--port', '4096'],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        for _ in range(30):
            try:
                resp = requests.get(f"{OPENCODE_SERVER}/health", timeout=1)
                if resp.status_code == 200:
                    OPENCODE_RUNNING = True
                    print("✅ OpenCode server started")
                    return True
            except:
                pass
            time.sleep(1)
        
        return False
    except FileNotFoundError:
        print("⚠️ OpenCode not installed")
        return False


def send_prompt(session_path: str, prompt: str):
    auth = ('', OPENCODE_PASSWORD) if OPENCODE_PASSWORD else None
    
    try:
        resp = requests.post(
            f"{OPENCODE_SERVER}/session/{session_path}/prompt",
            json={
                'body': {
                    'role': 'user',
                    'parts': [{'type': 'text', 'text': prompt}]
                },
                'noReply': False
            },
            auth=auth,
            timeout=300,
            stream=True
        )
        
        if resp.status_code != 200:
            return f"Error: {resp.status_code}", False
        
        full_response = ""
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if 'message' in data:
                        msg = data['message']
                        if 'parts' in msg:
                            for part in msg['parts']:
                                if part.get('type') == 'text':
                                    full_response += part.get('text', '')
                        elif 'content' in msg:
                            full_response += msg.get('content', '')
                except:
                    pass
        
        return full_response if full_response else "No response", True
    except Exception as e:
        return f"Error: {str(e)}", False


class SecAIOS:
    """
    SecAIOS Agent with Enhanced Memory (Agent Zero-like)
    """
    
    def __init__(self):
        self.running = False
        self.user_sessions = {}
    
    def start_server(self):
        if not self.running:
            self.running = True
            thread = Thread(target=start_opencode_server, daemon=True)
            thread.start()
            time.sleep(2)
            return True
        return True
    
    def _ensure_session(self, user_id: str) -> str:
        """Ensure user has an OpenCode session"""
        auth = ('', OPENCODE_PASSWORD) if OPENCODE_PASSWORD else None
        
        if user_id not in self.user_sessions:
            try:
                resp = requests.post(
                    f"{OPENCODE_SERVER}/session/create",
                    json={
                        'body': {
                            'role': 'system',
                            'parts': [{'type': 'text', 'text': PENTEST_SYSTEM_PROMPT}]
                        },
                        'path': str(user_id),
                        'title': f'SecAIOS-{user_id}'
                    },
                    auth=auth,
                    timeout=30
                )
                
                if resp.status_code == 200:
                    self.user_sessions[user_id] = str(user_id)
                else:
                    return str(user_id)
            except:
                pass
        
        return self.user_sessions.get(user_id, str(user_id))
    
    def chat(self, user_id: int, message: str) -> str:
        """Send a message with full memory context"""
        
        user_id_str = str(user_id)
        
        # Build comprehensive context from enhanced memory
        context = MEMORY.build_context_prompt(
            user_id_str,
            include_skills=True,
            include_knowledge=True,
            include_web_search=True,
            query=message
        )
        
        # Build enhanced prompt with all memory layers
        enhanced_prompt = f"""
=== SECAIOS MEMORY CONTEXT ===
{context}

=== NEW USER REQUEST ===
{message}

Instructions:
1. First, review the memory context above - this tells you:
   - Current engagement status (target, phase)
   - What you've already done
   - Findings discovered so far
   - Tools you've used
   - Any relevant skills for this task

2. Execute the requested task using appropriate tools

3. After completing tasks, ALWAYS use memory to:
   - Record any new findings (severity: critical/high/medium/low)
   - Track tool usage
   - Update engagement phase if changed
   - Add important notes to cross-engagement memory

4. Provide comprehensive response with findings and next steps
"""
        
        session_path = self._ensure_session(user_id_str)
        
        # Record this interaction in memory
        MEMORY.record_episode(user_id_str, 'user_message', message[:500])
        
        response, success = send_prompt(session_path, enhanced_prompt)
        
        if success:
            MEMORY.record_episode(user_id_str, 'assistant_response', 
                                response[:500], outcome='success')
        else:
            MEMORY.record_episode(user_id_str, 'error', response[:200], 
                                outcome='error')
        
        return response


SECAIOS = SecAIOS()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = "Big Pickle (Cloud)" if current_model == DEFAULT_MODEL else "Ollama (Local)"
    await update.message.reply_text(
        f"🎯 *SecAIOS - Enhanced Memory*\n\n"
        f"Current model: *{current}*\n\n"
        "Your AI-powered pentesting assistant.\n\n"
        "Memory System:\n"
        "• Working Memory - Current engagement\n"
        "• Semantic Memory - Facts & findings\n"
        "• Episodic Memory - Activity history\n"
        "• Cross-Engagement - Persistent knowledge\n"
        "• Skills - Dynamic tool prompts\n"
        "• Knowledge Base - OWASP, payloads\n\n"
        "Commands:\n"
        "/start - This message\n"
        "/model - Switch model (big-pickle/ollama)\n"
        "/scope <target> - Start engagement\n"
        "/status - Current engagement\n"
        "/phase <phase> - Set phase\n"
        "/findings - All vulnerabilities\n"
        "/help - Help",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *SecAIOS Commands*\n\n"
        "*Engagement:*\n"
        "/scope <target> - New engagement\n"
        "/status - Current status\n"
        "/phase <phase> - Set phase\n\n"
        "*Memory:*\n"
        "/findings - List findings\n"
        "/history - Recent activity\n"
        "/memory <query> - Search\n"
        "/forget - Clear memory\n\n"
        "*Skills:*\n"
        "/skills - Show skills\n\n"
        "Just chat naturally!",
        parse_mode='Markdown'
    )

async def scope_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /scope <target>")
        return
    
    target = ' '.join(context.args)
    user_id = str(update.effective_user.id)
    
    MEMORY.start_engagement(user_id, target)
    
    await update.message.reply_text(
        f"✅ *Engagement Started*\n\n"
        f"Target: `{target}`\n"
        f"Phase: Reconnaissance\n\n"
        f"Memory initialized. What's the first scan?",
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    engagement = MEMORY.get_engagement(user_id)
    
    if not engagement:
        await update.message.reply_text("No active engagement. /scope <target> to start.")
        return
    
    findings = MEMORY.get_findings(user_id)
    tool_history = MEMORY.get_tool_history(user_id, limit=5)
    
    status_text = (
        f"📊 *Current Engagement*\n\n"
        f"Target: `{engagement['target']}`\n"
        f"Phase: {engagement['phase']}\n"
        f"Findings: {len(findings)}\n"
        f"Tools Used: {len(tool_history)}\n"
        f"Last Active: {engagement['last_active'][:19]}"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def findings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    findings = MEMORY.get_findings(user_id)
    
    if not findings:
        await update.message.reply_text("No findings yet.")
        return
    
    response = "🔍 *Findings*\n\n"
    critical = [f for f in findings if f['severity'] == 'critical']
    high = [f for f in findings if f['severity'] == 'high']
    
    if critical:
        response += f"🔴 Critical: {len(critical)}\n"
    if high:
        response += f"🟠 High: {len(high)}\n"
    
    for f in findings[:10]:
        emoji = "🔴" if f['severity'] == 'critical' else "🟠" if f['severity'] == 'high' else "🟡"
        response += f"{emoji} {f['title']}\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    episodes = MEMORY.get_recent_episodes(user_id, limit=15)
    
    if not episodes:
        await update.message.reply_text("No recent activity.")
        return
    
    response = "📜 *Recent Activity*\n\n"
    for ep in reversed(episodes):
        ts = ep['timestamp'][:19].replace('T', ' ')
        response += f"• {ts}: {ep['content'][:80]}\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /memory <search query>")
        return
    
    query = ' '.join(context.args)
    user_id = str(update.effective_user.id)
    
    results = MEMORY.semantic_search(query, k=5)
    
    if not results:
        await update.message.reply_text(f"No memories found for: {query}")
        return
    
    response = f"🧠 *Memory Search: {query}*\n\n"
    for r in results:
        response += f"• {r['content'][:150]}...\n"
        response += f"  (similarity: {r.get('distance', 'N/A')})\n\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from skills.manager import SKILLS_MANAGER
    
    skills_list = SKILLS_MANAGER.list_skills()
    
    response = "🔧 *Available Skills*\n\n"
    for s in skills_list:
        response += f"*{s['name']}*\n{s['description'][:80]}...\n\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def phase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /phase <recon|assessment|exploitation|documentation>")
        return
    
    phase = context.args[0].lower()
    valid_phases = ['recon', 'assessment', 'exploitation', 'documentation']
    
    if phase not in valid_phases:
        await update.message.reply_text(f"Invalid phase. Use: {', '.join(valid_phases)}")
        return
    
    user_id = str(update.effective_user.id)
    MEMORY.update_engagement(user_id, phase=phase)
    
    await update.message.reply_text(f"✅ Phase updated to: *{phase}*", parse_mode='Markdown')

async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switch between default (Big Pickle) and sensitive (Ollama) model"""
    global current_model
    
    if not context.args:
        current = "🔒 Local (Ollama)" if current_model.startswith('ollama') else "☁️ Cloud (Big Pickle)"
        await update.message.reply_text(
            f"Current model: *{current}*\n\n"
            f"Available models:\n"
            f"• `big-pickle` - OpenCode's free model (faster)\n"
            f"• `ollama` - Local Ollama (100% private)\n\n"
            f"Usage: `/model ollama` or `/model big-pickle`",
            parse_mode='Markdown'
        )
        return
    
    model_choice = context.args[0].lower()
    
    if model_choice in ['ollama', 'local', 'sensitive', 'private']:
        # Start Ollama if not running
        try:
            requests.get(f"{OLLAMA_BASE_URL}/", timeout=2)
        except:
            # Start Ollama in background
            subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)
        
        current_model = SENSITIVE_MODEL
        await update.message.reply_text(
            "✅ Switched to *Ollama (Local)* model\n\n"
            "🔒 All conversations are now 100% local and private.\n"
            "Data never leaves your machine.",
            parse_mode='Markdown'
        )
    
    elif model_choice in ['big-pickle', 'cloud', 'default', 'opencode']:
        current_model = DEFAULT_MODEL
        await update.message.reply_text(
            "✅ Switched to *Big Pickle (Cloud)* model\n\n"
            "☁️ Using OpenCode's default model - faster but data may be used for training.",
            parse_mode='Markdown'
        )
    
    else:
        await update.message.reply_text(
            "Unknown model. Use:\n"
            "• `/model ollama` - Local private model\n"
            "• `/model big-pickle` - Cloud model"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    await update.message.chat.send_action('typing')
    
    response = SECAIOS.chat(user_id, text)
    
    if len(response) > 4000:
        response = response[:4000] + "\n\n... (truncated)"
    
    await update.message.reply_text(response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

def main():
    print("🎯 Starting SecAIOS with Enhanced Memory...")
    print("Memory: Working + Semantic + Episodic + Vector + Cross-Engagement")
    
    if not SECAIOS.start_server():
        print("⚠️ Warning: OpenCode not available")
    
    # Initialize memory
    _ = MEMORY
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("scope", scope_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("findings", findings_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("memory", memory_command))
    app.add_handler(CommandHandler("skills", skills_command))
    app.add_handler(CommandHandler("phase", phase_command))
    app.add_handler(CommandHandler("model", model_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.add_error_handler(error_handler)
    
    print("✅ SecAIOS running with full memory!")
    app.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()