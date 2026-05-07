"""
Weekly Environment-wise FinOps Report Generator
Aggregates weekly cost data with trends, anomalies, and optimization recommendations.
"""
from datetime import datetime, timedelta
from pathlib import Path
import calendar
import pandas as pd

from core.bigquery_client import BigQueryClient
from core.config import GCP_CONFIG, FINOPS_REPORT_CONFIG
from core.logger import setup_logger
from reports.pdf_generator import PDFReportGenerator
from core.queries import CostQueries
from reports.enhanced_chart_generator import EnhancedChartGenerator
from services.anomaly_detector import AnomalyDetector
from services.budget_tracker import BudgetTracker
from services.cost_optimizer import CostOptimizer
from services.notification_service import NotificationService
from services.env_cost_analyzer import EnvCostAnalyzer
from services.cost_forecaster import CostForecaster


logger = setup_logger(__name__)


class WeeklyEnvFinOpsReporter:
    """Generate weekly environment-wise FinOps reports."""
    
    def __init__(self):
        """Initialize the weekly environment FinOps reporter."""
        self.config = FINOPS_REPORT_CONFIG
        self.gcp_config = GCP_CONFIG
        self.bq_client = BigQueryClient(self.gcp_config)
        self.chart_gen = EnhancedChartGenerator(self.config.chart_dir)
        
        # Calculate dates - last 7 complete days
        self.today = datetime.utcnow().date()
        self.end_date = self.today - timedelta(days=1)
        self.start_date = self.end_date - timedelta(days=6)  # 7 days total
        self.date_range = f"{self.start_date}_to_{self.end_date}"
        
        self.days_in_month = calendar.monthrange(self.today.year, self.today.month)[1]
        
        # Environment budgets
        from core.budgets import get_budgets
        self.budgets = get_budgets()
        
        # Initialize services
        self.anomaly_detector = AnomalyDetector()
        self.budget_tracker = BudgetTracker(self.budgets, period='weekly')
        self.cost_optimizer = CostOptimizer(self.gcp_config, self.bq_client)
        self.notifier = NotificationService()
        self.env_analyzer = EnvCostAnalyzer()
        self.cost_forecaster = CostForecaster()
        
        logger.info(f"Weekly FinOps reporter initialized for: {self.date_range}")

    def fetch_weekly_env_costs(self) -> pd.DataFrame:
        """Fetch weekly cost breakdown by environment, app, service, and region."""
        logger.info("Fetching weekly environment cost details...")
        
        query = CostQueries.period_cost_detail(
            self.gcp_config.full_table_path,
            self.start_date,
            self.end_date,
            min_cost=10.0
        )
        
        df = self.bq_client.execute_query(query)
        
        # Save to CSV
        csv_path = self.config.output_dir / f"weekly_env_cost_{self.date_range}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Weekly environment costs saved to: {csv_path}")
        
        return df
    
    def fetch_env_summary(self, weekly_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate environment-level cost summary for the week."""
        logger.info("Calculating weekly environment summary...")
        
        env_summary = weekly_df.groupby('env').agg({
            'cost': 'sum',
            'app': 'nunique',
            'service': 'nunique'
        }).reset_index()
        
        env_summary.columns = ['env', 'total_cost', 'app_count', 'service_count']
        env_summary = env_summary.sort_values('total_cost', ascending=False)
        
        # Save to CSV
        csv_path = self.config.output_dir / f"weekly_env_summary_{self.date_range}.csv"
        env_summary.to_csv(csv_path, index=False)
        logger.info(f"Weekly environment summary saved to: {csv_path}")
        
        return env_summary
    
    def fetch_daily_trends(self) -> pd.DataFrame:
        """Fetch daily cost trends for the past 30 days by environment."""
        logger.info("Fetching 30-day cost trends by environment...")
        
        trend_start_date = self.end_date - timedelta(days=29)
        
        query = f"""
        SELECT
            DATE(usage_start_time) AS date,
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS cost
        FROM `{self.gcp_config.full_table_path}`
        WHERE DATE(usage_start_time) >= "{trend_start_date}"
            AND DATE(usage_start_time) <= "{self.end_date}"
        GROUP BY date, env
        ORDER BY date DESC, cost DESC
        """
        
        df = self.bq_client.execute_query(query)
        
        # Save to CSV
        csv_path = self.config.output_dir / f"weekly_daily_trends_{self.date_range}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Daily trends saved to: {csv_path}")
        
        return df
    
    def calculate_governance_metrics(self, weekly_df: pd.DataFrame) -> dict:
        """Calculate governance and compliance metrics for the week."""
        logger.info("Calculating weekly governance metrics...")
        
        total_cost = weekly_df['cost'].sum()
        unlabeled_spend = weekly_df[weekly_df['env'] == 'UNLABELED']['cost'].sum()
        unlabeled_percent = round((unlabeled_spend / total_cost * 100), 2) if total_cost > 0 else 0
        
        metrics = {
            'weekly_total': total_cost,
            'daily_average': total_cost / 7,
            'unlabeled_spend': unlabeled_spend,
            'unlabeled_percent': unlabeled_percent,
            'env_count': len(weekly_df['env'].unique())
        }
        
        # Save to CSV
        governance_df = pd.DataFrame([metrics])
        csv_path = self.config.output_dir / f"weekly_governance_{self.date_range}.csv"
        governance_df.to_csv(csv_path, index=False)
        logger.info(f"Weekly governance metrics saved to: {csv_path}")
        
        return metrics
    
    def generate_charts(
        self,
        weekly_df: pd.DataFrame,
        env_summary: pd.DataFrame,
        trends_df: pd.DataFrame
    ) -> dict:
        """Generate all charts for weekly report."""
        logger.info("Generating weekly charts...")
        
        charts = {}
        
        # Environment comparison
        charts['env_comparison'] = self.chart_gen.create_env_comparison_chart(env_summary)
        
        # 30-day trend (showing full month context)
        charts['30day_trend'] = self.chart_gen.create_7day_trend_chart(trends_df)
        
        # Top resources
        charts['top_resources'] = self.chart_gen.create_top_resources_chart(weekly_df)
        
        # Service breakdown for prod
        if 'prod' in env_summary['env'].values:
            charts['service_pie_prod'] = self.chart_gen.create_service_breakdown_pie(
                weekly_df, 'prod'
            )
        
        # Budget tracking
        charts['budget_tracking'] = self.chart_gen.create_budget_tracking_chart(
            env_summary,
            self.budgets,
            self.days_in_month,
            self.today.day
        )
        
        logger.info(f"Generated {len(charts)} charts")
        return charts
    
    def detect_anomalies(
        self,
        trends_df: pd.DataFrame,
        env_summary: pd.DataFrame,
        governance: dict
    ) -> list:
        """Detect cost anomalies in weekly data."""
        logger.info("Detecting weekly anomalies...")
        
        # Unlabeled issues
        self.anomaly_detector.detect_unlabeled_issues(governance)
        
        # Budget alerts
        self.anomaly_detector.detect_budget_alerts(
            env_summary,
            self.budgets,
            self.days_in_month,
            self.today.day
        )
        
        anomalies = self.anomaly_detector.get_all_anomalies()
        
        # Save anomalies to CSV
        if anomalies:
            anomaly_data = [{
                'severity': a.severity,
                'category': a.category,
                'environment': a.environment,
                'message': a.message,
                'current_value': a.current_value,
                'threshold_value': a.threshold_value
            } for a in anomalies]
            
            anomaly_df = pd.DataFrame(anomaly_data)
            csv_path = self.config.output_dir / f"weekly_anomalies_{self.date_range}.csv"
            anomaly_df.to_csv(csv_path, index=False)
            logger.info(f"Weekly anomalies saved to: {csv_path}")
        
        summary = self.anomaly_detector.generate_summary()
        logger.info(f"Detected {summary['total']} anomalies")
        
        return anomalies
    
    def track_budgets(self, env_summary: pd.DataFrame) -> list:
        """Track budget usage for the week."""
        logger.info("Tracking weekly budgets...")
        
        budget_statuses = self.budget_tracker.calculate_budget_status(env_summary)
        
        # Save budget report
        budget_df = self.budget_tracker.generate_budget_report(budget_statuses)
        csv_path = self.config.output_dir / f"weekly_budget_tracking_{self.date_range}.csv"
        budget_df.to_csv(csv_path, index=False)
        logger.info(f"Weekly budget tracking saved to: {csv_path}")
        
        return budget_statuses
    
    def forecast_costs(self, trends_df: pd.DataFrame) -> dict:
        """Generate cost forecasts based on weekly trends."""
        logger.info("Generating weekly cost forecasts...")
        
        forecasts = self.cost_forecaster.forecast_costs(trends_df, forecast_days=30)
        
        # Save forecast report
        forecast_df = self.cost_forecaster.generate_forecast_report(forecasts)
        csv_path = self.config.output_dir / f"weekly_cost_forecasts_{self.date_range}.csv"
        forecast_df.to_csv(csv_path, index=False)
        logger.info(f"Weekly cost forecasts saved to: {csv_path}")
        
        summary = self.cost_forecaster.get_summary_metrics(forecasts)
        
        return {'forecasts': forecasts, 'summary': summary}
    
    def find_optimizations(self, weekly_df: pd.DataFrame) -> list:
        """Find cost optimization opportunities from weekly data."""
        logger.info("Finding weekly optimization opportunities...")
        
        # Find idle VMs
        self.cost_optimizer.find_idle_compute_instances(str(self.end_date))
        
        # Find unattached disks
        self.cost_optimizer.find_unattached_disks(str(self.end_date))
        
        # Find oversized resources
        self.cost_optimizer.find_oversized_resources(weekly_df)
        
        # Analyze commitment opportunities
        self.cost_optimizer.analyze_commitment_opportunities(weekly_df)
        
        opportunities = self.cost_optimizer.get_all_opportunities()
        total_savings = self.cost_optimizer.calculate_total_savings()
        
        # Save optimization report
        if opportunities:
            opt_df = self.cost_optimizer.generate_optimization_report()
            csv_path = self.config.output_dir / f"weekly_optimizations_{self.date_range}.csv"
            opt_df.to_csv(csv_path, index=False)
            logger.info(f"Weekly optimization opportunities saved to: {csv_path}")
        
        logger.info(f"Found {len(opportunities)} optimization opportunities "
                   f"with potential savings of ₹{total_savings:,.2f}/month")
        
        return opportunities
    
    def generate_env_cost_analysis(
        self,
        weekly_df: pd.DataFrame,
        anomalies: list,
        optimizations: list,
        budget_statuses: list
    ) -> dict:
        """Generate comprehensive environment-wise cost analysis for the week."""
        logger.info("Generating weekly environment-wise cost analysis...")
        
        analysis = {}
        
        # Environment anomaly costs
        analysis['env_anomaly_costs'] = self.env_analyzer.get_env_anomaly_costs(
            anomalies, weekly_df
        )
        
        # Environment optimization costs
        analysis['env_optimization_costs'] = self.env_analyzer.get_env_optimization_costs(
            optimizations, weekly_df
        )
        
        # Environment budget summary
        analysis['env_budget_summary'] = self.env_analyzer.get_env_budget_summary(
            budget_statuses, weekly_df
        )
        
        # Environment service costs
        analysis['env_service_costs'] = self.env_analyzer.get_env_service_costs(
            weekly_df, top_n=5
        )
        
        # Environment resource counts
        analysis['env_resource_counts'] = self.env_analyzer.get_env_resource_counts(
            weekly_df
        )
        
        # Environment governance details
        analysis['env_governance_details'] = self.env_analyzer.get_env_governance_details(
            weekly_df
        )
        
        # Comprehensive environment summary
        analysis['env_comprehensive_summary'] = self.env_analyzer.generate_env_summary_report(
            weekly_df, anomalies, optimizations, budget_statuses
        )
        
        # Save all analysis to CSV with weekly prefix
        for key, df in analysis.items():
            if isinstance(df, pd.DataFrame):
                csv_path = self.config.output_dir / f"weekly_{key}_{self.date_range}.csv"
                df.to_csv(csv_path, index=False)
                logger.info(f"Saved weekly {key} to: {csv_path}")
            elif isinstance(df, dict):
                # For env_service_costs which is a dict of DataFrames
                for env, env_df in df.items():
                    csv_path = self.config.output_dir / f"weekly_{key}_{env}_{self.date_range}.csv"
                    env_df.to_csv(csv_path, index=False)
        
        logger.info("Weekly environment-wise cost analysis complete")
        return analysis
    
    def generate_pdf_report(
        self,
        weekly_df: pd.DataFrame,
        env_summary: pd.DataFrame,
        trends_df: pd.DataFrame,
        governance: dict,
        charts: dict,
        anomalies: list,
        budget_statuses: list,
        optimizations: list,
        env_analysis: dict,
        forecast_data: dict = None
    ):
        """Generate comprehensive weekly PDF report."""
        logger.info("Generating weekly PDF report...")
        
        pdf_path = self.config.output_dir / f"Weekly_FinOps_Report_{self.date_range}.pdf"
        pdf = PDFReportGenerator(pdf_path)
        
        # 1. Cover page
        pdf.add_cover_page(
            title="Weekly FinOps Report",
            subtitle="7-Day Cost Analysis & Budget Tracking",
            date_str=f"{self.start_date} to {self.end_date}"
        )
        
        # 2. Executive Summary
        pdf.add_heading("Executive Summary")
        anomaly_summary = self.anomaly_detector.generate_summary()
        
        summary_data = [
            ["Metric", "Value"],
            ["Weekly Total Cost", f"{self.config.currency_symbol} {governance['weekly_total']:,.2f}"],
            ["Daily Average Cost", f"{self.config.currency_symbol} {governance['daily_average']:,.2f}"],
            ["Active Environments", str(governance['env_count'])],
            ["Unlabeled Spend", f"{self.config.currency_symbol} {governance['unlabeled_spend']:,.2f} ({governance['unlabeled_percent']}%)"],
        ]
        pdf.add_summary_table(summary_data)
        pdf.add_page_break()

        # 3. Environment-wise Cost Breakdown
        pdf.add_heading("Environment-wise Cost Breakdown")
        pdf.add_paragraph("Weekly cost overview by environment with resource counts and compliance metrics")
        
        env_comp_summary = env_analysis['env_comprehensive_summary'].copy()
        env_comp_display = env_comp_summary[[
            'environment', 'total_cost', 'resource_count',
            'budget_status', 'unlabeled_percent'
        ]].copy()
        env_comp_display.columns = [
            'Environment', 'Total Cost', 'Resources',
            'Budget Status', 'Unlabeled %'
        ]
        env_comp_display['Total Cost'] = env_comp_display['Total Cost'].apply(
            lambda x: f"{self.config.currency_symbol} {x:,.2f}"
        )
        env_comp_display['Unlabeled %'] = env_comp_display['Unlabeled %'].apply(
            lambda x: f"{x:.1f}%"
        )
        pdf.add_data_table(env_comp_display)
        pdf.add_page_break()
        
        # 4. Cost Forecasting
        if forecast_data:
            pdf.add_heading("Cost Forecasting")
            forecast_summary = forecast_data['summary']
            
            forecast_summary_data = [
                ["Metric", "Next 7 Days", "Next 30 Days"],
                ["Total Forecasted", 
                 f"{self.config.currency_symbol} {forecast_summary['total_forecasted_weekly']:,.2f}",
                 f"{self.config.currency_symbol} {forecast_summary['total_forecasted_monthly']:,.2f}"],
                ["Labeled Resources", 
                 f"{self.config.currency_symbol} {forecast_summary['labeled_forecasted_weekly']:,.2f}",
                 f"{self.config.currency_symbol} {forecast_summary['labeled_forecasted_monthly']:,.2f}"],
                ["Unlabeled Resources", 
                 f"{self.config.currency_symbol} {forecast_summary['unlabeled_forecasted_weekly']:,.2f}",
                 f"{self.config.currency_symbol} {forecast_summary['unlabeled_forecasted_monthly']:,.2f}"],
            ]
            pdf.add_summary_table(forecast_summary_data)
            pdf.add_page_break()
        
        # 5. Budget Tracking & Status
        pdf.add_heading("Budget Tracking & Status")
        
        env_budget_summary = env_analysis['env_budget_summary'].copy()
        env_budget_display = env_budget_summary[[
            'environment', 'daily_cost', 'monthly_budget', 'projected_monthly',
            'budget_usage_percent', 'status'
        ]].copy()
        env_budget_display.columns = [
            'Environment', 'Avg Daily Cost', 'Monthly Budget', 'Projected',
            'Usage %', 'Status'
        ]
        env_budget_display['Avg Daily Cost'] = env_budget_display['Avg Daily Cost'].apply(
            lambda x: f"{self.config.currency_symbol} {x:,.2f}"
        )
        env_budget_display['Monthly Budget'] = env_budget_display['Monthly Budget'].apply(
            lambda x: f"{self.config.currency_symbol} {x:,.2f}"
        )
        env_budget_display['Projected'] = env_budget_display['Projected'].apply(
            lambda x: f"{self.config.currency_symbol} {x:,.2f}"
        )
        env_budget_display['Usage %'] = env_budget_display['Usage %'].apply(
            lambda x: f"{x:.1f}%"
        )
        pdf.add_data_table(env_budget_display)
        
        # Highlight critical budgets
        critical_budgets = self.budget_tracker.get_critical_budgets(budget_statuses)
        if critical_budgets:
            pdf.add_spacer(0.3)
            pdf.add_info_box(
                "<b>⚠️ Budget Alerts:</b><br/>" + 
                "<br/>".join([
                    f"• <b>{status.environment}</b>: Projected {status.budget_usage_percent:.1f}% "
                    f"of budget (₹{status.projected_monthly:,.2f} / ₹{status.monthly_budget:,.2f})"
                    for status in critical_budgets
                ]),
                box_type='warning'
            )
        
        # Build PDF
        pdf.build()
        
        logger.info(f"Weekly PDF report saved: {pdf_path}")
        return pdf_path
    
    def run(self, send_notifications: bool = False):
        """Execute the weekly environment FinOps report generation."""
        try:
            logger.info("=" * 70)
            logger.info("Starting Weekly Environment FinOps Report Generation")
            logger.info("=" * 70)
            
            # Fetch data
            weekly_df = self.fetch_weekly_env_costs()
            env_summary = self.fetch_env_summary(weekly_df)
            trends_df = self.fetch_daily_trends()
            
            # Calculate governance metrics
            governance = self.calculate_governance_metrics(weekly_df)
            
            # Generate charts
            charts = self.generate_charts(weekly_df, env_summary, trends_df)
            
            # Detect anomalies
            anomalies = self.detect_anomalies(trends_df, env_summary, governance)
            
            # Track budgets
            budget_statuses = self.track_budgets(env_summary)
            
            # Generate forecasts
            forecast_data = self.forecast_costs(trends_df)
            
            # Find optimizations
            optimizations = self.find_optimizations(weekly_df)
            
            # Generate environment-wise cost analysis
            env_analysis = self.generate_env_cost_analysis(
                weekly_df, anomalies, optimizations, budget_statuses
            )
            
            # Generate PDF report
            pdf_path = self.generate_pdf_report(
                weekly_df,
                env_summary,
                trends_df,
                governance,
                charts,
                anomalies,
                budget_statuses,
                optimizations,
                env_analysis,
                forecast_data
            )
            
            # Send notifications (optional for weekly)
            if send_notifications:
                self.send_notifications(governance, env_summary, anomalies, pdf_path)
            
            # Summary
            anomaly_summary = self.anomaly_detector.generate_summary()
            
            logger.info("=" * 70)
            logger.info("✅ Weekly FinOps Report Generated Successfully")
            logger.info("=" * 70)
            logger.info(f"📊 Weekly Total: {self.config.currency_symbol}{governance['weekly_total']:,.2f}")
            logger.info(f"📊 Daily Average: {self.config.currency_symbol}{governance['daily_average']:,.2f}")
            logger.info(f"🏷️  Environments: {governance['env_count']}")
            logger.info(f"🚨 Anomalies: {anomaly_summary['total']} ({anomaly_summary['critical']} critical)")
            logger.info(f"📁 Output: {self.config.output_dir}")
            logger.info(f"📄 PDF: {pdf_path.name}")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Error generating weekly FinOps report: {e}", exc_info=True)
            raise
    
    def send_notifications(
        self,
        governance: dict,
        env_summary: pd.DataFrame,
        anomalies: list,
        pdf_path: Path
    ):
        """Send email and Slack notifications for weekly report."""
        logger.info("Sending weekly notifications...")
        
        # Send anomaly alerts if critical issues found
        critical_anomalies = [a for a in anomalies if a.severity == 'critical']
        if critical_anomalies:
            self.notifier.send_anomaly_alert(anomalies, self.date_range)
        
        # Send weekly summary
        env_costs = dict(zip(env_summary['env'], env_summary['total_cost']))
        self.notifier.send_daily_summary(
            report_date=self.date_range,
            total_cost=governance['weekly_total'],
            env_summary=env_costs,
            anomaly_count=len(anomalies),
            pdf_path=pdf_path
        )
        
        logger.info("Weekly notifications sent")


def main():
    """Main entry point for weekly report."""
    reporter = WeeklyEnvFinOpsReporter()
    reporter.run()


if __name__ == "__main__":
    main()
