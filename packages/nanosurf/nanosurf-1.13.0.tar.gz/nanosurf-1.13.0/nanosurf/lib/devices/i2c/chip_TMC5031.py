"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import nanosurf.lib.devices.i2c.bus_master as i2c 

class RampStatFlags(enum.IntEnum):
    Stop_Left             = 0x00000001
    Stop_Right            = 0x00000002
    Stop_Left_Latched     = 0x00000004
    Stop_Right_Latched    = 0x00000008
    Stop_Left_Event       = 0x00000010
    Stop_Right_Event      = 0x00000020
    Stop_StallGuard_Event = 0x00000040
    Pos_Reached_Event     = 0x00000080
    Velocity_Reached      = 0x00000100
    TargetPos_Reached     = 0x00000200
    ZeroVelocity_Reached  = 0x00000400
    T_Wait_Active         = 0x00000800
    Second_Move_Active    = 0x00001000
    Status_StallGuard     = 0x00002000

class SWModeFlags(enum.IntEnum):
    Switch_Left_Enabled     = 0x00000001
    Switch_Right_Enabled    = 0x00000002
    Switch_Left_HighActive  = 0x00000004
    Switch_Right_HighActive = 0x00000008
    Swap_Left_Right_Switch  = 0x00000010
    LatchPos_Left_Active    = 0x00000020
    LatchPos_Left_Inactive  = 0x00000040
    LatchPos_Right_Active   = 0x00000080
    LatchPos_Right_Inactive = 0x00000100
    Reserved                = 0x00000200
    StallGuard_Stop_Enabled = 0x00000400
    SoftStop_Enabled        = 0x00000800

class Reg_Channel(enum.IntEnum):
    # General Configuration
    GCONF = 0
    GSTAT = 1
    TESTSEL = 2
    INPUT = 3
    X_COMPARE= 4
    # RampGen Motion Control
    RAMPMODE =  5
    XACTUAL =  6
    VACTUAL =  7
    VSTART =  8
    A1 =  9
    V1 =  10
    AMAX =  11
    VMAX =  12
    DMAX =  13
    D1 =  14
    VSTOP =  15
    TZEROWAIT = 16
    XTARGET =  17
    # RampGen Driver Features Control
    IHOLD_IRUN =  18
    VCOOLTHRS =  19
    VHIGH =  20
    SW_MODE =  21
    RAMP_STAT =  22
    XLATCH =  23
    # Motor Drive Registers
    MSLUT_0 =  24
    MSLUT_1 =  25
    MSLUT_2 =  26
    MSLUT_3 =  27
    MSLUT_4 =  28
    MSLUT_5 =  29
    MSLUT_6 =  30
    MSLUT_7 =  31
    MSLUTSEL =  32
    MSLUTSTART =  33
    MSCNT =  34
    MSCURACT =  35
    CHOPCONF =  36
    COOLCONF =  37
    DRV_STATUS =  38

class Chip_TMC5031(i2c.I2CChip): 
    """ stepper motor controller chip
    connected to I2C by a I2C<->SPI bridge 
    """

    class SPI_Function_IDS(enum.IntEnum):
        slave_select_0  = 0x01
        slave_select_1  = 0x02
        slave_select_2  = 0x04
        slave_select_3  = 0x08
        slave_select_23 = 0x04 | 0x08
        config_spi      = 0xf0
        clear_int       = 0xf1
        idle_mode       = 0xf2
        gpio_write      = 0xf4
        gpio_read       = 0xf5
        gpio_enable     = 0xf6
        gpio_config     = 0xf7

    class Reg_TMC(enum.IntEnum):
        #// General Configuration
        GCONF = 0x00
        GSTAT = 0x01
        TESTSEL = 0x03
        INPUT = 0x04
        X_COMPARE = 0x05
        # RampGen Motion Control
        M1_RAMPMODE = 0x20
        M1_XACTUAL = 0x21
        M1_VACTUAL = 0x22
        M1_VSTART = 0x23
        M1_A1 = 0x24
        M1_V1 = 0x25
        M1_AMAX = 0x26
        M1_VMAX = 0x27
        M1_DMAX = 0x28
        M1_D1 = 0x2A
        M1_VSTOP = 0x2B
        M1_TZEROWAIT = 0x2C
        M1_XTARGET = 0x2D
        M2_RAMPMODE = 0x40
        M2_XACTUAL = 0x41
        M2_VACTUAL = 0x42
        M2_VSTART = 0x43
        M2_A1 = 0x44
        M2_V1 = 0x45
        M2_AMAX = 0x46
        M2_VMAX = 0x47
        M2_DMAX = 0x48
        M2_D1 = 0x4A
        M2_VSTOP = 0x4B
        M2_TZEROWAIT = 0x4C
        M2_XTARGET = 0x4D
        # RampGen Driver Features Control
        M1_IHOLD_IRUN = 0x30
        M1_VCOOLTHRS = 0x31
        M1_VHIGH = 0x32
        M1_SW_MODE = 0x34
        M1_RAMP_STAT = 0x35
        M1_XLATCH = 0x36
        M2_IHOLD_IRUN = 0x50
        M2_VCOOLTHRS = 0x51
        M2_VHIGH = 0x52
        M2_SW_MODE = 0x54
        M2_RAMP_STAT = 0x55
        M2_XLATCH = 0x56
        # Motor Drive Registers
        M1_MSLUT_0 = 0x60
        M1_MSLUT_1 = 0x61
        M1_MSLUT_2 = 0x62
        M1_MSLUT_3 = 0x63
        M1_MSLUT_4 = 0x64
        M1_MSLUT_5 = 0x65
        M1_MSLUT_6 = 0x66
        M1_MSLUT_7 = 0x67
        M1_MSLUTSEL = 0x68
        M1_MSLUTSTART = 0x69
        M1_MSCNT = 0x6A
        M1_MSCURACT = 0x6B
        M1_CHOPCONF = 0x6C
        M1_COOLCONF = 0x6D
        M1_DRV_STATUS = 0x6F
        M2_MSLUT_0 = 0x70
        M2_MSLUT_1 = 0x71
        M2_MSLUT_2 = 0x72
        M2_MSLUT_3 = 0x73
        M2_MSLUT_4 = 0x74
        M2_MSLUT_5 = 0x75
        M2_MSLUT_6 = 0x76
        M2_MSLUT_7 = 0x77
        M2_MSLUTSEL = 0x78
        M2_MSLUTSTART = 0x79
        M2_MSCNT = 0x7A
        M2_MSCURACT = 0x7B
        M2_CHOPCONF = 0x7C
        M2_COOLCONF = 0x7D
        M2_DRV_STATUS = 0x7F
    
    config_set_first:dict[Reg_Channel, Reg_TMC] = {
        Reg_Channel.GCONF: Reg_TMC.GCONF,
        Reg_Channel.GSTAT: Reg_TMC.GSTAT,
        Reg_Channel.TESTSEL: Reg_TMC.TESTSEL,
        Reg_Channel.INPUT: Reg_TMC.INPUT,
        Reg_Channel.X_COMPARE: Reg_TMC.X_COMPARE,
        Reg_Channel.RAMPMODE: Reg_TMC.M1_RAMPMODE,
        Reg_Channel.XACTUAL: Reg_TMC.M1_XACTUAL,
        Reg_Channel.VACTUAL: Reg_TMC.M1_VACTUAL,
        Reg_Channel.VSTART: Reg_TMC.M1_VSTART,
        Reg_Channel.A1: Reg_TMC.M1_A1,
        Reg_Channel.V1: Reg_TMC.M1_V1,
        Reg_Channel.AMAX: Reg_TMC.M1_AMAX,
        Reg_Channel.VMAX: Reg_TMC.M1_VMAX,
        Reg_Channel.DMAX: Reg_TMC.M1_DMAX,
        Reg_Channel.D1: Reg_TMC.M1_D1,
        Reg_Channel.VSTOP: Reg_TMC.M1_VSTOP,
        Reg_Channel.TZEROWAIT: Reg_TMC.M1_TZEROWAIT,
        Reg_Channel.XTARGET: Reg_TMC.M1_XTARGET,
        Reg_Channel.IHOLD_IRUN: Reg_TMC.M1_IHOLD_IRUN,
        Reg_Channel.VCOOLTHRS: Reg_TMC.M1_VCOOLTHRS,
        Reg_Channel.VHIGH: Reg_TMC.M1_VHIGH,
        Reg_Channel.SW_MODE: Reg_TMC.M1_SW_MODE,
        Reg_Channel.RAMP_STAT: Reg_TMC.M1_RAMP_STAT,
        Reg_Channel.XLATCH: Reg_TMC.M1_XLATCH,
        Reg_Channel.MSLUT_0: Reg_TMC.M1_MSLUT_0,
        Reg_Channel.MSLUT_1: Reg_TMC.M1_MSLUT_1,
        Reg_Channel.MSLUT_2: Reg_TMC.M1_MSLUT_2,
        Reg_Channel.MSLUT_3: Reg_TMC.M1_MSLUT_3,
        Reg_Channel.MSLUT_4: Reg_TMC.M1_MSLUT_4,
        Reg_Channel.MSLUT_5: Reg_TMC.M1_MSLUT_5,
        Reg_Channel.MSLUT_6: Reg_TMC.M1_MSLUT_6,
        Reg_Channel.MSLUT_7: Reg_TMC.M1_MSLUT_7,
        Reg_Channel.MSLUTSEL: Reg_TMC.M1_MSLUTSEL,
        Reg_Channel.MSLUTSTART: Reg_TMC.M1_MSLUTSTART,
        Reg_Channel.MSCNT: Reg_TMC.M1_MSCNT,
        Reg_Channel.MSCURACT: Reg_TMC.M1_MSCURACT,       
        Reg_Channel.CHOPCONF: Reg_TMC.M1_CHOPCONF,
        Reg_Channel.COOLCONF: Reg_TMC.M1_COOLCONF,
        Reg_Channel.DRV_STATUS: Reg_TMC.M1_DRV_STATUS
    }

    config_set_second:dict[Reg_Channel, Reg_TMC] = {
        Reg_Channel.GCONF: Reg_TMC.GCONF,
        Reg_Channel.GSTAT: Reg_TMC.GSTAT,
        Reg_Channel.TESTSEL: Reg_TMC.TESTSEL,
        Reg_Channel.INPUT: Reg_TMC.INPUT,
        Reg_Channel.X_COMPARE: Reg_TMC.X_COMPARE,
        Reg_Channel.RAMPMODE: Reg_TMC.M2_RAMPMODE,
        Reg_Channel.XACTUAL: Reg_TMC.M2_XACTUAL,
        Reg_Channel.VACTUAL: Reg_TMC.M2_VACTUAL,
        Reg_Channel.VSTART: Reg_TMC.M2_VSTART,
        Reg_Channel.A1: Reg_TMC.M2_A1,
        Reg_Channel.V1: Reg_TMC.M2_V1,
        Reg_Channel.AMAX: Reg_TMC.M2_AMAX,
        Reg_Channel.VMAX: Reg_TMC.M2_VMAX,
        Reg_Channel.DMAX: Reg_TMC.M2_DMAX,
        Reg_Channel.D1: Reg_TMC.M2_D1,
        Reg_Channel.VSTOP: Reg_TMC.M2_VSTOP,
        Reg_Channel.TZEROWAIT: Reg_TMC.M2_TZEROWAIT,
        Reg_Channel.XTARGET: Reg_TMC.M2_XTARGET,
        Reg_Channel.IHOLD_IRUN: Reg_TMC.M2_IHOLD_IRUN,
        Reg_Channel.VCOOLTHRS: Reg_TMC.M2_VCOOLTHRS,
        Reg_Channel.VHIGH: Reg_TMC.M2_VHIGH,
        Reg_Channel.SW_MODE: Reg_TMC.M2_SW_MODE,
        Reg_Channel.RAMP_STAT: Reg_TMC.M2_RAMP_STAT,
        Reg_Channel.XLATCH: Reg_TMC.M2_XLATCH,
        Reg_Channel.MSLUT_0: Reg_TMC.M2_MSLUT_0,
        Reg_Channel.MSLUT_1: Reg_TMC.M2_MSLUT_1,
        Reg_Channel.MSLUT_2: Reg_TMC.M2_MSLUT_2,
        Reg_Channel.MSLUT_3: Reg_TMC.M2_MSLUT_3,
        Reg_Channel.MSLUT_4: Reg_TMC.M2_MSLUT_4,
        Reg_Channel.MSLUT_5: Reg_TMC.M2_MSLUT_5,
        Reg_Channel.MSLUT_6: Reg_TMC.M2_MSLUT_6,
        Reg_Channel.MSLUT_7: Reg_TMC.M2_MSLUT_7,
        Reg_Channel.MSLUTSEL: Reg_TMC.M2_MSLUTSEL,
        Reg_Channel.MSLUTSTART: Reg_TMC.M2_MSLUTSTART,
        Reg_Channel.MSCNT: Reg_TMC.M2_MSCNT, 
        Reg_Channel.MSCURACT: Reg_TMC.M2_MSCURACT,       
        Reg_Channel.CHOPCONF: Reg_TMC.M2_CHOPCONF,
        Reg_Channel.COOLCONF: Reg_TMC.M2_COOLCONF,
        Reg_Channel.DRV_STATUS: Reg_TMC.M2_DRV_STATUS
    }

    class Channels(enum.IntEnum):
        first = 0
        second = 1

    class TMC_Chip(enum.IntEnum):
        first = 0
        second = 1
    
    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, offset_mode=i2c.I2COffsetMode.NoOffset, auto_lock=True, **kwargs)
        self._spi_gpio_cache = 0
        self._last_spi_status = 0

    def init_spi_bridge(self):    
        self.spi_bridge_config_spi(0x0c)  # 0x0c = ORDER=MSB first,  MODE0/1=CPHA=1, CPOL=1, F0/1(SPI_Clk)=1.8MHz
        self.spi_bridge_gpio_config(0x55) #  select all pins to Push-Pull output 
        self.spi_bridge_gpio_enable(Chip_TMC5031.SPI_Function_IDS.config_spi.slave_select_23) # activate DrvEn-Signal as GPIO 
        self.spi_bridge_gpio_write(0xff)  # Disable all (1 = off, 0 = on)

    def spi_bridge_write_byte(self, id: SPI_Function_IDS, val: int):
        self.write_bytes([id, val])

    def spi_bridge_read_byte(self, id: SPI_Function_IDS) -> int:
        self.write_byte(id)
        return self.read_byte()

    def spi_bridge_config_spi(self, val: int):
        self.spi_bridge_write_byte(Chip_TMC5031.SPI_Function_IDS.config_spi, val)

    def spi_bridge_clear_int(self):
        self.spi_bridge_write_byte(Chip_TMC5031.SPI_Function_IDS.clear_int, 0)

    def spi_bridge_set_idle_mode(self):
        self.spi_bridge_write_byte(Chip_TMC5031.SPI_Function_IDS.idle_mode, 0)

    def spi_bridge_gpio_write(self, val: int):
        self._spi_gpio_cache = val
        self.spi_bridge_write_byte(Chip_TMC5031.SPI_Function_IDS.gpio_write, self._spi_gpio_cache)

    def spi_bridge_gpio_read(self) -> int:
        return self.spi_bridge_read_byte(Chip_TMC5031.SPI_Function_IDS.gpio_read)

    def spi_bridge_gpio_enable(self, val: int):
        self.spi_bridge_write_byte(Chip_TMC5031.SPI_Function_IDS.gpio_enable, val)

    def spi_bridge_gpio_config(self, val: int):
        self.spi_bridge_write_byte(Chip_TMC5031.SPI_Function_IDS.gpio_config, val)

    def spi_bridge_write_buffer(self, id: SPI_Function_IDS, data: list[int]):
        buffer = [int(id)]
        buffer.extend(data)
        self.write_bytes(buffer)

    def spi_bridge_read_buffer(self, size: int) -> list[int]:
        return self.read_bytes(size)

    def motor_to_chip_ch(self, motor: int) -> tuple:
        chip = int(motor / 2)
        ch   = int(motor % 2)
        return (chip, ch)        

    def channel_to_tmc_reg(self, ch: Channels, reg: Reg_Channel) -> Reg_TMC:
        if ch == Chip_TMC5031.Channels.first:
            return Chip_TMC5031.config_set_first[reg]
        elif ch == Chip_TMC5031.Channels.second:
            return Chip_TMC5031.config_set_second[reg]
        assert False, f"Illegal channel number {ch}"

    def chip_to_spi_function_register(self, chip: TMC_Chip) -> SPI_Function_IDS:
        if chip == Chip_TMC5031.TMC_Chip.first:
            return Chip_TMC5031.SPI_Function_IDS.slave_select_0
        elif chip == Chip_TMC5031.TMC_Chip.second:
            return Chip_TMC5031.SPI_Function_IDS.slave_select_1
        assert False, f"Illegal chip number {chip}"

    def motor_driver_enable(self, motor: int, enable: bool):
        chip, ch = self.motor_to_chip_ch(motor)
        if  chip == Chip_TMC5031.TMC_Chip.first:
            id = Chip_TMC5031.SPI_Function_IDS.slave_select_2
        elif chip == Chip_TMC5031.TMC_Chip.second:
            id = Chip_TMC5031.SPI_Function_IDS.slave_select_3
        else:
            assert False, f"Illegal chip number {chip}"

        if enable:
            self.spi_bridge_gpio_write(self._spi_gpio_cache & (~id))
        else:
            self.spi_bridge_gpio_write(self._spi_gpio_cache | id)

    def is_motor_driver_enabled(self, motor: int) -> bool:
        chip, ch = self.motor_to_chip_ch(motor)
        if chip == Chip_TMC5031.TMC_Chip.first:
            id = Chip_TMC5031.SPI_Function_IDS.slave_select_2
        elif chip == Chip_TMC5031.TMC_Chip.second:
            id = Chip_TMC5031.SPI_Function_IDS.slave_select_3
        else:
            assert False, f"Illegal chip number {chip}"
        
        val = self.spi_bridge_gpio_read()
        return (val & (~id)) > 0

    def write_register(self, motor: int, reg: Reg_Channel, val: int, signed: bool = False): 
        chip, ch = self.motor_to_chip_ch(motor)
        buffer:list[int] = [self.channel_to_tmc_reg(ch, reg) | 0x80] # write access
        try:
            buffer.extend(val.to_bytes(4, byteorder='big', signed=signed))
            self.spi_bridge_write_buffer(self.chip_to_spi_function_register(chip), buffer)
        except OverflowError:
            print(f"value out of range error: '{val}'")

    def read_register(self, motor: int, reg: Reg_Channel, signed: bool = False) -> int:
        chip, ch = self.motor_to_chip_ch(motor)
        buffer:list[int] = [self.channel_to_tmc_reg(ch, reg)] # read access
        buffer.extend([0,0,0,0])

        # have to send it twice in order to get data from selected register, see TMC5031 data sheet for read access
        self.spi_bridge_write_buffer(self.chip_to_spi_function_register(chip), buffer)
        self.spi_bridge_write_buffer(self.chip_to_spi_function_register(chip), buffer)

        
        read_bytes = 5
        read_buffer = self.spi_bridge_read_buffer(read_bytes)
        assert len(read_buffer) == 5, f"Register read error. Assumed {read_bytes} bytes, but got {len(read_buffer)} bytes."
 
        self._last_spi_status = read_buffer[0]
        return int.from_bytes(read_buffer[1:], byteorder='big', signed=signed)

    def get_last_status(self) -> int:
        return self._last_spi_status

