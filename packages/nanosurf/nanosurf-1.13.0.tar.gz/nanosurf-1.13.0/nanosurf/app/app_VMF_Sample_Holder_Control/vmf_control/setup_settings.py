""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

import nanosurf.lib.datatypes.prop_val as prop_val

class SetupSettings(prop_val.PropStore):
    """ settings defined here as PropVal are stored persistently in a ini-file
        settings with a '_' as first char are not stored
    """
    def __init__(self) -> None:
        super().__init__()
        self._controller_sn = prop_val.PropVal("-")
        self._sample_holder_sn = prop_val.PropVal("-")
        self._cal_names = ""
        self._cal_0_values:list[float] = []
        self._cal_1_values:list[float] = []
        self._cal_2_values:list[float] = []

