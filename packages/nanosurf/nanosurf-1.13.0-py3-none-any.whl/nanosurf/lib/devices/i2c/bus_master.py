
"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""


import enum
from typing import Union
import platform

from nanosurf.lib.devices.i2c.bus_access import _I2CBusID, I2COffsetMode, I2CBusSpeed, I2CInstances, I2CMasterType, I2CBusAccess


if platform.system() == "Windows":
    from nanosurf.lib.devices.i2c.windows_bus_access import SPMBusAccess, StudioBusAccess, I2CBusID

elif platform.system() == "Linux":
    from nanosurf.lib.devices.i2c.linux_bus_access import LinuxBusAccess, I2CBusID



class I2CBusMaster():
        
    _active_chip_ref = int(0)
    _next_chip_ref = 1

    def __init__(self, spm_root:"Union[Studio, Spm]", bus_id: _I2CBusID, instance_id: I2CInstances = I2CInstances.CONTROLLER, master_type: I2CMasterType = I2CMasterType.AUTO_DETECT, bus_speed: I2CBusSpeed = I2CBusSpeed.kHz_400):
        self._spm_root = spm_root
        self._spm = None
        self._bus_access:I2CBusAccess = None
 
        if platform.system() == "Windows":
            self._spm = spm_root.spm
            if self._spm.is_studio:            
                self._bus_access = StudioBusAccess(self, bus_id, self._spm, instance_id, master_type)
            else:
                self._bus_access = SPMBusAccess(self, bus_id, spm_root, instance_id, master_type)
        elif platform.system() == "Linux":
            self._bus_access = LinuxBusAccess(self, bus_id)
        else:
            raise Exception("Unknown platform")

        self._metadata = None
        self.assign_i2c_bus(bus_id,bus_speed)

    def assign_i2c_bus(self,  bus_id: _I2CBusID, bus_speed: I2CBusSpeed):
        self._bus_id = bus_id
        self._bus_speed = bus_speed
        self._bus_access.update_bus_parameter(self._bus_id, self._bus_speed )

    def assign_chip(self, chip: 'I2CChip'):
        chip.setup_bus_connection(self, self.create_unique_chip_id())

    def setup_metadata(self, addr: int, offset_mode: I2COffsetMode, auto_lock: bool = True):
        self._metadata = self._bus_access.set_metadata(addr, offset_mode, auto_lock)

    def check_connection(self, chip: 'I2CChip') -> bool:
        self.activate_chip(chip)
        is_connected = self._bus_access.is_connected(self._metadata)
        return is_connected

    @classmethod
    def get_active_chip_id(cls) -> int:
        return I2CBusMaster._active_chip_ref

    @classmethod
    def create_unique_chip_id(cls) -> int:
        I2CBusMaster._next_chip_ref += 1
        return I2CBusMaster._next_chip_ref

    def activate_chip(self, chip: 'I2CChip'):
        if chip.get_chip_ref() != I2CBusMaster._active_chip_ref:
            chip.activate()
            I2CBusMaster._active_chip_ref = chip.get_chip_ref()

    def write_bytes(self, offset: int, data: list[int]) -> bool:
        done = False
        try:
            done = self._bus_access.write(self._metadata, offset, data) == 0
        except Exception as e:
            print(f"write_bytes() exception: {e}")
        return done

    def read_bytes(self, offset:int, data_count:int) -> list[int]:
        data: list[int] = []
        try:
            data: list[int] = list(self._bus_access.read(self._metadata, offset, data_count)) 
        except Exception as e:
            print(f"read_bytes() exception: {e}")
        return data

class I2CChip():

    def __init__(self, bus_addr: int, offset_mode: I2COffsetMode, name: str = "", bus_master: I2CBusMaster = None, auto_lock: bool = True):
        """ Minimal initialization is bus_addr and offset_mode. connection to bus master can be done later by bus_master.assign_chip() """
        self._bus_master = bus_master
        self._chip_ref = -1
        self.name = name
        self.bus_address = bus_addr
        self.offset_mode = offset_mode
        self.auto_lock = auto_lock
        if self._bus_master is not None:
            self._bus_master.assign_chip(self)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name:str):
        self.__name = name

    @property
    def bus_address(self) -> int:
        return self.__bus_addr

    @bus_address.setter
    def bus_address(self, addr: int):
        self.__bus_addr = addr

    @property
    def offset_mode(self) -> I2COffsetMode:
        return self.__offset_mode

    @offset_mode.setter
    def offset_mode(self, mode: I2COffsetMode):
        self.__offset_mode = mode

    @property
    def auto_lock(self) -> bool:
        return self.__auto_lock

    @auto_lock.setter
    def auto_lock(self, lock:bool):
        self.__auto_lock = lock

    def setup_bus_connection(self, bus_master: I2CBusMaster, chip_ref: int):
        self._bus_master = bus_master
        self._chip_ref = chip_ref

    def activate(self):
        self._bus_master.setup_metadata(self.bus_address, self.offset_mode, self.auto_lock)

    def get_chip_ref(self) -> int:
        return self._chip_ref

    def get_bus(self):
        self._bus_master.activate_chip(self)

    def is_connected(self) -> bool:
        return self._bus_master.check_connection(self)

    def write_bytes_with_offset(self, offset: int, data: list[int]) -> bool:
        self.get_bus()
        done = self._bus_master.write_bytes(offset, data)
        return done

    def write_byte_with_offset(self, offset:int, data:int) -> bool:
        return self.write_bytes_with_offset(offset, [data])

    def write_bytes(self, data: list[int]) -> bool:
        return self.write_bytes_with_offset(0, data)

    def write_byte(self, data: int) -> bool:
        return self.write_bytes_with_offset(0, [data])

    def read_bytes_with_offset(self, offset:int, count: int) -> list[int]:
        self.get_bus()
        data = self._bus_master.read_bytes(offset, count)
        return data

    def read_byte_with_offset(self, offset: int) -> int:
        data = self.read_bytes_with_offset(offset, count=1)
        return data[0]

    def read_bytes(self, count: int) -> list[int]:
        data = self.read_bytes_with_offset(0, count)
        return data

    def read_byte(self) -> int:
        data = self.read_bytes_with_offset(0, count=1)
        return data[0]

