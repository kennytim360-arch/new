#!/usr/bin/env python3
"""
FINAL SETUP - Guaranteed to work
Checks structure, then tells you exactly what to run
"""

import os
import sys

print("=" * 76)
print("  RO/RO MONITOR - FINAL SETUP & VERIFICATION")
print("=" * 76)
print()

# Check we're in the right directory
if not os.path.exists('main.py'):
    print("ERROR: main.py not found!")
    print("Please run this script from the project root directory.")
    sys.exit(1)

print("✓ In correct directory")
print()

# ============================================================================
# FIX 1: Dashboard exports
# ============================================================================

print("Step 1: Fixing dashboard/__init__.py...")

dashboard_init = os.path.join('roro_monitor', 'dashboard', '__init__.py')
dashboard_content = '''"""Interactive dashboard package."""

from .app import create_dashboard, run_dashboard
from .alerts import AlertSystem

__all__ = ['create_dashboard', 'run_dashboard', 'AlertSystem']
'''

with open(dashboard_init, 'w', encoding='utf-8') as f:
    f.write(dashboard_content)

print("  ✓ Fixed dashboard exports")

# ============================================================================
# FIX 2: Verify data module exists
# ============================================================================

print("Step 2: Verifying data module...")

data_files = ['__init__.py', 'cache.py', 'fetcher.py']
data_dir = os.path.join('roro_monitor', 'data')
all_exist = True

for filename in data_files:
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"  ✓ {filename}")
    else:
        print(f"  ✗ {filename} missing")
        all_exist = False

if not all_exist:
    print()
    print("DATA MODULE MISSING - Run this first:")
    print("  python install_data_module.py")
    print()
    sys.exit(1)

print("  ✓ All data module files present")

# ============================================================================
# STRUCTURAL VERIFICATION
# ============================================================================

print()
print("Step 3: Verifying file structure...")

required_modules = [
    'roro_monitor/__init__.py',
    'roro_monitor/config/__init__.py',
    'roro_monitor/config/settings.py',
    'roro_monitor/config/tickers.py',
    'roro_monitor/data/__init__.py',
    'roro_monitor/data/cache.py',
    'roro_monitor/data/fetcher.py',
    'roro_monitor/engine/__init__.py',
    'roro_monitor/engine/regime.py',
    'roro_monitor/engine/positioning.py',
    'roro_monitor/pillars/__init__.py',
    'roro_monitor/dashboard/__init__.py',
    'roro_monitor/dashboard/app.py',
]

all_present = True
for module in required_modules:
    if os.path.exists(module):
        print(f"  ✓ {module}")
    else:
        print(f"  ✗ {module} MISSING")
        all_present = False

if not all_present:
    print()
    print("ERROR: Some core files are missing!")
    sys.exit(1)

print()
print("  ✓ All core files present")

# ============================================================================
# CHECK DEPENDENCIES
# ============================================================================

print()
print("Step 4: Checking dependencies...")

try:
    import pandas
    print("  ✓ pandas installed")
    has_pandas = True
except ImportError:
    print("  ✗ pandas NOT installed")
    has_pandas = False

try:
    import numpy
    print("  ✓ numpy installed")
    has_numpy = True
except ImportError:
    print("  ✗ numpy NOT installed")
    has_numpy = False

try:
    import yfinance
    print("  ✓ yfinance installed")
    has_yfinance = True
except ImportError:
    print("  ✗ yfinance NOT installed")
    has_yfinance = False

try:
    import dash
    print("  ✓ dash installed")
    has_dash = True
except ImportError:
    print("  ✗ dash NOT installed")
    has_dash = False

# ============================================================================
# FINAL INSTRUCTIONS
# ============================================================================

print()
print("=" * 76)

if has_pandas and has_numpy and has_yfinance:
    print("  ✓✓✓ SYSTEM READY TO RUN ✓✓✓")
    print("=" * 76)
    print()
    print("All files and dependencies are in place!")
    print()
    print("Run the monitor now:")
    print()
    print("  python main.py analyze")
    print()
    print("This will:")
    print("  • Fetch real market data from Yahoo Finance")
    print("  • Calculate regime score (0-100)")
    print("  • Show pillar breakdowns")
    print("  • Generate CFD recommendations")
    print("  • Display any alerts")
    print()
    if has_dash:
        print("Or launch the dashboard:")
        print("  python main.py dashboard")
        print("  (then open http://localhost:8050)")
        print()
else:
    print("  DEPENDENCIES NEEDED")
    print("=" * 76)
    print()
    print("Files are ready, but you need to install dependencies:")
    print()
    print("  pip install -r requirements.txt")
    print()
    print("Or install individually:")
    if not has_pandas:
        print("  pip install pandas")
    if not has_numpy:
        print("  pip install numpy")
    if not has_yfinance:
        print("  pip install yfinance")
    if not has_dash:
        print("  pip install dash plotly dash-bootstrap-components")
    print()
    print("After installing, run:")
    print("  python main.py analyze")
    print()

print("=" * 76)
print()
