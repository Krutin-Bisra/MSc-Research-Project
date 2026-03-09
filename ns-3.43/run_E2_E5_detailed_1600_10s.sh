#!/usr/bin/env bash
set -euo pipefail

SCEN="constellation-spacex-1600-sats"
SIM=10

run_one () {
  local tag="$1" pkt="$2" intv="$3" isl="$4" detailed="$5"

  echo "============================================================"
  echo "Running: ${tag}"
  echo "pkt=${pkt} interval=${intv} islRate=${isl} simTime=${SIM}s detailedStats=${detailed}"
  echo "============================================================"

  ./ns3 run sat-spacex-study -- \
    --scenarioFolder="${SCEN}" \
    --fastDev=0 \
    --enableStats=1 \
    --detailedStats="${detailed}" \
    --packetSize="${pkt}" \
    --interval="${intv}" \
    --islRate="${isl}" \
    --simTime="${SIM}" \
    --outputTag="${tag}" | tee "${tag}.log"

  echo "Done: ${tag}"
  echo
}

# E2: Medium load, baseline ISL
run_one "E2_med_100M_10s_detailed" 1200 "20ms" "100Mb/s" 1

# E5: Medium load, highest ISL
run_one "E5_med_1G_10s_detailed"   1200 "20ms" "1Gb/s"   1

echo "All E2+E5 detailed runs completed."
echo "Find outputs:"
echo "  find ~/Desktop/ns-3.43 -type d -name '*E2_med_100M_10s_detailed*' 2>/dev/null | head"
echo "  find ~/Desktop/ns-3.43 -type d -name '*E5_med_1G_10s_detailed*' 2>/dev/null | head"
