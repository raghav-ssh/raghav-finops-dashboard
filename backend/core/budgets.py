import json
import os
from pathlib import Path

BUDGETS_FILE = Path(__file__).parent.parent / "data" / "budgets.json"

DEFAULT_BUDGETS = {
    'prod': {
        'daily': 20000.0,
        'weekly': 140000.0,
        'monthly': 600000.0
    },
    'uat': {
        'daily': 5000.0,
        'weekly': 35000.0,
        'monthly': 150000.0
    },
    'dev': {
        'daily': 3333.0,
        'weekly': 23333.0,
        'monthly': 100000.0
    },
    'UNLABELED': {
        'daily': 1667.0,
        'weekly': 11667.0,
        'monthly': 50000.0
    }
}

def normalize_budget(budget):
    """Normalize budget to new format with daily, weekly, monthly."""
    if isinstance(budget, (int, float)):
        # Old format - monthly budget only
        monthly = float(budget)
        return {
            'daily': round(monthly / 30, 2),
            'weekly': round(monthly / 30 * 7, 2),
            'monthly': monthly
        }
    elif isinstance(budget, dict):
        # New format - ensure all periods exist
        return {
            'daily': float(budget.get('daily', 0)),
            'weekly': float(budget.get('weekly', 0)),
            'monthly': float(budget.get('monthly', 0))
        }
    return {
        'daily': 0.0,
        'weekly': 0.0,
        'monthly': 0.0
    }

def get_budgets() -> dict:
    """Get budgets with normalization to new format."""
    if not BUDGETS_FILE.exists():
        return DEFAULT_BUDGETS.copy()
    
    try:
        with open(BUDGETS_FILE, 'r') as f:
            budgets = json.load(f)
            
        # Normalize all budgets to new format
        normalized = {}
        for env, budget in budgets.items():
            normalized[env] = normalize_budget(budget)
            
        return normalized
    except Exception:
        return DEFAULT_BUDGETS.copy()

def update_budgets(new_budgets: dict) -> dict:
    """Update budgets with normalization."""
    BUDGETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    current_budgets = get_budgets()
    
    # Update with new budgets, normalizing each one
    for env, budget in new_budgets.items():
        current_budgets[env] = normalize_budget(budget)
    
    with open(BUDGETS_FILE, 'w') as f:
        json.dump(current_budgets, f, indent=4)
        
    return current_budgets

def get_budget_for_period(env: str, period: str = 'monthly') -> float:
    """
    Get budget for a specific environment and period.
    
    Args:
        env: Environment name
        period: 'daily', 'weekly', or 'monthly'
        
    Returns:
        Budget amount for the specified period
    """
    budgets = get_budgets()
    env_budget = budgets.get(env, {'daily': 0, 'weekly': 0, 'monthly': 0})
    return float(env_budget.get(period, 0))
