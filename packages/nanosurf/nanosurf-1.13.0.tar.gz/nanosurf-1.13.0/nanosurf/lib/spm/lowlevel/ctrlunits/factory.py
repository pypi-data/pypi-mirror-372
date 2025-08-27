"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

from nanosurf.lib.spm.lowlevel import ctrlunits
import nanosurf.lib.spm.lowlevel.ctrlunits.dac as dac
import nanosurf.lib.spm.lowlevel.ctrlunits.adc as adc
import nanosurf.lib.spm.lowlevel.ctrlunits.analyzer as analyzer
import nanosurf.lib.spm.lowlevel.ctrlunits.channelmux as channelmux
import nanosurf.lib.spm.lowlevel.ctrlunits.capture as capture
import nanosurf.lib.spm.lowlevel.ctrlunits.sampler as sampler

class _CtrlUnitFactory:
    """Main class for working with the CX """

    def __init__(self, spm: 'Spm' = None):
        """
        Parameters
        ----------
        spm
            reference to the nanosurf.spm class used
        """
        self._spm = spm
        self._dacmap = {
            ctrlunits.DAC.HiResOut_POSITIONX:["AnalogHiResOut", "POSITIONX"],
            ctrlunits.DAC.HiResOut_POSITIONY:["AnalogHiResOut", "POSITIONY"],
            ctrlunits.DAC.HiResOut_POSITIONZ:["AnalogHiResOut", "POSITIONZ"],
            ctrlunits.DAC.HiResOut_POSITIONW:["AnalogHiResOut", "POSITIONW"],
            ctrlunits.DAC.HiResOut_TIPVOLTAGE:["AnalogHiResOut", "TIPVOLTAGE"],
            ctrlunits.DAC.HiResOut_OUT6:["AnalogHiResOut", "APPROACH"],
            ctrlunits.DAC.HiResOut_OUT7:["AnalogHiResOut", "OUT7"],
            ctrlunits.DAC.HiResOut_OUT8:["AnalogHiResOut", "OUT8"],
            ctrlunits.DAC.HiResOut_USER1:["AnalogHiResOut", "USER1"],
            ctrlunits.DAC.HiResOut_USER2:["AnalogHiResOut", "USER2"],
            ctrlunits.DAC.HiResOut_USER3:["AnalogHiResOut", "USER3"],
            ctrlunits.DAC.HiResOut_USER4:["AnalogHiResOut", "USER4"],
            ctrlunits.DAC.FastOut_EXCITATION:["AnalogFastOut", "EXCITATION"],
            ctrlunits.DAC.FastOut_USER:["AnalogFastOut", "USER"],
            ctrlunits.DAC.FastOut_FAST2:["AnalogFastOut", "FAST2"],
            ctrlunits.DAC.FastOut_FAST3:["AnalogFastOut", "FAST3"],
        }
        self._adcmap = {
            ctrlunits.ADC.HiResIn_DEFLECTION:["AnalogHiResIn", "DEFLECTION"],
            ctrlunits.ADC.HiResIn_LATERAL:["AnalogHiResIn", "LATERAL"],
            ctrlunits.ADC.HiResIn_POSITIONX:["AnalogHiResIn", "POSITIONX"],
            ctrlunits.ADC.HiResIn_POSITIONY:["AnalogHiResIn", "POSITIONY"],
            ctrlunits.ADC.HiResIn_POSITIONZ:["AnalogHiResIn", "POSITIONZ"],
            ctrlunits.ADC.HiResIn_DETECTORSUM:["AnalogHiResIn", "DETECTORSUM"],
            ctrlunits.ADC.HiResIn_TIPCURRENT:["AnalogHiResIn", "TIPCURRENT"],
            ctrlunits.ADC.HiResIn_IN6:["AnalogHiResIn", "IN6"],
            ctrlunits.ADC.HiResIn_USER1:["AnalogHiResIn", "USER1"],
            ctrlunits.ADC.HiResIn_USER2:["AnalogHiResIn", "USER2"],
            ctrlunits.ADC.HiResIn_USER3:["AnalogHiResIn", "USER3"],
            ctrlunits.ADC.HiResIn_USER4:["AnalogHiResIn", "USER4"],
            ctrlunits.ADC.FastIn_DEFLECTION:["AnalogFastIn", "DEFLECTION"],
            ctrlunits.ADC.FastIn_CH2:["AnalogFastIn", "CH2"],
            ctrlunits.ADC.FastIn_USER :["AnalogFastIn", "USER"],
        }
        self._analyzermap = {
            ctrlunits.Analyzer.SigAnalyzer_1:["SignalAnalyzer", "INST1"],
            ctrlunits.Analyzer.SigAnalyzer_2:["SignalAnalyzer", "INST2"],
        }

    def get_dac(self, ctrlunit_id: ctrlunits.DAC) -> dac._CtrlUnitDAC:
        if self._dacmap[ctrlunit_id][0] == "AnalogHiResOut":
            return dac.CtrlUnitDACHires(self._spm, self._dacmap[ctrlunit_id][1])
        elif self._dacmap[ctrlunit_id][0] == "AnalogFastOut":
            return dac.CtrlUnitDACFast(self._spm, self._dacmap[ctrlunit_id][1])
        return None

    def get_adc(self, ctrlunit_id: ctrlunits.ADC) -> adc._CtrlUnitADC:
        if self._adcmap[ctrlunit_id][0] == "AnalogHiResIn":
            return adc.CtrlUnitADCHiRes(self._spm, self._adcmap[ctrlunit_id][1])
        elif self._adcmap[ctrlunit_id][0] == "AnalogFastIn":
            return adc.CtrlUnitADCFast(self._spm, self._adcmap[ctrlunit_id][1])
        return None

    def get_sin_generator(self, ctrlunit_id: ctrlunits.Analyzer = ctrlunits.Analyzer.SigAnalyzer_2) -> analyzer.CtrlUnitsSineWaveGenerator:
        if self._analyzermap[ctrlunit_id][0] == "SignalAnalyzer":
            return analyzer.CtrlUnitsSineWaveGenerator(self._spm, self._analyzermap[ctrlunit_id][1])
        return None

    def get_lock_in(self, ctrlunit_id: ctrlunits.Analyzer = ctrlunits.Analyzer.SigAnalyzer_2) -> analyzer.CtrlUnitLockIn:
        if self._analyzermap[ctrlunit_id][0] == "SignalAnalyzer":
            return analyzer.CtrlUnitLockIn(self._spm, self._analyzermap[ctrlunit_id][1])
        return None

    def get_multiplexer(self, ctrlunit_id: ctrlunits.ChannelMux) -> channelmux._CtrlUnitChannelMux:
        if ctrlunit_id == ctrlunits.ChannelMux.AnalogHiResOut:
            return channelmux.CtrlUnitDACHiResMux(self._spm)
        elif ctrlunit_id == ctrlunits.ChannelMux.AnalogFastOut:
            return channelmux.CtrlUnitDACFastMux(self._spm)
        elif ctrlunit_id == ctrlunits.ChannelMux.SigAnalyzer_1:
            return channelmux.CtrlUnitLockInMux(self._spm)
        elif ctrlunit_id == ctrlunits.ChannelMux.SigAnalyzer_2:
            return channelmux.CtrlUnitLockInMux(self._spm)
        return None

    def get_data_capture(self, ctrlunit_id: ctrlunits.DataCapture) -> capture._CtrlUnitCapture:
        if ctrlunit_id == ctrlunits.DataCapture.CaptureHiRes:
            return capture.CtrlUnitCaptureHiRes(self._spm)
        elif ctrlunit_id == ctrlunits.DataCapture.CaptureFast:
            return capture.CtrlUnitCaptureFast(self._spm)
        return None

    def get_data_sampler(self, sampler_mod = ctrlunits.DataSampler.SamplerHiRes) -> sampler._CtrlUnitSampler:
        if sampler_mod == ctrlunits.DataSampler.SamplerHiRes:
            return sampler.CtrlUnitSamplerHiRes(self._spm)
        return None