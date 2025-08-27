""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import pathlib
import os
import nanosurf.lib.datatypes.sci_val as sci_val
import nanosurf.lib.datatypes.prop_val as prop_val

class AutoImageSettings(prop_val.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file
        settings with a '_' as first char are not stored
    """
    def __init__(self) -> None:
        super().__init__()
        self.auto_field_start = prop_val.PropVal(sci_val.SciVal(0, "T"))
        self.auto_field_stop = prop_val.PropVal(sci_val.SciVal(0.0, "T"))
        self.auto_field_steps = prop_val.PropVal(sci_val.SciVal(2, ""))
        self.auto_field_frame_rep = prop_val.PropVal(sci_val.SciVal(1, ""))
        self.save_to_path = prop_val.PropVal(pathlib.Path(str(os.getenv(r"UserProfile")))  / "Desktop" / "VMF_Data")
        self.data_file_mask = prop_val.PropVal(pathlib.Path(r'VMF_Image'))

class VMFResults():
    """ This class saves the worker task result (e.g be read by gui elements or saved to file """
    def __init__(self) -> None:
        self.number_of_data_points = 0
        self.last_data = 0.0
        self.mean_value = 0.0


