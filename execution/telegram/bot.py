import os
import json
import re
import requests
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from agents.tools import TOOL_SCHEMAS, TOOL_REGISTRY

load_dotenv()

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen3:14b')
DATABASE_PATH = os.environ.get('DATABASE_PATH', './data/aios.db')

MAX_TOOL_CALLS = 5

def load_context():
    context_files = {
        'business': './context/business.md',
        'products': './context/products.md',
        'processes': './context/processes.md',
        'goals': './context/goals.md'
    }
    
    context_parts = ["# Context OS\n"]
    for name, path in context_files.items():
        if os.path.exists(path):
            with open(path, 'r') as f:
                context_parts.append(f"## {name.upper()}\n{f.read()}\n")
    
    return '\n'.join(context_parts)

def load_recent_conversation(user_id, limit=10):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT role, message FROM conversations 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (str(user_id), limit))
    
    messages = cursor.fetchall()
    conn.close()
    
    return list(reversed(messages))

def save_message(user_id, role, message):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (user_id, role, message)
        VALUES (?, ?, ?)
    ''', (str(user_id), role, message))
    
    conn.commit()
    conn.close()

def chat_with_ollama(messages, tools=None):
    payload = {
        'model': OLLAMA_MODEL,
        'messages': messages,
        'stream': False,
    }
    
    if tools:
        payload['tools'] = tools
    
    try:
        response = requests.post(
            f'{OLLAMA_BASE_URL}/api/chat',
            json=payload,
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"HTTP {response.status_code}", 'message': {'content': response.text}}
    except Exception as e:
        return {'error': str(e), 'message': {'content': f"Connection error: {str(e)}"}}

def parse_tool_calls(response_json):
    message = response_json.get('message', {})
    
    tool_calls = message.get('tool_calls', [])
    
    if not tool_calls and 'function_call' in message:
        tool_calls = [message['function_call']]
    
    return tool_calls

def execute_tool_calls(tool_calls):
    results = []
    
    for tool_call in tool_calls:
        if isinstance(tool_call, dict):
            func_name = tool_call.get('function', {}).get('name', '')
            arguments = tool_call.get('function', {}).get('arguments', '{}')
        else:
            continue
        
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except:
                arguments = {}
        
        result = TOOL_REGISTRY.execute_tool(func_name, arguments)
        
        results.append({
            'tool_call_id': tool_call.get('id', 'unknown'),
            'name': func_name,
            'result': result[:3000]
        })
    
    return results

def run_agent(user_id, user_message, context_text):
    system_prompt = f"""You are a professional web application penetration testing assistant. You have access to various security tools to help with assessments.

{context_text}

Your role is to:
1. Help plan and execute penetration tests
2. Run reconnaissance tools (nmap, gobuster, subfinder, etc.)
3. Analyze tool output and identify vulnerabilities
4. Provide exploitation guidance
5. Document findings

AVAILABLE TOOLS:
- run_nmap: Port scanning
- run_nikto: Web vulnerability scanning
- run_gobuster: Directory enumeration
- curl_head: Check HTTP headers
- curl_get: Fetch web pages
- run_subfinder: Subdomain enumeration
- run_whois: Domain information
- check_http_methods: Check HTTP methods allowed
- run_nuclei: Vulnerability scanning

IMPORTANT RULES:
- Only use tools when necessary to gather information
- Never attack targets without explicit scope authorization
- Always explain what you're doing before running tools
- Analyze tool output thoroughly before reporting findings
- Use safe, non-destructive testing methods first

When a user asks you to test something, use the appropriate tools to gather information and analyze results. If they ask about something you need more information on, ask follow-up questions."""

    messages = [{'role': 'system', 'content': system_prompt}]
    
    history = load_recent_conversation(user_id)
    for role, msg in history:
        messages.append({'role': role, 'content': msg})
    
    messages.append({'role': 'user', 'content': user_message})
    
    tool_call_count = 0
    final_response = None
    
    while tool_call_count < MAX_TOOL_CALLS:
        response = chat_with_ollama(messages, TOOL_SCHEMAS)
        
        if 'error' in response:
            return f"Error: {response['error']}"
        
        assistant_message = response.get('message', {})
        content = assistant_message.get('content', '')
        
        tool_calls = parse_tool_calls(response)
        
        if tool_calls:
            tool_call_count += 1
            
            messages.append({'role': 'assistant', 'content': content})
            if content:
                messages.append({'role': 'assistant', 'content': str(tool_calls)})
            
            tool_results = execute_tool_calls(tool_calls)
            
            for tr in tool_results:
                result_msg = f"Tool: {tr['name']}\nResult:\n{tr['result']}"
                messages.append({
                    'role': 'tool',
                    'tool_call_id': tr.get('tool_call_id', 'unknown'),
                    'content': tr['result']
                })
            
            if content.strip():
                final_response = content + "\n\n" + "\n\n".join([f"Executing {tr['name']}..." for tr in tool_results])
            else:
                final_response = "\n\n".join([f"Executing {tr['name']}..." for tr in tool_results])
        else:
            final_response = content
            messages.append({'role': 'assistant', 'content': content})
            break
    
    return final_response or "No response generated"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 *SecAIOS - Cybersecurity AI Assistant*\n\n"
        "Your AI-powered penetration testing companion.\n\n"
        "I can help you with:\n"
        "• Reconnaissance (nmap, gobuster, subfinder)\n"
        "• Vulnerability scanning (nikto, nuclei)\n"
        "• Web analysis (curl, headers, HTTP methods)\n"
        "• Information gathering (whois, DNS)\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/tools - List available tools\n"
        "/scope <target> - Set target scope\n"
        "/help - Show help\n\n"
        "Just tell me what you want to test!",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Available Commands*\n\n"
        "/start - Start the bot\n"
        "/tools - Show available pentesting tools\n"
        "/scope <target> - Define target scope\n"
        "/help - Show this help\n\n"
        "Example queries:\n"
        "• \"Scan example.com for open ports\"\n"
        "• \"Find directories on http://example.com\"\n"
        "• \"What subdomains does example.com have?\"\n"
        "• \"Check HTTP headers on example.com\"",
        parse_mode='Markdown'
    )

async def tools_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tools_list = """
🔧 *Available Tools*

*Reconnaissance:*
• `run_nmap` - Port scanning
• `run_subfinder` - Subdomain enumeration  
• `run_whois` - Domain info

*Web Testing:*
• `run_gobuster` - Directory enumeration
• `run_nikto` - Vulnerability scanning
• `run_nuclei` - Template-based scanning
• `curl_head` - HTTP headers
• `curl_get` - Fetch pages
• `check_http_methods` - Check allowed methods
"""
    await update.message.reply_text(tools_list, parse_mode='Markdown')

async def scope_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /scope <target>")
        return
    
    target = ' '.join(context.args)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO metrics (name, value, unit, category, recorded_at) 
        VALUES (?, ?, ?, ?, ?)
    ''', ('scope_target', target, 'domain', 'scope', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    await update.message.reply_text(f"✅ Target scope set to: `{target}`", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    save_message(user_id, 'user', text)
    
    await update.message.chat.send_action('typing')
    
    context_text = load_context()
    response = run_agent(user_id, text, context_text)
    
    save_message(user_id, 'assistant', response[:4000])
    
    await update.message.reply_text(response[:4000])

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

def main():
    print("🎯 Starting SecAIOS - Cybersecurity AIOS...")
    print(f"Using model: {OLLAMA_MODEL}")
    print(f"Ollama endpoint: {OLLAMA_BASE_URL}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tools", tools_command))
    app.add_handler(CommandHandler("scope", scope_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.add_error_handler(error_handler)
    
    print("✅ Bot started! Press Ctrl+C to stop.")
    app.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()