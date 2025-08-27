"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import time
import numpy as np
import nanosurf.lib.spm.lowlevel.ctrlunits as ctrlunits

class _CtrlUnitCapture(ctrlunits._CtrlUnit):
    def __init__(self, spm):
        super().__init__(spm)
        self._lu = self._spm.lowlevel.DataAcquisition()
        self._databuffer = self._spm.lowlevel.DataBuffer()
        self._channel_list = []
        self._channel_index = {}
        self.data = {}
        self.data_max = {}
        self.data_unit = {}

    @property
    def samples(self):
        return self.__samples

    @samples.setter
    def samples(self, val):
        if val > self.samples_max:
            val = self.samples_max
        if val > int(self._get_samples_max()):
            val = int(self._get_samples_max())

        self.__samples = val

    @property
    def samples_max(self):
        max_samples = self._get_samples_max()
        # if max_samples > self._databuffer.available_points:
        #     max_samples = self._databuffer.available_points
        return int(max_samples)

    @property
    def channels(self):
        return self._channel_list

    @property
    def sample_rate(self):
        return self._get_capture_rate()

    @sample_rate.setter
    def sample_rate(self, val):
        return self._set_capture_rate(val)

    @channels.setter
    def channels(self, val):
        self._channel_list = val
        self._channel_index.clear()
        index = 0
        for ch in self._channel_list:
            self._channel_index[ch] = index
            index += 1

    def measure(self, setuptime: float = 2.0):
        self._lu.number_of_capture_sets.value = 1
        self._lu.active_capture_set.value = 0
        self._setup_inputs_and_mask()

        print("Measuring", end='')
        self._lu.capture_start()
        time.sleep(setuptime) # these waiting time is important to let controller sw prepare the start and avoid wrong valid buffer message
        tick = 0
        while not self._databuffer.is_valid:
            time.sleep(0.01)
            if tick > 100:
                print(".", end='')
                tick = 0
            tick += 1
        print("")

        print("Read data", end='')
        self.data.clear()
        self.data_max.clear()
        self.data_unit.clear()
        for ch in self._channel_list:
            print(".", end='')
            data_channel = self._databuffer.channel(self._channel_index[ch])
            self.data[ch] = np.array(data_channel.data)/(pow(2, 31) - 1) * data_channel.dimension(2).data_range / 2.0
            self.data_max[ch] = data_channel.dimension(2).data_range / 2.0
            self.data_unit[ch] = data_channel.dimension(2).unit
        print("")

        self.timeline = np.linspace(0, 1.0 / self.sample_rate * (self.samples - 1), self.samples, endpoint=True)

    def _setup_inputs_and_mask(self):
        raise NotImplementedError

    def _get_capture_rate(self):
        raise NotImplementedError

    def _set_capture_rate(self, val):
        raise NotImplementedError

    def _get_samples_max(self):
        raise NotImplementedError


class CtrlUnitCaptureHiRes(_CtrlUnitCapture):
    def __init__(self, spm):
        super().__init__(spm)

    def _get_capture_rate(self):
        return self._lu.sampler_data_rate.value_max

    def _set_capture_rate(self, val):
       raise NotImplementedError

    def _get_samples_max(self):
       return int(self._lu.capture_hi_res_datapoints.value_max)

    def _set_daq_input_channel(self, ch):
        index = self._channel_index[ch]
        if index == 0:
            self._lu.capture_hi_res_ch_0_input.value = self._lu.CaptureHiResInSignal[ch]
        elif index == 1:
            self._lu.capture_hi_res_ch_1_input.value = self._lu.CaptureHiResInSignal[ch]
        elif index == 2:
            self._lu.capture_hi_res_ch_2_input.value = self._lu.CaptureHiResInSignal[ch]
        elif index == 3:
            self._lu.capture_hi_res_ch_3_input.value = self._lu.CaptureHiResInSignal[ch]
        elif index == 4:
            self._lu.capture_hi_res_ch_4_input.value = self._lu.CaptureHiResInSignal[ch]
        elif index == 5:
            self._lu.capture_hi_res_ch_5_input.value = self._lu.CaptureHiResInSignal[ch]
        elif index == 6:
            self._lu.capture_hi_res_ch_6_input.value = self._lu.CaptureHiResInSignal[ch]
        elif index == 7:
            self._lu.capture_hi_res_ch_7_input.value = self._lu.CaptureHiResInSignal[ch]
        else:
            assert False, f"index={index} is out of range"

    def _setup_inputs_and_mask(self):
        mask = 0
        for ch in self._channel_list:
            mask |= 1 << self._channel_index[ch]
            self._set_daq_input_channel(ch)
        self._lu.capture_fast_channel_mask.value = 0
        self._lu.capture_hi_res_channel_mask.value = mask
        self._lu.capture_hi_res_group_id.value = self._databuffer.group_id
        self._lu.capture_hi_res_datapoints.value = self.samples

class CtrlUnitCaptureFast(_CtrlUnitCapture):
    def __init__(self, spm):
        super().__init__(spm)
        self._lu.capture_fast_sampling_rate.value = 24000000.0
        
    def _get_capture_rate(self):
        return self._lu.capture_fast_sampling_rate.value

    def _set_capture_rate(self, val):
       self._lu.capture_fast_sampling_rate.value = val

    def _get_samples_max(self):
       return int(self._lu.capture_fast_datapoints.value_max)

    def _set_daq_input_channel(self, ch):
        index = self._channel_index[ch]
        if index == 0:
            self._lu.capture_fast_ch_0_input.value = self._lu.CaptureFastInSignal[ch]
        elif index == 1:
            self._lu.capture_fast_ch_1_input.value = self._lu.CaptureFastInSignal[ch]
        else:
            assert False, f"index={index} is out of range"

    def _setup_inputs_and_mask(self):
        mask = 0
        for ch in self._channel_list:
            mask |= 1 << self._channel_index[ch]
            self._set_daq_input_channel(ch)
        self._lu.capture_hi_res_channel_mask.value = 0
        self._lu.capture_fast_channel_mask.value = mask
        self._lu.capture_fast_group_id.value = self._databuffer.group_id
        self._lu.capture_fast_datapoints.value = self.samples
        

