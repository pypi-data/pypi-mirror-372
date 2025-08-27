"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import nanosurf.lib.spm.lowlevel.ctrlunits as ctrlunits

class _CtrlUnitADC(ctrlunits._CtrlUnit):
    def __init__(self, spm, lu_inst_name):
        super().__init__(spm)
        self._lu_inst_name = lu_inst_name

    @property
    def inst_name(self):
        return self._lu_inst_name

    @property
    def dc(self):
        return self._lu.current_input_value.value

    @property
    def dc_norm(self):
        return self._lu.current_input_value.value / self.max

    @property
    def dc_v(self):
        return self.dc_norm * self._voltage_range

    @property
    def unit(self):
        return self._lu.current_input_value.unit

    @property
    def max(self):
        return self._lu.current_input_value.value_max

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

class CtrlUnitADCHiRes(_CtrlUnitADC):
    def __init__(self, spm, lu_inst_name):
        super().__init__(spm,lu_inst_name)
        self._lu = self._spm.lowlevel.AnalogHiResIn(spm.lowlevel.AnalogHiResIn.Instance[lu_inst_name])
        if 'USER' in lu_inst_name:
            self._voltage_range = 10.0
        else:
            self._voltage_range = 5.0

class CtrlUnitADCFast(_CtrlUnitADC):
    def __init__(self, spm, lu_inst_name):
        super().__init__(spm,lu_inst_name)
        self._lu = self._spm.lowlevel.AnalogFastIn(spm.lowlevel.AnalogFastIn.Instance[lu_inst_name])
        self._voltage_range = 1.0

