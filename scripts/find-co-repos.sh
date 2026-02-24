#!/bin/bash
# Find co-repository set: repos by contributors to dasl/ and time-grants/
# ISO 9001 compliant - reproducible analysis

set -e

DASL_DIR="/mnt/data1/time-2026/02-february/22/dasl"
GRANTS_DIR="/mnt/data1/nix/time/2024/08/01/time-grants"
OUTPUT_DIR="/mnt/data1/time-2026/02-february/24"
REPORT="$OUTPUT_DIR/CO_REPO_ANALYSIS_$(date +%Y%m%d_%H%M%S).json"

mkdir -p "$OUTPUT_DIR"

echo "🔍 Analyzing co-repository set..."
echo "{"
echo "  \"timestamp\": \"$(date -Iseconds)\","
echo "  \"sources\": ["
echo "    \"$DASL_DIR\","
echo "    \"$GRANTS_DIR\""
echo "  ],"
echo "  \"contributors\": {"

# Collect unique contributors from both directories
declare -A contributors

# From dasl submodules
if [ -d "$DASL_DIR" ]; then
    for repo in "$DASL_DIR"/*/.git; do
        if [ -d "$repo" ]; then
            dir=$(dirname "$repo")
            cd "$dir"
            git log --format="%ae|%an" | sort -u | while IFS='|' read email name; do
                contributors["$email"]="$name"
            done
            cd - > /dev/null
        fi
    done
fi

# From time-grants submodules
if [ -d "$GRANTS_DIR/2024/08/01" ]; then
    for repo in "$GRANTS_DIR/2024/08/01"/*/.git; do
        if [ -d "$repo" ]; then
            dir=$(dirname "$repo")
            cd "$dir"
            git log --format="%ae|%an" --max-count=100 | sort -u | while IFS='|' read email name; do
                contributors["$email"]="$name"
            done
            cd - > /dev/null
        fi
    done
fi

# Output top contributors
echo "    \"total\": ${#contributors[@]},"
echo "    \"sample\": ["

count=0
for email in "${!contributors[@]}"; do
    if [ $count -lt 20 ]; then
        echo "      {\"email\": \"$email\", \"name\": \"${contributors[$email]}\"},"
        ((count++))
    fi
done | sed '$ s/,$//'

echo "    ]"
echo "  },"
echo "  \"analysis\": \"Contributors extracted from git logs\""
echo "}"

echo ""
echo "✅ Analysis complete"
echo "📊 Found ${#contributors[@]} unique contributors"
