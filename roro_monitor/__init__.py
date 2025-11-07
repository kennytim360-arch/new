"""
Institutional Risk-On/Risk-Off Monitor

A comprehensive, multi-dimensional market regime analysis system.
"""

__version__ = '1.0.0'
__author__ = 'RO/RO Monitor Team'

from .config import settings, AssetUniverse
from .data import DataFetcher
from .engine import RegimeEngine, PositioningEngine
from .dashboard import create_dashboard, run_dashboard
from .backtest import BacktestEngine

__all__ = [
    'settings',
    'AssetUniverse',
    'DataFetcher',
    'RegimeEngine',
    'PositioningEngine',
    'create_dashboard',
    'run_dashboard',
    'BacktestEngine',
]
