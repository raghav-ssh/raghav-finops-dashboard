"""
Budget Tracking and Forecasting Module
Tracks budget usage, burn rate, and forecasts month-end costs.
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, List
import pandas as pd
import calendar

from core.logger import setup_logger


logger = setup_logger(__name__)


@dataclass
class BudgetStatus:
    """Budget status for an environment."""
    environment: str
    monthly_budget: float
    actual_spend: float
    expected_spend: float
    projected_monthly: float
    budget_usage_percent: float
    burn_rate: float
    days_elapsed: int
    days_remaining: int
    daily_avg: float
    status: str  # 'on_track', 'warning', 'critical', 'over_budget'


class BudgetTracker:
    """Track and forecast budget usage with support for daily, weekly, and monthly budgets."""
    
    def __init__(self, budgets: Dict[str, dict], period: str = 'monthly'):
        """
        Initialize budget tracker.
        
        Args:
            budgets: Dictionary of environment -> {daily, weekly, monthly} budgets
            period: Report period ('daily', 'weekly', or 'monthly')
        """
        self.budgets = budgets
        self.period = period
        self.today = datetime.utcnow().date()
        self.days_in_month = calendar.monthrange(self.today.year, self.today.month)[1]
        self.current_day = self.today.day
        self.days_remaining = self.days_in_month - self.current_day
    
    def get_budget_for_env(self, env: str) -> float:
        """Get the appropriate budget for an environment based on period."""
        if env not in self.budgets:
            return 0.0
            
        env_budget = self.budgets[env]
        
        # Handle old format (single number = monthly budget)
        if isinstance(env_budget, (int, float)):
            if self.period == 'daily':
                return env_budget / 30
            elif self.period == 'weekly':
                return env_budget / 30 * 7
            else:
                return env_budget
        
        # Handle new format (dict with daily/weekly/monthly)
        return float(env_budget.get(self.period, env_budget.get('monthly', 0)))
    
    def get_monthly_budget(self, env: str) -> float:
        """Get monthly budget for an environment (always use monthly for projections)."""
        if env not in self.budgets:
            return 0.0
            
        env_budget = self.budgets[env]
        
        if isinstance(env_budget, (int, float)):
            return env_budget
        
        return float(env_budget.get('monthly', 0))
    
    def calculate_budget_status(
        self,
        env_summary: pd.DataFrame
    ) -> List[BudgetStatus]:
        """
        Calculate budget status for all environments.
        
        Args:
            env_summary: DataFrame with environment cost summary
            
        Returns:
            List of BudgetStatus objects
        """
        logger.info(f"Calculating budget status for {self.period} period...")
        
        statuses = []
        
        for _, row in env_summary.iterrows():
            env = row['env']
            actual_spend = row['total_cost']
            
            if env not in self.budgets:
                logger.warning(f"No budget defined for environment: {env}")
                continue
            
            monthly_budget = self.get_monthly_budget(env)
            expected_spend = (monthly_budget / self.days_in_month) * self.current_day
            daily_avg = actual_spend / self.current_day if self.current_day > 0 else 0
            projected_monthly = daily_avg * self.days_in_month
            
            budget_usage = (projected_monthly / monthly_budget * 100) if monthly_budget > 0 else 0
            burn_rate = (actual_spend / expected_spend * 100) if expected_spend > 0 else 0
            
            # Determine status
            if budget_usage >= 100:
                status = 'over_budget'
            elif budget_usage >= 95:
                status = 'critical'
            elif budget_usage >= 80:
                status = 'warning'
            else:
                status = 'on_track'
            
            statuses.append(BudgetStatus(
                environment=env,
                monthly_budget=monthly_budget,
                actual_spend=actual_spend,
                expected_spend=expected_spend,
                projected_monthly=projected_monthly,
                budget_usage_percent=budget_usage,
                burn_rate=burn_rate,
                days_elapsed=self.current_day,
                days_remaining=self.days_remaining,
                daily_avg=daily_avg,
                status=status
            ))
        
        logger.info(f"Calculated budget status for {len(statuses)} environments")
        return statuses
    
    def get_critical_budgets(
        self,
        statuses: List[BudgetStatus]
    ) -> List[BudgetStatus]:
        """Get environments with critical or over-budget status."""
        return [s for s in statuses if s.status in ['critical', 'over_budget']]
    
    def forecast_month_end(
        self,
        trends_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Forecast month-end costs based on trends.
        
        Args:
            trends_df: DataFrame with daily cost trends
            
        Returns:
            Dictionary of environment -> forecasted month-end cost
        """
        logger.info("Forecasting month-end costs...")
        
        forecasts = {}
        
        for env in trends_df['env'].unique():
            env_data = trends_df[trends_df['env'] == env].sort_values('date')
            
            # Use last 7 days average
            recent_data = env_data.tail(7)
            avg_daily_cost = recent_data['cost'].mean()
            
            # Project to month end
            forecasted_monthly = avg_daily_cost * self.days_in_month
            forecasts[env] = forecasted_monthly
        
        return forecasts
    
    def generate_budget_report(
        self,
        statuses: List[BudgetStatus]
    ) -> pd.DataFrame:
        """Generate budget report DataFrame."""
        data = []
        
        for status in statuses:
            data.append({
                'Environment': status.environment,
                'Monthly Budget': f"₹{status.monthly_budget:,.2f}",
                'Actual Spend': f"₹{status.actual_spend:,.2f}",
                'Expected Spend': f"₹{status.expected_spend:,.2f}",
                'Projected Monthly': f"₹{status.projected_monthly:,.2f}",
                'Budget Usage': f"{status.budget_usage_percent:.1f}%",
                'Burn Rate': f"{status.burn_rate:.1f}%",
                'Daily Avg': f"₹{status.daily_avg:,.2f}",
                'Days Remaining': status.days_remaining,
                'Status': status.status.replace('_', ' ').title()
            })
        
        return pd.DataFrame(data)
    
    def calculate_savings_needed(
        self,
        status: BudgetStatus
    ) -> float:
        """Calculate daily savings needed to stay within budget."""
        if status.days_remaining <= 0:
            return 0
        
        remaining_budget = status.monthly_budget - status.actual_spend
        required_daily_avg = remaining_budget / status.days_remaining
        savings_needed = status.daily_avg - required_daily_avg
        
        return max(0, savings_needed)
