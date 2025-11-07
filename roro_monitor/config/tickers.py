"""
Asset universe definitions for the RO/RO Monitor.
Based on the strategic blueprint's data architecture.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AssetClass:
    """Represents a category of assets with specific tickers."""
    name: str
    tickers: List[str]
    purpose: str


class AssetUniverse:
    """
    Complete asset universe for institutional RO/RO analysis.
    Tier-1 data sources for institutional quality.
    """

    # Equities - Risk Assets
    EQUITIES_RISK = AssetClass(
        name="Equities (Risk)",
        tickers=["SPY", "QQQ", "IWM", "EEM"],
        purpose="Core Risk Assets"
    )

    # Equities - Safety/Defensive
    EQUITIES_SAFETY = AssetClass(
        name="Equities (Safety)",
        tickers=["XLU", "XLP"],  # Removed VDEF (delisted)
        purpose="Defensive Hedges"
    )

    # Government Bonds
    GOVERNMENT_BONDS = AssetClass(
        name="Government Bonds",
        tickers=["IEF", "TLT"],
        purpose="Core Safety Assets"
    )

    # Credit
    CREDIT = AssetClass(
        name="Credit",
        tickers=["HYG", "LQD"],
        purpose="Credit Stress & Spreads"
    )

    # Volatility
    VOLATILITY = AssetClass(
        name="Volatility",
        tickers=["^VIX"],
        purpose="Fear & Market Stress"
    )

    # Commodities
    COMMODITIES = AssetClass(
        name="Commodities",
        tickers=["GLD", "USO"],
        purpose="Inflation/Fear & Growth"
    )

    # Currencies
    CURRENCIES = AssetClass(
        name="Currencies",
        tickers=["USDJPY=X", "AUDJPY=X"],
        purpose="Carry Trade Unwind"
    )

    # Sector ETFs for rotation analysis
    SECTORS = AssetClass(
        name="Sectors",
        tickers=[
            "XLY",  # Consumer Discretionary
            "XLF",  # Financials
            "XLI",  # Industrials
            "XLE",  # Energy
            "XLV",  # Healthcare
            "XLK",  # Technology
            "XLB",  # Materials
            "XLRE", # Real Estate
            "XLC",  # Communication Services
        ],
        purpose="Sector Rotation Analysis"
    )

    @classmethod
    def get_all_tickers(cls) -> List[str]:
        """Get all unique tickers across all asset classes."""
        all_tickers = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, AssetClass):
                all_tickers.extend(attr.tickers)
        return list(set(all_tickers))

    @classmethod
    def get_risk_assets(cls) -> List[str]:
        """Get tickers classified as risk assets."""
        return cls.EQUITIES_RISK.tickers

    @classmethod
    def get_safe_haven_assets(cls) -> List[str]:
        """Get tickers classified as safe-haven assets."""
        return (cls.EQUITIES_SAFETY.tickers +
                cls.GOVERNMENT_BONDS.tickers +
                ["GLD"])  # Gold is a safe haven

    @classmethod
    def get_cyclical_sectors(cls) -> List[str]:
        """Get cyclical sector tickers."""
        return ["XLY", "XLF", "XLI", "XLE", "XLB", "XLK"]

    @classmethod
    def get_defensive_sectors(cls) -> List[str]:
        """Get defensive sector tickers."""
        return ["XLU", "XLP", "XLV"]

    @classmethod
    def get_asset_class_map(cls) -> Dict[str, str]:
        """Create a mapping of ticker to asset class name."""
        asset_map = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, AssetClass):
                for ticker in attr.tickers:
                    asset_map[ticker] = attr.name
        return asset_map
