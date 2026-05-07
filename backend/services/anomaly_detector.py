"""
Cost Anomaly Detection Module
Detects unusual cost patterns and generates alerts.
"""
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd

from core.logger import setup_logger


logger = setup_logger(__name__)


@dataclass
class Anomaly:
    """Represents a detected cost anomaly."""
    severity: str  # 'critical', 'warning', 'info'
    category: str  # 'spike', 'unlabeled', 'budget', 'service'
    environment: str
    message: str
    current_value: float
    threshold_value: float
    details: dict


class AnomalyDetector:
    """Detect cost anomalies and unusual patterns."""
    
    def __init__(self, config: dict = None):
        """
        Initialize anomaly detector.
        
        Args:
            config: Configuration with thresholds
        """
        self.config = config or {
            'dod_spike_threshold': 20.0,  # % increase
            'dod_drop_threshold': -30.0,  # % decrease
            'unlabeled_threshold': 25.0,  # % of total
            'budget_warning_threshold': 80.0,  # % of budget
            'budget_critical_threshold': 95.0,  # % of budget
            'service_spike_threshold': 50.0,  # % increase
        }
        
        self.anomalies: List[Anomaly] = []
    
    def detect_dod_spikes(
        self,
        trends_df: pd.DataFrame,
        target_date: str
    ) -> List[Anomaly]:
        """Detect day-over-day cost spikes."""
        logger.info("Detecting DoD cost spikes...")
        
        anomalies = []
        yesterday_data = trends_df[trends_df['date'] == target_date]
        
        for _, row in yesterday_data.iterrows():
            dod_change = row['dod_percent']
            
            # Critical spike
            if dod_change > self.config['dod_spike_threshold']:
                anomalies.append(Anomaly(
                    severity='critical',
                    category='spike',
                    environment=row['env'],
                    message=f"Critical cost spike: {dod_change:+.1f}% increase",
                    current_value=row['cost'],
                    threshold_value=self.config['dod_spike_threshold'],
                    details={
                        'previous_cost': row['previous_cost'],
                        'increase_amount': row['cost'] - row['previous_cost']
                    }
                ))
            
            # Unusual drop (might indicate missing data)
            elif dod_change < self.config['dod_drop_threshold']:
                anomalies.append(Anomaly(
                    severity='warning',
                    category='spike',
                    environment=row['env'],
                    message=f"Unusual cost drop: {dod_change:+.1f}% decrease",
                    current_value=row['cost'],
                    threshold_value=self.config['dod_drop_threshold'],
                    details={
                        'previous_cost': row['previous_cost'],
                        'decrease_amount': row['previous_cost'] - row['cost']
                    }
                ))
        
        self.anomalies.extend(anomalies)
        logger.info(f"Found {len(anomalies)} DoD anomalies")
        return anomalies
    
    def detect_unlabeled_issues(
        self,
        governance: dict
    ) -> List[Anomaly]:
        """Detect high unlabeled resource spend."""
        logger.info("Detecting unlabeled resource issues...")
        
        anomalies = []
        unlabeled_percent = governance['unlabeled_percent']
        
        if unlabeled_percent > self.config['unlabeled_threshold']:
            anomalies.append(Anomaly(
                severity='critical',
                category='unlabeled',
                environment='ALL',
                message=f"High unlabeled spend: {unlabeled_percent:.1f}% of total cost",
                current_value=governance['unlabeled_spend'],
                threshold_value=self.config['unlabeled_threshold'],
                details={
                    'total_cost': governance['daily_total'],
                    'unlabeled_cost': governance['unlabeled_spend']
                }
            ))
        
        self.anomalies.extend(anomalies)
        logger.info(f"Found {len(anomalies)} unlabeled anomalies")
        return anomalies
    
    def detect_budget_alerts(
        self,
        env_summary: pd.DataFrame,
        budgets: dict,
        days_in_month: int,
        current_day: int
    ) -> List[Anomaly]:
        """Detect budget threshold breaches."""
        logger.info("Detecting budget alerts...")
        
        anomalies = []
        
        for _, row in env_summary.iterrows():
            env = row['env']
            if env not in budgets:
                continue
            
            # Extract monthly budget - handle both old format (float) and new format (dict)
            env_budget = budgets[env]
            if isinstance(env_budget, (int, float)):
                monthly_budget = float(env_budget)
            elif isinstance(env_budget, dict):
                monthly_budget = float(env_budget.get('monthly', 0))
            else:
                logger.warning(f"Invalid budget format for {env}: {env_budget}")
                continue
            
            expected_spend = (monthly_budget / days_in_month) * current_day
            actual_spend = row['total_cost']
            
            # Calculate burn rate
            burn_rate = (actual_spend / expected_spend * 100) if expected_spend > 0 else 0
            
            # Project month-end cost
            projected_monthly = (actual_spend / current_day) * days_in_month
            budget_usage = (projected_monthly / monthly_budget * 100) if monthly_budget > 0 else 0
            
            if budget_usage >= self.config['budget_critical_threshold']:
                anomalies.append(Anomaly(
                    severity='critical',
                    category='budget',
                    environment=env,
                    message=f"Critical: Projected to use {budget_usage:.1f}% of monthly budget",
                    current_value=projected_monthly,
                    threshold_value=monthly_budget,
                    details={
                        'actual_spend': actual_spend,
                        'expected_spend': expected_spend,
                        'burn_rate': burn_rate,
                        'days_remaining': days_in_month - current_day
                    }
                ))
            
            elif budget_usage >= self.config['budget_warning_threshold']:
                anomalies.append(Anomaly(
                    severity='warning',
                    category='budget',
                    environment=env,
                    message=f"Warning: Projected to use {budget_usage:.1f}% of monthly budget",
                    current_value=projected_monthly,
                    threshold_value=monthly_budget,
                    details={
                        'actual_spend': actual_spend,
                        'expected_spend': expected_spend,
                        'burn_rate': burn_rate,
                        'days_remaining': days_in_month - current_day
                    }
                ))
        
        self.anomalies.extend(anomalies)
        logger.info(f"Found {len(anomalies)} budget anomalies")
        return anomalies
    
    def detect_service_anomalies(
        self,
        daily_df: pd.DataFrame,
        historical_avg: pd.DataFrame = None
    ) -> List[Anomaly]:
        """Detect unusual service cost patterns."""
        logger.info("Detecting service anomalies...")
        
        anomalies = []
        
        # Group by environment and service
        service_costs = daily_df.groupby(['env', 'service'])['cost'].sum().reset_index()
        
        # Find top services per environment
        for env in service_costs['env'].unique():
            env_services = service_costs[service_costs['env'] == env].nlargest(3, 'cost')
            
            for _, row in env_services.iterrows():
                # If historical data available, compare
                if historical_avg is not None:
                    hist_row = historical_avg[
                        (historical_avg['env'] == row['env']) & 
                        (historical_avg['service'] == row['service'])
                    ]
                    
                    if not hist_row.empty:
                        avg_cost = hist_row['avg_cost'].iloc[0]
                        change_percent = ((row['cost'] - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0
                        
                        if change_percent > self.config['service_spike_threshold']:
                            anomalies.append(Anomaly(
                                severity='warning',
                                category='service',
                                environment=row['env'],
                                message=f"{row['service']}: {change_percent:+.1f}% above average",
                                current_value=row['cost'],
                                threshold_value=avg_cost,
                                details={
                                    'service': row['service'],
                                    'historical_avg': avg_cost
                                }
                            ))
        
        self.anomalies.extend(anomalies)
        logger.info(f"Found {len(anomalies)} service anomalies")
        return anomalies
    
    def get_all_anomalies(self) -> List[Anomaly]:
        """Get all detected anomalies."""
        return self.anomalies
    
    def get_critical_anomalies(self) -> List[Anomaly]:
        """Get only critical anomalies."""
        return [a for a in self.anomalies if a.severity == 'critical']
    
    def generate_summary(self) -> Dict[str, int]:
        """Generate anomaly summary by severity."""
        summary = {
            'critical': len([a for a in self.anomalies if a.severity == 'critical']),
            'warning': len([a for a in self.anomalies if a.severity == 'warning']),
            'info': len([a for a in self.anomalies if a.severity == 'info']),
            'total': len(self.anomalies)
        }
        return summary
