"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

from enum import IntEnum

class DAC(IntEnum):
    HiResOut_POSITIONX = 1
    HiResOut_POSITIONY = 2
    HiResOut_POSITIONZ = 3
    HiResOut_POSITIONW = 4
    HiResOut_TIPVOLTAGE = 5
    HiResOut_OUT6 = 6
    HiResOut_OUT7 = 7
    HiResOut_OUT8 = 8
    HiResOut_USER1= 9
    HiResOut_USER2 = 10
    HiResOut_USER3 = 11
    HiResOut_USER4 = 12
    FastOut_EXCITATION = 13
    FastOut_USER = 14
    FastOut_FAST2 = 15
    FastOut_FAST3 = 16

class ADC(IntEnum):
    HiResIn_DEFLECTION = 1
    HiResIn_LATERAL = 2
    HiResIn_POSITIONX = 3
    HiResIn_POSITIONY = 4
    HiResIn_POSITIONZ = 5
    HiResIn_DETECTORSUM = 6
    HiResIn_TIPCURRENT = 7
    HiResIn_IN6 = 8
    HiResIn_USER1 = 9
    HiResIn_USER2 = 10
    HiResIn_USER3 = 11
    HiResIn_USER4 = 12
    FastIn_DEFLECTION = 13
    FastIn_CH2 = 14
    FastIn_USER = 15

class Analyzer(IntEnum):
    SigAnalyzer_1 = 1
    SigAnalyzer_2 = 2

class ChannelMux(IntEnum):
    AnalogHiResOut = 1
    AnalogFastOut = 2
    SigAnalyzer_1 = 3
    SigAnalyzer_2 = 4

class DataCapture(IntEnum):
    CaptureHiRes = 5
    CaptureFast = 6

class DataSampler(IntEnum):
    SamplerHiRes = 7


class _CtrlUnit:
    def __init__(self, spm):
        self._spm = spm
        self._lu = None
        self.__source = None
        self.__target = None

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, val):
        self.__source = val

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, val):
        self.__target = val

