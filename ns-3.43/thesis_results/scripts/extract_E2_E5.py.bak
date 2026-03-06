#!/usr/bin/env python3
import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- User-editable defaults (should match your environment) ----
NS3_ROOT = Path.home() / "Desktop" / "ns-3.43"
BASE_OUT = NS3_ROOT / "contrib" / "satellite" / "data" / "sims" / "spacex-study"

TAGS = [
    "E2_med_100M_10s_detailed",
    "E5_med_1G_10s_detailed",
]

OUT_DIR = NS3_ROOT / "thesis_results" / "E2_E5"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- Helpers ----
def find_run_dir(tag: str) -> Path:
    p = BASE_OUT / tag
    if p.exists() and p.is_dir():
        return p
    # Fallback: search in case your folder name has slight variations
    hits = list(BASE_OUT.glob(f"*{tag}*"))
    hits = [h for h in hits if h.is_dir()]
    if hits:
        return hits[0]
    raise FileNotFoundError(f"Could not find output dir for tag '{tag}' under {BASE_OUT}")

def read_scalar_file(path: Path) -> pd.DataFrame:
    """
    SNS-3 scalar files look like:
      % comment
      0 281662
    or multiple rows:
      % comment
      0 123
      1 456
    """
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            idx = int(parts[0])
            val = float(parts[1])
            rows.append((idx, val))
    if not rows:
        return pd.DataFrame(columns=["id", "value_kbps"])
    return pd.DataFrame(rows, columns=["id", "value_kbps"])

def kbps_to_mbps(x):
    return x / 1000.0

def summarize_series_mbps(values_mbps: np.ndarray) -> dict:
    values_mbps = np.asarray(values_mbps, dtype=float)
    values_mbps = values_mbps[np.isfinite(values_mbps)]
    if values_mbps.size == 0:
        return {
            "n": 0, "min": np.nan, "p10": np.nan, "median": np.nan,
            "mean": np.nan, "p90": np.nan, "max": np.nan, "jain": np.nan
        }
    n = values_mbps.size
    s = float(values_mbps.sum())
    ss = float((values_mbps ** 2).sum())
    jain = (s * s) / (n * ss) if ss > 0 else np.nan
    return {
        "n": int(n),
        "min": float(np.min(values_mbps)),
        "p10": float(np.percentile(values_mbps, 10)),
        "median": float(np.percentile(values_mbps, 50)),
        "mean": float(np.mean(values_mbps)),
        "p90": float(np.percentile(values_mbps, 90)),
        "max": float(np.max(values_mbps)),
        "jain": float(jain),
    }

def cdf_plot(values_a, label_a, values_b, label_b, title, out_png: Path):
    def cdf_xy(v):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        v = np.sort(v)
        if v.size == 0:
            return np.array([0.0]), np.array([0.0])
        y = np.arange(1, v.size + 1) / v.size
        return v, y

    xa, ya = cdf_xy(values_a)
    xb, yb = cdf_xy(values_b)

    plt.figure()
    plt.plot(xa, ya, label=label_a)
    plt.plot(xb, yb, label=label_b)
    plt.xlabel("Throughput (Mbps)")
    plt.ylabel("CDF")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def bar_plot(ids, vals, title, xlabel, ylabel, out_png: Path):
    plt.figure()
    plt.bar([str(i) for i in ids], vals)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

# ---- Main extraction ----
def extract_one(tag: str) -> dict:
    run_dir = find_run_dir(tag)

    files = {
        "global_fwd": run_dir / "stat-global-fwd-app-throughput-scalar.txt",
        "global_rtn": run_dir / "stat-global-rtn-app-throughput-scalar.txt",
        "per_ut_fwd": run_dir / "stat-per-ut-fwd-app-throughput-scalar.txt",
        "per_ut_rtn": run_dir / "stat-per-ut-rtn-app-throughput-scalar.txt",
        "per_gw_fwd": run_dir / "stat-per-gw-fwd-app-throughput-scalar.txt",
        "per_gw_rtn": run_dir / "stat-per-gw-rtn-app-throughput-scalar.txt",
    }

    # Read scalar files (if any missing, raise a clear error)
    data = {}
    for k, p in files.items():
        if not p.exists():
            raise FileNotFoundError(f"Missing expected stat file: {p}")
        df = read_scalar_file(p)
        df["value_mbps"] = kbps_to_mbps(df["value_kbps"])
        data[k] = df

    global_fwd_mbps = float(data["global_fwd"]["value_mbps"].iloc[0]) if len(data["global_fwd"]) else np.nan
    global_rtn_mbps = float(data["global_rtn"]["value_mbps"].iloc[0]) if len(data["global_rtn"]) else np.nan

    # Save raw per-UT / per-GW CSVs
    out_raw = OUT_DIR / "raw"
    out_raw.mkdir(exist_ok=True)

    data["per_ut_fwd"].to_csv(out_raw / f"{tag}_per_ut_fwd.csv", index=False)
    data["per_ut_rtn"].to_csv(out_raw / f"{tag}_per_ut_rtn.csv", index=False)
    data["per_gw_fwd"].to_csv(out_raw / f"{tag}_per_gw_fwd.csv", index=False)
    data["per_gw_rtn"].to_csv(out_raw / f"{tag}_per_gw_rtn.csv", index=False)

    # Summaries
    per_ut_fwd_summary = summarize_series_mbps(data["per_ut_fwd"]["value_mbps"].to_numpy())
    per_ut_rtn_summary = summarize_series_mbps(data["per_ut_rtn"]["value_mbps"].to_numpy())
    per_gw_fwd_summary = summarize_series_mbps(data["per_gw_fwd"]["value_mbps"].to_numpy())
    per_gw_rtn_summary = summarize_series_mbps(data["per_gw_rtn"]["value_mbps"].to_numpy())

    return {
        "tag": tag,
        "run_dir": str(run_dir),
        "global_fwd_mbps": global_fwd_mbps,
        "global_rtn_mbps": global_rtn_mbps,
        "per_ut_fwd_summary": per_ut_fwd_summary,
        "per_ut_rtn_summary": per_ut_rtn_summary,
        "per_gw_fwd_summary": per_gw_fwd_summary,
        "per_gw_rtn_summary": per_gw_rtn_summary,
    }

def main():
    results = [extract_one(t) for t in TAGS]

    # Global summary table
    df_global = pd.DataFrame([{
        "experiment": r["tag"],
        "global_fwd_mbps": r["global_fwd_mbps"],
        "global_rtn_mbps": r["global_rtn_mbps"],
        "run_dir": r["run_dir"],
    } for r in results])
    df_global.to_csv(OUT_DIR / "global_summary.csv", index=False)

    # Delta table (E5 - E2)
    if len(results) == 2:
        a, b = results[0], results[1]
        delta = {
            "metric": ["global_fwd_mbps", "global_rtn_mbps"],
            "E2": [a["global_fwd_mbps"], a["global_rtn_mbps"]],
            "E5": [b["global_fwd_mbps"], b["global_rtn_mbps"]],
        }
        df_delta = pd.DataFrame(delta)
        df_delta["abs_diff"] = df_delta["E5"] - df_delta["E2"]
        df_delta["pct_diff_%"] = np.where(df_delta["E2"] != 0, 100.0 * df_delta["abs_diff"] / df_delta["E2"], np.nan)
        df_delta.to_csv(OUT_DIR / "global_delta_E5_minus_E2.csv", index=False)
    else:
        df_delta = None

    # Plots
    plots_dir = OUT_DIR / "plots"
    plots_dir.mkdir(exist_ok=True)

    # Global bar plot (FWD/RTN)
    plt.figure()
    x = np.arange(len(df_global))
    width = 0.35
    plt.bar(x - width/2, df_global["global_fwd_mbps"], width, label="FWD")
    plt.bar(x + width/2, df_global["global_rtn_mbps"], width, label="RTN")
    plt.xticks(x, df_global["experiment"], rotation=20, ha="right")
    plt.ylabel("Goodput (Mbps)")
    plt.title("Global Application Goodput (E2 vs E5)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(plots_dir / "global_goodput_E2_vs_E5.png")
    plt.close()

    # UT CDF plots (FWD and RTN)
    # Load raw CSVs back for plotting (simple)
    raw = OUT_DIR / "raw"
    e2_tag, e5_tag = TAGS[0], TAGS[1]
    e2_ut_fwd = pd.read_csv(raw / f"{e2_tag}_per_ut_fwd.csv")["value_mbps"].to_numpy()
    e5_ut_fwd = pd.read_csv(raw / f"{e5_tag}_per_ut_fwd.csv")["value_mbps"].to_numpy()
    e2_ut_rtn = pd.read_csv(raw / f"{e2_tag}_per_ut_rtn.csv")["value_mbps"].to_numpy()
    e5_ut_rtn = pd.read_csv(raw / f"{e5_tag}_per_ut_rtn.csv")["value_mbps"].to_numpy()

    cdf_plot(e2_ut_fwd, "E2 (100Mb/s)", e5_ut_fwd, "E5 (1Gb/s)",
             "Per-UT FWD App Throughput CDF", plots_dir / "cdf_per_ut_fwd_E2_vs_E5.png")
    cdf_plot(e2_ut_rtn, "E2 (100Mb/s)", e5_ut_rtn, "E5 (1Gb/s)",
             "Per-UT RTN App Throughput CDF", plots_dir / "cdf_per_ut_rtn_E2_vs_E5.png")

    # GW bar plots (FWD and RTN)
    e2_gw_fwd = pd.read_csv(raw / f"{e2_tag}_per_gw_fwd.csv")
    e5_gw_fwd = pd.read_csv(raw / f"{e5_tag}_per_gw_fwd.csv")
    e2_gw_rtn = pd.read_csv(raw / f"{e2_tag}_per_gw_rtn.csv")
    e5_gw_rtn = pd.read_csv(raw / f"{e5_tag}_per_gw_rtn.csv")

    bar_plot(e2_gw_fwd["id"].to_list(), e2_gw_fwd["value_mbps"].to_list(),
             "Per-GW FWD App Throughput (E2)", "GW id", "Mbps", plots_dir / "bar_per_gw_fwd_E2.png")
    bar_plot(e5_gw_fwd["id"].to_list(), e5_gw_fwd["value_mbps"].to_list(),
             "Per-GW FWD App Throughput (E5)", "GW id", "Mbps", plots_dir / "bar_per_gw_fwd_E5.png")
    bar_plot(e2_gw_rtn["id"].to_list(), e2_gw_rtn["value_mbps"].to_list(),
             "Per-GW RTN App Throughput (E2)", "GW id", "Mbps", plots_dir / "bar_per_gw_rtn_E2.png")
    bar_plot(e5_gw_rtn["id"].to_list(), e5_gw_rtn["value_mbps"].to_list(),
             "Per-GW RTN App Throughput (E5)", "GW id", "Mbps", plots_dir / "bar_per_gw_rtn_E5.png")

    # Markdown report (ready to paste)
    md = []
    md.append("# Results: E2 vs E5 (10s, 1600 sats)\n")
    md.append("## Global application goodput\n")
    md.append(df_global.to_markdown(index=False))
    md.append("\n")
    if df_delta is not None:
        md.append("## Change from E2 to E5 (E5 − E2)\n")
        md.append(df_delta.to_markdown(index=False))
        md.append("\n")

    def add_summary_block(tag, r):
        md.append(f"## Distribution summaries: {tag}\n")
        md.append("### Per-UT app throughput (Mbps)\n")
        md.append(pd.DataFrame([
            {"direction": "FWD", **r["per_ut_fwd_summary"]},
            {"direction": "RTN", **r["per_ut_rtn_summary"]},
        ]).to_markdown(index=False))
        md.append("\n### Per-GW app throughput (Mbps)\n")
        md.append(pd.DataFrame([
            {"direction": "FWD", **r["per_gw_fwd_summary"]},
            {"direction": "RTN", **r["per_gw_rtn_summary"]},
        ]).to_markdown(index=False))
        md.append("\n")

    for r in results:
        add_summary_block(r["tag"], r)

    md.append("## Generated figures\n")
    md.append("- `plots/global_goodput_E2_vs_E5.png`\n")
    md.append("- `plots/cdf_per_ut_fwd_E2_vs_E5.png`\n")
    md.append("- `plots/cdf_per_ut_rtn_E2_vs_E5.png`\n")
    md.append("- `plots/bar_per_gw_fwd_E2.png`, `plots/bar_per_gw_fwd_E5.png`\n")
    md.append("- `plots/bar_per_gw_rtn_E2.png`, `plots/bar_per_gw_rtn_E5.png`\n")

    (OUT_DIR / "E2_E5_report.md").write_text("\n".join(md), encoding="utf-8")
    (OUT_DIR / "E2_E5_summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\nDone. Outputs written to: {OUT_DIR}")
    print(f"Main thesis-ready report: {OUT_DIR / 'E2_E5_report.md'}")

if __name__ == "__main__":
    main()
