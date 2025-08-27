"""Copyright (C) Nanosurf AG - All Rights Reserved (2024)
License - MIT"""

import nanosurf.lib.devices.i2c as i2c
import nanosurf.lib.devices.i2c.chip_AD7172 as chip_AD7172


class ADC_Module_7172(chip_AD7172.Chip_AD7172): 
    """ An ADC module board based on the AD7172-2 and the I2C/SPI bridge SC18IS606
    """

    def __init__(self, bus_addr: int = 0x2c, **kwargs):
        super().__init__(bus_addr, **kwargs)
        self._bus = None
        self._connected = False
        self._active_input_channel = 0

    def connect(self, bus:i2c.I2CBusMaster)-> bool:
        self._bus = bus
        bus.assign_chip(self)
        self._connected = self.is_connected()
        if self._connected:
            self.init_chip(active_channel=0, differential_mode=False, sampling_seed=self.SamplingSpeed.Hz_49_68)
        return self._connected

    def read_active_channel_voltage(self) -> float:
        """ This function is used to read out the voltage of the active channel.

            Result
            ------
            voltage:float
                return the voltage according to chip setting. single_end 0..+5.0V, differential: +-2.5V
        """
        adc_ch_voltage = super().read_active_channel_voltage()
        if self._in_differential_mode:
            module_in_voltage = adc_ch_voltage * 8.0  # Conversion of the data into volts and recalculation of the +-2.5V signal into a ±20V signal
        else: 
            module_in_voltage = (adc_ch_voltage-1.25) * 8.0 # Conversion of the data into volts and recalculation of the 0V-2.5V signal into a ±10V signal  
        return module_in_voltage