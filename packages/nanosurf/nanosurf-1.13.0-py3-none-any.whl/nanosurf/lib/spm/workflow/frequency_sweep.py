"""Frequency Sweep configuration and execution
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
from typing import Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
import time

from nanosurf.lib.spm.com_proxy import Spm
import nanosurf.lib.spm.studio as studio
try:
    from nanosurf.lib.spm.studio.wrapper.cmd_tree_spm import RootLu
except ImportError:
    pass
from nanosurf.lib.spm.lowlevel import check
from nanosurf.lib.spm.lowlevel import data_buffer
from nanosurf.lib.datatypes.sci_stream import SciStream
from nanosurf.lib.datatypes.sci_channel import SciChannel
from nanosurf.lib import plot as nsf_plot

class _ModulationOutput():
    def __init__(self, lu):
        self._lu = lu

    def __del__(self):
        pass

class _NormalExcitation(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._fast_out1 = self._lu.AnalogFastOut(self._lu.AnalogFastOut.Instance.EXCITATION)
        self._old_input = self._fast_out1.input.value
        self._fast_out1.input.value = self._fast_out1.InputChannels.Analyzer2_Reference

    def del_mobile_s(self):
        self._fast_out1.input.value = self._old_input
        super().__del__()

    def init_studio(self):
        self._lu:RootLu
        self._fast_out1 = self._lu.analog_fast_out.excitation
        self._old_input = self._fast_out1.attribute.input.value
        self._fast_out1.attribute.input.value = self._fast_out1.attribute.input.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu
        self._fast_out1.attribute.input.value = self._old_input


class _TipVoltage(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._fast_out2 = self._lu.AnalogFastOut(self._lu.AnalogFastOut.Instance.USER)
        self._hi_res_tip_voltage = self._lu.AnalogHiResOut(self._lu.AnalogHiResOut.Instance.TIPVOLTAGE)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_tip_voltage_modulation = self._hi_res_tip_voltage.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._hi_res_tip_voltage.modulation.value = (self._hi_res_tip_voltage.Modulation.Enabled)

    def del_mobile_s(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._hi_res_tip_voltage.modulation.value = self._old_tip_voltage_modulation
        super().__del__()

    def init_studio(self):
        self._lu:RootLu
        self._fast_out2 = self._lu.analog_fast_out.user
        self._hi_res_tip_voltage = self._lu.analog_hi_res_out.tip_voltage
        self._old_fast2_input = self._fast_out2.attribute.input.value
        self._old_tip_voltage_modulation = self._hi_res_tip_voltage.attribute.modulation.value
        self._fast_out2.attribute.input.value = self._fast_out2.attribute.input.ValueEnum.analyzer2_reference
        self._hi_res_tip_voltage.attribute.modulation.value = self._hi_res_tip_voltage.attribute.modulation.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu
        self._fast_out2.attribute.input.value = self._old_fast2_input
        self._hi_res_tip_voltage.attribute.modulation.value = self._old_tip_voltage_modulation

class _FastUser(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._fast_out2 = self._lu.AnalogFastOut(self._lu.AnalogFastOut.Instance.USER)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_fast2_analog = self._fast_out2.analog_output.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._fast_out2.analog_output.value = (self._fast_out2.AnalogOutput.Enabled)

    def del_mobile_s(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._fast_out2.analog_output.value = self._old_fast2_analog

    def init_studio(self):
        self._lu:RootLu
        self._fast_out2 = self._lu.analog_fast_out.user
        self._old_fast2_input = self._fast_out2.attribute.input.value
        self._old_fast2_analog = self._fast_out2.attribute.analog_output.value
        self._fast_out2.attribute.input.value = self._fast_out2.attribute.input.ValueEnum.analyzer2_reference
        self._fast_out2.attribute.analog_output.value = self._fast_out2.attribute.analog_output.ValueEnum.enabled

    def del_studio(self):
        self._lu:nsf.studio.spm.RootLu
        self._fast_out2.attribute.input.value = self._old_fast2_input
        self._fast_out2.attribute.analog_output.value = self._old_fast2_analog
 

class _OutUser1(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._fast_out2 = self._lu.AnalogFastOut(
            self._lu.AnalogFastOut.Instance.USER)
        self._hi_res_user_1 = self._lu.AnalogHiResOut(
            self._lu.AnalogHiResOut.Instance.USER1)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_hires4_modulation = self._hi_res_user_1.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._hi_res_user_1.modulation.value = (
                self._hi_res_user_1.Modulation.Enabled)

    def del_mobile_s(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._hi_res_user_1.modulation.value = self._old_hires4_modulation
        super().__del__()
    
    def init_studio(self):
        self._lu:RootLu
        self._fast_out2 = self._lu.analog_fast_out.user
        self._hi_res_user_1 = self._lu.analog_hi_res_out.user1
        self._old_fast2_input = self._fast_out2.attribute.input.value
        self._old_hires4_modulation = self._hi_res_user_1.attribute.modulation.value
        self._fast_out2.attribute.input.value = self._fast_out2.attribute.input.ValueEnum.analyzer2_reference
        self._hi_res_user_1.attribute.modulation.value = self._hi_res_user_1.attribute.modulation.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu        
        self._fast_out2.attribute.input.value = self._old_fast2_input
        self._hi_res_user_1.attribute.modulation.value = self._old_hires4_modulation

class _OutUser2(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._fast_out2 = self._lu.AnalogFastOut(
            self._lu.AnalogFastOut.Instance.USER)
        self._hi_res_user2 = self._lu.AnalogHiResOut(
            self._lu.AnalogHiResOut.Instance.USER2)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_user2_modulation = self._hi_res_user2.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._hi_res_user2.modulation.value = (
                self._hi_res_user2.Modulation.Enabled)

    def del_mobile_s(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._hi_res_user2.modulation.value = self._old_user2_modulation
        
    def init_studio(self):
        self._lu:RootLu
        self._fast_out2 = self._lu.analog_fast_out.user
        self._hi_res_user_2 = self._lu.analog_hi_res_out.user2
        self._old_fast2_input = self._fast_out2.attribute.input.value
        self._old_user2_modulation = self._hi_res_user_2.attribute.modulation.value
        self._fast_out2.attribute.input.value = self._fast_out2.attribute.input.ValueEnum.analyzer2_reference
        self._hi_res_user_2.attribute.modulation.value = self._hi_res_user_2.attribute.modulation.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu        
        self._fast_out2.attribute.input.value = self._old_fast2_input
        self._hi_res_user_2.attribute.modulation.value = self._old_user2_modulation


class _OutUser3(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._fast_out2 = self._lu.AnalogFastOut(
            self._lu.AnalogFastOut.Instance.USER)
        self._out_user3 = self._lu.AnalogHiResOut(
            self._lu.AnalogHiResOut.Instance.USER3)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_user3_modulation = self._out_user3.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._out_user3.modulation.value = (
                self._out_user3.Modulation.Enabled)

    def del_mobile_s(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._out_user3.modulation.value = self._old_user3_modulation

    def init_studio(self):
        self._lu:RootLu
        self._fast_out2 = self._lu.analog_fast_out.user
        self._hi_res_user_3 = self._lu.analog_hi_res_out.user3
        self._old_fast2_input = self._fast_out2.attribute.input.value
        self._old_user3_modulation = self._hi_res_user_3.attribute.modulation.value
        self._fast_out2.attribute.input.value = self._fast_out2.attribute.input.ValueEnum.analyzer2_reference
        self._hi_res_user_3.attribute.modulation.value = self._hi_res_user_3.attribute.modulation.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu        
        self._fast_out2.attribute.input.value = self._old_fast2_input
        self._hi_res_user_3.attribute.modulation.value = self._old_user3_modulation


class _OutUser4(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._fast_out2 = self._lu.AnalogFastOut(
            self._lu.AnalogFastOut.Instance.USER)
        self._monitor_out2 = self._lu.AnalogHiResOut(
            self._lu.AnalogHiResOut.Instance.USER4)
        self._old_fast2_input = self._fast_out2.input.value
        self._old_monitor2_modulation = self._monitor_out2.modulation.value
        self._fast_out2.input.value = self._fast_out2.InputChannels.Analyzer2_Reference
        self._monitor_out2.modulation.value = (
                self._monitor_out2.Modulation.Enabled)

    def del_mobile_s(self):
        self._fast_out2.input.value = self._old_fast2_input
        self._monitor_out2.modulation.value = self._old_monitor2_modulation

    def init_studio(self):
        self._lu:RootLu
        self._fast_out2 = self._lu.analog_fast_out.user
        self._monitor_out2 = self._lu.analog_hi_res_out.user4
        self._old_fast2_input = self._fast_out2.attribute.input.value
        self._old_user4_modulation = self._monitor_out2.attribute.modulation.value
        self._fast_out2.attribute.input.value = self._fast_out2.attribute.input.ValueEnum.analyzer2_reference
        self._monitor_out2.attribute.modulation.value = self._monitor_out2.attribute.modulation.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu        
        self._fast_out2.attribute.input.value = self._old_fast2_input
        self._monitor_out2.attribute.modulation.value = self._old_user4_modulation


class _OutPositionX(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._scan_x_out = self._lu.AnalogHiResOut(
                self._lu.AnalogHiResOut.Instance.POSITIONX)
        self._old_scan_x_out = self._scan_x_out.input.value
        self._scan_x_out.input.value = self._scan_x_out.InputChannels.Analyzer2_Reference

    def del_mobile_s(self):
        self._scan_x_out.input.value = self._old_scan_x_out

    def init_studio(self):
        self._lu:RootLu
        self._scan_x_out = self._lu.analog_hi_res_out.position_x
        self._old_scan_x_out = self._scan_x_out.attribute.input.value
        self._scan_x_out.attribute.input.value = self._scan_x_out.attribute.input.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu        
        self._scan_x_out.attribute.input.value = self._old_scan_x_out
 

class _OutPositionY(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._scan_y_out = self._lu.AnalogHiResOut(
                self._lu.AnalogHiResOut.Instance.POSITIONY)
        self._old_scan_y_out = self._scan_y_out.input.value
        self._scan_y_out.input.value = self._scan_y_out.InputChannels.Analyzer2_Reference

    def del_mobile_s(self):
        self._scan_y_out.input.value = self._old_scan_y_out

    def init_studio(self):
        self._lu:RootLu
        self._scan_y_out = self._lu.analog_hi_res_out.position_y
        self._old_scan_y_out = self._scan_y_out.attribute.input.value
        self._scan_y_out.attribute.input.value = self._scan_y_out.attribute.input.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu        
        self._scan_y_out.attribute.input.value = self._old_scan_y_out


class _OutPositionZ(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._hi_res_pos_out_z = self._lu.AnalogHiResOut(
            self._lu.AnalogHiResOut.Instance.POSITIONZ)
        self._old_posz_input = self._hi_res_pos_out_z.input.value
        self._hi_res_pos_out_z.input.value = (
                self._hi_res_pos_out_z.InputChannels.Analyzer2_Reference)

    def del_mobile_s(self):
        self._hi_res_pos_out_z.input.value = self._old_posz_input

    def init_studio(self):
        self._lu:RootLu
        self._hi_res_pos_out_z = self._lu.analog_hi_res_out.position_z
        self._old_posz_input = self._hi_res_pos_out_z.attribute.input.value
        self._hi_res_pos_out_z.attribute.input.value = self._hi_res_pos_out_z.attribute.input.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu        
        self._hi_res_pos_out_z.attribute.input.value = self._old_posz_input


class _ModOutZ(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._hi_res_pos_out_z = self._lu.AnalogHiResOut(
            self._lu.AnalogHiResOut.Instance.POSITIONZ)
        self._old_posz_modulation = self._hi_res_pos_out_z.modulation.value
        self._hi_res_pos_out_z.modulation.value = (
                self._hi_res_pos_out_z.Modulation.Enabled)

    def del_mobile_s(self):
        self._hi_res_pos_out_z.modulation.value = self._old_posz_modulation
        super().__del__()

    def init_studio(self):
        self._lu:RootLu
        self._hi_res_pos_out_z = self._lu.analog_hi_res_out.position_z
        self._old_posz_modulation = self._hi_res_pos_out_z.attribute.modulation.value
        self._hi_res_pos_out_z.attribute.modulation.value = self._hi_res_pos_out_z.attribute.modulation.ValueEnum.analyzer2_reference

    def del_studio(self):
        self._lu:RootLu        
        self._hi_res_pos_out_z.attribute.modulation.value = self._old_posz_modulation
 

class _ModXControlSet(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._pid_control = self._lu.PIDController(self._lu.PIDController.Instance.PIDX)
        try:
            self._old_value = self._pid_control.set_point_modulation_enable.value
            self._pid_control.set_point_modulation_enable.value = (
                self._pid_control.Enable.Enabled)
            self.new_style = True
        except:
            self._old_value = self._pid_control.select_sweep.value
            self._pid_control.select_sweep.value = (
                self._pid_control.SelectSweep.Selected)
            self.new_style = False


    def del_mobile_s(self):
        if self.new_style:
            self._pid_control.set_point_modulation_enable.value = self._old_value
        else:
            self._pid_control.select_sweep.value = self._old_value

    def init_studio(self):
        self._lu:RootLu
        self._pid_control = self._lu.pid_controller.pid_x
        self._old_value = self._pid_control.attribute.set_point_modulation_enable.value
        self._pid_control.attribute.set_point_modulation_enable.value = self._pid_control.attribute.set_point_modulation_enable.ValueEnum.enabled

    def del_studio(self):
        self._lu:RootLu        
        self._pid_control.attribute.set_point_modulation_enable.value = self._old_value


class _ModYControlSet(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._pid_control = self._lu.PIDController(self._lu.PIDController.Instance.PIDY)
        try:
            self._old_value = self._pid_control.set_point_modulation_enable.value
            self._pid_control.set_point_modulation_enable.value = (
                self._pid_control.Enable.Enabled)
            self.new_style = True
        except:
            self._old_value = self._pid_control.select_sweep.value
            self._pid_control.select_sweep.value = (
                self._pid_control.SelectSweep.Selected)
            self.new_style = False

    def del_mobile_s(self):
        if self.new_style:
            self._pid_control.set_point_modulation_enable.value = self._old_value
        else:
            self._pid_control.select_sweep.value = self._old_value

    def init_studio(self):
        self._lu:RootLu
        self._pid_control = self._lu.pid_controller.pid_y
        self._old_value = self._pid_control.attribute.set_point_modulation_enable.value
        self._pid_control.attribute.set_point_modulation_enable.value = self._pid_control.attribute.set_point_modulation_enable.ValueEnum.enabled

    def del_studio(self):
        self._lu:RootLu        
        self._pid_control.attribute.set_point_modulation_enable.value = self._old_value

class _ModZControlSet(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._pid_control = self._lu.ZControllerEx()
        try:
            self._old_value = self._pid_control.set_point_modulation_enable.value
            self._pid_control.set_point_modulation_enable.value = (
                self._pid_control.Enable.Enabled)
            self.new_style = True
        except:
            self._old_value = self._pid_control.select_sweep.value
            self._pid_control.select_sweep.value = (
                self._pid_control.SelectSweep.Selected)
            self.new_style = False

    def del_mobile_s(self):
        if self.new_style:
            self._pid_control.set_point_modulation_enable.value = self._old_value
        else:
            self._pid_control.select_sweep.value = self._old_value

    def init_studio(self):
        self._lu:RootLu
        self._pid_control = self._lu.z_controller_ex.instance
        self._old_value = self._pid_control.attribute.set_point_modulation_enable.value
        self._pid_control.attribute.set_point_modulation_enable.value = self._pid_control.attribute.set_point_modulation_enable.ValueEnum.enabled

    def del_studio(self):
        self._lu:RootLu        
        self._pid_control.attribute.set_point_modulation_enable.value = self._old_value


class _ModZControlOutput(_ModulationOutput):
    def __init__(self, lowlevel):
        super().__init__(lowlevel)
        if check.is_studio(self._lu):
            self.init_studio()
        else:
            self.init_mobile_s()    

    def __del__(self):
        if check.is_studio(self._lu):
            self.del_studio()
        else:
            self.del_mobile_s()
        super().__del__()

    def init_mobile_s(self):
        self._pid_control = self._lu.ZControllerEx()
        try:
            self._old_value = self._pid_control.output_modulation_enable.value
            self._pid_control.output_modulation_enable.value = (
                self._pid_control.Enable.Enabled)
            self.new_style = True
        except:
            self._old_value = self._pid_control.select_sweep.value
            self._pid_control.select_sweep.value = (
                self._pid_control.SelectSweep.Selected)
            self.new_style = False

    def del_mobile_s(self):
        if self.new_style:
            self._pid_control.output_modulation_enable.value = self._old_value
        else:
            self._pid_control.select_sweep.value = self._old_value

    def init_studio(self):
        self._lu:RootLu
        self._pid_control = self._lu.z_controller_ex.instance
        self._old_value = self._pid_control.attribute.output_modulation_enable.value
        self._pid_control.attribute.output_modulation_enable.value = self._pid_control.attribute.output_modulation_enable.ValueEnum.enabled

    def del_studio(self):
        self._lu:RootLu        
        self._pid_control.attribute.output_modulation_enable.value = self._old_value

class FrequencySweepOutput(enum.IntEnum):
    """Enumeration for the modulation output selection"""
    Normal_Excitation = 0
    FastUser_OutB = 1 
    TipVoltage_UserOutA = 2
    UserOut1_UserC = 3
    UserOut2_UserA = 4
    UserOut3_Monitor1 = 5
    UserOut4_Monitor2 = 6
    PositionX = 7
    PositionY = 8
    PositionZ = 9
    ModOutZ = 10
    ModXControlSet = 11
    ModYControlSet = 12
    ModZControlSet = 13
    ModZControlOutput = 14

class InputSource(enum.IntEnum):
    Deflection = 0
    Fast2_CX = 1
    Fast_User_CX = 2
    Friction = 3
    UserIn1 = 4
    UserIn2_UserB = 5
    UserIn3_UserA = 6
    UserIn4_CX = 7
    TipCurrent = 8
    TestGND_C3000 = 9
    TesRef_C3000 = 10
    TestMixedOut3_C3000 = 11
    AxisInX = 12
    AxisInY = 13
    AxisInZ = 14
    MainLockIn_Amplitude = 15
    MainPLL_FreqShift = 16
    ZControllerOut = 17
    InDetectorSum = 18
    In6 = 19
    CtrlX_Out = 20
    CtrlY_Out = 21
    CtrlW_Out = 22
    CtrlUser1_Out = 23
    CtrlUser2_Out = 24
    Analyzer1_CtrlDeltaF = 25
    Analyzer1_CtrlAmplitude = 26
    Analyzer1_Phase = 27
    Analyzer1_Amplitude = 28
    Analyzer1_X = 29
    Analyzer1_Y = 30
    Ort_Baseline = 31
    Ort_AmplitudeReduction = 32
    Ort_Excitation = 33

class InputRanges(enum.IntEnum):
    Full = 0
    OneOverFour = 1
    OneOverSixteen = 2

class Bandwidths(enum.IntEnum):
    Hz_23 = 0,
    Hz_45 = 1,
    Hz_90 = 2,
    Hz_180 = 3,
    Hz_360 = 4,
    Hz_740 = 5,
    Hz_1500 = 6,
    Hz_3000 = 7,
    Hz_6000 = 8,
    Hz_12k = 9,
    Hz_24k= 10,
    Hz_48k = 11,
    Hz_100k = 12,
    Hz_230k = 13,
    Hz_500k = 14


class AbstractSPM():
    def __init__(self) -> None:
        pass

class StudioAbstraction(AbstractSPM):
    class StudioBufferState(enum.IntEnum):
        invalid = 0
        trimmed = 1
        synchronizing = 2
        synchronized = 3

    def __init__(self, studio:studio.Studio) -> None:
        super().__init__()
        self.data_channel_amplitude = 0
        self.data_channel_phase = 1
        self._studio = studio
        self._spm = studio.spm
        self._lu = studio.spm.lu
        self._data_buffer = data_buffer.DataBufferAccess(self._studio)
        self._analyzer = self._lu.signal_analyzer.inst2
        self._system_infra = self._lu.system_infra.instance
        self._frequency_sweep_generator = self._lu.frequency_sweep_gen.instance

    def __del__(self):
        self._lu = None
        self._spm = None
        
    def init_input_source_map(self):
        analyzer_input = self._analyzer.attribute.input
        self.input_sources_to_lu_map: dict[InputSource, self._analyzer.attribute.input.ValueEnum] = {
            # LUSignalAnalyzer_Input
            InputSource.Deflection: analyzer_input.ValueEnum.fast_in_deflection,
            InputSource.Fast2_CX: analyzer_input.ValueEnum.fast_in2,
            InputSource.Fast_User_CX: analyzer_input.ValueEnum.fast_in_user,
            InputSource.Friction: analyzer_input.ValueEnum.in_lateral,
            InputSource.UserIn1: analyzer_input.ValueEnum.in_user1,
            InputSource.UserIn2_UserB: analyzer_input.ValueEnum.in_user2,
            InputSource.UserIn3_UserA: analyzer_input.ValueEnum.in_user3,
            InputSource.UserIn4_CX: analyzer_input.ValueEnum.in_user4,
            InputSource.TipCurrent: analyzer_input.ValueEnum.in_tip_current,
            InputSource.AxisInX: analyzer_input.ValueEnum.in_position_x,
            InputSource.AxisInY: analyzer_input.ValueEnum.in_position_y,
            InputSource.AxisInZ: analyzer_input.ValueEnum.in_position_z,
            InputSource.MainLockIn_Amplitude: analyzer_input.ValueEnum.analyzer1_amplitude,
            InputSource.MainPLL_FreqShift: analyzer_input.ValueEnum.analyzer1_ctrl_delta_f,
            InputSource.ZControllerOut: analyzer_input.ValueEnum.ctrl_z_out,
            InputSource.Ort_AmplitudeReduction: analyzer_input.ValueEnum.ort_amplitude_reduction,
            InputSource.InDetectorSum : analyzer_input.ValueEnum.in_detector_sum,
            InputSource.In6 : analyzer_input.ValueEnum.in6,
            InputSource.CtrlX_Out : analyzer_input.ValueEnum.ctrl_x_out,
            InputSource.CtrlY_Out : analyzer_input.ValueEnum.ctrl_y_out,
            InputSource.CtrlW_Out : analyzer_input.ValueEnum.ctrl_w_out,
            InputSource.CtrlUser1_Out : analyzer_input.ValueEnum.ctrl_user1_out,
            InputSource.CtrlUser2_Out : analyzer_input.ValueEnum.ctrl_user2_out,
            InputSource.Analyzer1_CtrlDeltaF : analyzer_input.ValueEnum.analyzer1_ctrl_delta_f,
            InputSource.Analyzer1_CtrlAmplitude : analyzer_input.ValueEnum.analyzer1_ctrl_amplitude,
            InputSource.Analyzer1_Amplitude : analyzer_input.ValueEnum.analyzer1_amplitude,
            InputSource.Analyzer1_Phase : analyzer_input.ValueEnum.analyzer1_phase,
            InputSource.Analyzer1_X : analyzer_input.ValueEnum.analyzer1_x,
            InputSource.Analyzer1_Y : analyzer_input.ValueEnum.analyzer1_y,
            InputSource.Ort_Baseline : analyzer_input.ValueEnum.ort_baseline,
            InputSource.Ort_AmplitudeReduction : analyzer_input.ValueEnum.ort_amplitude_reduction,
            InputSource.Ort_Excitation : analyzer_input.ValueEnum.ort_excitation,
        }

    def init_input_range_map(self):
        self.input_range_to_gain_map: dict[InputRanges, float] = {
            InputRanges.Full:           self._system_infra.attribute.main_in2_gain.ValueEnum.gain1,
            InputRanges.OneOverFour:    self._system_infra.attribute.main_in2_gain.ValueEnum.gain4,
            InputRanges.OneOverSixteen: self._system_infra.attribute.main_in2_gain.ValueEnum.gain16
        }

    def init_bandwidth_map(self):
        self.bandwidths_to_lu_map : dict[Bandwidths, int] = {
            # LUSignalAnalyzer_DemodulatorBW
            Bandwidths.Hz_23 : self._analyzer.attribute.demodulator_bw.ValueEnum.bw_23_hz,
            Bandwidths.Hz_45: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_45_hz,
            Bandwidths.Hz_90: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_90_hz,
            Bandwidths.Hz_180: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_180_hz,
            Bandwidths.Hz_360: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_360_hz,
            Bandwidths.Hz_740: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_750_hz,
            Bandwidths.Hz_1500: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_1500_hz,
            Bandwidths.Hz_3000: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_3_k_hz,
            Bandwidths.Hz_6000: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_6_k_hz,
            Bandwidths.Hz_12k: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_12_k_hz,
            Bandwidths.Hz_24k: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_23_k_hz,
            Bandwidths.Hz_48k: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_45_k_hz,
            Bandwidths.Hz_100k: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_100_k_hz,
            Bandwidths.Hz_230k: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_230_k_hz,
            Bandwidths.Hz_500k: self._analyzer.attribute.demodulator_bw.ValueEnum.bw_500_k_hz,
        }

    def start(self, start_frequency: float, end_frequency: float, points: int,
                    step_time: float, settle_time: float, amplitude: float, reference_phase:float, input_source:InputSource, input_range:InputRanges):

        self._analyzer.attribute.operating_mode.value = self._analyzer.attribute.operating_mode.ValueEnum.lock_in
        self._analyzer.attribute.reference_phase.value = reference_phase
        self._analyzer.attribute.input.value = self.input_sources_to_lu_map[input_source]
        self._system_infra.attribute.main_in2_gain.value = self.input_range_to_gain_map[input_range]
        max_amp = self._analyzer.attribute.current_reference_amplitude.max
        self._start_freq = start_frequency
        self._end_freq = end_frequency
        self._data_points = points

        limited_step_time = max(step_time, 0.01)

        sweep_gen = self._frequency_sweep_generator
        sweep_gen.attribute.lu_sig_analyzer_inst_no.value = sweep_gen.attribute.lu_sig_analyzer_inst_no.ValueEnum.inst2
        sweep_gen.attribute.data_group_id.value = self._data_buffer.group_id
        sweep_gen.attribute.start_frequency.value = self._start_freq
        sweep_gen.attribute.end_frequency.value = self._end_freq
        sweep_gen.attribute.data_points.value = self._data_points

        # Settle time before starting the measurement...
        sweep_gen.attribute.settle_time.value = settle_time
        sweep_gen.attribute.step_time.value = limited_step_time
        sweep_gen.attribute.sweep_amplitude.value = amplitude * max_amp
        sweep_gen.trigger.start_frequency_sweep()

    def abort(self):
        self._frequency_sweep_generator.trigger.user_abort()

    def get_current_sweep_frequency(self) -> float:
        cur_freq = self._analyzer.attribute.reference_frequency.value
        return cur_freq

class SPMAbstraction(AbstractSPM):
    def __init__(self, spm:Spm) -> None:
        super().__init__()
        self.data_channel_amplitude = 2
        self.data_channel_phase = 3
        self._spm = spm
        self._lu = self._spm.lu
        self._data_buffer = data_buffer.DataBufferAccess(self._spm)
        self._analyzer = self._lu.SignalAnalyzer(self._lu.SignalAnalyzer.Instance.INST2)
        self._system_infra = self._lu.SystemInfra()
        self._frequency_sweep_generator = self._lu.FrequencySweepGen()

    def __del__(self):
        self._lu = None
        self._spm = None
        
    def init_input_source_map(self):
        self.input_sources_to_lu_map: dict[InputSource, int] = {
            InputSource.Deflection: self._analyzer.Input.FastInDeflection,
            InputSource.Fast2_CX: self._analyzer.Input.FastIn2,
            InputSource.Fast_User_CX: self._analyzer.Input.FastInUser,
            InputSource.Friction: self._analyzer.Input.InLateral,
            InputSource.UserIn1: self._analyzer.Input.InUser1,
            InputSource.UserIn2_UserB: self._analyzer.Input.InUser2,
            InputSource.UserIn3_UserA: self._analyzer.Input.InUser3,
            InputSource.UserIn4_CX: self._analyzer.Input.InUser4,
            InputSource.TipCurrent: self._analyzer.Input.InTipCurrent,
            InputSource.TestGND_C3000: self._analyzer.Input.Test_AnaGND,
            InputSource.TesRef_C3000: self._analyzer.Input.Test_Ref,
            InputSource.TestMixedOut3_C3000: self._analyzer.Input.Test_TipVoltage,
            InputSource.AxisInX: self._analyzer.Input.InPositionX,
            InputSource.AxisInY: self._analyzer.Input.InPositionY,
            InputSource.AxisInZ: self._analyzer.Input.InPositionZ,
            InputSource.MainLockIn_Amplitude: self._analyzer.Input.Analyzer1_Amplitude,
            InputSource.MainPLL_FreqShift: self._analyzer.Input.Analyzer1_CtrlDeltaF,
            InputSource.ZControllerOut: self._analyzer.Input.CtrlZ_Out,
            InputSource.InDetectorSum : self._analyzer.Input.InDetectorSum,
            InputSource.In6 : self._analyzer.Input.In6,
            InputSource.CtrlX_Out : self._analyzer.Input.CtrlX_Out,
            InputSource.CtrlY_Out : self._analyzer.Input.CtrlY_Out,
            InputSource.CtrlW_Out : self._analyzer.Input.CtrlW_Out,
            InputSource.CtrlUser1_Out : self._analyzer.Input.CtrlUser1_Out,
            InputSource.CtrlUser2_Out : self._analyzer.Input.CtrlUser2_Out,
            InputSource.Analyzer1_CtrlDeltaF : self._analyzer.Input.Analyzer1_CtrlDeltaF,
            InputSource.Analyzer1_CtrlAmplitude : self._analyzer.Input.Analyzer1_CtrlAmplitude,
            InputSource.Analyzer1_Amplitude : self._analyzer.Input.Analyzer1_Amplitude,
            InputSource.Analyzer1_Phase : self._analyzer.Input.Analyzer1_Phase,
            InputSource.Analyzer1_X : self._analyzer.Input.Analyzer1_X,
            InputSource.Analyzer1_Y : self._analyzer.Input.Analyzer1_Y,
            InputSource.Ort_Baseline : self._analyzer.Input.Ort_Baseline,
            InputSource.Ort_AmplitudeReduction : self._analyzer.Input.Ort_AmplitudeReduction,
            InputSource.Ort_Excitation : self._analyzer.Input.Ort_Excitation,
        }

    def init_input_range_map(self):
        self.input_range_to_gain_map: dict[InputRanges, float] = {
            InputRanges.Full:           self._system_infra.main_in_2_gain.value_min,
            InputRanges.OneOverFour:    self._system_infra.main_in_2_gain.value_max / self._system_infra.main_in_2_gain.value_max,
            InputRanges.OneOverSixteen: self._system_infra.main_in_2_gain.value_max
        }

    def init_bandwidth_map(self):
        self.bandwidths_to_lu_map : dict[Bandwidths, int] = {
            Bandwidths.Hz_23 : self._analyzer.DemodulatorBW.BW_23Hz,
            Bandwidths.Hz_45: self._analyzer.DemodulatorBW.BW_45Hz,
            Bandwidths.Hz_90: self._analyzer.DemodulatorBW.BW_90Hz,
            Bandwidths.Hz_180: self._analyzer.DemodulatorBW.BW_180Hz,
            Bandwidths.Hz_360: self._analyzer.DemodulatorBW.BW_360Hz,
            Bandwidths.Hz_740: self._analyzer.DemodulatorBW.BW_750Hz,
            Bandwidths.Hz_1500: self._analyzer.DemodulatorBW.BW_1500Hz,
            Bandwidths.Hz_3000: self._analyzer.DemodulatorBW.BW_3kHz,
            Bandwidths.Hz_6000: self._analyzer.DemodulatorBW.BW_6kHz,
            Bandwidths.Hz_12k: self._analyzer.DemodulatorBW.BW_12kHz,
            Bandwidths.Hz_24k: self._analyzer.DemodulatorBW.BW_23kHz,
            Bandwidths.Hz_48k: self._analyzer.DemodulatorBW.BW_45kHz,
            Bandwidths.Hz_100k: self._analyzer.DemodulatorBW.BW_100kHz,
            Bandwidths.Hz_230k: self._analyzer.DemodulatorBW.BW_230kHz,
            Bandwidths.Hz_500k: self._analyzer.DemodulatorBW.BW_500kHz,
        }

    def start(self, start_frequency: float, end_frequency: float, points: int,
            step_time: float, settle_time: float, amplitude: float, reference_phase:float, input_source:InputSource, input_range:InputRanges):
        self._start_freq = start_frequency
        self._end_freq = end_frequency
        self._data_points = points

        self._analyzer.operating_mode.value = self._analyzer.OperatingMode.LockIn
        self._analyzer.reference_phase.value = reference_phase
        self._analyzer.input.value = self.input_sources_to_lu_map[input_source]
        self._system_infra.main_in_2_gain.value = self.input_range_to_gain_map[input_range]
        max_amp = self._analyzer.current_reference_amplitude.value_max

        limited_step_time = max(step_time, 0.01)

        sweep_gen = self._frequency_sweep_generator
        sweep_gen.lusig_analyzer_inst_no.value = (sweep_gen.LUSigAnalyzerInstNo.INST2)

        sweep_gen.data_group_id.value = self._data_buffer.group_id

        sweep_gen.start_frequency.value = self._start_freq
        sweep_gen.end_frequency.value = self._end_freq
        sweep_gen.data_points.value = self._data_points

        # Settle time before starting the measurement...
        sweep_gen.settle_time.value = settle_time
        sweep_gen.step_time.value = limited_step_time
        sweep_gen.sweep_amplitude.value = amplitude * max_amp
        sweep_gen.start_frequency_sweep()

    def abort(self):
        self._frequency_sweep_generator.user_abort()

    def get_current_sweep_frequency(self) -> float:
        cur_freq =  self._analyzer.reference_frequency.value
        return cur_freq

class FrequencySweep():
    """Workflow for acquiring and plotting frequency sweeps."""

    # Output = enum.Enum('Output', {
    Output = {
        FrequencySweepOutput.Normal_Excitation: _NormalExcitation,
        FrequencySweepOutput.FastUser_OutB: _FastUser,
        FrequencySweepOutput.TipVoltage_UserOutA: _TipVoltage,
        FrequencySweepOutput.UserOut1_UserC: _OutUser1,
        FrequencySweepOutput.UserOut2_UserA: _OutUser2,
        FrequencySweepOutput.UserOut3_Monitor1: _OutUser3,
        FrequencySweepOutput.UserOut4_Monitor2: _OutUser4,
        FrequencySweepOutput.PositionX: _OutPositionX,
        FrequencySweepOutput.PositionY: _OutPositionY,
        FrequencySweepOutput.PositionZ: _OutPositionZ,
        FrequencySweepOutput.ModOutZ: _ModOutZ,
        FrequencySweepOutput.ModXControlSet: _ModXControlSet,
        FrequencySweepOutput.ModYControlSet: _ModYControlSet,
        FrequencySweepOutput.ModZControlSet: _ModZControlSet,
        FrequencySweepOutput.ModZControlOutput: _ModZControlOutput
        }

    input_sources_names: dict[InputSource, str] = {
        InputSource.Deflection : "Deflection",
        InputSource.Fast2_CX :  "Fast2 (CX)",
        InputSource.Fast_User_CX : "Fast User (CX)",
        InputSource.Friction : "Friction",
        InputSource.UserIn1: "User In 1",
        InputSource.UserIn2_UserB : "User In 2 / B",
        InputSource.UserIn3_UserA : "User In 3 / A",
        InputSource.UserIn4_CX : "User In 4 (CX)",
        InputSource.TipCurrent : "TipCurrent",
        InputSource.TestGND_C3000 : "Test GND (C3000)",
        InputSource.TesRef_C3000 : "Test Ref (C3000)",
        InputSource.TestMixedOut3_C3000 : "Test MixedOut3 (C3000)",
        InputSource.AxisInX : "Axis In X",
        InputSource.AxisInY : "Axis In Y",
        InputSource.AxisInZ : "Axis In Z",
        InputSource.MainLockIn_Amplitude : "Main Lock-In Amplitude",
        InputSource.MainPLL_FreqShift : "Main PLL Frequency Shift",
        InputSource.ZControllerOut : "Z-Controller Out",
        InputSource.InDetectorSum : "Detector Sum",
        InputSource.In6 : "Interface Aux Input",
        InputSource.CtrlX_Out : "X-Controller Out",
        InputSource.CtrlY_Out : "Y-Controller Out",
        InputSource.CtrlW_Out : "W-Controller Out",
        InputSource.CtrlUser1_Out : "Controller User 1 Out",
        InputSource.CtrlUser2_Out : "Controller User 2 Out",
        InputSource.Analyzer1_CtrlDeltaF : "Analyzer 1 Ctrl. Delta f",
        InputSource.Analyzer1_CtrlAmplitude : "Analyzer 1 Ctrl. Amp.",
        InputSource.Analyzer1_Amplitude : "Analyzer 1 Amplitude",
        InputSource.Analyzer1_Phase : "Analyzer 1 Phase",
        InputSource.Analyzer1_X : "Analyzer 1 X",
        InputSource.Analyzer1_Y : "Analyzer 1 Y",
        InputSource.Ort_Baseline : "WaveMode Baseline",
        InputSource.Ort_AmplitudeReduction : "WaveMode Amplitude Reduction",
        InputSource.Ort_Excitation : "WaveMode Excitation",
    }

    bandwidths_names = {
        Bandwidths.Hz_23: "23Hz",
        Bandwidths.Hz_45:"45Hz",
        Bandwidths.Hz_90:"90Hz",
        Bandwidths.Hz_180:"180Hz",
        Bandwidths.Hz_360:"360Hz",
        Bandwidths.Hz_740:"740Hz",
        Bandwidths.Hz_1500:"1500Hz",
        Bandwidths.Hz_3000:"3kHz",
        Bandwidths.Hz_6000:"6kHz",
        Bandwidths.Hz_12k:"12kHz",
        Bandwidths.Hz_24k:"23kHz",
        Bandwidths.Hz_48k:"45kHz",
        Bandwidths.Hz_100k:"100kHz",
        Bandwidths.Hz_230k:"230kHz",
        Bandwidths.Hz_500k:"500kHz"
    }

    input_ranges_names: dict[InputRanges,str] = {
        InputRanges.Full:           "Full",
        InputRanges.OneOverFour:    "1/4",
        InputRanges.OneOverSixteen: "1/16"
    }

    output_names: dict[FrequencySweepOutput, str] = {
        FrequencySweepOutput.Normal_Excitation:"Normal Excitation",
        FrequencySweepOutput.FastUser_OutB: "Fast User / Out B",
        FrequencySweepOutput.TipVoltage_UserOutA:"Tip Voltage / User Out A",
        FrequencySweepOutput.UserOut1_UserC:"User 1 / C",
        FrequencySweepOutput.UserOut2_UserA:"User 2 / A",
        FrequencySweepOutput.UserOut3_Monitor1:"User 3 / Monitor 1",
        FrequencySweepOutput.UserOut4_Monitor2:"User 4 / Monitor 2",
        FrequencySweepOutput.PositionX:"X Position",
        FrequencySweepOutput.PositionY:"Y Position",
        FrequencySweepOutput.PositionZ:"PosOutZ",
        FrequencySweepOutput.ModOutZ:"ModOutZ",
        FrequencySweepOutput.ModXControlSet:"ModXControlSet",
        FrequencySweepOutput.ModYControlSet:"ModYControlSet",
        FrequencySweepOutput.ModZControlSet:"ModZControlSet",
        FrequencySweepOutput.ModZControlOutput:"ModZControlOutput"
    }

    def __init__(self, spm_root:Union[studio.Studio, Spm]):
        self.is_busy = False
        self.output_setup = None
        self.data_group_name = "Frequency sweep"
        self._internal_transfer_time = 5.0

        self._spm = spm_root
        if spm_root.is_studio:
            self.spm_hal = StudioAbstraction(self._spm)
        else:
            self.spm_hal = SPMAbstraction(self._spm)

        self.spm_hal.init_input_source_map()
        self.spm_hal.init_input_range_map()
        self.spm_hal.init_bandwidth_map()

    def __del__(self):
        if self.output_setup is not None:
            del self.output_setup

    def _read_data_buffer(self) -> SciStream:
        """Returns transfer function and frequencies of the measurement"""
        
        self.spm_hal._data_buffer.transfer_data_buffer()

        # read back measured data and scale to physical unit 
        print("Read data buffer")
        ch_amp   = self.spm_hal._data_buffer.read_channel(self.spm_hal.data_channel_amplitude)
        ch_phase_raw = self.spm_hal._data_buffer.read_channel(self.spm_hal.data_channel_phase)
        
        ch_phase_unwrapped = SciChannel(ch_phase_raw)
        ch_phase_unwrapped.value = np.unwrap(ch_phase_raw.value, discont=180)

        measured_data_points = len(ch_amp.value)
        print(f"measured data = {measured_data_points}")

        frequencies = np.linspace(self._start_freq, self._end_freq, self._data_points, endpoint=True)
        frequencies = frequencies[:measured_data_points]

        result_stream = SciStream(frequencies, channels=2, x_name="Frequency", x_unit="Hz")
        result_stream.channels[0] = ch_amp
        result_stream.channels[1] = ch_phase_unwrapped
        return result_stream

    def _start(
            self, start_frequency: float, end_frequency: float, points: int,
            step_time: float, settle_time: float, amplitude: float, reference_phase: float, 
            input_source: InputSource,
            input_range: InputRanges,
            ) -> float:
        """Starts Frequency Sweep.

        Parameters
        ----------
        start_frequency
            Start frequency [Hz]
        end_frequency
            End frequency [Hz]
        points
            Number of points in the sweep.
        step_time
            Time between measurement points. [s]
        settle_time
            Time to wait between setting up signal_analyzer and
            starting the frequency sweep. [s]
        amplitude: float
            Normalized Amplitude [0..1.0]
        """
        self._start_freq = start_frequency
        self._end_freq = end_frequency
        self._data_points = points

        limited_step_time = max(step_time, 0.01)
        process_time = limited_step_time*points + 2*settle_time

        self.start_time = time.time()
        self.spm_hal.start(start_frequency, end_frequency, points, step_time, settle_time, amplitude, reference_phase, input_source, input_range)
        self.is_busy = True

        return process_time + self._internal_transfer_time/2

    def _finish(self):
        """Stop FrequencySweep and capture measured data into new document"""
        self.spm_hal.abort()
        time.sleep(0.1 + self._internal_transfer_time/2)
        self.is_busy = False

    def _to_hz(self, mixer_bw_sel: Bandwidths) -> float:
        """Converts MixerBW enumeration to bandwidth in Hz."""
        mixer_base_filter_frequency = 11.1
        mixer_filter_step_factor = 2.0
        return mixer_base_filter_frequency * mixer_filter_step_factor**mixer_bw_sel

    def start_execute(
            self, start_frequency: float, end_frequency: float, frequency_step: float,
            sweep_amplitude: float,
            input_source: InputSource,
            input_range: InputRanges,
            mixer_bw_select: Bandwidths,
            reference_phase: float, output: FrequencySweepOutput) -> float:
        """Prepares and executes the Frequency Sweep.

        Parameters
        ----------
        start_frequency
            Start frequency [Hz]
        end_frequency
            End frequency [Hz]
        frequency_step
            Frequency difference between two consecutive points [Hz]
        sweep_amplitude
            Normalized Amplitude [0..1.0]
        input_source: InputSource
            Lock-in input channel
        input_range: InputRanges
            Input range switch
        mixer_bw_select : Bandwidths
            Mixer bandwidth
        reference_phase : float
            Phase shift of the reference output relative to the internal reference [°]
        output :  FrequencySweepOutput
            Selects the output

        Returns
        ----------
        total_time: float
            returns the calculated measuring time in [s]
        """
        sweep_amplitude = max(min(float(sweep_amplitude), 1.0), 0.0)
        step_time = 1/self._to_hz(mixer_bw_select)
        settle_time = 100 * step_time
        points = int((end_frequency - start_frequency)/frequency_step) + 1

        # activate output for modulation
        self.output_setup = self.Output[output](self.spm_hal._lu)

        self.measure_time = self._start(
            start_frequency, end_frequency, points, step_time, settle_time,
            sweep_amplitude, reference_phase, input_source, input_range
        )
        return self.measure_time

    def finish_execution(self, result_as_sci_stream:bool = False) -> SciStream | tuple[np.ndarray, np.ndarray]:
        """ cleanup freq execution and extract data

        parameters
        ----------
            result_as_sci_stream: bool
                if True measurement is return als SciStream with Amplitude and Phase in channel 0 and 1
        result
        -------
            two dimensional array with measured data (complex measurement data, frequency array)
            or SciStream wih amplitude and phase separated in channel 0/1
        """
        self._finish()

        # cleanup and restore original setting of output
        del self.output_setup
        self.output_setup = None

        data_stream = self._read_data_buffer()
        if not(result_as_sci_stream):
            complex_transfer = data_stream.get_channel(0).value * np.exp(1j * 2*np.pi * data_stream.get_channel(1).value/360.0)
            result = (complex_transfer, data_stream.x.value)
        else:
            result = data_stream
        return result

    def is_executing(self) -> bool:
        """ Polls the measuring status.

        Returns
        -------
        returns True if still measuring. False if finished

        """
        if self.is_busy:
            return (time.time() - self.start_time) <= self.measure_time
        return False

    def get_current_sweep_frequency(self) -> float:
        return self.spm_hal.get_current_sweep_frequency()

    def execute(self, *args, result_as_sci_stream: bool = False, **kwargs):
        """ Do the freq sweep and wait until sweep is finished.
        If blocking is not desired, then use the commands start_execute(), is_executing() and finish_execute()

        Parameters
        ----------
        See start_execute()

        Result
        ------
        see result of finish_execute()
        """

        total_time = self.start_execute(*args, **kwargs)

        print(f"Wait for {total_time:.1f}s.")
        while self.is_executing():
            time.sleep(0.1)

        return self.finish_execution(result_as_sci_stream=result_as_sci_stream)

    def bode_plot(self, complex_transfer: np.ndarray, frequencies: np.ndarray, show:bool = True) -> Tuple[plt.Figure, list[plt.Axes]]:
        """Plots Frequency sweep data to Bode Plot.

        complex_transfer
            transfer function as complex numbers
        frequencies
            frequencies where the complex transfer function is given.
        """
        bode_stream = SciStream(frequencies, channels=2, x_name="Frequency", x_unit="Hz")
        bode_stream.set_channel(0, np.abs(complex_transfer), name="Amplitude", unit="")
        bode_stream.set_channel(1, np.unwrap(np.angle(complex_transfer, deg=True), discont=180), name="Phase shift", unit="°")
        return nsf_plot.plot_bode(bode_stream, show=show)

if __name__ == "__main__":
    """This test requires hardware:
    C3000: Connect cable connectors *Out B* and *User In 1*.
    CX: Connect cable connectors *Fast Out* and *User Input 1*.
    """
    import nanosurf as nsf
    spm_app =  nsf.SPMApp()
    spm_ctrl = spm_app.connect()
    if spm_ctrl is None:
        raise ProcessLookupError("Missing running controller application")

    # test if all output configurations work
    print(f"Checking outputs.")
    ll = spm_ctrl.spm.lu
    my_fs = FrequencySweep(spm_ctrl)
    for key, output in my_fs.Output.items():
        try:
            print(f"Checking output: {key.name}")
            my_output = output(ll)
        except:
            raise ValueError(f"Problem with output: {key.name}")
        else:
            del my_output
    print("Done.")

    print("Start sweep.")
    data_as_sci_stream = True
    data = my_fs.execute(
        start_frequency=100e3, end_frequency=1e6,
        frequency_step=20e3, sweep_amplitude=0.3,
        input_source=InputSource.UserIn1,
        input_range=InputRanges.Full,
        mixer_bw_select=Bandwidths.Hz_360,
        reference_phase=0.0,
        output=FrequencySweepOutput.FastUser_OutB,
        result_as_sci_stream = data_as_sci_stream
    )
    if data_as_sci_stream:
        fig, (amp_plt, phase_plt) = nsf_plot.plot_bode(data, show=False)    
    else:
        fig, (amp_plt, phase_plt) = my_fs.bode_plot(data[0], data[1], show=False)
    phase_plt.set_ylim(-180.0, +180.0)
    plt.show()
