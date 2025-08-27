""" The fit module where the obtained sweep data gets fitted with simple harmonic oscillator funciton
Copyright Nanosurf AG 2021
License - MIT
"""
import math
import warnings
from dataclasses import dataclass
import numpy as np
from scipy import optimize as sci_optimize

from nanosurf.lib.frameworks.qt_app import nsf_thread
from nanosurf.lib.frameworks.qt_app import module_base

@dataclass
class FrequencySweepFitData():
    result_ok = False
    result_fit_freq = []
    result_fit_amplitude = []
    result_fit_phase = []
    result_resonance_frequency_amplitude = 0.0
    result_q_factor_amplitude = 0.0

class FrequencySweepFitWorker(nsf_thread.NSFBackgroundWorker):

    par_measured_amplitudes = []
    par_measured_phases = []
    par_measured_frequencys = []
    par_init_param_amplitude = [0, 0, 0, 0, 0]
    par_init_param_phase = [0, 0, 0, 0]

    def __init__(self, my_module: module_base.ModuleBase):
        super().__init__(my_module)
        self.resulting_data = FrequencySweepFitData()
        
    def do_work(self):
        self.resulting_data = FrequencySweepFitData()
        self.resulting_data.result_ok = True
        
        ok = self.estimate_initial_parameter()
        self.resulting_data.result_ok &= ok
        
        ok, *_ = self.fit_amplitude()
        self.resulting_data.result_ok &= ok
        
        ok, *_ = self.fit_phase()
        self.resulting_data.result_ok &= ok

    def get_task_result(self) -> FrequencySweepFitData:
        return self.resulting_data

    def phase_function(self, x, fn, q, a, b) -> list[float]:
        """ Phase response of a damped driven harmonic oscillator """
        return np.arctan(q * (fn**2 - x**2) / (fn * x)) + a*x + b

    def amplitude_function(self, x, fn, q, a, b, c) -> list[float]:
        """ Amplitude response of a damped driven harmonic oscillator"""
        return a / np.sqrt((fn**2 - x**2) ** 2 + ((fn * x) / q)**2) + b*x + c

    def estimate_initial_parameter(self) -> bool:
        self.send_info_message("Estimating initial parameter for curve fitting...")
        preparation_ok = False
        amplitudes = self.par_measured_amplitudes
        phases = self.par_measured_phases
        frequencies = self.par_measured_frequencys
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                
                # Get max amplitude frequency from raw data
                fn_est = frequencies[np.argmax(amplitudes)]

                # Calculate q-factor from estimated resonance freq and bandwidth
                bw = 2.0*abs((fn_est - frequencies[round((np.argmax(amplitudes) - np.argmin(amplitudes))/2.0 + np.argmin(amplitudes))]))
                q = fn_est / bw

                # Calculate the linear fit to take the influence of other vibration into account
                slope_fit, offset_fit = np.polyfit(frequencies, amplitudes, 1)

                # Calculate the excitation amplitude from max amplitude and max amplitude frequency
                a_excitations = amplitudes*np.sqrt(np.square(fn_est**2 - np.square(frequencies)) + np.square(fn_est*frequencies/q)) + slope_fit*frequencies + offset_fit
                amplitude_excitation = np.mean(a_excitations)

                # Calculate the linear fit to get the slope
                phase_slope, *_ = np.polyfit(frequencies, phases, 1)
                phase_offset = np.mean(phases)

                self.par_init_param_amplitude[0] = fn_est
                self.par_init_param_amplitude[1] = q
                self.par_init_param_amplitude[2] = amplitude_excitation
                self.par_init_param_amplitude[3] = slope_fit
                self.par_init_param_amplitude[4] = offset_fit

                self.par_init_param_phase[0] = fn_est
                self.par_init_param_phase[1] = q
                self.par_init_param_phase[2] = phase_slope
                self.par_init_param_phase[3] = phase_offset
                # print(self.par_init_param_amplitude)
                # print(self.par_init_param_phase)

                # Get resonance frequency and Q-factor from phase fit as initial parameter for amplitude fit
                ok, p_opt = self.fit_phase()
                if ok:
                    self.par_init_param_amplitude[0] = p_opt[0]
                    self.par_init_param_amplitude[1] = p_opt[1]
                    self.send_info_message("initial parameter estimating successful")
                    preparation_ok = True
        except Exception :
            self.send_info_message("initial parameter estimating not successful")
            self.logger.warn("initial parameter estimating not successful")
        return preparation_ok

    def fit_phase(self) -> tuple[bool, list[float]]:
        print("fitting phase data...")
        initial = self.par_init_param_phase
        frequencies = np.asarray(self.par_measured_frequencys)
        phases =  np.asarray(self.par_measured_phases)

        ok = False
        p_opt:list[float] = [] 
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")   

                phases_rad = phases*math.pi/180.0
                p_opt, *_ = sci_optimize.curve_fit(self.phase_function, frequencies, phases_rad, p0=initial)

                fn, q, phase_slope, phase_offset = p_opt
                phase_response = self.phase_function(frequencies, fn, q, phase_slope, phase_offset)

                phase_array_deg = np.asarray(phase_response) * 180.0 / math.pi
                self.resulting_data.result_fit_phase = phase_array_deg

                ok = True
                self.send_info_message("phase fit successful")
        except Exception:
            self.logger.warn("Could not fit phase")
            ok = False
        return (ok, p_opt)

    def fit_amplitude(self) -> tuple[bool, list[float]]:
        self.send_info_message("fitting amplitude data...")
        initial = self.par_init_param_amplitude
        freq = self.par_measured_frequencys
        amplitude = self.par_measured_amplitudes

        ok = False
        p_opt:list[float] = [] 
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")

                p_opt, *_= sci_optimize.curve_fit(self.amplitude_function, freq, amplitude, p0=initial)
                fn, q, amplitude_excitation, amplitude_slope, amplitude_offset  = p_opt

                self.resulting_data.result_fit_freq = freq
                self.resulting_data.result_resonance_frequency_amplitude = fn
                self.resulting_data.result_q_factor_amplitude = q

                amplitude_at_peak_freq = self.amplitude_function(freq, fn, q, amplitude_excitation, amplitude_slope, amplitude_offset)
                self.resulting_data.result_fit_amplitude = amplitude_at_peak_freq 
                self.send_info_message("amplitude fit successful")
                ok = True
        except Exception:
            self.logger.warn("Could not fit amplitude")
            ok = False
        return (ok, p_opt)