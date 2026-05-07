"""
BigQuery client wrapper with query utilities.
"""
from typing import Optional
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

from core.logger import setup_logger
from core.config import GCPConfig


logger = setup_logger(__name__)


class BigQueryClient:
    """Wrapper for BigQuery operations with error handling."""
    
    def __init__(self, config: GCPConfig):
        """
        Initialize BigQuery client.
        
        Args:
            config: GCP configuration
        """
        self.config = config
        self.client = bigquery.Client(project=config.project_id)
        logger.info(f"BigQuery client initialized for project: {config.project_id}")
    
    def execute_query(self, query: str, job_config: Optional[bigquery.QueryJobConfig] = None) -> pd.DataFrame:
        """
        Execute a BigQuery query and return results as DataFrame.
        
        Args:
            query: SQL query string
            job_config: Optional query job configuration
            
        Returns:
            Query results as pandas DataFrame
            
        Raises:
            GoogleAPIError: If query execution fails
        """
        try:
            logger.debug(f"Executing query: {query[:100]}...")
            query_job = self.client.query(query, job_config=job_config)
            df = query_job.to_dataframe()
            logger.info(f"Query executed successfully. Rows returned: {len(df)}")
            return df
        except GoogleAPIError as e:
            logger.error(f"BigQuery error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise
    
    def get_table_schema(self, table_id: str) -> list:
        """
        Get schema for a BigQuery table.
        
        Args:
            table_id: Fully qualified table ID
            
        Returns:
            List of schema fields
        """
        try:
            table = self.client.get_table(table_id)
            return table.schema
        except GoogleAPIError as e:
            logger.error(f"Error fetching table schema: {e}")
            raise
