"""
Main entry point for FinOps Backend API.
"""
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.api import app, logger

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FinOps API server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
