"""
Technical indicators for price trend and momentum analysis.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Collection of technical analysis indicators.
    Institutional-grade implementation with proper error handling.
    """

    @staticmethod
    def calculate_moving_averages(
        data: pd.DataFrame,
        periods: list = None
    ) -> pd.DataFrame:
        """
        Calculate multiple Simple Moving Averages.

        Args:
            data: DataFrame with 'close' column
            periods: List of MA periods (default: [50, 100, 200])

        Returns:
            DataFrame with MA columns
        """
        if periods is None:
            periods = [settings.MA_SHORT, settings.MA_MEDIUM, settings.MA_LONG]

        result = data.copy()

        for period in periods:
            result[f'ma_{period}'] = result['close'].rolling(window=period).mean()

        return result

    @staticmethod
    def calculate_rsi(
        data: pd.DataFrame,
        period: int = None
    ) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Args:
            data: DataFrame with 'close' column
            period: RSI period (default from settings)

        Returns:
            Series with RSI values
        """
        if period is None:
            period = settings.RSI_PERIOD

        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(
        data: pd.DataFrame,
        fast: int = None,
        slow: int = None,
        signal: int = None
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            data: DataFrame with 'close' column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        if fast is None:
            fast = settings.MACD_FAST
        if slow is None:
            slow = settings.MACD_SLOW
        if signal is None:
            signal = settings.MACD_SIGNAL

        exp1 = data['close'].ewm(span=fast, adjust=False).mean()
        exp2 = data['close'].ewm(span=slow, adjust=False).mean()

        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.DataFrame,
        period: int = 20,
        num_std: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.

        Args:
            data: DataFrame with 'close' column
            period: Moving average period
            num_std: Number of standard deviations

        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle_band = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()

        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)

        return upper_band, middle_band, lower_band

    @staticmethod
    def calculate_atr(
        data: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range (volatility measure).

        Args:
            data: DataFrame with high, low, close columns
            period: ATR period

        Returns:
            Series with ATR values
        """
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_momentum(
        data: pd.DataFrame,
        period: int = 10
    ) -> pd.Series:
        """
        Calculate price momentum.

        Args:
            data: DataFrame with 'close' column
            period: Lookback period

        Returns:
            Series with momentum values (percentage change)
        """
        return data['close'].pct_change(periods=period) * 100

    @staticmethod
    def ma_alignment_score(data: pd.DataFrame) -> float:
        """
        Score based on moving average alignment.
        Perfect bullish alignment (50 > 100 > 200) = 100
        Perfect bearish alignment (50 < 100 < 200) = 0

        Args:
            data: DataFrame with MA columns

        Returns:
            Score from 0-100
        """
        if data.empty or len(data) < settings.MA_LONG:
            return 50.0  # Neutral

        latest = data.iloc[-1]

        # Check if MAs exist
        required_cols = ['ma_50', 'ma_100', 'ma_200']
        if not all(col in latest.index for col in required_cols):
            return 50.0

        ma_50 = latest['ma_50']
        ma_100 = latest['ma_100']
        ma_200 = latest['ma_200']

        # Price above all MAs
        price = latest['close']

        score = 50.0  # Start neutral

        # Alignment scoring
        if ma_50 > ma_100 > ma_200:
            score += 30  # Bullish alignment
        elif ma_50 < ma_100 < ma_200:
            score -= 30  # Bearish alignment

        # Price position
        if price > ma_50:
            score += 10
        if price > ma_200:
            score += 10
        if price < ma_50:
            score -= 10
        if price < ma_200:
            score -= 10

        return np.clip(score, 0, 100)

    @staticmethod
    def rsi_regime_score(rsi: pd.Series) -> float:
        """
        Score based on RSI regime.
        Penalizes extreme overbought/oversold conditions.

        Args:
            rsi: RSI series

        Returns:
            Score from 0-100
        """
        if rsi.empty:
            return 50.0

        current_rsi = rsi.iloc[-1]

        if np.isnan(current_rsi):
            return 50.0

        # Optimal RSI range is 40-60 (neutral with slight bullish bias)
        if 40 <= current_rsi <= 60:
            score = 100
        elif current_rsi > settings.RSI_OVERBOUGHT:
            # Overbought - potential reversal risk
            score = max(0, 100 - (current_rsi - settings.RSI_OVERBOUGHT) * 2)
        elif current_rsi < settings.RSI_OVERSOLD:
            # Oversold - potential reversal opportunity
            score = max(0, current_rsi / settings.RSI_OVERSOLD * 50)
        elif current_rsi > 60:
            # Mildly overbought
            score = 80 - (current_rsi - 60) * 2
        else:
            # Below 40
            score = 50 + (current_rsi - 40) * 2.5

        return np.clip(score, 0, 100)

    @staticmethod
    def macd_signal_score(histogram: pd.Series) -> float:
        """
        Score based on MACD histogram direction and strength.

        Args:
            histogram: MACD histogram series

        Returns:
            Score from 0-100
        """
        if histogram.empty or len(histogram) < 5:
            return 50.0

        current = histogram.iloc[-1]
        previous = histogram.iloc[-2]

        if np.isnan(current) or np.isnan(previous):
            return 50.0

        # Base score on histogram value
        if current > 0:
            base_score = 60
        else:
            base_score = 40

        # Adjust for momentum
        if current > previous:
            base_score += 20  # Bullish momentum
        else:
            base_score -= 20  # Bearish momentum

        # Check for recent crossover
        recent_cross_up = (histogram.iloc[-3:] < 0).any() and current > 0
        recent_cross_down = (histogram.iloc[-3:] > 0).any() and current < 0

        if recent_cross_up:
            base_score += 15
        elif recent_cross_down:
            base_score -= 15

        return np.clip(base_score, 0, 100)

    @staticmethod
    def calculate_roc(
        data: pd.DataFrame,
        period: int = 5
    ) -> pd.Series:
        """
        Calculate Rate of Change (ROC) indicator.

        ROC is a leading momentum indicator that measures the percentage
        change in price over a specified period.

        Args:
            data: DataFrame with 'close' column
            period: Number of periods for ROC calculation (default: 5)

        Returns:
            Series with ROC values
        """
        close = data['close']
        roc = ((close - close.shift(period)) / close.shift(period)) * 100
        return roc

    @staticmethod
    def roc_momentum_score(data: pd.DataFrame, period: int = 5) -> float:
        """
        Score based on Rate of Change momentum.

        Leading indicator for early trend detection.

        Args:
            data: DataFrame with price data
            period: ROC period (default: 5 days)

        Returns:
            Score from 0-100
        """
        if data.empty or len(data) < period + 1:
            return 50.0

        roc = TechnicalIndicators.calculate_roc(data, period)

        if roc.empty or pd.isna(roc.iloc[-1]):
            return 50.0

        current_roc = roc.iloc[-1]

        # Score based on ROC value and direction
        score = 50.0

        # Positive/negative momentum
        if current_roc > 2.0:
            score = 70 + min(30, current_roc * 3)  # Strong positive
        elif current_roc > 0:
            score = 50 + (current_roc / 2.0) * 20  # Moderate positive
        elif current_roc > -2.0:
            score = 50 + (current_roc / 2.0) * 20  # Moderate negative
        else:
            score = 30 + max(-30, current_roc * 3)  # Strong negative

        return np.clip(score, 0, 100)

    @staticmethod
    def momentum_divergence_score(
        data: pd.DataFrame,
        rsi: pd.Series,
        lookback: int = 20
    ) -> float:
        """
        Detect bullish/bearish divergences between price and RSI.

        Divergences are powerful leading indicators:
        - Bullish divergence: Price makes lower low, RSI makes higher low
        - Bearish divergence: Price makes higher high, RSI makes lower high

        Args:
            data: DataFrame with price data
            rsi: RSI series
            lookback: Period to check for divergences

        Returns:
            Score from 0-100 (>50 = bullish divergence, <50 = bearish)
        """
        if data.empty or rsi.empty or len(data) < lookback:
            return 50.0

        recent_data = data.iloc[-lookback:]
        recent_rsi = rsi.iloc[-lookback:]

        # Find price highs/lows
        price_high_idx = recent_data['close'].idxmax()
        price_low_idx = recent_data['close'].idxmin()

        # Find RSI highs/lows
        rsi_high_idx = recent_rsi.idxmax()
        rsi_low_idx = recent_rsi.idxmin()

        score = 50.0  # Neutral

        # Bullish divergence check (price lower low, RSI higher low)
        if price_low_idx < len(recent_data) - 5:  # Not too recent
            price_trend = recent_data['close'].iloc[-1] - recent_data['close'].iloc[price_low_idx]
            rsi_trend = recent_rsi.iloc[-1] - recent_rsi.iloc[rsi_low_idx]

            if price_trend < 0 and rsi_trend > 0:
                score = 70  # Bullish divergence

        # Bearish divergence check (price higher high, RSI lower high)
        if price_high_idx < len(recent_data) - 5:  # Not too recent
            price_trend = recent_data['close'].iloc[-1] - recent_data['close'].iloc[price_high_idx]
            rsi_trend = recent_rsi.iloc[-1] - recent_rsi.iloc[rsi_high_idx]

            if price_trend > 0 and rsi_trend < 0:
                score = 30  # Bearish divergence

        return score

    @staticmethod
    def fast_ma_crossover_score(data: pd.DataFrame) -> float:
        """
        Score based on fast MA (20-day) crossover with medium MA (50-day).

        Early trend detection signal.

        Args:
            data: DataFrame with MA columns

        Returns:
            Score from 0-100
        """
        if data.empty or len(data) < settings.MA_SHORT:
            return 50.0

        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest

        # Calculate fast MA if not present
        if 'ma_20' not in latest.index:
            data['ma_20'] = data['close'].rolling(window=settings.MA_FAST).mean()
            latest = data.iloc[-1]
            previous = data.iloc[-2] if len(data) > 1 else latest

        if 'ma_50' not in latest.index:
            return 50.0

        ma_20_current = latest['ma_20']
        ma_50_current = latest['ma_50']
        ma_20_prev = previous['ma_20'] if 'ma_20' in previous.index else ma_20_current
        ma_50_prev = previous['ma_50'] if 'ma_50' in previous.index else ma_50_current

        score = 50.0

        # Check for crossover
        if ma_20_current > ma_50_current:
            score = 70  # Bullish position
            if ma_20_prev <= ma_50_prev:  # Recent crossover
                score = 85  # Strong bullish signal
        elif ma_20_current < ma_50_current:
            score = 30  # Bearish position
            if ma_20_prev >= ma_50_prev:  # Recent crossover
                score = 15  # Strong bearish signal

        return score
