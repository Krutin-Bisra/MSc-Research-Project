# Simulation & Results Guide (SNS-3 / ns-3.43)

This guide documents how to build, run, extract results, and upload outputs for the MSc Research Project.

---

## 1) Folder locations

### ns-3 working directory (where you run simulations)
- `~/Desktop/ns-3.43/`

### GitHub repository folder
- `~/Desktop/MSc-Research-Project/`

### Scenario used for thesis (SpaceX-like 1600 sats)
- `ns-3.43/contrib/satellite/data/scenarios/constellation-spacex-1600-sats/`

### Simulation outputs (SNS-3 writes here)
- `ns-3.43/contrib/satellite/data/sims/spacex-study/<outputTag>/`

### Extracted “thesis-ready” outputs (tables/plots/reports)
- `ns-3.43/thesis_results/`

---

## 2) Build ns-3 (one time after code changes)

```bash
cd ~/Desktop/ns-3.43
./ns3 build
