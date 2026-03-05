#!/usr/bin/env bash
set -euo pipefail

SCEN="constellation-spacex-1600-sats"
SIM=10

run_one () {
  local tag="$1" pkt="$2" intv="$3" isl="$4"

  echo "============================================================"
  echo "Running: ${tag}"
  echo "pkt=${pkt} interval=${intv} islRate=${isl} simTime=${SIM}s"
  echo "============================================================"

  ./ns3 run sat-spacex-study -- \
    --scenarioFolder="${SCEN}" \
    --fastDev=0 \
    --enableStats=1 \
    --detailedStats=0 \
    --packetSize="${pkt}" \
    --interval="${intv}" \
    --islRate="${isl}" \
    --simTime="${SIM}" \
    --outputTag="${tag}" | tee "${tag}.log"

  echo "Done: ${tag}"
  echo
}

# E1: Light load
run_one "E1_light_100M_10s" 512  "50ms" "100Mb/s"

# E3: Heavy load
run_one "E3_heavy_100M_10s" 1200 "5ms"  "100Mb/s"

# E4: Medium load, mid ISL
run_one "E4_med_500M_10s"   1200 "20ms" "500Mb/s"

echo "All E1+E3+E4 runs completed."
