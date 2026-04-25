# SecAIOS - Specification

## Project Overview
- **Name**: SecAIOS (Security AI Operating System)
- **Type**: AI Operating System for Cybersecurity
- **Core Functionality**: AI-powered pentesting assistant with persistent memory and OpenCode agent
- **Target Users**: Penetration testers, security researchers, red teamers

## Architecture (5-Layer)

### Layer 1: Context OS
- `business.md` - Pentester profile
- `products.md` - Services and scope
- `processes.md` - Methodology and commands
- `goals.md` - Certifications, engagements, metrics

### Layer 2: Data OS
- SQLite database
- Engagement tracking
- Findings repository
- Conversation history

### Layer 3: Intelligence Layer
- Tool output analysis
- Finding correlation
- Context building for agent

### Layer 4: Automation Layer
- Cron jobs for scheduled tasks

### Layer 5: Interface Layer
- Telegram bot with OpenCode agent

## Memory System (CRITICAL)

SecAIOS implements a multi-layer memory system to solve the agent forgetting problem:

### 1. Working Memory (Engagement State)
- Current target
- Scope definition
- Current phase (recon, assessment, exploitation, documentation)
- Current task in progress
- Last active timestamp

### 2. Semantic Memory (Core Facts)
- Pentester profile
- Target information
- Methodology preferences
- Tool preferences

### 3. Episodic Memory (History)
- Every interaction recorded
- Tools used
- Outcomes
- Timestamps

### 4. Findings Database
- Structured vulnerability storage
- Severity tracking
- Proof of concept
- Remediation notes

### Context Builder
- Builds comprehensive prompt from all memory layers
- Injected into every agent request
- Ensures agent always knows current state

## Technology Stack
- **Agent**: OpenCode (full tool access)
- **Memory**: SQLite-based custom implementation
- **Interface**: Telegram Bot API

## Agent Capabilities
- Full shell execution
- File read/write
- Tool execution (nmap, gobuster, nikto, nuclei, sqlmap, etc.)
- Memory-aware conversations

## VM Requirements
- **OS**: Ubuntu 22.04 LTS Server
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 100GB+ SSD