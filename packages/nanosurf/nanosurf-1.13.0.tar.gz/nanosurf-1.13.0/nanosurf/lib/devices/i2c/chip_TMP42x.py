"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_TMP42X(i2c.I2CChip): 
    """ temperature sensor chip"""
    class Register(enum.IntEnum):
        LocalTempHiByte = 0x00
        RemoteTempHiByte1 = 0x01
        RemoteTempHiByte2 = 0x02
        RemoteTempHiByte3 = 0x03
        StatusReg = 0x08
        ConfigReg1 = 0x09
        ConfigReg2 = 0x0a
        ConversionRateReg = 0x0b
        OneShotStart = 0x0f
        LocalTempLowByte = 0x10
        RemoteTempLowByte1 = 0x11
        RemoteTempLowByte2 = 0x12
        RemoteTempLowByte3 = 0x13
        NCorrection1 = 0x21
        NCorrection2 = 0x22
        NCorrection3 = 0x23
        SoftReset = 0xfc
        ManufacturingID = 0xfe
        DeviceID = 0xff

    class ConversionRate(enum.IntEnum):
        Convert_every_16s = 0
        Convert_every_8s = 1
        Convert_every_4s = 2
        Convert_every_2s = 3
        Convert_1_per_sec = 4
        Convert_2_per_sec = 5
        Convert_4_per_sec = 6
        Convert_8_per_sec = 7

    class ConfigReg1(enum.IntEnum):
        ShutDown = 0x40
        TempRangeExtended = 0x04

    class ConfigReg2(enum.IntEnum):
        EnableSensor3 = 0x40
        EnableSensor2 = 0x20
        EnableSensor1 = 0x10
        EnableLocal   = 0x08
        EnableResistorCorrection = 0x04

    class StatusReg(enum.IntEnum):
        Busy = 0x80

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, offset_mode=i2c.I2COffsetMode.NoOffset,**kwargs)

    def start_measuring(self, rate: ConversionRate = ConversionRate.Convert_1_per_sec, active_sensors: ConfigReg2 = ConfigReg2.EnableLocal):
        self.ConversionRate = rate
        self.reg_config_reg2 = active_sensors
        self.reg_config_reg1 = 0x00

    @property
    def reg_config_reg1(self) -> int:
        self.write_byte(self.Register.ConfigReg1)
        return self.read_byte()

    @reg_config_reg1.setter
    def reg_config_reg1(self, val: ConfigReg1):
        self.write_bytes([self.Register.ConfigReg1, val])

    @property
    def reg_config_reg2(self) -> int:
        self.write_byte(self.Register.ConfigReg2)
        return self.read_byte()

    @reg_config_reg2.setter
    def reg_config_reg2(self, val: ConfigReg2):
        self.write_bytes([self.Register.ConfigReg2, val])

    @property
    def reg_conversion(self) -> int:
        self.write_byte(self.Register.ConversionRateReg)
        return self.read_byte()

    @reg_conversion.setter
    def reg_conversion(self, rate: ConversionRate):
        self.write_bytes([self.Register.ConversionRateReg, rate])

    @property
    def reg_local_temp_high(self) -> int:
        self.write_byte(self.Register.LocalTempHiByte)
        return self.read_byte()

    @property
    def reg_local_temp_low(self) -> int:
        self.write_byte(self.Register.LocalTempLowByte)
        return self.read_byte()
        
    @property
    def reg_status(self) -> int:
        self.write_byte(self.Register.StatusReg)
        return self.read_byte()

    @property
    def temperature(self) -> float:
        """ Get current chip temperature in degree. Read only"""
        temp =  float(self.reg_local_temp_high) + 0.0625 * int((self.reg_local_temp_low >> 4) & 0x0f)
        return temp 

    @property
    def is_busy(self) -> bool:
        return (self.reg_status & self.StatusReg.Busy) > 0

    

   