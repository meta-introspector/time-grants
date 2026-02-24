#!/usr/bin/env python3
"""Collect all forks and branches from all grant repos"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

def get_repo_info(repo_path):
    """Get forks and branches for a repo"""
    try:
        # Get remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        remote_url = result.stdout.strip()
        
        # Get all branches (local and remote)
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        branches = [b.strip().replace('* ', '') for b in result.stdout.split('\n') if b.strip()]
        
        # Try to get fork info from GitHub API if it's a GitHub repo
        forks = []
        if 'github.com' in remote_url:
            # Extract owner/repo from URL
            parts = remote_url.replace('.git', '').split('/')
            if len(parts) >= 2:
                owner_repo = f"{parts[-2]}/{parts[-1]}"
                
                # Use gh CLI if available
                try:
                    result = subprocess.run(
                        ["gh", "repo", "view", owner_repo, "--json", "forkCount,parent"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        forks = {
                            "count": data.get("forkCount", 0),
                            "parent": data.get("parent", {}).get("nameWithOwner")
                        }
                except:
                    pass
        
        return {
            "path": str(repo_path),
            "name": repo_path.name,
            "remote": remote_url,
            "branches": branches,
            "branch_count": len(branches),
            "forks": forks
        }
    except Exception as e:
        return {
            "path": str(repo_path),
            "name": repo_path.name,
            "error": str(e)
        }

def main():
    grants_dir = Path("/mnt/data1/nix/time/2024/08/01/time-grants/2024/08/01")
    output_dir = Path("/mnt/data1/time-2026/02-february/24")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Collecting forks and branches from all grant repos...")
    
    all_repos = []
    
    # Find all git repos
    for item in grants_dir.iterdir():
        if item.is_dir() and (item / ".git").exists():
            print(f"📂 {item.name}...")
            info = get_repo_info(item)
            all_repos.append(info)
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "source_dir": str(grants_dir),
        "total_repos": len(all_repos),
        "total_branches": sum(r.get("branch_count", 0) for r in all_repos),
        "repos": all_repos
    }
    
    # Save report
    output_file = output_dir / f"FORK_BRANCH_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.write_text(json.dumps(report, indent=2))
    
    print(f"\n✅ Analysis complete")
    print(f"📊 Total repos: {len(all_repos)}")
    print(f"🌿 Total branches: {report['total_branches']}")
    print(f"📁 Report: {output_file}")
    
    # Show repos with most branches
    top_repos = sorted(all_repos, key=lambda r: r.get("branch_count", 0), reverse=True)[:10]
    print(f"\n🏆 Top repos by branch count:")
    for repo in top_repos:
        if "error" not in repo:
            print(f"  {repo['name']}: {repo['branch_count']} branches")

if __name__ == "__main__":
    main()
