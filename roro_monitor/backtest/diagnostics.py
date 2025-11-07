"""
Diagnostic tools for RO/RO strategy optimization.

Analyzes regime transition timing, signal quality, and identifies
opportunities for improvement.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class StrategyDiagnostics:
    """
    Advanced diagnostics for regime-switching strategy optimization.

    Identifies:
    - Regime transition timing issues
    - Missed opportunities (late entries/early exits)
    - Signal quality problems
    - Pillar contribution analysis
    """

    def __init__(self, results_df: pd.DataFrame, score_df: pd.DataFrame):
        """
        Initialize diagnostics.

        Args:
            results_df: Backtest results with scores and returns
            score_df: Full score timeline with all periods
        """
        self.results_df = results_df.copy()
        self.score_df = score_df.copy()

    def analyze_missed_rallies(self, benchmark_returns: pd.Series) -> Dict[str, Any]:
        """
        Identify periods where benchmark rallied but strategy was defensive.

        Returns:
            Dictionary with missed rally analysis
        """
        analysis = {}

        # Define strong rally periods (benchmark > +5% over 20 days)
        benchmark_rolling = benchmark_returns.rolling(20).sum()
        strong_rallies = benchmark_rolling > 5.0

        # Check strategy positioning during rallies
        rally_periods = self.score_df[strong_rallies].copy()

        if len(rally_periods) > 0:
            # How often were we in Risk-On during rallies?
            risk_on_during_rally = (rally_periods['regime'].isin(['MODERATE_RISK_ON', 'STRONG_RISK_ON'])).mean()
            avg_score_during_rally = rally_periods['score'].mean()

            analysis['missed_rally_rate'] = (1 - risk_on_during_rally) * 100
            analysis['avg_score_in_rallies'] = avg_score_during_rally
            analysis['rally_periods_count'] = len(rally_periods)
            analysis['risk_on_percentage'] = risk_on_during_rally * 100
        else:
            analysis['missed_rally_rate'] = 0
            analysis['avg_score_in_rallies'] = 0
            analysis['rally_periods_count'] = 0
            analysis['risk_on_percentage'] = 0

        return analysis

    def analyze_regime_transitions(self) -> Dict[str, Any]:
        """
        Analyze regime transition patterns and timing.

        Returns:
            Dictionary with transition analysis
        """
        # Calculate regime changes
        self.score_df['regime_change'] = self.score_df['regime'] != self.score_df['regime'].shift(1)
        self.score_df['prev_regime'] = self.score_df['regime'].shift(1)

        # Transition matrix
        transitions = []
        for i in range(1, len(self.score_df)):
            if self.score_df['regime_change'].iloc[i]:
                transitions.append({
                    'from': self.score_df['prev_regime'].iloc[i],
                    'to': self.score_df['regime'].iloc[i],
                    'score_change': self.score_df['score'].iloc[i] - self.score_df['score'].iloc[i-1]
                })

        transitions_df = pd.DataFrame(transitions)

        # Calculate regime persistence
        regime_runs = []
        current_regime = self.score_df['regime'].iloc[0]
        run_length = 1

        for i in range(1, len(self.score_df)):
            if self.score_df['regime'].iloc[i] == current_regime:
                run_length += 1
            else:
                regime_runs.append({'regime': current_regime, 'length': run_length})
                current_regime = self.score_df['regime'].iloc[i]
                run_length = 1

        runs_df = pd.DataFrame(regime_runs)
        avg_persistence = runs_df.groupby('regime')['length'].mean().to_dict()

        return {
            'total_transitions': len(transitions),
            'transition_details': transitions_df.to_dict('records') if len(transitions) > 0 else [],
            'avg_persistence': avg_persistence,
            'transition_frequency': len(transitions) / len(self.score_df) * 100
        }

    def analyze_pillar_contributions(self, pillar_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Analyze which pillars contribute most to returns.

        Args:
            pillar_data: Dictionary of pillar scores over time

        Returns:
            Pillar contribution analysis
        """
        # Calculate correlation between each pillar and forward returns
        correlations = {}
        for pillar_name, scores in pillar_data.items():
            if len(scores) == len(self.results_df):
                corr = np.corrcoef(scores, self.results_df['forward_return'])[0, 1]
                correlations[pillar_name] = corr

        # Identify most predictive pillars
        sorted_pillars = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)

        return {
            'pillar_correlations': correlations,
            'most_predictive': sorted_pillars[0] if sorted_pillars else None,
            'least_predictive': sorted_pillars[-1] if sorted_pillars else None,
            'recommendations': self._generate_weight_recommendations(correlations)
        }

    def _generate_weight_recommendations(self, correlations: Dict[str, float]) -> List[str]:
        """Generate pillar weight recommendations based on correlations."""
        recommendations = []

        for pillar, corr in correlations.items():
            if abs(corr) < 0.05:
                recommendations.append(f"{pillar}: Low predictive power ({corr:.3f}). Consider reducing weight.")
            elif corr > 0.15:
                recommendations.append(f"{pillar}: Strong positive correlation ({corr:.3f}). Consider increasing weight.")
            elif corr < -0.15:
                recommendations.append(f"{pillar}: Strong defensive correlation ({corr:.3f}). Good for downside protection.")

        return recommendations

    def analyze_entry_exit_timing(self, benchmark_returns: pd.Series) -> Dict[str, Any]:
        """
        Analyze entry/exit timing relative to market moves.

        Returns:
            Entry/exit timing analysis
        """
        # Identify regime transitions to Risk-On
        risk_on_entries = self.score_df[
            (self.score_df['regime'].isin(['MODERATE_RISK_ON', 'STRONG_RISK_ON'])) &
            (~self.score_df['prev_regime'].isin(['MODERATE_RISK_ON', 'STRONG_RISK_ON']))
        ].copy()

        # Check forward returns after entry
        entry_analysis = {
            'avg_forward_5d_return': 0,
            'avg_forward_10d_return': 0,
            'entry_timing_score': 0
        }

        if len(risk_on_entries) > 0 and len(benchmark_returns) >= len(risk_on_entries):
            # Calculate returns after entries
            forward_returns = []
            for idx in risk_on_entries.index:
                if idx + 5 < len(benchmark_returns):
                    forward_5d = benchmark_returns.iloc[idx:idx+5].sum()
                    forward_returns.append(forward_5d)

            if forward_returns:
                entry_analysis['avg_forward_5d_return'] = np.mean(forward_returns)
                entry_analysis['entry_timing_score'] = 'Good' if np.mean(forward_returns) > 2.0 else 'Early'

        return entry_analysis

    def generate_optimization_report(self) -> str:
        """
        Generate comprehensive optimization report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("="*80)
        report.append("STRATEGY DIAGNOSTICS & OPTIMIZATION REPORT")
        report.append("="*80)

        # Regime transition analysis
        transitions = self.analyze_regime_transitions()
        report.append("\n1. REGIME TRANSITION ANALYSIS")
        report.append("─"*80)
        report.append(f"Total Transitions: {transitions['total_transitions']}")
        report.append(f"Transition Frequency: {transitions['transition_frequency']:.2f}%")
        report.append("\nAverage Regime Persistence (days):")
        for regime, days in transitions['avg_persistence'].items():
            report.append(f"  {regime}: {days:.1f} days")

        # Recommendations
        report.append("\n" + "="*80)
        report.append("RECOMMENDATIONS")
        report.append("="*80)

        if transitions['transition_frequency'] > 10:
            report.append("\n⚠ HIGH TRANSITION FREQUENCY DETECTED")
            report.append("  → Strategy is flipping too frequently")
            report.append("  → Add momentum confirmation filters")
            report.append("  → Use moving averages of pillar scores")

        report.append("\n" + "="*80)

        return "\n".join(report)


def calculate_optimal_pillar_weights(
    results_df: pd.DataFrame,
    pillar_scores: Dict[str, List[float]]
) -> Dict[str, float]:
    """
    Calculate optimal pillar weights based on historical performance.

    Uses correlation with forward returns to suggest weight adjustments.

    Args:
        results_df: Backtest results DataFrame
        pillar_scores: Dictionary of pillar scores

    Returns:
        Dictionary of recommended weights
    """
    diagnostics = StrategyDiagnostics(results_df, pd.DataFrame())
    analysis = diagnostics.analyze_pillar_contributions(pillar_scores)

    # Start with equal weights
    n_pillars = len(pillar_scores)
    base_weight = 1.0 / n_pillars

    # Adjust based on correlations
    correlations = analysis['pillar_correlations']
    adjusted_weights = {}

    # Normalize correlations to sum to 1.0
    total_abs_corr = sum(abs(c) for c in correlations.values())

    if total_abs_corr > 0:
        for pillar, corr in correlations.items():
            # Higher absolute correlation = higher weight
            adjusted_weights[pillar] = abs(corr) / total_abs_corr
    else:
        # Fall back to equal weights
        adjusted_weights = {pillar: base_weight for pillar in pillar_scores.keys()}

    # Ensure weights sum to 1.0
    total_weight = sum(adjusted_weights.values())
    adjusted_weights = {k: v/total_weight for k, v in adjusted_weights.items()}

    return adjusted_weights
