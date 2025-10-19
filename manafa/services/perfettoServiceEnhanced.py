from __future__ import absolute_import

import re
from .perfettoService import PerfettoService, device_has_perfetto
import os
from manafa.utils.Utils import execute_shell_command, get_resources_dir
from ..utils.Logger import log, LogSeverity

RESOURCES_DIR = get_resources_dir()

DEFAULT_OUT_DIR = "/data/misc/perfetto-traces"
CONFIG_FILE_ENHANCED = "perfetto_config_power_rails.pbtxt"


def device_supports_power_rails():
    """Check if device supports power.rails.* data sources.
    
    Returns:
        bool: True if device supports power rails, False otherwise.
    """
    # Check if power rails are available
    cmd = "adb shell perfetto --query-raw | grep -i 'power.rails'"
    res, output, _ = execute_shell_command(cmd)
    
    if res == 0 and 'power.rails' in output:
        log("Device supports power.rails.* data sources", log_sev=LogSeverity.INFO)
        return True
    
    log("Device does not support power.rails.* data sources, falling back to legacy profiler", 
        log_sev=LogSeverity.WARNING)
    return False


class PerfettoServiceEnhanced(PerfettoService):
    """Enhanced Perfetto service that uses power.rails.* data sources.
    
    This class extends PerfettoService to use the newer power.rails.* data sources
    available on modern Android devices (Android 10+, Pixel 4+, etc.).
    
    The enhanced profiler provides more accurate and granular power consumption data
    by directly accessing hardware power rails instead of relying on battery counters.
    
    Attributes:
        Inherits all attributes from PerfettoService
        cfg_file (str): Uses perfetto_config_power_rails.pbtxt
    """
    
    def __init__(self, boot_time=0, output_res_folder="perfetto_enhanced", 
                 default_out_dir=DEFAULT_OUT_DIR, cfg_file=CONFIG_FILE_ENHANCED):
        """Initialize enhanced Perfetto service.
        
        Args:
            boot_time (float): Timestamp of device's last boot
            output_res_folder (str): Folder where logs will be stored
            default_out_dir (str): Device default results directory
            cfg_file (str): Perfetto config file (defaults to enhanced config)
        """
        # Check if device supports power rails
        if not device_supports_power_rails():
            log("Falling back to standard PerfettoService", log_sev=LogSeverity.WARNING)
            # Fall back to parent class config
            cfg_file = "perfetto.config.bin"
        
        # Initialize parent class
        super().__init__(boot_time=boot_time, 
                        output_res_folder=output_res_folder,
                        default_out_dir=default_out_dir,
                        cfg_file=cfg_file)
        
        log(f"Initialized PerfettoServiceEnhanced with config: {self.cfg_file}", 
            log_sev=LogSeverity.INFO)
    
    def start(self):
        """Start profiling session with enhanced config.
        
        Uses text-based protobuf config (.pbtxt) with --txt flag for power rails.
        """
        config_path = os.path.join(RESOURCES_DIR, self.cfg_file)
        
        # Use --txt flag for .pbtxt configs, otherwise use -c flag
        if self.cfg_file.endswith('.pbtxt'):
            cmd = f"cat {config_path} | adb shell perfetto " \
                  f"{self.get_switch('background', '-b')} --txt " \
                  f"-o {self.output_filename} -c -"
        else:
            # Fall back to binary config
            cmd = f"cat {config_path} | adb shell perfetto " \
                  f"{self.get_switch('background', '-b')} " \
                  f"-o {self.output_filename} {self.get_switch('config', '-c')} -"
        
        log(f"Starting enhanced perfetto: {cmd}", log_sev=LogSeverity.INFO)
        res, o, e = execute_shell_command(cmd=cmd)
        
        if res != 0 or e.strip() != "":
            log(f"Error starting perfetto: {e}", log_sev=LogSeverity.ERROR)
            return False
        
        return True
