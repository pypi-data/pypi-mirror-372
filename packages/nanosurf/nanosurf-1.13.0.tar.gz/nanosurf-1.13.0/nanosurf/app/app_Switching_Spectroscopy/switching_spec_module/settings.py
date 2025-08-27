""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import enum
import numpy as np
import pathlib
import nanosurf.lib.datatypes.sci_val as sci_val
import nanosurf.lib.datatypes.prop_val as prop_val

class OutputChannelID(enum.IntEnum):
    User1 = 0,
    User2 = 1,
    TipVoltage = 2


class SpecSettings(prop_val.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file
        settings with a '_' as first char are not stored
    """
    def __init__(self):
        self.output_id = prop_val.PropVal(int(OutputChannelID.User1))
        self.number_of_steps = prop_val.PropVal(int(20))
        self.time_delay_after_step = prop_val.PropVal(sci_val.SciVal(0.05, "s"))
        self.output_span = prop_val.PropVal(sci_val.SciVal(20.0, "V"))
        self.output_center = prop_val.PropVal(sci_val.SciVal(0.0, "V"))
        self.revers_ramp = prop_val.PropVal(bool(False))
        self.folder_name = prop_val.PropVal(pathlib.Path(""))
        self.file_name_mask = prop_val.PropVal(str("switching-spec-"))
        self.file_index = prop_val.PropVal(int(1))
        self.auto_save_data = prop_val.PropVal(bool(True))
        self.show_on_data_values = prop_val.PropVal(bool(False))

class SpecResults():
    """ This class saves the worker task result (e.g be read by gui elements or saved to file """
    def __init__(self):
        self.outputs : np.ndarray = np.array([], dtype=float)
        self.outputs_unit: str = ""
        self.amplitudes_on : np.ndarray = np.array([], dtype=float)
        self.amplitudes_off : np.ndarray = np.array([], dtype=float)
        self.amplitudes_unit: str = ""
        self.phases_on : np.ndarray = np.array([], dtype=float)
        self.phases_off : np.ndarray = np.array([], dtype=float)

