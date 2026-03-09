#!/usr/bin/env python3
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- Paths ----------------
NS3_ROOT = Path.home() / "Desktop" / "ns-3.43"
THESIS = NS3_ROOT / "thesis_results"
SIMS = NS3_ROOT / "contrib" / "satellite" / "data" / "sims" / "spacex-study"

OUT = THESIS / "ALL"
TABLES = OUT / "tables"
PLOTS = OUT / "plots"
RAWOUT = OUT / "raw"
for d in (TABLES, PLOTS, RAWOUT):
    d.mkdir(parents=True, exist_ok=True)

# ---------------- Experiment metadata (known from your design) ----------------
META = {
    "E1_light_100M_10s":               {"E": "E1", "packetSize": 512,  "interval_ms": 50, "isl_Mbps": 100},
    "E2_med_100M_10s_detailed":        {"E": "E2", "packetSize": 1200, "interval_ms": 20, "isl_Mbps": 100},
    "E3_heavy_100M_10s":               {"E": "E3", "packetSize": 1200, "interval_ms": 5,  "isl_Mbps": 100},
    "E4_med_500M_10s":                 {"E": "E4", "packetSize": 1200, "interval_ms": 20, "isl_Mbps": 500},
    "E5_med_1G_10s_detailed":          {"E": "E5", "packetSize": 1200, "interval_ms": 20, "isl_Mbps": 1000},
}

ORDER = [
    "E1_light_100M_10s",
    "E2_med_100M_10s_detailed",
    "E3_heavy_100M_10s",
    "E4_med_500M_10s",
    "E5_med_1G_10s_detailed"
]

# ---------------- Helpers ----------------
def df_to_md_table(df: pd.DataFrame) -> str:
    df = df.copy().fillna("")
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)

def summarize(values: np.ndarray) -> dict:
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return {"n": 0, "min": np.nan, "p10": np.nan, "median": np.nan, "mean": np.nan, "p90": np.nan, "max": np.nan, "jain": np.nan}
    s = float(v.sum())
    ss = float((v ** 2).sum())
    jain = (s * s) / (v.size * ss) if ss > 0 else np.nan
    return {
        "n": int(v.size),
        "min": float(np.min(v)),
        "p10": float(np.percentile(v, 10)),
        "median": float(np.percentile(v, 50)),
        "mean": float(np.mean(v)),
        "p90": float(np.percentile(v, 90)),
        "max": float(np.max(v)),
        "jain": float(jain),
    }

def cdf_xy(v):
    v = np.asarray(v, dtype=float)
    v = v[np.isfinite(v)]
    v = np.sort(v)
    if v.size == 0:
        return np.array([0.0]), np.array([0.0])
    y = np.arange(1, v.size + 1) / v.size
    return v, y

def plot_cdf(v_a, label_a, v_b, label_b, title, xlabel, out_png):
    xa, ya = cdf_xy(v_a)
    xb, yb = cdf_xy(v_b)
    plt.figure()
    plt.plot(xa, ya, label=label_a)
    plt.plot(xb, yb, label=label_b)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("CDF")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def plot_hist(v, title, xlabel, out_png, bins=30):
    v = np.asarray(v, dtype=float)
    v = v[np.isfinite(v)]
    plt.figure()
    plt.hist(v, bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def plot_bar_two(df, xcol, y1, y2, label1, label2, title, out_png):
    x = np.arange(len(df))
    w = 0.35
    plt.figure()
    plt.bar(x - w/2, df[y1], w, label=label1)
    plt.bar(x + w/2, df[y2], w, label=label2)
    plt.xticks(x, df[xcol], rotation=20, ha="right")
    plt.ylabel("Goodput (Mbps)")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def plot_scatter(x, y, title, xlabel, ylabel, out_png):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m]; y = y[m]
    corr = np.corrcoef(x, y)[0,1] if len(x) > 1 else np.nan
    plt.figure()
    plt.scatter(x, y, s=12)
    plt.title(f"{title}\nPearson r = {corr:.3f}" if np.isfinite(corr) else title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    return corr

def safe_read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def find_raw_csv(tag: str, suffix: str) -> Path:
    # suffix examples: "_per_ut_fwd.csv", "_per_gw_rtn.csv"
    rawdir = THESIS / "E2_E5" / "raw"
    hits = list(rawdir.glob(f"{tag}*{suffix}"))
    if not hits:
        raise FileNotFoundError(f"Missing raw CSV for tag {tag} suffix {suffix} in {rawdir}")
    return hits[0]

def read_delay_scatter(run_dir: Path, direction: str) -> np.ndarray:
    """
    Reads all files named like:
      stat-per-ut-fwd-phy-delay-scatter-*.txt
      stat-per-ut-rtn-phy-delay-scatter-*.txt
    Returns concatenated delay samples (converted to ms if looks like seconds).
    """
    pattern = f"stat-per-ut-{direction}-phy-delay-scatter-*.txt"
    files = sorted(run_dir.glob(pattern))
    if not files:
        return np.array([])

    vals = []
    for f in files:
        with f.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("%"):
                    continue
                parts = line.split()
                # expected: time value  (or id value). take last numeric as delay
                try:
                    num = float(parts[-1])
                    vals.append(num)
                except:
                    continue
    v = np.asarray(vals, dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return v

    # Heuristic unit conversion:
    # If median < 1, probably seconds -> convert to ms.
    if np.median(v) < 1.0:
        v = v * 1000.0
    return v  # ms (heuristic)

# ---------------- Load global summaries ----------------
def load_global_tables():
    e2e5 = pd.read_csv(THESIS / "E2_E5" / "global_summary.csv")
    e1e3e4 = pd.read_csv(THESIS / "E1_E3_E4" / "global_summary.csv")
    df = pd.concat([e1e3e4, e2e5], ignore_index=True)

    # Keep only E1–E5 rows
    df = df[df["experiment"].isin(ORDER)].copy()
    df["E"] = df["experiment"].map(lambda x: META.get(x, {}).get("E", ""))
    df["packetSize_B"] = df["experiment"].map(lambda x: META.get(x, {}).get("packetSize", np.nan))
    df["interval_ms"] = df["experiment"].map(lambda x: META.get(x, {}).get("interval_ms", np.nan))
    df["isl_Mbps"] = df["experiment"].map(lambda x: META.get(x, {}).get("isl_Mbps", np.nan))
    df["order"] = df["experiment"].apply(lambda x: ORDER.index(x) if x in ORDER else 999)
    df = df.sort_values("order").drop(columns=["order"])

    # Save master
    df.to_csv(TABLES / "global_master_E1_to_E5.csv", index=False)
    return df

# ---------------- Main ----------------
def main():
    md = []
    md.append("# Full Results Pack (A + B + C)\n")
    md.append("Generated by `thesis_results/scripts/extract_ALL_A_B_C.py`.\n")

    # ---- A) Global tables + plots ----
    df_global = load_global_tables()

    md.append("## A1. Master global goodput table (E1–E5)\n")
    md.append(df_to_md_table(df_global[["E","experiment","isl_Mbps","packetSize_B","interval_ms","global_fwd_mbps","global_rtn_mbps"]]))
    md.append("\n")

    # Global E1–E5 bar plot
    plot_bar_two(
        df_global,
        xcol="E",
        y1="global_fwd_mbps",
        y2="global_rtn_mbps",
        label1="FWD",
        label2="RTN",
        title="Global Application Goodput (E1–E5)",
        out_png=PLOTS / "A_global_goodput_E1_to_E5.png"
    )

    # Load sweep E1/E2/E3
    df_load = df_global[df_global["E"].isin(["E1","E2","E3"])].copy()
    df_load.to_csv(TABLES / "A_load_sweep_E1_E2_E3.csv", index=False)
    plot_bar_two(df_load, "E", "global_fwd_mbps", "global_rtn_mbps", "FWD", "RTN",
                 "Load Sweep (E1/E2/E3): Global Goodput", PLOTS / "A_load_sweep_goodput.png")

    # ISL sweep E2/E4/E5
    df_isl = df_global[df_global["E"].isin(["E2","E4","E5"])].copy()
    df_isl.to_csv(TABLES / "A_isl_sweep_E2_E4_E5.csv", index=False)
    # Line plot vs ISL Mbps
    plt.figure()
    plt.plot(df_isl["isl_Mbps"], df_isl["global_fwd_mbps"], marker="o", label="FWD")
    plt.plot(df_isl["isl_Mbps"], df_isl["global_rtn_mbps"], marker="o", label="RTN")
    plt.xlabel("ISL rate (Mbps)")
    plt.ylabel("Goodput (Mbps)")
    plt.title("ISL Capacity Sweep (E2/E4/E5): Global Goodput")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "A_isl_sweep_goodput.png")
    plt.close()

    # Delta E5 - E2 (use existing if present, else compute)
    delta_path = THESIS / "E2_E5" / "global_delta_E5_minus_E2.csv"
    if delta_path.exists():
        df_delta = pd.read_csv(delta_path)
    else:
        e2 = df_global[df_global["E"]=="E2"].iloc[0]
        e5 = df_global[df_global["E"]=="E5"].iloc[0]
        df_delta = pd.DataFrame({
            "metric":["global_fwd_mbps","global_rtn_mbps"],
            "E2":[e2["global_fwd_mbps"], e2["global_rtn_mbps"]],
            "E5":[e5["global_fwd_mbps"], e5["global_rtn_mbps"]],
        })
        df_delta["abs_diff"]=df_delta["E5"]-df_delta["E2"]
        df_delta["pct_diff_%"]=100.0*df_delta["abs_diff"]/df_delta["E2"]
    df_delta.to_csv(TABLES / "A_delta_E5_minus_E2.csv", index=False)
    md.append("## A2. Delta table (E5 − E2)\n")
    md.append(df_to_md_table(df_delta))
    md.append("\n")

    md.append("## A3. Figures generated\n")
    md.append("- `plots/A_global_goodput_E1_to_E5.png`\n")
    md.append("- `plots/A_load_sweep_goodput.png`\n")
    md.append("- `plots/A_isl_sweep_goodput.png`\n")

    # ---- B) Distribution / fairness (E2 vs E5) ----
    tag_e2 = "E2_med_100M_10s_detailed"
    tag_e5 = "E5_med_1G_10s_detailed"

    e2_ut_fwd = safe_read_csv(find_raw_csv(tag_e2, "_per_ut_fwd.csv"))
    e2_ut_rtn = safe_read_csv(find_raw_csv(tag_e2, "_per_ut_rtn.csv"))
    e5_ut_fwd = safe_read_csv(find_raw_csv(tag_e5, "_per_ut_fwd.csv"))
    e5_ut_rtn = safe_read_csv(find_raw_csv(tag_e5, "_per_ut_rtn.csv"))

    e2_gw_fwd = safe_read_csv(find_raw_csv(tag_e2, "_per_gw_fwd.csv"))
    e2_gw_rtn = safe_read_csv(find_raw_csv(tag_e2, "_per_gw_rtn.csv"))
    e5_gw_fwd = safe_read_csv(find_raw_csv(tag_e5, "_per_gw_fwd.csv"))
    e5_gw_rtn = safe_read_csv(find_raw_csv(tag_e5, "_per_gw_rtn.csv"))

    # Save copies
    e2_ut_fwd.to_csv(RAWOUT / "E2_per_ut_fwd.csv", index=False)
    e2_ut_rtn.to_csv(RAWOUT / "E2_per_ut_rtn.csv", index=False)
    e5_ut_fwd.to_csv(RAWOUT / "E5_per_ut_fwd.csv", index=False)
    e5_ut_rtn.to_csv(RAWOUT / "E5_per_ut_rtn.csv", index=False)

    # Summary tables
    ut_summary = pd.DataFrame([
        {"run":"E2", "dir":"FWD", **summarize(e2_ut_fwd["value_mbps"].to_numpy())},
        {"run":"E2", "dir":"RTN", **summarize(e2_ut_rtn["value_mbps"].to_numpy())},
        {"run":"E5", "dir":"FWD", **summarize(e5_ut_fwd["value_mbps"].to_numpy())},
        {"run":"E5", "dir":"RTN", **summarize(e5_ut_rtn["value_mbps"].to_numpy())},
    ])
    gw_summary = pd.DataFrame([
        {"run":"E2", "dir":"FWD", **summarize(e2_gw_fwd["value_mbps"].to_numpy())},
        {"run":"E2", "dir":"RTN", **summarize(e2_gw_rtn["value_mbps"].to_numpy())},
        {"run":"E5", "dir":"FWD", **summarize(e5_gw_fwd["value_mbps"].to_numpy())},
        {"run":"E5", "dir":"RTN", **summarize(e5_gw_rtn["value_mbps"].to_numpy())},
    ])
    ut_summary.to_csv(TABLES / "B_per_ut_summary_E2_E5.csv", index=False)
    gw_summary.to_csv(TABLES / "B_per_gw_summary_E2_E5.csv", index=False)

    md.append("\n## B1. Per-UT throughput summary (E2 vs E5)\n")
    md.append(df_to_md_table(ut_summary))
    md.append("\n## B2. Per-GW throughput summary (E2 vs E5)\n")
    md.append(df_to_md_table(gw_summary))
    md.append("\n")

    # CDF plots UT
    plot_cdf(e2_ut_fwd["value_mbps"], "E2 (100Mb/s)", e5_ut_fwd["value_mbps"], "E5 (1Gb/s)",
             "Per-UT FWD App Throughput CDF", "Throughput (Mbps)", PLOTS / "B_cdf_ut_fwd_E2_vs_E5.png")
    plot_cdf(e2_ut_rtn["value_mbps"], "E2 (100Mb/s)", e5_ut_rtn["value_mbps"], "E5 (1Gb/s)",
             "Per-UT RTN App Throughput CDF", "Throughput (Mbps)", PLOTS / "B_cdf_ut_rtn_E2_vs_E5.png")

    # GW bar plots (separate, readable)
    def gw_bar(df, title, out_png):
        plt.figure()
        plt.bar(df["id"].astype(str), df["value_mbps"])
        plt.xticks(rotation=90)
        plt.ylabel("Mbps")
        plt.title(title)
        plt.tight_layout()
        plt.savefig(out_png)
        plt.close()

    gw_bar(e2_gw_fwd, "Per-GW FWD App Throughput (E2)", PLOTS / "B_bar_gw_fwd_E2.png")
    gw_bar(e5_gw_fwd, "Per-GW FWD App Throughput (E5)", PLOTS / "B_bar_gw_fwd_E5.png")
    gw_bar(e2_gw_rtn, "Per-GW RTN App Throughput (E2)", PLOTS / "B_bar_gw_rtn_E2.png")
    gw_bar(e5_gw_rtn, "Per-GW RTN App Throughput (E5)", PLOTS / "B_bar_gw_rtn_E5.png")

    md.append("## B3. Figures generated\n")
    md.append("- `plots/B_cdf_ut_fwd_E2_vs_E5.png`\n")
    md.append("- `plots/B_cdf_ut_rtn_E2_vs_E5.png`\n")
    md.append("- `plots/B_bar_gw_fwd_E2.png`, `plots/B_bar_gw_fwd_E5.png`\n")
    md.append("- `plots/B_bar_gw_rtn_E2.png`, `plots/B_bar_gw_rtn_E5.png`\n")

    # ---- C) Extra tables/plots ----
    def top_bottom(df, run, direction, out_prefix):
        d = df.sort_values("value_mbps", ascending=False).copy()
        top10 = d.head(10)
        bot10 = d.tail(10).sort_values("value_mbps", ascending=True)
        top10.to_csv(TABLES / f"C_top10_{out_prefix}_{run}_{direction}.csv", index=False)
        bot10.to_csv(TABLES / f"C_bottom10_{out_prefix}_{run}_{direction}.csv", index=False)
        return top10, bot10

    # Top/bottom UT for E2 and E5 (FWD/RTN)
    top_bottom(e2_ut_fwd, "E2", "FWD", "UT")
    top_bottom(e2_ut_rtn, "E2", "RTN", "UT")
    top_bottom(e5_ut_fwd, "E5", "FWD", "UT")
    top_bottom(e5_ut_rtn, "E5", "RTN", "UT")

    # Histograms UT
    plot_hist(e2_ut_fwd["value_mbps"], "UT Throughput Histogram (E2 FWD)", "Mbps", PLOTS / "C_hist_ut_fwd_E2.png")
    plot_hist(e5_ut_fwd["value_mbps"], "UT Throughput Histogram (E5 FWD)", "Mbps", PLOTS / "C_hist_ut_fwd_E5.png")
    plot_hist(e2_ut_rtn["value_mbps"], "UT Throughput Histogram (E2 RTN)", "Mbps", PLOTS / "C_hist_ut_rtn_E2.png")
    plot_hist(e5_ut_rtn["value_mbps"], "UT Throughput Histogram (E5 RTN)", "Mbps", PLOTS / "C_hist_ut_rtn_E5.png")

    # Correlation plots UT: FWD vs RTN (same run)
    e2_ut = pd.merge(e2_ut_fwd[["id","value_mbps"]].rename(columns={"value_mbps":"fwd"}),
                     e2_ut_rtn[["id","value_mbps"]].rename(columns={"value_mbps":"rtn"}), on="id", how="inner")
    e5_ut = pd.merge(e5_ut_fwd[["id","value_mbps"]].rename(columns={"value_mbps":"fwd"}),
                     e5_ut_rtn[["id","value_mbps"]].rename(columns={"value_mbps":"rtn"}), on="id", how="inner")

    r_e2_ut = plot_scatter(e2_ut["fwd"], e2_ut["rtn"], "UT Throughput Correlation (E2)", "FWD Mbps", "RTN Mbps", PLOTS / "C_corr_ut_E2.png")
    r_e5_ut = plot_scatter(e5_ut["fwd"], e5_ut["rtn"], "UT Throughput Correlation (E5)", "FWD Mbps", "RTN Mbps", PLOTS / "C_corr_ut_E5.png")

    # Correlation plots GW
    e2_gw = pd.merge(e2_gw_fwd[["id","value_mbps"]].rename(columns={"value_mbps":"fwd"}),
                     e2_gw_rtn[["id","value_mbps"]].rename(columns={"value_mbps":"rtn"}), on="id", how="inner")
    e5_gw = pd.merge(e5_gw_fwd[["id","value_mbps"]].rename(columns={"value_mbps":"fwd"}),
                     e5_gw_rtn[["id","value_mbps"]].rename(columns={"value_mbps":"rtn"}), on="id", how="inner")

    r_e2_gw = plot_scatter(e2_gw["fwd"], e2_gw["rtn"], "GW Throughput Correlation (E2)", "FWD Mbps", "RTN Mbps", PLOTS / "C_corr_gw_E2.png")
    r_e5_gw = plot_scatter(e5_gw["fwd"], e5_gw["rtn"], "GW Throughput Correlation (E5)", "FWD Mbps", "RTN Mbps", PLOTS / "C_corr_gw_E5.png")

    corr_table = pd.DataFrame([
        {"entity":"UT", "run":"E2", "pearson_r": r_e2_ut},
        {"entity":"UT", "run":"E5", "pearson_r": r_e5_ut},
        {"entity":"GW", "run":"E2", "pearson_r": r_e2_gw},
        {"entity":"GW", "run":"E5", "pearson_r": r_e5_gw},
    ])
    corr_table.to_csv(TABLES / "C_correlations.csv", index=False)

    md.append("\n## C1. Correlations (FWD vs RTN)\n")
    md.append(df_to_md_table(corr_table))
    md.append("\n")

    # ---- Delay extraction (E2 & E5, if available) ----
    e2_dir = SIMS / tag_e2
    e5_dir = SIMS / tag_e5

    delay_rows = []
    for run_tag, run_dir, label in [(tag_e2, e2_dir, "E2"), (tag_e5, e5_dir, "E5")]:
        if run_dir.exists():
            for d in ["fwd", "rtn"]:
                v = read_delay_scatter(run_dir, d)
                if v.size > 0:
                    # Save raw delay samples
                    pd.DataFrame({"delay_ms": v}).to_csv(RAWOUT / f"delay_{label}_{d}.csv", index=False)
                    summ = summarize(v)
                    delay_rows.append({"run":label, "dir":d.upper(), **summ})
        # else: skip

    if delay_rows:
        delay_df = pd.DataFrame(delay_rows)
        delay_df.to_csv(TABLES / "D_delay_summary_E2_E5.csv", index=False)
        md.append("## D. PHY delay (from scatter files, ms heuristic)\n")
        md.append(df_to_md_table(delay_df))
        md.append("\n")

        # Delay CDF plots (E2 vs E5)
        e2_fwd = pd.read_csv(RAWOUT / "delay_E2_fwd.csv")["delay_ms"].to_numpy() if (RAWOUT / "delay_E2_fwd.csv").exists() else np.array([])
        e5_fwd = pd.read_csv(RAWOUT / "delay_E5_fwd.csv")["delay_ms"].to_numpy() if (RAWOUT / "delay_E5_fwd.csv").exists() else np.array([])
        e2_rtn = pd.read_csv(RAWOUT / "delay_E2_rtn.csv")["delay_ms"].to_numpy() if (RAWOUT / "delay_E2_rtn.csv").exists() else np.array([])
        e5_rtn = pd.read_csv(RAWOUT / "delay_E5_rtn.csv")["delay_ms"].to_numpy() if (RAWOUT / "delay_E5_rtn.csv").exists() else np.array([])

        if e2_fwd.size and e5_fwd.size:
            plot_cdf(e2_fwd, "E2", e5_fwd, "E5", "PHY Delay CDF (FWD)", "Delay (ms)", PLOTS / "D_cdf_delay_fwd_E2_vs_E5.png")
        if e2_rtn.size and e5_rtn.size:
            plot_cdf(e2_rtn, "E2", e5_rtn, "E5", "PHY Delay CDF (RTN)", "Delay (ms)", PLOTS / "D_cdf_delay_rtn_E2_vs_E5.png")

        # Delay histograms
        if e2_fwd.size:
            plot_hist(e2_fwd, "PHY Delay Histogram (E2 FWD)", "Delay (ms)", PLOTS / "D_hist_delay_fwd_E2.png")
        if e5_fwd.size:
            plot_hist(e5_fwd, "PHY Delay Histogram (E5 FWD)", "Delay (ms)", PLOTS / "D_hist_delay_fwd_E5.png")
        if e2_rtn.size:
            plot_hist(e2_rtn, "PHY Delay Histogram (E2 RTN)", "Delay (ms)", PLOTS / "D_hist_delay_rtn_E2.png")
        if e5_rtn.size:
            plot_hist(e5_rtn, "PHY Delay Histogram (E5 RTN)", "Delay (ms)", PLOTS / "D_hist_delay_rtn_E5.png")

    else:
        md.append("## D. PHY delay\nNo delay scatter files found for E2/E5.\n")

    # Final report
    md.append("\n## File index\n")
    md.append("- Tables: `thesis_results/ALL/tables/`\n")
    md.append("- Plots: `thesis_results/ALL/plots/`\n")
    md.append("- Raw extracted CSVs: `thesis_results/ALL/raw/`\n")
    (OUT / "ALL_report.md").write_text("\n".join(md), encoding="utf-8")

    print("Done.")
    print("Outputs:", OUT)
    print("Report :", OUT / "ALL_report.md")

if __name__ == "__main__":
    main()
