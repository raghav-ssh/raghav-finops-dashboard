"""
Environment-wise Cost Analyzer
Provides detailed cost breakdowns by environment for each category.
"""
from typing import Dict, List
import pandas as pd

from core.logger import setup_logger


logger = setup_logger(__name__)


class EnvCostAnalyzer:
    """Analyze costs by environment for different categories."""
    
    def __init__(self):
        """Initialize environment cost analyzer."""
        pass
    
    def get_env_anomaly_costs(
        self,
        anomalies: list,
        daily_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get environment-wise cost totals for resources with anomalies.
        
        Args:
            anomalies: List of detected anomalies
            daily_df: Daily cost DataFrame
            
        Returns:
            DataFrame with environment-wise anomaly costs
        """
        logger.info("Calculating environment-wise anomaly costs...")
        
        # Group anomalies by environment
        env_anomaly_data = []
        
        for env in daily_df['env'].unique():
            env_anomalies = [a for a in anomalies if a.environment == env or a.environment == 'ALL']
            env_cost = daily_df[daily_df['env'] == env]['cost'].sum()
            
            critical_count = len([a for a in env_anomalies if a.severity == 'critical'])
            warning_count = len([a for a in env_anomalies if a.severity == 'warning'])
            
            env_anomaly_data.append({
                'environment': env,
                'total_cost': env_cost,
                'anomaly_count': len(env_anomalies),
                'critical_anomalies': critical_count,
                'warning_anomalies': warning_count,
                'status': 'Critical' if critical_count > 0 else 'Warning' if warning_count > 0 else 'OK'
            })
        
        df = pd.DataFrame(env_anomaly_data)
        df = df.sort_values('total_cost', ascending=False)
        
        logger.info(f"Analyzed anomaly costs for {len(df)} environments")
        return df
    
    def get_env_optimization_costs(
        self,
        optimizations: list,
        daily_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get environment-wise optimization opportunities and potential savings.
        
        Args:
            optimizations: List of optimization opportunities
            daily_df: Daily cost DataFrame
            
        Returns:
            DataFrame with environment-wise optimization costs
        """
        logger.info("Calculating environment-wise optimization costs...")
        
        env_opt_data = []
        
        for env in daily_df['env'].unique():
            env_opts = [o for o in optimizations if o.environment == env]
            env_cost = daily_df[daily_df['env'] == env]['cost'].sum()
            
            total_savings = sum(o.potential_savings for o in env_opts)
            high_priority = len([o for o in env_opts if o.priority == 'high'])
            
            # Count by category
            idle_vms = len([o for o in env_opts if o.category == 'idle_vm'])
            unattached_disks = len([o for o in env_opts if o.category == 'unattached_disk'])
            oversized = len([o for o in env_opts if o.category == 'oversized'])
            commitment = len([o for o in env_opts if o.category == 'commitment'])
            
            env_opt_data.append({
                'environment': env,
                'total_cost': env_cost,
                'opportunity_count': len(env_opts),
                'potential_savings': total_savings,
                'savings_percent': (total_savings / (env_cost * 30) * 100) if env_cost > 0 else 0,
                'high_priority': high_priority,
                'idle_vms': idle_vms,
                'unattached_disks': unattached_disks,
                'oversized': oversized,
                'commitment_opportunities': commitment
            })
        
        df = pd.DataFrame(env_opt_data)
        df = df.sort_values('potential_savings', ascending=False)
        
        logger.info(f"Analyzed optimization costs for {len(df)} environments")
        return df
    
    def get_env_budget_summary(
        self,
        budget_statuses: list,
        daily_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get environment-wise budget summary with costs.
        
        Args:
            budget_statuses: List of budget status objects
            daily_df: Daily cost DataFrame
            
        Returns:
            DataFrame with environment-wise budget summary
        """
        logger.info("Calculating environment-wise budget summary...")
        
        env_budget_data = []
        
        for status in budget_statuses:
            env = status.environment
            env_cost = daily_df[daily_df['env'] == env]['cost'].sum()
            
            # Calculate variance
            variance = status.actual_spend - status.expected_spend
            variance_percent = (variance / status.expected_spend * 100) if status.expected_spend > 0 else 0
            
            env_budget_data.append({
                'environment': env,
                'daily_cost': env_cost,
                'monthly_budget': status.monthly_budget,
                'actual_spend_mtd': status.actual_spend,
                'expected_spend_mtd': status.expected_spend,
                'variance': variance,
                'variance_percent': variance_percent,
                'projected_monthly': status.projected_monthly,
                'budget_usage_percent': status.budget_usage_percent,
                'burn_rate': status.burn_rate,
                'days_remaining': status.days_remaining,
                'status': status.status
            })
        
        df = pd.DataFrame(env_budget_data)
        df = df.sort_values('budget_usage_percent', ascending=False)
        
        logger.info(f"Analyzed budget for {len(df)} environments")
        return df
    
    def get_env_service_costs(
        self,
        daily_df: pd.DataFrame,
        top_n: int = 5
    ) -> Dict[str, pd.DataFrame]:
        """
        Get top services by cost for each environment.
        
        Args:
            daily_df: Daily cost DataFrame
            top_n: Number of top services to return per environment
            
        Returns:
            Dictionary of environment -> DataFrame with top services
        """
        logger.info("Calculating environment-wise service costs...")
        
        env_services = {}
        
        for env in daily_df['env'].unique():
            env_data = daily_df[daily_df['env'] == env]
            
            service_costs = env_data.groupby('service').agg({
                'cost': 'sum',
                'app': 'nunique',
                'region': 'nunique'
            }).reset_index()
            
            service_costs.columns = ['service', 'total_cost', 'app_count', 'region_count']
            service_costs = service_costs.sort_values('total_cost', ascending=False).head(top_n)
            
            # Add percentage
            env_total = env_data['cost'].sum()
            service_costs['cost_percent'] = (service_costs['total_cost'] / env_total * 100).round(2)
            
            env_services[env] = service_costs
        
        logger.info(f"Analyzed service costs for {len(env_services)} environments")
        return env_services
    
    def get_env_resource_counts(
        self,
        daily_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get resource counts by environment.
        
        Args:
            daily_df: Daily cost DataFrame
            
        Returns:
            DataFrame with environment-wise resource counts
        """
        logger.info("Calculating environment-wise resource counts...")
        
        env_resource_data = []
        
        for env in daily_df['env'].unique():
            env_data = daily_df[daily_df['env'] == env]
            
            total_cost = env_data['cost'].sum()
            app_count = env_data['app'].nunique()
            service_count = env_data['service'].nunique()
            region_count = env_data['region'].nunique()
            resource_count = len(env_data)
            
            # Calculate averages
            avg_cost_per_resource = total_cost / resource_count if resource_count > 0 else 0
            avg_cost_per_app = total_cost / app_count if app_count > 0 else 0
            
            # Find top app
            top_app = env_data.groupby('app')['cost'].sum().idxmax() if len(env_data) > 0 else 'N/A'
            top_app_cost = env_data.groupby('app')['cost'].sum().max() if len(env_data) > 0 else 0
            
            env_resource_data.append({
                'environment': env,
                'total_cost': total_cost,
                'resource_count': resource_count,
                'app_count': app_count,
                'service_count': service_count,
                'region_count': region_count,
                'avg_cost_per_resource': avg_cost_per_resource,
                'avg_cost_per_app': avg_cost_per_app,
                'top_app': top_app,
                'top_app_cost': top_app_cost,
                'top_app_percent': (top_app_cost / total_cost * 100) if total_cost > 0 else 0
            })
        
        df = pd.DataFrame(env_resource_data)
        df = df.sort_values('total_cost', ascending=False)
        
        logger.info(f"Analyzed resource counts for {len(df)} environments")
        return df
    
    def get_env_governance_details(
        self,
        daily_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get detailed governance metrics by environment.
        
        Args:
            daily_df: Daily cost DataFrame
            
        Returns:
            DataFrame with environment-wise governance details
        """
        logger.info("Calculating environment-wise governance details...")
        
        env_gov_data = []
        
        for env in daily_df['env'].unique():
            env_data = daily_df[daily_df['env'] == env]
            
            total_cost = env_data['cost'].sum()
            total_resources = len(env_data)
            
            # Unlabeled apps
            unlabeled_apps = len(env_data[env_data['app'] == 'UNLABELED'])
            unlabeled_cost = env_data[env_data['app'] == 'UNLABELED']['cost'].sum()
            unlabeled_percent = (unlabeled_cost / total_cost * 100) if total_cost > 0 else 0
            
            # Labeled resources
            labeled_resources = total_resources - unlabeled_apps
            compliance_percent = (labeled_resources / total_resources * 100) if total_resources > 0 else 100
            
            # Governance status
            if unlabeled_percent > 25:
                gov_status = 'Poor'
            elif unlabeled_percent > 10:
                gov_status = 'Fair'
            elif unlabeled_percent > 5:
                gov_status = 'Good'
            else:
                gov_status = 'Excellent'
            
            env_gov_data.append({
                'environment': env,
                'total_cost': total_cost,
                'total_resources': total_resources,
                'labeled_resources': labeled_resources,
                'unlabeled_resources': unlabeled_apps,
                'unlabeled_cost': unlabeled_cost,
                'unlabeled_percent': unlabeled_percent,
                'compliance_percent': compliance_percent,
                'governance_status': gov_status
            })
        
        df = pd.DataFrame(env_gov_data)
        df = df.sort_values('unlabeled_percent', ascending=False)
        
        logger.info(f"Analyzed governance for {len(df)} environments")
        return df
    
    def generate_env_summary_report(
        self,
        daily_df: pd.DataFrame,
        anomalies: list,
        optimizations: list,
        budget_statuses: list
    ) -> pd.DataFrame:
        """
        Generate comprehensive environment summary with all metrics.
        
        Args:
            daily_df: Daily cost DataFrame
            anomalies: List of anomalies
            optimizations: List of optimizations
            budget_statuses: List of budget statuses
            
        Returns:
            DataFrame with comprehensive environment summary
        """
        logger.info("Generating comprehensive environment summary...")
        
        env_summary_data = []
        
        for env in daily_df['env'].unique():
            env_data = daily_df[daily_df['env'] == env]
            env_anomalies = [a for a in anomalies if a.environment == env or a.environment == 'ALL']
            env_opts = [o for o in optimizations if o.environment == env]
            env_budget = next((b for b in budget_statuses if b.environment == env), None)
            
            # Basic metrics
            total_cost = env_data['cost'].sum()
            resource_count = len(env_data)
            app_count = env_data['app'].nunique()
            service_count = env_data['service'].nunique()
            
            # Anomaly metrics
            anomaly_count = len(env_anomalies)
            critical_anomalies = len([a for a in env_anomalies if a.severity == 'critical'])
            
            # Optimization metrics
            optimization_count = len(env_opts)
            potential_savings = sum(o.potential_savings for o in env_opts)
            
            # Budget metrics
            budget_status = env_budget.status if env_budget else 'N/A'
            budget_usage = env_budget.budget_usage_percent if env_budget else 0
            
            # Governance metrics
            unlabeled_count = len(env_data[env_data['app'] == 'UNLABELED'])
            unlabeled_cost = env_data[env_data['app'] == 'UNLABELED']['cost'].sum()
            unlabeled_percent = (unlabeled_cost / total_cost * 100) if total_cost > 0 else 0
            
            env_summary_data.append({
                'environment': env,
                'total_cost': total_cost,
                'resource_count': resource_count,
                'app_count': app_count,
                'service_count': service_count,
                'anomaly_count': anomaly_count,
                'critical_anomalies': critical_anomalies,
                'optimization_count': optimization_count,
                'potential_savings': potential_savings,
                'budget_status': budget_status,
                'budget_usage_percent': budget_usage,
                'unlabeled_count': unlabeled_count,
                'unlabeled_cost': unlabeled_cost,
                'unlabeled_percent': unlabeled_percent
            })
        
        df = pd.DataFrame(env_summary_data)
        df = df.sort_values('total_cost', ascending=False)
        
        logger.info(f"Generated comprehensive summary for {len(df)} environments")
        return df
