""" This device controls the TipAccess Addon Module for the DriveAFM
Copyright Nanosurf AG 2023
License - MIT
"""
import enum
import nanosurf as nsf

class TipConnection(enum.Enum):
    Open     = enum.auto()
    Internal = enum.auto()
    External = enum.auto()

class DriveAFM_Tip_Access_Addon():

    class _RelaysMask(enum.IntEnum):
        AllOff = 0x00
        Intern = 0x02
        Extern = 0x01

    def __init__(self) -> None:
        self.connected = False
        self.chip_gpio : nsf.devices.i2c.Chip_PCA9534 = None

    def connect(self, spm:nsf.Spm, do_initialize_chip: bool = True)-> bool:
        self.connected = False
        try:
            self.bus_master = nsf.devices.i2c.I2CBusMaster(spm, nsf.devices.i2c.I2CBusID.ScanHead)
            self.chip_gpio = nsf.devices.i2c.Chip_PCA9534(bus_addr=0x27)
            self.bus_master.assign_chip(self.chip_gpio)
            self.connected = self.chip_gpio.is_connected()
            if do_initialize_chip:
                self.setup()
        except Exception:
            self.connected = False
        return self.connected
    
    def is_connected(self) -> bool:
        return self.connected

    def setup(self):
        if self.connected:
            self.chip_gpio.reg_config   = 0x00
            self.chip_gpio.reg_polarity = 0x00
            self.chip_gpio.reg_output   = self._RelaysMask.AllOff
            self.set_tip_connection(TipConnection.Internal)
        else:
            raise IOError("Not connected.")
        
    def set_tip_connection(self, connection_id:TipConnection):
        if self.connected:
            if connection_id == TipConnection.Internal:
                self.chip_gpio.reg_output = self._RelaysMask.AllOff
                self.chip_gpio.reg_output = self._RelaysMask.Intern
            elif connection_id == TipConnection.External:
                self.chip_gpio.reg_output = self._RelaysMask.AllOff
                self.chip_gpio.reg_output = self._RelaysMask.Extern
            elif connection_id == TipConnection.Open:
                self.chip_gpio.reg_output = self._RelaysMask.AllOff
            else:
                raise ValueError(f"Unknown connection selected: {connection_id}")
        else:
            raise IOError("Not connected.")
        
    def get_tip_connection(self) -> TipConnection:
        if self.connected:
            relay_mask = self.chip_gpio.reg_output
            if (relay_mask & self._RelaysMask.Intern) & (relay_mask & self._RelaysMask.Extern):
                raise IOError(f"Illegal Relay state found. 0x{relay_mask:02x}")
            if relay_mask & self._RelaysMask.Intern:
                return TipConnection.Internal
            elif relay_mask & self._RelaysMask.Extern:
                return TipConnection.External
            else:
                return TipConnection.Open 
        else:
            raise IOError("Not connected.")