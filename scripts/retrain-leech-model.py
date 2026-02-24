#!/usr/bin/env python3
"""Retrain Leech lattice model with all data including our proofs"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import math

def collect_all_repos():
    """Collect all repos including new submodules and our proofs"""
    grants_dir = Path("/mnt/data1/nix/time/2024/08/01/time-grants")
    
    all_repos = []
    
    # Scan all submodule directories
    for year_dir in ["2024/08/01", "2026/02/24"]:
        full_dir = grants_dir / year_dir
        if not full_dir.exists():
            continue
        
        for repo_dir in full_dir.iterdir():
            if repo_dir.is_dir() and (repo_dir / ".git").exists():
                # Get repo info
                try:
                    # Branch count
                    result = subprocess.run(
                        ["git", "branch", "-a"],
                        cwd=repo_dir,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    branch_count = len([b for b in result.stdout.split('\n') if b.strip()])
                    
                    # Commit count (as activity metric)
                    result = subprocess.run(
                        ["git", "rev-list", "--count", "HEAD"],
                        cwd=repo_dir,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    commit_count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
                    
                    # Check for proof files
                    has_proofs = any([
                        (repo_dir / "ai-life-uucp.py").exists(),
                        (repo_dir / "flake.nix").exists(),
                        (repo_dir / "default.nix").exists(),
                        (repo_dir / "Cargo.toml").exists()
                    ])
                    
                    all_repos.append({
                        "name": repo_dir.name,
                        "path": str(repo_dir),
                        "branch_count": branch_count,
                        "commit_count": commit_count,
                        "has_proofs": has_proofs,
                        "is_our_repo": repo_dir.name in ["osm-planet-torrent", "monster-osm-quest", "cicadia71"]
                    })
                except:
                    pass
    
    return all_repos

def compute_enhanced_coords(repo):
    """Enhanced 24D coordinates including proof metrics"""
    coords = [0] * 24
    
    # Dims 0-2: Branch count
    bc = repo["branch_count"]
    coords[0] = bc % 3
    coords[1] = (bc // 3) % 3
    coords[2] = (bc // 9) % 3
    
    # Dims 3-5: Commit count (activity)
    cc = repo["commit_count"]
    coords[3] = cc % 3
    coords[4] = (cc // 3) % 3
    coords[5] = (cc // 9) % 3
    
    # Dims 6-8: Name hash
    name_hash = sum(ord(c) for c in repo["name"])
    coords[6] = name_hash % 3
    coords[7] = (name_hash // 3) % 3
    coords[8] = (name_hash // 9) % 3
    
    # Dims 9-11: Proof indicators
    coords[9] = 2 if repo["has_proofs"] else 0
    coords[10] = 2 if repo["is_our_repo"] else 0
    coords[11] = 2 if "grant" in repo["name"].lower() else 0
    
    # Dims 12-23: Reserved for future metrics
    
    return coords

def leech_distance(c1, c2):
    """Euclidean distance in 24D"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def main():
    output_dir = Path("/mnt/data1/time-2026/02-february/24")
    
    print("🔮 Retraining Leech Lattice Model")
    print("=" * 60)
    
    # Collect all repos
    print("📂 Collecting all repos...")
    all_repos = collect_all_repos()
    print(f"✅ Found {len(all_repos)} repos")
    
    # Compute coordinates
    print("📐 Computing enhanced 24D coordinates...")
    for repo in all_repos:
        repo["coords"] = compute_enhanced_coords(repo)
    
    # Find centroid of grant-related repos
    grant_repos = [r for r in all_repos if "grant" in r["name"].lower() or r["has_proofs"]]
    print(f"🎯 Grant/proof repos: {len(grant_repos)}")
    
    if grant_repos:
        centroid = [
            sum(r["coords"][i] for r in grant_repos) / len(grant_repos)
            for i in range(24)
        ]
    else:
        centroid = [0] * 24
    
    # Rank all repos by distance to centroid
    for repo in all_repos:
        repo["distance"] = leech_distance(repo["coords"], centroid)
    
    ranked = sorted(all_repos, key=lambda r: r["distance"])
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": "Leech Lattice v2 (Enhanced with Proofs)",
        "total_repos": len(all_repos),
        "grant_repos": len(grant_repos),
        "centroid": centroid,
        "top_50": [
            {
                "rank": i + 1,
                "name": r["name"],
                "distance": r["distance"],
                "branches": r["branch_count"],
                "commits": r["commit_count"],
                "has_proofs": r["has_proofs"],
                "is_ours": r["is_our_repo"]
            }
            for i, r in enumerate(ranked[:50])
        ]
    }
    
    # Save
    output_file = output_dir / f"LEECH_LATTICE_V2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.write_text(json.dumps(report, indent=2))
    
    print(f"\n✅ Model retrained")
    print(f"📊 Total repos: {len(all_repos)}")
    print(f"🎯 Grant/proof repos: {len(grant_repos)}")
    print(f"📁 Report: {output_file}")
    
    # Show top 10
    print(f"\n🏆 Top 10 (closest to grant/proof centroid):")
    for i, r in enumerate(ranked[:10], 1):
        proof_marker = " 🔬" if r["has_proofs"] else ""
        our_marker = " ⭐" if r["is_our_repo"] else ""
        print(f"  {i}. {r['name']}{proof_marker}{our_marker}")
        print(f"     Distance: {r['distance']:.2f} | Branches: {r['branch_count']} | Commits: {r['commit_count']}")

if __name__ == "__main__":
    main()
