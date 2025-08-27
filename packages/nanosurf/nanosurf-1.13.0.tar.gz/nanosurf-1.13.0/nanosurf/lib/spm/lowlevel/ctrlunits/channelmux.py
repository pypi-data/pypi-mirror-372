"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import nanosurf.lib.spm.lowlevel.ctrlunits as ctrlunits

class _CtrlUnitChannelMux(ctrlunits._CtrlUnit):
    def __init__(self, spm):
        self._channelmap = None
        self._channel_name = ""

    @property
    def channelmap(self):
        return self._channelmap

    @channelmap.setter
    def channelmap(self, val):
        self._channelmap = val

    @property
    def channel(self):
        return self._channel_name

    @channel.setter
    def channel(self, val):
        self._channel_name = val
        self.target._lu.input.value = self._channelmap[val]

class CtrlUnitDACHiResMux(_CtrlUnitChannelMux):
    def __init__(self, spm):
        super().__init__(spm)
        self.channelmap = spm.lowlevel.AnalogHiResOut.InputChannels

class CtrlUnitDACFastMux(_CtrlUnitChannelMux):
    def __init__(self, spm):
        super().__init__(spm)
        self.channelmap = spm.lowlevel.AnalogFastOut.InputChannels

class CtrlUnitLockInMux(_CtrlUnitChannelMux):
    def __init__(self, spm):
        super().__init__(spm)
        self.channelmap = spm.lowlevel.SignalAnalyzer.Input

