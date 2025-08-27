"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_TCN75(i2c.I2CChip): 
    """ temperature sensor chip"""
    class Resolution(enum.IntEnum):
        Bit9 = 0
        Bit10 = 1
        Bit11 = 2
        Bit12 = 3

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, offset_mode=i2c.I2COffsetMode.U8Bit,**kwargs)

    @property
    def reg_config(self) -> int:
        return self.read_byte_with_offset(0x01)

    @reg_config.setter
    def reg_config(self, config: int):
        self.write_byte_with_offset(0x01, config)

    @property
    def reg_temp(self) -> int:
        val = self.read_bytes_with_offset(0x00,2)
        return val[0]*256+val[1]

    @property
    def reg_hysteresis(self) -> int:
        val = self.read_bytes_with_offset(0x02,2)
        return val[0]*256+val[1]
        
    @reg_hysteresis.setter
    def reg_hysteresis(self, val: int):
        val = self.write_bytes_with_offset(0x02,[val/256, val%256])
        
    @property
    def reg_limit(self) -> int:
        val = self.read_bytes_with_offset(0x03,2)
        return val[0]*256+val[1]
        
    @reg_limit.setter
    def reg_hysteresis(self, val: int):
        val = self.write_bytes_with_offset(0x03,[val/256, val%256])
        
    @property
    def temperature(self) -> float:
        """ Get current chip temperature in degree. Read only"""
        temp = 1.0 / 256.0 * self.reg_temp
        return temp 

    @property
    def hysteresis(self) -> float:
        temp = 1.0 / 256.0 * self.reg_hysteresis
        return temp 

    @hysteresis.setter
    def hysteresis(self, val: float):
        self.reg_hysteresis = int(val * 256.0)

    @property
    def temp_limit(self) -> float:
        temp = 1.0 / 256.0 * self.reg_limit
        return temp 

    @temp_limit.setter
    def temp_limit(self, val: float):
        self.reg_limit = int(val * 256.0)

    @property
    def resolution(self) -> Resolution:
        """ Defines bit resolution of temp measurement. 
        From 9Bit -> 0.5deg up to 12Bit -> 0.0625deg"""
        resolution_bits = int((self.reg_config >> 5) & 0x03)
        if resolution_bits == 0:
            return self.Resolution.Bit9
        elif resolution_bits == 1:
              return self.Resolution.Bit10
        elif resolution_bits == 2:
              return self.Resolution.Bit11
        elif resolution_bits == 3:
              return self.Resolution.Bit12
        raise NotImplementedError
            
    @resolution.setter
    def resolution(self, res: Resolution):
        config_value = self.reg_config & ~(0x03 << 5)
        self.reg_config = config_value | (res << 5)
       
