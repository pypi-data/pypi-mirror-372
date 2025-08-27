"""Copyright (C) Nanosurf AG - All Rights Reserved (2024)
License - MIT"""

from . import chip_AD7172 as ADC

class ADC_Module(ADC.Chip_AD7172): 
    """ An ADC module board based on the AD7172-2 and the I2C/SPI bridge SC18IS606
    """

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, **kwargs)
        self.differential = False

    def connect(self, ai, differential:bool = False)-> bool:
        ai.assign_chip(self)
        self.init_bridge()
        self.setup_analog_mode(differential)
        return self.is_connected()

    def setup_analog_mode(self, differential: bool):
        self.differential = differential
        if self.differential:
            self.setup_differential_mode()
        else:
            self.setup_single_end_mode()

    def active_channel(self, channel):
        self.setChannel = channel

    def set_sampling_speed(self, sampling_speed):
        self.write_register_bytes(self.ADC_Registers.FILTCON0, [0x0E, self.sampling_speed.x10sps])

    def read(self) -> float:
        if self.differential:
            voltage = (self.read_channel(self.setChannel)/1.25 * 10) # Conversion of the data into volts and recalculation of the 0V-2.5V signal into a ±10V signal
        else: 
            voltage = ((self.read_channel(self.setChannel)* 20) + 10) # Conversion of the data into volts and recalculation of the 0V-2.5V signal into a ±10V signal
        return voltage
    
    def read_multiple_channel(self, channel: int) -> float:
        if self.differential:
            voltage = (self.read_manual_channel(channel)/1.25 * 10) # Conversion of the data into volts and recalculation of the 0V-2.5V signal into a ±10V signal
        else: 
            voltage = ((self.read_manual_channel(channel)* 20) + 10) # Conversion of the data into volts and recalculation of the 0V-2.5V signal into a ±10V signal  
        return voltage
