"""
Cost Forecasting Module
Provides weekly and monthly cost forecasts for labeled and unlabeled resources.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

from core.logger import setup_logger


logger = setup_logger(__name__)


@dataclass
class CostForecast:
    """Cost forecast for a specific category."""
    category: str  # 'labeled', 'unlabeled', or environment name
    current_daily_avg: float
    current_weekly_total: float
    current_monthly_total: float
    forecasted_weekly: float
    forecasted_monthly: float
    trend: str  # 'increasing', 'decreasing', 'stable'
    confidence: float  # 0-100


class CostForecaster:
    """Forecast future costs based on historical trends."""
    
    def __init__(self):
        """Initialize cost forecaster."""
        self.today = datetime.utcnow().date()
    
    def calculate_trend(self, daily_costs: List[float]) -> Tuple[str, float]:
        """
        Calculate cost trend from daily costs.
        
        Args:
            daily_costs: List of daily costs (oldest to newest)
            
        Returns:
            Tuple of (trend_direction, trend_percentage)
        """
        if len(daily_costs) < 2:
            return 'stable', 0.0
        
        # Simple linear regression
        x = np.arange(len(daily_costs))
        y = np.array(daily_costs)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        avg_cost = np.mean(y)
        
        # Calculate trend percentage
        trend_pct = (slope / avg_cost * 100) if avg_cost > 0 else 0
        
        if abs(trend_pct) < 5:
            return 'stable', trend_pct
        elif trend_pct > 0:
            return 'increasing', trend_pct
        else:
            return 'decreasing', trend_pct
    
    def forecast_costs(
        self,
        trends_df: pd.DataFrame,
        forecast_days: int = 30
    ) -> Dict[str, CostForecast]:
        """
        Forecast costs for all environments and labeled/unlabeled categories.
        
        Args:
            trends_df: DataFrame with daily cost trends (must have 'date', 'env', 'cost')
            forecast_days: Number of days to forecast (default 30 for monthly)
            
        Returns:
            Dictionary of category -> CostForecast
        """
        logger.info(f"Forecasting costs for {forecast_days} days...")
        
        forecasts = {}
        
        # Get unique environments
        environments = trends_df['env'].unique()
        
        for env in environments:
            env_data = trends_df[trends_df['env'] == env].sort_values('date')
            
            if len(env_data) < 3:
                logger.warning(f"Insufficient data for {env}, skipping forecast")
                continue
            
            # Get last 7 days for weekly calculation
            last_7_days = env_data.tail(7)
            current_weekly_total = last_7_days['cost'].sum()
            current_daily_avg = last_7_days['cost'].mean()
            
            # Get last 30 days for monthly calculation (if available)
            last_30_days = env_data.tail(30)
            current_monthly_total = last_30_days['cost'].sum()
            
            # Calculate trend
            daily_costs = env_data.tail(14)['cost'].tolist()  # Use last 14 days for trend
            trend_direction, trend_pct = self.calculate_trend(daily_costs)
            
            # Forecast using weighted average (recent days weighted more)
            weights = np.exp(np.linspace(-1, 0, len(last_7_days)))
            weights = weights / weights.sum()
            weighted_avg = np.average(last_7_days['cost'].values, weights=weights)
            
            # Apply trend adjustment
            trend_multiplier = 1 + (trend_pct / 100)
            forecasted_daily = weighted_avg * trend_multiplier
            
            # Calculate forecasts
            forecasted_weekly = forecasted_daily * 7
            forecasted_monthly = forecasted_daily * 30
            
            # Calculate confidence (based on data consistency)
            std_dev = last_7_days['cost'].std()
            cv = (std_dev / current_daily_avg * 100) if current_daily_avg > 0 else 100
            confidence = max(0, min(100, 100 - cv))  # Lower variance = higher confidence
            
            forecasts[env] = CostForecast(
                category=env,
                current_daily_avg=current_daily_avg,
                current_weekly_total=current_weekly_total,
                current_monthly_total=current_monthly_total,
                forecasted_weekly=forecasted_weekly,
                forecasted_monthly=forecasted_monthly,
                trend=trend_direction,
                confidence=confidence
            )
        
        # Calculate labeled vs unlabeled forecasts
        labeled_envs = [e for e in environments if e != 'UNLABELED']
        
        if labeled_envs:
            labeled_total_weekly = sum(
                forecasts[e].forecasted_weekly for e in labeled_envs if e in forecasts
            )
            labeled_total_monthly = sum(
                forecasts[e].forecasted_monthly for e in labeled_envs if e in forecasts
            )
            labeled_current_weekly = sum(
                forecasts[e].current_weekly_total for e in labeled_envs if e in forecasts
            )
            labeled_current_monthly = sum(
                forecasts[e].current_monthly_total for e in labeled_envs if e in forecasts
            )
            labeled_daily_avg = sum(
                forecasts[e].current_daily_avg for e in labeled_envs if e in forecasts
            )
            
            forecasts['LABELED_TOTAL'] = CostForecast(
                category='LABELED_TOTAL',
                current_daily_avg=labeled_daily_avg,
                current_weekly_total=labeled_current_weekly,
                current_monthly_total=labeled_current_monthly,
                forecasted_weekly=labeled_total_weekly,
                forecasted_monthly=labeled_total_monthly,
                trend='stable',
                confidence=85.0
            )
        
        logger.info(f"Generated forecasts for {len(forecasts)} categories")
        return forecasts
    
    def generate_forecast_report(
        self,
        forecasts: Dict[str, CostForecast]
    ) -> pd.DataFrame:
        """
        Generate forecast report DataFrame.
        
        Args:
            forecasts: Dictionary of forecasts
            
        Returns:
            DataFrame with forecast details
        """
        data = []
        
        for category, forecast in forecasts.items():
            data.append({
                'Category': category,
                'Current Daily Avg': f"₹{forecast.current_daily_avg:,.2f}",
                'Current Weekly': f"₹{forecast.current_weekly_total:,.2f}",
                'Current Monthly': f"₹{forecast.current_monthly_total:,.2f}",
                'Forecasted Weekly': f"₹{forecast.forecasted_weekly:,.2f}",
                'Forecasted Monthly': f"₹{forecast.forecasted_monthly:,.2f}",
                'Trend': forecast.trend.title(),
                'Confidence': f"{forecast.confidence:.0f}%"
            })
        
        return pd.DataFrame(data)
    
    def get_summary_metrics(
        self,
        forecasts: Dict[str, CostForecast]
    ) -> Dict:
        """
        Get summary metrics for dashboard.
        
        Args:
            forecasts: Dictionary of forecasts
            
        Returns:
            Dictionary with summary metrics
        """
        total_forecasted_weekly = sum(
            f.forecasted_weekly for f in forecasts.values() 
            if f.category not in ['LABELED_TOTAL']
        )
        total_forecasted_monthly = sum(
            f.forecasted_monthly for f in forecasts.values()
            if f.category not in ['LABELED_TOTAL']
        )
        
        unlabeled_forecast = forecasts.get('UNLABELED')
        labeled_forecast = forecasts.get('LABELED_TOTAL')
        
        return {
            'total_forecasted_weekly': total_forecasted_weekly,
            'total_forecasted_monthly': total_forecasted_monthly,
            'unlabeled_forecasted_weekly': unlabeled_forecast.forecasted_weekly if unlabeled_forecast else 0,
            'unlabeled_forecasted_monthly': unlabeled_forecast.forecasted_monthly if unlabeled_forecast else 0,
            'labeled_forecasted_weekly': labeled_forecast.forecasted_weekly if labeled_forecast else 0,
            'labeled_forecasted_monthly': labeled_forecast.forecasted_monthly if labeled_forecast else 0,
            'unlabeled_percent_of_forecast': (
                (unlabeled_forecast.forecasted_monthly / total_forecasted_monthly * 100)
                if unlabeled_forecast and total_forecasted_monthly > 0 else 0
            )
        }
