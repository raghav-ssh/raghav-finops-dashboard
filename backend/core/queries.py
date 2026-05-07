"""
BigQuery SQL queries for cost analysis and governance.
"""
from datetime import date
from typing import Optional


class CostQueries:
    """SQL query templates for cost analysis."""
    
    @staticmethod
    def period_cost_detail(table_path: str, start_date: date, end_date: date, min_cost: float = 50.0) -> str:
        """
        Query for cost breakdown by app, service, and region over a date range.
        
        Args:
            table_path: Fully qualified table path
            start_date: Start date for query
            end_date: End date for query
            min_cost: Minimum cost threshold
            
        Returns:
            SQL query string
        """
        return f"""
        SELECT
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "app" LIMIT 1),
                "UNLABELED"
            ) AS app,
            service.description AS service,
            location.region AS region,
            SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS cost
        FROM `{table_path}`
        WHERE DATE(usage_start_time) >= "{start_date}" AND DATE(usage_start_time) <= "{end_date}"
        GROUP BY env, app, service, region
        HAVING cost > {min_cost}
        ORDER BY cost DESC
        """
    
    @staticmethod
    def daily_cost_detail(table_path: str, target_date: date, min_cost: float = 50.0) -> str:
        """
        Query for daily cost breakdown by app, service, and region.
        
        Args:
            table_path: Fully qualified table path
            target_date: Date to query
            min_cost: Minimum cost threshold
            
        Returns:
            SQL query string
        """
        return f"""
        SELECT
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "app" LIMIT 1),
                "UNLABELED"
            ) AS app,
            service.description AS service,
            location.region AS region,
            SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS cost
        FROM `{table_path}`
        WHERE DATE(usage_start_time) = "{target_date}"
        GROUP BY env, app, service, region
        HAVING cost > {min_cost}
        ORDER BY cost DESC
        """
    
    @staticmethod
    def service_cost_breakdown(table_path: str, target_date: date) -> str:
        """Query for service-level cost breakdown."""
        return f"""
        SELECT
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            service.description AS service,
            sku.description AS sku,
            resource.name AS resource_name,
            SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS net_cost
        FROM `{table_path}`
        WHERE DATE(usage_start_time) = "{target_date}"
        GROUP BY env, service, sku, resource_name
        ORDER BY net_cost DESC
        """
    
    @staticmethod
    def weekly_app_cost(table_path: str, days_back: int = 42) -> str:
        """Query for weekly cost trends by application."""
        return f"""
        SELECT
            FORMAT_DATE('%G-W%V', DATE(usage_start_time)) AS week,
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "app" LIMIT 1),
                "UNLABELED"
            ) AS app,
            SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS cost
        FROM `{table_path}`
        WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY)
        GROUP BY week, env, app
        ORDER BY app, week
        """
    
    @staticmethod
    def compute_engine_cost(table_path: str, target_date: date, limit: int = 10) -> str:
        """Query for top Compute Engine VM costs."""
        return f"""
        SELECT
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            resource.name AS resource_name,
            SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS net_cost
        FROM `{table_path}`
        WHERE DATE(usage_start_time) = "{target_date}"
            AND service.description = "Compute Engine"
        GROUP BY env, resource_name
        ORDER BY net_cost DESC
        LIMIT {limit}
        """
    
    @staticmethod
    def network_cost_by_app(table_path: str, target_date: date, min_cost: float = 10.0) -> str:
        """
        Query for network usage cost breakdown by app label.
        
        Args:
            table_path: Fully qualified table path
            target_date: Date to query
            min_cost: Minimum cost threshold
            
        Returns:
            SQL query string
        """
        return f"""
        SELECT
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "app" LIMIT 1),
                "UNLABELED"
            ) AS app,
            service.description AS service,
            sku.description AS sku_description,
            location.region AS region,
            SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS net_cost
        FROM `{table_path}`
        WHERE DATE(usage_start_time) = "{target_date}"
            AND service.description = "Networking"
        GROUP BY env, app, service, sku_description, region
        HAVING net_cost > {min_cost}
        ORDER BY net_cost DESC
        """


class GovernanceQueries:
    """SQL query templates for governance and compliance."""
    
    @staticmethod
    def unlabeled_resources(table_path: str, target_date: date, required_label: str) -> str:
        """Query for resources missing required labels."""
        return f"""
        SELECT
            IFNULL(
                (SELECT value FROM UNNEST(labels) WHERE key = "env" LIMIT 1),
                "UNLABELED"
            ) AS env,
            resource.name AS resource_name,
            service.description AS service,
            SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS net_cost
        FROM `{table_path}`
        WHERE DATE(usage_start_time) = "{target_date}"
            AND NOT EXISTS (
                SELECT 1 FROM UNNEST(labels) l WHERE l.key = "{required_label}"
            )
        GROUP BY env, resource_name, service
        ORDER BY net_cost DESC
        """
    
    @staticmethod
    def label_compliance(table_path: str, target_date: date, required_label: str) -> str:
        """Query for label compliance metrics."""
        return f"""
        SELECT
            COUNT(*) AS total_count,
            COUNTIF(
                EXISTS(SELECT 1 FROM UNNEST(labels) l WHERE l.key = "{required_label}")
            ) AS labeled_count
        FROM `{table_path}`
        WHERE DATE(usage_start_time) = "{target_date}"
        """
