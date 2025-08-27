""" Some helpful mathematical functions for analyzing data in SciChannels and SciStreams
Copyright Nanosurf AG 2021
License - MIT
"""

import enum
import math
import numpy as np
import statistics as stat 
from scipy import signal
import nanosurf.lib.datatypes.sci_channel as ch
import nanosurf.lib.datatypes.sci_stream as ss
import nanosurf.lib.datatypes.sci_val as sci_val

g_use_matplotlib_format_for_unit_str = False

def get_spectral_density_unit() -> str:
    return r"/$\sqrt{Hz}$" if g_use_matplotlib_format_for_unit_str else r"\sqrt(Hz)"

def find_peaks(stream: ss.SciStream, channel_index: int = 0, **kwargs) -> ss.SciStream:
    """ Find all peaks in a stream's channel. e.g amplitude peaks in a frq-spectrum.
    It is based on scipy.signal.find_peaks() for detailed documentation  
    
    Returns
    -------
    SciStream : 
        x-data contains the x positions of the peaks
        data stream contains the y positions of the peaks
    """
    data_channel = stream.get_channel(channel_index)
    peak_indexes, _ = signal.find_peaks(data_channel.value, **kwargs)    
    max_x_array = np.empty(len(peak_indexes))
    max_y_array = np.empty_like(max_x_array)
    for idx, peak_index in enumerate(peak_indexes):
        max_x_array[idx] = stream.x.value[peak_index]
        max_y_array[idx] = data_channel.value[peak_index]
    
    # create resulting stream
    result = ss.SciStream(channels=1)
    result.x = ch.SciChannel(copy_from=max_x_array, unit=stream.x.unit)
    result.channels[0] = ch.SciChannel(copy_from=max_y_array, unit=data_channel.unit)
    return result

def find_highest_peak(stream: ss.SciStream, channel_index: int = 0, **kwargs) -> tuple[bool, float, float]:
    """ Returns the highest peak in a data channel.
    
    Returns
    -------
    tuple : (bool, x, y)
        First boolean  indicates if a peak could be detected
        If True, then x, y is the coordinate of the peak
    """
    peaks = find_peaks(stream, channel_index, **kwargs)
    if peaks.get_stream_length() >= 1:
        max_indexes = np.where(peaks.channels[0].value == np.amax(peaks.channels[0].value))
        highest_peak_index = int(max_indexes[0])
        return (True, peaks.x.value[highest_peak_index], peaks.channels[0].value[highest_peak_index])
    else:
        return (False, 0, 0)

def calc_poly_fit(stream: ss.SciStream, channel_index: int = 0, degree: int = 1) -> np.ndarray:
    """ Calculates a polynomial fit of a data channel.
    It is a non exception throwing version of numpy's np.polyfit(). See detailed function description there
    
    Results
    -------
    fir_param : ndarray
        either the result of the poly_fit or an array with size = 0
    """
    try:
        fit_param = np.polyfit(stream.x.value, stream.channels[channel_index].value, deg=degree)
    except :
        fit_param = np.array([]) 
    return fit_param

class fft_window_type(enum.Enum): 
    uniform = enum.auto()   # no windowing (all coefficient are 1.0)
    hanning = enum.auto()   # windowing function useful for noise and single frequencies (amplitude most accurate but broader spectrum)
    hamming = enum.auto()   # windowing function useful for signals with many frequency components (amplitude not so accurate but higher resolution)
    blackman = enum.auto()

def calc_fft(data_samples: ch.SciChannel, samplerate: float, window: fft_window_type = fft_window_type.hanning, spectral_density: bool = False, compress: bool = False, **kwargs) -> ss.SciStream:
    """ calculate amplitude or spectral density spectrum from time data array(s) 
    
    Parameters
    ----------
    data_samples: SciChannel
        A array of data points sampled at equally time differences 
    samplerate: float
        defines how fast data points where measured. Provided in [Hz]   
    window: optional, fft_window_type
        defines the data windowing function to be used. Available functions are defined in enum fft_window_type 
    spectral_density: optional, bool
        if True then the spectrum is normalized by the frequency resolution and the resulting unit is 1/sqrt(Hz)
    compress: optional, bool
        if True, the spectrum data is compress. it uses "rms" compression if spectral_density is True otherwise "mean" 
    Result
    ------
        DataChannel
            Spectrum as SciStream  
    """
    # handle depreciated keyword for "spectral_density" 
    if "powerspectrum" in kwargs:
        spectral_density = kwargs["powerspectrum"]

    n_samples = data_samples.value.shape[0]

    #prepare result arrays--------------------------
    n_fft_points = int(n_samples/2+1)

    fft_result_array = np.zeros(n_fft_points)

    # define FFT windowing --------------------------------
    if window == fft_window_type.uniform:
        s_window_array = np.ones(n_samples)
        noise_power_bandwidth = 1.0

    elif window == fft_window_type.hanning:
        s_window_array = np.hanning(n_samples)/0.5
        noise_power_bandwidth = 1.5

    elif window == fft_window_type.hamming:
        s_window_array = np.hamming(n_samples)/0.54
        noise_power_bandwidth = 1.36

    elif window == fft_window_type.blackman:
        s_window_array = np.blackman(n_samples)
        noise_power_bandwidth = 1.73
    else:
        print(f"calc_frq_spectrum: Error: unknown windowing function selected: {window}")
        return ss.SciStream()
    
    # calculate FFT spectrums --------------------------------
    fft_data_array = np.fft.fft(s_window_array * data_samples.value)
    fft_amp_array = np.abs(fft_data_array[:n_fft_points]) / n_fft_points
    fft_phase_array = np.angle(fft_data_array[:n_fft_points],deg=True) 

    # convert to power spectrum if needed
    if spectral_density:
        fft_result_array = fft_amp_array / np.sqrt(samplerate / n_fft_points * noise_power_bandwidth)
    else:
        fft_result_array = fft_amp_array

    # create X-Axis vector with frequencies
    if samplerate > 0.0:
        fft_frequency_array = np.linspace(0.0, samplerate/2.0, n_fft_points, endpoint=True)
    else:
        fft_frequency_array = np.linspace(0.0, n_fft_points, 1.0, endpoint=False)

    # assemble the resulting FFT spectrum as SciStream
    result = ss.SciStream(fft_frequency_array, channels=2,x_unit="Hz", x_name="Frequency")
    result.channels[0] = ch.SciChannel(fft_result_array, name = data_samples.name, unit=data_samples.unit)
    result.channels[1] = ch.SciChannel(fft_phase_array, name = "Phase", unit="deg")
    if spectral_density:
        result.channels[0].unit = f"{data_samples.unit}{get_spectral_density_unit()}"

    if compress:
        compress_method = compress_spec_algo.rms if spectral_density else compress_spec_algo.mean
        result = calc_compressed_spectrum(result, algo=compress_method)
    return result

class compress_spec_algo(enum.Enum): 
    none = enum.auto()  # no compression, return original stream
    max = enum.auto()   # calc maximum value of signal per compression slot
    mean = enum.auto()  # calc mean value of signal per compression slot 
    rms = enum.auto()   # calc rms value of signal per compression slot 
    custom = enum.auto()   # uses custom defined function to compress of signal 

def calc_compressed_spectrum(spec_data: ss.SciStream, min_dist_factor=1.02, algo:compress_spec_algo = compress_spec_algo.mean, custom_func = None) -> ss.SciStream:
    """Reduces number of data points in large data sets by logarithmic compression method
        uses a predefined or custom compression algorithm

    Parameters
    ----------
    spec_data: DataArray
        original spectrum to be compressed
    min_dist_factor
        defines the minimal distance of two frq_array points must have to compress these. Distance > frq_array[i]/frq_array[i-1] 
    algo: enum of type compress_spec_algo, optional
        if none, no compression happen at all, otherwise use one of the predefined algorithms or the supplied custom_func
    custom_func: function points, optional
        if algo is compress_spec_algo.custom, then use this function for calculating the pressed value 

    Result
    ------
        compressed_data_channel: SciStream
            new compressed array of frequency data points, not equally spaced anymore
    """
    def func_max(value_array: np.ndarray, from_index:int, to_index:int) -> float:
        return value_array[from_index:to_index].max()

    def func_mean(value_array: np.ndarray, from_index:int, to_index:int) -> float:
        return np.mean(value_array[from_index:to_index])

    def func_rms(value_array: np.ndarray, from_index:int, to_index:int) -> float:
        return np.sqrt(np.mean(np.square(value_array[from_index:to_index])))

    if algo == compress_spec_algo.none:
      result = spec_data
    else:    
        algo_map = {}
        algo_map[compress_spec_algo.mean] = func_mean
        algo_map[compress_spec_algo.max] = func_max
        algo_map[compress_spec_algo.rms] = func_rms
        algo_map[compress_spec_algo.custom] = custom_func

        compressed_frq:list[float] = spec_data.get_stream_range().value.tolist()[0:2]
        compressed_data:list[list[float]] = [ch.value.tolist()[0:2] for ch in spec_data.channels]

        compression_func = algo_map[algo]
        data_len = spec_data.get_stream_length()
        last_source_index=1 # last position in data, that was included in calculation of filter   
        for next_index in range(2,data_len):
            frq_data = spec_data.get_stream_range().value
            if frq_data[next_index]/frq_data[last_source_index] >= min_dist_factor:
                compressed_frq.append(stat.mean(frq_data[(last_source_index+1):(next_index+1)]))
                for ch_index in range(spec_data.get_channel_count()):
                    amp_data = spec_data.get_channel(ch_index).value
                    compressed_data[ch_index].append(compression_func(amp_data,last_source_index+1,next_index+1))
                last_source_index = next_index

        compressed_frq = ch.SciChannel(compressed_frq, unit=spec_data.get_stream_unit(), name=spec_data.get_stream_name())

        result = ss.SciStream(compressed_frq, channels=spec_data.get_channel_count())
        for ch_index in range(spec_data.get_channel_count()):
            result.set_channel(ch_index, compressed_data[ch_index], unit=spec_data.get_channel_unit(ch_index), name=spec_data.get_channel_name(ch_index))
    return result


def remove_peaks_in_spectrum(spec_data: ss.SciStream, channel_index: int = 0, frq_peaks: list[float] = [], span=1) -> ss.SciStream:
    """removes peaks at certain frequencies 
    
    Parameter
    ---------
    spec_data: SciStream
        The original spectrum
    channel_index: int
        The channel to smooth out
    frq_peaks: list[float]
        array of frequencys to be smoothed out
    span              
        defined as number of frequency index left and right of the peak to be used to smooth out the peak
    
    Returns
    -------
    smoothed_spec: SciStream
    """ 
    result = ss.SciStream(spec_data)
    for frq in frq_peaks:
        peak_ind = np.where(spec_data.x.value >= frq)[0][0]
        
        for smooth_index in range(peak_ind-span,peak_ind+span):
            result.channels[channel_index].value[smooth_index] = result.channels[channel_index].value[smooth_index+span*2+1]
    return result

def get_total_harmonic_distortion(spec_data: ss.SciStream, channel_index: int = 0, fundamental_frequency: float = 0.0, max_number_of_harmonics: int = 0) -> float:
    """ calculates the distortion of a signal by measuring its harmonics 
    
    Parameters
    ----------
    spec_data: SciStream
        The data source 
    channel_index: int
        The data source  channel to analyze
    fundamental_frequency
        the fundamental frequency from which the THD calculation shall be done. Defined in [Hz]. The nearest frq found in the frq_array is used 
    max_number_of_harmonics 
        optional, limits the number of harmonic frequency to used for THD calculation, 0 tells the function to use all possible harmonics found in the spectrum
    
    Result
    ------  
        thd - distortion in [dB]
    """ 
    ind = np.where(spec_data.x.value >= fundamental_frequency)[0][0]
    list_of_harmonics = range(ind*2, len(spec_data.x.value), ind)
    if max_number_of_harmonics > 0:
        list_of_harmonics = list_of_harmonics[:max_number_of_harmonics] # limit number of harmonics to be measured

    thd = 20.0 * math.log10(np.sqrt(sum(spec_data.channels[channel_index].value[list_of_harmonics]**2))/spec_data.channels[channel_index].value[ind])
    return thd

def get_noise_floor(spec_data: ss.SciStream, channel_index: int = 0, one_over_f_edge_frq: float = 0.0, level_of_percentile: float = 50.0, res_noise_floor_spec: ss.SciStream = None) -> sci_val.SciVal:
    """ determine the noise floor of a spectrum.
    
    With the level_of_percentile one can define the amount of spike and noise hills to be suppressed.
    With a value of 50 in most cases the background noise is returned. 
    With 100 maximal value found in the spectrum is returned
    With 80-95 small spikes (50Hz or so) can be ignored but real unexpected noise increase is detected

    Can be nicely combined with the function "calc_compressed_spectrum()" to improve result

    Parameter
    ---------
    spec_data: SciStream
        The data source 
    channel_index: int
        The data source  channel to analyze
    one_over_f_edge_frq:  optional
        if defined compensate for 1/f noise increase below edge frequency. Defined in [Hz]. 
    level_of_percentile:  optional
        defines the amount of data to be inside the noise_level. Useful to compensate for spikes. Has to be from 1-100 [%]. 
    res_noise_floor_spec: optional
        if defined the used spectrum for noise_floor calculation is returned. Useful to check for 1/f compensation
    
    Result
    ------  
    noise_level: sci_val.SciVal
        noise level found 
    """ 
    # compensate for 1/f noise increase below edge frequency
    if one_over_f_edge_frq > 0.0:
        # # scale 1/f noise below frequency point
        low_data_array = spec_data.channels[channel_index].value[spec_data.x.value < one_over_f_edge_frq]
        low_frq_array  = spec_data.x.value[spec_data.x.value < one_over_f_edge_frq]
    
        low_data_array = low_data_array * np.sqrt(low_frq_array) / np.sqrt(one_over_f_edge_frq)
    
        low_data_array = low_data_array[2:] # remove DC
        low_frq_array  = low_frq_array[2:]
        
        res_data_array = np.concatenate((low_data_array, spec_data.channels[channel_index].value[len(low_data_array):]))
    else:
        res_data_array = spec_data.channels[channel_index].value

    noise_floor = np.percentile(res_data_array, level_of_percentile)

    if isinstance(res_noise_floor_spec, ss.SciStream):
        res_noise_floor_spec.channels[0].value = res_data_array
        res_noise_floor_spec.x.value = spec_data.x.value
    return sci_val.SciVal(noise_floor, unit_str=spec_data.channels[channel_index].unit)

def get_amplitude(spec_data: ss.SciStream, channel_index: int = 0, frq: float = 0.0) -> tuple[sci_val.SciVal, int]:
    """ returns the amplitude value of a specified frequency
        The amplitude value of the closest frequency found in the array is returned         
    
    Parameter
    ---------
    spec_data: SciStream
        The data source 
    channel_index: int
        The data source  channel to analyze
    frq : float
        the frequency of interest in [Hz]

    Result
    ------
    (amplitude, found_index): tuple(sci_val.SciVal, int)
        The amplitude of the data array at nearest frq
        found_index, the position index in data array. If not found, index is negativ
    """ 
    found_index = -1
    
    ind = np.where(spec_data.x.value >= frq)
    found_any = ind[0].shape[0]
    
    if found_any > 0:
        found_index = ind[0][0]
    
    if found_index >= 0:
        amp = spec_data.channels[channel_index].value[found_index]
    else:
        amp = 0.0
    return (sci_val.SciVal(amp, unit_str=spec_data.channels[channel_index].unit), found_index)

def calc_signal_integral_of_frq_band(spec_data: ss.SciStream, start_frq: float, end_frq:float, spectral_density=False) -> float:
    """ calculates the area of data in a specified frequency band

    Parameters
    ----------
        spec_data: SciStream:
             with frequency data in x channel and signal data in channel 0
        start_frq, end_frq: float
            defines the start and end frequency of the desired frequency band
        spectral_density: bool
            if true, the amplitude data are assumed to have unit [1/sqrt(Hz)]
    
    Result
    ------
        amp_integral: float
            amplitude area from start_frq to end_frq in [amp_unit]
    Exception
    ---------
        ValueError: 
            In case the start or end_frq are not found in provided spec_data stream this exception is thrown
    """
    amp_integral = 0.0
    try:
        start_index: int = np.where(spec_data.x.value >= start_frq)[0][0]
        end_index: int = np.where(spec_data.x.value >= end_frq)[0][0]
    except Exception:
        raise ValueError(f"Start or End value not found in spec_data.x stream: start_frq={start_frq}, end_frq={end_frq}")
    else:
        if end_index == start_index:
            raise ValueError(f"start_frq={start_frq} end_frq={end_frq} not in stream range.")    
        
        for i in range(start_index, end_index):
            current_value = spec_data.channels[0].value[i]
            current_frq_band = spec_data.x.value[i+1] - spec_data.x.value[i]
            if spectral_density:
                current_value = current_value*current_value
            amp_integral += current_value*current_frq_band
    if spectral_density:
        amp_integral = np.sqrt(amp_integral)
    return amp_integral

def calc_signal_integral_versus_upper_bandwidth(spec_data: ss.SciStream, start_frq: float, end_frq:float, spectral_density=False) -> ss.SciStream:
    """ calculates an array of signal amplitudes versus frequency upper bound with fix start frequency
        It creates the result array of amplitude integrals by sweeping from start_frq to end_frq and calculates for each step the signal integral.

    Parameters
    ----------
        spec_data: SciStream:
             with frequency data in x channel and signal data in channel 0
        start_frq, end_frq: float
            defines the start and end frequency of the desired frequency band
        spectral_density: bool
            if true, the amplitude data are assumed to have unit [1/sqrt(Hz)]
    
    Result
    ------
        SciStream: 
            amplitude array of signal amplitude versus frequency upper bound with fix start frequency
    Exception
    ---------
        ValueError: 
            In case the start or end_frq are not found in provided spec_data stream this exception is thrown
    """
    result = ss.SciStream()
    try:
        start_index: int = np.where(spec_data.x.value >= start_frq)[0][0]
        end_index: int = np.where(spec_data.x.value >= end_frq)[0][0]
    except:
        raise ValueError(f"Start or End value not found in spec_data.x stream: start_frq={start_frq}, end_frq={end_frq}")
    else:
        integral_value_array = np.zeros(end_index - start_index) 
        integral_frq_array = spec_data.x.value[start_index:end_index]

        for i in range(len(integral_value_array)):
            integral_frq_array[i] = spec_data.x.value[start_index + i]
            integral_value_array[i] = calc_signal_integral_of_frq_band(spec_data, start_frq, integral_frq_array[i], spectral_density)
    
        result = ss.SciStream((integral_frq_array, integral_value_array), x_unit=spec_data.x.unit)
        result.set_channel_unit(0, spec_data.get_channel_unit(0).removesuffix(get_spectral_density_unit()))
    return result
