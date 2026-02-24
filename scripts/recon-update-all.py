#!/usr/bin/env python3
"""Recon: Update all forks, branches, and issues from grant repos"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

def update_repo(repo_path):
    """Fetch all remotes, branches, and metadata"""
    try:
        # Fetch all remotes
        subprocess.run(["git", "fetch", "--all"], cwd=repo_path, timeout=30, capture_output=True)
        
        # Get all branches
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        branches = [b.strip().replace('* ', '') for b in result.stdout.split('\n') if b.strip()]
        
        # Get remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        remote_url = result.stdout.strip()
        
        # Extract owner/repo from GitHub URL
        owner_repo = None
        if 'github.com' in remote_url:
            parts = remote_url.replace('.git', '').split('/')
            if len(parts) >= 2:
                owner_repo = f"{parts[-2]}/{parts[-1]}"
        
        # Get issues via gh CLI
        issues = []
        if owner_repo:
            try:
                result = subprocess.run(
                    ["gh", "issue", "list", "-R", owner_repo, "--limit", "100", "--json", "number,title,state,labels"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    issues = json.loads(result.stdout)
            except:
                pass
        
        # Get forks via gh CLI
        forks = []
        if owner_repo:
            try:
                result = subprocess.run(
                    ["gh", "repo", "view", owner_repo, "--json", "forkCount,parent"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    fork_data = json.loads(result.stdout)
                    forks = {
                        "count": fork_data.get("forkCount", 0),
                        "parent": fork_data.get("parent", {}).get("nameWithOwner")
                    }
            except:
                pass
        
        return {
            "name": repo_path.name,
            "path": str(repo_path),
            "remote": remote_url,
            "owner_repo": owner_repo,
            "branches": branches,
            "branch_count": len(branches),
            "issues": issues,
            "issue_count": len(issues),
            "forks": forks,
            "updated": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "name": repo_path.name,
            "path": str(repo_path),
            "error": str(e)
        }

def main():
    grants_dir = Path("/mnt/data1/nix/time/2024/08/01/time-grants")
    output_dir = Path("/mnt/data1/time-2026/02-february/24")
    
    print("🔍 RECON: Updating all forks, branches, and issues")
    print("=" * 60)
    
    all_data = []
    
    # Scan all repo directories
    for year_dir in ["2024/08/01", "2026/02/24"]:
        full_dir = grants_dir / year_dir
        if not full_dir.exists():
            continue
        
        for repo_dir in full_dir.iterdir():
            if repo_dir.is_dir() and (repo_dir / ".git").exists():
                print(f"📂 {repo_dir.name}...")
                data = update_repo(repo_dir)
                all_data.append(data)
                
                if "error" not in data:
                    print(f"   ✅ {data['branch_count']} branches, {data['issue_count']} issues")
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "action": "recon",
        "total_repos": len(all_data),
        "total_branches": sum(d.get("branch_count", 0) for d in all_data),
        "total_issues": sum(d.get("issue_count", 0) for d in all_data),
        "repos": all_data
    }
    
    # Save
    output_file = output_dir / f"RECON_COMPLETE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.write_text(json.dumps(report, indent=2))
    
    print(f"\n✅ Recon complete")
    print(f"📊 Repos: {report['total_repos']}")
    print(f"🌿 Branches: {report['total_branches']}")
    print(f"🐛 Issues: {report['total_issues']}")
    print(f"📁 Report: {output_file}")
    
    # Show repos with most issues
    with_issues = [d for d in all_data if d.get("issue_count", 0) > 0]
    top_issues = sorted(with_issues, key=lambda d: d.get("issue_count", 0), reverse=True)[:10]
    
    if top_issues:
        print(f"\n🔥 Top repos by issue count:")
        for repo in top_issues:
            print(f"  {repo['name']}: {repo['issue_count']} issues")

if __name__ == "__main__":
    main()
