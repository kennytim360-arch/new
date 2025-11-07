#!/usr/bin/env python3
"""
Institutional RO/RO Monitor - Main Entry Point

Usage:
    python main.py dashboard    # Run interactive dashboard
    python main.py analyze      # Run one-time analysis
    python main.py backtest     # Run backtest
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'roro_monitor_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)

logger = logging.getLogger(__name__)


def run_dashboard():
    """Launch the interactive dashboard."""
    from roro_monitor.dashboard import run_dashboard as start_dashboard

    logger.info("Starting Dashboard Mode")
    start_dashboard()


def run_analysis():
    """Run a one-time regime analysis."""
    from roro_monitor.engine import RegimeEngine, PositioningEngine
    from roro_monitor.dashboard.alerts import AlertSystem

    logger.info("Starting Analysis Mode")

    print("\n" + "="*60)
    print("INSTITUTIONAL RO/RO MONITOR - ANALYSIS")
    print("="*60 + "\n")

    # Initialize engines
    regime_engine = RegimeEngine()
    positioning_engine = PositioningEngine()
    alert_system = AlertSystem()

    # Calculate regime
    print("Fetching market data and calculating regime...")
    regime_data = regime_engine.calculate_regime()

    # Display results
    print("\n" + "="*60)
    print("REGIME ANALYSIS RESULTS")
    print("="*60)

    print(f"\nMaster Score: {regime_data['master_score']:.1f}/100")
    print(f"Regime: {regime_data['regime']}")
    print(f"Conviction: {regime_data['conviction']}")
    print(f"\nSummary: {regime_data['summary']}")

    print("\n--- Pillar Scores ---")
    for pillar_name, pillar_data in regime_data['pillar_scores'].items():
        print(f"{pillar_name}: {pillar_data['score']:.1f} ({pillar_data['status']})")

    print("\n--- Key Drivers ---")
    for driver in regime_data['key_drivers']:
        print(f"  • {driver}")

    # Generate positioning recommendations
    print("\n" + "="*60)
    print("CFD POSITIONING RECOMMENDATIONS")
    print("="*60 + "\n")

    recommendations = positioning_engine.generate_recommendations(regime_data)

    for rec in recommendations:
        print(f"{rec['asset']:6} | {rec['action']:12} | Sizing: {rec['sizing']:+4}% | {rec['rationale']}")

    print(f"\n{positioning_engine.get_summary()}")

    # Check for alerts
    alerts = alert_system.check_alerts(regime_data)

    if alerts:
        print("\n" + "="*60)
        print("ACTIVE ALERTS")
        print("="*60 + "\n")

        for alert in alerts:
            print(f"[{alert['severity']}] {alert['title']}")
            print(f"  {alert['message']}\n")

    print("\n" + "="*60)
    print(f"Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


def run_backtest():
    """Run backtesting analysis."""
    from roro_monitor.backtest import BacktestEngine

    logger.info("Starting Backtest Mode")

    print("\n" + "="*60)
    print("INSTITUTIONAL RO/RO MONITOR - BACKTEST")
    print("="*60 + "\n")

    backtest_engine = BacktestEngine()

    print("Running backtest (this may take a few minutes)...")
    results = backtest_engine.run_backtest(rebalance_days=5)

    if 'error' in results:
        print(f"Backtest failed: {results['error']}")
        return

    backtest_engine.print_results()

    # Export results
    export_path = f'backtest_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    backtest_engine.export_results(export_path)
    print(f"\nResults exported to: {export_path}")


def print_usage():
    """Print usage instructions."""
    print("""
Institutional RO/RO Monitor

Usage:
    python main.py dashboard    Launch interactive web dashboard
    python main.py analyze      Run one-time regime analysis
    python main.py backtest     Run historical backtest
    python main.py help         Show this help message

Examples:
    python main.py dashboard    # Start dashboard on http://localhost:8050
    python main.py analyze      # Print current regime analysis to console
    """)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == 'dashboard':
            run_dashboard()
        elif command == 'analyze':
            run_analysis()
        elif command == 'backtest':
            run_backtest()
        elif command in ['help', '-h', '--help']:
            print_usage()
        else:
            print(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nShutdown requested... exiting")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
