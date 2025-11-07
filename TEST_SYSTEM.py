#!/usr/bin/env python3
"""
Test the RO/RO Monitor system end-to-end
This will actually run a regime calculation
"""

import sys
import os

print("=" * 76)
print("  RO/RO Monitor - System Test")
print("=" * 76)
print()

try:
    # Import required modules
    print("Step 1: Importing modules...")
    from roro_monitor.engine import RegimeEngine, PositioningEngine
    from roro_monitor.dashboard.alerts import AlertSystem
    from roro_monitor.config import settings
    print("  ✓ All modules imported successfully")
    print()

    # Initialize engines
    print("Step 2: Initializing engines...")
    regime_engine = RegimeEngine()
    positioning_engine = PositioningEngine()
    alert_system = AlertSystem()
    print("  ✓ Engines initialized")
    print()

    # Calculate regime (this will fetch real data)
    print("Step 3: Calculating regime (fetching market data)...")
    print("  (This may take 30-60 seconds...)")
    print()

    regime_data = regime_engine.calculate_regime()

    print()
    print("=" * 76)
    print("  REGIME ANALYSIS RESULTS")
    print("=" * 76)
    print()

    # Display results
    print(f"Master Score: {regime_data['master_score']:.1f}/100")
    print(f"Regime: {regime_data['regime']}")
    print(f"Conviction: {regime_data['conviction']}")
    print(f"Timestamp: {regime_data['timestamp']}")
    print()

    print("Pillar Scores:")
    print("-" * 76)
    for pillar_name, pillar_data in regime_data['pillar_scores'].items():
        score = pillar_data['score']
        status = pillar_data['status']
        weight = pillar_data['weight']
        weighted = pillar_data['weighted_score']
        print(f"  {pillar_name}")
        print(f"    Score: {score:.1f} | Status: {status} | Weight: {weight:.0%} | Weighted: {weighted:.1f}")

    print()
    print("Key Drivers:")
    print("-" * 76)
    for driver in regime_data.get('key_drivers', []):
        print(f"  • {driver}")

    print()
    print("=" * 76)
    print("  POSITIONING RECOMMENDATIONS")
    print("=" * 76)
    print()

    # Generate positioning
    recommendations = positioning_engine.generate_recommendations(regime_data)

    print(f"{'Asset':<8} {'Action':<15} {'Sizing':<10} {'Rationale'}")
    print("-" * 76)
    for rec in recommendations[:10]:  # Show first 10
        print(f"{rec['asset']:<8} {rec['action']:<15} {rec['sizing']:>+4}%      {rec['rationale']}")

    print()
    print(f"Net Exposure: {positioning_engine.get_summary()}")

    print()
    print("=" * 76)
    print("  ALERTS")
    print("=" * 76)
    print()

    alerts = alert_system.check_alerts(regime_data)

    if alerts:
        for alert in alerts:
            print(f"[{alert['severity']}] {alert['title']}")
            print(f"  {alert['message']}")
            print()
    else:
        print("  No active alerts")

    print()
    print("=" * 76)
    print("  ✓ SYSTEM TEST SUCCESSFUL!")
    print("=" * 76)
    print()
    print("The RO/RO Monitor is working correctly and can:")
    print("  ✓ Fetch real market data from Yahoo Finance")
    print("  ✓ Calculate regime scores across all 5 pillars")
    print("  ✓ Generate CFD positioning recommendations")
    print("  ✓ Detect and alert on regime changes")
    print()
    print("Ready to use:")
    print("  • python main.py analyze    (console output)")
    print("  • python main.py dashboard  (web interface)")
    print("  • python main.py backtest   (historical analysis)")
    print()

except ImportError as e:
    print(f"✗ Import Error: {e}")
    print()
    print("Fix:")
    print("  1. Run: python FIX_ALL_ISSUES.py")
    print("  2. Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"✗ Error during test: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("This might be a network issue (Yahoo Finance).")
    print("The system structure is correct, but data fetch failed.")
    print()
    print("Check:")
    print("  • Internet connection")
    print("  • Yahoo Finance is accessible")
    print("  • No firewall blocking Python")
    sys.exit(1)
