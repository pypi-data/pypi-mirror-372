import typing
import nanosurf as nsf
import nanosurf.lib.devices.accessory_interface.accessory_master as am
from nanosurf.lib.devices.i2c import chip_PCA9548
from nanosurf.lib.devices.i2c.config_eeprom import DataSerializer, ConfigEEPROM

class GSSSwitchIDEEPROM(am.GenericIDEEPROM):

    def __init__(self) -> None: 
        super().__init__(version=1)
        self.number_of_ports = 4   

    def serialize(self) -> bytearray:
        super().serialize()
        self._serialize(self.number_of_ports, DataSerializer.Formats.Int8)
        return self._write_data_bytes

    def deserialize(self, data:bytearray) -> bool:
        if (ok:=super().deserialize(data)):
            self.number_of_ports = typing.cast(int,self._deserialize(DataSerializer.Formats.Int8))
            ok = True
        return ok


class GSSSwitch(am.AccessoryDevice):

    Assigned_BTNumber = "BT10225"

    def __init__(self, serial_no:str = ""):
        super().__init__(serial_no=serial_no, bt_number=self.Assigned_BTNumber, config=GSSSwitchIDEEPROM())
        self.config:GSSSwitchIDEEPROM
        self._chip_mux = chip_PCA9548.Chip_PCA9548(0x71)
        
    def register_chips(self):
        self.assign_chip(self._chip_mux)
    
    def init_device(self):
        pass
    
    def get_number_of_ports(self) -> int:
        return self.config.number_of_ports
    