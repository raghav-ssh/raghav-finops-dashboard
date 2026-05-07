# Report Generation Changes Summary

## Overview

The FinOps reporting system has been refactored to provide clear separation between daily and weekly reports with improved file naming conventions.

## What Changed

### 1. Separate Report Generators

**Before:**
- Single file `daily_env_finops_enhanced.py` with a `period` parameter
- Confusing to maintain and extend
- Mixed daily/weekly logic in one class

**After:**
- `daily_env_finops_enhanced.py` - Dedicated daily report generator
- `weekly_env_finops_report.py` - Dedicated weekly report generator
- Clear separation of concerns
- Easier to maintain and extend

### 2. Clear File Naming

**Before:**
```
Enhanced_Daily_FinOps_Report_2026-03-10.pdf
env_cost_2026-03-10.csv
anomalies_2026-03-10.csv
```

**After:**
```
Daily_FinOps_Report_2026-03-10.pdf
daily_env_cost_2026-03-10.csv
daily_anomalies_2026-03-10.csv

Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf
weekly_env_cost_2026-03-04_to_2026-03-10.csv
weekly_anomalies_2026-03-04_to_2026-03-10.csv
```

### 3. Improved Run Script

**Before:**
```bash
python backend/run_report.py --period daily
python backend/run_report.py --period weekly
```

**After:**
```bash
python backend/run_report.py --type daily
python backend/run_report.py --type weekly
python backend/run_report.py --type both
python backend/run_report.py --type daily --no-notifications
```

## Key Benefits

### 1. No File Conflicts
- Daily and weekly reports never overwrite each other
- All files have clear prefixes (`daily_` or `weekly_`)
- Date ranges clearly indicate the report period

### 2. Easy to Find Files
```bash
# Find all daily reports
ls finops_reports/daily_*.csv

# Find all weekly reports
ls finops_reports/weekly_*.csv

# Find all budget tracking files
ls finops_reports/*_budget_tracking_*.csv

# Find reports for specific date
ls finops_reports/*_2026-03-10.*
```

### 3. Better Organization
- CSV files clearly indicate their report type
- PDF files have descriptive names
- Charts are shared between reports (no duplication)

### 4. Cleaner Code
- Each report generator is focused on one task
- No complex conditional logic based on period
- Easier to add new report types in the future

## File Structure

```
backend/finops_reports/
├── Daily_FinOps_Report_2026-03-10.pdf
├── Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf
├── daily_env_cost_2026-03-10.csv
├── daily_env_summary_2026-03-10.csv
├── daily_anomalies_2026-03-10.csv
├── daily_budget_tracking_2026-03-10.csv
├── weekly_env_cost_2026-03-04_to_2026-03-10.csv
├── weekly_env_summary_2026-03-04_to_2026-03-10.csv
├── weekly_anomalies_2026-03-04_to_2026-03-10.csv
├── weekly_budget_tracking_2026-03-04_to_2026-03-10.csv
└── charts/
    ├── env_comparison.png
    ├── 7day_trend.png
    ├── top_resources.png
    ├── service_pie_prod.png
    └── budget_tracking.png
```

## Migration Guide

### For Users

No action needed! The new system is backward compatible:
- Old reports remain accessible
- New reports use the improved naming
- Both can coexist in the same directory

### For Developers

If you have scripts that reference report files:

**Old pattern:**
```python
report_file = f"Enhanced_Daily_FinOps_Report_{date}.pdf"
csv_file = f"env_cost_{date}.csv"
```

**New pattern:**
```python
# Daily reports
daily_report = f"Daily_FinOps_Report_{date}.pdf"
daily_csv = f"daily_env_cost_{date}.csv"

# Weekly reports
weekly_report = f"Weekly_FinOps_Report_{start_date}_to_{end_date}.pdf"
weekly_csv = f"weekly_env_cost_{start_date}_to_{end_date}.csv"
```

## Usage Examples

### Generate Daily Report
```bash
python backend/run_report.py --type daily
```
Output:
- `Daily_FinOps_Report_2026-03-10.pdf`
- Multiple `daily_*_2026-03-10.csv` files

### Generate Weekly Report
```bash
python backend/run_report.py --type weekly
```
Output:
- `Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf`
- Multiple `weekly_*_2026-03-04_to_2026-03-10.csv` files

### Generate Both Reports
```bash
python backend/run_report.py --type both
```
Output:
- Both daily and weekly reports
- All CSV files with appropriate prefixes

### Skip Notifications
```bash
python backend/run_report.py --type daily --no-notifications
```

## Testing

To verify the changes work correctly:

```bash
# Test daily report generation
python backend/run_report.py --type daily --no-notifications

# Test weekly report generation
python backend/run_report.py --type weekly --no-notifications

# Test both reports
python backend/run_report.py --type both --no-notifications

# Verify file naming
ls -la backend/finops_reports/daily_*.csv
ls -la backend/finops_reports/weekly_*.csv
ls -la backend/finops_reports/*.pdf
```

## Documentation

- [Report File Naming Conventions](REPORT_FILE_NAMING.md)
- [Report Generation README](../backend/reports/README.md)

## Future Enhancements

With this new structure, it's easy to add:
- Monthly reports
- Custom date range reports
- Quarterly reports
- Year-end reports

Each would follow the same pattern:
```
{report_type}_{data_category}_{date_range}.{extension}
```
