"""Factory for creating appropriate Perfetto service based on device capabilities."""

from .perfettoService import PerfettoService, device_has_perfetto
from .perfettoServiceEnhanced import PerfettoServiceEnhanced, device_supports_power_rails
from ..utils.Logger import log, LogSeverity


def create_perfetto_service(boot_time=0, output_res_folder="perfetto", 
                            force_enhanced=False, force_legacy=False):
    """Factory function to create appropriate Perfetto service.
    
    Automatically detects device capabilities and returns either:
    - PerfettoServiceEnhanced: For devices with power.rails.* support (newer devices)
    - PerfettoService: For older devices without power rails support
    
    Args:
        boot_time (float): Timestamp of device's last boot
        output_res_folder (str): Folder where logs will be stored
        force_enhanced (bool): Force use of enhanced service (for testing)
        force_legacy (bool): Force use of legacy service (for compatibility)
    
    Returns:
        PerfettoService or PerfettoServiceEnhanced: Appropriate service instance
    
    Raises:
        Exception: If Perfetto is not available on device
    """
    if not device_has_perfetto():
        raise Exception("Perfetto is not available on this device")
    
    # Handle forced modes
    if force_legacy:
        log("Forcing legacy PerfettoService", log_sev=LogSeverity.INFO)
        return PerfettoService(boot_time=boot_time, output_res_folder=output_res_folder)
    
    if force_enhanced:
        log("Forcing enhanced PerfettoServiceEnhanced", log_sev=LogSeverity.INFO)
        return PerfettoServiceEnhanced(boot_time=boot_time, output_res_folder=output_res_folder)
    
    # Auto-detect device capabilities
    if device_supports_power_rails():
        log("Using PerfettoServiceEnhanced (power rails supported)", log_sev=LogSeverity.INFO)
        return PerfettoServiceEnhanced(boot_time=boot_time, output_res_folder=output_res_folder)
    else:
        log("Using legacy PerfettoService (power rails not supported)", log_sev=LogSeverity.INFO)
        return PerfettoService(boot_time=boot_time, output_res_folder=output_res_folder)
