""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import enum
from dataclasses import dataclass
import nanosurf
import nanosurf.lib.datatypes.sci_val as sci_val
import nanosurf.lib.datatypes.prop_val as prop_val

class ScanSettings(prop_val.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file
        settings with a '_' as first char are not stored
    """
    def __init__(self) -> None:
        super().__init__()
        self.image_size = prop_val.PropVal(sci_val.SciVal(10e-6, "m"))
        self.time_per_line = prop_val.PropVal(sci_val.SciVal(0.2, "s"))
        self.points_per_line = prop_val.PropVal(int(256))
        self.channel_id = prop_val.PropVal(int(nanosurf.Spm.ScanChannel.Deflection_or_ZCtrlIn))
        self.show_backward = prop_val.PropVal(bool(True))
        self.show_power_spec = prop_val.PropVal(bool(True))
        self.show_compress_spec = prop_val.PropVal(bool(False))

class ScanResults():
    """ This class saves the worker task result (e.g be read by gui elements or saved to file """
    def __init__(self) -> None:
        self.current_scan_line_index = 0

""" Combo boxes show entries with IDs and the names in second list"""
class ChannelD(enum.IntEnum):
    Deflection = 0,
    Topography = 1,

