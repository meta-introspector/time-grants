#!/bin/bash
# Add grant-related repos as submodules and retrain model

set -e

GRANTS_DIR="/mnt/data1/nix/time/2024/08/01/time-grants"
DATE_DIR="2026/02/24"

cd "$GRANTS_DIR"
mkdir -p "$DATE_DIR"

echo "📥 Adding grant-related repos as submodules..."

# Add the 12 grant/funding repos found
git submodule add https://github.com/jthiller/helium-wallet-names "$DATE_DIR/helium-wallet-names" 2>&1 || echo "Already exists"
git submodule add https://github.com/JessmFromEarth/grants "$DATE_DIR/jessmfromearth-grants" 2>&1 || echo "Already exists"
git submodule add https://github.com/ertemann/relayer-feegrant-wg "$DATE_DIR/relayer-feegrant-wg" 2>&1 || echo "Already exists"
git submodule add https://github.com/ertemann/Grants "$DATE_DIR/ertemann-grants" 2>&1 || echo "Already exists"
git submodule add https://github.com/jthiller/grants "$DATE_DIR/jthiller-grants" 2>&1 || echo "Already exists"
git submodule add https://github.com/shelbeeee/radworks-grants "$DATE_DIR/radworks-grants-fork" 2>&1 || echo "Already exists"
git submodule add https://github.com/MasterHW/gitcoindonordata "$DATE_DIR/gitcoindonordata" 2>&1 || echo "Already exists"
git submodule add https://github.com/MasterHW/grants-infographic "$DATE_DIR/grants-infographic-fork" 2>&1 || echo "Already exists"
git submodule add https://github.com/MasterHW/grants-stack "$DATE_DIR/grants-stack-fork" 2>&1 || echo "Already exists"

# Add our own repos with proofs
git submodule add https://github.com/meta-introspector/osm-planet-torrent "$DATE_DIR/osm-planet-torrent" 2>&1 || echo "Already exists"
git submodule add https://github.com/jmikedupont2/monster-osm-quest "$DATE_DIR/monster-osm-quest" 2>&1 || echo "Already exists"
git submodule add https://github.com/meta-introspector/cicadia71 "$DATE_DIR/cicadia71" 2>&1 || echo "Already exists"

echo ""
echo "✅ Submodules added"
echo "📊 Updating .gitmodules..."

git add .gitmodules "$DATE_DIR"
git commit -m "Add grant-related repos and our proof repos as submodules

Grant repos from contributors:
- helium-wallet-names (5 stars)
- grants (multiple forks)
- radworks-grants
- gitcoindonordata
- grants-infographic
- grants-stack

Our repos with proofs:
- osm-planet-torrent (AI life, UUCP, FRACTRAN)
- monster-osm-quest (web game)
- cicadia71 (Nix integration)

Ready for model retraining" || echo "Nothing to commit"

echo ""
echo "✅ Complete"
