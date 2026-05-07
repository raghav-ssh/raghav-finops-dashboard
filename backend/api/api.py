"""
FastAPI Backend for FinOps Dashboard.
Provides REST API endpoints for cost analytics and reporting.
"""
import datetime
import os
import subprocess
from pathlib import Path
from typing import Optional

import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from reports.daily_env_finops_enhanced import DailyEnvFinOpsReporter
from reports.weekly_env_finops_report import WeeklyEnvFinOpsReporter
from core.logger import setup_logger
from core.budgets import get_budgets, update_budgets
from core.config import FINOPS_REPORT_CONFIG

logger = setup_logger(__name__)

app = FastAPI(
    title="FinOps Dashboard Backend",
    description="Cost analytics and reporting API",
    version="1.0.0",
    root_path="/ssh-gcp-costing-backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache to prevent excessive BQ queries
cache = {}


@app.get("/api/dashboard")
def get_dashboard_data(
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    refresh: bool = Query(False, description="Force refresh cache"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get dashboard data for specified period.
    
    Args:
        period: Reporting period (daily, weekly, monthly)
        refresh: Force cache refresh
        start_date: Optional custom start date
        end_date: Optional custom end date
        
    Returns:
        Dashboard data with cost trends, environments, and alerts
    """
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    cache_key = f"{today_str}_{period}_{start_date}_{end_date}"
    
    # Return from cache if available and not refreshing
    if not refresh and cache_key in cache:
        logger.info(f"Returning cached data for {cache_key}")
        return cache[cache_key]
    
    logger.info(f"Fetching fresh data for period: {period}")
    
    # Instantiate reporter dynamically based on requested period
    if period == 'weekly':
        reporter = WeeklyEnvFinOpsReporter()
        # Override to use current week (Monday to Sunday)
        today = datetime.datetime.now().date()
        # Get the Monday of current week (0 = Monday, 6 = Sunday)
        days_since_monday = today.weekday()  # 0 = Monday, 6 = Sunday
        week_start = today - datetime.timedelta(days=days_since_monday)
        # If today is Monday, use last week's data (Monday to Sunday)
        # Otherwise use Monday of this week to yesterday
        if days_since_monday == 0:
            # Today is Monday, use last week
            week_start = today - datetime.timedelta(days=7)
            week_end = today - datetime.timedelta(days=1)
        else:
            # Use this week's Monday to yesterday
            week_end = today - datetime.timedelta(days=1)
        
        reporter.start_date = week_start
        reporter.end_date = week_end
        reporter.date_range = f"{week_start}_to_{week_end}"
        logger.info(f"Weekly period: {week_start} to {week_end}")
        
    elif period == 'monthly':
        # For monthly, use daily reporter but with full month date range
        reporter = DailyEnvFinOpsReporter()
        # Set to first day of current month through yesterday
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        reporter.start_date = yesterday.replace(day=1)
        reporter.end_date = yesterday
        reporter.report_date = str(yesterday)
    else:  # daily
        # Daily reporter already defaults to yesterday only
        reporter = DailyEnvFinOpsReporter()
    
    # Override dates if custom range provided
    if start_date and end_date:
        try:
            reporter.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            reporter.end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            if period == 'weekly':
                reporter.date_range = f"{start_date}_to_{end_date}"
            else:
                reporter.report_date = start_date
            logger.info(f"Using custom date range: {start_date} to {end_date}")
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            # Continue with default dates
    
    try:
        # Fetch live backend data
        # Note: Weekly reporter has different method name for cost data
        if period == 'weekly':
            daily_df = reporter.fetch_weekly_env_costs()
            env_summary = reporter.fetch_env_summary(daily_df)
            trends_df = reporter.fetch_daily_trends()  # Same method name
        else:
            # Daily and monthly use the same methods
            daily_df = reporter.fetch_daily_env_costs()
            env_summary = reporter.fetch_env_summary(daily_df)
            trends_df = reporter.fetch_daily_trends()
        
        governance = reporter.calculate_governance_metrics(daily_df)
        
        # Normalize governance keys for different reporters
        # Weekly reporter uses 'weekly_total', daily uses 'daily_total'
        if 'weekly_total' in governance:
            governance['daily_total'] = governance['weekly_total']
        elif 'daily_total' not in governance:
            # Fallback: calculate from data
            governance['daily_total'] = daily_df['cost'].sum() if 'cost' in daily_df.columns else 0
        
        anomalies = reporter.detect_anomalies(trends_df, env_summary, governance)
        budget_statuses = reporter.track_budgets(env_summary)
        forecast_data = reporter.forecast_costs(trends_df)
        
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise
    
    # Transform into frontend-friendly JSON structure
    # Build cost trends
    date_sums = trends_df.groupby('date')['cost'].sum().reset_index().sort_values('date')
    
    if start_date and end_date:
        filter_start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        filter_end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        if period == 'daily':
            filter_start = reporter.end_date - datetime.timedelta(days=6)
            filter_end = reporter.end_date
        elif period == 'weekly':
            filter_start = reporter.end_date - datetime.timedelta(days=84)
            filter_end = reporter.end_date
        else:
            filter_start = reporter.end_date.replace(day=1)
            filter_end = reporter.end_date

    date_sums['date_obj'] = pd.to_datetime(date_sums['date']).dt.date
    date_sums = date_sums[
        (date_sums['date_obj'] >= filter_start) & 
        (date_sums['date_obj'] <= filter_end)
    ]
    
    # Calculate cost trend (compare current period vs previous period)
    cost_trend_percent = 0.0
    if len(date_sums) >= 2:
        # Get the most recent cost and compare to previous
        sorted_dates = date_sums.sort_values('date_obj', ascending=False)
        if period == 'daily':
            # Compare yesterday vs day before yesterday
            if len(sorted_dates) >= 2:
                current_cost = sorted_dates.iloc[0]['cost']
                previous_cost = sorted_dates.iloc[1]['cost']
                if previous_cost > 0:
                    cost_trend_percent = round(((current_cost - previous_cost) / previous_cost * 100), 1)
        elif period == 'weekly':
            # Compare this week vs last week
            # Get last 2 weeks of data
            all_dates = trends_df.groupby('date')['cost'].sum().reset_index().sort_values('date', ascending=False)
            if len(all_dates) >= 14:
                this_week_cost = all_dates.iloc[0:7]['cost'].sum()
                last_week_cost = all_dates.iloc[7:14]['cost'].sum()
                if last_week_cost > 0:
                    cost_trend_percent = round(((this_week_cost - last_week_cost) / last_week_cost * 100), 1)
        else:  # monthly
            # Compare this month vs last month (same day)
            current_day = reporter.end_date.day
            last_month_end = reporter.end_date.replace(day=1) - datetime.timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            last_month_same_day = min(current_day, last_month_end.day)
            
            # Get last month's data for comparison
            last_month_query = trends_df.copy()
            last_month_query['date_obj'] = pd.to_datetime(last_month_query['date']).dt.date
            last_month_data = last_month_query[
                (last_month_query['date_obj'] >= last_month_start) &
                (last_month_query['date_obj'] <= last_month_start + datetime.timedelta(days=last_month_same_day-1))
            ]
            
            if not last_month_data.empty:
                this_month_cost = governance.get('daily_total', 0)
                last_month_cost = last_month_data['cost'].sum()
                if last_month_cost > 0:
                    cost_trend_percent = round(((this_month_cost - last_month_cost) / last_month_cost * 100), 1)

    cost_trends = []
    # Format date based on period
    for _, row in date_sums.iterrows():
        if period == 'daily':
            date_str = pd.to_datetime(row['date']).strftime('%a')
        else:  # weekly or monthly
            date_str = pd.to_datetime(row['date']).strftime('%b %d')
            
        cost_trends.append({
            "date": date_str,
            "cost": float(row['cost'])
        })

    # Build environments breakdown
    budgets_data = get_budgets()  # Get all budgets with periods
    environments = []
    for _, row in env_summary.iterrows():
        env_name = row['env']
        env_anomalies = [
            a for a in anomalies 
            if a.environment == env_name or a.environment == 'ALL'
        ]
        budget = next(
            (b for b in budget_statuses if b.environment == env_name), 
            None
        )
        
        # Get period-specific budget amount
        env_budget_data = budgets_data.get(env_name, {})
        if isinstance(env_budget_data, dict):
            period_budget = float(env_budget_data.get(period, env_budget_data.get('monthly', 0)))
        else:
            # Old format - single number is monthly, calculate period budget
            monthly_budget = float(env_budget_data)
            if period == 'daily':
                period_budget = monthly_budget / 30
            elif period == 'weekly':
                period_budget = (monthly_budget / 30) * 7
            else:  # monthly
                period_budget = monthly_budget
        
        unlabeled_df = daily_df[
            (daily_df['env'] == env_name) & (daily_df['app'] == 'UNLABELED')
        ]
        unlabeled_cost = float(unlabeled_df['cost'].sum()) if not unlabeled_df.empty else 0.0
        total_cost = float(row['total_cost'])
        unlabeled_percent = (unlabeled_cost / total_cost * 100) if total_cost > 0 else 0
        
        environments.append({
            "name": str(env_name),
            "cost": total_cost,  # This is now period-specific cost
            "apps": int(row['app_count']),
            "anomalies": len(env_anomalies),
            "budgetStatus": str(budget.status.replace('_', ' ').title()) if budget else "N/A",
            "budgetAmount": period_budget,  # Period-specific budget
            "budgetUsed": total_cost,  # Use period cost instead of budget.actual_spend
            "budgetPercent": round((total_cost / period_budget * 100) if period_budget > 0 else 0, 1),
            "unlabeledPercent": round(unlabeled_percent, 1),
            "period": period  # Add period info for frontend
        })
    
    # Build critical alerts
    critical_alerts = []
    for anomaly in anomalies:
        if anomaly.severity == 'critical':
            critical_alerts.append({
                "env": str(anomaly.environment),
                "message": str(anomaly.message)
            })

    
    # Determine how many data points to return based on period just as a safety cap
    if period == 'daily':
        trend_limit = 7
    elif period == 'weekly':
        trend_limit = 12 * 7
    else:
        trend_limit = 31
    
    # Build final response
    result = {
        "summary": {
            "dailyTotalCost": float(governance['daily_total']),
            "costTrendPercent": cost_trend_percent,  # Add trend percentage
            "envCount": int(governance['env_count']),
            "anomalies": { 
                "total": len(anomalies), 
                "critical": len(critical_alerts) 
            },
            "unlabeledSpend": { 
                "amount": float(governance['unlabeled_spend']), 
                "percent": float(governance['unlabeled_percent']) 
            }
        },
        "costTrends": cost_trends[-trend_limit:],
        "environments": environments,
        "criticalAlerts": critical_alerts,
        "forecast": forecast_data.get("summary", {}) if forecast_data else {},
        "forecastsDetails": {k: v.__dict__ for k, v in forecast_data.get("forecasts", {}).items()} if forecast_data else {}
    }
    
    cache[cache_key] = result
    logger.info(f"Data cached for {cache_key}")
    return result


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "finops-api"}


@app.get("/api/download-report")
def download_report(
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Download report data in PDF format.
    
    Args:
        period: Reporting period (daily, weekly, monthly)
        start_date: Optional custom start date
        end_date: Optional custom end date
        
    Returns:
        PDF report file
    """
    logger.info(f"Generating PDF report for period: {period}")
    
    # Instantiate reporter
    if period == 'weekly':
        reporter = WeeklyEnvFinOpsReporter()
    else:
        reporter = DailyEnvFinOpsReporter()
    
    # Override dates if custom range provided
    if start_date and end_date:
        try:
            reporter.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            reporter.end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            if period == 'weekly':
                reporter.date_range = f"{start_date}_to_{end_date}"
            else:
                reporter.report_date = start_date
            logger.info(f"Using custom date range for download: {start_date} to {end_date}")
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
    
    try:
        # Fetch data
        logger.info("Fetching data for PDF report...")
        if period == 'weekly':
            daily_df = reporter.fetch_weekly_env_costs()
        else:
            daily_df = reporter.fetch_daily_env_costs()
            
        env_summary = reporter.fetch_env_summary(daily_df)
        trends_df = reporter.fetch_daily_trends()
        governance = reporter.calculate_governance_metrics(daily_df)
        anomalies = reporter.detect_anomalies(trends_df, env_summary, governance)
        budget_statuses = reporter.track_budgets(env_summary)
        
        logger.info("Generating charts...")
        charts = reporter.generate_charts(daily_df, env_summary, trends_df)
        
        logger.info("Finding optimizations...")
        optimizations = reporter.find_optimizations(daily_df)
        
        logger.info("Generating environment analysis...")
        env_analysis = reporter.generate_env_cost_analysis(
            daily_df, anomalies, optimizations, budget_statuses
        )
        
        logger.info("Generating PDF report...")
        # Generate PDF
        pdf_path = reporter.generate_pdf_report(
            daily_df=daily_df,
            env_summary=env_summary,
            trends_df=trends_df,
            governance=governance,
            charts=charts,
            anomalies=anomalies,
            budget_statuses=budget_statuses,
            optimizations=optimizations,
            env_analysis=env_analysis
        )
        
        if pdf_path and pdf_path.exists():
            logger.info(f"PDF generated successfully: {pdf_path}")
            return FileResponse(
                path=str(pdf_path),
                media_type="application/pdf",
                filename=f"finops_report_{period}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
            )
        else:
            logger.error("PDF file not found after generation")
            raise HTTPException(status_code=500, detail="PDF generation failed - file not created")
            
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


class BudgetsUpdate(BaseModel):
    budgets: dict

@app.get("/api/budgets")
def api_get_budgets():
    """Get current budgets configured for the environments."""
    return get_budgets()

@app.post("/api/budgets")
def api_update_budgets(data: BudgetsUpdate):
    """Update budgets for the environments."""
    try:
        updated = update_budgets(data.budgets)
        return {"status": "success", "budgets": updated}
    except Exception as e:
        logger.error(f"Error updating budgets: {e}")
        raise HTTPException(status_code=500, detail="Failed to update budgets")


# New Report Management Endpoints

@app.get("/api/reports/list")
def list_reports():
    """
    List all available daily and weekly reports.
    
    Returns:
        Dictionary with daily and weekly report lists
    """
    try:
        output_dir = FINOPS_REPORT_CONFIG.output_dir
        
        daily_reports = []
        weekly_reports = []
        
        if output_dir.exists():
            # Find daily reports
            for pdf_file in output_dir.glob("Daily_FinOps_Report_*.pdf"):
                stat = pdf_file.stat()
                daily_reports.append({
                    "filename": pdf_file.name,
                    "size": stat.st_size,
                    "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            # Find weekly reports
            for pdf_file in output_dir.glob("Weekly_FinOps_Report_*.pdf"):
                stat = pdf_file.stat()
                weekly_reports.append({
                    "filename": pdf_file.name,
                    "size": stat.st_size,
                    "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by modified date (newest first)
        daily_reports.sort(key=lambda x: x['modified'], reverse=True)
        weekly_reports.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            "daily": daily_reports,
            "weekly": weekly_reports
        }
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing reports: {str(e)}")


class ReportGenerateRequest(BaseModel):
    type: str  # 'daily' or 'weekly'

@app.post("/api/reports/generate")
def generate_report(request: ReportGenerateRequest):
    """
    Generate a new daily or weekly report.
    
    Args:
        request: Report generation request with type
        
    Returns:
        Status and generated report filename
    """
    try:
        report_type = request.type.lower()
        
        if report_type not in ['daily', 'weekly']:
            raise HTTPException(status_code=400, detail="Invalid report type. Must be 'daily' or 'weekly'")
        
        logger.info(f"Generating {report_type} report via API...")
        
        # Run the report generation script
        script_path = Path(__file__).parent.parent / "run_report.py"
        result = subprocess.run(
            ["python3", str(script_path), "--type", report_type, "--no-notifications"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Report generation failed: {result.stderr}")
            raise HTTPException(
                status_code=500, 
                detail=f"Report generation failed: {result.stderr}"
            )
        
        logger.info(f"{report_type.capitalize()} report generated successfully")
        
        # Find the newly generated report
        output_dir = FINOPS_REPORT_CONFIG.output_dir
        if report_type == 'daily':
            pattern = "Daily_FinOps_Report_*.pdf"
        else:
            pattern = "Weekly_FinOps_Report_*.pdf"
        
        reports = list(output_dir.glob(pattern))
        if reports:
            # Get the most recent report
            latest_report = max(reports, key=lambda p: p.stat().st_mtime)
            return {
                "status": "success",
                "message": f"{report_type.capitalize()} report generated successfully",
                "filename": latest_report.name
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Report generated but file not found"
            )
            
    except subprocess.TimeoutExpired:
        logger.error("Report generation timed out")
        raise HTTPException(status_code=504, detail="Report generation timed out")
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@app.get("/api/reports/download/{report_type}/{filename}")
def download_report_file(report_type: str, filename: str):
    """
    Download a specific report file.
    
    Args:
        report_type: 'daily' or 'weekly'
        filename: Name of the report file
        
    Returns:
        PDF file
    """
    try:
        if report_type not in ['daily', 'weekly']:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        output_dir = FINOPS_REPORT_CONFIG.output_dir
        file_path = output_dir / filename
        
        # Security check: ensure file is in the output directory
        if not file_path.resolve().is_relative_to(output_dir.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report file not found")
        
        if not file_path.suffix == '.pdf':
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        logger.info(f"Downloading report: {filename}")
        
        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading report: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FinOps API server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
