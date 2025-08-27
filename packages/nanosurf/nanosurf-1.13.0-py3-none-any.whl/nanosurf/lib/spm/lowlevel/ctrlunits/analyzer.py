"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import nanosurf.lib.spm.lowlevel.ctrlunits as ctrlunits

class CtrlUnitsSineWaveGenerator(ctrlunits._CtrlUnit):
    def __init__(self, spm, lu_inst_name):
        super().__init__(spm)
        self._lu_inst_name = lu_inst_name
        self._lu = self._spm.lowlevel.SignalAnalyzer(spm.lowlevel.SignalAnalyzer.Instance[lu_inst_name])
        self._lu.operating_mode.value = self._lu.OperatingMode.LockIn
        self._lu.target_amplitude_ctrl_mode.value = self._lu.AmplitudeCtrlMode.ConstDrive
 
    @property
    def inst_name(self):
        return self._lu_inst_name

    @property
    def amp(self):
        return self.amp_norm * self.amp_max

    @amp.setter
    def amp(self, val):
        self.amp_norm = val / self.amp_max

    @property
    def amp_norm(self):
        return self._lu.reference_amplitude.value / self._lu.reference_amplitude.value_max

    @amp_norm.setter
    def amp_norm(self, val):
        self._lu.reference_amplitude.value = val * self._lu.reference_amplitude.value_max
        self._lu.switch_to_target_amplitude_ctrl_mode()

    @property
    def amp_v(self):
        return self.amp_norm * self.target._voltage_range

    @amp_v.setter
    def amp_v(self, val):
        self.amp_norm = val / self.target._voltage_range

    @property
    def amp_max(self):
        return self.target.max

    @property
    def amp_unit(self):
        return self.target.unit

    @property
    def freq(self):
        return  self._lu.reference_frequency.value

    @freq.setter
    def freq(self, val):
        self._lu.reference_frequency.value = val

class CtrlUnitLockIn(CtrlUnitsSineWaveGenerator):
    def __init__(self, spm, lu_inst_name):
        super().__init__(spm, lu_inst_name)
        self.list_of_bandwidth = self._lu.DemodulatorBW
        self._lu.input.value = self._lu.Input.FastInDeflection
        self._fast_input_channel_index = {
            "DEFLECTION":spm.lowlevel.SignalAnalyzer.Input.FastInDeflection,
            "CH2":spm.lowlevel.SignalAnalyzer.Input.FastIn2,
            "USER":spm.lowlevel.SignalAnalyzer.Input.FastInUser,
        }
        try:
            # only v3.10.3 or newer has longer list of input channels
            self._hires_input_channel_index = {
                "DEFLECTION":spm.lowlevel.SignalAnalyzer.Input.InDeflection,
                "USER1":spm.lowlevel.SignalAnalyzer.Input.InUser1,
                "USER2":spm.lowlevel.SignalAnalyzer.Input.InUser2,
                "USER3":spm.lowlevel.SignalAnalyzer.Input.InUser3,
                "USER4":spm.lowlevel.SignalAnalyzer.Input.InUser4,
                "TIPCURRENT":spm.lowlevel.SignalAnalyzer.Input.InTipCurrent,
                "POSITIONX":spm.lowlevel.SignalAnalyzer.Input.InPositionX,
                "POSITIONY":spm.lowlevel.SignalAnalyzer.Input.InPositionY,
                "POSITIONZ":spm.lowlevel.SignalAnalyzer.Input.InPositionZ,
                "LATERAL":spm.lowlevel.SignalAnalyzer.Input.InLateral,
                "DETECTORSUM":spm.lowlevel.SignalAnalyzer.Input.InDetectorSum,
                "IN6":spm.lowlevel.SignalAnalyzer.Input.In6,
            }
        except:
            self._hires_input_channel_index = {
                "USER1":spm.lowlevel.SignalAnalyzer.Input.InUser1,
                "USER2":spm.lowlevel.SignalAnalyzer.Input.InUser2,
                "USER3":spm.lowlevel.SignalAnalyzer.Input.InUser3,
                "USER4":spm.lowlevel.SignalAnalyzer.Input.InUser4,
                "TIPCURRENT":spm.lowlevel.SignalAnalyzer.Input.InTipCurrent,
                "POSITIONX":spm.lowlevel.SignalAnalyzer.Input.InPositionX,
                "POSITIONY":spm.lowlevel.SignalAnalyzer.Input.InPositionY,
                "POSITIONZ":spm.lowlevel.SignalAnalyzer.Input.InPositionZ,
                "LATERAL":spm.lowlevel.SignalAnalyzer.Input.InLateral,
            }

    @property
    def reference_phase(self):
        return self._lu.reference_pase.value

    @reference_phase.setter
    def reference_phase(self, val):
        self._lu.reference_pase.value = val

    @property
    def demodulation_bw(self):
        return self._lu.demodulator_bw.value

    @demodulation_bw.setter
    def demodulation_bw(self, val):
        self._lu.demodulator_bw.value = val

    @property
    def input_amp(self):
        return self._lu.current_amplitude.value

    @property
    def input_amp_unit(self):
        return self._lu.current_amplitude.unit

    @property
    def input_amp_max(self):
        return self._lu.current_amplitude.value_max

    @property
    def input_phase(self):
        return self._lu.current_phase.value

    @property
    def input_phase_unit(self):
        return self._lu.current_phase.unit

    @property
    def input_phase_max(self):
        return self._lu.current_phase.value_max

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, val):
        import nanosurf.lib.spm.lowlevel.ctrlunits.adc as adc
        import nanosurf.lib.spm.lowlevel.ctrlunits.channelmux as channelmux

        self.__source = val
        if isinstance(self.__source, adc.CtrlUnitADCFast):
            self.__source.target = self
            self._lu.input.value = self._fast_input_channel_index[self.__source.inst_name]
        elif isinstance(self.__source, adc.CtrlUnitADCHiRes):
            self.__source.target = self
            self._lu.input.value = self._hires_input_channel_index[self.__source.inst_name]
        elif isinstance(self.__source, channelmux.CtrlUnitLockInMux):
            self.__source.target = self
            if self.__source.channel != "":
                self.__source.channel =  self.__source.channel  # reset channel to saved value
        else:
            assert False, "Assigned Lock-In source not supported: type: "+str(type(val))
            self.__source = None
