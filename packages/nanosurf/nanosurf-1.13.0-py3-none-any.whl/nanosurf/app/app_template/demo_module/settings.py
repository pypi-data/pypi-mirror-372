""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import enum
import nanosurf.lib.datatypes.sci_val as sci_val
import nanosurf.lib.datatypes.prop_val as prop_val

class DemoSettings(prop_val.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file
        settings with a '_' as first char are not stored
    """
    def __init__(self) -> None:
        super().__init__()
        self.repetitions = prop_val.PropVal(int(300))
        self.time_per_repetition = prop_val.PropVal(sci_val.SciVal(0.1, "s"))
        self.send_ticks = prop_val.PropVal(False)
        self.plot_func_id = prop_val.PropVal(int(0))
        self.this_is_not_stored = prop_val.PropVal(int(0))

class DemoResults():
    """ This class saves the worker task result (e.g be read by gui elements or saved to file """
    def __init__(self) -> None:
        self.number_of_data_points = 0
        self.last_data = 0.0
        self.mean_value = 0.0

""" Combo boxes show entries with IDs and the names in second list"""
class PlotStyleID(enum.IntEnum):
    PlotSin = 0,
    PlotCos = 1,
