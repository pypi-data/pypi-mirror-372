""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import enum
from dataclasses import dataclass
import nanosurf as nsf

""" Available tip modes """
class TipMode(enum.IntEnum):
    Unknown = 0
    Open = 1
    Internal = 2
    External = 3

class Settings(nsf.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file 
    """
    def __init__(self) -> None:
        super().__init__()
        self.tip_mode = nsf.PropVal(int(TipMode.Unknown))

@dataclass
class WorkerResults():
    """ This class saves the worker module result (e.g.: be read by gui elements like NSFChart or saved to file) """
    pass