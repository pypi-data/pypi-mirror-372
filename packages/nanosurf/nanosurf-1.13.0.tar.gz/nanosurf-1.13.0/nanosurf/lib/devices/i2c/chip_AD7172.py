"""Copyright (C) Nanosurf AG - All Rights Reserved (2024)
License - MIT"""

import enum
import time
import struct
import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_AD7172(i2c.I2CChip): 
    """ AD7172-2 ADC Chip,
    connected to I2C by a I2C<->SPI bridge (SC18IS606)
    """

    class _SPI_Function_IDS(enum.IntEnum):
        slave_select_0  = 0x01
        slave_select_1  = 0x02
        slave_select_2  = 0x04
        slave_select_3  = 0x08
        slave_select_12 = 0x02 | 0x04
        slave_select_23 = 0x04 | 0x08
        config_spi      = 0xf0
        clear_int       = 0xf1
        idle_mode       = 0xf2
        gpio_write      = 0xf4
        gpio_read       = 0xf5
        gpio_enable     = 0xf6
        gpio_config     = 0xf7

    class ADC_Registers(enum.IntEnum):
        STATUS          =0x00   #Status Register
        ADCMODE         =0x01   #ADC Mode Register
        IFMODE          =0x02   #Interface Mode Register  
        REGCHECK        =0x03   #Register Check
        DATA            =0x04   #Data Register
        GPICON          =0x06   #GPIO Configuration Register
        ID              =0x07   #ID Register

        CH0             =0x10   #Channel Register 0
        CH1             =0x11   #Channel Register 1
        CH2             =0x12   #Channel Register 2
        CH3             =0x13   #Channel Register 3

        SETUPCON0       =0x20   #Setup Configuration Register 0
        SETUPCON1       =0x21   #Setup Configuration Register 1
        SETUPCON2       =0x22   #Setup Configuration Register 2
        SETUPCON3       =0x23   #Setup Configuration Register 3

        FILTCON0        =0X28   #Filter Configuration Register 0
        FILTCON1        =0X29   #Filter Configuration Register 1
        FILTCON2        =0x2A   #Filter Configuration Register 2
        FILTCON3        =0x2B   #Filter Configuration Register 3

        OFFSET0         =0x30   #Offset Register 0
        OFFSET1         =0x31   #Offset Register 1
        OFFSET2         =0x32   #Offset Register 2
        OFFSET3         =0x33   #Offset Register 3

        GAIN0           =0x38   #Gain Register 0
        GAIN1           =0x39   #Gain Register 1
        GAIN2           =0x3A   #Gain Register 2
        GAIN3           =0x3B   #Gain Register 3


    class SamplingSpeed(enum.IntEnum):
        """This are the values to control the data output rate of the ADC with sinc5 + sinc1 filters active"""
    
        Hz_31250       = 0x00 #data output rate = 31250 samples per second
        Hz_15625       = 0x06 #data output rate = 15625 samples per second
        Hz_10417       = 0x07 #data output rate = 10417 samples per second
        Hz_5208        = 0x08 #data output rate = 5208 samples per second
        Hz_2597        = 0x09 #data output rate = 2597 samples per second
        Hz_1007        = 0x0A #data output rate = 1007 samples per second
        Hz_503_8       = 0x0B #data output rate = 503.8 samples per second
        Hz_381         = 0x0C #data output rate = 381 samples per second
        Hz_200_3       = 0x0D #data output rate = 200.3 samples per second
        Hz_100_2       = 0x0E #data output rate = 100.2 samples per second
        Hz_59_2        = 0x0F #data output rate = 59.2 samples per second
        Hz_49_68       = 0x10 #data output rate = 49.68 samples per second
        Hz_20_01       = 0x11 #data output rate = 20.01 samples per second
        Hz_16_63       = 0x12 #data output rate = 16.63 samples per second
        Hz_10          = 0x13 #data output rate = 10 samples per second
        Hz_5           = 0x14 #data output rate = 5 samples per second
        Hz_2_5         = 0x15 #data output rate = 2 samples per second
        Hz_1_25        = 0x16 #data output rate = 1.25 samples per second

    MapSampleSpeedEnumToNumber = {
        SamplingSpeed.Hz_31250 : 31250.0,
        SamplingSpeed.Hz_15625 : 15625.0,
        SamplingSpeed.Hz_10417 : 10417.0,
        SamplingSpeed.Hz_5208  : 5208.0,
        SamplingSpeed.Hz_2597  : 2597.0,
        SamplingSpeed.Hz_1007  : 1007.0,
        SamplingSpeed.Hz_503_8 : 503.8,
        SamplingSpeed.Hz_381   : 381.0,
        SamplingSpeed.Hz_200_3 : 200.3,
        SamplingSpeed.Hz_100_2 : 100.2,
        SamplingSpeed.Hz_59_2  : 59.2,
        SamplingSpeed.Hz_49_68 : 49.68,
        SamplingSpeed.Hz_20_01 : 20.01,
        SamplingSpeed.Hz_16_63 : 16.63,
        SamplingSpeed.Hz_10    : 10.0,
        SamplingSpeed.Hz_5     : 5.0,
        SamplingSpeed.Hz_2_5   : 2.5,
        SamplingSpeed.Hz_1_25  : 1.25,
    }

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, offset_mode=i2c.I2COffsetMode.NoOffset, auto_lock=True, **kwargs)
        self._spi_gpio_cache = 0
        self._last_spi_status = 0
        self._active_channel = -1
        self._in_differential_mode = False
        self._selected_speed = self.SamplingSpeed.Hz_49_68
        self._differential_ch_map = [0x01,0x43,0x20,0x62] # ch 0 -> AIN0 - AIN1, # ch 1 -> AIN2 - AIN3, # ch 2 -> AIN1 - AIN0, # ch 3 -> AIN3 - AIN2
        self._single_end_ch_map   = [0x04,0x24,0x44,0x64] # ch 0 -> AIN0, ch 1 -> AIN1, ch 2 -> AIN2, ch 3 -> AIN3, 

    def init_chip(self, active_channel:int, differential_mode:bool, sampling_seed:SamplingSpeed):
        self._init_bridge()
        self._init_adc_registers()
        self.set_analog_input_mode(differential_mode)
        self.set_sampling_speed(sampling_seed)
        self.set_active_channel(active_channel)
        
    def set_analog_input_mode(self, differential_mode:bool):
        self._in_differential_mode = differential_mode
        if self._in_differential_mode:
            self.write_register_bytes(self.ADC_Registers.SETUPCON0, [0x1F, 0x20]) # Bipolar coded output (offset binary) 
        else:
            self.write_register_bytes(self.ADC_Registers.SETUPCON0, [0x0F, 0x20]) # Unipolar coded output
    
    def is_in_differential_input_mode(self) -> bool:
        return self._in_differential_mode

    def set_active_channel(self, channel: int):
        """ This function configures inputs for single channel measurement """
        if channel < 0 or channel > 3:
            raise ValueError(f"Channel out of range: {channel}")
        
        if self._in_differential_mode:
            self.write_register_bytes(self.ADC_Registers.CH0,[0x80, self._differential_ch_map[channel]])     #
        else:   
            self.write_register_bytes(self.ADC_Registers.CH0,[0x80, self._single_end_ch_map[channel]]) 

    def get_active_channel(self) -> int:
        return self._active_channel
    
    def read_active_channel_voltage(self) -> float:
        """ This function is used to read out the voltage of the active channel.

            Result
            ------
            voltage:float
                return the voltage according to chip setting. single_end 0..+5.0V, differential: +-2.5V
        """
        if self._in_differential_mode: 
            data24_signed = self._read_adc_data_reg_as_signed_integer()
            ch_voltage = (float(data24_signed) / float(2**23)) * 2.5
        else: 
            data24_unsigned = self._read_adc_data_reg_as_unsigned_integer()
            ch_voltage = (float(data24_unsigned) / float(2**24)) * 2.5
        return ch_voltage
    
    def read_channel_voltage(self, channel:int) -> float:
        """ This function is used to read out the voltage of the selected channel.

            Parameter
            ---------
            in single end mode there are 4 channels (0 .. 3) selectable
            in differential mode 2 channels (0,1) or the inversion of them as (2,3)

            Result
            ------

            voltage:float
                return the voltage according to chip setting. single_end 0..+5.0V, differential: +-2.5V
        """
        if channel != self._active_channel:
            self.set_active_channel(channel)
        return self.read_active_channel_voltage()
    
    def set_sampling_speed(self, speed:SamplingSpeed): 
        self._selected_speed = speed
        self.write_register_bytes(self.ADC_Registers.FILTCON0,  [0x02, self._selected_speed]) 

    def get_sampling_speed(self) -> SamplingSpeed:
        return self._selected_speed
    
    def get_sampling_speed_in_Hz(self) -> float:
        return self.convert_sampling_speed_to_Hz(self._selected_speed)
    
    def convert_sampling_speed_to_Hz(self, speed:SamplingSpeed) -> float:
        return self.MapSampleSpeedEnumToNumber[speed]
    
    #------- internal -------------

    def _init_bridge(self): 
        """ Initializes chip communication. 
            Must be called at least once after assigning chip to master 
        """   
        self._spi_bridge_config_spi(0x0c)  # 0x0c = ORDER=MSB first,  MODE0/1=CPHA=1, CPOL=1, F0/1(SPI_Clk)=1.8MHz
        self._spi_bridge_gpio_config(0x55) #  select all pins to Push-Pull output 
        self._spi_bridge_gpio_enable(self._SPI_Function_IDS.config_spi.slave_select_12)
        self._spi_bridge_gpio_write(0x00)  # Disable all (1 = off, 0 = on)

    def _init_adc_registers(self):
        # single conversion mode, int. ref no delay, int. osc
        self.write_register_bytes(self.ADC_Registers.ADCMODE, [0xC0, 0x00]) 
        self.write_register_bytes(self.ADC_Registers.IFMODE,  [0x00, 0x00])
        self.write_register_bytes(self.ADC_Registers.CH0,[ 0x80, 0x01]) # activate CH0 
        self.write_register_bytes(self.ADC_Registers.CH1,[ 0x00, 0x00]) # disable CH1-3
        self.write_register_bytes(self.ADC_Registers.CH2,[ 0x00, 0x00]) 
        self.write_register_bytes(self.ADC_Registers.CH3,[ 0x00, 0x00]) 


    def _read_adc_data_reg_as_signed_integer(self) -> int:
        """ read ADC data register content.
            returns the content converted to signed integer
        """
        self._spi_bridge_gpio_enable(self._SPI_Function_IDS.config_spi.slave_select_12|self._SPI_Function_IDS.config_spi.slave_select_0)
        self._spi_bridge_gpio_write(0x00)

        data_bytes = self.read_register_bytes(self.ADC_Registers.DATA, 3) # msb first
        data_bytes.reverse()  # make LSB first

        if data_bytes[2] & 0b1000_0000:   # if mbs is set it is a positive number (strange but true)
            data_bytes[2] &= ~0b1000_0000 # clear MSB bit
            data_bytes.append(0x00)       # add zeros to make it 4 bytes long and represent positive 'signed int'

        else:                             # negative values have cleared sign bit
            data_bytes[2] |= 0b1000_0000  # convert to standard signed number by setting msb bit
            data_bytes.append(0xff)       # add ones to make it 4 bytes long and represent negative 'signed int'

        self._spi_bridge_gpio_write(0xFF)  # Disable all (1 = off, 0 = on)
        self._spi_bridge_gpio_enable(self._SPI_Function_IDS.config_spi.slave_select_12)

        data_array = bytearray(data_bytes)
        int_value, *_ = struct.unpack("<i",data_array)
        return int_value

    def _read_adc_data_reg_as_unsigned_integer(self) -> int:
        """ read ADC data register content.
            returns the content converted to unsigned integer
        """
        self._spi_bridge_gpio_enable(self._SPI_Function_IDS.config_spi.slave_select_12|self._SPI_Function_IDS.config_spi.slave_select_0)
        self._spi_bridge_gpio_write(0x00)

        data_bytes = self.read_register_bytes(self.ADC_Registers.DATA, 3) # msb first
        data_bytes.reverse()    # LSB first
        data_bytes.append(0x00) # make it 4 bytes long to represent unsigned 'int'

        self._spi_bridge_gpio_write(0xFF)  # Disable all (1 = off, 0 = on)
        self._spi_bridge_gpio_enable(self._SPI_Function_IDS.config_spi.slave_select_12)

        data_array = bytearray(data_bytes)
        int_value, *_ = struct.unpack("<I",data_array)
        return int_value
                     


    ####SPI/I2C Bridge functions#####################################################################################################################          
    def write_register_bytes(self, reg_id: ADC_Registers, data:list[int]):
        """ Write some data to a ADC register. 

            reg_id: defines the register to write to, 
            data:   list of bytes written into register. MSB first
        """
        self._spi_bridge_write_buffer(self._SPI_Function_IDS.slave_select_0, [reg_id.value] + data)
    
    def read_register_bytes(self, reg_id: ADC_Registers, num_of_data_bytes:int) -> list[int]:
        """ read ADC register content. 

            reg_id:       defines the register to read, 
            num_of_bytes: defines how many bytes the register contains

            returns a list with read bytes
        """
        # send command with read flag and dummy data as many as we want to read data bytes
        buffer_data = [reg_id.value + 0x40] # set read bit 
        buffer_data.extend([0xff for _ in range(num_of_data_bytes)])
        self._spi_bridge_write_buffer(self._SPI_Function_IDS.slave_select_0, buffer_data)

        # read one byte more due to sent register address as additional byte
        buffer_result = self._spi_bridge_read_buffer(1 + num_of_data_bytes) 

        # discard first byte which is only garbage which is received while sending the command byte
        return buffer_result[1:] 
    
    def read_register_integer(self, reg_id: ADC_Registers, num_of_data_bytes: int) -> int:
        """ read ADC register content.
            reg_id:         defines the register to read,
            num_of_bytes:   defines how many bytes the register contains
            returns the content converted to unsigned integer
        """
        data_bytes = self.read_register_bytes(reg_id, num_of_data_bytes)
        int_value = 0
        data_bytes.reverse()  # make LSB first

        for i in range(len(data_bytes)):
            int_value += data_bytes[i] * (256 ** i) #convert the data bytes into an integer
        return int_value
 
    def _spi_bridge_write_byte(self, id: _SPI_Function_IDS, val: int):
        self.write_bytes([id, val])

    def _spi_bridge_read_byte(self, id: _SPI_Function_IDS) -> int:
        self.write_byte(id)
        return self.read_byte()

    def _spi_bridge_config_spi(self, val: int):
        self._spi_bridge_write_byte(self._SPI_Function_IDS.config_spi, val)

    def _spi_bridge_clear_int(self):
        self._spi_bridge_write_byte(self._SPI_Function_IDS.clear_int, 0)

    def _spi_bridge_set_idle_mode(self):
        self._spi_bridge_write_byte(self._SPI_Function_IDS.idle_mode, 0)

    def _spi_bridge_gpio_write(self, val: int):
        self._spi_gpio_cache = val
        self._spi_bridge_write_byte(self._SPI_Function_IDS.gpio_write, self._spi_gpio_cache)

    def _spi_bridge_gpio_read(self) -> int:
        return self._spi_bridge_read_byte(self._SPI_Function_IDS.gpio_read)

    def _spi_bridge_gpio_enable(self, val: int):
        self._spi_bridge_write_byte(self._SPI_Function_IDS.gpio_enable, val)

    def _spi_bridge_gpio_config(self, val: int):
        self._spi_bridge_write_byte(self._SPI_Function_IDS.gpio_config, val)

    def _spi_bridge_write_buffer(self, id: _SPI_Function_IDS, data: list[int]):
        self.write_bytes([int(id)] + data)

    def _spi_bridge_read_buffer(self, size: int) -> list[int]:
        return self.read_bytes(size)
    

