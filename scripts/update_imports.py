#!/usr/bin/env python3
"""
Update import paths after reorganization.
"""
import os
import re
from pathlib import Path

# Import mapping
IMPORT_MAPPINGS = {
    # Core modules
    r'from config import': 'from backend.core.config import',
    r'from logger import': 'from backend.core.logger import',
    r'from bigquery_client import': 'from backend.core.bigquery_client import',
    r'from queries import': 'from backend.core.queries import',
    
    # Services
    r'from anomaly_detector import': 'from backend.services.anomaly_detector import',
    r'from budget_tracker import': 'from backend.services.budget_tracker import',
    r'from cost_optimizer import': 'from backend.services.cost_optimizer import',
    r'from env_cost_analyzer import': 'from backend.services.env_cost_analyzer import',
    r'from notification_service import': 'from backend.services.notification_service import',
    
    # Reports
    r'from daily_env_finops_enhanced import': 'from backend.reports.daily_env_finops_enhanced import',
    r'from pdf_generator import': 'from backend.reports.pdf_generator import',
    r'from enhanced_chart_generator import': 'from backend.reports.enhanced_chart_generator import',
    
    # Utils
    r'from utils import': 'from backend.utils.utils import',
    r'from secretmanager import': 'from backend.utils.secretmanager import',
}

def update_file_imports(filepath):
    """Update imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        for old_pattern, new_import in IMPORT_MAPPINGS.items():
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_import, content)
                updated = True
        
        if updated and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
        return False

def main():
    """Main function to update all Python files."""
    print("Updating import paths in backend files...")
    
    backend_dir = Path('backend')
    if not backend_dir.exists():
        print("Backend directory not found. Run reorganize.sh first.")
        return
    
    updated_count = 0
    for py_file in backend_dir.rglob('*.py'):
        if '__pycache__' not in str(py_file) and py_file.name != '__init__.py':
            if update_file_imports(py_file):
                updated_count += 1
    
    print(f"\nUpdated {updated_count} files")
    print("Import paths updated successfully!")

if __name__ == '__main__':
    main()
