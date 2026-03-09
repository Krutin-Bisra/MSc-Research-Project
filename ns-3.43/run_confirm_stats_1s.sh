#!/usr/bin/env bash
set -euo pipefail

SCEN="constellation-spacex-64-sats"
SIM=1

TAG="CHECK_stats_write_1s"

echo "Running confirmation: ${TAG}"
./ns3 run sat-spacex-study -- \
  --scenarioFolder="${SCEN}" \
  --fastDev=0 \
  --enableStats=1 \
  --detailedStats=0 \
  --packetSize=1200 \
  --interval=20ms \
  --islRate=100Mb/s \
  --simTime="${SIM}" \
  --outputTag="${TAG}" | tee "${TAG}.log"

echo
echo "Searching for output folder for ${TAG} ..."
find ~/Desktop/ns-3.43 -type d -name "*${TAG}*" 2>/dev/null | head -n 5 || true
echo "Done."
