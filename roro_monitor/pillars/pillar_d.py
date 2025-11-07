"""
Pillar D: Currency & Carry Trade Signals (10% Weight)

Analyzes currency pair movements as risk barometers.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

from .base import BasePillar

logger = logging.getLogger(__name__)


class PillarD_CurrencyCarry(BasePillar):
    """
    Pillar D: Currency & Carry Trade Signals

    Components:
    1. JPY Crosses (USDJPY, AUDJPY) (70%)
    2. Risk Currency Momentum (30%)
    """

    def __init__(self):
        super().__init__(name="Pillar D: Currency & Carry Trade", weight=0.10)
        self.components = {}

    def calculate_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate Pillar D score.

        Args:
            data: Dictionary of ticker -> DataFrame

        Returns:
            Score from 0-100
        """
        scores = []

        # 1. JPY Crosses (70%)
        jpy_score = self._calculate_jpy_crosses(data)
        if jpy_score is not None:
            scores.append(('jpy_crosses', jpy_score, 0.70))

        # 2. Currency Momentum (30%)
        momentum_score = self._calculate_currency_momentum(data)
        if momentum_score is not None:
            scores.append(('currency_momentum', momentum_score, 0.30))

        if not scores:
            logger.error("No valid data for Pillar D calculation")
            self.last_score = 50.0
            return 50.0

        # Weighted combination
        final_score = sum(s * w for name, s, w in scores) / sum(w for _, _, w in scores)
        self.last_score = final_score

        # Store components
        self.components = {name: score for name, score, _ in scores}

        logger.info(f"Pillar D Score: {final_score:.1f}")
        return final_score

    def _calculate_jpy_crosses(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate JPY crosses score.
        Rising USDJPY and AUDJPY = Risk-On
        Falling (JPY strengthening) = Risk-Off
        """
        jpy_pairs = ['USDJPY=X', 'AUDJPY=X']
        pair_scores = []

        for pair in jpy_pairs:
            if pair not in data or data[pair].empty or len(data[pair]) < 20:
                logger.warning(f"Missing or insufficient data for {pair}")
                continue

            pair_data = data[pair]

            # Calculate momentum over multiple periods
            ret_5d = (pair_data['close'].iloc[-1] / pair_data['close'].iloc[-5] - 1) * 100
            ret_20d = (pair_data['close'].iloc[-1] / pair_data['close'].iloc[-20] - 1) * 100

            # Average momentum
            avg_momentum = (ret_5d * 0.6 + ret_20d * 0.4)

            # Map to score (rising = risk-on)
            # +2% = 100, -2% = 0
            score = 50 + (avg_momentum * 25)
            pair_scores.append(np.clip(score, 0, 100))

            # Store component data
            self.components[f'{pair}_momentum'] = avg_momentum

        if not pair_scores:
            return None

        return np.mean(pair_scores)

    def _calculate_currency_momentum(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate overall currency momentum score.
        """
        if 'AUDJPY=X' not in data or data['AUDJPY=X'].empty:
            return None

        # AUDJPY is a pure risk proxy
        audjpy_data = data['AUDJPY=X']

        if len(audjpy_data) < 10:
            return None

        # Short-term momentum
        ret_10d = (audjpy_data['close'].iloc[-1] / audjpy_data['close'].iloc[-10] - 1) * 100

        # Map to score
        score = 50 + (ret_10d * 25)

        return np.clip(score, 0, 100)

    def get_details(self) -> Dict[str, Any]:
        """Get detailed component breakdown."""
        return {
            'score': self.last_score,
            'components': self.components,
            'status': self.get_status_message(),
        }
