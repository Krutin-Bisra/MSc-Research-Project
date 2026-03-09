## Results Index (Thesis-ready outputs)

All thesis-ready results are stored under:

`ns-3.43/thesis_results/`

### 1) Full Results Pack (Recommended for dissertation write-up)

**Folder:** `ns-3.43/thesis_results/ALL/`

- **Main report (tables + figure list):**  
  `ns-3.43/thesis_results/ALL/ALL_report.md`

- **Plots (PNG):**  
  `ns-3.43/thesis_results/ALL/plots/`

  Key figures (recommended for main Results chapter):
  - `A_global_goodput_E1_to_E5.png` — global goodput comparison across E1–E5  
  - `A_load_sweep_goodput.png` — load sweep (E1/E2/E3)  
  - `A_isl_sweep_goodput.png` — ISL sweep (E2/E4/E5)  
  - `B_cdf_ut_rtn_E2_vs_E5.png` — per-UT RTN throughput CDF (E2 vs E5)

  Additional figures (good for Appendix):
  - `B_cdf_ut_fwd_E2_vs_E5.png` — per-UT FWD throughput CDF  
  - `B_bar_gw_*` — per-GW throughput bars  
  - `C_hist_*` — UT throughput histograms  
  - `C_corr_*` — correlation scatter plots  
  - `D_*` — delay plots (if present)

- **Tables (CSV):**  
  `ns-3.43/thesis_results/ALL/tables/`

  Key tables:
  - `global_master_E1_to_E5.csv` — master global table (E1–E5)  
  - `A_delta_E5_minus_E2.csv` — E5–E2 delta table  
  - `A_load_sweep_E1_E2_E3.csv` — load sweep table  
  - `A_isl_sweep_E2_E4_E5.csv` — ISL sweep table  
  - `B_per_ut_summary_E2_E5.csv` — per-UT distribution summary (incl. Jain fairness)  
  - `B_per_gw_summary_E2_E5.csv` — per-GW distribution summary  
  - `C_top10_*` / `C_bottom10_*` — top/bottom UT tables  
  - `C_correlations.csv` — correlation summary table  
  - `D_delay_summary_E2_E5.csv` — delay summary (if generated)

- **Raw extracted CSVs used for plots:**  
  `ns-3.43/thesis_results/ALL/raw/`

---

### 2) E2 vs E5 Pack (ISL sensitivity)

**Folder:** `ns-3.43/thesis_results/E2_E5/`

- `E2_E5_report.md` — report for E2 vs E5  
- `global_summary.csv` — global goodput (E2, E5)  
- `global_delta_E5_minus_E2.csv` — delta table  
- `plots/` — global bars + UT CDFs + GW bars  
- `raw/` — per-UT and per-GW throughput CSVs

---

### 3) E1, E3, E4 Pack (Load + mid-ISL)

**Folder:** `ns-3.43/thesis_results/E1_E3_E4/`

- `E1_E3_E4_report.md` — report for E1/E3/E4  
- `global_summary.csv` — global goodput (E1, E3, E4)  
- `global_goodput_E1_E3_E4.png` — global goodput plot (E1/E3/E4)

---

## Experiment scripts (how simulations were executed)

Stored under `ns-3.43/`:
- `ns-3.43/run_confirm_stats_1s.sh` — quick stats write check
- `ns-3.43/run_E2_E5_detailed_1600_10s.sh` — E2 & E5 (detailed stats)
- `ns-3.43/run_E1_E3_E4_1600_10s.sh` — E1/E3/E4 (stats enabled, detailed off)

## Extraction scripts (how tables/plots were generated)

Stored under `ns-3.43/thesis_results/scripts/`:
- `extract_E2_E5.py`
- `extract_E1_E3_E4.py`
- `extract_ALL_A_B_C.py`
