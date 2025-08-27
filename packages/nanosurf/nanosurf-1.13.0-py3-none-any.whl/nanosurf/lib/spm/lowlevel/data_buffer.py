""" Functions to simplify the usage of the lowlevel data_buffer interface
    It's compatible with spm and studio software

Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT"""

import enum
import time
from typing import Union
import numpy as np


from nanosurf.lib.spm.com_proxy import Spm
from nanosurf.lib.spm.studio import Studio
try:
    from nanosurf.lib.spm.studio.wrapper.cmd_tree_spm import Root
except ImportError: 
    pass
import nanosurf.lib.spm.lowlevel.data_buffer_interface as nsf_databuffer
import nanosurf.lib.datatypes.sci_channel as ch

class DataBufferAccess():

    class StudioBufferState(enum.IntEnum):
        invalid = 0
        trimmed = 1
        synchronizing = 2
        synchronized = 3

    def __init__(self, spm_root:Union[Studio, Spm], buffer_id:int = -1, verbose:bool = False) -> None:
        self._verbose = verbose
        self._spm_root = spm_root
        self._spm = spm_root.spm
        self._lu = self._spm.lu
 
        if self._spm.is_studio:
            self._spm:Root 
            self._core_acq = self._spm.core.acquisition
        else:
            self._spm:Spm 
        self.create_data_buffer(buffer_id)
        self.set_busy_callback(None)

    def __del__(self):
        if self._spm.is_studio:
            del self._data_buffer

    def _default_busy_callback(self, busy:str):
        if self._verbose: print(busy)

    def set_busy_callback(self, busy_call_back = None):
        self._busy_callback = busy_call_back if busy_call_back is not None else self._default_busy_callback

    def create_data_buffer(self, buffer_id:int = -1):
        if self._spm.is_studio:
            if buffer_id < 0: buffer_id = 4410
            self._data_buffer_id = buffer_id
            self._core_acq.reserve_lu_data_buffer(self._data_buffer_id)
            self._data_buffer = None
        else:
            self._data_buffer:nsf_databuffer.DataBufferInterface = self._lu.DataBuffer()
            if buffer_id >= 0:
                self._data_buffer._group_id = buffer_id
            self._data_buffer_id = self._data_buffer.group_id
        
    def transfer_data_buffer(self):
        busy_str = ""
        if self._spm.is_studio:
            self._core_acq.trim_sampler_buffer(self._data_buffer_id)
            self._core_acq.synchronize_lu_data_buffer(self._data_buffer_id)
            while self._core_acq.lu_data_buffer_state(self._data_buffer_id) != DataBufferAccess.StudioBufferState.synchronized:
                busy_str += "*"
                self._busy_callback(busy_str)
                time.sleep(0.01)
        else:
            self._data_buffer.synchronize_data_group()
            while self._data_buffer.is_synchronizing:
                busy_str += "*"
                self._busy_callback(busy_str)
                time.sleep(0.1)
            
            while not self._data_buffer.is_valid:
                busy_str += "*"
                self._busy_callback(busy_str)
                time.sleep(0.1)

    def read_channel_data(self, channel_id:int) -> np.ndarray:
        if not(self.is_valid):
            self.transfer_data_buffer()
        channel_data  = self.get_channel_data_raw(channel_id)
        channel_range = self.get_channel_range(channel_id)
        return np.array(channel_data)/(pow(2, 31) - 1) * channel_range

    def read_channel(self, channel_id:int) -> ch.SciChannel:
        channel_data = self.read_channel_data(channel_id)
        channel_unit = self.get_channel_unit(channel_id)
        channel_name = self.get_channel_name(channel_id)
        return ch.SciChannel(channel_data, unit=channel_unit, name=channel_name)

    def get_channel_data_raw(self, channel_id:int) -> np.ndarray:
        if not(self.is_valid):
            self.transfer_data_buffer()
        if self._spm.is_studio:
            channel_data  = self._core_acq.lu_data_buffer_channel_data(self._data_buffer_id, channel_id)
        else:
            data_buffer   = self._data_buffer.channel(channel_id)
            channel_data  = data_buffer.data
        return np.array(channel_data)
    
    def get_channel_range(self, channel_id:int) -> float:
        if not(self.is_valid):
            self.transfer_data_buffer()
        if self._spm.is_studio:
            channel_range = self._core_acq.lu_data_buffer_channel_range(self._data_buffer_id, channel_id)
        else:
            data_buffer   = self._data_buffer.channel(channel_id)
            channel_range = data_buffer.dimension(2).data_range / 2.0
        return channel_range

    def get_channel_unit(self, channel_id:int) -> str:
        if not(self.is_valid):
            self.transfer_data_buffer()
        if self._spm.is_studio:
            channel_unit = self._core_acq.lu_data_buffer_channel_unit(self._data_buffer_id, channel_id)
        else:
            data_buffer  = self._data_buffer.channel(channel_id)
            channel_unit = data_buffer.dimension(2).unit
        return channel_unit

    def get_channel_name(self, channel_id:int) -> str:
        if not(self.is_valid):
            self.transfer_data_buffer()
        if self._spm.is_studio:
            channel_name = self._core_acq.lu_data_buffer_channel_name(self._data_buffer_id, channel_id)
        else:
            data_buffer  = self._data_buffer.channel(channel_id)
            channel_name = data_buffer.dimension(2).name
        return channel_name
    
    @property
    def group_id(self):
        return self._data_buffer_id

    @property
    def is_synchronizing(self) -> bool:
        if self._spm.is_studio:
            syncing = self._core_acq.lu_data_buffer_state(self._data_buffer_id) == DataBufferAccess.StudioBufferState.synchronizing
        else:
            syncing = self._data_buffer.is_synchronizing
        return syncing

    @property
    def is_valid(self):
        if self._spm.is_studio:
            valid = self._core_acq.lu_data_buffer_state(self._data_buffer_id) == DataBufferAccess.StudioBufferState.synchronized
        else:
            valid = self._data_buffer.is_valid
        return valid

    @property
    def timestamp_first_sample(self):
        if self._spm.is_studio:
            timestamp = self._core_acq.lu_data_buffer_timestamp(self._data_buffer_id) 
        else:
            timestamp = self._data_buffer.timestamp_first_sample
        return timestamp

    @property
    def timestamp_first_sample_str(self):
        return str(self.timestamp_first_sample(self))

    @property
    def channel_count(self):
        if self._spm.is_studio:
            num_channels = self._core_acq.lu_data_buffer_channel_count(self._data_buffer_id) 
        else:
            num_channels = self._data_buffer.channel_count
        return num_channels      

if __name__ == "__main__":
    import nanosurf as nsf
    
    spm_app = nsf.SPMApp()
    spm = spm_app.connect()
    if spm is not None:
        if spm.is_studio:
            print("Using Studio")
        else:
            print("Using SPM")
    else:
        raise ProcessLookupError("Could not find running instance of afm software")
        
