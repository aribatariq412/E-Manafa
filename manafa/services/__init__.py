"""Services module for E-MANAFA.

This module contains services for profiling Android applications,
including Perfetto-based power profiling with support for both
legacy devices and newer devices with power.rails.* data sources.
"""

from .perfettoService import PerfettoService, device_has_perfetto
from .perfettoServiceEnhanced import PerfettoServiceEnhanced, device_supports_power_rails
from .perfettoServiceFactory import create_perfetto_service

__all__ = [
    'PerfettoService',
    'PerfettoServiceEnhanced', 
    'create_perfetto_service',
    'device_has_perfetto',
    'device_supports_power_rails'
]
