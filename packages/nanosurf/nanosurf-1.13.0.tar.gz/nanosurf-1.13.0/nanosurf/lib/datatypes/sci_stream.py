"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""


import numpy as np
from typing import Any, Union
import nanosurf.lib.datatypes.sci_channel as ch


class SciStream:
    def __init__(self, 
        source:Union[tuple, list[Any], ch.SciChannel, 'SciStream' , None] = None, 
        channels:int = 1, stream_length:int = 0, 
        x_unit:str = "", x_name:str = ""):

        self.x = ch.SciChannel(unit=x_unit, name=x_name)
        
        if isinstance(source, ch.SciChannel):
            self.x = ch.SciChannel(source)
            self.channels = [ch.SciChannel(np.zeros_like(source.value)) for _ in range(channels)]
        elif isinstance(source, SciStream):
            self.x = ch.SciChannel(source.x)
            self.copy_channels(source)
        elif isinstance(source, tuple):
            self.x = ch.SciChannel(source[0],unit=x_unit, name=x_name)
            self.channels = [ch.SciChannel(source[1])]
        elif source is not None:
            self.x = ch.SciChannel(source,unit=x_unit, name=x_name)
            self.channels = [ch.SciChannel(array_length=len(self.x.value)) for ch_index in range(channels)]
        else:
            self.channels = [ch.SciChannel(array_length=stream_length) for ch_index in range(channels)]

    def set_stream_length(self, length: int):
        if length != self.get_stream_length():
            if self.x.value.size > 0:       
                min = np.min(self.x.value)
                max = np.max(self.x.value)
            else:
                min = 0.0
                max = 1.0
            self.x.value = np.resize(self.x.value, length)
            self.define_stream_range(min, max)
            self._adjust_channel_length()

    def get_stream_length(self) -> int:
        return self.x.value.size

    def set_stream_range(self, range: ch.SciChannel| np.ndarray | list, unit: str = "", name:str =""):
        if isinstance(range, ch.SciChannel):
            self.x = range
        else:
            self.x = ch.SciChannel(range, unit=unit, name=name)
        self._adjust_channel_length()

    def get_stream_range(self) -> ch.SciChannel:
        return self.x

    def define_stream_range(self, min: float, max: float, unit: str = "", name:str = ""):
        self.x.value = np.linspace(min, max, self.get_stream_length())
        if unit != "":
            self.x.unit = unit
        if name != "":
            self.x.name = name

    def get_stream_unit(self) -> str:
        return self.x.unit

    def set_stream_unit(self, unit: str):
        self.x.unit = unit

    def get_stream_name(self) -> str:
        return self.x.name

    def set_stream_name(self, name: str):
        self.x.name = name

    def get_channel_count(self) -> int:
        return len(self.channels)
        
    def set_channel_count(self, channels: int):
        current_len = self.get_channel_count()
        if current_len < channels:
            self.channels.extend( [ch.SciChannel(array_length=self.get_stream_length()) for d in range(channels - current_len)])
        elif current_len > channels:
            self.channels = self.channels[:channels]

    def copy_channels(self, source: 'SciStream'):
        assert source.get_stream_length() == self.get_stream_length(), "SciStream: Streams must have equal length"
        self.channels = [ch.SciChannel(source.channels[stream_index]) for stream_index in range(source.get_channel_count())]    

    def get_channel(self, channel_index: int) -> ch.SciChannel:
        assert channel_index < len(self.channels), "SciStream: Channel index out of bound error"
        return self.channels[channel_index]

    def set_channel(self, channel_index: int, source: ch.SciChannel | np.ndarray | list, unit: str = "", name:str = ""):
        assert channel_index < len(self.channels), "SciStream: Channel index out of bound error"
        self.channels[channel_index] = ch.SciChannel(source, unit=unit, name=name)

    def get_channel_unit(self, channel_index: int) -> str:
        assert channel_index < len(self.channels), "SciStream: Channel index out of bound error"
        return self.channels[channel_index].unit

    def set_channel_unit(self, channel_index: int, unit: str):
        assert channel_index < len(self.channels), "SciStream: Channel index out of bound error"
        self.channels[channel_index].unit = unit

    def get_channel_name(self, channel_index: int) -> str:
        assert channel_index < len(self.channels), "SciStream: Channel index out of bound error"
        return self.channels[channel_index].name

    def set_channel_name(self, channel_index: int, name: str):
        assert channel_index < len(self.channels), "SciStream: Channel index out of bound error"
        self.channels[channel_index].name = name

    def _adjust_channel_length(self):
        x_size = self.x.value.size
        for ch in self.channels:
            if ch.value.size != x_size:
                ch.value = np.resize(ch.value, x_size)

    def __len__(self):
        return len(self.x.value)
        
