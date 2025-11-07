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
        """
        Comprehensive institutional-grade backtest analysis.

        Calculates all critical metrics for RO/RO strategy evaluation:
        - Risk-adjusted returns (Sharpe, Sortino, Calmar)
        - Drawdown analysis
        - Beta/Alpha relative to benchmark
        - Capture ratios
        - Regime efficacy
        """
        analysis = {}

        # ===================================================================
        # 1. CALCULATE STRATEGY EQUITY CURVE
        # ===================================================================
        results_df = results_df.copy()
        results_df['strategy_return'] = results_df['forward_return'] / 100
        results_df['cumulative_return'] = (1 + results_df['strategy_return']).cumprod()

        # ===================================================================
        # 2. PRIMARY PERFORMANCE METRICS
        # ===================================================================
        total_return = results_df['cumulative_return'].iloc[-1] - 1
        n_periods = len(results_df)
        trading_days_per_year = 252
        years = n_periods / (trading_days_per_year / 5)  # Assuming 5-day rebalancing

        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        annualized_volatility = results_df['strategy_return'].std() * np.sqrt(252 / 5)

        # Maximum Drawdown
        cumulative = results_df['cumulative_return']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        analysis['primary_metrics'] = {
            'total_return': total_return * 100,
            'annualized_return': annualized_return * 100,
            'annualized_volatility': annualized_volatility * 100,
            'max_drawdown': max_drawdown * 100,
            'periods': n_periods,
            'years': years,
        }

        # ===================================================================
        # 3. RISK-ADJUSTED RETURN METRICS
        # ===================================================================
        risk_free_rate = 0.04  # 4% annual risk-free rate

        # Sharpe Ratio
        excess_return = annualized_return - risk_free_rate
        sharpe_ratio = excess_return / annualized_volatility if annualized_volatility > 0 else 0

        # Sortino Ratio (downside deviation only)
        negative_returns = results_df['strategy_return'][results_df['strategy_return'] < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252 / 5) if len(negative_returns) > 0 else annualized_volatility
        sortino_ratio = excess_return / downside_deviation if downside_deviation > 0 else 0

        # Calmar Ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # Hit Rate and Profit Factor
        winning_periods = len(results_df[results_df['strategy_return'] > 0])
        hit_rate = winning_periods / n_periods if n_periods > 0 else 0

        gross_profits = results_df[results_df['strategy_return'] > 0]['strategy_return'].sum()
        gross_losses = abs(results_df[results_df['strategy_return'] < 0]['strategy_return'].sum())
        profit_factor = gross_profits / gross_losses if gross_losses > 0 else 0

        analysis['risk_adjusted'] = {
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'hit_rate': hit_rate * 100,
            'profit_factor': profit_factor,
        }

        # ===================================================================
        # 4. BENCHMARK COMPARISON (SPY Buy & Hold)
        # ===================================================================
        # Calculate benchmark returns over same period
        start_idx = score_df.index[0]
        end_idx = score_df.index[-1]

        benchmark_start = spy_data['close'].iloc[252]  # After warmup
        benchmark_end = spy_data['close'].iloc[-1]
        benchmark_total_return = (benchmark_end / benchmark_start - 1)
        benchmark_ann_return = (1 + benchmark_total_return) ** (1 / years) - 1 if years > 0 else 0

        # Benchmark drawdown
        spy_close = spy_data['close'].iloc[252:]
        spy_cumulative = spy_close / spy_close.iloc[0]
        spy_running_max = spy_cumulative.expanding().max()
        spy_drawdown = (spy_cumulative - spy_running_max) / spy_running_max
        benchmark_max_dd = spy_drawdown.min()

        # Benchmark volatility
        spy_returns = spy_close.pct_change().dropna()
        benchmark_volatility = spy_returns.std() * np.sqrt(252)

        analysis['benchmark'] = {
            'total_return': benchmark_total_return * 100,
            'annualized_return': benchmark_ann_return * 100,
            'max_drawdown': benchmark_max_dd * 100,
            'volatility': benchmark_volatility * 100,
        }

        # ===================================================================
        # 5. BETA AND ALPHA
        # ===================================================================
        # Align strategy and benchmark returns
        # For simplicity, use the forward returns correlation
        benchmark_returns = spy_returns.values
        if len(benchmark_returns) >= len(results_df):
            aligned_benchmark = benchmark_returns[:len(results_df)]
            strategy_returns = results_df['strategy_return'].values

            # Beta calculation
            covariance = np.cov(strategy_returns, aligned_benchmark)[0, 1]
            benchmark_variance = np.var(aligned_benchmark)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0

            # Alpha calculation (Jensen's Alpha)
            alpha_annual = annualized_return - (risk_free_rate + beta * (benchmark_ann_return - risk_free_rate))
        else:
            beta = 1.0
            alpha_annual = 0.0

        analysis['beta_alpha'] = {
            'beta': beta,
            'alpha_annual': alpha_annual * 100,
        }

        # ===================================================================
        # 6. CAPTURE RATIOS
        # ===================================================================
        # Up/Down Capture: Strategy performance during benchmark up/down periods
        results_df['benchmark_return'] = aligned_benchmark[:len(results_df)]

        up_periods = results_df[results_df['benchmark_return'] > 0]
        down_periods = results_df[results_df['benchmark_return'] < 0]

        if len(up_periods) > 0:
            strategy_up_return = up_periods['strategy_return'].sum()
            benchmark_up_return = up_periods['benchmark_return'].sum()
            up_capture = (strategy_up_return / benchmark_up_return) * 100 if benchmark_up_return != 0 else 0
        else:
            up_capture = 0

        if len(down_periods) > 0:
            strategy_down_return = down_periods['strategy_return'].sum()
            benchmark_down_return = down_periods['benchmark_return'].sum()
            down_capture = (strategy_down_return / benchmark_down_return) * 100 if benchmark_down_return != 0 else 0
        else:
            down_capture = 0

        analysis['capture_ratios'] = {
            'up_capture': up_capture,
            'down_capture': down_capture,
        }

        # ===================================================================
        # 7. REGIME-SPECIFIC PERFORMANCE
        # ===================================================================
        regime_performance = results_df.groupby('regime')['forward_return'].agg([
            'mean', 'std', 'count'
        ]).to_dict()
        analysis['regime_performance'] = regime_performance

        # ===================================================================
        # 8. SCORE QUARTILE PERFORMANCE
        # ===================================================================
        results_df['score_quartile'] = pd.qcut(
            results_df['score'],
            q=4,
            labels=['Q1 (0-25)', 'Q2 (25-50)', 'Q3 (50-75)', 'Q4 (75-100)']
        )
        quartile_performance = results_df.groupby('score_quartile')['forward_return'].agg([
            'mean', 'std', 'count'
        ]).to_dict()
        analysis['quartile_performance'] = quartile_performance

        # ===================================================================
        # 9. ADDITIONAL METRICS
        # ===================================================================
        score_return_corr = results_df[['score', 'forward_return']].corr().iloc[0, 1]

        score_df['regime_change'] = score_df['regime'] != score_df['regime'].shift(1)
        regime_changes = score_df['regime_change'].sum()

        analysis['additional'] = {
            'score_return_correlation': score_return_corr,
            'regime_changes': int(regime_changes),
            'turnover_events': int(regime_changes),  # Number of position changes
            'avg_score': results_df['score'].mean(),
            'score_std': results_df['score'].std(),
        }

        return analysis

    def print_results(self) -> None:
        """Print comprehensive institutional-grade backtest results."""
        if not self.results:
            print("No backtest results available. Run backtest first.")
            return

        analysis = self.results['analysis']

        print("\n" + "="*80)
        print(" "*20 + "INSTITUTIONAL RO/RO BACKTEST RESULTS")
        print("="*80)

        # ===================================================================
        # A. PRIMARY PERFORMANCE METRICS
        # ===================================================================
        print("\n" + "─"*80)
        print("A. PRIMARY PERFORMANCE METRICS (The Headline Numbers)")
        print("─"*80)

        pm = analysis['primary_metrics']
        bm = analysis['benchmark']

        print(f"\n{'Metric':<35} {'Strategy':>15} {'Benchmark':>15} {'Diff':>12}")
        print("─"*80)
        print(f"{'Total Return':<35} {pm['total_return']:>14.2f}% {bm['total_return']:>14.2f}% {pm['total_return']-bm['total_return']:>11.2f}%")
        print(f"{'Annualized Return':<35} {pm['annualized_return']:>14.2f}% {bm['annualized_return']:>14.2f}% {pm['annualized_return']-bm['annualized_return']:>11.2f}%")
        print(f"{'Annualized Volatility':<35} {pm['annualized_volatility']:>14.2f}% {bm['volatility']:>14.2f}% {pm['annualized_volatility']-bm['volatility']:>11.2f}%")
        print(f"{'Maximum Drawdown':<35} {pm['max_drawdown']:>14.2f}% {bm['max_drawdown']:>14.2f}% {pm['max_drawdown']-bm['max_drawdown']:>11.2f}%")
        print(f"{'Backtest Period (years)':<35} {pm['years']:>14.2f} {pm['years']:>14.2f} {0:>11.2f}")

        # ===================================================================
        # B. RISK-ADJUSTED RETURN METRICS
        # ===================================================================
        print("\n" + "─"*80)
        print("B. RISK-ADJUSTED RETURN METRICS (Success Indicators)")
        print("─"*80)

        ra = analysis['risk_adjusted']

        print(f"\n{'Metric':<35} {'Value':>15} {'Target':>15} {'Status':>12}")
        print("─"*80)
        print(f"{'Sharpe Ratio':<35} {ra['sharpe_ratio']:>15.3f} {'>1.0':>15} {'✓' if ra['sharpe_ratio'] > 1.0 else '✗':>12}")
        print(f"{'Sortino Ratio':<35} {ra['sortino_ratio']:>15.3f} {'>1.5':>15} {'✓' if ra['sortino_ratio'] > 1.5 else '✗':>12}")
        print(f"{'Calmar Ratio':<35} {ra['calmar_ratio']:>15.3f} {'>1.0':>15} {'✓' if ra['calmar_ratio'] > 1.0 else '✗':>12}")
        print(f"{'Hit Rate':<35} {ra['hit_rate']:>14.2f}% {'>50%':>15} {'✓' if ra['hit_rate'] > 50 else '✗':>12}")
        print(f"{'Profit Factor':<35} {ra['profit_factor']:>15.3f} {'>1.5':>15} {'✓' if ra['profit_factor'] > 1.5 else '✗':>12}")

        # ===================================================================
        # C. BETA, ALPHA & CAPTURE RATIOS
        # ===================================================================
        print("\n" + "─"*80)
        print("C. BENCHMARK-RELATIVE METRICS (Strategy Positioning)")
        print("─"*80)

        ba = analysis['beta_alpha']
        cr = analysis['capture_ratios']

        print(f"\n{'Metric':<35} {'Value':>15} {'Target':>15} {'Status':>12}")
        print("─"*80)
        print(f"{'Beta to SPY':<35} {ba['beta']:>15.3f} {'<1.0':>15} {'✓' if ba['beta'] < 1.0 else '✗':>12}")
        print(f"{'Alpha (Annual)':<35} {ba['alpha_annual']:>14.2f}% {'>0%':>15} {'✓' if ba['alpha_annual'] > 0 else '✗':>12}")
        print(f"{'Upside Capture Ratio':<35} {cr['up_capture']:>14.2f}% {'>70%':>15} {'✓' if cr['up_capture'] > 70 else '✗':>12}")
        print(f"{'Downside Capture Ratio':<35} {cr['down_capture']:>14.2f}% {'<50%':>15} {'✓' if cr['down_capture'] < 50 else '✗':>12}")

        # ===================================================================
        # D. DRAWDOWN ANALYSIS (Critical for RO/RO)
        # ===================================================================
        print("\n" + "─"*80)
        print("D. DRAWDOWN ANALYSIS (Crisis Performance)")
        print("─"*80)

        dd_reduction = ((pm['max_drawdown'] - bm['max_drawdown']) / bm['max_drawdown']) * 100
        print(f"\nStrategy Max Drawdown:     {pm['max_drawdown']:>8.2f}%")
        print(f"Benchmark Max Drawdown:    {bm['max_drawdown']:>8.2f}%")
        print(f"Drawdown Reduction:        {dd_reduction:>8.2f}%")
        print(f"\nTarget: >50% drawdown reduction {'✓ ACHIEVED' if dd_reduction > 50 else '✗ NOT MET'}")

        # ===================================================================
        # E. REGIME SWITCHING EFFICACY
        # ===================================================================
        print("\n" + "─"*80)
        print("E. REGIME SWITCHING EFFICACY (Signal Quality)")
        print("─"*80)

        regime_perf = analysis['regime_performance']
        print(f"\n{'Regime':<25} {'Avg Return':>15} {'Volatility':>15} {'Count':>10}")
        print("─"*80)
        for regime in sorted(regime_perf['mean'].keys()):
            avg_ret = regime_perf['mean'][regime]
            vol = regime_perf['std'][regime]
            count = int(regime_perf['count'][regime])
            print(f"{regime:<25} {avg_ret:>14.3f}% {vol:>14.3f}% {count:>10}")

        # ===================================================================
        # F. SCORE QUARTILE ANALYSIS
        # ===================================================================
        print("\n" + "─"*80)
        print("F. SCORE QUARTILE ANALYSIS (Calibration Check)")
        print("─"*80)

        quartile_perf = analysis['quartile_performance']
        print(f"\n{'Quartile':<25} {'Avg Return':>15} {'Volatility':>15} {'Count':>10}")
        print("─"*80)
        for quartile in ['Q1 (0-25)', 'Q2 (25-50)', 'Q3 (50-75)', 'Q4 (75-100)']:
            if quartile in quartile_perf['mean']:
                avg_ret = quartile_perf['mean'][quartile]
                vol = quartile_perf['std'][quartile]
                count = int(quartile_perf['count'][quartile])
                print(f"{quartile:<25} {avg_ret:>14.3f}% {vol:>14.3f}% {count:>10}")

        # ===================================================================
        # G. ADDITIONAL METRICS
        # ===================================================================
        print("\n" + "─"*80)
        print("G. ADDITIONAL METRICS")
        print("─"*80)

        add = analysis['additional']
        print(f"\nScore-Return Correlation:  {add['score_return_correlation']:>8.3f}")
        print(f"Regime Changes:            {add['regime_changes']:>8}")
        print(f"Average Score:             {add['avg_score']:>8.2f}")
        print(f"Score Volatility:          {add['score_std']:>8.2f}")

        # ===================================================================
        # H. OVERALL ASSESSMENT
        # ===================================================================
        print("\n" + "="*80)
        print("H. OVERALL ASSESSMENT")
        print("="*80)

        # Calculate success score
        success_criteria = []
        success_criteria.append(('MDD < Benchmark', pm['max_drawdown'] > bm['max_drawdown']))
        success_criteria.append(('Sharpe > 1.0', ra['sharpe_ratio'] > 1.0))
        success_criteria.append(('Calmar > 1.0', ra['calmar_ratio'] > 1.0))
        success_criteria.append(('Beta < 1.0', ba['beta'] < 1.0))
        success_criteria.append(('Alpha > 0', ba['alpha_annual'] > 0))
        success_criteria.append(('Down Capture < 50%', cr['down_capture'] < 50))

        success_count = sum(1 for _, passed in success_criteria if passed)
        total_criteria = len(success_criteria)

        print(f"\nSuccess Criteria Met: {success_count}/{total_criteria}")
        print("\nDetailed Checklist:")
        for criterion, passed in success_criteria:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}  {criterion}")

        # Overall verdict
        print("\n" + "─"*80)
        if success_count >= 5:
            print("VERDICT: ✓ STRATEGY IS PERFORMING WELL")
            print("The RO/RO model demonstrates strong risk-adjusted returns and effective")
            print("regime switching. It is successfully achieving capital preservation goals.")
        elif success_count >= 3:
            print("VERDICT: ⚠ STRATEGY SHOWS PROMISE BUT NEEDS OPTIMIZATION")
            print("The RO/RO model shows some positive attributes but requires refinement")
            print("in pillar weights or signal generation to meet all institutional standards.")
        else:
            print("VERDICT: ✗ STRATEGY REQUIRES SIGNIFICANT IMPROVEMENT")
            print("The RO/RO model is not meeting key performance criteria. Consider")
            print("re-calibrating pillar weights or reviewing signal generation logic.")

        print("="*80 + "\n")

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
