"""Quick test to verify settings import fix."""

import sys
import importlib.util

# Load settings module directly without triggering full package imports
spec = importlib.util.spec_from_file_location(
    "settings",
    "roro_monitor/config/settings.py"
)
settings_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings_module)

# Get the settings instance
settings = settings_module.settings

# Verify attributes
print("✓ Settings module loaded successfully")
print(f"✓ DATA_CACHE_HOURS = {settings.DATA_CACHE_HOURS}")
print(f"✓ MA_SHORT = {settings.MA_SHORT}")
print(f"✓ MA_MEDIUM = {settings.MA_MEDIUM}")
print(f"✓ MA_LONG = {settings.MA_LONG}")
print(f"✓ PILLAR_WEIGHTS = {settings.PILLAR_WEIGHTS}")
print("\n✓✓✓ Settings instance is properly configured! ✓✓✓")
