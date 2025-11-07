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
    # OPTIMIZED (Nov 2025) - Added fast MA for early signals, adjusted RSI
    MA_FAST: int = 20      # NEW: Fast MA for early trend detection
    MA_SHORT: int = 50
    MA_MEDIUM: int = 100
    MA_LONG: int = 200
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: float = 65.0   # OPTIMIZED: Was 70.0 (earlier signals)
    RSI_OVERSOLD: float = 35.0     # OPTIMIZED: Was 30.0 (earlier signals)
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
            # REBALANCED WEIGHTS (Nov 2025 v2) - More measured approach
            # First optimization was too aggressive with leading indicators
            # This version maintains offense but adds stability
            self.PILLAR_WEIGHTS = {
                'pillar_a': 0.32,  # Price Trend & Momentum (was 0.35, now 0.32)
                'pillar_b': 0.25,  # Market Breadth & Health (unchanged)
                'pillar_c': 0.23,  # Macro-Fundamental Drivers (was 0.20, now 0.23 - more stability)
                'pillar_d': 0.10,  # Currency & Carry Trade (unchanged)
                'pillar_e': 0.10,  # Sentiment & Positioning (unchanged)
            }

        if self.REGIME_THRESHOLDS is None:
            # v4: Made Risk-Off harder to trigger (was 20-39, now 15-39)
            # Reason: MODERATE_RISK_OFF had -1.618% avg returns (catastrophic)
            # Fewer Risk-Off periods + defensive allocation = better protection
            self.REGIME_THRESHOLDS = {
                'STRONG_RISK_ON': (80, 100),
                'MODERATE_RISK_ON': (60, 79),
                'NEUTRAL': (40, 59),
                'MODERATE_RISK_OFF': (15, 39),  # CHANGED from (20, 39) - harder to trigger
                'STRONG_RISK_OFF': (0, 14),      # CHANGED from (0, 19) - only extreme fear
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
