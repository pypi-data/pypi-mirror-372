import nanosurf as nsf
import nanosurf.lib.devices.accessory_interface.accessory_master as am

class GSSClimateSensor(am.AccessoryDevice):
    
    Assigned_BTNumber = "BT10224"
    
    def __init__(self, serial_no:str = ""):
        super().__init__(serial_no=serial_no, bt_number=self.Assigned_BTNumber)
        self.chip_sht = nsf.devices.i2c.Chip_SHT4x(bus_addr=0x44)
        self.chip_temp = nsf.devices.i2c.Chip_TMP119(bus_addr=0x48)
    
    def register_chips(self):
        self.assign_chip(self.chip_sht)
        self.assign_chip(self.chip_temp)
    
    def init_device(self):
        self.chip_sht.reset()
        self.chip_sht.set_heating_power(self.chip_sht.HeatingPower.Power_110mW_1s)
        self.chip_sht.set_measure_mode(self.chip_sht.MeasureMode.Without_Heating)

        self.chip_temp.reset()
        self.chip_temp.set_average_mode(self.chip_temp.AverageMode.Averages_8)
        self.chip_temp.set_conversion_cycle(self.chip_temp.ConversionCycle.ms_250)
        self.chip_temp.start_continuous_mode()
        
    def get_body_temperature(self) -> float:
        return self.chip_temp.read_temperature()
    
    def get_air_temperature(self) -> float:
        temp, _ = self.chip_sht.read_temp_and_humidity()
        return temp
    
    def get_air_humidity(self) -> float:
        _, humidity = self.chip_sht.read_temp_and_humidity()
        return humidity
    

    
    
    