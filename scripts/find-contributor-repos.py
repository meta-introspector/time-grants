#!/usr/bin/env python3
"""Find all other repos by grant contributors using GitHub API"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def get_contributors_from_grants():
    """Extract all contributors from grant repos"""
    grants_dir = Path("/mnt/data1/nix/time/2024/08/01/time-grants/2024/08/01")
    contributors = {}
    
    print("🔍 Extracting contributors from grant repos...")
    
    for repo_dir in grants_dir.iterdir():
        if repo_dir.is_dir() and (repo_dir / ".git").exists():
            try:
                result = subprocess.run(
                    ["git", "log", "--format=%ae|%an", "--max-count=50"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                for line in result.stdout.strip().split('\n'):
                    if '|' in line and '@' in line:
                        email, name = line.split('|', 1)
                        # Extract GitHub username from email if possible
                        if 'users.noreply.github.com' in email:
                            username = email.split('+')[1].split('@')[0] if '+' in email else None
                            if username:
                                contributors[username] = name
                        elif 'github.com' not in email and 'noreply' not in email:
                            # Real email - try to find GitHub username via gh CLI
                            contributors[email] = name
            except:
                pass
    
    return contributors

def find_user_repos(username):
    """Find all repos for a GitHub user"""
    try:
        result = subprocess.run(
            ["gh", "repo", "list", username, "--limit", "100", "--json", "name,url,stargazerCount,pushedAt"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        pass
    
    return []

def main():
    output_dir = Path("/mnt/data1/time-2026/02-february/24")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get contributors
    contributors = get_contributors_from_grants()
    print(f"✅ Found {len(contributors)} unique contributors")
    
    # Find their other repos
    print(f"\n🔎 Finding other repos by these contributors...")
    
    all_repos = defaultdict(list)
    processed = 0
    
    for username, name in list(contributors.items())[:50]:  # Limit to first 50 to avoid rate limits
        print(f"  {username} ({name})...")
        repos = find_user_repos(username)
        
        if repos:
            all_repos[username] = repos
            processed += 1
            print(f"    Found {len(repos)} repos")
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_contributors": len(contributors),
        "contributors_processed": processed,
        "total_repos_found": sum(len(repos) for repos in all_repos.values()),
        "contributors": {
            username: {
                "name": contributors.get(username, "Unknown"),
                "repo_count": len(repos),
                "repos": repos
            }
            for username, repos in all_repos.items()
        }
    }
    
    # Save report
    output_file = output_dir / f"CONTRIBUTOR_REPOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.write_text(json.dumps(report, indent=2))
    
    print(f"\n✅ Analysis complete")
    print(f"📊 Contributors processed: {processed}")
    print(f"📦 Total repos found: {report['total_repos_found']}")
    print(f"📁 Report: {output_file}")
    
    # Show top contributors by repo count
    top = sorted(all_repos.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    print(f"\n🏆 Top contributors by repo count:")
    for username, repos in top:
        print(f"  {username}: {len(repos)} repos")

if __name__ == "__main__":
    main()
