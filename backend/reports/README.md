# FinOps Report Generation

This module generates comprehensive FinOps reports for GCP cost analysis with separate daily and weekly reporting capabilities.

## Report Types

### Daily Report
- **File**: `daily_env_finops_enhanced.py`
- **Class**: `DailyEnvFinOpsReporter`
- **Coverage**: Single day (yesterday's data)
- **Output**: `Daily_FinOps_Report_YYYY-MM-DD.pdf`
- **CSV Prefix**: `daily_*`

### Weekly Report
- **File**: `weekly_env_finops_report.py`
- **Class**: `WeeklyEnvFinOpsReporter`
- **Coverage**: Last 7 complete days
- **Output**: `Weekly_FinOps_Report_YYYY-MM-DD_to_YYYY-MM-DD.pdf`
- **CSV Prefix**: `weekly_*`

## Usage

### Generate Daily Report
```bash
python backend/run_report.py --type daily
```

### Generate Weekly Report
```bash
python backend/run_report.py --type weekly
```

### Generate Both Reports
```bash
python backend/run_report.py --type both
```

### Skip Notifications
```bash
python backend/run_report.py --type daily --no-notifications
```

## Output Structure

All reports are saved to `backend/finops_reports/` with clear naming conventions:

### Daily Report Files
- `Daily_FinOps_Report_YYYY-MM-DD.pdf` - Main PDF report
- `daily_env_cost_YYYY-MM-DD.csv` - Detailed cost breakdown
- `daily_env_summary_YYYY-MM-DD.csv` - Environment summary
- `daily_env_trends_YYYY-MM-DD.csv` - 30-day trend data
- `daily_anomalies_YYYY-MM-DD.csv` - Detected anomalies
- `daily_budget_tracking_YYYY-MM-DD.csv` - Budget status
- `daily_cost_forecasts_YYYY-MM-DD.csv` - Cost forecasts
- `daily_optimizations_YYYY-MM-DD.csv` - Optimization opportunities
- `daily_env_*_YYYY-MM-DD.csv` - Various environment analyses

### Weekly Report Files
- `Weekly_FinOps_Report_YYYY-MM-DD_to_YYYY-MM-DD.pdf` - Main PDF report
- `weekly_env_cost_YYYY-MM-DD_to_YYYY-MM-DD.csv` - Aggregated weekly costs
- `weekly_env_summary_YYYY-MM-DD_to_YYYY-MM-DD.csv` - Environment summary
- `weekly_daily_trends_YYYY-MM-DD_to_YYYY-MM-DD.csv` - 30-day trend data
- `weekly_anomalies_YYYY-MM-DD_to_YYYY-MM-DD.csv` - Detected anomalies
- `weekly_budget_tracking_YYYY-MM-DD_to_YYYY-MM-DD.csv` - Budget status
- `weekly_cost_forecasts_YYYY-MM-DD_to_YYYY-MM-DD.csv` - Cost forecasts
- `weekly_optimizations_YYYY-MM-DD_to_YYYY-MM-DD.csv` - Optimization opportunities
- `weekly_env_*_YYYY-MM-DD_to_YYYY-MM-DD.csv` - Various environment analyses

## Report Contents

Both daily and weekly reports include:

1. **Executive Summary** - Key metrics and totals
2. **Cost Trends & Highlights** - Visual charts and comparisons
3. **Environment-wise Breakdown** - Detailed per-environment analysis
4. **Cost Forecasting** - Projected costs for next 7 and 30 days
5. **Budget Tracking** - Budget usage and alerts
6. **Service Breakdown** - Cost by GCP service
7. **Anomalies & Alerts** - Critical issues and warnings
8. **Optimization Opportunities** - Cost-saving recommendations

## Key Differences

### Daily Report
- Focuses on single-day snapshot
- Day-over-day change analysis
- Immediate anomaly detection
- Best for: Daily monitoring, quick checks, immediate alerts

### Weekly Report
- Aggregates 7 days of data
- Shows weekly trends and patterns
- Better for: Strategic planning, trend analysis, weekly reviews
- Includes daily average calculations

## Automation

You can schedule these reports using cron:

```bash
# Daily report at 8 AM
0 8 * * * cd /path/to/project && python backend/run_report.py --type daily

# Weekly report every Monday at 9 AM
0 9 * * 1 cd /path/to/project && python backend/run_report.py --type weekly
```

## Dependencies

All reports use shared services:
- `AnomalyDetector` - Identifies cost anomalies
- `BudgetTracker` - Monitors budget usage
- `CostOptimizer` - Finds savings opportunities
- `CostForecaster` - Predicts future costs
- `EnvCostAnalyzer` - Environment-wise analysis
- `NotificationService` - Email/Slack alerts
- `EnhancedChartGenerator` - Visual charts
- `PDFReportGenerator` - PDF creation
