"""
Backtesting Engine for the RO/RO Monitor

Tests the regime scoring system against historical data and
provides performance metrics for calibration.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import logging

from ..engine import RegimeEngine, PositioningEngine
from ..data import DataFetcher

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Backtesting engine for regime analysis validation.

    Simulates historical regime calculations and evaluates:
    - Regime classification accuracy
    - Signal quality
    - Position performance
    - Optimal pillar weights
    """

    def __init__(self):
        """Initialize backtest engine."""
        self.regime_engine = RegimeEngine()
        self.positioning_engine = PositioningEngine()
        self.data_fetcher = DataFetcher(use_cache=True)
        self.results = None

    def run_backtest(
        self,
        start_date: str = None,
        end_date: str = None,
        rebalance_days: int = 5
    ) -> Dict[str, Any]:
        """
        Run historical backtest of the regime system.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            rebalance_days: Days between rebalancing

        Returns:
            Dictionary with backtest results
        """
        logger.info("="*60)
        logger.info("STARTING BACKTEST")
        logger.info("="*60)

        # Fetch historical data
        logger.info("Fetching historical data...")
        market_data = self.data_fetcher.fetch_all_universe(period='2y', interval='1d')

        if not market_data:
            logger.error("Failed to fetch market data")
            return {'error': 'Data fetch failed'}

        # Get SPY as benchmark
        if 'SPY' not in market_data:
            logger.error("SPY data not available")
            return {'error': 'SPY data missing'}

        spy_data = market_data['SPY']

        # Calculate regime scores for each rebalance period
        backtest_results = []
        score_timeline = []

        # Simulate rolling regime calculation
        logger.info("Calculating historical regime scores...")

        total_days = len(spy_data)
        for i in range(252, total_days, rebalance_days):  # Start after 1 year of data
            try:
                # Create subset of data up to this point
                date = spy_data.index[i]
                subset_data = {}

                for ticker, df in market_data.items():
                    if len(df) > i:
                        subset_data[ticker] = df.iloc[:i]

                # Calculate regime
                regime_result = self.regime_engine.calculate_regime(subset_data)

                score = regime_result.get('master_score', 50)
                regime = regime_result.get('regime', 'NEUTRAL')

                # Store results
                score_timeline.append({
                    'date': date,
                    'score': score,
                    'regime': regime,
                    'spy_price': spy_data['close'].iloc[i]
                })

                # Calculate forward returns
                if i + rebalance_days < total_days:
                    forward_return = (
                        spy_data['close'].iloc[i + rebalance_days] /
                        spy_data['close'].iloc[i] - 1
                    ) * 100

                    backtest_results.append({
                        'date': date,
                        'score': score,
                        'regime': regime,
                        'forward_return': forward_return
                    })

            except Exception as e:
                logger.warning(f"Error at index {i}: {e}")
                continue

        if not backtest_results:
            logger.error("No backtest results generated")
            return {'error': 'Backtest failed'}

        # Analyze results
        results_df = pd.DataFrame(backtest_results)
        score_df = pd.DataFrame(score_timeline)

        analysis = self._analyze_results(results_df, score_df, spy_data)

        logger.info("="*60)
        logger.info("BACKTEST COMPLETE")
        logger.info(f"Signals Generated: {len(results_df)}")
        logger.info("="*60)

        self.results = {
            'results_df': results_df,
            'score_timeline': score_df,
            'analysis': analysis
        }

        return self.results

    def _analyze_results(
        self,
        results_df: pd.DataFrame,
        score_df: pd.DataFrame,
        spy_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Analyze backtest results."""

        analysis = {}

        # 1. Regime Performance Analysis
        regime_performance = results_df.groupby('regime')['forward_return'].agg([
            'mean', 'std', 'count'
        ]).to_dict()

        analysis['regime_performance'] = regime_performance

        # 2. Score Quartile Performance
        results_df['score_quartile'] = pd.qcut(
            results_df['score'],
            q=4,
            labels=['Q1 (0-25)', 'Q2 (25-50)', 'Q3 (50-75)', 'Q4 (75-100)']
        )

        quartile_performance = results_df.groupby('score_quartile')['forward_return'].agg([
            'mean', 'std', 'count'
        ]).to_dict()

        analysis['quartile_performance'] = quartile_performance

        # 3. Signal Quality Metrics
        # Correlation between score and forward returns
        score_return_corr = results_df[['score', 'forward_return']].corr().iloc[0, 1]
        analysis['score_return_correlation'] = score_return_corr

        # 4. Regime Transition Analysis
        score_df['regime_change'] = score_df['regime'] != score_df['regime'].shift(1)
        regime_changes = score_df['regime_change'].sum()
        analysis['regime_changes'] = int(regime_changes)

        # 5. Overall Statistics
        analysis['statistics'] = {
            'total_signals': len(results_df),
            'avg_score': results_df['score'].mean(),
            'score_std': results_df['score'].std(),
            'avg_forward_return': results_df['forward_return'].mean(),
            'forward_return_std': results_df['forward_return'].std(),
        }

        # 6. Buy and Hold Comparison
        if len(spy_data) > 0:
            bnh_return = (
                spy_data['close'].iloc[-1] / spy_data['close'].iloc[252] - 1
            ) * 100
            analysis['buy_and_hold_return'] = bnh_return

        return analysis

    def print_results(self) -> None:
        """Print backtest results in human-readable format."""
        if not self.results:
            print("No backtest results available. Run backtest first.")
            return

        analysis = self.results['analysis']

        print("\n" + "="*60)
        print("BACKTEST RESULTS SUMMARY")
        print("="*60)

        # Statistics
        stats = analysis['statistics']
        print("\nOverall Statistics:")
        print(f"  Total Signals: {stats['total_signals']}")
        print(f"  Average Score: {stats['avg_score']:.2f}")
        print(f"  Score Std Dev: {stats['score_std']:.2f}")
        print(f"  Avg Forward Return: {stats['avg_forward_return']:.3f}%")
        print(f"  Return Std Dev: {stats['forward_return_std']:.3f}%")

        # Correlation
        print(f"\nScore-Return Correlation: {analysis['score_return_correlation']:.3f}")

        # Regime Performance
        print("\nPerformance by Regime:")
        regime_perf = analysis['regime_performance']
        for metric, values in regime_perf.items():
            print(f"\n  {metric.upper()}:")
            for regime, value in values.items():
                print(f"    {regime}: {value:.3f}")

        # Quartile Performance
        print("\nPerformance by Score Quartile:")
        quartile_perf = analysis['quartile_performance']
        for metric, values in quartile_perf.items():
            print(f"\n  {metric.upper()}:")
            for quartile, value in values.items():
                print(f"    {quartile}: {value:.3f}")

        # Buy and Hold
        if 'buy_and_hold_return' in analysis:
            print(f"\nBuy & Hold Return: {analysis['buy_and_hold_return']:.2f}%")

        print("\n" + "="*60)

    def export_results(self, filepath: str) -> None:
        """
        Export backtest results to CSV.

        Args:
            filepath: Output file path
        """
        if not self.results:
            logger.error("No results to export")
            return

        results_df = self.results['results_df']
        results_df.to_csv(filepath, index=False)
        logger.info(f"Results exported to {filepath}")

    def calculate_optimal_weights(self) -> Dict[str, float]:
        """
        Calculate optimal pillar weights using historical data.
        (Placeholder for future implementation)

        Returns:
            Dictionary of optimal weights
        """
        logger.warning("Optimal weight calculation not yet implemented")
        return {
            'pillar_a': 0.30,
            'pillar_b': 0.25,
            'pillar_c': 0.25,
            'pillar_d': 0.10,
            'pillar_e': 0.10,
        }
