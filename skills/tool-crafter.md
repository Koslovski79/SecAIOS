# TOOL CRAFTER

Dynamic tool creation - Create custom tools on-the-fly.

## Concept

Build custom tools during conversation for specific tasks.

## Syntax

### Create Tool
```
/tool create <name>
  description: "<description>"
  parameters:
    - <param>: <type>
  command: <command with $params>
```

### Example
```
/tool create quick-scan
  description: "Quick port scanner for fast discovery"
  parameters:
    - target: string
    - ports: string (default: "22,80,443,3389")
  command: nmap -p$ports --open -T4 $target
```

## Available

After creation:
```
quick-scan(target="target.com", ports="22,80,443")
```

## Tool Library

### Save to Library
```
/tool save <name>
```
Persists tool for future sessions

### List Tools
```
/tool list
```

### Delete Tool
```
/tool delete <name>
```

## Use Cases

- Target-specific scans
- Custom enumeration
- Format converters
- Output parsers
- Automation scripts

## Key Principles

1. Keep tools focused
2. Document parameters
3. Test before saving
4. Share useful tools