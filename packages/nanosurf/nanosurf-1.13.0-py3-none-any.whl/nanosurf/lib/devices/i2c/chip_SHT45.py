"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import struct
import time
import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_SHT4x(i2c.I2CChip): 
    """ temperature and humidity sensor chip from Sensirion."""

    class MeasureMode(enum.IntEnum):
        With_Heating = 0
        Without_Heating = 1

    class HeatingPower(enum.IntEnum):
        Power_200mW_1s = 0                      
        Power_200mW_100ms = 1                      
        Power_110mW_1s = 2                      
        Power_110mW_100ms = 3                      
        Power_20mW_1s = 4                      
        Power_20mW_100ms = 5                      

    class Register(enum.IntEnum):
        HighPrecision_NoHeating = 0xfd
        MediumPrecision_NoHeating = 0xf6
        LowPrecision_NoHeating = 0xe0
        Device_Serial_ID = 0x89
        Soft_Reset = 0x94
        HighPrecision_Heating_200mW_1s = 0x39
        HighPrecision_Heating_200mW_100ms = 0x32
        HighPrecision_Heating_110mW_1s = 0x2f
        HighPrecision_Heating_110mW_100ms = 0x24
        HighPrecision_Heating_20mW_1s = 0x1e
        HighPrecision_Heating_20mW_100ms = 0x15

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, offset_mode=i2c.I2COffsetMode.NoOffset,**kwargs)
        self._map_heating_mode_to_reg = {
            Chip_SHT4x.HeatingPower.Power_200mW_1s:    Chip_SHT4x.Register.HighPrecision_Heating_200mW_1s,
            Chip_SHT4x.HeatingPower.Power_200mW_100ms: Chip_SHT4x.Register.HighPrecision_Heating_200mW_100ms,
            Chip_SHT4x.HeatingPower.Power_110mW_1s:    Chip_SHT4x.Register.HighPrecision_Heating_110mW_1s,
            Chip_SHT4x.HeatingPower.Power_110mW_100ms: Chip_SHT4x.Register.HighPrecision_Heating_110mW_100ms,
            Chip_SHT4x.HeatingPower.Power_20mW_1s:     Chip_SHT4x.Register.HighPrecision_Heating_20mW_1s,
            Chip_SHT4x.HeatingPower.Power_20mW_100ms:  Chip_SHT4x.Register.HighPrecision_Heating_20mW_100ms
        }
        self._map_heating_mode_to_delay = {
            Chip_SHT4x.HeatingPower.Power_200mW_1s:    1.0,
            Chip_SHT4x.HeatingPower.Power_200mW_100ms: 0.2,
            Chip_SHT4x.HeatingPower.Power_110mW_1s:    1.0,
            Chip_SHT4x.HeatingPower.Power_110mW_100ms: 0.2,
            Chip_SHT4x.HeatingPower.Power_20mW_1s:     1.0,
            Chip_SHT4x.HeatingPower.Power_20mW_100ms:  0.2
        }
        self._measure_mode = Chip_SHT4x.MeasureMode.Without_Heating
        self._heating_power = Chip_SHT4x.HeatingPower.Power_110mW_100ms

    def is_connected(self) -> bool:
        _ = super().is_connected() # used only to connect to right bus
        # chip needs always a write command for correct responding
        return self.write_byte(self.Register.Soft_Reset)
    
    def get_measure_mode(self) -> MeasureMode:
        return self._measure_mode
    
    def set_measure_mode(self, mode:MeasureMode):
        self._measure_mode = mode
    
    def get_heating_power(self) -> HeatingPower:
        return self._heating_power
    
    def set_heating_power(self, power:HeatingPower):
        self._heating_power = power
    
    def reset(self):
        self.write_byte(self.Register.Soft_Reset)
        time.sleep(0.2)

    def read_temp_and_humidity(self) -> tuple[float, float]:
        if self.get_measure_mode() == Chip_SHT4x.MeasureMode.With_Heating:
            command_reg = self._map_heating_mode_to_reg[self.get_heating_power()]
            measure_time = self._map_heating_mode_to_delay[self.get_heating_power()]
        else:
            command_reg = Chip_SHT4x.Register.HighPrecision_NoHeating
            measure_time = 0.1

        self.write_byte(command_reg)
        time.sleep(measure_time)

        result_buffer = bytearray(self.read_bytes(6))
        temp_raw, temp_crc, humidity_raw, humidity_crc = struct.unpack(">HbHb", result_buffer)
        
        temp = temp_raw/65535.0*175.0 - 45.0
        temp = min(max(-40.0,temp),125.0)
        
        humidity = humidity_raw/65535.0*125.0 - 6
        humidity = min(max(0.0,humidity),100.0)
        
        return (temp, humidity)
    
    def read_serial_number(self) ->int:
        self.write_byte(Chip_SHT4x.Register.Device_Serial_ID)
        time.sleep(0.5)
        result_buffer = bytearray(self.read_bytes(6))
        hi_word, hi_crc, low_world, low_crc = struct.unpack(">HbHb", result_buffer)
        return hi_word*65536 + low_world


