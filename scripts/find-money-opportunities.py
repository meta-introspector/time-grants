#!/usr/bin/env python3
"""Find best money-making opportunities from grant repos"""

import json
from pathlib import Path
from collections import defaultdict

def score_opportunity(repo):
    """Score repo for money-making potential"""
    score = 0
    signals = []
    
    # High issue count = active funding
    issues = repo.get("issue_count", 0)
    if issues > 50:
        score += 50
        signals.append(f"{issues} issues (very active)")
    elif issues > 20:
        score += 30
        signals.append(f"{issues} issues (active)")
    elif issues > 5:
        score += 10
        signals.append(f"{issues} issues")
    
    # Check issue labels for money signals
    for issue in repo.get("issues", []):
        labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
        title = issue.get("title", "").lower()
        
        # Bounty/funding signals
        if any(x in labels for x in ["bounty", "funding", "grant", "reward", "paid"]):
            score += 20
            signals.append(f"💰 Bounty issue: {issue['title'][:50]}")
        
        # Help wanted = opportunity
        if any(x in labels for x in ["help wanted", "good first issue", "hacktoberfest"]):
            score += 5
            signals.append(f"🎯 Help wanted: {issue['title'][:50]}")
        
        # Money keywords in title
        if any(x in title for x in ["bounty", "$", "reward", "prize", "grant", "funding"]):
            score += 15
            signals.append(f"💵 Money keyword: {issue['title'][:50]}")
    
    # Active development = more opportunities
    branches = repo.get("branch_count", 0)
    if branches > 20:
        score += 10
        signals.append(f"{branches} branches (very active)")
    
    # Fork count = popular/funded
    fork_count = repo.get("forks", {}).get("count", 0) if isinstance(repo.get("forks"), dict) else 0
    if fork_count > 100:
        score += 20
        signals.append(f"{fork_count} forks (popular)")
    elif fork_count > 50:
        score += 10
        signals.append(f"{fork_count} forks")
    
    return score, signals

def main():
    recon_file = Path("/mnt/data1/time-2026/02-february/24/RECON_COMPLETE_20260224_101537.json")
    data = json.loads(recon_file.read_text())
    
    print("💰 FINDING BEST MONEY-MAKING OPPORTUNITIES")
    print("=" * 70)
    
    # Score all repos
    scored = []
    for repo in data["repos"]:
        if "error" in repo:
            continue
        score, signals = score_opportunity(repo)
        if score > 0:
            scored.append({
                "name": repo["name"],
                "owner_repo": repo.get("owner_repo"),
                "score": score,
                "signals": signals,
                "issues": repo.get("issue_count", 0),
                "branches": repo.get("branch_count", 0)
            })
    
    # Sort by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    # Show top 15
    print(f"\n🏆 TOP 15 MONEY-MAKING OPPORTUNITIES\n")
    for i, opp in enumerate(scored[:15], 1):
        print(f"{i}. {opp['name']} (Score: {opp['score']})")
        print(f"   Repo: {opp['owner_repo']}")
        print(f"   Issues: {opp['issues']}, Branches: {opp['branches']}")
        print(f"   Signals:")
        for sig in opp['signals'][:5]:  # Top 5 signals
            print(f"     • {sig}")
        print()
    
    # Save full report
    output = Path("/mnt/data1/time-2026/02-february/24/MONEY_OPPORTUNITIES_20260224.json")
    output.write_text(json.dumps({
        "timestamp": data["timestamp"],
        "total_analyzed": len(data["repos"]),
        "opportunities_found": len(scored),
        "top_opportunities": scored[:30]
    }, indent=2))
    
    print(f"📊 Full report: {output}")
    print(f"✅ Found {len(scored)} opportunities from {len(data['repos'])} repos")

if __name__ == "__main__":
    main()
