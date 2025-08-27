
"""
Device driver for DS2484 - A Single-Channel 1-Wire Master
Integrated 1-Wire Line Driver Facilitates Protocol Conversion Between I2C Host and 1-Wire Slave Network
MAnufacturer is AnalogDevices. For more detail see data sheet

Copyright (C) Nanosurf AG - All Rights Reserved (2024)
License - MIT
"""

import time
import enum

import nanosurf.lib.devices.i2c as i2c

class Chip_DS2484(i2c.I2CChip):
    """ Single Channel 1-Wire Master"""

    class Command(enum.IntEnum):
        Device_Reset = 0xF0
        Set_ReadPointer = 0xE1
        Set_DeviceConfig = 0xD2
        OneWire_Adjust = 0xC3
        OneWire_Reset= 0xB4
        OneWire_WriteBit = 0x87
        OneWire_WriteByte = 0xA5
        OneWire_ReadByte = 0x96
        OneWire_Triplet = 0x78         

    class Register(enum.IntEnum):
        Device_Config = 0xC3
        Status = 0xF0
        ReadData = 0xE1
        Port_Config = 0xB4

    class Conf_Bits(enum.IntEnum):
        APU = 0x01
        PDN = 0x02
        SPU = 0x04
        OneWS = 0x08

    class Status_Bits(enum.IntEnum):
        WB  = 0x01
        PPD = 0x02
        SD  = 0x04
        LL  = 0x08
        RST = 0x10
        SBR = 0x20
        TSB = 0x40
        DIR = 0x80

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, i2c.I2COffsetMode.NoOffset, **kwargs)
        self.write_timeout = 1.0

    def device_reset(self) -> int:
        self.write_byte(self.Command.Device_Reset)
        return self.read_byte()

    def read_register(self, reg_addr: int) -> int:
        self.write_bytes( [self.Command.Set_ReadPointer, reg_addr] )   
        return self.read_byte()
    
    def read_full_config(self) -> list[int]:
        self.config_list = []
        self.config_list.append(self.read_register(self.Register.Device_Config))
        self.config_list.append(self.read_register(self.Register.Status))
        self.config_list.append(self.read_register(self.Register.ReadData))
        self.config_list.append(self.read_register(self.Register.Port_Config))
        return self.config_list  

    def read_status_register(self) -> Status_Bits:
        """ read the status register of the bus. """ 
        return self.read_register(self.Register.Status)
     
    def write_device_config(self, config: Conf_Bits):
        lo_nibble = config & 0b00001111
        # inverted version of config hast to go into hi_nipple
        hi_nibble = (lo_nibble ^ 0b00001111) << 4 

        register_data = hi_nibble | lo_nibble
        self.write_bytes( [self.Command.Set_DeviceConfig, register_data] )
        _ = self.read_byte()

    def one_wire_reset(self) -> int:
        """ rests 1-wire bus and read back status register """
        self.write_byte(self.Command.OneWire_Reset)
        return self.read_byte()

    def one_wire_config(self, adjust_reg_data: int) -> int:
        """ configure 1-Wire bus timing and read back port configuration register """
        self.write_bytes( [self.Command.OneWire_Adjust, adjust_reg_data] )
        return self.read_byte()
    
    def one_wire_write_byte(self, data_byte: int) -> bool:
        """ write a byte to 1-wire bus. if succeeded returns True"""
        self.write_bytes( [self.Command.OneWire_WriteByte, data_byte] )
        status = self.read_byte()
        start_time = time.time()
        while (((status & self.Status_Bits.WB) != 0) and ((time.time() - start_time) < self.write_timeout)):
            time.sleep(0.1)
            status = self.read_byte()     
        return (status & self.Status_Bits.WB) == 0
    
    def one_wire_write_bytes(self, data: list[int]) -> bool:
        """ writes a series of bytes to 1-wire bus. If succeeded it returns True"""
        done = True
        for x in data:
            done =  self.one_wire_write_byte(x)
            if not done: 
                break
        return done
    
    def one_wire_read_bytes(self, bytes_to_read: int) -> list[int]:
        read_result:list[int] = []
        for x in range(bytes_to_read):
            self.write_byte(self.Command.OneWire_ReadByte)
            status = self.read_byte()
            start_time = time.time()
            while (((status & self.Status_Bits.WB) != 0) and ((time.time() - start_time) < self.write_timeout)):
                time.sleep(0.1)
                status = self.read_byte()  
            done = (status & self.Status_Bits.WB) == 0   
            if not done:
                raise TimeoutError("Timeout while reading on 1-wire bus.")
            read_result.append(self.read_register(self.Register.ReadData))
        return read_result

         