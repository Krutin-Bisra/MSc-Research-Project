#!/usr/bin/env python3
import math
from datetime import datetime, timezone

# -----------------------------
# SpaceX initial deployment (your PDF)
# 32 planes, 50 sats/plane, 1150 km, 53 deg
# -----------------------------
N_PLANES = 32
SATS_PER_PLANE = 50
ALT_KM = 1150.0
INC_DEG = 53.0

# Epoch for TLE + scenario start time (keep consistent)
EPOCH_DT = datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc)

# Output filenames (EDIT THESE to match your folder)
TLE_OUT = "tles.txt"
ISL_OUT = "isls.txt"
START_DATE_OUT = "start_date.txt"

# Constants
MU = 398600.4418          # km^3/s^2 (Earth gravitational parameter)
R_E = 6378.137            # km (Earth equatorial radius)

def day_of_year_fraction(dt: datetime) -> float:
    """Return day-of-year with fraction for TLE epoch field."""
    year_start = datetime(dt.year, 1, 1, tzinfo=timezone.utc)
    delta = dt - year_start
    doy = delta.days + 1
    frac = (delta.seconds + delta.microseconds / 1e6) / 86400.0
    return doy + frac

def tle_checksum(line: str) -> str:
    """Compute TLE checksum digit (mod 10)."""
    s = 0
    for ch in line[:68]:
        if ch.isdigit():
            s += int(ch)
        elif ch == '-':
            s += 1
    return str(s % 10)

def fmt_exp(num: float) -> str:
    """
    Format BSTAR / 2nd deriv fields like ' 00000-0' with implied decimal.
    We'll use zero drag for simplicity at 1150 km.
    """
    return " 00000-0"

def build_tle_lines(satnum: int, inc_deg: float, raan_deg: float, mean_anom_deg: float, mm_rev_per_day: float, epoch_yy: int, epoch_doy: float):
    # Line 1 fields (simple, mostly zeros)
    # Intl designator fields are dummy but valid-format
    intl = "26001A  "  # YYNNNPPP (dummy)
    # Epoch: YY + day of year fraction (width 12, 8 decimals)
    epoch_str = f"{epoch_yy:02d}{epoch_doy:012.8f}"[-14:]  # ensure consistent width
    # First deriv, second deriv, BSTAR all zero
    ndot = " .00000000"
    nddot = " 00000-0"
    bstar = fmt_exp(0.0)

    # Element set number
    elset = "  999"

    line1 = (
        f"1 {satnum:05d}U {intl}{epoch_str}{ndot} {nddot} {bstar} 0{elset}"
    )
    line1 = line1.ljust(68)
    line1 += tle_checksum(line1)

    # Line 2
    ecc = "0000000"
    argp = 0.0
    revnum = 1

    line2 = (
        f"2 {satnum:05d} {inc_deg:8.4f} {raan_deg:8.4f} {ecc} {argp:8.4f} {mean_anom_deg:8.4f} {mm_rev_per_day:11.8f}{revnum:5d}"
    )
    line2 = line2.ljust(68)
    line2 += tle_checksum(line2)

    return line1, line2

def main():
    n_sats = N_PLANES * SATS_PER_PLANE

    # Mean motion from circular orbit at a = Re + h
    a_km = R_E + ALT_KM
    n_rad_s = math.sqrt(MU / (a_km ** 3))
    mm_rev_day = n_rad_s * 86400.0 / (2.0 * math.pi)

    epoch_yy = EPOCH_DT.year % 100
    epoch_doy = day_of_year_fraction(EPOCH_DT)

    # 1) Write start date file (SNS-3 expects "YYYY-MM-DD hh:mm:ss")
    with open(START_DATE_OUT, "w", encoding="utf-8") as f:
        f.write(EPOCH_DT.strftime("%Y-%m-%d %H:%M:%S") + "\n")

    # 2) Write TLE file in SNS-3 format:
    # first line = size, then blocks of (name, line1, line2)
    with open(TLE_OUT, "w", encoding="utf-8") as f:
        f.write(f"{n_sats}\n")
        sat_id = 0
        base_satnum = 80000  # avoid collisions with real catalog numbers
        for p in range(N_PLANES):
            raan = (360.0 * p) / N_PLANES
            for s in range(SATS_PER_PLANE):
                mean_anom = (360.0 * s) / SATS_PER_PLANE
                satnum = base_satnum + sat_id
                name = f"SPACEX-{sat_id:04d}"
                line1, line2 = build_tle_lines(
                    satnum=satnum,
                    inc_deg=INC_DEG,
                    raan_deg=raan,
                    mean_anom_deg=mean_anom,
                    mm_rev_per_day=mm_rev_day,
                    epoch_yy=epoch_yy,
                    epoch_doy=epoch_doy,
                )
                f.write(name + "\n")
                f.write(line1 + "\n")
                f.write(line2 + "\n")
                sat_id += 1

    # 3) Write ISL file in SNS-3 format:
    # first line = size, then each line "sat1 sat2"
    # We'll build a torus +Grid: intra-plane neighbors and adjacent-plane neighbors.
    edges = set()

    def sat_index(plane, pos):
        return plane * SATS_PER_PLANE + pos

    for p in range(N_PLANES):
        p_next = (p + 1) % N_PLANES
        for s in range(SATS_PER_PLANE):
            s_next = (s + 1) % SATS_PER_PLANE

            a = sat_index(p, s)

            # East neighbor (same plane)
            b = sat_index(p, s_next)
            edges.add(tuple(sorted((a, b))))

            # North neighbor (adjacent plane, same slot)
            c = sat_index(p_next, s)
            edges.add(tuple(sorted((a, c))))

    edges = sorted(edges)
    with open(ISL_OUT, "w", encoding="utf-8") as f:
        f.write(f"{len(edges)}\n")
        for (u, v) in edges:
            f.write(f"{u} {v}\n")

    print("Generated:")
    print(f"  {START_DATE_OUT} (scenario start time)")
    print(f"  {TLE_OUT} ({n_sats} satellites)")
    print(f"  {ISL_OUT} ({len(edges)} ISLs)")

if __name__ == "__main__":
    main()
