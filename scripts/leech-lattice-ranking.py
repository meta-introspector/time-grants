#!/usr/bin/env python3
"""Rank potential repos using Leech lattice model (24-dimensional)"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import math

def load_data():
    """Load all collected data"""
    data_dir = Path("/mnt/data1/time-2026/02-february/24")
    
    # Load fork/branch analysis
    fork_files = sorted(data_dir.glob("FORK_BRANCH_ANALYSIS_*.json"))
    fork_data = json.loads(fork_files[-1].read_text()) if fork_files else {"repos": []}
    
    # Load contributor repos
    contrib_files = sorted(data_dir.glob("CONTRIBUTOR_REPOS_*.json"))
    contrib_data = json.loads(contrib_files[-1].read_text()) if contrib_files else {"contributors": {}}
    
    return fork_data, contrib_data

def compute_leech_coordinates(repo_data):
    """Map repo to 24-dimensional Leech lattice coordinates"""
    # 24 dimensions based on Monster Group properties
    coords = [0] * 24
    
    # Dimension 0-2: Branch activity (mod 3)
    branch_count = repo_data.get("branch_count", 0)
    coords[0] = branch_count % 3
    coords[1] = (branch_count // 3) % 3
    coords[2] = (branch_count // 9) % 3
    
    # Dimension 3-5: Star count (if available)
    stars = repo_data.get("stargazerCount", 0)
    coords[3] = stars % 3
    coords[4] = (stars // 3) % 3
    coords[5] = (stars // 9) % 3
    
    # Dimension 6-8: Name hash (for uniqueness)
    name = repo_data.get("name", "")
    name_hash = sum(ord(c) for c in name)
    coords[6] = name_hash % 3
    coords[7] = (name_hash // 3) % 3
    coords[8] = (name_hash // 9) % 3
    
    # Dimension 9-11: URL hash
    url = repo_data.get("url", repo_data.get("remote", ""))
    url_hash = sum(ord(c) for c in url)
    coords[9] = url_hash % 3
    coords[10] = (url_hash // 3) % 3
    coords[11] = (url_hash // 9) % 3
    
    # Dimensions 12-23: Reserved for future metrics
    # (contributor count, fork count, recent activity, etc.)
    
    return coords

def leech_distance(coords1, coords2):
    """Compute distance in Leech lattice (simplified)"""
    # Euclidean distance in 24D space
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(coords1, coords2)))

def rank_repos(fork_data, contrib_data):
    """Rank repos using Leech lattice clustering"""
    
    # Collect all repos
    all_repos = []
    
    # From fork/branch analysis
    for repo in fork_data.get("repos", []):
        if "error" not in repo:
            all_repos.append({
                "source": "grants",
                "name": repo["name"],
                "url": repo.get("remote", ""),
                "branch_count": repo.get("branch_count", 0),
                "type": "grant"
            })
    
    # From contributor repos
    for username, data in contrib_data.get("contributors", {}).items():
        for repo in data.get("repos", []):
            all_repos.append({
                "source": f"contributor:{username}",
                "name": repo["name"],
                "url": repo["url"],
                "stargazerCount": repo.get("stargazerCount", 0),
                "type": "contributor"
            })
    
    # Compute Leech coordinates for each repo
    print(f"📐 Computing Leech lattice coordinates for {len(all_repos)} repos...")
    
    for repo in all_repos:
        repo["leech_coords"] = compute_leech_coordinates(repo)
    
    # Find centroid of grant repos (our current focus)
    grant_repos = [r for r in all_repos if r["type"] == "grant"]
    if grant_repos:
        centroid = [
            sum(r["leech_coords"][i] for r in grant_repos) / len(grant_repos)
            for i in range(24)
        ]
    else:
        centroid = [0] * 24
    
    # Rank contributor repos by distance to grant centroid
    contributor_repos = [r for r in all_repos if r["type"] == "contributor"]
    
    for repo in contributor_repos:
        repo["distance_to_grants"] = leech_distance(repo["leech_coords"], centroid)
    
    # Sort by distance (closer = more relevant)
    ranked = sorted(contributor_repos, key=lambda r: r["distance_to_grants"])
    
    return ranked, centroid

def main():
    output_dir = Path("/mnt/data1/time-2026/02-february/24")
    
    print("🔮 Leech Lattice Repo Ranking")
    print("=" * 60)
    
    # Load data
    fork_data, contrib_data = load_data()
    
    # Rank repos
    ranked, centroid = rank_repos(fork_data, contrib_data)
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": "Leech Lattice (24-dimensional)",
        "total_repos_analyzed": len(ranked),
        "centroid": centroid,
        "top_recommendations": [
            {
                "rank": i + 1,
                "name": repo["name"],
                "url": repo["url"],
                "source": repo["source"],
                "distance": repo["distance_to_grants"],
                "stars": repo.get("stargazerCount", 0)
            }
            for i, repo in enumerate(ranked[:50])
        ]
    }
    
    # Save report
    output_file = output_dir / f"LEECH_LATTICE_RANKING_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.write_text(json.dumps(report, indent=2))
    
    print(f"\n✅ Analysis complete")
    print(f"📊 Repos analyzed: {len(ranked)}")
    print(f"📁 Report: {output_file}")
    
    # Show top 10 recommendations
    print(f"\n🏆 Top 10 Recommended Repos (closest to grant centroid):")
    for i, repo in enumerate(ranked[:10], 1):
        print(f"  {i}. {repo['name']}")
        print(f"     Distance: {repo['distance_to_grants']:.2f}")
        print(f"     Source: {repo['source']}")
        print(f"     URL: {repo['url']}")

if __name__ == "__main__":
    main()
