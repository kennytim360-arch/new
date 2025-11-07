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

        # OPTIMIZED (Nov 2025) - Added sector rotation and leadership signals
        # 1. Sector Rotation Score (35%) - Cyclicals vs Defensives
        sector_score = self._calculate_sector_rotation(data)
        scores.append(('sector_rotation', sector_score, 0.35))

        # 2. Financial Sector Leadership (20%) - NEW confidence indicator
        financial_leadership = self._calculate_financial_leadership(data)
        scores.append(('financial_leadership', financial_leadership, 0.20))

        # 3. Small/Large Cap Ratio (25%) - Risk appetite
        size_ratio = self._calculate_size_ratio(data)
        scores.append(('size_ratio', size_ratio, 0.25))

        # 4. Risk Asset Dispersion (20%) - Breadth health
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
        """
        Calculate sector rotation score using new method.
        Financials + Industrials vs Consumer Staples.
        """
        required_tickers = ['XLF', 'XLI', 'XLP']

        if not all(t in data for t in required_tickers):
            logger.warning("Missing sector ETF data for rotation analysis")
            return None

        xlf_data = data['XLF']
        xli_data = data['XLI']
        xlp_data = data['XLP']

        if xlf_data.empty or xli_data.empty or xlp_data.empty:
            return None

        score = self.macro_indicators.sector_rotation_score(
            xlf_data, xli_data, xlp_data, period=20
        )

        return score

    def _calculate_financial_leadership(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate financial sector leadership score (NEW).
        Financials outperforming SPY = economic confidence.
        """
        if 'XLF' not in data or 'SPY' not in data:
            logger.warning("Missing XLF or SPY data for financial leadership")
            return None

        xlf_data = data['XLF']
        spy_data = data['SPY']

        if xlf_data.empty or spy_data.empty:
            return None

        score = self.macro_indicators.financial_sector_leadership_score(
            xlf_data, spy_data, period=20
        )

        return score

    def _calculate_size_ratio(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate small-cap vs large-cap ratio score (UPDATED).
        Uses the new small_cap_large_cap_ratio_score method.
        """
        if 'IWM' not in data or 'SPY' not in data:
            logger.warning("Missing IWM or SPY data for size ratio")
            return None

        iwm_data = data['IWM']
        spy_data = data['SPY']

        if iwm_data.empty or spy_data.empty:
            return None

        score = self.macro_indicators.small_cap_large_cap_ratio_score(
            iwm_data, spy_data, period=20
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
