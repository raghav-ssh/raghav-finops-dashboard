# Report Structure Overview

## Report Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    run_report.py                            │
│                  (Entry Point)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ --type daily/weekly/both
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────────┐      ┌───────────────────┐
│  Daily Reporter   │      │  Weekly Reporter  │
│                   │      │                   │
│ DailyEnvFinOps    │      │ WeeklyEnvFinOps   │
│ Reporter          │      │ Reporter          │
└────────┬──────────┘      └────────┬──────────┘
         │                          │
         │                          │
         ▼                          ▼
┌─────────────────────────────────────────────┐
│         Shared Services                     │
│  ┌──────────────────────────────────────┐  │
│  │ • AnomalyDetector                    │  │
│  │ • BudgetTracker                      │  │
│  │ • CostOptimizer                      │  │
│  │ • CostForecaster                     │  │
│  │ • EnvCostAnalyzer                    │  │
│  │ • NotificationService                │  │
│  │ • EnhancedChartGenerator             │  │
│  │ • PDFReportGenerator                 │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
┌─────────────────┐      ┌─────────────────┐
│  Daily Outputs  │      │ Weekly Outputs  │
│                 │      │                 │
│ • PDF Report    │      │ • PDF Report    │
│ • CSV Files     │      │ • CSV Files     │
│ • Charts        │      │ • Charts        │
└─────────────────┘      └─────────────────┘
```

## Report Components

### Daily Report
```
Daily_FinOps_Report_2026-03-10.pdf
├── Executive Summary
│   ├── Daily Total Cost
│   ├── Active Environments
│   ├── Anomalies Detected
│   └── Unlabeled Spend
├── Cost Trends & Highlights
│   ├── 7-day Trend Chart
│   ├── Environment Comparison
│   └── Day-over-Day Changes
├── Environment-wise Breakdown
│   ├── Cost by Environment
│   ├── Resource Counts
│   └── Top Resources
├── Cost Forecasting
│   ├── Next 7 Days
│   └── Next 30 Days
├── Budget Tracking
│   ├── Budget Status
│   ├── Projected Usage
│   └── Alerts
├── Service Breakdown
│   └── Production Services
├── Anomalies & Alerts
│   ├── Critical Issues
│   └── Warnings
└── Optimization Opportunities
    ├── Idle Resources
    ├── Unattached Disks
    └── Potential Savings
```

### Weekly Report
```
Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf
├── Executive Summary
│   ├── Weekly Total Cost
│   ├── Daily Average Cost
│   ├── Active Environments
│   ├── Anomalies Detected
│   └── Unlabeled Spend
├── Cost Trends & Highlights
│   ├── 30-day Trend Chart
│   ├── Environment Comparison
│   └── Weekly Patterns
├── Environment-wise Breakdown
│   ├── Cost by Environment
│   ├── Resource Counts
│   └── Top Resources
├── Cost Forecasting
│   ├── Next 7 Days
│   └── Next 30 Days
├── Budget Tracking
│   ├── Budget Status
│   ├── Projected Usage
│   └── Alerts
├── Service Breakdown
│   └── Production Services
├── Anomalies & Alerts
│   ├── Critical Issues
│   └── Warnings
└── Optimization Opportunities
    ├── Idle Resources
    ├── Unattached Disks
    └── Potential Savings
```

## Data Flow

```
┌──────────────┐
│  BigQuery    │
│  (GCP Data)  │
└──────┬───────┘
       │
       │ SQL Queries
       │
       ▼
┌──────────────────────────────────────┐
│  Data Collection                     │
│  • fetch_daily_env_costs()           │
│  • fetch_env_summary()               │
│  • fetch_daily_trends()              │
│  • calculate_governance_metrics()    │
└──────┬───────────────────────────────┘
       │
       │ Raw Data
       │
       ▼
┌──────────────────────────────────────┐
│  Analysis Services                   │
│  • detect_anomalies()                │
│  • track_budgets()                   │
│  • forecast_costs()                  │
│  • find_optimizations()              │
│  • generate_env_cost_analysis()      │
└──────┬───────────────────────────────┘
       │
       │ Analyzed Data
       │
       ▼
┌──────────────────────────────────────┐
│  Visualization                       │
│  • generate_charts()                 │
│  • create_comparison_charts()        │
│  • create_trend_charts()             │
└──────┬───────────────────────────────┘
       │
       │ Charts + Data
       │
       ▼
┌──────────────────────────────────────┐
│  Report Generation                   │
│  • generate_pdf_report()             │
│  • save_csv_files()                  │
└──────┬───────────────────────────────┘
       │
       │ Reports
       │
       ▼
┌──────────────────────────────────────┐
│  Notifications (Optional)            │
│  • send_notifications()              │
│  • send_anomaly_alert()              │
│  • send_daily_summary()              │
└──────────────────────────────────────┘
```

## File Organization

```
backend/finops_reports/
│
├── PDF Reports
│   ├── Daily_FinOps_Report_2026-03-10.pdf
│   ├── Daily_FinOps_Report_2026-03-09.pdf
│   ├── Weekly_FinOps_Report_2026-03-04_to_2026-03-10.pdf
│   └── Weekly_FinOps_Report_2026-02-26_to_2026-03-03.pdf
│
├── Daily CSV Files
│   ├── daily_env_cost_2026-03-10.csv
│   ├── daily_env_summary_2026-03-10.csv
│   ├── daily_env_trends_2026-03-10.csv
│   ├── daily_anomalies_2026-03-10.csv
│   ├── daily_budget_tracking_2026-03-10.csv
│   ├── daily_cost_forecasts_2026-03-10.csv
│   ├── daily_optimizations_2026-03-10.csv
│   └── daily_env_*_2026-03-10.csv
│
├── Weekly CSV Files
│   ├── weekly_env_cost_2026-03-04_to_2026-03-10.csv
│   ├── weekly_env_summary_2026-03-04_to_2026-03-10.csv
│   ├── weekly_daily_trends_2026-03-04_to_2026-03-10.csv
│   ├── weekly_anomalies_2026-03-04_to_2026-03-10.csv
│   ├── weekly_budget_tracking_2026-03-04_to_2026-03-10.csv
│   ├── weekly_cost_forecasts_2026-03-04_to_2026-03-10.csv
│   ├── weekly_optimizations_2026-03-04_to_2026-03-10.csv
│   └── weekly_env_*_2026-03-04_to_2026-03-10.csv
│
└── charts/
    ├── env_comparison.png
    ├── 7day_trend.png
    ├── 30day_trend.png
    ├── dod_changes.png
    ├── top_resources.png
    ├── service_pie_prod.png
    └── budget_tracking.png
```

## Class Structure

```
DailyEnvFinOpsReporter
├── __init__()
│   ├── Initialize BigQuery client
│   ├── Initialize chart generator
│   ├── Calculate dates (yesterday)
│   └── Initialize all services
├── fetch_daily_env_costs()
├── fetch_env_summary()
├── fetch_daily_trends()
├── calculate_governance_metrics()
├── generate_charts()
├── detect_anomalies()
├── track_budgets()
├── forecast_costs()
├── find_optimizations()
├── generate_env_cost_analysis()
├── generate_pdf_report()
├── send_notifications()
└── run()

WeeklyEnvFinOpsReporter
├── __init__()
│   ├── Initialize BigQuery client
│   ├── Initialize chart generator
│   ├── Calculate dates (last 7 days)
│   └── Initialize all services
├── fetch_weekly_env_costs()
├── fetch_env_summary()
├── fetch_daily_trends()
├── calculate_governance_metrics()
├── generate_charts()
├── detect_anomalies()
├── track_budgets()
├── forecast_costs()
├── find_optimizations()
├── generate_env_cost_analysis()
├── generate_pdf_report()
├── send_notifications()
└── run()
```

## Shared Services

All services are used by both daily and weekly reporters:

```
services/
├── anomaly_detector.py
│   └── AnomalyDetector
│       ├── detect_dod_spikes()
│       ├── detect_unlabeled_issues()
│       ├── detect_budget_alerts()
│       └── generate_summary()
│
├── budget_tracker.py
│   └── BudgetTracker
│       ├── calculate_budget_status()
│       ├── generate_budget_report()
│       └── get_critical_budgets()
│
├── cost_optimizer.py
│   └── CostOptimizer
│       ├── find_idle_compute_instances()
│       ├── find_unattached_disks()
│       ├── find_oversized_resources()
│       └── analyze_commitment_opportunities()
│
├── cost_forecaster.py
│   └── CostForecaster
│       ├── forecast_costs()
│       ├── generate_forecast_report()
│       └── get_summary_metrics()
│
├── env_cost_analyzer.py
│   └── EnvCostAnalyzer
│       ├── get_env_anomaly_costs()
│       ├── get_env_optimization_costs()
│       ├── get_env_budget_summary()
│       └── generate_env_summary_report()
│
└── notification_service.py
    └── NotificationService
        ├── send_anomaly_alert()
        └── send_daily_summary()
```

## Configuration

```
core/config.py
├── GCPConfig
│   ├── project_id
│   ├── dataset
│   └── table
│
├── ReportConfig
│   ├── output_dir (finops_reports/)
│   ├── chart_dir (finops_reports/charts/)
│   ├── monthly_budget
│   └── currency_symbol
│
└── GovernanceConfig
    ├── required_label
    ├── alert_threshold
    └── slack_webhook
```
