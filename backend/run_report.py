"""
Report generation entry point.
"""
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from reports.daily_env_finops_enhanced import main

if __name__ == "__main__":
    main()
