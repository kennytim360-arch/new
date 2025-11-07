"""
Alert System for the RO/RO Monitor

Generates alerts for:
- Regime changes
- Credit spread warnings
- Divergence signals
"""

from typing import List, Dict, Any
from datetime import datetime
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class AlertSystem:
    """
    Multi-level alert system for market regime changes and warnings.
    """

    def __init__(self):
        """Initialize alert system."""
        self.alerts = []
        self.alert_history = []

    def check_alerts(
        self,
        regime_data: Dict[str, Any],
        previous_regime_data: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for alert conditions.

        Args:
            regime_data: Current regime analysis
            previous_regime_data: Previous regime analysis for comparison

        Returns:
            List of active alerts
        """
        self.alerts = []

        # 1. Regime Change Alert
        if previous_regime_data:
            self._check_regime_change(regime_data, previous_regime_data)

        # 2. Score Movement Alert
        if previous_regime_data:
            self._check_score_movement(regime_data, previous_regime_data)

        # 3. Credit Spread Alert
        self._check_credit_spreads(regime_data)

        # 4. VIX Spike Alert
        self._check_vix_spike(regime_data)

        # 5. Divergence Alert
        self._check_divergence(regime_data)

        # Store in history
        for alert in self.alerts:
            self.alert_history.append({
                **alert,
                'timestamp': datetime.now()
            })

        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

        return self.alerts

    def _check_regime_change(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> None:
        """Check for regime classification changes."""
        current_regime = current.get('regime')
        previous_regime = previous.get('regime')

        if current_regime != previous_regime:
            severity = self._determine_severity(current_regime, previous_regime)

            self.alerts.append({
                'type': 'REGIME_CHANGE',
                'severity': severity,
                'title': 'Regime Change Detected',
                'message': f"Market regime changed from {previous_regime} to {current_regime}",
                'details': {
                    'from': previous_regime,
                    'to': current_regime,
                    'score': current.get('master_score')
                }
            })

            logger.warning(f"ALERT: Regime change {previous_regime} -> {current_regime}")

    def _check_score_movement(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> None:
        """Check for significant score movements."""
        current_score = current.get('master_score', 50)
        previous_score = previous.get('master_score', 50)

        score_change = current_score - previous_score

        if abs(score_change) > settings.REGIME_CHANGE_THRESHOLD:
            direction = "increased" if score_change > 0 else "decreased"
            severity = 'HIGH' if abs(score_change) > 15 else 'MEDIUM'

            self.alerts.append({
                'type': 'SCORE_MOVEMENT',
                'severity': severity,
                'title': 'Significant Score Change',
                'message': f"Master score {direction} by {abs(score_change):.1f} points",
                'details': {
                    'change': score_change,
                    'from': previous_score,
                    'to': current_score
                }
            })

            logger.warning(f"ALERT: Score movement {score_change:+.1f} points")

    def _check_credit_spreads(self, regime_data: Dict[str, Any]) -> None:
        """Check for credit spread warnings."""
        pillar_scores = regime_data.get('pillar_scores', {})
        pillar_c = pillar_scores.get('Pillar C: Macro-Fundamental Drivers', {})
        components = pillar_c.get('details', {}).get('components', {})

        spread_widening = components.get('spread_widening', False)
        hy_spread = components.get('hy_spread', 0)

        if spread_widening and abs(hy_spread) > 2:
            self.alerts.append({
                'type': 'CREDIT_WARNING',
                'severity': 'HIGH',
                'title': 'Credit Spread Warning',
                'message': f"High-yield spreads widening significantly ({hy_spread:+.2f}%)",
                'details': {
                    'hy_spread': hy_spread,
                    'widening': spread_widening
                }
            })

            logger.warning(f"ALERT: Credit spreads widening {hy_spread:+.2f}%")

    def _check_vix_spike(self, regime_data: Dict[str, Any]) -> None:
        """Check for VIX spikes."""
        pillar_scores = regime_data.get('pillar_scores', {})
        pillar_e = pillar_scores.get('Pillar E: Sentiment & Positioning', {})
        components = pillar_e.get('details', {}).get('components', {})

        vix_current = components.get('vix_current', 0)
        vix_zscore = components.get('vix_zscore', 0)

        if vix_zscore > 2:
            self.alerts.append({
                'type': 'VIX_SPIKE',
                'severity': 'HIGH',
                'title': 'Extreme Volatility Spike',
                'message': f"VIX at {vix_current:.1f} (z-score: {vix_zscore:.2f})",
                'details': {
                    'vix': vix_current,
                    'zscore': vix_zscore
                }
            })

            logger.warning(f"ALERT: VIX spike {vix_current:.1f} (z={vix_zscore:.2f})")

    def _check_divergence(self, regime_data: Dict[str, Any]) -> None:
        """Check for breadth divergence signals."""
        pillar_scores = regime_data.get('pillar_scores', {})

        # Get Pillar A (trend) and Pillar B (breadth) scores
        pillar_a = pillar_scores.get('Pillar A: Price Trend & Momentum', {})
        pillar_b = pillar_scores.get('Pillar B: Market Breadth & Health', {})

        score_a = pillar_a.get('score', 50)
        score_b = pillar_b.get('score', 50)

        # Significant divergence (>30 points difference)
        divergence = abs(score_a - score_b)

        if divergence > 30:
            self.alerts.append({
                'type': 'DIVERGENCE',
                'severity': 'MEDIUM',
                'title': 'Price-Breadth Divergence',
                'message': f"Price trend ({score_a:.0f}) diverging from breadth ({score_b:.0f})",
                'details': {
                    'trend_score': score_a,
                    'breadth_score': score_b,
                    'divergence': divergence
                }
            })

            logger.warning(f"ALERT: Divergence detected {divergence:.1f} points")

    def _determine_severity(self, current_regime: str, previous_regime: str) -> str:
        """Determine alert severity based on regime transition."""
        regime_ranks = {
            'STRONG_RISK_OFF': 0,
            'MODERATE_RISK_OFF': 1,
            'NEUTRAL': 2,
            'MODERATE_RISK_ON': 3,
            'STRONG_RISK_ON': 4
        }

        current_rank = regime_ranks.get(current_regime, 2)
        previous_rank = regime_ranks.get(previous_regime, 2)

        rank_change = abs(current_rank - previous_rank)

        if rank_change >= 3:
            return 'CRITICAL'
        elif rank_change >= 2:
            return 'HIGH'
        else:
            return 'MEDIUM'

    def get_active_alerts(self, severity_filter: str = None) -> List[Dict[str, Any]]:
        """
        Get currently active alerts.

        Args:
            severity_filter: Optional filter by severity level

        Returns:
            List of active alerts
        """
        if severity_filter:
            return [a for a in self.alerts if a['severity'] == severity_filter]

        return self.alerts

    def get_alert_summary(self) -> str:
        """Get text summary of active alerts."""
        if not self.alerts:
            return "No active alerts"

        critical = sum(1 for a in self.alerts if a['severity'] == 'CRITICAL')
        high = sum(1 for a in self.alerts if a['severity'] == 'HIGH')
        medium = sum(1 for a in self.alerts if a['severity'] == 'MEDIUM')

        parts = []
        if critical:
            parts.append(f"{critical} CRITICAL")
        if high:
            parts.append(f"{high} HIGH")
        if medium:
            parts.append(f"{medium} MEDIUM")

        return f"{len(self.alerts)} Active Alerts: " + ", ".join(parts)
