#!/usr/bin/env python3
"""Find co-repository set from dasl/ and time-grants/ contributors"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def get_contributors(repo_path):
    """Extract contributors from a git repo"""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ae|%an", "--max-count=100"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        contributors = {}
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                email, name = line.split('|', 1)
                contributors[email] = name
        
        return contributors
    except:
        return {}

def find_repos_in_dir(base_dir):
    """Find all git repos in directory"""
    repos = []
    base = Path(base_dir)
    
    if not base.exists():
        return repos
    
    for item in base.rglob('.git'):
        if item.is_dir():
            repo_path = item.parent
            repos.append(repo_path)
    
    return repos

def main():
    dasl_dir = Path("/mnt/data1/time-2026/02-february/22/dasl")
    grants_dir = Path("/mnt/data1/nix/time/2024/08/01/time-grants")
    output_dir = Path("/mnt/data1/time-2026/02-february/24")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Finding co-repository set...")
    
    all_contributors = {}
    repo_contributors = defaultdict(list)
    
    # Scan dasl repos
    print(f"📂 Scanning {dasl_dir}...")
    for repo in find_repos_in_dir(dasl_dir):
        contribs = get_contributors(repo)
        repo_name = repo.name
        for email, name in contribs.items():
            all_contributors[email] = name
            repo_contributors[email].append(f"dasl/{repo_name}")
        print(f"  {repo_name}: {len(contribs)} contributors")
    
    # Scan grants repos
    print(f"📂 Scanning {grants_dir}...")
    for repo in find_repos_in_dir(grants_dir):
        contribs = get_contributors(repo)
        repo_name = repo.name
        for email, name in contribs.items():
            all_contributors[email] = name
            repo_contributors[email].append(f"grants/{repo_name}")
        if len(contribs) > 0:
            print(f"  {repo_name}: {len(contribs)} contributors")
    
    # Find contributors in both
    cross_contributors = {
        email: {
            "name": name,
            "repos": repos
        }
        for email, repos in repo_contributors.items()
        if any('dasl/' in r for r in repos) and any('grants/' in r for r in repos)
    }
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "sources": [str(dasl_dir), str(grants_dir)],
        "total_contributors": len(all_contributors),
        "cross_contributors": len(cross_contributors),
        "top_contributors": [
            {"email": email, "name": name, "repo_count": len(repos)}
            for email, data in sorted(
                repo_contributors.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:20]
            for name, repos in [(all_contributors[email], data)]
        ],
        "cross_contributor_details": cross_contributors
    }
    
    # Save report
    output_file = output_dir / f"CO_REPO_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.write_text(json.dumps(report, indent=2))
    
    print(f"\n✅ Analysis complete")
    print(f"📊 Total contributors: {len(all_contributors)}")
    print(f"🔗 Cross-contributors: {len(cross_contributors)}")
    print(f"📁 Report: {output_file}")
    
    # Show top cross-contributors
    if cross_contributors:
        print(f"\n🌟 Top cross-contributors:")
        for email, data in list(cross_contributors.items())[:10]:
            print(f"  {data['name']} ({email})")
            print(f"    Repos: {len(data['repos'])}")

if __name__ == "__main__":
    main()
