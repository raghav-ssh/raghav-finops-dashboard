"""
Cost Optimization Analyzer
Identifies potential cost savings opportunities.
"""
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd

from core.bigquery_client import BigQueryClient
from core.config import GCPConfig
from core.logger import setup_logger


logger = setup_logger(__name__)


@dataclass
class Optimization:
    """Represents a cost optimization opportunity."""
    category: str  # 'idle_vm', 'unattached_disk', 'oversized', 'commitment'
    resource: str
    environment: str
    current_cost: float
    potential_savings: float
    recommendation: str
    priority: str  # 'high', 'medium', 'low'


class CostOptimizer:
    """Analyze costs and identify optimization opportunities."""
    
    def __init__(self, gcp_config: GCPConfig, bq_client: BigQueryClient):
        """Initialize cost optimizer."""
        self.gcp_config = gcp_config
        self.bq_client = bq_client
        self.opportunities: List[Optimization] = []
    
    def find_idle_compute_instances(
        self,
        target_date: str,
        cpu_threshold: float = 5.0
    ) -> List[Optimization]:
        """
        Find potentially idle Compute Engine instances.
        
        Args:
            target_date: Date to analyze
            cpu_threshold: CPU usage threshold (%)
            
        Returns:
            List of optimization opportunities
        """
        logger.info("Analyzing idle Compute Engine instances...")
        
        # Note: This requires Cloud Monitoring data integration
        # For now, we'll identify low-cost VMs that might be idle
        query = f"""
        SELECT
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            resource.name AS resource_name,
            SUM(cost) AS daily_cost
        FROM `{self.gcp_config.full_table_path}`
        WHERE DATE(usage_start_time) = "{target_date}"
            AND service.description = "Compute Engine"
            AND sku.description LIKE "%Instance%"
        GROUP BY env, resource_name
        HAVING daily_cost > 10
        ORDER BY daily_cost DESC
        """
        
        try:
            df = self.bq_client.execute_query(query)
            opportunities = []
            
            # Heuristic: VMs with consistent low cost might be idle
            # In production, integrate with Cloud Monitoring for actual CPU metrics
            for _, row in df.iterrows():
                if row['daily_cost'] < 50:  # Low-cost VMs
                    opportunities.append(Optimization(
                        category='idle_vm',
                        resource=row['resource_name'],
                        environment=row['env'],
                        current_cost=row['daily_cost'] * 30,  # Monthly estimate
                        potential_savings=row['daily_cost'] * 30 * 0.8,  # 80% savings if stopped
                        recommendation=f"Review VM utilization. Consider stopping or downsizing if idle.",
                        priority='medium'
                    ))
            
            self.opportunities.extend(opportunities)
            logger.info(f"Found {len(opportunities)} potential idle VM opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding idle instances: {e}")
            return []
    
    def find_unattached_disks(
        self,
        target_date: str
    ) -> List[Optimization]:
        """Find unattached persistent disks."""
        logger.info("Analyzing unattached persistent disks...")
        
        query = f"""
        SELECT
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            resource.name AS resource_name,
            sku.description AS sku,
            SUM(cost) AS daily_cost
        FROM `{self.gcp_config.full_table_path}`
        WHERE DATE(usage_start_time) = "{target_date}"
            AND service.description = "Compute Engine"
            AND sku.description LIKE "%Storage PD%"
            AND sku.description NOT LIKE "%attached%"
        GROUP BY env, resource_name, sku
        HAVING daily_cost > 1
        ORDER BY daily_cost DESC
        """
        
        try:
            df = self.bq_client.execute_query(query)
            opportunities = []
            
            for _, row in df.iterrows():
                monthly_cost = row['daily_cost'] * 30
                opportunities.append(Optimization(
                    category='unattached_disk',
                    resource=row['resource_name'],
                    environment=row['env'],
                    current_cost=monthly_cost,
                    potential_savings=monthly_cost,  # 100% savings if deleted
                    recommendation=f"Delete unattached disk or create snapshot and delete.",
                    priority='high'
                ))
            
            self.opportunities.extend(opportunities)
            logger.info(f"Found {len(opportunities)} unattached disk opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding unattached disks: {e}")
            return []
    
    def find_oversized_resources(
        self,
        daily_df: pd.DataFrame,
        cost_threshold: float = 1000.0
    ) -> List[Optimization]:
        """Find potentially oversized resources."""
        logger.info("Analyzing oversized resources...")
        
        opportunities = []
        
        # Find top cost resources
        top_resources = daily_df.nlargest(20, 'cost')
        
        for _, row in top_resources.iterrows():
            if row['cost'] > cost_threshold:
                monthly_cost = row['cost'] * 30
                opportunities.append(Optimization(
                    category='oversized',
                    resource=f"{row['app']} - {row['service']}",
                    environment=row['env'],
                    current_cost=monthly_cost,
                    potential_savings=monthly_cost * 0.3,  # Potential 30% savings
                    recommendation=f"Review resource sizing. Consider rightsizing or using committed use discounts.",
                    priority='high' if row['cost'] > 2000 else 'medium'
                ))
        
        self.opportunities.extend(opportunities)
        logger.info(f"Found {len(opportunities)} oversized resource opportunities")
        return opportunities
    
    def analyze_commitment_opportunities(
        self,
        daily_df: pd.DataFrame
    ) -> List[Optimization]:
        """Analyze commitment use discount opportunities."""
        logger.info("Analyzing commitment use discount opportunities...")
        
        opportunities = []
        
        # Find consistent high-cost Compute Engine usage
        compute_costs = daily_df[
            daily_df['service'].str.contains('Compute Engine', na=False)
        ].groupby('env')['cost'].sum()
        
        for env, daily_cost in compute_costs.items():
            monthly_cost = daily_cost * 30
            
            if monthly_cost > 5000:  # Threshold for CUD consideration
                potential_savings = monthly_cost * 0.25  # 25% savings with 1-year CUD
                opportunities.append(Optimization(
                    category='commitment',
                    resource=f"Compute Engine - {env}",
                    environment=env,
                    current_cost=monthly_cost,
                    potential_savings=potential_savings,
                    recommendation=f"Consider 1-year or 3-year committed use discounts for consistent workloads. "
                                 f"Potential 25-57% savings.",
                    priority='high'
                ))
        
        self.opportunities.extend(opportunities)
        logger.info(f"Found {len(opportunities)} commitment opportunities")
        return opportunities
    
    def get_all_opportunities(self) -> List[Optimization]:
        """Get all optimization opportunities."""
        return self.opportunities
    
    def get_high_priority_opportunities(self) -> List[Optimization]:
        """Get high priority opportunities."""
        return [o for o in self.opportunities if o.priority == 'high']
    
    def calculate_total_savings(self) -> float:
        """Calculate total potential savings."""
        return sum(o.potential_savings for o in self.opportunities)
    
    def generate_optimization_report(self) -> pd.DataFrame:
        """Generate optimization report DataFrame."""
        data = []
        
        for opp in self.opportunities:
            data.append({
                'Category': opp.category.replace('_', ' ').title(),
                'Environment': opp.environment,
                'Resource': opp.resource,
                'Current Cost': f"₹{opp.current_cost:,.2f}",
                'Potential Savings': f"₹{opp.potential_savings:,.2f}",
                'Priority': opp.priority.title(),
                'Recommendation': opp.recommendation
            })
        
        return pd.DataFrame(data)
