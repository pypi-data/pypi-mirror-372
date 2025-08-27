
"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import nanosurf.lib.devices.i2c.bus_master as i2c

class Chip_MAX1161x(i2c.I2CChip):
    """ 4/8/12-Channel 12bit ADC chip family from maxim integrated"""

    class Reference_Modes(enum.IntEnum):
        VDD_used_as_reference            = 0
        External_Reference_in            = 2
        Internal_Analog_in_always_off    = 4
        Internal_Analog_in_always_on     = 5
        Internal_Ref_out_always_off      = 6
        Internal_Ref_out_always_on       = 7

    class Scan_Modes(enum.IntEnum):
        Start_from_AIN0                     = 0
        Convert_single_channel_eight_times  = 1
        Scan_upper_part                     = 2
        Convert_single_channel              = 3

    class _Setup_Mode_Bit_Mask(enum.IntEnum):
        Setup_mode  = 0x80
        Reference_Sel_Mask = 0x70
        External_Clock = 0x08
        Bipolar_Inputs = 0x04
        No_Reset = 0x02

    class _Config_Mode_Bit_Mask(enum.IntEnum):
        Config_mode = 0x00
        Scan_bit_mask = 0x60
        Channel_sel_mask = 0x01E
        Single_end_inputs = 0x01

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, i2c.I2COffsetMode.NoOffset, **kwargs)
        self._cur_config_mode = self._Setup_Mode_Bit_Mask.Setup_mode
        self._cur_setup_mode  = self._Config_Mode_Bit_Mask.Config_mode

    def init_device(self, ref_mode:Reference_Modes, external_clock:bool, bipolar_inputs:bool, single_end_inputs:bool, scan_mode:Scan_Modes = Scan_Modes.Convert_single_channel, channel_select: int = 0):
        # prepare setup register
        self._cur_setup_mode = self._Setup_Mode_Bit_Mask.Setup_mode
        self._cur_setup_mode |= ref_mode.value * 16
        if external_clock: 
            self._cur_setup_mode |= self._Setup_Mode_Bit_Mask.External_Clock
        if bipolar_inputs: 
            self._cur_setup_mode |= self._Setup_Mode_Bit_Mask.Bipolar_Inputs
        self._cur_setup_mode |= self._Setup_Mode_Bit_Mask.No_Reset

        # prepare config register
        self._cur_config_mode = self._Config_Mode_Bit_Mask.Config_mode
        self._cur_config_mode |= scan_mode*32
        self._cur_config_mode |= channel_select*2
        if single_end_inputs: 
            self._cur_config_mode |= self._Config_Mode_Bit_Mask.Single_end_inputs

        # send configuration  to device
        self.write_bytes([self._cur_setup_mode, self._cur_config_mode])

    def read_active_channel(self) -> int:
        """ Read the current channels ADC input value.
            Use self.select_active_channel() to select an input as active
            Attention: Device has to be in Convert_single_channel mode
        """
        value_high_byte, value_low_byte = self.read_bytes(2)
        value_high_byte &= 0x0f
        return value_high_byte*256 + value_low_byte
    
    def select_active_channel(self, active_channel:int):
        """ Selects the channel to be read by self.read_active_channel(). 
            Device is set into Convert_single_channel mode automatically
        """        
        self._cur_config_mode &= ~self._Config_Mode_Bit_Mask.Channel_sel_mask
        self._cur_config_mode |= active_channel*2
        self._cur_config_mode &= ~self._Config_Mode_Bit_Mask.Scan_bit_mask
        self._cur_config_mode |= self.Scan_Modes.Convert_single_channel *32
        self.write_byte(self._cur_config_mode)

    def read_multiple_channels(self, num_channels:int) -> list[int]:
        self._cur_config_mode &= ~self._Config_Mode_Bit_Mask.Channel_sel_mask
        self._cur_config_mode |= num_channels*2
        self._cur_config_mode &= ~self._Config_Mode_Bit_Mask.Scan_bit_mask
        self._cur_config_mode |= self.Scan_Modes.Start_from_AIN0 *32
        self.write_byte(self._cur_config_mode)
        try:
            read_values = self.read_bytes(2*num_channels)
            hi_lo_grouped_list = [read_values[i:i+2] for i in range(0, len(read_values), 2)]
            channel_values = [int(int(hi&0x0f)*256+lo) for hi,lo in hi_lo_grouped_list]
            return channel_values
        except Exception:
            raise ValueError(f"Could not read {num_channels} channels from chip")
