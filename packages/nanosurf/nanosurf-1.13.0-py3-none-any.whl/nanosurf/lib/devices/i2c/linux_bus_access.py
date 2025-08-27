# nanosurf linux I2C bus access driver
import enum
import enum
from typing import Any
import smbus3 as smbus
from nanosurf.lib.devices.i2c.bus_access import I2CBusAccess, I2COffsetMode, I2CMetaData, I2CBusSpeed

  
class I2CBusID(enum.IntEnum):
    Unassigned = -1
    Bus_0      = 10
    Bus_1      = 1
    Bus_3	   = 3

class LinuxBusAccess(I2CBusAccess):
    
    def __init__(self, parent, bus_id:I2CBusID):
        super().__init__(parent, bus_id)
        self._bus_speed = I2CBusSpeed.kHz_Default   
        self._smbus = smbus.SMBus(self._bus_id.value)
        
    def set_metadata(self, addr: int, offset_mode: I2COffsetMode, auto_lock: bool = True) -> Any:
        self._metadata = I2CMetaData(self._bus_id, addr, offset_mode, auto_lock=auto_lock, max_speed= I2CBusSpeed.kHz_Default)
        self._metadata.max_length_rx = 32
        self._metadata.max_length_tx = 32
        return self._metadata

    def update_bus_parameter(self,  bus_id: I2CBusID, bus_speed: I2CBusSpeed):    
        self._bus_id = bus_id
        self._bus_speed = bus_speed
        
    def is_connected(self, metadata:I2CMetaData) -> bool:
        found = False
        try:
            _ = self._smbus.i2c_rd(metadata.chip_addr,1)
            found = True
        except IOError as e:
            pass
        return found
    
    def write(self, metadata:I2CMetaData, offset:int, data:list[int]) -> int:
        try:
            if metadata.offset_mode == I2COffsetMode.NoOffset.value:
                _ = self._smbus.i2c_wr(metadata.chip_addr, data)
            elif metadata.offset_mode == I2COffsetMode.U8Bit.value:
                wr_msg = smbus.i2c_msg.write(metadata.chip_addr, [offset]+data)
                self._smbus.i2c_rdwr(wr_msg)
            elif metadata.offset_mode == I2COffsetMode.U16Bit_MSBFiRST.value:
                hibyte = offset>>8
                lobyte = offset & 0x00ff
                wr_msg = smbus.i2c_msg.write(metadata.chip_addr, [hibyte, lobyte]+data)
                self._smbus.i2c_rdwr(wr_msg)
            elif metadata.offset_mode == I2COffsetMode.U16Bit_LSBFiRST.value:
                hibyte = offset>>8
                lobyte = offset & 0x00ff
                wr_msg = smbus.i2c_msg.write(metadata.chip_addr, [lobyte, hibyte]+data)
                self._smbus.i2c_rdwr(wr_msg)
            else:
                print(f"Unknown {metadata.offset_mode=}")
                return -1
            return 0
        except IOError:
            return -1
    
    def read(self, metadata:I2CMetaData, offset:int, data_count:int) -> list[int]:
        try:
            if metadata.offset_mode == I2COffsetMode.NoOffset.value:
                rd_msg = self._smbus.i2c_rd(metadata.chip_addr,data_count)
            elif metadata.offset_mode == I2COffsetMode.U8Bit.value:
                wr_msg = smbus.i2c_msg.write(metadata.chip_addr, [offset])
                rd_msg = smbus.i2c_msg.read(metadata.chip_addr, data_count)
                self._smbus.i2c_rdwr(wr_msg, rd_msg)
            elif metadata.offset_mode == I2COffsetMode.U16Bit_MSBFiRST.value:
                hibyte = offset>>8
                lobyte = offset & 0x00ff
                wr_msg = smbus.i2c_msg.write(metadata.chip_addr, [hibyte, lobyte])
                rd_msg = smbus.i2c_msg.read(metadata.chip_addr, data_count)
                self._smbus.i2c_rdwr(wr_msg, rd_msg)
            elif metadata.offset_mode == I2COffsetMode.U16Bit_LSBFiRST.value:
                hibyte = offset>>8
                lobyte = offset & 0x00ff
                wr_msg = smbus.i2c_msg.write(metadata.chip_addr, [lobyte, hibyte])
                rd_msg = smbus.i2c_msg.read(metadata.chip_addr, data_count)
                self._smbus.i2c_rdwr(wr_msg, rd_msg)
            else:
                print(f"Unknown {metadata.offset_mode=}")
            return list(rd_msg)
        except IOError:
            return []
