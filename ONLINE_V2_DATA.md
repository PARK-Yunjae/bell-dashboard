# Online V2 Data

This dashboard can be deployed with a small GitHub-safe V2 data snapshot instead of the full local `C:\Coding\data` tree.

## Storage

Commit this folder:

```text
data/closingbell/online_v2/
```

Do not commit full parquet source data:

```text
data/market/daily_ohlcv/
data/market/minute_ohlcv/
data/dart/
```

## Export Command

Run from `C:\Coding\projects\bell-data`:

```powershell
$py='C:\Coding\projects\_venvs\closingbell-py312\Scripts\python.exe'
& $py -m bell_data.cli export-online-v2-dashboard --date 2026-05-13
```

The scheduled `bell-data` flow also exports this snapshot after the V2 minute refresh and after postclose backdata refresh.

## Files

```text
data/closingbell/online_v2/latest/manifest.json
data/closingbell/online_v2/latest/v2_top3_latest.csv
data/closingbell/online_v2/latest/v2_top3_overlay_latest.csv
data/closingbell/online_v2/latest/v2_backdata_1y_detail.csv
data/closingbell/online_v2/latest/v2_backdata_1y_daily_summary.csv
data/closingbell/online_v2/latest/supply_freshness.json
```

## Notes

- `v2_top3_overlay_latest.csv` includes company, institution/foreign, short-sale, and program status fields for the current V2 Top3 only.
- Program data is exported as status/context but is not used in the V2 score.
- Full minute parquet is not exported; D+1~D+5 minute-derived returns are precomputed into the 1-year CSV.
