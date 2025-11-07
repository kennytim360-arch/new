"""
Pillar A: Price Trend & Momentum (30% Weight)

Analyzes moving average alignment, RSI regime, and MACD signals
across multiple timeframes.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

from .base import BasePillar
from ..indicators import TechnicalIndicators
from ..config import AssetUniverse, settings

logger = logging.getLogger(__name__)


class PillarA_PriceTrend(BasePillar):
    """
    Pillar A: Price Trend & Momentum Analysis

    Components:
    1. Moving Average Alignment (40%)
    2. RSI Regime (30%)
    3. MACD Signal (30%)
    """

    def __init__(self):
        super().__init__(name="Pillar A: Price Trend & Momentum", weight=0.30)
        self.tech_indicators = TechnicalIndicators()
        self.components = {}

    def calculate_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate Pillar A score.

        Args:
            data: Dictionary of ticker -> DataFrame

        Returns:
            Score from 0-100
        """
        # Focus on key risk assets
        key_assets = ['SPY', 'QQQ', 'IWM']
        scores = []

        for ticker in key_assets:
            if ticker not in data or data[ticker].empty:
                logger.warning(f"Missing data for {ticker}")
                continue

            ticker_data = data[ticker].copy()

            # 1. Moving Average Alignment
            ticker_data = self.tech_indicators.calculate_moving_averages(ticker_data)
            ma_score = self.tech_indicators.ma_alignment_score(ticker_data)

            # 2. RSI Regime
            rsi = self.tech_indicators.calculate_rsi(ticker_data)
            rsi_score = self.tech_indicators.rsi_regime_score(rsi)

            # 3. MACD Signal
            macd_line, signal_line, histogram = self.tech_indicators.calculate_macd(ticker_data)
            macd_score = self.tech_indicators.macd_signal_score(histogram)

            # Weighted combination for this ticker
            ticker_score = (ma_score * 0.40 + rsi_score * 0.30 + macd_score * 0.30)
            scores.append(ticker_score)

            # Store component scores for the primary asset (SPY)
            if ticker == 'SPY':
                self.components = {
                    'ma_alignment': ma_score,
                    'rsi_regime': rsi_score,
                    'macd_signal': macd_score,
                    'ma_50': ticker_data['ma_50'].iloc[-1] if 'ma_50' in ticker_data.columns else np.nan,
                    'ma_200': ticker_data['ma_200'].iloc[-1] if 'ma_200' in ticker_data.columns else np.nan,
                    'current_rsi': rsi.iloc[-1] if not rsi.empty else np.nan,
                    'current_price': ticker_data['close'].iloc[-1],
                }

        if not scores:
            logger.error("No valid data for Pillar A calculation")
            self.last_score = 50.0
            return 50.0

        # Average score across key assets
        final_score = np.mean(scores)
        self.last_score = final_score

        logger.info(f"Pillar A Score: {final_score:.1f}")
        return final_score

    def get_details(self) -> Dict[str, Any]:
        """Get detailed component breakdown."""
        return {
            'score': self.last_score,
            'components': self.components,
            'status': self.get_status_message(),
            'interpretation': self._get_interpretation()
        }

    def _get_interpretation(self) -> str:
        """Generate human-readable interpretation."""
        if not self.components:
            return "Insufficient data for interpretation"

        ma_score = self.components.get('ma_alignment', 50)
        rsi_score = self.components.get('rsi_regime', 50)
        macd_score = self.components.get('macd_signal', 50)

        interpretations = []

        if ma_score > 70:
            interpretations.append("Strong bullish trend structure")
        elif ma_score < 30:
            interpretations.append("Weak bearish trend structure")

        if rsi_score > 70:
            interpretations.append("Healthy momentum")
        elif rsi_score < 30:
            interpretations.append("Weak momentum, potential oversold")

        if macd_score > 70:
            interpretations.append("Positive MACD momentum")
        elif macd_score < 30:
            interpretations.append("Negative MACD momentum")

        return "; ".join(interpretations) if interpretations else "Neutral conditions"
