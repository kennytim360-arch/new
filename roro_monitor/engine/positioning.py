"""
CFD Positioning Recommendation Engine

Translates regime scores into actionable CFD position recommendations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

from ..config import settings, AssetUniverse

logger = logging.getLogger(__name__)


class PositioningEngine:
    """
    CFD Positioning Engine

    Generates dynamic position sizing and recommendations based on:
    - Master Regime Score
    - Conviction Level
    - Asset-specific factors
    """

    def __init__(self):
        """Initialize the positioning engine."""
        self.recommendations = []
        self.q4_sizing_multiplier = 0.5  # Reduce Q4 (>75 scores) by 50% due to signal quality issues

    def generate_recommendations(
        self,
        regime_data: Dict[str, Any],
        market_data: Dict[str, pd.DataFrame] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate CFD positioning recommendations.

        Args:
            regime_data: Output from RegimeEngine
            market_data: Optional market data for additional context

        Returns:
            List of position recommendations
        """
        master_score = regime_data['master_score']
        regime = regime_data['regime']
        conviction = regime_data['conviction']

        # CRITICAL FIX: Check for Q4 signal quality issues (scores > 75)
        is_q4_extreme = master_score > 75
        if is_q4_extreme:
            logger.warning(f"Q4 EXTREME SIGNAL DETECTED (score: {master_score:.1f}) - Applying 50% position sizing reduction")

        logger.info(f"Generating positions for {regime} regime (score: {master_score:.1f})")

        recommendations = []

        # 1. Equity Index CFDs
        recommendations.extend(self._equity_recommendations(master_score, conviction, is_q4_extreme))

        # 2. Bond CFDs
        recommendations.extend(self._bond_recommendations(master_score, conviction))

        # 3. Commodity CFDs
        recommendations.extend(self._commodity_recommendations(master_score, conviction))

        # 4. Sector CFDs
        recommendations.extend(self._sector_recommendations(master_score, conviction))

        self.recommendations = recommendations
        return recommendations

    def _equity_recommendations(self, score: float, conviction: str, is_q4_extreme: bool = False) -> List[Dict[str, Any]]:
        """
        Generate equity index CFD recommendations.

        Args:
            score: Master regime score (0-100)
            conviction: Conviction level (HIGH/MEDIUM/LOW)
            is_q4_extreme: True if score > 75 (apply position sizing reduction)
        """
        recommendations = []

        # REBALANCED POSITION SIZING (Nov 2025 v3) - SIGNAL QUALITY FIXES
        # v1: Extreme sizing caused negative downside capture
        # v2: Fixed short exposure but Q4 signal quality still poor
        # v3: CRITICAL FIX - Reduce Q4 sizing by 50%, NEUTRAL to CASH

        # Key improvements:
        # 1. Q4 (>75) gets 50% reduction due to signal decay
        # 2. NEUTRAL changed from 35% long to 0% (CASH - no edge, no risk)
        # 3. Maintained measured short exposure from v2

        if score >= 80:
            # STRONG RISK-ON - Aggressive but not extreme
            spy_action = "STRONG BUY"
            spy_sizing = 100  # Kept at 100 (was 120 - too aggressive)
            qqq_action = "STRONG BUY"
            qqq_sizing = 50   # Kept at 50 (was 60 - too aggressive)
            iwm_action = "BUY"
            iwm_sizing = 35   # Slightly increased from original 30
            # Net exposure: 185% long (BEFORE Q4 reduction)

        elif score >= 60:
            # MODERATE RISK-ON - Increased but measured
            spy_action = "BUY"
            spy_sizing = 80   # Increased from original 75
            qqq_action = "BUY"
            qqq_sizing = 40   # Increased from original 35
            iwm_action = "BUY"
            iwm_sizing = 25   # Increased from original 20
            # Net exposure: 145% long (BEFORE Q4 reduction)

        elif score >= 40:
            # NEUTRAL - GO TO CASH (v3 FIX!)
            # Problem: 0.016% return with 3.37% volatility = taking risk with NO EDGE
            # Solution: 0% equity exposure, hold cash or bonds
            spy_action = "CASH"
            spy_sizing = 0    # CHANGED from 25 (was taking risk with no edge)
            qqq_action = "CASH"
            qqq_sizing = 0    # CHANGED from 10
            iwm_action = "CASH"
            iwm_sizing = 0    # No change (was already 0)
            # Net exposure: 0% (TRUE NEUTRAL - no risk when no edge)

        elif score >= 20:
            # MODERATE RISK-OFF - GO TO CASH/DEFENSIVE (v4 CRITICAL FIX!)
            # Problem: v3 had -30% shorts → -1.618% avg returns (CATASTROPHIC!)
            # Root cause: Shorting during Risk-Off creates losses, not protection
            # Solution: 0% equity exposure, pure defensive positioning
            spy_action = "CASH"
            spy_sizing = 0    # CHANGED from -20 (shorting was losing money)
            qqq_action = "CASH"
            qqq_sizing = 0    # CHANGED from -10
            iwm_action = "CASH"
            iwm_sizing = 0    # No change (was already 0)
            # Net exposure: 0% equities (bonds via _bond_recommendations)
            # Philosophy: Risk-Off = DEFENSE not OFFENSE. Cash + bonds, zero shorts.

        else:
            # STRONG RISK-OFF - MINIMAL short exposure (v4 fix)
            # v3 had -70% shorts which could still cause losses
            # v4: Cap at -30% maximum shorts, focus on preservation
            spy_action = "REDUCE"
            spy_sizing = -20  # REDUCED from -40 (v3 shorts still too high)
            qqq_action = "REDUCE"
            qqq_sizing = -10  # REDUCED from -20
            iwm_action = "CASH"
            iwm_sizing = 0    # CHANGED from -10 (no small cap shorts)
            # Net exposure: -30% max shorts (was -70%)
            # Philosophy: Even in panic, limited shorting. Bonds do the work.

        # CRITICAL Q4 FIX: Reduce position sizing by 50% for extreme scores (>75)
        # Problem: Q4 scores (75-100) have NEGATIVE avg returns (-0.034%) vs Q3 (+0.803%)
        # Root cause: Signal quality degrades at extremes (mean reversion, overfitting)
        # Solution: Cut all positions in half when score > 75
        if is_q4_extreme:
            spy_sizing = int(spy_sizing * self.q4_sizing_multiplier)
            qqq_sizing = int(qqq_sizing * self.q4_sizing_multiplier)
            iwm_sizing = int(iwm_sizing * self.q4_sizing_multiplier)
            logger.warning(f"Q4 SIZING REDUCTION APPLIED: SPY={spy_sizing}% QQQ={qqq_sizing}% IWM={iwm_sizing}%")

        recommendations.extend([
            {
                'asset': 'SPY',
                'asset_class': 'Equity Index',
                'action': spy_action,
                'sizing': spy_sizing,
                'conviction': conviction,
                'rationale': 'Large Cap US Equities'
            },
            {
                'asset': 'QQQ',
                'asset_class': 'Equity Index',
                'action': qqq_action,
                'sizing': qqq_sizing,
                'conviction': conviction,
                'rationale': 'Tech-heavy Nasdaq exposure'
            },
            {
                'asset': 'IWM',
                'asset_class': 'Equity Index',
                'action': iwm_action,
                'sizing': iwm_sizing,
                'conviction': conviction,
                'rationale': 'Small Cap risk barometer'
            }
        ])

        return recommendations

    def _bond_recommendations(self, score: float, conviction: str) -> List[Dict[str, Any]]:
        """Generate bond CFD recommendations."""
        recommendations = []

        # Inverse relationship to equities
        if score >= 80:
            tlt_action = "SELL"
            tlt_sizing = -30
        elif score >= 60:
            tlt_action = "NEUTRAL"
            tlt_sizing = 0
        elif score >= 40:
            tlt_action = "NEUTRAL"
            tlt_sizing = 25
        elif score >= 20:
            tlt_action = "BUY"
            tlt_sizing = 75
        else:
            tlt_action = "STRONG BUY"
            tlt_sizing = 100

        recommendations.append({
            'asset': 'TLT',
            'asset_class': 'Government Bonds',
            'action': tlt_action,
            'sizing': tlt_sizing,
            'conviction': conviction,
            'rationale': 'Long-term Treasury safe haven'
        })

        return recommendations

    def _commodity_recommendations(self, score: float, conviction: str) -> List[Dict[str, Any]]:
        """Generate commodity CFD recommendations."""
        recommendations = []

        # Gold - complex relationship (safe haven but also inflation hedge)
        if score >= 70:
            gld_action = "NEUTRAL"
            gld_sizing = 0
        elif score >= 40:
            gld_action = "NEUTRAL"
            gld_sizing = 10
        elif score >= 20:
            gld_action = "BUY"
            gld_sizing = 40
        else:
            gld_action = "BUY"
            gld_sizing = 60

        # Oil - cyclical/growth proxy
        if score >= 70:
            uso_action = "BUY"
            uso_sizing = 30
        elif score >= 40:
            uso_action = "NEUTRAL"
            uso_sizing = 0
        else:
            uso_action = "SELL"
            uso_sizing = -20

        recommendations.extend([
            {
                'asset': 'GLD',
                'asset_class': 'Commodities',
                'action': gld_action,
                'sizing': gld_sizing,
                'conviction': conviction,
                'rationale': 'Gold safe-haven hedge'
            },
            {
                'asset': 'USO',
                'asset_class': 'Commodities',
                'action': uso_action,
                'sizing': uso_sizing,
                'conviction': conviction,
                'rationale': 'Oil as growth proxy'
            }
        ])

        return recommendations

    def _sector_recommendations(self, score: float, conviction: str) -> List[Dict[str, Any]]:
        """Generate sector rotation recommendations."""
        recommendations = []

        # Cyclical vs Defensive rotation
        if score >= 70:
            # Strong Risk-On: Overweight Cyclicals
            recommendations.extend([
                {'asset': 'XLF', 'asset_class': 'Sector', 'action': 'BUY', 'sizing': 40,
                 'conviction': conviction, 'rationale': 'Financials - Risk-On leader'},
                {'asset': 'XLY', 'asset_class': 'Sector', 'action': 'BUY', 'sizing': 30,
                 'conviction': conviction, 'rationale': 'Consumer Discretionary'},
                {'asset': 'XLU', 'asset_class': 'Sector', 'action': 'SELL', 'sizing': -20,
                 'conviction': conviction, 'rationale': 'Utilities - Reduce defensive'},
            ])
        elif score <= 30:
            # Strong Risk-Off: Overweight Defensives
            recommendations.extend([
                {'asset': 'XLU', 'asset_class': 'Sector', 'action': 'BUY', 'sizing': 50,
                 'conviction': conviction, 'rationale': 'Utilities - Defensive safe haven'},
                {'asset': 'XLP', 'asset_class': 'Sector', 'action': 'BUY', 'sizing': 40,
                 'conviction': conviction, 'rationale': 'Consumer Staples - Defensive'},
                {'asset': 'XLF', 'asset_class': 'Sector', 'action': 'SELL', 'sizing': -40,
                 'conviction': conviction, 'rationale': 'Financials - Reduce risk'},
            ])

        return recommendations

    def get_net_exposure(self) -> Dict[str, float]:
        """
        Calculate net portfolio exposure.

        Returns:
            Dictionary with exposure metrics
        """
        if not self.recommendations:
            return {'net_equity': 0, 'net_bond': 0, 'net_total': 0}

        equity_exposure = sum(
            rec['sizing'] for rec in self.recommendations
            if rec['asset_class'] == 'Equity Index'
        )

        bond_exposure = sum(
            rec['sizing'] for rec in self.recommendations
            if rec['asset_class'] == 'Government Bonds'
        )

        total_exposure = equity_exposure + bond_exposure

        return {
            'net_equity': equity_exposure,
            'net_bond': bond_exposure,
            'net_total': total_exposure,
            'risk_bias': 'LONG' if total_exposure > 0 else 'SHORT' if total_exposure < 0 else 'NEUTRAL'
        }

    def get_positioning_matrix(self) -> pd.DataFrame:
        """
        Convert recommendations to DataFrame for display.

        Returns:
            DataFrame with position recommendations
        """
        if not self.recommendations:
            return pd.DataFrame()

        df = pd.DataFrame(self.recommendations)

        # Sort by sizing (absolute value)
        df['abs_sizing'] = df['sizing'].abs()
        df = df.sort_values('abs_sizing', ascending=False)
        df = df.drop('abs_sizing', axis=1)

        return df

    def get_summary(self) -> str:
        """
        Get text summary of positioning recommendations.

        Returns:
            Human-readable summary
        """
        if not self.recommendations:
            return "No recommendations generated"

        exposure = self.get_net_exposure()

        summary_parts = [
            f"Net Equity Exposure: {exposure['net_equity']:+.0f}%",
            f"Net Bond Exposure: {exposure['net_bond']:+.0f}%",
            f"Total Net Exposure: {exposure['net_total']:+.0f}%",
            f"Risk Bias: {exposure['risk_bias']}"
        ]

        return " | ".join(summary_parts)
