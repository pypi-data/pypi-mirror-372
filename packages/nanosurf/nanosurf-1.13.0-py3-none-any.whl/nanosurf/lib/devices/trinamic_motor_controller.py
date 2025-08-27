
import pathlib
import enum
import typing
import xml.etree.ElementTree as xmldoc
import nanosurf.lib.devices.i2c.chip_TMC5031 as tmc

class MoveStatusFlags(enum.IntEnum): 
    Left_Switch_Active         = tmc.RampStatFlags.Stop_Left
    Right_Switch_Active        = tmc.RampStatFlags.Stop_Right
    IsNotMoving                = tmc.RampStatFlags.ZeroVelocity_Reached
    Left_Latched_Switch_Active = tmc.RampStatFlags.Stop_Left_Latched
    Right_Latched_Switch_Active = tmc.RampStatFlags.Stop_Right_Latched
    NONE = 0x00000000
    All  = (
        tmc.RampStatFlags.Stop_Left         | tmc.RampStatFlags.Stop_Right         |
        tmc.RampStatFlags.Stop_Left_Latched | tmc.RampStatFlags.Stop_Right_Latched |
        tmc.RampStatFlags.ZeroVelocity_Reached
    )
    OTHERS = 0xffffffff & (~All)

class LimitSwitchConfig(enum.IntEnum): # part of SWModeFlags
    Switch_Left_Enabled     = tmc.SWModeFlags.Switch_Left_Enabled
    Switch_Right_Enabled    = tmc.SWModeFlags.Switch_Right_Enabled
    Switch_Left_HighActive  = tmc.SWModeFlags.Switch_Left_HighActive
    Switch_Right_HighActive = tmc.SWModeFlags.Switch_Right_HighActive
    Swap_Left_Right_Switch  = tmc.SWModeFlags.Swap_Left_Right_Switch
    LatchPos_Left_Active    = tmc.SWModeFlags.LatchPos_Left_Active
    LatchPos_Left_Inactive  = tmc.SWModeFlags.LatchPos_Left_Inactive
    LatchPos_Right_Active   = tmc.SWModeFlags.LatchPos_Right_Active
    LatchPos_Right_Inactive = tmc.SWModeFlags.LatchPos_Right_Inactive
    NONE = 0x00000000
    All  = (
        tmc.SWModeFlags.Switch_Left_Enabled    | tmc.SWModeFlags.Switch_Right_Enabled    |
        tmc.SWModeFlags.Switch_Left_HighActive | tmc.SWModeFlags.Switch_Right_HighActive |
        tmc.SWModeFlags.Swap_Left_Right_Switch | 
        tmc.SWModeFlags.LatchPos_Left_Active   | tmc.SWModeFlags.LatchPos_Left_Inactive  |
        tmc.SWModeFlags.LatchPos_Right_Active  | tmc.SWModeFlags.LatchPos_Right_Inactive 
    )
    OTHERS = 0xffffffff & (~All)

class TrinamicMotorController(tmc.Chip_TMC5031):
    """ A stepper motor controller board based around the TMC3051 chip
        Multiple designs are build with different amount of motor drivers
    """
    
    #  usable for DriveAFM Approach Foot / DIMO Focus
    default_config:dict[tmc.Reg_Channel, int] = { 
        tmc.Reg_Channel.GCONF:0x08,
        tmc.Reg_Channel.X_COMPARE: 0,
        tmc.Reg_Channel.RAMPMODE: 0,
        tmc.Reg_Channel.XACTUAL: 0,
        tmc.Reg_Channel.VSTART: 0,
        tmc.Reg_Channel.A1: 32767,
        tmc.Reg_Channel.V1: 0,
        tmc.Reg_Channel.AMAX: 65535,
        tmc.Reg_Channel.VMAX: 0,
        tmc.Reg_Channel.DMAX: 65535,
        tmc.Reg_Channel.D1: 32767,
        tmc.Reg_Channel.VSTOP: 1,
        tmc.Reg_Channel.TZEROWAIT: 0,
        tmc.Reg_Channel.XTARGET: 0,
        tmc.Reg_Channel.IHOLD_IRUN: 0x00071f00,
        tmc.Reg_Channel.VCOOLTHRS: 0,
        tmc.Reg_Channel.VHIGH: 0,
        tmc.Reg_Channel.SW_MODE: 0x00000863,
        tmc.Reg_Channel.MSLUT_0: 0xaaaab554,
        tmc.Reg_Channel.MSLUT_1: 0x4a9554aa,
        tmc.Reg_Channel.MSLUT_2: 0x24492929,
        tmc.Reg_Channel.MSLUT_3: 0x10104222,
        tmc.Reg_Channel.MSLUT_4: 0xf8000000,
        tmc.Reg_Channel.MSLUT_5: 0xb5bb777d,
        tmc.Reg_Channel.MSLUT_6: 0x49295556,
        tmc.Reg_Channel.MSLUT_7: 0x80404222,
        tmc.Reg_Channel.MSLUTSEL: 0xffff9a06,
        tmc.Reg_Channel.MSLUTSTART: 0x00f80001,
        tmc.Reg_Channel.CHOPCONF: 0x101d5,
        tmc.Reg_Channel.COOLCONF: 0x0
    }

    def __init__(self, bus_addr: int, motors: int = 1, **kwargs):
        super().__init__(bus_addr, **kwargs)
        self._motors = motors

    def init_board(self, motors: int = 1, auto_config: bool = True, motor_config: dict[tmc.Reg_Channel, int] = default_config):
        self.init_spi_bridge()
        self._motors = motors
        for motor in range(self._motors):
            if auto_config:
                self.write_config(motor, motor_config) 
            self.set_current_position(0, motor)
            self.motor_driver_enable(motor, True)

    def write_config(self,  motor: int, motor_config: dict[tmc.Reg_Channel, int]):
        old_driver_state = self.is_motor_driver_enabled(motor)
        self.motor_driver_enable(motor, False)
        
        for reg, reg_val in motor_config.items():
            self.write_register(motor, reg, reg_val, signed=False)

        self.motor_driver_enable(motor, old_driver_state)

    def is_motor_moving(self, motor: int = 0) -> bool:
        reg_val = self.read_register(motor, tmc.Reg_Channel.RAMP_STAT) 
        return (reg_val & tmc.RampStatFlags.ZeroVelocity_Reached) == 0

    def is_limit_switch_active(self, motor: int = 0) -> bool:
        reg_val = self.read_register(motor, tmc.Reg_Channel.RAMP_STAT) 
        return (reg_val & (tmc.RampStatFlags.Stop_Left | tmc.RampStatFlags.Stop_Right)) > 0

    def motor_stop(self, motor: int = 0):
        self.write_register(motor, tmc.Reg_Channel.VMAX, 0)
        self.write_register(motor, tmc.Reg_Channel.XTARGET, 0)

    def get_current_position(self, motor: int = 0) -> int:
        return self.read_register(motor,tmc.Reg_Channel.XACTUAL, signed=True)

    def set_current_position(self, pos: int, motor: int = 0):
        self.write_register(motor,tmc.Reg_Channel.XACTUAL, int(pos), signed=True)

    def change_speed(self, speed: int, motor: int = 0):
        self.write_register(motor, tmc.Reg_Channel.VMAX, int(speed))

    def start_move_to_absolute(self, pos: int, speed: int, motor: int = 0):
        self.write_register(motor, tmc.Reg_Channel.XTARGET, int(pos))
        self.write_register(motor, tmc.Reg_Channel.VMAX, int(speed))

    def start_move_relative(self, pos: int, speed: int, motor: int = 0):
        cur_pos = self.get_current_position(motor)
        self.write_register(motor, tmc.Reg_Channel.XTARGET, int(cur_pos + pos), signed=True)
        self.write_register(motor, tmc.Reg_Channel.VMAX, int(speed), signed=False)

    def get_move_status(self, motor: int = 0) -> MoveStatusFlags:
        stat = self.read_register(motor, tmc.Reg_Channel.RAMP_STAT)
        return typing.cast(MoveStatusFlags, stat & MoveStatusFlags.All)

    def get_limit_switch_configuration(self, motor: int = 0) -> LimitSwitchConfig:
        sw_mode = self.read_register(motor, tmc.Reg_Channel.SW_MODE)
        return typing.cast(LimitSwitchConfig, sw_mode & LimitSwitchConfig.All) 

    def set_limit_switch_configuration(self, config:  LimitSwitchConfig,motor: int = 0):
        cur_val = self.read_register(motor, tmc.Reg_Channel.SW_MODE)
        self.write_register(motor, tmc.Reg_Channel.SW_MODE, (cur_val & LimitSwitchConfig.OTHERS) | (config & LimitSwitchConfig.All))
 
def from_normalized_speed(speed: float) -> int:
    """ convert normalized speed between 0 (stop) and 1.0 (max speed) to value of tmc register"""
    return int(min(max(0.0, speed), 1.0) * float((2**23)-512))

def to_normalize_speed(speed: int) -> float:
    """ convert tmc speed register value to normalized speed between 0 (stop) and 1.0 (max speed)"""
    return float(speed) / float((2**23)-512)

def from_normalized_signed_position(pos: float) -> int:
    """ convert normalized positions between -1.0 and +1.0 to value of tmc register"""
    return int(min(max(-1.0, pos), 1.0) * float((2**31)-1))

def to_normalized_signed_position(pos: int) -> float:
    """ convert tmc position register value to normalized position between -1.0 and +1.0"""
    return float(pos) / float((2**31)-1)

def read_motor_config_from_xml(file: pathlib.Path, set_id: int) -> dict[tmc.Reg_Channel, int]:
    
    def to_value(val_str: str) -> int:
        if "0x" in val_str:
            return int(val_str[2:], base=16)
        else:
            return int(val_str)

    config_dict :dict[tmc.Reg_Channel, int]= {}
    try:
        doc = xmldoc.parse(file)
        
        # search for set to load
        found_set = None
        sets = doc.findall("set")
        for cur_set in sets:
            id = int(cur_set.attrib["id"])
            if id == set_id:
                found_set = cur_set
                break

        # if desired set was found, load all register values into a dictionary
        if found_set is not None:
            regs = found_set.findall("register")
            for reg in regs:
                config_dict[int(reg.attrib['id'])] = to_value(reg.text)
    except Exception:
        pass
    return config_dict
