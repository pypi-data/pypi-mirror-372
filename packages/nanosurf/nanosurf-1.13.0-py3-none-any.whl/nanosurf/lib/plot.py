""" Functions to plot easily SciStream, SciChannels, and general list by matplotlib
Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT"""

import sys
from typing import Tuple
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker
import nanosurf.lib.datatypes.sci_channel as ch
import nanosurf.lib.datatypes.sci_stream as ss



g_plot_line_width = 2
g_plot_tick_length = 6

def plot_stream(plot_data:ss.SciStream | list[ss.SciStream], ch_list:list[int] = None, individual_plots:bool = True, title:str = None, as_dB: bool = False, log_x:bool = False, log_y:bool = False, show:bool=True, **kwargs) -> Tuple[plt.Figure, list[plt.Axes]]:
    """ Plot the channels of a stream(s) as diagram 

    Parameters:
    -----------
    plot_data: single SciStream or list of SciStream
        Assumptions are:
            stream.x data = frequencies 
            stream.channel(n) are some kind of amplitude data 

    individual_plots: bool, optional, default = True
        if True each channel is plotted into a individual chart
        all equal channel indexes of multiple streams are plotted into the same chart

    title: str, optional
        if provided plot a title

    as_dB: bool, optional, default=False
        if set to True. the data is plotted as dB (20*log(amp))

    log_x, log_y: bool
        this flags define if a certain axis shall be plotted in logarithmic scale
    
    show: bool, optional, default=True
        if True, show plot. 

    Returns:
    --------
        plt.Figure, list[plt.Axes]: 
            matplotlib style fig and subplots
            Can be used to further modify the plot and then sh

    """
    list_of_streams = plot_data if isinstance(plot_data, list) else [plot_data]

    number_of_channels = 0
    for stream in list_of_streams:
        number_of_channels = max(stream.get_channel_count(), number_of_channels)

    if ch_list is None:
        ch_list = range(number_of_channels)

    number_of_subplots = 1
    if individual_plots:
        number_of_subplots = len(ch_list)

    fig, subplots = plt.subplots(number_of_subplots,1,figsize=(9,6))
    subplots = subplots if isinstance(subplots, np.ndarray) else [subplots]

    x_min = sys.float_info.max 
    x_max = sys.float_info.min
    for stream in list_of_streams:
        x_min = min(x_min, min(stream.x.value))    
        x_max = max(x_max, max(stream.x.value))   

        if ch_list is None:
            ch_list = range(stream.get_channel_count())

        for ch_index, ch in enumerate(ch_list):
            ch_data = stream.get_channel(ch).value
            if as_dB:
                ch_data = 20*np.log10(ch_data)
                
            sub_plot_num = ch_index if individual_plots else 0

            if log_x and log_y:
                subplots[sub_plot_num].loglog(stream.x.value, ch_data, linewidth=g_plot_line_width, label=f"{stream.get_channel(ch).name} ({stream.get_channel(ch).unit})", **kwargs)    
            elif log_x:
                subplots[sub_plot_num].semilogx(stream.x.value, ch_data, linewidth=g_plot_line_width, label=f"{stream.get_channel(ch).name} ({stream.get_channel(ch).unit})", **kwargs)    
            elif log_y:
                subplots[sub_plot_num].semilogy(stream.x.value, ch_data, linewidth=g_plot_line_width, label=f"{stream.get_channel(ch).name} ({stream.get_channel(ch).unit})", **kwargs)    
            else:
                subplots[sub_plot_num].plot(stream.x.value, ch_data, linewidth=g_plot_line_width, label=f"{stream.get_channel(ch).name} ({stream.get_channel(ch).unit})", **kwargs)    

    fig.suptitle(title if title is not None else "Stream plot")

    #grid and tick marks settings 
    stream = list_of_streams[0]
    for subplot_index, subplot in enumerate(subplots):
        subplot.set_xlabel(f"{stream.x.name} ({stream.x.unit})")
        subplot.set_xlim(x_min, x_max)
        subplot.grid(False)
        subplot.tick_params(axis='both', length=int(g_plot_tick_length))
        subplot.tick_params(axis='both', which='minor', length=int(g_plot_tick_length/2))
        if as_dB:
            subplot.set_ylabel(f'{stream.get_channel_name(subplot_index)} (dB)')
        else:
            subplot.set_ylabel(f'{stream.get_channel_name(subplot_index)} ({stream.get_channel_unit(subplot_index)})')

        if len(list_of_streams) > 1:
            subplot.legend()

    plt.tight_layout()
    if show:
        plt.show()
    return (fig, subplots)


def plot_bode(plot_data: ss.SciStream | list[ss.SciStream] | Tuple[list,list, list], title:str = None, amp_as_dB: bool = False, show:bool=True, log_amp:bool = True) -> Tuple[plt.Figure, list[plt.Axes]]:
    """ Plot amp/phase stream(s) into bode plot diagram 

    Parameters:
    -----------
    plot_data: single SciStream or list of SciStream or tuple()
        Assumptions are:
            stream.x data = frequencies 
            stream.channel(0) is amplitude 
            stream.channel(1) is phase in (degree)
        
        Alternatively a tuple of three list or numpy_array is also supported. 
        The tuple must have the form (frq, amp, phase)
        

    title: str, optional
        if provided plot a title

    amp_as_dB: bool, optional, default=False
        if set to True. the amplitude data is plotted as dB (20*log(amp))
    
    show: bool, optional, default=True
        if True, show plot. 

    Returns:
    --------
        fig, amp_plot, phase_plot: 
            matplotlib style fig and two subplots for amp and phase
            Can be used to further modify the plot and then sh

    """
    amp_channel   = 0 
    phase_channel = 1 

    plot_stream_array = plot_data if isinstance(plot_data, list) else [plot_data]

    for index, data in enumerate(plot_stream_array):
        if not isinstance(data, ss.SciStream):
            try: 
                frq_array, amp_array, phase_array = data
                new_stream = ss.SciStream(frq_array, channels=2, x_unit="Hz", x_name="Frequency")        
                new_stream.set_channel(amp_channel,amp_array, unit="arb", name="Amplitude")
                new_stream.set_channel(phase_channel, phase_array, unit="°", name="Phase")
                plot_stream_array[index] = new_stream
            except:
                raise ValueError("plot_data tuple must have for of (frq, amp, phase)")

    fig, (amp_plot, phase_plot) = plt.subplots(2,1,figsize=(9,6))

    #loop through frequency response list, calculate magnitude and phase
    freq_min = sys.float_info.max
    freq_max = sys.float_info.min
    for amp_phase_stream in plot_stream_array:
        if amp_phase_stream.get_channel_count() < 2:
            raise ValueError("stream must have at least two channels. ch(0)=amp. ch(1)=phase")    
        freq_min = min(freq_min, min(amp_phase_stream.x.value))    
        freq_max = max(freq_max, max(amp_phase_stream.x.value))   

        amp_data = amp_phase_stream.get_channel(amp_channel).value
        if amp_as_dB:
            amp_data = 20*np.log10(amp_data)

        if log_amp:
            amp_plot.loglog(amp_phase_stream.x.value, amp_data, linewidth=g_plot_line_width, label=f"{amp_phase_stream.get_channel(amp_channel).name} ({amp_phase_stream.get_channel(amp_channel).unit})")    
        else:
            amp_plot.semilogx(amp_phase_stream.x.value, amp_data, linewidth=g_plot_line_width, label=f"{amp_phase_stream.get_channel(amp_channel).name} ({amp_phase_stream.get_channel(amp_channel).unit})")    

        phase_data = amp_phase_stream.get_channel(phase_channel).value
        phase_plot.semilogx(amp_phase_stream.x.value, phase_data, linewidth=g_plot_line_width, label=f"{amp_phase_stream.get_channel(phase_channel).name} ({amp_phase_stream.get_channel(phase_channel).unit})")    

    fig.suptitle(title if title is not None else "Bode plot")

    #grid and tick marks settings for amplitude plot
    amp_phase_stream = plot_stream_array[0]
    amp_plot.set_xlabel(f"{amp_phase_stream.x.name} ({amp_phase_stream.x.unit})")
    amp_plot.set_xlim(freq_min, freq_max)
    amp_plot.grid(False)
    amp_plot.tick_params(axis='both', length=int(g_plot_tick_length))
    amp_plot.tick_params(axis='both', which='minor', length=int(g_plot_tick_length/2))
    if amp_as_dB:
        amp_plot.set_ylabel(f'{amp_phase_stream.get_channel_name(amp_channel)} (dB)')
    else:
        amp_plot.set_ylabel(f'{amp_phase_stream.get_channel_name(amp_channel)} ({amp_phase_stream.get_channel_unit(amp_channel)})')

    #grid and tick marks settings for phase plot
    phase_plot.set_xlabel(f"{amp_phase_stream.x.name} ({amp_phase_stream.x.unit})")
    phase_plot.set_xlim(freq_min, freq_max)
    phase_plot.grid(False)
    phase_plot.tick_params(axis='both', length=6)
    phase_plot.tick_params(axis='both', which='minor', length=3)
    loc = ticker.MultipleLocator(base=30)
    phase_plot.yaxis.set_major_locator(loc)
    phase_plot.set_ylabel(f'{amp_phase_stream.get_channel_name(phase_channel)} ({amp_phase_stream.get_channel_unit(phase_channel)})')
    
    if len(plot_stream_array) > 1:
        amp_plot.legend()
        phase_plot.legend()

    plt.tight_layout()
    if show:
        plt.show()
    return (fig, [amp_plot, phase_plot])


def plot_spectrum(plot_data:ss.SciStream | list[ss.SciStream], ch_list:list[int] = None, individual_plots:bool = True, title:str = None, as_dB: bool = False, show:bool=True, log_y:bool=False) -> Tuple[plt.Figure, list[plt.Axes]]:
    """ Plot spectrum stream(s) as diagram 

    Parameters:
    -----------
    plot_data: single SciStream or list of SciStream
        Assumptions are:
            stream.x data = frequencies 
            stream.channel(n) are some kind of amplitude data

    individual_plots: bool, optional, default = False
        if True each channel is plotted into a individual chart

    title: str, optional
        if provided plot a title

    as_dB: bool, optional, default=True
        if set to True. the data is plotted as dB (20*log(amp))
    
    show: bool, optional, default=True
        if True, show plot. 

    Returns:
    --------
        plt.Figure, list[plt.Axes]: 
            matplotlib style fig and subplots
            Can be used to further modify the plot and then sh

    """
    return plot_stream(plot_data, ch_list = ch_list, individual_plots=individual_plots, title=title, as_dB=as_dB,show=show, log_x=True, log_y=log_y)

def plot(plot_data, ch_list:list[int] = None, individual_plots:bool = True, title:str = None, as_dB: bool = False, log_x:bool = False, log_y:bool = False, show:bool=True, **kwargs) -> Tuple[plt.Figure, list[plt.Axes]]:
    """ Try to plot any data provided as nicely as possible
        
        plot_data can by any type of numerical list, numpy.ndarray, SciChannel or SciStream
        multiple data array can be provided as list in mixed format
    """
    # make sure plot_data is list like
    plot_data_array = plot_data if isinstance(plot_data, list) else [plot_data]
    if len(plot_data_array) == 0:
        raise ValueError("Cannot plot empty data array")

    # check if plot_data is a basic numeric list
    if isinstance(plot_data_array[0], int) or isinstance(plot_data_array[0], float):
        plot_data_array = [plot_data_array]     

    if len(plot_data_array[0]) == 0:
        raise ValueError("Cannot plot empty data array")
    
    # convert all plot_data into SciStream
    for index, data in enumerate(plot_data_array):
        if not isinstance(data, ss.SciStream):
            x_len = len(data)
            x_array = np.linspace(0, x_len, x_len, endpoint=False)
            plot_data_array[index] = ss.SciStream((x_array, data), x_unit="Index", x_name="Position")

    return plot_stream(plot_data_array, ch_list = ch_list, individual_plots=individual_plots, title=title, as_dB=as_dB,show=show, log_x=log_x, log_y=log_y, **kwargs)

if __name__ == "__main__":
    import nanosurf as nsf

    # Create some fake data.
    x1 = np.linspace(0.0, 5.0, num=512)
    y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
    y2 = np.cos(2 * np.pi * x1 + np.pi/4.0) * np.exp(-x1/10.0)
    spec_data_1 = nsf.sci_math.calc_fft(ch.SciChannel(y1, unit="arb", name="Damped oscillator "), samplerate=1e3)
    spec_data_2 = nsf.sci_math.calc_fft(ch.SciChannel(y2, unit="arb", name="More damped oscillator"), samplerate=1e3)
    
    dual_channel_stream = ss.SciStream(channels=2)
    dual_channel_stream.set_stream_range(spec_data_1.x)
    dual_channel_stream.set_channel(0, spec_data_1.get_channel(0))
    dual_channel_stream.set_channel(1, spec_data_2.get_channel(0))
    plot(dual_channel_stream, title="Frequency Spectrum plot", individual_plots=False, log_x=True, log_y=False, as_dB=False )


