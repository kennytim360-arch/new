"""
Base class for all regime analysis pillars.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BasePillar(ABC):
    """
    Abstract base class for all pillars.
    Ensures consistent interface across all regime scoring components.
    """

    def __init__(self, name: str, weight: float):
        """
        Initialize pillar.

        Args:
            name: Pillar name
            weight: Weight in master score (0-1)
        """
        self.name = name
        self.weight = weight
        self.last_score = None
        self.last_details = None

    @abstractmethod
    def calculate_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """
        Calculate the pillar score from market data.

        Args:
            data: Dictionary of ticker -> DataFrame

        Returns:
            Score from 0-100
        """
        pass

    @abstractmethod
    def get_details(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of the score components.

        Returns:
            Dictionary with component scores and metrics
        """
        pass

    def get_weighted_score(self) -> float:
        """
        Get the weighted score for this pillar.

        Returns:
            Weighted score
        """
        if self.last_score is None:
            return 0.0
        return self.last_score * self.weight

    def get_status_message(self) -> str:
        """
        Get human-readable status message.

        Returns:
            Status description
        """
        if self.last_score is None:
            return "Not calculated"

        if self.last_score >= 70:
            return "BULLISH"
        elif self.last_score >= 55:
            return "Slightly Bullish"
        elif self.last_score >= 45:
            return "NEUTRAL"
        elif self.last_score >= 30:
            return "Slightly Bearish"
        else:
            return "BEARISH"

    def __repr__(self) -> str:
        return f"{self.name} (weight={self.weight:.1%}, score={self.last_score:.1f})"
