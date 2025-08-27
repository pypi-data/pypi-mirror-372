"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import nanosurf.lib.spm.lowlevel.ctrlunits as ctrlunits

class _CtrlUnitDAC(ctrlunits._CtrlUnit):
    def __init__(self, spm, lu_inst_name):
        super().__init__(spm)
        self._lu_inst_name = lu_inst_name

    @property
    def inst_name(self):
        return self._lu_inst_name
    @property
    def dc(self):
        return self._lu.current_output_value.value

    @dc.setter
    def dc(self, val):
        self._lu.static_value.value = val
        self._lu.input.value = self._static_input_channel_index

    @property
    def dc_norm(self):
        return self._lu.current_output_value.value / self.max

    @dc_norm.setter
    def dc_norm(self, val):
        self.dc = val * self.max

    @property
    def dc_v(self):
        return self.dc_norm * self._voltage_range

    @dc_v.setter
    def dc_v(self, val):
        self.dc_norm = val / self._voltage_range

    @property
    def unit(self):
        return self._lu.current_output_value.unit

    @property
    def max(self):
        return self._lu.current_output_value.value_max

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, val):
        import nanosurf.lib.spm.lowlevel.ctrlunits.analyzer as analyzer
        import nanosurf.lib.spm.lowlevel.ctrlunits.channelmux as channelmux

        self.__source = val
        if isinstance(self.__source, analyzer.CtrlUnitsSineWaveGenerator):
            self.__source.target = self
            self._lu.input.value = self._ac_input_channel_index[self.__source.inst_name]
            self._lu.calib_sig_source_dir.value = self._spm.lowlevel.AnalogHiResOut.CalibSigSourceDir.FromOutputToInput
        elif isinstance(self.__source, channelmux._CtrlUnitChannelMux):
            self.__source.channelmap = self._channelmap
            self.__source.target = self
            if self.__source.channel != "":
                self.__source.channel =  self.__source.channel  # reset channel to saved value
            self._lu.calib_sig_source_dir.value = self._spm.lowlevel.AnalogHiResOut.CalibSigSourceDir.FromInputToOutput
        else:
            self._lu.input.value = self._static_input_channel_index
            self._lu.calib_sig_source_dir.value = self._spm.lowlevel.AnalogHiResOut.CalibSigSourceDir.FromOutputToInput

    @property
    def inverted(self):
        return self._lu.calib_polarity.value == self._spm.lowlevel.AnalogHiResIn.CalibPolarity.Negative

    @inverted.setter
    def inverted(self, val):
        if val == True:
            self._lu.calib_polarity.value = self._spm.lowlevel.AnalogHiResIn.CalibPolarity.Negative
        else:
            self._lu.calib_polarity.value = self._spm.lowlevel.AnalogHiResIn.CalibPolarity.Positive

    @property
    def calib_gain(self):
        return self._lu.calib_gain.value

    @calib_gain.setter
    def calib_gain(self, val):
        self._lu.calib_gain.value = val

    @property
    def calib_offset(self):
        return self._lu.calib_offset.value

    @calib_offset.setter
    def calib_offset(self, val):
        self._lu.calib_offset.value = val

class CtrlUnitDACHires(_CtrlUnitDAC):
    def __init__(self, spm, lu_inst_name):
        super().__init__(spm, lu_inst_name)
        self._lu = spm.lowlevel.AnalogHiResOut(spm.lowlevel.AnalogHiResOut.Instance[lu_inst_name])
        self._voltage_range = 10.0
        self._channelmap = self._spm.lowlevel.AnalogHiResOut.InputChannels
        self._static_input_channel_index = spm.lowlevel.AnalogHiResOut.InputChannels.Static
        self._ac_input_channel_index = {
            "INST2":spm.lowlevel.AnalogHiResOut.InputChannels.GenTest_Dynamic
        }

class CtrlUnitDACFast(_CtrlUnitDAC):
    def __init__(self, spm, lu_inst_name):
        super().__init__(spm, lu_inst_name)
        self._lu = spm.lowlevel.AnalogFastOut(spm.lowlevel.AnalogFastOut.Instance[lu_inst_name])
        self._voltage_range = 1.0
        self._channelmap = self._spm.lowlevel.AnalogFastOut.InputChannels
        self._static_input_channel_index = spm.lowlevel.AnalogFastOut.InputChannels.Static
        self._ac_input_channel_index = {
            "INST1":spm.lowlevel.AnalogFastOut.InputChannels.Analyzer1_Reference,
            "INST2":spm.lowlevel.AnalogFastOut.InputChannels.Analyzer2_Reference,
        }
