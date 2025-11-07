#!/usr/bin/env python3
"""Fix dashboard __init__.py to export run_dashboard"""

import os

print("Fixing dashboard __init__.py...")

dashboard_init = os.path.join('roro_monitor', 'dashboard', '__init__.py')

fixed_content = '''"""Interactive dashboard package."""

from .app import create_dashboard, run_dashboard
from .alerts import AlertSystem

__all__ = ['create_dashboard', 'run_dashboard', 'AlertSystem']
'''

with open(dashboard_init, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print(f"✓ Fixed: {dashboard_init}")
print()
print("Now run:")
print("  python main.py analyze")
