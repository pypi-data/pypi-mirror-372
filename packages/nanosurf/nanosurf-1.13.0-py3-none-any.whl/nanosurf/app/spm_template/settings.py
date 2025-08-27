""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import enum
import pathlib
import os
import nanosurf as nsf

""" Available monitoring channels defined by the worker task"""
class MonitorChannelID(enum.IntEnum):
    User1Input = 0,
    Deflection = 1,
    ZAxisOut = 2


class Settings(nsf.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file 
        Could be connected also to GUI elements (e.g.: look into bind_gui_elements() in gui.py)
    """
    def __init__(self) -> None:
        super().__init__()
        self.repetitions = nsf.PropVal(int(200))
        self.time_per_repetition = nsf.PropVal(nsf.SciVal(0.1, "s"))
        self.channel_id = nsf.PropVal(int(MonitorChannelID.Deflection))
        self.save_path = nsf.PropVal(pathlib.Path(os.getenv(r"UserProfile")) / "Desktop")
        self.continuous_rolling = nsf.PropVal(bool(True))
        self.auto_y_range = nsf.PropVal(bool(True))

class ModuleResults:
    """ This class saves the worker module result (e.g.: be read by gui elements like NSFChart or saved to file) """
    def __init__(self) -> None:
        self.data_stream = nsf.SciStream()
        self.mean_value = nsf.SciVal()
        self.last_value = nsf.SciVal()
        self.last_index : int = -1
