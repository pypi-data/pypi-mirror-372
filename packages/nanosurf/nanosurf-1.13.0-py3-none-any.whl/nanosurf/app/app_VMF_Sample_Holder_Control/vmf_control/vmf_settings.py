""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import nanosurf.lib.datatypes.prop_val as prop_val

class VMFSettings(prop_val.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file
        settings with a '_' as first char are not stored
    """
    def __init__(self) -> None:
        super().__init__()
        self.sample_holder_config = prop_val.PropVal(int(0))

class VMFResults():
    """ This class saves the worker task result (e.g be read by gui elements or saved to file """
    def __init__(self) -> None:
        self.number_of_data_points = 0
        self.last_data = 0.0
        self.mean_value = 0.0


