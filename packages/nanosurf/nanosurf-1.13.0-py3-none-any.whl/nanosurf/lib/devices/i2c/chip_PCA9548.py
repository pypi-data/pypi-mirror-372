
"""Copyright (C) Nanosurf AG - All Rights Reserved (2024)
License - MIT"""


import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_PCA9548(i2c.I2CChip):
    """ I2C-Bus switch chip"""

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, i2c.I2COffsetMode.NoOffset, **kwargs)

    @property
    def reg_control(self) -> int:
        return self.read_byte()

    @reg_control.setter
    def reg_control(self, control_mask: int):
        self.write_byte(control_mask)

