"""
Pillar C: Macro-Fundamental Drivers (25% Weight)

Analyzes credit spreads, volatility term structure, and safe-haven flows.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

from .base import BasePillar
from ..indicators import MacroIndicators

logger = logging.getLogger(__name__)


class PillarC_MacroFundamentals(BasePillar):
    """
    Pillar C: Macro-Fundamental Drivers

    Components:
    1. Credit Spreads (HYG vs IEF) (40%)
    2. Volatility Term Structure (VIX) (35%)
    3. Safe-Haven Flows (TLT, GLD) (25%)
    """

    def __init__(self):
        super().__init__(name="Pillar C: Macro-Fundamental Drivers", weight=0.25)
        self.macro_indicators = MacroIndicators()
        self.components = {}

    def calculate_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate Pillar C score.

        Args:
            data: Dictionary of ticker -> DataFrame

        Returns:
            Score from 0-100
        """
        scores = []

        # 1. Credit Spreads (40%)
        credit_score = self._calculate_credit_score(data)
        if credit_score is not None:
            scores.append(('credit_spreads', credit_score, 0.40))

        # 2. Volatility Term Structure (35%)
        vix_score = self._calculate_vix_score(data)
        if vix_score is not None:
            scores.append(('vix_term_structure', vix_score, 0.35))

        # 3. Safe-Haven Flows (25%)
        safe_haven_score = self._calculate_safe_haven_score(data)
        if safe_haven_score is not None:
            scores.append(('safe_haven_flows', safe_haven_score, 0.25))

        if not scores:
            logger.error("No valid data for Pillar C calculation")
            self.last_score = 50.0
            return 50.0

        # Weighted combination
        final_score = sum(s * w for name, s, w in scores) / sum(w for _, _, w in scores)
        self.last_score = final_score

        # Store components
        self.components = {name: score for name, score, _ in scores}

        logger.info(f"Pillar C Score: {final_score:.1f}")
        return final_score

    def _calculate_credit_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate credit spread score."""
        required = ['HYG', 'LQD', 'IEF']

        if not all(ticker in data for ticker in required):
            logger.warning("Missing credit spread data")
            return None

        hyg_data = data['HYG']
        lqd_data = data['LQD']
        ief_data = data['IEF']

        if any(d.empty or len(d) < 63 for d in [hyg_data, lqd_data, ief_data]):
            return None

        # Calculate spread proxies using relative performance
        period = 21
        hyg_return = (hyg_data['close'].iloc[-1] / hyg_data['close'].iloc[-period] - 1) * 100
        ief_return = (ief_data['close'].iloc[-1] / ief_data['close'].iloc[-period] - 1) * 100

        hy_spread = hyg_return - ief_return

        # Check for widening (compare to longer period)
        period_long = 63
        hyg_return_long = (hyg_data['close'].iloc[-1] / hyg_data['close'].iloc[-period_long] - 1) * 100
        ief_return_long = (ief_data['close'].iloc[-1] / ief_data['close'].iloc[-period_long] - 1) * 100
        spread_widening = hy_spread < (hyg_return_long - ief_return_long)

        credit_spreads = {
            'hy_spread': hy_spread,
            'spread_widening': spread_widening
        }

        score = self.macro_indicators.credit_spread_score(credit_spreads)
        self.components['hy_spread'] = hy_spread
        self.components['spread_widening'] = spread_widening

        return score

    def _calculate_vix_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate VIX term structure score."""
        if '^VIX' not in data:
            logger.warning("Missing VIX data")
            return None

        vix_data = data['^VIX']

        if vix_data.empty or len(vix_data) < 63:
            return None

        # Calculate term structure proxy
        spot_vix = vix_data['close'].iloc[-1]
        avg_3m_vix = vix_data['close'].rolling(63).mean().iloc[-1]

        vix_term_structure = {
            'spot': spot_vix,
            '3m_avg': avg_3m_vix,
            'slope': avg_3m_vix - spot_vix,
            'backwardation': avg_3m_vix < spot_vix
        }

        score = self.macro_indicators.vix_term_structure_score(vix_term_structure)

        self.components['vix_spot'] = spot_vix
        self.components['vix_slope'] = vix_term_structure['slope']

        return score

    def _calculate_safe_haven_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate safe-haven flow score."""
        if 'TLT' not in data or 'GLD' not in data:
            logger.warning("Missing safe-haven data")
            return None

        tlt_data = data['TLT']
        gld_data = data['GLD']

        if tlt_data.empty or gld_data.empty or len(tlt_data) < 20:
            return None

        score = self.macro_indicators.safe_haven_flow_score(tlt_data, gld_data, period=20)

        # Store component data
        tlt_return = (tlt_data['close'].iloc[-1] / tlt_data['close'].iloc[-20] - 1) * 100
        gld_return = (gld_data['close'].iloc[-1] / gld_data['close'].iloc[-20] - 1) * 100

        self.components['tlt_return_20d'] = tlt_return
        self.components['gld_return_20d'] = gld_return

        return score

    def get_details(self) -> Dict[str, Any]:
        """Get detailed component breakdown."""
        return {
            'score': self.last_score,
            'components': self.components,
            'status': self.get_status_message(),
        }
