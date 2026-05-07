"""
Configuration management for GCP FinOps reporting.
Centralizes all configuration settings with validation.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GCPConfig:
    """GCP BigQuery configuration."""
    project_id: str
    dataset: str
    table: str
    
    @property
    def full_table_path(self) -> str:
        """Returns fully qualified table path."""
        return f"{self.project_id}.{self.dataset}.{self.table}"


@dataclass
class ReportConfig:
    """Report generation configuration."""
    output_dir: Path
    chart_dir: Path
    monthly_budget: float
    currency_symbol: str = "₹"
    
    def __post_init__(self):
        """Create directories if they don't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chart_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class GovernanceConfig:
    """Governance and compliance configuration."""
    required_label: str
    alert_threshold: float
    slack_webhook: Optional[str] = None


# Default configurations
GCP_CONFIG = GCPConfig(
    project_id=os.getenv("GCP_PROJECT_ID", "ssh-marine"),
    dataset=os.getenv("GCP_DATASET", "gcp_billing"),
    table=os.getenv("GCP_TABLE", "gcp_billing_export_resource_v1_01D037_3AB34D_12AAE9")
)

DAILY_REPORT_CONFIG = ReportConfig(
    output_dir=Path("cost_reports"),
    chart_dir=Path("cost_reports/charts"),
    monthly_budget=1200000.0
)

FINOPS_REPORT_CONFIG = ReportConfig(
    output_dir=Path("finops_reports"),
    chart_dir=Path("finops_reports/charts"),
    monthly_budget=1200000.0
)

GOVERNANCE_CONFIG = GovernanceConfig(
    required_label=os.getenv("REQUIRED_LABEL", "env"),
    alert_threshold=float(os.getenv("ALERT_THRESHOLD", "90")),
    slack_webhook=os.getenv("SLACK_WEBHOOK")
)
