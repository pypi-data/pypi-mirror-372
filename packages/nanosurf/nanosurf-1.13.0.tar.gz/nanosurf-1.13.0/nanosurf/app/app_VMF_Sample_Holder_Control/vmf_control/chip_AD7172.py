"""Copyright (C) Nanosurf AG - All Rights Reserved (2024)
License - MIT"""

import enum
import time
import struct
import nanosurf.lib.devices.i2c.bus_master as i2c 


average = False
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


    class sampling_speed(enum.IntEnum):
        """This are the values to control the data output rate of the ADC with sinc5 + sinc1 filters active"""
    
        x31250sps       = 0x00 #data output rate = 31250 samples per second
        x15625sps       = 0x06 #data output rate = 15625 samples per second
        x10417sps       = 0x07 #data output rate = 10417 samples per second
        x5208sps        = 0x08 #data output rate = 5208 samples per second
        x2597sps        = 0x09 #data output rate = 2597 samples per second
        x1007sps        = 0x0A #data output rate = 1007 samples per second
        x503c8sps       = 0x0B #data output rate = 503.8 samples per second
        x381sps         = 0x0C #data output rate = 381 samples per second
        x200c3sps       = 0x0D #data output rate = 200.3 samples per second
        x100c2sps       = 0x0E #data output rate = 100.2 samples per second
        x59c2sps        = 0x0F #data output rate = 59.2 samples per second
        x49c68sps       = 0x10 #data output rate = 49.68 samples per second
        x20c01sps       = 0x11 #data output rate = 20.01 samples per second
        x16c63sps       = 0x12 #data output rate = 16.63 samples per second
        x10sps          = 0x13 #data output rate = 10 samples per second
        x5sps           = 0x14 #data output rate = 5 samples per second
        x2c5sps         = 0x15 #data output rate = 2 samples per second
        x1c25sps        = 0x16 #data output rate = 1.25 samples per second



    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, offset_mode=i2c.I2COffsetMode.NoOffset, auto_lock=True, **kwargs)
        self._spi_gpio_cache = 0
        self._last_spi_status = 0
        self._active_channel = -1

    def init_bridge(self): 
        """ Initializes chip communication. 
            Must be called at least once after assigning chip to master 
        """   
        self._spi_bridge_config_spi(0x0c)  # 0x0c = ORDER=MSB first,  MODE0/1=CPHA=1, CPOL=1, F0/1(SPI_Clk)=1.8MHz
        self._spi_bridge_gpio_config(0x55) #  select all pins to Push-Pull output 
        self._spi_bridge_gpio_enable(self._SPI_Function_IDS.config_spi.slave_select_12)
        self._spi_bridge_gpio_write(0x00)  # Disable all (1 = off, 0 = on)


###########ADC functions#################################################################################
    def setup_differential_mode(self):
        """ Setting up the registers of the chip. 
            This is the setup for a differential configuration.
        """  
        self.differential = True #information variable for other functions so that they know that the system is in differential mode.
        self.write_register_bytes(self.ADC_Registers.ADCMODE, [0xC0, 0x10])
        self.write_register_bytes(self.ADC_Registers.IFMODE,[0x00, 0x00])
        self.write_register_bytes(self.ADC_Registers.SETUPCON0, [0x1F, 0x20])  #Bipolar coded output (offset binary) 
        self.write_register_bytes(self.ADC_Registers.FILTCON0, [0x06, self.sampling_speed.x49c68sps]) #self.write_register_bytes(self.ADC_Registers.FILTCON0, [0x0E, 0x16])

        self._select_channel(0)
        print("\nThe device is set to differential mode...\n")

                
    def setup_single_end_mode(self):
        """ Setting up the registers of the chip. 
            This is the setup for a single ended configuration.
        """  
        self.differential = False #information variable for other functions so that they know that the system is NOT in differential mode.
        self.write_register_bytes(self.ADC_Registers.ADCMODE, [0x70, 0x00])
        self.write_register_bytes(self.ADC_Registers.IFMODE,[0x00, 0x00])
        self.write_register_bytes(self.ADC_Registers.SETUPCON0, [0x0F, 0x20]) #Unipolar coded output
        self.write_register_bytes(self.ADC_Registers.FILTCON0, [0x0E, self.sampling_speed.x49c68sps])
        self._select_channel(0)                
        print("\nThe device is set to single ended mode...\n")


    def read_channel(self, channel: int):
        """ This function is used to read out the voltage of the selected channel.
            in single end mode there are 4 channels (0 .. 3) selectable
        """
        if not channel == self._active_channel:
            self._select_channel(channel)
            time.sleep(0.3)
    
        self.write_register_bytes(self.ADC_Registers.ADCMODE, [0xC0, 0x10])
        
        if self.differential: 
            val = self.read_adc_data_signed_integer()
            pinVoltage = (float(val) / float(2**23)) * 2.5
            
        else:   #single ended
            data24 = self.read_register_integer(self.ADC_Registers.DATA, 3)
            pinVoltage = (float(data24) / float(2**24)) 
           
        return pinVoltage
    
    def read_manual_channel(self, channel: int):
        """ This function is used to read out the voltage of the selected channel.
            in single end mode there are 4 channels (0 .. 3) selectable
            With this function, the CS Signal is set manually
        """
        if not channel == self._active_channel:
            self._select_channel(channel)

        # cs in manual control
            
        self._spi_bridge_gpio_enable(self._SPI_Function_IDS.config_spi.slave_select_12|self._SPI_Function_IDS.config_spi.slave_select_0)
        # cs set low
        self._spi_bridge_gpio_write(0x00)

        self.write_register_bytes(self.ADC_Registers.ADCMODE, [0xC0, 0x10])
        time.sleep(0.08)

        if self.differential: 
            val = self.read_adc_data_signed_integer()
            pinVoltage = (float(val) / float(2**23)) * 2.5
        else:   #single ended
            data24 = self.read_register_integer(self.ADC_Registers.DATA, 3)
            pinVoltage = (float(data24) / float(2**24)) 

        # cs set hight
        # cs in auto mode
        self._spi_bridge_gpio_write(0xFF)  # Disable all (1 = off, 0 = on)
        self._spi_bridge_gpio_enable(self._SPI_Function_IDS.config_spi.slave_select_12)

        return pinVoltage
    
    def read_adc_data_signed_integer(self) -> int:
        """ read ADC data register content.
            returns the content converted to signed integer
        """
        data_bytes = self.read_register_bytes(self.ADC_Registers.DATA, 3) # msb first
        data_bytes.reverse()  # make LSB first

        if data_bytes[2] & 0b1000_0000:   # if mbs is set it is a positive number (strange but true)
            data_bytes[2] &= ~0b1000_0000 # clear msb bit
            data_bytes.append(0x00)       # add zeros to make it 4 bytes long and represent positive 'signed int'

        else:                             # negative values have cleared sign bit
            data_bytes[2] |= 0b1000_0000  # convert to standard signed number by setting msb bit
            data_bytes.append(0xff)       # add ones to make it 4 bytes long and represent negative 'signed int'

        data_array = bytearray(data_bytes)
        int_value, *_ = struct.unpack("<i",data_array)
        return int_value

    def read_adc_data_unsigned_integer(self) -> int:
        """ read ADC data register content.
            returns the content converted to unsigned integer
        """
        data_bytes = self.read_register_bytes(self.ADC_Registers.DATA, 3) # msb first
        data_bytes.reverse()    # LSB first
        data_bytes.append(0x00) # make it 4 bytes long to represent unsigned 'int'
        data_array = bytearray(data_bytes)
        int_value, *_ = struct.unpack("<I",data_array)
        return int_value
                     
    def _select_channel(self, channel: int):
        """ This function is used to set the channel registers
            to the channel that was set and transferred.
        """

        if self.differential: #Set the register according to the channel set in differential mode.
            if channel == 0: #Positive Input = AIN0, Negative Input = AIN1
                self.write_register_bytes(self.ADC_Registers.CH0,[0x80, 0x01])

                self.write_register_bytes(self.ADC_Registers.CH1,[0x00, 0x43])
                self.write_register_bytes(self.ADC_Registers.CH2,[0x00, 0x10])
                self.write_register_bytes(self.ADC_Registers.CH3,[0x00, 0x62])
            
            elif channel == 1: #Positive Input = AIN2, Negative Input = AIN3
                self.write_register_bytes(self.ADC_Registers.CH1,[0x80, 0x43])

                self.write_register_bytes(self.ADC_Registers.CH0,[0x00, 0x01])
                self.write_register_bytes(self.ADC_Registers.CH2,[0x00, 0x10])
                self.write_register_bytes(self.ADC_Registers.CH3,[0x00, 0x62])

            elif channel == 2: #Positive Input = AIN1, Negative Input = AIN0
                self.write_register_bytes(self.ADC_Registers.CH2,[0x80, 0x10])

                self.write_register_bytes(self.ADC_Registers.CH0,[0x00, 0x01])
                self.write_register_bytes(self.ADC_Registers.CH1,[0x00, 0x43])
                self.write_register_bytes(self.ADC_Registers.CH3,[0x00, 0x62])
                
            elif channel == 3: #Positive Input = AIN3, Negative Input = AIN2
                self.write_register_bytes(self.ADC_Registers.CH3,[0x80, 0x62])

                self.write_register_bytes(self.ADC_Registers.CH0,[0x00, 0x01])
                self.write_register_bytes(self.ADC_Registers.CH1,[0x00, 0x43])
                self.write_register_bytes(self.ADC_Registers.CH2,[0x00, 0x10])

            else: #Positive Input = AIN0, Negative Input = AIN1
                self.write_register_bytes(self.ADC_Registers.CH0,[0x80, 0x01])

                self.write_register_bytes(self.ADC_Registers.CH1,[0x00, 0x43])
                self.write_register_bytes(self.ADC_Registers.CH2,[0x00, 0x10])
                self.write_register_bytes(self.ADC_Registers.CH3,[0x00, 0x62])

            self._active_channel = channel #sets the channel memory variable to the newly set channel.


        else: #Set the register according to the channel set in single ended mode.
            if channel == 0: #Positive Input = AIN0, Negative Input = AIN4 (GND)
                self.write_register_bytes(self.ADC_Registers.CH0,[0x80, 0x04])

                self.write_register_bytes(self.ADC_Registers.CH1,[0x00, 0x24])
                self.write_register_bytes(self.ADC_Registers.CH2,[0x00, 0x44])
                self.write_register_bytes(self.ADC_Registers.CH3,[0x00, 0x64])
            
            elif channel == 1: #Positive Input = AIN1, Negative Input = AIN4 (GND)
                self.write_register_bytes(self.ADC_Registers.CH1,[0x80, 0x24])

                self.write_register_bytes(self.ADC_Registers.CH0,[0x00, 0x04])
                self.write_register_bytes(self.ADC_Registers.CH2,[0x00, 0x44])
                self.write_register_bytes(self.ADC_Registers.CH3,[0x00, 0x64])

            elif channel == 2: #Positive Input = AIN2, Negative Input = AIN4 (GND)
                self.write_register_bytes(self.ADC_Registers.CH2,[0x80, 0x44])

                self.write_register_bytes(self.ADC_Registers.CH0,[0x00, 0x04])
                self.write_register_bytes(self.ADC_Registers.CH1,[0x00, 0x24])
                self.write_register_bytes(self.ADC_Registers.CH3,[0x00, 0x64])
                
            elif channel == 3: #Positive Input = AIN3, Negative Input = AIN4 (GND)
                self.write_register_bytes(self.ADC_Registers.CH3,[0x80, 0x64])

                self.write_register_bytes(self.ADC_Registers.CH0,[0x00, 0x04])
                self.write_register_bytes(self.ADC_Registers.CH1,[0x00, 0x24])
                self.write_register_bytes(self.ADC_Registers.CH2,[0x00, 0x44])

            else: #Positive Input = AIN0, Negative Input = AIN4 (GND)
                self.write_register_bytes(self.ADC_Registers.CH0,[0x80, 0x04])

                self.write_register_bytes(self.ADC_Registers.CH1,[0x00, 0x24])
                self.write_register_bytes(self.ADC_Registers.CH2,[0x00, 0x44])
                self.write_register_bytes(self.ADC_Registers.CH3,[0x00, 0x64])

            self._active_channel = channel #sets the channel memory variable to the newly set channel.



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
    

