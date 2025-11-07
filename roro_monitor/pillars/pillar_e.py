"""
Pillar E: Sentiment & Positioning (10% Weight)

Analyzes market sentiment through put/call ratios and positioning extremes.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

from .base import BasePillar

logger = logging.getLogger(__name__)


class PillarE_Sentiment(BasePillar):
    """
    Pillar E: Sentiment & Positioning

    Components:
    1. VIX Level (Sentiment Proxy) (60%)
    2. Price Extremes (Overbought/Oversold) (40%)

    Note: Put/Call ratios require specialized data sources.
    This implementation uses VIX as a sentiment proxy.
    """

    def __init__(self):
        super().__init__(name="Pillar E: Sentiment & Positioning", weight=0.10)
        self.components = {}

    def calculate_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate Pillar E score.

        Args:
            data: Dictionary of ticker -> DataFrame

        Returns:
            Score from 0-100
        """
        scores = []

        # 1. VIX Sentiment (60%)
        vix_score = self._calculate_vix_sentiment(data)
        if vix_score is not None:
            scores.append(('vix_sentiment', vix_score, 0.60))

        # 2. Price Extremes (40%)
        extreme_score = self._calculate_price_extremes(data)
        if extreme_score is not None:
            scores.append(('price_extremes', extreme_score, 0.40))

        if not scores:
            logger.error("No valid data for Pillar E calculation")
            self.last_score = 50.0
            return 50.0

        # Weighted combination
        final_score = sum(s * w for name, s, w in scores) / sum(w for _, _, w in scores)
        self.last_score = final_score

        # Store components
        self.components = {name: score for name, score, _ in scores}

        logger.info(f"Pillar E Score: {final_score:.1f}")
        return final_score

    def _calculate_vix_sentiment(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate VIX-based sentiment score.
        Low VIX = complacency/risk-on
        High VIX = fear/risk-off
        """
        if '^VIX' not in data or data['^VIX'].empty:
            logger.warning("Missing VIX data")
            return None

        vix_data = data['^VIX']

        if len(vix_data) < 63:
            return None

        current_vix = vix_data['close'].iloc[-1]
        vix_mean = vix_data['close'].rolling(63).mean().iloc[-1]
        vix_std = vix_data['close'].rolling(63).std().iloc[-1]

        # Z-score
        if vix_std > 0:
            vix_zscore = (current_vix - vix_mean) / vix_std
        else:
            vix_zscore = 0

        # Store components
        self.components['vix_current'] = current_vix
        self.components['vix_zscore'] = vix_zscore

        # Map to score (lower VIX = higher score)
        # VIX < 15 = 100, VIX > 30 = 0
        if current_vix < 15:
            base_score = 100
        elif current_vix < 20:
            base_score = 80
        elif current_vix < 25:
            base_score = 50
        elif current_vix < 30:
            base_score = 30
        else:
            base_score = 10

        # Adjust for z-score (extreme fear can be contrarian)
        if vix_zscore > 2:
            base_score += 15  # Extreme fear = contrarian buy
        elif vix_zscore < -1:
            base_score -= 10  # Complacency warning

        return np.clip(base_score, 0, 100)

    def _calculate_price_extremes(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate price extreme score using distance from highs/lows.
        """
        if 'SPY' not in data or data['SPY'].empty:
            return None

        spy_data = data['SPY']

        if len(spy_data) < 63:
            return None

        current_price = spy_data['close'].iloc[-1]
        high_63 = spy_data['close'].rolling(63).max().iloc[-1]
        low_63 = spy_data['close'].rolling(63).min().iloc[-1]

        # Distance from high/low
        range_63 = high_63 - low_63

        if range_63 == 0:
            return 50.0

        distance_from_high = (high_63 - current_price) / range_63
        distance_from_low = (current_price - low_63) / range_63

        # Store components
        self.components['distance_from_high'] = distance_from_high * 100
        self.components['distance_from_low'] = distance_from_low * 100

        # Near high = risk-on, near low = risk-off
        score = distance_from_low * 100

        return np.clip(score, 0, 100)

    def get_details(self) -> Dict[str, Any]:
        """Get detailed component breakdown."""
        return {
            'score': self.last_score,
            'components': self.components,
            'status': self.get_status_message(),
        }
