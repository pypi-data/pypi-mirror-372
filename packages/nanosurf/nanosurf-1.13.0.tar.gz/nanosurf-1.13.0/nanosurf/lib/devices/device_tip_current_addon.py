""" This device controls the TipCurrent Addon Module for the DriveAFM
Copyright Nanosurf AG 2023
License - MIT
"""
import enum
import nanosurf as nsf

class AmplifierGain(enum.Enum):
    Gain_10k = enum.auto()
    Gain_1Meg = enum.auto()
    Gain_100Meg = enum.auto()

class DriveAFM_Tip_Current_Addon():

    def __init__(self) -> None:
        self.connected = False
        self.chip_gpio : nsf.devices.i2c.Chip_PCA9534 = None
        self.current_gain = AmplifierGain.Gain_10k

    def connect(self, spm:nsf.Spm)-> bool:
        self.connected = False
        try:
            self.bus_master = nsf.devices.i2c.I2CBusMaster(spm, nsf.devices.i2c.I2CBusID.ScanHead)
            self.chip_gpio = nsf.devices.i2c.Chip_PCA9534(bus_addr=0x27)
            self.bus_master.assign_chip(self.chip_gpio)
            self.connected = self.chip_gpio.is_connected()
            if self.connected:
                self.setup()
        except:
            self.connected = False
        return self.connected
    
    def is_connected(self) -> bool:
        found = False
        if self.chip_gpio is not None:
            found = self.chip_gpio.is_connected()
        return found

    def setup(self):
        if self.connected:
            self.chip_gpio.reg_config   = 0x00
            self.chip_gpio.reg_polarity = 0x00
            self.chip_gpio.reg_output   = 0b10000000
            self.set_gain(AmplifierGain.Gain_10k)

    def set_gain(self, gaid_id:AmplifierGain):
        if self.connected:
            if gaid_id == AmplifierGain.Gain_10k:
                self.chip_gpio.reg_output = 0b10000101
            elif gaid_id == AmplifierGain.Gain_1Meg:
                self.chip_gpio.reg_output = 0b10000110
            elif gaid_id == AmplifierGain.Gain_100Meg:
                self.chip_gpio.reg_output = 0b10000000
            else:
                raise ValueError(f"Unknown gain setting selected: {gaid_id}")
            self.current_gain = gaid_id
    
    def get_gain(self) -> AmplifierGain:
        return self.current_gain