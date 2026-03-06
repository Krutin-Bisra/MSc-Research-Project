#!/usr/bin/env python3
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

NS3_ROOT = Path.home() / "Desktop" / "ns-3.43"
BASE_OUT = NS3_ROOT / "contrib" / "satellite" / "data" / "sims" / "spacex-study"

TAGS = [
    "E1_light_100M_10s",
    "E3_heavy_100M_10s",
    "E4_med_500M_10s",
]

OUT_DIR = NS3_ROOT / "thesis_results" / "E1_E3_E4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def find_run_dir(tag: str) -> Path:
    p = BASE_OUT / tag
    if p.exists() and p.is_dir():
        return p
    hits = list(BASE_OUT.glob(f"*{tag}*"))
    hits = [h for h in hits if h.is_dir()]
    if hits:
        return hits[0]
    raise FileNotFoundError(f"Could not find output dir for tag '{tag}' under {BASE_OUT}")

def read_scalar_file(path: Path) -> pd.DataFrame:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            rows.append((int(parts[0]), float(parts[1])))
    return pd.DataFrame(rows, columns=["id", "value_kbps"])

def kbps_to_mbps(x): return x / 1000.0

def main():
    rows = []
    for tag in TAGS:
        run_dir = find_run_dir(tag)
        fwd = run_dir / "stat-global-fwd-app-throughput-scalar.txt"
        rtn = run_dir / "stat-global-rtn-app-throughput-scalar.txt"
        if not fwd.exists() or not rtn.exists():
            raise FileNotFoundError(f"Missing global throughput stat files in {run_dir}")

        df_f = read_scalar_file(fwd)
        df_r = read_scalar_file(rtn)
        f_mbps = float(kbps_to_mbps(df_f["value_kbps"].iloc[0])) if len(df_f) else np.nan
        r_mbps = float(kbps_to_mbps(df_r["value_kbps"].iloc[0])) if len(df_r) else np.nan

        rows.append({
            "experiment": tag,
            "global_fwd_mbps": f_mbps,
            "global_rtn_mbps": r_mbps,
            "run_dir": str(run_dir),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "global_summary.csv", index=False)

    # Simple bar plot
    plt.figure()
    x = np.arange(len(df))
    width = 0.35
    plt.bar(x - width/2, df["global_fwd_mbps"], width, label="FWD")
    plt.bar(x + width/2, df["global_rtn_mbps"], width, label="RTN")
    plt.xticks(x, df["experiment"], rotation=20, ha="right")
    plt.ylabel("Goodput (Mbps)")
    plt.title("Global Application Goodput (E1, E3, E4)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "global_goodput_E1_E3_E4.png")
    plt.close()

    # Markdown report
    md = []
    md.append("# Results: E1, E3, E4 (10s, 1600 sats)\n")
    md.append("## Global application goodput\n")
    md.append(df.to_markdown(index=False))
    md.append("\n")
    md.append("## Generated figure\n")
    md.append("- `global_goodput_E1_E3_E4.png`\n")

    (OUT_DIR / "E1_E3_E4_report.md").write_text("\n".join(md), encoding="utf-8")
    (OUT_DIR / "E1_E3_E4_summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")

    print(f"\nDone. Outputs written to: {OUT_DIR}")
    print(f"Main thesis-ready report: {OUT_DIR / 'E1_E3_E4_report.md'}")

if __name__ == "__main__":
    main()
