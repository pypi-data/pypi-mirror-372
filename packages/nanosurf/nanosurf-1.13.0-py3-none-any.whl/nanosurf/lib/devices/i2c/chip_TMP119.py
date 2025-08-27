"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import struct
import time
from math import nan
import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_TMP119(i2c.I2CChip): 
    """ temperature sensor chip from Texas Instrument."""

    class ConversionMode(enum.IntEnum):
        Continuous     = 0b0000_0000_0000_0000
        Shutdown       = 0b0000_0100_0000_0000
        One_Shot       = 0b0000_1100_0000_0000

    class AverageMode(enum.IntEnum):
        Averages_No = 0b0000_0000_0000_0000
        Averages_8  = 0b0000_0000_0010_0000
        Averages_32 = 0b0000_0000_0100_0000
        Averages_64 = 0b0000_0000_0110_0000

    class ConversionCycle(enum.IntEnum):
        ms_015      = 0b0000_0000_0000_0000
        ms_125      = 0b0000_0000_1000_0000
        ms_250      = 0b0000_0001_0000_0000
        ms_500      = 0b0000_0001_1000_0000
        ms_1000     = 0b0000_0010_0000_0000
        ms_4000     = 0b0000_0010_1000_0000
        ms_8000     = 0b0000_0011_0000_0000
        ms_16000    = 0b0000_0011_1000_0000

    class _ConfigMask(enum.IntEnum):
        Soft_Reset      = 0b0_0000_0000_0000_0010
        AlertPinMode    = 0b0_0000_0000_0000_0100
        AlertPolarity   = 0b0_0000_0000_0000_1000
        AlertMode       = 0b0_0000_0000_0001_0000
        AveragingMode   = 0b0_0000_0000_0110_0000
        ConversionCycle = 0b0_0000_0011_1000_0000
        ConversionMode  = 0b0_0000_1100_0000_0000
        EEPROM_Busy     = 0b0_0001_0000_0000_0000
        Data_Ready      = 0b0_0010_0000_0000_0000
        Low_Alert       = 0b0_0100_0000_0000_0000
        High_Alert      = 0b0_1000_0000_0000_0000
        
    class _Register(enum.IntEnum):
        Temp_Result = 0x00
        Configuration = 0x01
        THigh_Limit = 0x02
        TLow_Limit = 0x03
        EEPROM_Unlock = 0x04
        EEPROM_1 = 0x05
        EEPROM_2 = 0x06
        Temp_Offset = 0x07
        EEPROM_3 = 0x08
        Device_ID = 0x0f

    _temp_bit_resolution = 0.0078125 # [deg/bit]
    _no_measurement_raw = -256.0 / _temp_bit_resolution
    
    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, offset_mode=i2c.I2COffsetMode.U8Bit,**kwargs)
        self._map_conversion_cycle_to_time = {
            self.ConversionCycle.ms_015  : 0.015,
            self.ConversionCycle.ms_125  : 0.125,
            self.ConversionCycle.ms_250  : 0.25,
            self.ConversionCycle.ms_500  : 0.5,
            self.ConversionCycle.ms_1000 : 1.0,
            self.ConversionCycle.ms_4000 : 4.0,
            self.ConversionCycle.ms_8000 : 8.0,
            self.ConversionCycle.ms_16000: 16.0,
        }
        self._map_averages_to_time = {
            self.AverageMode.Averages_No: 0.05,
            self.AverageMode.Averages_8 : 0.2,
            self.AverageMode.Averages_32: 0.6,
            self.AverageMode.Averages_64: 1.1,
        }
        self._conversion_mode = self.ConversionMode.Shutdown
        self._averaging_mode = self.AverageMode.Averages_8
        self._conversion_cycle = self.ConversionCycle.ms_500
        self._cycle_time = 0.0

    def reset(self):
        self._write_reg_word(self._Register.Configuration,self._ConfigMask.Soft_Reset)
        self.set_temp_offset(0.0)
        self.start_shutdown_mode()
    
    def start_continuous_mode(self):
        self._conversion_mode = self.ConversionMode.Continuous
        self._cycle_time = self.get_cycle_time()
        config_reg = self._conversion_mode | self._averaging_mode | self._conversion_cycle
        self._write_reg_word(self._Register.Configuration, config_reg)

    def start_one_shot_mode(self):
        self._conversion_mode = self.ConversionMode.One_Shot
        self._cycle_time = self.get_cycle_time()

    def start_shutdown_mode(self):
        self._conversion_mode = self.ConversionMode.Shutdown
        self._cycle_time = self.get_cycle_time()
        config_reg = self._conversion_mode | self._averaging_mode | self._conversion_cycle
        self._write_reg_word(self._Register.Configuration, config_reg)

    def get_conversion_mode(self) -> ConversionMode:
        return self._conversion_mode

    def read_temperature(self) -> float:
        mode = self.get_conversion_mode()
        if mode == self.ConversionMode.One_Shot:
            self._trigger_one_shot_measurement()
            time.sleep(self._cycle_time)
            if self._is_ready():
                temp_raw = self._read_reg_word(self._Register.Temp_Result)
            else:
                temp_raw = self._no_measurement_raw
        elif mode == self.ConversionMode.Continuous:
            if self._wait_for_data_ready(timeout=True):
                temp_raw = self._read_reg_word(self._Register.Temp_Result)
            else:
                temp_raw = self._no_measurement_raw
        elif mode == self.ConversionMode.Shutdown:
            temp_raw = self._no_measurement_raw
        else:
            raise ValueError(f"Unknown conversion mode '{mode}' detected.")

        if temp_raw == self._no_measurement_raw:
            temp_deg = nan
        else:
            temp_deg = temp_raw * self._temp_bit_resolution
        return temp_deg

    def set_conversion_cycle(self, cycle:ConversionCycle):
        self._conversion_cycle = cycle

    def get_conversion_cycle(self) -> ConversionCycle:
        return self._conversion_cycle

    def set_average_mode(self, avg_mode:AverageMode):
        self._averaging_mode = avg_mode

    def get_average_mode(self) -> AverageMode:
        return self._averaging_mode

    def set_temp_offset(self, offset:float):
        raw_offset = int(offset/self._temp_bit_resolution)
        self._write_reg_word(self._Register.Temp_Offset,raw_offset)
    
    def get_temp_offset(self) -> float:
        raw_offset = self._read_reg_word(self._Register.Temp_Offset)
        return raw_offset*self._temp_bit_resolution

    def get_cycle_time(self) -> float:
        mode = self.get_conversion_mode()
        if mode == self.ConversionMode.One_Shot:
            return self._map_averages_to_time[self.get_average_mode()]
        elif mode == self.ConversionMode.Continuous:
            return self._map_averages_to_time[self.get_average_mode()] + self._map_conversion_cycle_to_time[self.get_conversion_cycle()]
        else:
            return 0.0
    
    def _trigger_one_shot_measurement(self):
        self._conversion_mode = self.ConversionMode.One_Shot
        config_reg = self._conversion_mode | self._averaging_mode | self._conversion_cycle
        self._write_reg_word(self._Register.Configuration, config_reg)
        
    def _wait_for_data_ready(self, timeout:bool = False) -> bool:
        end_time = time.time() + 2.0*self._cycle_time
        while not self._is_ready():
            if timeout and (time.time() > end_time):
                return False
        return True
    
    def _is_ready(self) -> bool:
        config_reg = self._read_reg_word(self._Register.Configuration)
        return (config_reg & self._ConfigMask.Data_Ready) != 0

    def _write_reg_word(self, reg:_Register, val:int):
        byte_buffer = list(struct.pack(">h",val))
        self.write_bytes_with_offset(reg,byte_buffer)

    def _read_reg_word(self, reg:_Register) -> int:
        reg_val = bytearray(self.read_bytes_with_offset(reg,2))
        reg_unpack = struct.unpack(">h", reg_val)
        return reg_unpack[0]
