#!/bin/bash
# Update all grant submodules and find activity in last year
# ISO 9001 compliant - reproducible, traceable

set -e

GRANTS_DIR="/mnt/data1/nix/time/2024/08/01/time-grants"
OUTPUT_FILE="$GRANTS_DIR/ACTIVITY_REPORT_$(date +%Y%m%d).md"

cd "$GRANTS_DIR"

echo "# Grant Activity Report" > "$OUTPUT_FILE"
echo "Generated: $(date -Iseconds)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "## Submodule Updates" >> "$OUTPUT_FILE"
git submodule foreach 'git fetch origin && git pull origin main || git pull origin master || true' 2>&1 | \
    grep -E "Entering|Fast-forward|Already" | tee -a "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "## Activity (Last 365 Days)" >> "$OUTPUT_FILE"

cutoff_date=$(date -d '365 days ago' +%Y-%m-%d)

for dir in 2024/08/01/*/; do
    if [ -d "$dir/.git" ]; then
        name=$(basename "$dir")
        cd "$dir"
        commits=$(git log --since="$cutoff_date" --oneline 2>/dev/null | wc -l)
        if [ $commits -gt 0 ]; then
            last=$(git log -1 --format="%ci" 2>/dev/null | cut -d' ' -f1)
            echo "- $name: $commits commits (last: $last)" >> "$OUTPUT_FILE"
        fi
        cd - > /dev/null
    fi
done

echo "" >> "$OUTPUT_FILE"
echo "Report saved: $OUTPUT_FILE"
cat "$OUTPUT_FILE"
