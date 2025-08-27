""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import enum
from dataclasses import dataclass
import nanosurf as nsf

""" Available monitoring channels defined by the worker task"""
class AmplifierGainID(enum.IntEnum):
    Gain_500uA = 1
    Gain_5uA = 2
    Gain_50nA = 3

class Settings(nsf.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file 
        Could be connected also to GUI elements (e.g.: look into bind_gui_elements() in gui.py)
    """
    def __init__(self) -> None:
        super().__init__()
        self.gain_id = nsf.PropVal(int(AmplifierGainID.Gain_500uA))

@dataclass
class WorkerResults():
    """ This class saves the worker module result (e.g.: be read by gui elements like NSFChart or saved to file) """
    pass