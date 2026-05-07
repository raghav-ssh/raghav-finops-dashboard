# Quick Reference - Report Generation

## Commands

### Generate Reports
```bash
# Daily report
python backend/run_report.py --type daily

# Weekly report
python backend/run_report.py --type weekly

# Both reports
python backend/run_report.py --type both

# Skip notifications
python backend/run_report.py --type daily --no-notifications
```

## File Naming Patterns

### Daily Reports
```
Daily_FinOps_Report_YYYY-MM-DD.pdf
daily_{category}_YYYY-MM-DD.csv
```

### Weekly Reports
```
Weekly_FinOps_Report_YYYY-MM-DD_to_YYYY-MM-DD.pdf
weekly_{category}_YYYY-MM-DD_to_YYYY-MM-DD.csv
```

## Common File Categories

| Category | Description |
|----------|-------------|
| `env_cost` | Detailed cost breakdown by environment |
| `env_summary` | Environment-level summary |
| `env_trends` | Historical trend data |
| `anomalies` | Detected anomalies |
| `budget_tracking` | Budget status |
| `cost_forecasts` | Cost forecasts |
| `optimizations` | Optimization opportunities |
| `governance_summary` | Governance metrics |

## Finding Files

```bash
# All daily reports
ls finops_reports/daily_*.csv

# All weekly reports
ls finops_reports/weekly_*.csv

# All PDFs
ls finops_reports/*.pdf

# Specific date
ls finops_reports/*_2026-03-10.*

# Specific category
ls finops_reports/*_budget_tracking_*.csv
```

## Python Usage

### Daily Report
```python
from reports.daily_env_finops_enhanced import DailyEnvFinOpsReporter

reporter = DailyEnvFinOpsReporter()
reporter.run(send_notifications=True)
```

### Weekly Report
```python
from reports.weekly_env_finops_report import WeeklyEnvFinOpsReporter

reporter = WeeklyEnvFinOpsReporter()
reporter.run(send_notifications=False)
```

## Report Contents

### Both Reports Include
- Executive Summary
- Cost Trends & Highlights
- Environment-wise Breakdown
- Cost Forecasting
- Budget Tracking
- Service Breakdown
- Anomalies & Alerts
- Optimization Opportunities

### Key Differences
| Feature | Daily | Weekly |
|---------|-------|--------|
| Coverage | 1 day | 7 days |
| Trend Chart | 7-day | 30-day |
| DoD Changes | ✅ Yes | ❌ No |
| Daily Average | ❌ No | ✅ Yes |
| Best For | Monitoring | Planning |

## Output Locations

```
backend/finops_reports/
├── Daily_FinOps_Report_*.pdf
├── Weekly_FinOps_Report_*.pdf
├── daily_*.csv
├── weekly_*.csv
└── charts/
    ├── env_comparison.png
    ├── 7day_trend.png
    ├── 30day_trend.png
    ├── top_resources.png
    ├── service_pie_prod.png
    └── budget_tracking.png
```

## Automation Examples

### Cron Jobs
```cron
# Daily at 8 AM
0 8 * * * cd /path/to/project && python backend/run_report.py --type daily

# Weekly on Monday at 9 AM
0 9 * * 1 cd /path/to/project && python backend/run_report.py --type weekly
```

### Shell Script
```bash
#!/bin/bash
cd /path/to/project
source venv/bin/activate
python backend/run_report.py --type both
```

## Troubleshooting

### Check Syntax
```bash
python3 -m py_compile backend/reports/daily_env_finops_enhanced.py
python3 -m py_compile backend/reports/weekly_env_finops_report.py
```

### Test Without Notifications
```bash
python backend/run_report.py --type daily --no-notifications
```

### View Logs
```bash
tail -f backend/logs/finops_report.log
```

## Configuration

Edit `backend/core/config.py`:

```python
FINOPS_REPORT_CONFIG = ReportConfig(
    output_dir=Path("finops_reports"),
    chart_dir=Path("finops_reports/charts"),
    monthly_budget=1200000.0,
    currency_symbol="₹"
)
```

## Documentation

- [Report Structure](REPORT_STRUCTURE.md) - Architecture overview
- [File Naming](REPORT_FILE_NAMING.md) - Naming conventions
- [Changes Summary](REPORT_CHANGES_SUMMARY.md) - What changed
- [Upgrade Guide](UPGRADE_GUIDE.md) - Migration instructions
- [Reports README](../backend/reports/README.md) - Detailed usage

## Quick Tips

1. **Always use prefixes**: `daily_` or `weekly_`
2. **Date format**: `YYYY-MM-DD` for consistency
3. **Test first**: Use `--no-notifications` for testing
4. **Check outputs**: Verify PDF and CSV files are generated
5. **Monitor logs**: Check for errors or warnings
