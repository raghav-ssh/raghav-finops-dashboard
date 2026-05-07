"""
Utility functions for data processing and analysis.
"""
from typing import List, Dict, Any
import pandas as pd


def format_currency(amount: float, symbol: str = "₹") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Numeric amount
        symbol: Currency symbol
        
    Returns:
        Formatted currency string
    """
    return f"{symbol} {amount:,.2f}"


def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Percentage change (rounded to 2 decimals)
    """
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 2)


def aggregate_by_column(df: pd.DataFrame, group_col: str, value_col: str) -> pd.Series:
    """
    Aggregate DataFrame by column.
    
    Args:
        df: Input DataFrame
        group_col: Column to group by
        value_col: Column to sum
        
    Returns:
        Aggregated Series
    """
    return df.groupby(group_col)[value_col].sum().sort_values(ascending=False)


def filter_top_n(series: pd.Series, n: int = 10) -> pd.Series:
    """
    Get top N items from a Series.
    
    Args:
        series: Input Series
        n: Number of top items
        
    Returns:
        Top N items
    """
    return series.head(n)


def calculate_compliance_rate(total: int, compliant: int) -> float:
    """
    Calculate compliance rate percentage.
    
    Args:
        total: Total count
        compliant: Compliant count
        
    Returns:
        Compliance rate percentage
    """
    if total == 0:
        return 100.0
    return round((compliant / total) * 100, 2)


def create_summary_dict(data: Dict[str, Any]) -> List[List[str]]:
    """
    Convert dictionary to table format for PDF reports.
    
    Args:
        data: Dictionary with key-value pairs
        
    Returns:
        List of [key, value] pairs
    """
    return [[str(k), str(v)] for k, v in data.items()]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    return numerator / denominator if denominator != 0 else default


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Input string
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that DataFrame contains required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if all columns present, False otherwise
    """
    return all(col in df.columns for col in required_columns)


def export_to_csv(df: pd.DataFrame, filepath: str, **kwargs):
    """
    Export DataFrame to CSV with standard formatting.
    
    Args:
        df: DataFrame to export
        filepath: Output file path
        **kwargs: Additional arguments for to_csv
    """
    default_kwargs = {
        'index': False,
        'encoding': 'utf-8',
        'float_format': '%.2f'
    }
    default_kwargs.update(kwargs)
    df.to_csv(filepath, **default_kwargs)
