# Quick Directory Structure Checker
# Run: python check_structure.py

import os
import sys

def check_structure():
    print("=" * 60)
    print("RO/RO Monitor Structure Verification")
    print("=" * 60)
    print()

    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print()

    # Check for main.py
    if os.path.exists('main.py'):
        print("✓ main.py found")
    else:
        print("✗ main.py NOT found - you're in the wrong directory!")
        return False

    # Check roro_monitor folder
    if not os.path.exists('roro_monitor'):
        print("✗ roro_monitor folder NOT found!")
        return False

    print("✓ roro_monitor folder found")
    print()

    # Required structure
    required_structure = {
        'roro_monitor': ['__init__.py'],
        'roro_monitor/config': ['__init__.py', 'settings.py', 'tickers.py'],
        'roro_monitor/data': ['__init__.py', 'cache.py', 'fetcher.py'],
        'roro_monitor/engine': ['__init__.py', 'regime.py', 'positioning.py'],
        'roro_monitor/pillars': ['__init__.py', 'base.py', 'pillar_a.py', 'pillar_b.py', 'pillar_c.py', 'pillar_d.py', 'pillar_e.py'],
        'roro_monitor/dashboard': ['__init__.py', 'app.py', 'components.py', 'alerts.py'],
        'roro_monitor/indicators': ['__init__.py', 'technical.py', 'macro.py'],
        'roro_monitor/backtest': ['__init__.py', 'engine.py'],
        'roro_monitor/tests': ['__init__.py'],
    }

    print("Checking folder structure:")
    all_good = True

    for folder, files in required_structure.items():
        folder_path = folder.replace('/', os.sep)

        if os.path.exists(folder_path):
            print(f"  ✓ {folder}/")

            # Check files in folder
            for file in files:
                file_path = os.path.join(folder_path, file)
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"    ✓ {file} ({size} bytes)")
                else:
                    print(f"    ✗ {file} MISSING!")
                    all_good = False
        else:
            print(f"  ✗ {folder}/ MISSING!")
            all_good = False

    print()
    print("=" * 60)

    if all_good:
        print("✓ ALL FILES PRESENT - Structure is correct!")
        print()
        print("Next step: Install dependencies")
        print("  pip install -r requirements.txt")
        return True
    else:
        print("✗ MISSING FILES DETECTED!")
        print()
        print("Solutions:")
        print("1. Run: git status")
        print("2. Run: git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w")
        print("3. Or reset: git reset --hard origin/claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w")
        return False

if __name__ == '__main__':
    success = check_structure()

    if success:
        print()
        print("Testing imports...")
        try:
            import roro_monitor
            print("✓ roro_monitor imports successfully")

            from roro_monitor.data import DataFetcher
            print("✓ DataFetcher imports successfully")

            print()
            print("✓ SYSTEM READY TO RUN!")

        except ImportError as e:
            print(f"✗ Import error: {e}")
            print()
            print("Make sure you've installed dependencies:")
            print("  pip install -r requirements.txt")
