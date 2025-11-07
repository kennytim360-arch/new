"""
Macro indicators for fundamental regime analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MacroIndicators:
    """
    Macro-fundamental indicators for regime analysis.
    """

    @staticmethod
    def calculate_relative_strength(
        asset1: pd.DataFrame,
        asset2: pd.DataFrame,
        period: int = 20
    ) -> pd.Series:
        """
        Calculate relative strength between two assets.

        Args:
            asset1: First asset DataFrame
            asset2: Second asset DataFrame
            period: Lookback period for momentum

        Returns:
            Series with relative strength ratio
        """
        ratio = asset1['close'] / asset2['close']
        rs_momentum = ratio.pct_change(periods=period) * 100

        return rs_momentum

    @staticmethod
    def calculate_correlation(
        asset1: pd.DataFrame,
        asset2: pd.DataFrame,
        window: int = 30
    ) -> pd.Series:
        """
        Calculate rolling correlation between two assets.

        Args:
            asset1: First asset DataFrame
            asset2: Second asset DataFrame
            window: Rolling window size

        Returns:
            Series with rolling correlation
        """
        returns1 = asset1['close'].pct_change()
        returns2 = asset2['close'].pct_change()

        return returns1.rolling(window=window).corr(returns2)

    @staticmethod
    def sector_rotation_score(
        cyclical_data: Dict[str, pd.DataFrame],
        defensive_data: Dict[str, pd.DataFrame],
        period: int = 20
    ) -> float:
        """
        Score based on cyclical vs defensive sector performance.

        Args:
            cyclical_data: Dictionary of cyclical sector DataFrames
            defensive_data: Dictionary of defensive sector DataFrames
            period: Performance lookback period

        Returns:
            Score from 0-100 (higher = risk-on)
        """
        # Calculate average performance of each group
        cyclical_returns = []
        for ticker, data in cyclical_data.items():
            if not data.empty and len(data) > period:
                ret = (data['close'].iloc[-1] / data['close'].iloc[-period] - 1) * 100
                cyclical_returns.append(ret)

        defensive_returns = []
        for ticker, data in defensive_data.items():
            if not data.empty and len(data) > period:
                ret = (data['close'].iloc[-1] / data['close'].iloc[-period] - 1) * 100
                defensive_returns.append(ret)

        if not cyclical_returns or not defensive_returns:
            return 50.0

        avg_cyclical = np.mean(cyclical_returns)
        avg_defensive = np.mean(defensive_returns)

        # Outperformance differential
        differential = avg_cyclical - avg_defensive

        # Map to 0-100 scale
        # +10% outperformance = 100, -10% = 0
        score = 50 + (differential * 5)

        return np.clip(score, 0, 100)

    @staticmethod
    def breadth_divergence_score(
        index_data: pd.DataFrame,
        breadth_indicator: pd.Series
    ) -> float:
        """
        Detect divergence between price and breadth.

        Args:
            index_data: Index price DataFrame
            breadth_indicator: Advance/Decline or breadth series

        Returns:
            Score from 0-100 (lower = more divergence/warning)
        """
        if index_data.empty or breadth_indicator.empty:
            return 50.0

        # Compare recent trends
        price_trend = index_data['close'].iloc[-20:].values
        breadth_trend = breadth_indicator.iloc[-20:].values

        # Calculate correlations
        if len(price_trend) != len(breadth_trend):
            return 50.0

        correlation = np.corrcoef(price_trend, breadth_trend)[0, 1]

        # High correlation = no divergence = good
        # Low/negative correlation = divergence = warning
        score = (correlation + 1) * 50  # Map -1 to 1 => 0 to 100

        return np.clip(score, 0, 100)

    @staticmethod
    def vix_term_structure_score(vix_term_structure: Dict[str, float]) -> float:
        """
        Score based on VIX term structure.

        Args:
            vix_term_structure: Dictionary with VIX term structure data

        Returns:
            Score from 0-100 (higher = less fear)
        """
        if not vix_term_structure:
            return 50.0

        spot = vix_term_structure.get('spot', 20)
        slope = vix_term_structure.get('slope', 0)

        # Low VIX + positive slope (contango) = bullish
        # High VIX + negative slope (backwardation) = bearish

        score = 50.0

        # Adjust for VIX level
        if spot < 15:
            score += 30
        elif spot < 20:
            score += 15
        elif spot > 30:
            score -= 30
        elif spot > 25:
            score -= 15

        # Adjust for term structure
        if slope > 2:
            score += 20  # Strong contango
        elif slope > 0:
            score += 10  # Mild contango
        elif slope < -2:
            score -= 20  # Strong backwardation
        elif slope < 0:
            score -= 10  # Mild backwardation

        return np.clip(score, 0, 100)

    @staticmethod
    def credit_spread_score(credit_spreads: Dict[str, float]) -> float:
        """
        Score based on credit spread levels and direction.

        Args:
            credit_spreads: Dictionary with credit spread data

        Returns:
            Score from 0-100 (higher = tighter spreads = risk-on)
        """
        if not credit_spreads:
            return 50.0

        hy_spread = credit_spreads.get('hy_spread', 0)
        spread_widening = credit_spreads.get('spread_widening', False)

        score = 50.0

        # Tighter spreads = bullish
        if hy_spread < -2:
            score += 30
        elif hy_spread < 0:
            score += 15
        elif hy_spread > 3:
            score -= 30
        elif hy_spread > 1:
            score -= 15

        # Widening spreads = bearish
        if spread_widening:
            score -= 20

        return np.clip(score, 0, 100)

    @staticmethod
    def safe_haven_flow_score(
        tlt_data: pd.DataFrame,
        gld_data: pd.DataFrame,
        period: int = 20
    ) -> float:
        """
        Score based on safe-haven asset flows (TLT, GLD).

        Args:
            tlt_data: Treasury bond ETF data
            gld_data: Gold ETF data
            period: Lookback period

        Returns:
            Score from 0-100 (lower = more safe-haven flows = risk-off)
        """
        if tlt_data.empty or gld_data.empty:
            return 50.0

        # Calculate recent performance
        tlt_return = (tlt_data['close'].iloc[-1] / tlt_data['close'].iloc[-period] - 1) * 100
        gld_return = (gld_data['close'].iloc[-1] / gld_data['close'].iloc[-period] - 1) * 100

        # Strong safe-haven flows = bearish for risk
        avg_safe_haven = (tlt_return + gld_return) / 2

        # Map to score (inverse relationship)
        # +5% safe-haven rally = 25 score (risk-off)
        # -5% safe-haven decline = 75 score (risk-on)
        score = 50 - (avg_safe_haven * 5)

        return np.clip(score, 0, 100)

    @staticmethod
    def sector_rotation_score(
        financials_data: pd.DataFrame,
        cyclicals_data: pd.DataFrame,
        defensives_data: pd.DataFrame,
        period: int = 20
    ) -> float:
        """
        Score based on sector rotation patterns.

        Early cycle: Financials and cyclicals outperform
        Late cycle: Defensives outperform
        Risk-off: Defensives significantly outperform

        Args:
            financials_data: XLF (Financial sector) data
            cyclicals_data: XLI (Industrial sector) data
            defensives_data: XLP (Consumer staples) data
            period: Lookback period

        Returns:
            Score from 0-100
        """
        if financials_data.empty or cyclicals_data.empty or defensives_data.empty:
            return 50.0

        if len(financials_data) < period or len(cyclicals_data) < period or len(defensives_data) < period:
            return 50.0

        # Calculate relative performance
        xlf_return = (financials_data['close'].iloc[-1] / financials_data['close'].iloc[-period] - 1) * 100
        xli_return = (cyclicals_data['close'].iloc[-1] / cyclicals_data['close'].iloc[-period] - 1) * 100
        xlp_return = (defensives_data['close'].iloc[-1] / defensives_data['close'].iloc[-period] - 1) * 100

        # Financial sector strength = confidence = Risk-On
        # Cyclicals strength = growth = Risk-On
        # Defensives relative weakness = Risk-On

        risk_on_sectors = (xlf_return + xli_return) / 2
        risk_off_sectors = xlp_return

        # Relative strength
        relative_strength = risk_on_sectors - risk_off_sectors

        # Score based on rotation
        score = 50.0

        if relative_strength > 5:
            score = 75  # Strong Risk-On rotation
        elif relative_strength > 2:
            score = 65  # Moderate Risk-On rotation
        elif relative_strength > -2:
            score = 50  # Neutral
        elif relative_strength > -5:
            score = 35  # Moderate Risk-Off rotation
        else:
            score = 25  # Strong Risk-Off rotation

        return score

    @staticmethod
    def financial_sector_leadership_score(
        xlf_data: pd.DataFrame,
        spy_data: pd.DataFrame,
        period: int = 20
    ) -> float:
        """
        Financial sector relative strength as confidence indicator.

        Financials leading = Economic confidence = Risk-On
        Financials lagging = Economic concern = Risk-Off

        Args:
            xlf_data: Financial sector ETF (XLF) data
            spy_data: S&P 500 ETF (SPY) data
            period: Lookback period

        Returns:
            Score from 0-100
        """
        if xlf_data.empty or spy_data.empty:
            return 50.0

        if len(xlf_data) < period or len(spy_data) < period:
            return 50.0

        # Calculate returns
        xlf_return = (xlf_data['close'].iloc[-1] / xlf_data['close'].iloc[-period] - 1) * 100
        spy_return = (spy_data['close'].iloc[-1] / spy_data['close'].iloc[-period] - 1) * 100

        # Relative strength
        relative_strength = xlf_return - spy_return

        # Score based on leadership
        score = 50.0

        if relative_strength > 3:
            score = 80  # Strong financial leadership = high confidence
        elif relative_strength > 1:
            score = 65  # Moderate leadership
        elif relative_strength > -1:
            score = 50  # Neutral
        elif relative_strength > -3:
            score = 35  # Lagging
        else:
            score = 20  # Significant underperformance = low confidence

        return score

    @staticmethod
    def small_cap_large_cap_ratio_score(
        iwm_data: pd.DataFrame,
        spy_data: pd.DataFrame,
        period: int = 20
    ) -> float:
        """
        Small-cap vs Large-cap relative strength as risk appetite indicator.

        Small-caps outperforming = High risk appetite = Risk-On
        Large-caps outperforming = Risk aversion = Risk-Off

        Args:
            iwm_data: Russell 2000 ETF (IWM) data
            spy_data: S&P 500 ETF (SPY) data
            period: Lookback period

        Returns:
            Score from 0-100
        """
        if iwm_data.empty or spy_data.empty:
            return 50.0

        if len(iwm_data) < period or len(spy_data) < period:
            return 50.0

        # Calculate returns
        iwm_return = (iwm_data['close'].iloc[-1] / iwm_data['close'].iloc[-period] - 1) * 100
        spy_return = (spy_data['close'].iloc[-1] / spy_data['close'].iloc[-period] - 1) * 100

        # Relative strength
        relative_strength = iwm_return - spy_return

        # Score based on risk appetite
        score = 50.0

        if relative_strength > 4:
            score = 85  # Extreme risk appetite
        elif relative_strength > 2:
            score = 70  # High risk appetite
        elif relative_strength > -2:
            score = 50  # Neutral
        elif relative_strength > -4:
            score = 30  # Risk aversion
        else:
            score = 15  # Extreme risk aversion

        return score
