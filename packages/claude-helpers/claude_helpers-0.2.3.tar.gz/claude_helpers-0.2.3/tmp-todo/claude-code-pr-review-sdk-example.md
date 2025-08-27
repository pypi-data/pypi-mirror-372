# Example from Claude Code SDK Docs

## Automated security review

```python
import subprocess
import asyncio
import json
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

async def audit_pr(pr_number: int):
    """Security audit agent for pull requests with streaming feedback"""
    # Get PR diff
    pr_diff = subprocess.check_output(
        ["gh", "pr", "diff", str(pr_number)], 
        text=True
    )
    
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="You are a security engineer. Review this PR for vulnerabilities, insecure patterns, and compliance issues.",
            max_turns=3,
            allowed_tools=["Read", "Grep", "WebSearch"]
        )
    ) as client:
        print(f"🔍 Auditing PR #{pr_number}\n")
        await client.query(pr_diff)
        
        findings = []
        async for message in client.receive_response():
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        # Stream findings as they're discovered
                        print(block.text, end='', flush=True)
                        findings.append(block.text)
            
            if type(message).__name__ == "ResultMessage":
                return {
                    'pr_number': pr_number,
                    'findings': ''.join(findings),
                    'metadata': {
                        'cost': message.total_cost_usd,
                        'duration': message.duration_ms,
                        'severity': 'high' if 'vulnerability' in ''.join(findings).lower() else 'medium'
                    }
                }

# Usage
report = await audit_pr(123)
print(f"\n\nAudit complete. Severity: {report['metadata']['severity']}")
print(json.dumps(report, indent=2))
```