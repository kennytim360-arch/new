# ============================================================================
# RO/RO Monitor - Data Module Installation Script
# This script creates the missing roro_monitor/data module files
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  RO/RO Monitor - Data Module Installation" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Host "ERROR: main.py not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Creating data directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "roro_monitor\data" -Force | Out-Null
Write-Host "  -> Created: roro_monitor\data\" -ForegroundColor Green

# ============================================================================
# FILE 1: __init__.py
# ============================================================================

Write-Host ""
Write-Host "Step 2: Creating __init__.py..." -ForegroundColor Yellow

$init_content = @'
"""Data ingestion and management package."""

from .fetcher import DataFetcher
from .cache import DataCache

__all__ = ['DataFetcher', 'DataCache']
'@

$init_content | Out-File -FilePath "roro_monitor\data\__init__.py" -Encoding UTF8 -NoNewline
Write-Host "  -> Created: roro_monitor\data\__init__.py (148 bytes)" -ForegroundColor Green

# ============================================================================
# FILE 2: cache.py
# ============================================================================

Write-Host ""
Write-Host "Step 3: Creating cache.py..." -ForegroundColor Yellow

$cache_content = @'
"""
Data caching utilities for the RO/RO Monitor.
Reduces API calls and improves performance.
"""

import pandas as pd
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataCache:
    """
    File-based caching system for market data.
    Reduces redundant API calls within a configurable time window.
    """

    def __init__(self, cache_dir: str = ".cache", cache_hours: int = 1):
        """
        Initialize the data cache.

        Args:
            cache_dir: Directory to store cached data
            cache_hours: Number of hours before cache expires
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_hours = cache_hours

    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path for a given key."""
        safe_key = key.replace("/", "_").replace("=", "_")
        return self.cache_dir / f"{safe_key}.pkl"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file exists and is still valid."""
        if not cache_path.exists():
            return False

        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        expiry_time = datetime.now() - timedelta(hours=self.cache_hours)

        return file_time > expiry_time

    def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        Retrieve data from cache if available and valid.

        Args:
            key: Unique identifier for the cached data

        Returns:
            Cached DataFrame or None if cache miss/expired
        """
        cache_path = self._get_cache_path(key)

        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                logger.info(f"Cache HIT for {key}")
                return data
            except Exception as e:
                logger.warning(f"Cache read error for {key}: {e}")
                return None
        else:
            logger.info(f"Cache MISS for {key}")
            return None

    def set(self, key: str, data: pd.DataFrame) -> None:
        """
        Store data in cache.

        Args:
            key: Unique identifier for the data
            data: DataFrame to cache
        """
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Cached data for {key}")
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")

    def clear(self) -> None:
        """Clear all cached data."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        logger.info("Cache cleared")

    def clear_expired(self) -> None:
        """Remove only expired cache entries."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            if not self._is_cache_valid(cache_file):
                cache_file.unlink()
                logger.info(f"Removed expired cache: {cache_file.name}")
'@

$cache_content | Out-File -FilePath "roro_monitor\data\cache.py" -Encoding UTF8 -NoNewline
Write-Host "  -> Created: roro_monitor\data\cache.py (3,177 bytes)" -ForegroundColor Green

# ============================================================================
# FILE 3: fetcher.py
# ============================================================================

Write-Host ""
Write-Host "Step 4: Creating fetcher.py..." -ForegroundColor Yellow

$fetcher_content = @'
"""
Multi-source data fetcher for the Institutional RO/RO Monitor.
Tier-1 data ingestion with fallback mechanisms and caching.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import AssetUniverse, settings
from .cache import DataCache

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Institutional-grade multi-source data fetcher.
    Supports Yahoo Finance with planned extensions for Bloomberg API.
    """

    def __init__(self, use_cache: bool = True):
        """
        Initialize the data fetcher.

        Args:
            use_cache: Whether to use caching for data
        """
        self.cache = DataCache(cache_hours=settings.DATA_CACHE_HOURS) if use_cache else None
        self.asset_universe = AssetUniverse()

    def fetch_single_ticker(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data for a single ticker.

        Args:
            ticker: Ticker symbol
            period: Time period (e.g., '1y', '6mo', '3mo')
            interval: Data interval (e.g., '1d', '1h')

        Returns:
            DataFrame with OHLCV data or None on failure
        """
        cache_key = f"{ticker}_{period}_{interval}"

        # Check cache first
        if self.cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        try:
            logger.info(f"Fetching {ticker} from Yahoo Finance")
            ticker_obj = yf.Ticker(ticker)
            data = ticker_obj.history(period=period, interval=interval)

            if data.empty:
                logger.warning(f"No data returned for {ticker}")
                return None

            # Standardize column names
            data.columns = [col.lower() for col in data.columns]

            # Cache the data
            if self.cache:
                self.cache.set(cache_key, data)

            return data

        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}")
            return None

    def fetch_multiple_tickers(
        self,
        tickers: List[str],
        period: str = "1y",
        interval: str = "1d",
        max_workers: int = 10
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple tickers concurrently.

        Args:
            tickers: List of ticker symbols
            period: Time period
            interval: Data interval
            max_workers: Maximum concurrent threads

        Returns:
            Dictionary mapping ticker to DataFrame
        """
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(self.fetch_single_ticker, ticker, period, interval): ticker
                for ticker in tickers
            }

            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    data = future.result()
                    if data is not None:
                        results[ticker] = data
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {e}")

        logger.info(f"Successfully fetched {len(results)}/{len(tickers)} tickers")
        return results

    def fetch_all_universe(
        self,
        period: str = "1y",
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch all tickers in the asset universe.

        Args:
            period: Time period
            interval: Data interval

        Returns:
            Dictionary mapping ticker to DataFrame
        """
        all_tickers = self.asset_universe.get_all_tickers()
        logger.info(f"Fetching complete asset universe: {len(all_tickers)} tickers")
        return self.fetch_multiple_tickers(all_tickers, period, interval)

    def get_latest_prices(self, tickers: List[str]) -> Dict[str, float]:
        """
        Get the most recent closing prices for a list of tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dictionary mapping ticker to latest close price
        """
        data = self.fetch_multiple_tickers(tickers, period="5d", interval="1d")
        prices = {}

        for ticker, df in data.items():
            if not df.empty:
                prices[ticker] = df['close'].iloc[-1]

        return prices

    def calculate_returns(
        self,
        data: pd.DataFrame,
        periods: List[int] = [1, 5, 21, 63]
    ) -> pd.DataFrame:
        """
        Calculate returns over multiple periods.

        Args:
            data: DataFrame with 'close' column
            periods: List of lookback periods in days

        Returns:
            DataFrame with return columns
        """
        returns_df = pd.DataFrame(index=data.index)

        for period in periods:
            col_name = f'return_{period}d'
            returns_df[col_name] = data['close'].pct_change(periods=period) * 100

        return returns_df

    def get_market_snapshot(self) -> Dict[str, any]:
        """
        Get a comprehensive snapshot of current market conditions.

        Returns:
            Dictionary with key market metrics
        """
        snapshot = {
            'timestamp': datetime.now(),
            'prices': {},
            'changes_1d': {},
            'changes_5d': {},
        }

        # Fetch key instruments
        key_tickers = ['SPY', 'QQQ', 'TLT', 'HYG', '^VIX', 'GLD']
        data = self.fetch_multiple_tickers(key_tickers, period="1mo", interval="1d")

        for ticker, df in data.items():
            if not df.empty and len(df) > 5:
                latest_price = df['close'].iloc[-1]
                snapshot['prices'][ticker] = latest_price
                snapshot['changes_1d'][ticker] = ((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) * 100
                snapshot['changes_5d'][ticker] = ((df['close'].iloc[-1] / df['close'].iloc[-6]) - 1) * 100

        return snapshot

    def get_vix_term_structure(self) -> Optional[Dict[str, float]]:
        """
        Calculate VIX term structure (spot vs futures).
        Note: Simplified version using VIX history as proxy.

        Returns:
            Dictionary with term structure metrics
        """
        vix_data = self.fetch_single_ticker('^VIX', period='3mo', interval='1d')

        if vix_data is None or vix_data.empty:
            return None

        # Calculate implied term structure using historical volatility
        spot_vix = vix_data['close'].iloc[-1]
        avg_3m_vix = vix_data['close'].rolling(63).mean().iloc[-1]

        return {
            'spot': spot_vix,
            '3m_avg': avg_3m_vix,
            'slope': avg_3m_vix - spot_vix,
            'backwardation': avg_3m_vix < spot_vix
        }

    def calculate_credit_spreads(self) -> Optional[Dict[str, float]]:
        """
        Calculate credit spreads (HYG/LQD vs IEF).

        Returns:
            Dictionary with spread metrics
        """
        tickers = ['HYG', 'LQD', 'IEF']
        data = self.fetch_multiple_tickers(tickers, period='6mo', interval='1d')

        if any(ticker not in data for ticker in tickers):
            logger.warning("Missing data for credit spread calculation")
            return None

        # Simplified spread calculation using yield proxies
        # In production, you'd fetch actual yield data
        hyg_return = data['HYG']['close'].pct_change(21).iloc[-1]
        ief_return = data['IEF']['close'].pct_change(21).iloc[-1]
        lqd_return = data['LQD']['close'].pct_change(21).iloc[-1]

        return {
            'hy_spread': hyg_return - ief_return,
            'ig_spread': lqd_return - ief_return,
            'spread_widening': (hyg_return - ief_return) > data['HYG']['close'].pct_change(63).iloc[-1]
        }
'@

$fetcher_content | Out-File -FilePath "roro_monitor\data\fetcher.py" -Encoding UTF8 -NoNewline
Write-Host "  -> Created: roro_monitor\data\fetcher.py (8,145 bytes)" -ForegroundColor Green

# ============================================================================
# VERIFICATION
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  Verification" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check all files exist
$requiredFiles = @(
    "roro_monitor\data\__init__.py",
    "roro_monitor\data\cache.py",
    "roro_monitor\data\fetcher.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "  [OK] $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $file NOT FOUND" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""

if ($allGood) {
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host "  SUCCESS! All files created successfully" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Install dependencies:" -ForegroundColor White
    Write-Host "     pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  2. Run the system:" -ForegroundColor White
    Write-Host "     python main.py analyze" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "============================================================================" -ForegroundColor Red
    Write-Host "  FAILED - Some files were not created" -ForegroundColor Red
    Write-Host "============================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    exit 1
}

# Test Python import
Write-Host "Testing Python imports..." -ForegroundColor Yellow
Write-Host ""

python -c @"
import sys
import os

try:
    sys.path.insert(0, '.')

    # Test imports
    from roro_monitor.data import DataFetcher, DataCache
    print('  [OK] Successfully imported DataFetcher and DataCache')

    from roro_monitor.config import settings
    print('  [OK] Successfully imported settings')

    print('')
    print('='*76)
    print('  ALL IMPORTS SUCCESSFUL - System is ready!')
    print('='*76)

except ImportError as e:
    print(f'  [FAIL] Import error: {e}')
    print('')
    print('Make sure to install dependencies first:')
    print('  pip install -r requirements.txt')
    sys.exit(1)
"@

Write-Host ""
