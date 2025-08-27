import enum
from typing import Any

class _I2CBusID(enum.IntEnum):
    pass

class I2CInstances(enum.IntEnum):
    MAIN_APP = 0
    CONTROLLER = 1

class I2CMasterType(enum.IntEnum):
    AUTO_DETECT = -1
    EMBEDDED_AVALON = 0
    ACCESSORY_MASTER = 1
    EMBEDDED_LINUX = 2

class I2COffsetMode(enum.IntEnum):
    NoOffset = 0
    U8Bit = 1
    U16Bit_MSBFiRST = 2
    U16Bit_LSBFiRST = 3
    
class I2CBusSpeed(enum.IntEnum):
    kHz_Default = 0
    kHz_100 = 1
    kHz_200 = 2
    kHz_400 = 3

class I2CSyncing(enum.IntEnum):
    NoSync = 0
    Sync = 1
    
class I2CByteMode(enum.IntEnum):
    SingleByteOff = 0
    SingleByteOn = 1


class I2CMetaData():
        
    def __init__(self, bus_id:_I2CBusID, chip_addr:int, offset_mode:I2COffsetMode, auto_lock: bool, max_speed:I2CBusSpeed, sync:I2CSyncing=I2CSyncing.NoSync, byte_mode : I2CByteMode = I2CByteMode.SingleByteOff):
        self.bus_id = bus_id
        self.chip_addr = chip_addr
        self.offset_mode = offset_mode
        self.auto_lock = auto_lock
        self.bus_speed = max_speed
        self.max_length_rx = 50
        self.max_length_tx = 50
        self.sync = sync
        self.single_byte = byte_mode
        
    def __str__(self):
        return f"{self.bus_id=}\n{self.chip_addr=}\n{self.offset_mode=}\n"

    def __repr__(self):
        return self.__str__()
    

class I2CBusAccess():
    
    def __init__(self, parent, bus_id:_I2CBusID):
        self._bus_master = parent
        self._bus_id = bus_id
    
    def update_bus_parameter(self,  bus_id: _I2CBusID, bus_speed: I2CBusSpeed):    
        self._bus_id = bus_id
        self._bus_speed = bus_speed

    def set_metadata(self, addr: int, offset_mode: I2COffsetMode, auto_lock: bool = True) -> Any:
        raise NotImplementedError("This function has to be overwritten by subclass")
    
    def is_connected(self, metadata:I2CMetaData) -> bool:
        raise NotImplementedError("This function has to be overwritten by subclass")
        return False
    
    def write(self, metadata:I2CMetaData, offset:int, data:list[int]) -> int:
        raise NotImplementedError("This function has to be overwritten by subclass")
        return -1
    
    def read(self, metadata:I2CMetaData, offset:int, data_count:int) -> list[int]:
        raise NotImplementedError("This function has to be overwritten by subclass")
        return []