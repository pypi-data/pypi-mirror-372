""" Functions to simplify handling of iir-filter vectors
    It's compatible with spm and studio software
    
Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT"""

import numpy as np

from nanosurf.lib.spm.lowlevel.logical_unit_interface import _LogicalUnit
from nanosurf.lib.spm.lowlevel import check
from nanosurf.lib.spm.studio.wrapper import CmdTreeNode

def convert_filter_coeffs_to_lu_vector(scipy_sos:list[list[float]], filter_gain_factor:float = 1.0) -> np.ndarray:
    """ Converts standard second-order-section filter coefficients into """
    result:list[list[float]] = []
    for section in scipy_sos:
        if section[3] != 1.0:
            raise ValueError("SOS-Filter design parameters cannot be converted")
        result.append([filter_gain_factor, -section[5], -section[4], section[2], section[1], section[0]])
    return np.array(result)

def set_filter_lu_analog_hi_res_output(lu_instance: CmdTreeNode | _LogicalUnit, scipy_sos:list[list[float]], filter_gain:float = 1.0):
    """Configures the output filter of the named lu output.

    lu_instance: logical_unit object instance of type LUAnalogHiResOutput
    lu_filter_vector: np.array(2D) second order filter section coefficients as lu_filter_vector
        first dimension: section index
        second dimension: parameters in this order: [ gain, -A2, -A1, B2, B1, B0 ]
    """
    lu_filter_vector = convert_filter_coeffs_to_lu_vector(scipy_sos, filter_gain)
    if check.is_spm_lu(lu_instance):
        for stage_index in range(0, lu_filter_vector.shape[0]):
            lu_instance.filter_number.value = stage_index
            lu_instance.filter_coeff_vec.value = lu_filter_vector[stage_index].tolist()
    elif check.is_studio_lu(lu_instance):
        for stage_index in range(0, lu_filter_vector.shape[0]):
            lu_instance.attribute.filter_number.value = stage_index
            lu_instance.attribute.filter_coeff_vec.value = lu_filter_vector[stage_index].tolist()
    else:
          raise ValueError(f"Unknown type of lu_instance '{type(lu_instance)}'")          
    
def clear_filter_lu_analog_hi_res_output(lu_instance: CmdTreeNode | _LogicalUnit):
    all_pass_filter_coeffs = [[ 1., 0., 0., 1., 0., 0. ], [ 1., 0., 0., 1., 0., 0. ]]
    set_filter_lu_analog_hi_res_output(lu_instance, all_pass_filter_coeffs, filter_gain=1.0)

if __name__ == "__main__":
    import nanosurf as nsf
    filter_coeffs_0 = nsf.math.iir_filter.calc_bandpass_filter(f_cut_on=180, f_cut_off=500)
    amp_phase_stream_0 = nsf.math.iir_filter.calc_filter_response(filter_coeffs_0, freq_start=10, freq_stop=1000)
    nsf.math.plot.plot_bode(amp_phase_stream_0, "Plot of amplitude and phase for three filter designs", amp_as_dB=True)
    
    spm_ctrl = nsf.SPMApp()
    if spm_ctrl.connect():
        if spm_ctrl.is_spm():
            print("Using SPM")
            lu_analog_out = spm_ctrl.spm.lowlevel.AnalogHiResOut(spm_ctrl.spm.lowlevel.AnalogHiResOut.Instance.POSITIONX)
        elif spm_ctrl.is_studio():
            print("Using Studio")
            lu_analog_out = spm_ctrl.studio.spm.lu.analog_hi_res_out.position_x
        else:
            raise ProcessLookupError("Could not find running instance of afm software")
        
        nsf.spm.ll.iir_filter.set_filter_lu_analog_hi_res_output(lu_analog_out, filter_coeffs_0)
        nsf.spm.ll.iir_filter.clear_filter_lu_analog_hi_res_output(lu_analog_out)
        