"""
Master Regime Calculation Engine

Combines all 5 pillars into a unified regime score with conviction weighting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..pillars import (
    PillarA_PriceTrend,
    PillarB_MarketBreadth,
    PillarC_MacroFundamentals,
    PillarD_CurrencyCarry,
    PillarE_Sentiment
)
from ..data import DataFetcher
from ..config import settings

logger = logging.getLogger(__name__)


class RegimeEngine:
    """
    Master Regime Engine - The brain of the RO/RO Monitor.

    Orchestrates all pillars and produces:
    - Master Regime Score (0-100)
    - Regime Classification (STRONG_RISK_ON, etc.)
    - Conviction Level (HIGH, MEDIUM, LOW)
    - Detailed component breakdown
    """

    def __init__(self):
        """Initialize the regime engine with all pillars."""
        self.pillars = [
            PillarA_PriceTrend(),
            PillarB_MarketBreadth(),
            PillarC_MacroFundamentals(),
            PillarD_CurrencyCarry(),
            PillarE_Sentiment(),
        ]

        self.data_fetcher = DataFetcher(use_cache=True)
        self.master_score = None
        self.regime = None
        self.conviction = None
        self.timestamp = None
        self.score_history = []

    def calculate_regime(
        self,
        market_data: Optional[Dict[str, pd.DataFrame]] = None,
        fetch_fresh: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate the current market regime.

        Args:
            market_data: Optional pre-fetched market data
            fetch_fresh: Force fresh data fetch (ignore cache)

        Returns:
            Dictionary with regime analysis
        """
        logger.info("=" * 60)
        logger.info("REGIME CALCULATION STARTED")
        logger.info("=" * 60)

        # Fetch data if not provided
        if market_data is None or fetch_fresh:
            logger.info("Fetching market data...")
            market_data = self.data_fetcher.fetch_all_universe(period='1y', interval='1d')

            if not market_data:
                logger.error("Failed to fetch market data")
                return self._error_response()

        # Calculate each pillar score
        pillar_scores = {}

        for pillar in self.pillars:
            try:
                score = pillar.calculate_score(market_data)
                pillar_scores[pillar.name] = {
                    'score': score,
                    'weight': pillar.weight,
                    'weighted_score': score * pillar.weight,
                    'status': pillar.get_status_message(),
                    'details': pillar.get_details()
                }
                logger.info(f"{pillar.name}: {score:.1f} (weighted: {score * pillar.weight:.1f})")
            except Exception as e:
                logger.error(f"Error calculating {pillar.name}: {e}", exc_info=True)
                pillar_scores[pillar.name] = {
                    'score': 50.0,
                    'weight': pillar.weight,
                    'weighted_score': 50.0 * pillar.weight,
                    'status': 'ERROR',
                    'details': {'error': str(e)}
                }

        # Calculate master score (weighted sum normalized to 0-100)
        weighted_scores = [data['weighted_score'] for data in pillar_scores.values()]
        total_weight = sum(pillar.weight for pillar in self.pillars)
        self.master_score = (sum(weighted_scores) / total_weight) * 100

        # Determine regime and conviction
        self.regime = settings.get_regime_from_score(self.master_score)
        self.conviction = settings.get_conviction_level(self.master_score)
        self.timestamp = datetime.now()

        # Store in history
        self.score_history.append({
            'timestamp': self.timestamp,
            'score': self.master_score,
            'regime': self.regime,
            'conviction': self.conviction
        })

        # Keep only last 90 days of history
        if len(self.score_history) > 90:
            self.score_history = self.score_history[-90:]

        logger.info("=" * 60)
        logger.info(f"MASTER REGIME SCORE: {self.master_score:.1f}")
        logger.info(f"REGIME: {self.regime}")
        logger.info(f"CONVICTION: {self.conviction}")
        logger.info("=" * 60)

        return self._build_response(pillar_scores)

    def _build_response(self, pillar_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive response dictionary."""
        return {
            'master_score': self.master_score,
            'regime': self.regime,
            'conviction': self.conviction,
            'timestamp': self.timestamp,
            'pillar_scores': pillar_scores,
            'color': settings.regime_colors.get(self.regime, '#FFFF00'),
            'summary': self._generate_summary(),
            'key_drivers': self._identify_key_drivers(pillar_scores),
            'score_history': self.score_history[-30:]  # Last 30 datapoints
        }

    def _error_response(self) -> Dict[str, Any]:
        """Return error response."""
        return {
            'master_score': 50.0,
            'regime': 'NEUTRAL',
            'conviction': 'LOW',
            'timestamp': datetime.now(),
            'pillar_scores': {},
            'color': '#FFFF00',
            'summary': 'Error calculating regime',
            'key_drivers': [],
            'error': True
        }

    def _generate_summary(self) -> str:
        """Generate human-readable summary."""
        summaries = []

        if self.regime == 'STRONG_RISK_ON':
            summaries.append("Markets showing strong risk-on characteristics")
        elif self.regime == 'MODERATE_RISK_ON':
            summaries.append("Markets in moderate risk-on mode")
        elif self.regime == 'NEUTRAL':
            summaries.append("Markets in transitional/neutral regime")
        elif self.regime == 'MODERATE_RISK_OFF':
            summaries.append("Markets showing moderate risk-off characteristics")
        elif self.regime == 'STRONG_RISK_OFF':
            summaries.append("Markets in strong risk-off mode")

        summaries.append(f"Conviction level: {self.conviction}")

        return ". ".join(summaries)

    def _identify_key_drivers(self, pillar_scores: Dict[str, Any]) -> List[str]:
        """Identify the key drivers (pillars with extreme scores)."""
        drivers = []

        for pillar_name, data in pillar_scores.items():
            score = data['score']

            if score >= 75:
                drivers.append(f"{pillar_name}: Strong bullish ({score:.0f})")
            elif score <= 25:
                drivers.append(f"{pillar_name}: Strong bearish ({score:.0f})")

        return drivers if drivers else ["All pillars in neutral range"]

    def get_regime_change_alerts(self) -> List[Dict[str, Any]]:
        """
        Detect regime changes based on score history.

        Returns:
            List of alert dictionaries
        """
        alerts = []

        if len(self.score_history) < 2:
            return alerts

        current = self.score_history[-1]
        previous = self.score_history[-2]

        # Check for regime change
        if current['regime'] != previous['regime']:
            alerts.append({
                'type': 'REGIME_CHANGE',
                'severity': 'HIGH',
                'message': f"Regime changed from {previous['regime']} to {current['regime']}",
                'timestamp': current['timestamp']
            })

        # Check for significant score moves
        score_change = current['score'] - previous['score']

        if abs(score_change) > settings.REGIME_CHANGE_THRESHOLD:
            direction = "increased" if score_change > 0 else "decreased"
            alerts.append({
                'type': 'SCORE_CHANGE',
                'severity': 'MEDIUM',
                'message': f"Master score {direction} by {abs(score_change):.1f} points",
                'timestamp': current['timestamp']
            })

        return alerts

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current regime state without recalculating.

        Returns:
            Current state dictionary
        """
        return {
            'master_score': self.master_score,
            'regime': self.regime,
            'conviction': self.conviction,
            'timestamp': self.timestamp,
        }
