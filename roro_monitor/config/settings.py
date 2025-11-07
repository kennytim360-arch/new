"""
Configuration and settings for the Institutional RO/RO Monitor.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class Settings:
    """Master configuration for the RO/RO Monitor system."""

    # Pillar Weights (must sum to 1.0)
    PILLAR_WEIGHTS: Dict[str, float] = None

    # Regime Classification Thresholds
    REGIME_THRESHOLDS: Dict[str, tuple] = None

    # Timeframes for analysis
    TIMEFRAMES: Dict[str, int] = None

    # Technical Indicator Parameters
    MA_SHORT: int = 50
    MA_MEDIUM: int = 100
    MA_LONG: int = 200
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: float = 70.0
    RSI_OVERSOLD: float = 30.0
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9

    # Alert Thresholds
    CREDIT_SPREAD_ALERT_STD: float = 2.0
    REGIME_CHANGE_THRESHOLD: int = 10  # points on the 0-100 scale

    # Data Parameters
    LOOKBACK_DAYS: int = 252  # ~1 year of trading days
    DATA_CACHE_HOURS: int = 1

    # Dashboard Settings
    DASHBOARD_PORT: int = 8050
    DASHBOARD_DEBUG: bool = True
    DASHBOARD_REFRESH_SECONDS: int = 300  # 5 minutes

    def __post_init__(self):
        """Initialize default values."""
        if self.PILLAR_WEIGHTS is None:
            self.PILLAR_WEIGHTS = {
                'pillar_a': 0.30,  # Price Trend & Momentum
                'pillar_b': 0.25,  # Market Breadth & Health
                'pillar_c': 0.25,  # Macro-Fundamental Drivers
                'pillar_d': 0.10,  # Currency & Carry Trade
                'pillar_e': 0.10,  # Sentiment & Positioning
            }

        if self.REGIME_THRESHOLDS is None:
            self.REGIME_THRESHOLDS = {
                'STRONG_RISK_ON': (80, 100),
                'MODERATE_RISK_ON': (60, 79),
                'NEUTRAL': (40, 59),
                'MODERATE_RISK_OFF': (20, 39),
                'STRONG_RISK_OFF': (0, 19),
            }

        if self.TIMEFRAMES is None:
            self.TIMEFRAMES = {
                'daily': 1,
                'weekly': 5,
                'monthly': 21,
            }

    @property
    def regime_colors(self) -> Dict[str, str]:
        """Color coding for regime visualization."""
        return {
            'STRONG_RISK_ON': '#00FF00',      # Bright Green
            'MODERATE_RISK_ON': '#90EE90',    # Light Green
            'NEUTRAL': '#FFFF00',              # Yellow
            'MODERATE_RISK_OFF': '#FFA500',   # Orange
            'STRONG_RISK_OFF': '#FF0000',     # Red
        }

    def get_regime_from_score(self, score: float) -> str:
        """Determine regime classification from master score."""
        for regime, (low, high) in self.REGIME_THRESHOLDS.items():
            if low <= score <= high:
                return regime
        return 'NEUTRAL'

    def get_conviction_level(self, score: float) -> str:
        """Determine conviction level based on score."""
        regime = self.get_regime_from_score(score)
        if 'STRONG' in regime:
            return 'HIGH'
        elif 'MODERATE' in regime:
            return 'MEDIUM'
        else:
            return 'LOW'


# Global settings instance
settings = Settings()
