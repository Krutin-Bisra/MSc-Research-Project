# Results: E2 vs E5 (10s, 1600 sats)

## Global application goodput

| experiment | global_fwd_mbps | global_rtn_mbps | run_dir |
| --- | --- | --- | --- |
| E2_med_100M_10s_detailed | 281.662 | 185.396 | /home/ubuntu/Desktop/ns-3.43/contrib/satellite/data/sims/spacex-study/E2_med_100M_10s_detailed |
| E5_med_1G_10s_detailed | 282.13 | 207.151 | /home/ubuntu/Desktop/ns-3.43/contrib/satellite/data/sims/spacex-study/E5_med_1G_10s_detailed |


## Change from E2 to E5 (E5 − E2)

| metric | E2 | E5 | abs_diff | pct_diff_% |
| --- | --- | --- | --- | --- |
| global_fwd_mbps | 281.662 | 282.13 | 0.46800000000001774 | 0.16615659904425084 |
| global_rtn_mbps | 185.396 | 207.151 | 21.755000000000024 | 11.73434162549355 |


## Distribution summaries: E2_med_100M_10s_detailed

### Per-UT app throughput (Mbps)

| direction | n | min | p10 | median | mean | p90 | max | jain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FWD | 100 | 0.929341 | 2.821581 | 2.8579 | 2.82675401 | 2.886745 | 2.8890700000000002 | 0.9933922433381241 |
| RTN | 100 | 0.927439 | 1.5801290000000001 | 1.955975 | 1.86826804 | 2.0594210000000004 | 2.09329 | 0.9829489109317364 |

### Per-GW app throughput (Mbps)

| direction | n | min | p10 | median | mean | p90 | max | jain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FWD | 2 | 0.0 | 28.1662 | 140.831 | 140.831 | 253.49579999999997 | 281.662 | 0.5 |
| RTN | 2 | 0.0 | 18.5396 | 92.698 | 92.698 | 166.8564 | 185.396 | 0.5 |


## Distribution summaries: E5_med_1G_10s_detailed

### Per-UT app throughput (Mbps)

| direction | n | min | p10 | median | mean | p90 | max | jain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FWD | 100 | 0.929299 | 2.840884 | 2.862105 | 2.8312392900000005 | 2.887215 | 2.8890599999999997 | 0.9933636903426726 |
| RTN | 100 | 2.0499899999999998 | 2.0630290000000002 | 2.0899 | 2.0900394 | 2.0917030000000003 | 2.21981 | 0.999832048184984 |

### Per-GW app throughput (Mbps)

| direction | n | min | p10 | median | mean | p90 | max | jain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FWD | 2 | 0.0 | 28.213 | 141.065 | 141.065 | 253.917 | 282.13 | 0.5 |
| RTN | 2 | 0.0 | 20.715100000000003 | 103.5755 | 103.5755 | 186.4359 | 207.151 | 0.5 |


## Generated figures

- `plots/global_goodput_E2_vs_E5.png`

- `plots/cdf_per_ut_fwd_E2_vs_E5.png`

- `plots/cdf_per_ut_rtn_E2_vs_E5.png`

- `plots/bar_per_gw_fwd_E2.png`, `plots/bar_per_gw_fwd_E5.png`

- `plots/bar_per_gw_rtn_E2.png`, `plots/bar_per_gw_rtn_E5.png`
