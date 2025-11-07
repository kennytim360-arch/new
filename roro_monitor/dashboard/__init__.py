"""Interactive dashboard package."""

from .app import create_dashboard
from .alerts import AlertSystem

__all__ = ['create_dashboard', 'AlertSystem']
