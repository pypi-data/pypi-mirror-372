#!/usr/bin/env python3
"""Analyze what agent sees with pagination."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from claude_helpers.memory_bank import mcp_focus

def analyze_what_agent_sees():
    """Analyze exactly what the agent sees when calling get-pm-focus."""
    
    print("=" * 80)
    print("ANALYZING WHAT AGENT SEES WITH PAGINATION")
    print("=" * 80)
    
    # Get the function
    get_pm_focus_fn = mcp_focus.get_pm_focus.fn
    
    # Get page 1
    result1 = get_pm_focus_fn("02-alpha", "01-modus-id", page=1)
    
    print("\n📄 PAGE 1 RESPONSE STRUCTURE:")
    print("-" * 40)
    
    # What keys does the response have?
    print("Keys in response:")
    for key in result1.keys():
        if key == "content":
            print(f"  - {key}: {len(result1[key])} chars")
            # Check first and last lines of content
            lines = result1[key].split('\n')
            print(f"    First line: {lines[0][:80] if lines else 'EMPTY'}")
            print(f"    Last line: {lines[-1][:80] if lines and lines[-1] else 'EMPTY'}")
        elif key == "pagination":
            print(f"  - {key}:")
            for k, v in result1[key].items():
                print(f"      {k}: {v}")
        else:
            print(f"  - {key}: {result1[key]}")
    
    # What would the agent see?
    print("\n🤖 WHAT AGENT SEES:")
    print("-" * 40)
    
    # The agent would receive this as JSON from MCP
    json_response = json.dumps(result1)
    print(f"Total JSON size: {len(json_response)} chars ({len(json_response)/4:.0f} tokens)")
    
    # The agent would parse it and see:
    content = result1.get("content", "")
    pagination = result1.get("pagination", {})
    
    print(f"\nAgent sees content: {len(content)} chars")
    print(f"Agent sees pagination.has_more: {pagination.get('has_more')}")
    print(f"Agent sees pagination.next_page_hint: {pagination.get('next_page_hint')}")
    
    # But does the agent notice pagination?
    print("\n⚠️  PROBLEM ANALYSIS:")
    print("-" * 40)
    
    # Check if pagination info is visible in content
    if "has_more" in content or "page" in content.lower():
        print("✅ Pagination info IS in the content itself")
    else:
        print("❌ Pagination info is NOT in the content itself")
        print("   Agent must check the 'pagination' key separately!")
    
    # Check if there's any hint in the content about more pages
    if "продолжение следует" in content.lower() or "continued" in content.lower():
        print("✅ Content has continuation hint")
    else:
        print("❌ No continuation hint in content")
    
    print("\n💡 SOLUTION IDEAS:")
    print("-" * 40)
    print("1. Add header/footer to content itself showing page info")
    print("2. Add '... [Page 1 of 2, continue with page=2]' at the end")
    print("3. Add clear markers in content: '=== PAGE 1 OF 2 ===' at start/end")
    
    # Get page 2 to see the problem
    if pagination.get('has_more'):
        print("\n📄 PAGE 2 ANALYSIS:")
        print("-" * 40)
        result2 = get_pm_focus_fn("02-alpha", "01-modus-id", page=2)
        content2 = result2.get("content", "")
        
        # Check start of page 2
        lines2 = content2.split('\n')
        print(f"Page 2 starts with: {lines2[0][:80] if lines2 else 'EMPTY'}")
        
        # Does it show it's page 2?
        if "page 2" in content2.lower() or "страница 2" in content2.lower():
            print("✅ Page 2 identifies itself as page 2")
        else:
            print("❌ Page 2 does NOT identify itself as page 2")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_what_agent_sees()