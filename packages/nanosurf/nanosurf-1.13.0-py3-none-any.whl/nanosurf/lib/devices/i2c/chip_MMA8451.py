
"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_MMA8451(i2c.I2CChip):
    """ Digital Accelerometer from NXP Semiconductor
    """
        
    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, i2c.I2COffsetMode.NoOffset, **kwargs)

