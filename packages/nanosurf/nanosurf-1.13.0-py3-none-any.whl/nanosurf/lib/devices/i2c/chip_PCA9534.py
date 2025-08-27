
"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""


import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_PCA9534(i2c.I2CChip):
    """ 8bit GPIO chip"""

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, i2c.I2COffsetMode.NoOffset, **kwargs)

    @property
    def reg_config(self):
        self.write_byte(0x03)
        return self.read_byte()

    @reg_config.setter
    def reg_config(self, config_mask: int):
        self.write_bytes([0x03, config_mask])

    @property
    def reg_output(self) -> int:
        self.write_byte(0x01)
        return self.read_byte()

    @reg_output.setter
    def reg_output(self, output_bits: int):
        self.write_bytes([0x01, output_bits])

    @property
    def reg_polarity(self):
        self.write_byte(0x02)
        return self.read_byte()

    @reg_polarity.setter
    def reg_polarity(self, bitmask: int):
        self.write_bytes([0x02, bitmask])

    @property
    def reg_input(self) -> int:
        self.write_byte(0x00)
        return self.read_byte()

