# CONTINUOUS MONITOR

Continuous monitoring - Scheduled re-scanning and drift detection.

## Overview

Ongoing assessment after initial pentest:
- Scheduled re-scans
- New vulnerability alerts
- Drift detection
- Remediation verification

## Commands

### Create Monitor
```
/monitor create <target> --schedule daily
/monitor create <target> --schedule weekly
```

### List Monitors
```
/monitor list
```

### Check Status
```
/monitor status <target>
```

### Delete Monitor
```
/monitor delete <target>
```

## Schedule Options

| Frequency | Use Case |
|-----------|----------|
| Hourly | Critical assets |
| Daily | Production systems |
| Weekly | Standard assets |
| Monthly | Low priority |

## Alert Levels

| Level | Triggers |
|-------|----------|
| Critical | New RCE, SQLi |
| High | New Auth bypass |
| Medium | New XSS |
| Low | New info disclosure |

## Integration

- Run via cron/jobs
- Store results to knowledge base
- Alert on new vulnerabilities
- Track remediation status

## Key Principles

1. Rescan after patches
2. Alert only on NEW vulns
3. Track drift over time
4. Verify remediation