# Report File Naming Conventions

This document explains the file naming conventions for FinOps reports to make them easily identifiable and understandable.

## File Naming Pattern

All report files follow a consistent naming pattern:

```
{report_type}_{data_category}_{date_range}.{extension}
```

### Components

1. **report_type**: `daily` or `weekly`
2. **data_category**: Describes the content (e.g., `env_cost`, `anomalies`, `budget_tracking`)
3. **date_range**: 
   - Daily: `YYYY-MM-DD` (e.g., `2026-03-10`)
   - Weekly: `YYYY-MM-DD_to_YYYY-MM-DD` (e.g., `2026-03-04_to_2026-03-10`)
4. **extension**: `.pdf` or `.csv`

## Daily Report Files

### PDF Report
```
Daily_FinOps_Report_2026-03-10.pdf
```
Main comprehensive PDF report for a single day.

### CSV Data Files
```
daily_env_cost_2026-03-10.csv              # Detailed cost breakdown by environment
daily_env_summary_2026-03-10.csv           # Environment-level summary
daily_env_trends_2026-03-10.csv            # 30-day historical trends
daily_governance_summary_2026-03-10.csv    # Governance metrics
daily_env_governance_2026-03-10.csv        # Per-environment governance
daily_anomalies_2026-03-10.csv             # Detected anomalies
daily_budget_tracking_2026-03-10.csv       # Budget status
daily_cost_forecasts_2026-03-10.csv        # Cost forecasts
daily_optimizations_2026-03-10.csv         # Optimization opportunities
daily_env_anomaly_costs_2026-03-10.csv     # Anomaly costs by environment
daily_env_optimization_costs_2026-03-10.csv # Optimization potential by environment
daily_env_budget_summary_2026-03-10.csv    # Budget summary by environment
daily_env_service_costs_prod_2026-03-10.csv # Service costs for prod environment
daily_env_service_costs_dev_2026-03-10.csv  # Service costs for dev environment
daily_env_service_costs_uat_2026-03-10.csv  # Service costs for uat environment
daily_env_resource_counts_2026-03-10.csv   # Resource counts by environment
daily_env_governance_details_2026-03-10.csv # Detailed governance metrics
daily_env_comprehensive_summary_2026-03-10.csv # Complete environment summary
```

## Weekly Report Files

### PDF Report
```
Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf
```
Main comprehensive PDF report for a 7-day period.

### CSV Data Files
```
weekly_env_cost_2026-03-04_to_2026-03-10.csv              # Aggregated weekly costs
weekly_env_summary_2026-03-04_to_2026-03-10.csv           # Environment-level summary
weekly_daily_trends_2026-03-04_to_2026-03-10.csv          # 30-day historical trends
weekly_governance_2026-03-04_to_2026-03-10.csv            # Governance metrics
weekly_anomalies_2026-03-04_to_2026-03-10.csv             # Detected anomalies
weekly_budget_tracking_2026-03-04_to_2026-03-10.csv       # Budget status
weekly_cost_forecasts_2026-03-04_to_2026-03-10.csv        # Cost forecasts
weekly_optimizations_2026-03-04_to_2026-03-10.csv         # Optimization opportunities
weekly_env_anomaly_costs_2026-03-04_to_2026-03-10.csv     # Anomaly costs by environment
weekly_env_optimization_costs_2026-03-04_to_2026-03-10.csv # Optimization potential
weekly_env_budget_summary_2026-03-04_to_2026-03-10.csv    # Budget summary
weekly_env_service_costs_prod_2026-03-04_to_2026-03-10.csv # Service costs for prod
weekly_env_service_costs_dev_2026-03-04_to_2026-03-10.csv  # Service costs for dev
weekly_env_service_costs_uat_2026-03-04_to_2026-03-10.csv  # Service costs for uat
weekly_env_resource_counts_2026-03-04_to_2026-03-10.csv   # Resource counts
weekly_env_governance_details_2026-03-04_to_2026-03-10.csv # Detailed governance
weekly_env_comprehensive_summary_2026-03-04_to_2026-03-10.csv # Complete summary
```

## Chart Files

Charts are stored in the `charts/` subdirectory and are shared between reports:

```
charts/
├── env_comparison.png          # Environment cost comparison bar chart
├── 7day_trend.png             # 7-day cost trend line chart (daily)
├── 30day_trend.png            # 30-day cost trend line chart (weekly)
├── dod_changes.png            # Day-over-day changes (daily only)
├── top_resources.png          # Top cost resources
├── service_pie_prod.png       # Production service breakdown pie chart
└── budget_tracking.png        # Budget tracking chart
```

## Benefits of This Naming Convention

1. **Easy Sorting**: Files sort chronologically by default
2. **Clear Identification**: Report type is immediately visible
3. **No Conflicts**: Daily and weekly files never overwrite each other
4. **Searchable**: Easy to find specific report types or date ranges
5. **Automated Processing**: Scripts can easily parse file names
6. **Human Readable**: Anyone can understand what the file contains

## Examples

### Finding All Daily Reports for March 2026
```bash
ls finops_reports/Daily_FinOps_Report_2026-03-*.pdf
```

### Finding All Weekly Budget Tracking Files
```bash
ls finops_reports/weekly_budget_tracking_*.csv
```

### Finding All Reports for a Specific Date
```bash
ls finops_reports/*_2026-03-10.*
```

### Finding All Anomaly Reports
```bash
ls finops_reports/*_anomalies_*.csv
```

## Migration from Old Naming

If you have old reports without the `daily_` or `weekly_` prefix, they are daily reports. You can identify them by:
- Single date format (not date range)
- No prefix in the filename
- Generated before this naming convention was implemented

Example old format:
```
Enhanced_Daily_FinOps_Report_2026-03-10.pdf  # Old format
Daily_FinOps_Report_2026-03-10.pdf           # New format
```
