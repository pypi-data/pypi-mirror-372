""" demo of data sampler measurement with studio
Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT
"""

import time
import numpy as np
import nanosurf as nsf
from nanosurf.lib.spm.lowlevel.data_buffer import DataBufferAccess
import matplotlib.pyplot as plt

def read_data_buffer(data_buffer: DataBufferAccess, sampler_rate:float, sampler_points:int, verbose:bool = False) -> nsf.SciStream:
    num_channels = data_buffer.channel_count
    if num_channels >= 1:
        my_stream = nsf.SciStream(channels=num_channels)
        for i in range(num_channels):
            my_stream.set_channel(i, data_buffer.read_channel(i))
            if verbose: print(f"Read channel {i}: '{my_stream.get_channel_name(i)}' unit [{my_stream.get_channel_unit(i)}]")

        measured_num_samples = len(my_stream.get_channel(0).value)
        if verbose: print(f"Measured samples: {measured_num_samples}")

        time_array = np.linspace(0, (1.0 / sampler_rate) * (measured_num_samples - 1), measured_num_samples, endpoint=True)
        my_stream.set_stream_range(time_array, unit="s", name= "Time")
        return my_stream
    else:
        if verbose: print(f"No channels found.")
        return nsf.SciStream()

def measure_data_with_sampler(studio:nsf.Studio, channel_vector:list[int], number_of_points:int, sample_rate:float = 1e6, buffer_id:int = 456789, verbose:bool = False) -> nsf.SciStream:
    """ measure a set of data channels with data sampler 
        maximal sample rate is 1MHz

        Parameters
        ----------

        studio: object
                points to studio object 
        channel_vector: 
                list of channel id to measure. 
                They have to be enum id from: lu_daq.attribute.sampler_hi_res_ch0_input.ValueEnum
                they are measured according to their list index
        number_of_points: int
                Number of data samples to be measured. 
        sample_rate: float
                Speed of sampling in (Hz)
        buffer_id: int, optional
                If provided this data_buffer_id is used for sampling.
        verbose: bool, optional
                if True some log messages are printed to standard output

    Return
    ------
        data_stream:nsf.SciStream
            All measured data are stored in the SciStream. 
            Channel number is equal to channel index of channel vector

    """
    data_buffer = DataBufferAccess(studio, buffer_id=buffer_id, verbose=verbose)

    lu = studio.spm.lu
    lu_daq = lu.data_acquisition.instance
    lu_daq.attribute.sampler_hi_res_ch_input_vec.vector = channel_vector
    lu_daq.attribute.number_of_sampler_sets.value = 1
    lu_daq.attribute.active_sampler_set.value = 0
    lu_daq.attribute.sampler_group_id.value = data_buffer.group_id
    lu_daq.attribute.sampler_channel_mask.value = pow(2,len(channel_vector)) - 1
    lu_daq.attribute.sampler_datapoints.value = number_of_points
    lu_daq.attribute.sampler_auto_set_filter_mode.value = 1
    lu_daq.attribute.sampler_data_rate.value = sample_rate
    lu_daq.attribute.sampler_trigger_mode.value = lu_daq.attribute.sampler_trigger_mode.ValueEnum.internal_timer

    if verbose: print("Start sampling")
    lu_daq.trigger.sampler_prepare()
    lu_daq.trigger.background_sampler_start()

    while lu_daq.busy.is_sampling:
        if verbose: print("Wait until sampling is finished")
        time.sleep(0.01)

    data_buffer.transfer_data_buffer()
    daq_stream = read_data_buffer(data_buffer, lu_daq.attribute.sampler_data_rate.value, int(number_of_points), verbose=verbose)
    return daq_stream


studio = nsf.Studio()
if studio.connect():
    # define channels to be measured
    lu_daq_channel_id_enum = studio.spm.lu.data_acquisition.instance.attribute.sampler_hi_res_ch0_input.ValueEnum
    data_channels = [
        lu_daq_channel_id_enum.in_position_z,
        lu_daq_channel_id_enum.in_deflection,
    ]
    # do measurement and 
    measured_stream = measure_data_with_sampler(studio, data_channels, number_of_points=10000, sample_rate=1e6, verbose=True)

    # let the library plot the result
    nsf.plot.plot_stream(measured_stream)

    # or do it by yourself
    #---------------------
    # for ch in range(measured_stream.get_channel_count()):
    #     plt.plot(measured_stream.x.value, measured_stream.get_channel(ch).value, label=f"{measured_stream.get_channel(ch).name} ({measured_stream.get_channel(ch).unit})")
    # plt.xlabel(f"{measured_stream.x.name} ({measured_stream.x.unit})")
    # plt.legend()
    # plt.show()

else:
    print("Could not connect to studio. Is it running?")
del studio

