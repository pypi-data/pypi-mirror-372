""" Defines the configuration values of the module.
    Values in the ProStore are saved and loaded during application startup/shutdown automatically
Copyright Nanosurf AG 2021
License - MIT
"""

from datetime import datetime
import pathlib
import os

import nanosurf as nsf

class StartSettings(nsf.PropStore):
    def __init__(self) -> None:
        super().__init__()
        self.save_path = nsf.PropVal(pathlib.Path(str(os.getenv(r"UserProfile"))) / "Desktop")


