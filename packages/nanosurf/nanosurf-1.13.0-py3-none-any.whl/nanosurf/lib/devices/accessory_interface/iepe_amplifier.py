import nanosurf as nsf
import nanosurf.lib.devices.accessory_interface.accessory_master as am


class IEPEAmplifier(am.AccessoryDevice):
    
    Assigned_BTNumber = "BT10226"
        
    _adc_channel_input_diverder_factor = 11.0
    _adc_reference_voltage = 2.048
    _adc_binary_range = 4096.0
    _iepe_current_source_voltage_drop = 0.39
    _iepe_max_voltage_over_sensor = 18.0
    _iepe_min_voltage_over_sensor = 1.0
    
    def __init__(self, serial_no:str = ""):
        super().__init__(serial_no=serial_no, bt_number=self.Assigned_BTNumber)
        self.chip_adc = nsf.devices.i2c.Chip_MAX1161x(bus_addr=0x33)
    
    def register_chips(self):
        self.assign_chip(self.chip_adc)
    
    def init_device(self):
        self.chip_adc.init_device(ref_mode=self.chip_adc.Reference_Modes.Internal_Ref_out_always_on,
                                  external_clock=False,bipolar_inputs=False, single_end_inputs=True)
    
    def get_amplifier_voltage(self, channel:int) -> float:
        if channel < 1 and channel > 4:
            raise ValueError(f"channel out of range: {channel}")
        self.chip_adc.select_active_channel(channel-1)
        raw_adc_value = self.chip_adc.read_active_channel()
        channel_voltage = self._adc_channel_input_diverder_factor*self._adc_reference_voltage*raw_adc_value/self._adc_binary_range
        return channel_voltage - self._iepe_current_source_voltage_drop
    
    def is_sensor_short(self, channel:int) -> bool:
        sensor_voltage_drop = self.get_amplifier_voltage(channel)
        return sensor_voltage_drop < self._iepe_min_voltage_over_sensor
    
    def is_sensor_open(self, channel:int) -> bool:
        sensor_voltage_drop = self.get_amplifier_voltage(channel)
        return sensor_voltage_drop > self._iepe_max_voltage_over_sensor

    def is_sensor_connected(self, channel:int) -> bool:
        return not self.is_sensor_short(channel) and not self.is_sensor_open(channel)
    
    