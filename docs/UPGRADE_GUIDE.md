# Upgrade Guide - Report Generation System

## Overview

This guide helps you upgrade from the old report generation system to the new separated daily/weekly report system.

## What's New

✅ Separate daily and weekly report generators  
✅ Clear file naming conventions with prefixes  
✅ Improved command-line interface  
✅ Better code organization and maintainability  
✅ No file conflicts between report types  

## Breaking Changes

### Command Line Interface

**Old:**
```bash
python backend/run_report.py --period daily
python backend/run_report.py --period weekly
```

**New:**
```bash
python backend/run_report.py --type daily
python backend/run_report.py --type weekly
python backend/run_report.py --type both
```

### File Names

**Old:**
```
Enhanced_Daily_FinOps_Report_2026-03-10.pdf
env_cost_2026-03-10.csv
anomalies_2026-03-10.csv
budget_tracking_2026-03-10.csv
```

**New:**
```
Daily_FinOps_Report_2026-03-10.pdf
daily_env_cost_2026-03-10.csv
daily_anomalies_2026-03-10.csv
daily_budget_tracking_2026-03-10.csv

Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf
weekly_env_cost_2026-03-04_to_2026-03-10.csv
weekly_anomalies_2026-03-04_to_2026-03-10.csv
weekly_budget_tracking_2026-03-04_to_2026-03-10.csv
```

### Class Names

**Old:**
```python
from reports.daily_env_finops_enhanced import EnhancedDailyEnvFinOpsReporter

reporter = EnhancedDailyEnvFinOpsReporter(period='daily')
reporter.run()
```

**New:**
```python
# For daily reports
from reports.daily_env_finops_enhanced import DailyEnvFinOpsReporter

reporter = DailyEnvFinOpsReporter()
reporter.run()

# For weekly reports
from reports.weekly_env_finops_report import WeeklyEnvFinOpsReporter

reporter = WeeklyEnvFinOpsReporter()
reporter.run()
```

## Migration Steps

### Step 1: Update Scripts

If you have automation scripts that call the report generator:

**Before:**
```bash
#!/bin/bash
python backend/run_report.py --period daily
```

**After:**
```bash
#!/bin/bash
python backend/run_report.py --type daily
```

### Step 2: Update Cron Jobs

**Before:**
```cron
0 8 * * * cd /path/to/project && python backend/run_report.py --period daily
0 9 * * 1 cd /path/to/project && python backend/run_report.py --period weekly
```

**After:**
```cron
0 8 * * * cd /path/to/project && python backend/run_report.py --type daily
0 9 * * 1 cd /path/to/project && python backend/run_report.py --type weekly
```

### Step 3: Update File References

If you have code that reads report files:

**Before:**
```python
import glob

# Find latest daily report
reports = glob.glob("finops_reports/Enhanced_Daily_FinOps_Report_*.pdf")
latest = sorted(reports)[-1]

# Find CSV files
csv_files = glob.glob("finops_reports/env_cost_*.csv")
```

**After:**
```python
import glob

# Find latest daily report
daily_reports = glob.glob("finops_reports/Daily_FinOps_Report_*.pdf")
latest_daily = sorted(daily_reports)[-1]

# Find latest weekly report
weekly_reports = glob.glob("finops_reports/Weekly_FinOps_Report_*.pdf")
latest_weekly = sorted(weekly_reports)[-1]

# Find daily CSV files
daily_csv = glob.glob("finops_reports/daily_env_cost_*.csv")

# Find weekly CSV files
weekly_csv = glob.glob("finops_reports/weekly_env_cost_*.csv")
```

### Step 4: Update Import Statements

If you import the reporter class directly:

**Before:**
```python
from reports.daily_env_finops_enhanced import EnhancedDailyEnvFinOpsReporter

reporter = EnhancedDailyEnvFinOpsReporter(period='daily')
```

**After:**
```python
from reports.daily_env_finops_enhanced import DailyEnvFinOpsReporter

reporter = DailyEnvFinOpsReporter()
```

## Backward Compatibility

### Old Files

Old report files will continue to work and can coexist with new files:
- Old files without prefixes are still readable
- No need to delete or rename old files
- New files use clear prefixes to avoid confusion

### Identifying Old vs New Files

**Old format:**
```
Enhanced_Daily_FinOps_Report_2026-03-10.pdf  # Old
env_cost_2026-03-10.csv                      # Old
```

**New format:**
```
Daily_FinOps_Report_2026-03-10.pdf           # New
daily_env_cost_2026-03-10.csv                # New
```

## Testing the Upgrade

### 1. Test Daily Report
```bash
python backend/run_report.py --type daily --no-notifications
```

Expected output:
```
Starting Daily Environment FinOps Report Generation
...
✅ Daily FinOps Report Generated Successfully
📊 Total Cost: ₹X,XXX.XX
📄 PDF: Daily_FinOps_Report_2026-03-10.pdf
```

### 2. Test Weekly Report
```bash
python backend/run_report.py --type weekly --no-notifications
```

Expected output:
```
Starting Weekly Environment FinOps Report Generation
...
✅ Weekly FinOps Report Generated Successfully
📊 Weekly Total: ₹X,XXX.XX
📄 PDF: Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf
```

### 3. Test Both Reports
```bash
python backend/run_report.py --type both --no-notifications
```

Expected output:
```
Generating Both Daily and Weekly FinOps Reports...
...
✅ All Reports Generated Successfully
```

### 4. Verify File Names
```bash
ls -la backend/finops_reports/Daily_*.pdf
ls -la backend/finops_reports/Weekly_*.pdf
ls -la backend/finops_reports/daily_*.csv
ls -la backend/finops_reports/weekly_*.csv
```

## Rollback Plan

If you need to rollback to the old system:

1. The old code is preserved in git history
2. You can checkout the previous commit
3. Old files are not affected by the upgrade

```bash
# View git history
git log --oneline

# Rollback to previous version
git checkout <previous-commit-hash>
```

## Common Issues

### Issue: Command not found

**Problem:**
```bash
python backend/run_report.py --period daily
# Error: unrecognized arguments: --period daily
```

**Solution:**
Update to use `--type` instead of `--period`:
```bash
python backend/run_report.py --type daily
```

### Issue: Import error

**Problem:**
```python
from reports.daily_env_finops_enhanced import EnhancedDailyEnvFinOpsReporter
# ImportError: cannot import name 'EnhancedDailyEnvFinOpsReporter'
```

**Solution:**
Update class name:
```python
from reports.daily_env_finops_enhanced import DailyEnvFinOpsReporter
```

### Issue: Files not found

**Problem:**
```python
reports = glob.glob("finops_reports/Enhanced_Daily_*.pdf")
# Returns empty list
```

**Solution:**
Update file pattern:
```python
reports = glob.glob("finops_reports/Daily_*.pdf")
```

## Support

For questions or issues:
1. Check the [Report Structure](REPORT_STRUCTURE.md) documentation
2. Review [File Naming Conventions](REPORT_FILE_NAMING.md)
3. See [Report Changes Summary](REPORT_CHANGES_SUMMARY.md)

## Next Steps

After upgrading:
1. Update any automation scripts
2. Update documentation
3. Inform team members of the changes
4. Monitor first few report runs
5. Archive or clean up old report files (optional)
