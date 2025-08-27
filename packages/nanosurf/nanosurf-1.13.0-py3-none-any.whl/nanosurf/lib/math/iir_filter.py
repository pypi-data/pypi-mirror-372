""" Some functions to calculate iir filters and use them with lowlevel logical units
Copyright Nanosurf AG 2023
License - MIT


Usage:
------

Step 1: Calculate a filter, use one of these
    filter_coeffs = calc_bandpass_filter(f_cut_on=180, f_cut_off=500)
    filter_coeffs = calc_lowpass_filter(f_cut_off=300)
    filter_coeffs = calc_highpass_filter(f_cut_off=300)

Step 2: Convert coefficient to nanosurf filter format
    lu_out_filter_vector = convert_filter_coeffs_to_lu_vector(filter_coeffs)

Step 3: Set filter of an output
    import nanosurf as nsf
    spm = nsf.SPM()

    user1_out = spm.lowlevel.AnalogHiResOut(ll.AnalogHiResOut.Instance.USER1)
    set_filter_lu_analog_hi_res_output(user1_out, lu_out_filter_vector)

Step 4: optional, calc and plot amp/phase response
    import nanosurf as nsf
    amp_phase_stream = calc_filter_response(filter_coeffs, freq_start=100, freq_stop=1500)
    nsf.sci_math.plot_bode(amp_phase_stream)


"""

import numpy as np
from scipy import signal
import nanosurf.lib.datatypes.sci_stream as ss

g_high_res_output_filter_stage_count = 2
g_high_res_converter_sample_frequency = 1000000

def calc_bandpass_filter(f_cut_on:float,f_cut_off:float, filter_order:int = 2, filter_clock_freq:float=g_high_res_converter_sample_frequency) -> list[list[float]]:
    sos_filter_coeffs = signal.iirfilter(filter_order, [f_cut_on, f_cut_off], btype = 'bandpass', output = 'sos', fs=filter_clock_freq)
    return sos_filter_coeffs

def calc_bandstop_filter(f_cut_on:float,f_cut_off:float, filter_order:int = 2, filter_clock_freq:float=g_high_res_converter_sample_frequency) -> list[list[float]]:
    sos_filter_coeffs = signal.iirfilter(filter_order, [f_cut_on, f_cut_off], btype = 'bandstop', output = 'sos', fs=filter_clock_freq)
    return sos_filter_coeffs

def calc_lowpass_filter(f_cut_off:float, filter_order:int = 2, filter_clock_freq:float=g_high_res_converter_sample_frequency) -> list[list[float]]:
    sos_filter_coeffs = signal.iirfilter(filter_order, [f_cut_off], btype = 'lowpass', output = 'sos', fs=filter_clock_freq)
    return sos_filter_coeffs

def calc_highpass_filter(f_cut_off:float, filter_order:int = 2, filter_clock_freq:float=g_high_res_converter_sample_frequency) -> list[list[float]]:
    sos_filter_coeffs = signal.iirfilter(filter_order, [f_cut_off], btype = 'highpass', output = 'sos', fs=filter_clock_freq)
    return sos_filter_coeffs

def calc_filter_response(sos_filter_coeffs: list, freq_start:float, freq_stop:float, num_data_points:int=512, unwrap_phase:bool=True, filter_clock_freq:float=g_high_res_converter_sample_frequency) -> ss.SciStream:
    """ calculates amplitude and phase response of a filter.

    Parameters:
    -----------
    sos_filter_coeffs: list of sos-coefficients
        Coefficients of a second-order-section filter design of any order
    
    freq_start, freq_stop: float
        defines the frequency range of the resulting amplitude and phase stream

    num_data_points: int, optional
        defines the number of data points calculated in the amp/phase stream

    unwrap_phase: bool, optional
        If set to True, the phase can be more that 180°

    filter_clock_freq: float, optional
        defines the clock_frequency used to calculate the filter, default is standard high_res DAC clock frequency of the CX Controller

    Result:
    -------
    SciStream:
        Stream with x data as frequency, channel 0 with amplitude and channel 1 with phase
    """
    freq_array = np.geomspace(freq_start, freq_stop, num_data_points, endpoint=True)
    filt_freqs, complex_response = signal.sosfreqz(sos_filter_coeffs, freq_array, fs=filter_clock_freq)
    
    bode_plot_stream = ss.SciStream(channels=2)
    bode_plot_stream.set_stream_range(filt_freqs, unit="Hz", name="Frequency")

    bode_plot_stream.set_channel(0, abs(complex_response), unit="norm", name="Amplitude")
    
    if unwrap_phase:
        phase_data = np.unwrap(np.angle(complex_response))*180.0/np.pi
    else:
        phase_data = np.angle(complex_response)*180.0/np.pi
    bode_plot_stream.set_channel(1, phase_data, unit="deg", name="Phase")
    
    return bode_plot_stream


if __name__ == "__main__":
    import nanosurf as nsf
    filter_coeffs_0 = calc_bandpass_filter(f_cut_on=180, f_cut_off=500)
    amp_phase_stream_0 = calc_filter_response(filter_coeffs_0, freq_start=10, freq_stop=1000)
    amp_phase_stream_0.set_channel_name(0,"Bandpass")
    amp_phase_stream_0.set_channel_name(1,"Bandpass")
    # print(f"Filter coeff bandpass= {convert_filter_coeffs_to_lu_vector(filter_coeffs_0)}")

    filter_coeffs_1 = calc_highpass_filter(f_cut_off=300)
    amp_phase_stream_1 = calc_filter_response(filter_coeffs_1, freq_start=100, freq_stop=1500)
    amp_phase_stream_1.set_channel_name(0,"Highpass")
    amp_phase_stream_1.set_channel_name(1,"Highpass")
    # print(f"Filter coeff high pass = {convert_filter_coeffs_to_lu_vector(filter_coeffs_1)}")

    filter_coeffs_2 = calc_lowpass_filter(f_cut_off=300)
    amp_phase_stream_2 = calc_filter_response(filter_coeffs_2, freq_start=100, freq_stop=1500)
    amp_phase_stream_2.set_channel_name(0,"Lowpass")
    amp_phase_stream_2.set_channel_name(1,"Lowpass")
    # print(f"Filter coeff high pass = {convert_filter_coeffs_to_lu_vector(filter_coeffs_2)}")

    nsf.math.plot.plot_bode([amp_phase_stream_0, amp_phase_stream_1, amp_phase_stream_2], "Plot of amplitude and phase for three filter designs", amp_as_dB=True)
    
