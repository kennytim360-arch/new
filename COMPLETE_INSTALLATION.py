#!/usr/bin/env python3
"""
COMPLETE INSTALLATION AND VERIFICATION
Runs all fixes and tests in sequence
"""

import os
import sys
import subprocess

def run_script(script_name, description):
    """Run a Python script and report results"""
    print()
    print("=" * 76)
    print(f"  {description}")
    print("=" * 76)
    print()

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=True
        )
        print()
        print(f"✓ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print(f"✗ {description} - FAILED")
        print(f"Error code: {e.returncode}")
        return False
    except Exception as e:
        print()
        print(f"✗ {description} - ERROR: {e}")
        return False

def main():
    print("=" * 76)
    print("  RO/RO MONITOR - COMPLETE INSTALLATION")
    print("=" * 76)
    print()
    print("This will:")
    print("  1. Install missing data module files")
    print("  2. Fix all import/export issues")
    print("  3. Test the complete system with real data")
    print()
    input("Press ENTER to continue...")

    # Step 1: Install data module
    if not run_script('install_data_module.py', 'STEP 1: Installing Data Module'):
        print()
        print("Installation failed at Step 1")
        print("Try running manually: python install_data_module.py")
        sys.exit(1)

    # Step 2: Fix all issues
    if not run_script('FIX_ALL_ISSUES.py', 'STEP 2: Fixing All Issues'):
        print()
        print("Installation failed at Step 2")
        print("Try running manually: python FIX_ALL_ISSUES.py")
        sys.exit(1)

    # Step 3: Test system
    print()
    print("=" * 76)
    print("  STEP 3: Testing System with Real Data")
    print("=" * 76)
    print()
    print("NOTE: This will fetch real market data from Yahoo Finance")
    print("      It may take 30-60 seconds")
    print()
    input("Press ENTER to continue...")

    if not run_script('TEST_SYSTEM.py', 'STEP 3: System Test'):
        print()
        print("=" * 76)
        print("  System Test Failed")
        print("=" * 76)
        print()
        print("Possible causes:")
        print("  • Missing dependencies: pip install -r requirements.txt")
        print("  • Network issues: Check internet connection")
        print("  • Yahoo Finance unavailable: Try again later")
        print()
        print("The system structure is correct, but runtime test failed.")
        sys.exit(1)

    # Success!
    print()
    print("=" * 76)
    print("  ✓✓✓ INSTALLATION COMPLETE ✓✓✓")
    print("=" * 76)
    print()
    print("The RO/RO Monitor is fully installed and tested!")
    print()
    print("You can now run:")
    print()
    print("  Console Analysis:")
    print("    python main.py analyze")
    print()
    print("  Interactive Dashboard:")
    print("    python main.py dashboard")
    print("    (then open http://localhost:8050)")
    print()
    print("  Historical Backtest:")
    print("    python main.py backtest")
    print()
    print("=" * 76)
    print()

if __name__ == '__main__':
    main()
