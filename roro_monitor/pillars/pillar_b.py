"""
Pillar B: Market Breadth & Health (25% Weight)

Analyzes market breadth, sector rotation, and internal market health.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

from .base import BasePillar
from ..indicators import MacroIndicators
from ..config import AssetUniverse

logger = logging.getLogger(__name__)


class PillarB_MarketBreadth(BasePillar):
    """
    Pillar B: Market Breadth & Health

    Components:
    1. Sector Rotation Analysis (50%)
    2. Market Leadership (Small Cap vs Large Cap) (30%)
    3. Risk Asset Dispersion (20%)
    """

    def __init__(self):
        super().__init__(name="Pillar B: Market Breadth & Health", weight=0.25)
        self.macro_indicators = MacroIndicators()
        self.components = {}

    def calculate_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate Pillar B score.

        Args:
            data: Dictionary of ticker -> DataFrame

        Returns:
            Score from 0-100
        """
        scores = []

        # 1. Sector Rotation Score (50%)
        sector_score = self._calculate_sector_rotation(data)
        scores.append(('sector_rotation', sector_score, 0.50))

        # 2. Market Leadership - IWM vs SPY (30%)
        leadership_score = self._calculate_leadership(data)
        scores.append(('market_leadership', leadership_score, 0.30))

        # 3. Risk Asset Dispersion (20%)
        dispersion_score = self._calculate_dispersion(data)
        scores.append(('risk_dispersion', dispersion_score, 0.20))

        # Weighted combination
        valid_scores = [(score, weight) for name, score, weight in scores if score is not None]

        if not valid_scores:
            logger.error("No valid data for Pillar B calculation")
            self.last_score = 50.0
            return 50.0

        final_score = sum(s * w for s, w in valid_scores) / sum(w for _, w in valid_scores)
        self.last_score = final_score

        # Store components
        self.components = {name: score for name, score, _ in scores}

        logger.info(f"Pillar B Score: {final_score:.1f}")
        return final_score

    def _calculate_sector_rotation(self, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate sector rotation score."""
        cyclical_tickers = AssetUniverse.get_cyclical_sectors()
        defensive_tickers = AssetUniverse.get_defensive_sectors()

        cyclical_data = {t: data[t] for t in cyclical_tickers if t in data}
        defensive_data = {t: data[t] for t in defensive_tickers if t in data}

        if not cyclical_data or not defensive_data:
            logger.warning("Insufficient sector data")
            return None

        score = self.macro_indicators.sector_rotation_score(
            cyclical_data, defensive_data, period=20
        )

        return score

    def _calculate_leadership(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate market leadership score.
        Strong small cap (IWM) performance vs large cap (SPY) = healthy breadth.
        """
        if 'IWM' not in data or 'SPY' not in data:
            logger.warning("Missing IWM or SPY data")
            return None

        iwm_data = data['IWM']
        spy_data = data['SPY']

        if iwm_data.empty or spy_data.empty or len(iwm_data) < 20:
            return None

        # Calculate 20-day relative performance
        iwm_return = (iwm_data['close'].iloc[-1] / iwm_data['close'].iloc[-20] - 1) * 100
        spy_return = (spy_data['close'].iloc[-1] / spy_data['close'].iloc[-20] - 1) * 100

        outperformance = iwm_return - spy_return

        # Map to 0-100 scale
        # +5% outperformance = 100, -5% = 0
        score = 50 + (outperformance * 10)

        return np.clip(score, 0, 100)

    def _calculate_dispersion(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate risk asset dispersion.
        Low dispersion (assets moving together) = healthy risk-on.
        """
        risk_assets = ['SPY', 'QQQ', 'IWM', 'EEM']
        returns = []

        for ticker in risk_assets:
            if ticker in data and not data[ticker].empty and len(data[ticker]) >= 20:
                ret = (data[ticker]['close'].iloc[-1] / data[ticker]['close'].iloc[-20] - 1) * 100
                returns.append(ret)

        if len(returns) < 3:
            logger.warning("Insufficient data for dispersion calculation")
            return None

        # Calculate coefficient of variation (lower = less dispersion = better)
        std = np.std(returns)
        mean = np.mean(returns)

        if mean == 0:
            cv = 0
        else:
            cv = std / abs(mean)

        # Lower CV = higher score
        # CV of 0 = 100, CV of 2 = 0
        score = max(0, 100 - (cv * 50))

        return np.clip(score, 0, 100)

    def get_details(self) -> Dict[str, Any]:
        """Get detailed component breakdown."""
        return {
            'score': self.last_score,
            'components': self.components,
            'status': self.get_status_message(),
        }
