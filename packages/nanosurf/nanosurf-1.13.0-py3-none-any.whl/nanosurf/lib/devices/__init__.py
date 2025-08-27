"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import platform
if platform.system() == "Windows":
    from nanosurf.lib.devices.accessory_interface import AccessoryInterface
import nanosurf.lib.devices.i2c as i2c
