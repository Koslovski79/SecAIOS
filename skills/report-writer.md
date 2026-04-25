# REPORT WRITER

Reporting phase - Professional documentation of findings.

## Phase: 7

## Output Formats

- Markdown (default)
- HTML
- PDF (via pandoc)

## Report Structure

```markdown
# PENTEST REPORT: <TARGET>

## Executive Summary
[Brief overview]
[Risk rating]
[Key recommendations]

## Scope
- In-scope: [targets]
- Out-of-scope: [targets]
- Rules of engagement

## Methodology
[Phases executed]

## Findings

### Finding 01: <Title>
- Severity: Critical
- CVSS: 9.8
- Description: [what it is]
- Impact: [business impact]
- POC: [code/commands]
- Remediation: [fix]
- References: [CVE links]

## Recommendations
1. [Priority fix]
2. [Priority fix]
3. [Priority fix]

## Appendix
- Tool versions
- Raw output
- Screenshots
```

## Requirements

- Every finding has evidence
- Actionable remediation
- Business impact context
- Professional tone

## Key Principles

1. Be factual and objective
2. Document everything
3. Prioritize by severity
4. Provide actionable fixes