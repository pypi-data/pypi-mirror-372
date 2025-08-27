""" Script to be used to analyze WaveModeNMA data.
Copyright Nanosurf AG 2024
License - MIT
"""

#%%
#Import libraries
import datetime as datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
import sys
import time

from nanosurf.lib.util import nhf_reader, gwy_export, fileutil
from scipy.interpolate import griddata
from scipy.optimize import curve_fit

### Set row and column index for plotting an individual f-d curve here: ###
column_index = 0
row_index = 0

### Change factor (0 - 1) to select start and end of baseline here: ###
baseline_start = 0
baseline_end = 0.25

### Change factor (0 - 1) to select start and end of fit range here: ###
fit_start = 0.55
fit_end = 0.6

### Set model parameter here: ###
fit_model ="Linear" # Choose "Linear", "Hertz", "DMT", "JKR" or "Sneddon"
nu_sample = 0.5 # Poisson ratio of sample
#nu_probe = 0.25 # Poisson ratio of probe
#E_probe = 280e9 # Young's modulus of probe
tip_radius = 10 # Tip radius in nm (used for Hertz, DMT and JKR)
tip_opening_angle=np.deg2rad(25) # Tip opening angle in degree (used for Sneddon)

### Calculate constant parameters for contact model fitting ###
a0 = (4/3)/(1-nu_sample**2)*np.sqrt(tip_radius)
a1 = 2*np.pi*tip_radius
a2 = 1.5*np.pi*tip_radius
a3 = (2/np.pi)/(1-nu_sample**2)*np.tan(tip_opening_angle)


### Initialize global measurement data channels ###
class Measurement_Data:
    ch_nma_deflection: nhf_reader.NHFDataset = None
    ch_nma_interaction: nhf_reader.NHFDataset = None
    ch_topography: nhf_reader.NHFDataset = None

### Initialize empty lists to append during analysis ###
class Result_List:
    list_max_force_in_nN: list[float] = []
    list_adhesion_in_nN: list[float] = []
    list_elasticity_in_Pa: list[float] = []

### Initialize empty arrays for calculated data ###
class Result_Map:
    map_topography_in_m: np.ndarray = np.empty((0,0))
    map_max_force_in_nN: np.ndarray = np.empty((0,0))
    map_adhesion_in_nN: np.ndarray = np.empty((0,0))
    map_elasticity_in_Pa: np.ndarray = np.empty((0,0))

meas_data = Measurement_Data()
res_list = Result_List()
res_map = Result_Map()


### Analysis functions ###
def analyze_force_curve(distance_nm:np.array, force_nN:np.array, i:int, plot_curve_index:int = -1):
    analysis_result = {}
    analysis_result["model"] = fit_model

    ### Define index to split advance and retract part of force curve ###
    points_per_period: int = len(distance_nm)
    points_per_half_period: int = int(points_per_period/2)
    analysis_result["points_per_period"] = points_per_period
    analysis_result["points_per_half_period"] = points_per_half_period

    ### Do tilt correction of baseline by fitting linear function to baseline ###
    baseline_index_start = int(points_per_period*baseline_start)
    baseline_index_end = int(points_per_period*baseline_end)
    analysis_result["baseline_index_start"] = baseline_index_start
    analysis_result["baseline_index_end"] = baseline_index_end
    try:
        popt_baseline_fit, _ = curve_fit(fit_func_linear, distance_nm[baseline_index_start:baseline_index_end], force_nN[baseline_index_start:baseline_index_end])
        tilt = fit_func_linear(distance_nm, *popt_baseline_fit)
        # Comment for no baseline correction:
        force_nN = force_nN-tilt
    except Exception as e:
        print(f"Warning: Could not do baseline correction: {e}")

    
    ### Correct for baseline offset ###
    force_nN = force_nN - np.mean(force_nN[baseline_index_start:baseline_index_end])

    ### Get adhesion as minimum point of retract part ###
    adhesion = np.min(force_nN[points_per_half_period:-1])
    adhesion_index = np.where(force_nN[points_per_half_period:-1] == adhesion)[0][0]+points_per_half_period
    analysis_result["adhesion"] = adhesion*-1
    analysis_result["adhesion_index"] = adhesion_index
    analysis_result["adhesion_distance"] = distance_nm[adhesion_index]
    
    ### Correct for contact point offset ###
    # Find initial guess for contact point as first zero crossing for Hertz and Sneddon
    # Optional: Choose adhesion index as contact point index
    # Adapt atol if contact point is not found
    try:
        contact_point_index = np.where(np.isclose(force_nN[points_per_half_period:-1], 0, atol=1))[0][0]+points_per_half_period
        #contact_point_index = adhesion_index
    except Exception as e:
        print(f"Warning: Could not find contact point: {e}")
        contact_point_index = 0
        contact_point_offset = 0
    contact_point_offset = distance_nm[contact_point_index]
    distance_nm = distance_nm - contact_point_offset
    analysis_result["contact_point_index"] = contact_point_index
    analysis_result["contact_point_offset"] = contact_point_offset
    analysis_result["distance_nm"] = distance_nm
    analysis_result["force_nN"] = force_nN

    ### Get max force as maximum point of retract force ###
    max_force =  np.max(force_nN[points_per_half_period:-1])
    max_force_index = np.where(force_nN == max_force)[0][0]
    analysis_result["max_force"] = max_force
    analysis_result["max_force_index"] = max_force_index

    ### Fit contact mechanic model between max force and contact point index ###
    # Change initial and bounds parameter if fitting is not successful
    # Change value of fit_start and fit_end to select fit range
    fit_index_start = int(len(distance_nm)*fit_start)
    #fit_index_start = max_force_index # For full fit range
    fit_index_end = int(len(distance_nm)*fit_end)
    #fit_index_end = contact_point_index # For full fit range Hertz and Sneddon
    #fit_index_end = adhesion_index # For full fit range DMT and JKR
    analysis_result["fit_index_start"] = fit_index_start
    analysis_result["fit_index_end"] = fit_index_end

    if fit_model == 'Linear':
        fit_func = fit_func_linear
        p0_model = ([1, 0])
        bounds_model = ([-np.inf, -np.inf], [np.inf, np.inf]) 
    elif fit_model == 'Hertz':
        fit_func = fit_func_hertz
        p0_model = ([1, 0])
        bounds_model = ([0, -np.inf], [np.inf, np.inf])
    elif fit_model == 'DMT':
        fit_func = fit_func_DMT
        p0_model = ([1, 0, 0.5])
        bounds_model = ([0, -np.inf, 0], [np.inf, np.inf, np.inf])
    elif fit_model == 'JKR':
        fit_func = fit_func_JKR
        p0_model = ([1, 0, 0.5])
        bounds_model = ([0, -np.inf, 0], [np.inf, np.inf, np.inf])
    elif fit_model == 'Sneddon':
        fit_func = fit_func_sneddon
        p0_model = ([1, 0])
        bounds_model = ([0, -np.inf], [np.inf, np.inf])
    else:
        print(f"Warning: Model {fit_model} unknown.")
        return

    try:  # Change x- and y-data indices to adapt fit range
        popt_model_fit, _ = curve_fit(f=fit_func,
                            xdata=np.array(distance_nm[fit_index_start:fit_index_end]),
                            ydata=np.array(force_nN[fit_index_start:fit_index_end]),
                            p0=p0_model,
                            bounds=bounds_model)
        e_modulus = popt_model_fit[0]
        x0 = popt_model_fit[1]
        if fit_model=='DMT' or fit_model=="JKR":
            gamma = popt_model_fit[2]
        else:
            gamma = np.nan
    except Exception as e: # Put NaN if fit was not successful
        print(f"Warning: Could not fit contact mechanic model: {e}")
        e_modulus = np.nan
        x0 = np.nan
        gamma = np.nan
        if fit_model=='Linear' or fit_model=='Hertz' or fit_model=="Sneddon":
            popt_model_fit=[np.nan,np.nan]
        elif fit_model=='DMT' or fit_model=="JKR":
            popt_model_fit=[np.nan,np.nan,np.nan]
        else:
            print(f"Model {fit_model} unknown.")
            return

    if fit_model == 'Linear':
        analysis_result["elasticity"] = e_modulus
    else:
        analysis_result["elasticity"] = e_modulus*1e9
    analysis_result["fit_distance"] = np.array(distance_nm[fit_index_start:fit_index_end])
    analysis_result["fit_force"] = fit_func(np.array(distance_nm[fit_index_start:fit_index_end]), *popt_model_fit)

    ### Uncomment this block for plotting curves ###
    # By choosing index, the curve at the marker is shown
    if i==plot_curve_index:
        try:
            plot_single_curve(analysis_result)
        except Exception as e:
            print(f"Warning: Could not plot force curve: {e}")
            return
    return analysis_result


def analyze_nma_data():
    """ Cuts the interaction signal into segments that are analyzed as single force-distance curves using the free wave signal as distance.
    Assumes that free wave and interaction signal are well synchronized during measurement.
    Transforms the obtained analysis results into 2D matrices. Calls the analysis, post-process (optional) and plot function of the data.

    """
    global meas_data
    global res_list
    global res_map

    image_number_of_line = res_map.map_topography_in_m.shape[0]
    image_points_per_line = res_map.map_topography_in_m.shape[1]
    num_of_curves = int(image_points_per_line * image_number_of_line)
    points_per_period: int = int(len(meas_data.ch_nma_deflection.dataset)/num_of_curves)
    next_print_time = time.time()
    plot_curve_index = row_index * image_points_per_line + column_index

    for i in range(num_of_curves):
        ### Analyze single F-d-curve here ###
        # Cut signal into single curves:
        start_index: int = i * points_per_period
        end_index: int = i * points_per_period + points_per_period
        force_nN = np.array(meas_data.ch_nma_interaction.dataset[start_index:end_index])
        distance_nm = np.array(meas_data.ch_nma_deflection.dataset[start_index:end_index])
        # Analyze curves:
        analysis_result = analyze_force_curve(distance_nm,force_nN, i, plot_curve_index)
        # Append results to list:
        res_list.list_max_force_in_nN.append(analysis_result['max_force'])
        res_list.list_adhesion_in_nN.append(analysis_result['adhesion'])
        res_list.list_elasticity_in_Pa.append(analysis_result['elasticity'])

        ### Print curve number to show progress in console ###
        if time.time() > next_print_time:
            print(f"Analyzed curves: {i+1}/{num_of_curves}, {int(i/num_of_curves*100):d}%")
            print(f"Fitted elasticity: {analysis_result['elasticity']}")
            next_print_time = time.time() + 0.5

    ### Transform lists into image matrix ###
    res_map.map_max_force_in_nN = np.reshape(
        res_list.list_max_force_in_nN, (image_number_of_line, image_points_per_line))
    res_map.map_adhesion_in_nN = np.reshape(
        res_list.list_adhesion_in_nN, (image_number_of_line, image_points_per_line))
    res_map.map_elasticity_in_Pa = np.reshape(
        res_list.list_elasticity_in_Pa, (image_number_of_line, image_points_per_line))
    

def post_process_nma_data(image_size_x_um):
    """ Includes all (optional) operations to post process the obtained datasets after analysis.

    """
    global res_map
    ### Remove outliers that are not in the confidence interval (sigma): ###
    res_map.map_topography_in_m = remove_outliers(res_map.map_topography_in_m, sigma=3)
    res_map.map_max_force_in_nN = remove_outliers(res_map.map_max_force_in_nN, sigma=3)
    res_map.map_adhesion_in_nN = remove_outliers(res_map.map_adhesion_in_nN, sigma=3)
    res_map.map_elasticity_in_Pa = remove_outliers(res_map.map_elasticity_in_Pa, sigma=3)

    ### Interpolate nan values: ###
    res_map.map_topography_in_m = interpolate_matrix(res_map.map_topography_in_m)
    res_map.map_max_force_in_nN = interpolate_matrix(res_map.map_max_force_in_nN)
    res_map.map_adhesion_in_nN = interpolate_matrix(res_map.map_adhesion_in_nN)
    res_map.map_elasticity_in_Pa = interpolate_matrix(res_map.map_elasticity_in_Pa)
    ### Level topography data using line fit: ###
    res_map.map_topography_in_m  = line_fit(res_map.map_topography_in_m , 1, image_size_x_um)

def plot_nma_maps():
    """ Plots the obtained datasets as image and histogram.

    """
    global res_map

    for map_name, map_values in vars(res_map).items():
        plt.title(f"{map_name}")
        plt.imshow(map_values, origin="lower", cmap="gray")
        plt.scatter(column_index, row_index, color='red', s=100, marker='x')
        plt.show()
        plt.title(f"{map_name}")
        plt.hist(map_values.flatten(), bins = int(np.sqrt(map_values.size)))
        plt.show()

def plot_single_curve(curve_dict: dict):
    """ Plots a single force distance curve based on the analysis result

    """
    distance_nm = curve_dict['distance_nm']
    force_nN = curve_dict['force_nN']
    points_per_half_period = curve_dict['points_per_half_period']
    force_nN = curve_dict['force_nN']
    baseline_index_start = curve_dict['baseline_index_start']
    baseline_index_end = curve_dict['baseline_index_end']
    max_force_index = curve_dict['max_force_index']
    adhesion_index = curve_dict['adhesion_index']
    contact_point_index = curve_dict['contact_point_index']
    fit_index_start =  curve_dict['fit_index_start']
    fit_index_end =  curve_dict['fit_index_end']

    plt.plot(distance_nm[0:points_per_half_period], force_nN[0:points_per_half_period])
    plt.plot(distance_nm[points_per_half_period:-1], force_nN[points_per_half_period:-1])
    plt.plot(curve_dict["fit_distance"], curve_dict["fit_force"])
    plt.scatter(distance_nm[baseline_index_start:baseline_index_end], force_nN[baseline_index_start:baseline_index_end], alpha=0.5)
    plt.scatter(distance_nm[max_force_index], force_nN[max_force_index])
    plt.scatter(distance_nm[adhesion_index], force_nN[adhesion_index])
    plt.scatter(distance_nm[contact_point_index], force_nN[contact_point_index], marker="x", s=50, color="black")
    plt.scatter(distance_nm[fit_index_start], force_nN[fit_index_start], marker="*", color="gray")
    plt.scatter(distance_nm[fit_index_start:fit_index_end], force_nN[fit_index_start:fit_index_end], marker="*", alpha=0.1,color="black")
    plt.scatter(distance_nm[fit_index_end], force_nN[fit_index_end], marker="*", color="black")
    plt.show()

    print(f'{curve_dict["adhesion"]=}')
    print(f'{curve_dict["max_force"]=}')
    print(f'{curve_dict["elasticity"]=}')
    print(f'{curve_dict["fit_index_start"]=}')
    print(f'{curve_dict["fit_index_end"]=}')


### Conversion function ###
def convert_file(source_file:pathlib.Path, target_file:pathlib.Path) -> bool:
    """ Converts a .nhf file to .gwy file

    Parameters
    ----------
        source_file:pathlib.Path
            File to be converted.
        target_file:pathlib.Path
            Converted file.

    Return
    ------
        done:bool
            Returns True if conversion was successful.

    """
    global meas_data
    global res_list
    global res_map

    ### Open file instance ###
    nhf_file = nhf_reader.NHFFileReader(verbose=True)
    if not nhf_file.read(source_file):
        print("Could not read file")
        exit()
    if nhf_file.version() < (1,1):
        print(f"Unknown file version: {nhf_file.version()}")
        exit()
    print(f"Found {nhf_file.measurement_count()} measurements in file:")
    print(nhf_file.measurement.keys())

    ### Open group instances in file ###
    print("Reading first measurement in file")
    measurement_name = nhf_file.measurement_name(0)
    measurement = nhf_file.measurement[measurement_name]
    segment_name = 'Forward' # Choose 'Forward' or 'Backward' scan
    segment = measurement.segment[segment_name]
    
    ### Read image attributes ###
    image_points_per_line = measurement.dataset_size_x
    print(f"{image_points_per_line=}")
    image_number_of_line  = measurement.dataset_size_y
    print(f"{image_number_of_line=}")
    image_size_x_um = 1e6 * measurement.dataset_range_x
    print(f"{image_size_x_um=}")    
    image_size_y_um = 1e6 * measurement.dataset_range_y
    print(f"{image_size_y_um=}")
    deflection_sensitivity = measurement.attribute['spm_probe_calibration_deflection_sensitivity']
    spring_constant = measurement.attribute['spm_probe_calibration_spring_constant']

    ### Read channels ###
    print("Reading channels")
    ch_topography = segment.read_channel('Position Z')
    res_map.map_topography_in_m = np.flipud(np.reshape(np.array(ch_topography.dataset), (image_number_of_line, image_points_per_line)))
    # ch_nma_free_wave = measurement.read_channel('NMA Free Wave')

    meas_data.ch_nma_deflection = segment.read_channel('NMA Deflection')
    meas_data.ch_nma_deflection.dataset = np.array(meas_data.ch_nma_deflection.dataset, dtype='f') # Reduce data to float
    if(meas_data.ch_nma_deflection.unit =='V'):
        meas_data.ch_nma_deflection.dataset *= deflection_sensitivity * 1E9
    elif(meas_data.ch_nma_deflection.unit =='m'):
        meas_data.ch_nma_deflection.dataset *= 1E9
    else:
        print(f"{meas_data.ch_nma_deflection.name} unit unknown and not transformed.")

    meas_data.ch_nma_interaction = segment.read_channel('NMA Interaction')
    meas_data.ch_nma_interaction.dataset = np.array(meas_data.ch_nma_interaction.dataset, dtype='f') # Reduce data to float
    if(meas_data.ch_nma_interaction.unit =='V'):
        meas_data.ch_nma_interaction.dataset *= deflection_sensitivity * spring_constant * 1E9
    elif(meas_data.ch_nma_interaction.unit =='m'):
        meas_data.ch_nma_interaction.dataset *= spring_constant * 1E9
    elif(meas_data.ch_nma_interaction.unit =='N'):
        meas_data.ch_nma_interaction.dataset *= 1E9
    else:
        print(f"{meas_data.ch_nma_interaction.name} unit unknown and not transformed.")
 
    ### Analyze F-curves ###
    print("Start Analyzing...")
    analyze_nma_data()
    ### Optional: Do postprocessing of the maps ###
    # Comment if not needed
    #print("Start Postprocessing...")
    #post_process_nma_data(image_size_x_um)
    ### Optional: Plot the maps and histograms ###
    print("Start Plotting...")
    plot_nma_maps()
    print("Exporting Data...")
    ### Export data to gwyddion file ###
    if fit_model == "Linear":
        data_units = ['m', 'N', 'N', 'N/m']
        data_labels = ['Topography', 'Max_Force', 'Adhesion', 'Slope']
    else:
        data_units = ['m', 'N', 'N', 'Pa']
        data_labels = ['Topography', 'Max_Force', 'Adhesion', 'Elasticity']
    done = gwy_export.savedata_gwy(target_file, 
                            size_info=gwy_export.GwySizeInfo(
                                x_range=image_size_x_um*1e-6,
                                y_range=image_size_y_um*1e-6,
                                unit_xy="m"
                            ),
                            data_sets=[res_map.map_topography_in_m, res_map.map_max_force_in_nN*1e-9, res_map.map_adhesion_in_nN*1e-9, res_map.map_elasticity_in_Pa],
                            data_labels=data_labels,
                            data_units=data_units)
    if done:
        print(f"Saved result in gwyddion file at:\n{target_file}")
    else:
        print(f"Could not save gwyddion file to: \n{target_file}") 
    del measurement
    del segment
    del nhf_file
    print("Done.")
    return True


### Fit functions ###
def fit_func_linear(x: np.ndarray, slope: float, offset: float) -> np.ndarray:
    """
    Linear function that calculates the value of a line given a set of x values, slope, and y-intercept.

    Parameters
    ----------
        x: float or array-like
            The independent variable(s) for the linear function.
        slope: float
            The slope of the line.
        offset: float
            The y-intercept of the line.

    Returns
    -------
        y: float or array-like
            The dependent variable(s) for the linear function, calculated as slope*x + offset.
    """
    return slope*x+offset


def fit_func_hertz(x, e_eff, x0):
    """
    Function that calculates the tip sample force based on Hertz model.

    Parameters
    ----------
        x: float or array-like
            The independent variable(s) for the linear function.
        e_eff: float
            The effective youngs modulus of cantilever and sample.
        x0: float
            The contact point of the measurement.

    Returns
    -------
        y: float or array-like
            The calculated force based on effective youngs modulus and cantilever tip radius.
    """
    return a0*e_eff*(x0-x)**1.5


def fit_func_DMT(x, e_eff, x0, gamma):
    """
    Function that calculates the tip sample force based on Hertz model.

    Parameters
    ----------
        x: float or array-like
            The independent variable(s) for the linear function.
        e_eff: float
            The effective youngs modulus of cantilever and sample.
        x0: float
            The contact point of the measurement.

    Returns
    -------
        y: float or array-like
            The calculated force based on effective youngs modulus and cantilever tip radius.
    """
    return a0*e_eff*(x0-x)**1.5-a1*gamma


def fit_func_JKR(x, e_eff, x0, gamma):
    """
    Function that calculates the tip sample force based on simplified JKR model.

    Parameters
    ----------
        x: float or array-like
            The independent variable(s) for the linear function.
        e_eff: float
            The effective youngs modulus of cantilever and sample.
        x0: float
            The contact point of the measurement.
        gamma: float
            The adhesion energy.

    Returns
    -------
        y: float or array-like
            The calculated force based on effective youngs modulus and cantilever tip radius.
    """
    return a0*e_eff*(x0-x)**1.5-a2*gamma


def fit_func_sneddon(x, e_sample, x0):
    """
    Function that calculates the tip sample force based on Sneddon model.

    Parameters
    ----------
        x: float or array-like
            The independent variable(s) for the linear function.
        e_sample: float
            The youngs modulus of the sample.
        x0: float
            The contact point of the measurement.

    Returns
    -------
        y: float or array-like
            The calculated force based on sample youngs modulus, poisson ratio and opening angle of cantilever tip.
    """
    return a3*e_sample*(x0-x)**2


### Auxiliary functions ###
def remove_outliers(matrix: np.ndarray, sigma=3.0)->np.ndarray:
    """ Removes outliers of 2D matrix based on sigma as width of trust interval

    Parameters
    ----------
        matrix: np.ndarray
            Contains matrix to be modified.
        sigma: float
            Width of trust interval.

    Return
    ------
        matrix: np.ndarray
            Contains matrix with removed outliers.

    """
    matrix = matrix.astype(float)
    z_scores = np.abs((matrix - np.nanmean(matrix)) / np.nanstd(matrix))
    outliers = z_scores > sigma
    matrix[outliers] = np.nan
    return matrix


def interpolate_matrix(matrix: np.ndarray)->np.ndarray:
    """ Interpolates nan data of 2D matrix to overwrite empty data.

    Parameters
    ----------
        matrix: np.ndarray
            Contains matrix to be modified.

    Return
    ------
        matrix: np.ndarray
            Contains matrix with interpolated data.

    """
    n_rows, n_cols = matrix.shape
    x = np.arange(n_cols)
    y = np.arange(n_rows)
    xx, yy = np.meshgrid(x, y)
    valid_indices = np.where(~np.isnan(matrix))
    matrix = griddata(valid_indices, matrix[valid_indices], (xx, yy), method='linear').T
    return matrix


def line_fit(matrix: np.ndarray, order: int, image_size_x: int) -> np.ndarray:
    """ Levels matrix data by subtracting linewise the polynomial background.

    Parameters
    ----------
        matrix: np.ndarray
            Contains matrix data to be leveld.
        order: int
            Order of polynom to be fitted.
        image_size_x: int
            Size of obtained image.

    Return
    ------
        result_matrix: np.ndarray
            Contains leveld data in a matrix.

    """
    result_matrix: np.ndarray = np.zeros(np.shape(matrix))
    for i in range(len(matrix)):
        x_axis = np.linspace(0, image_size_x, len(matrix[0]))
        p = np.polyfit(x_axis, matrix[i, :], order)
        f = np.poly1d(p)
        fit_array: np.ndarray = f(x_axis)
        result_matrix[i, :] = matrix[i, :] - fit_array
    return result_matrix


def get_demo_app_folder() -> pathlib.Path:
    return pathlib.Path(os.path.abspath(__file__)).parent


def process_all_files_in_folder(folder:pathlib.Path, from_suffix:str, to_suffix) -> bool:
    done = True
    list_of_source_files = [file for file in pathlib.Path(folder).glob(f'**/*{from_suffix}')]
    if len(list_of_source_files) > 0:
        for current_file in list_of_source_files:
           done=process_file(current_file,from_suffix,to_suffix)
           if not done:
               break
    else:
        print(f"No source-files to found in {folder}")
    return done


def process_file(file:pathlib.Path, from_suffix:str, to_suffix) -> bool:
    done = True
    if file.is_file():
        print(f"Processing file: {file.name}")  
        target_file = file.with_suffix(to_suffix)
        done = convert_file(file, target_file)
        if not done:
            print("Error while processing data. Abort.")
    else:
        print(f"{file} not found.")
    return done



if __name__ == "__main__":
    cmd_line_option_ask_folder = False
    cmd_line_option_ask_file = True
    cmd_line_option_process_file = False
    path_of_the_directory = get_demo_app_folder() / "example_data"
    if len(sys.argv) >= 2:
        if sys.argv[1] == "-ask_folder": cmd_line_option_ask_folder = True
        if sys.argv[1] == "-ask_file": cmd_line_option_ask_file = True
        if sys.argv[1] == "-process_file": cmd_line_option_process_file = True
    else:
        cmd_line_option_ask_file = True
    
    if cmd_line_option_ask_folder:
        path_of_the_directory = fileutil.ask_folder()
        if path_of_the_directory is not None:
            process_all_files_in_folder(path_of_the_directory, ".nhf", ".gwy")
        else:
            print("no folder was given")
    elif cmd_line_option_ask_file:
        path_of_the_directory = fileutil.ask_open_file()
        if path_of_the_directory is not None:
            process_file(path_of_the_directory, ".nhf", ".gwy")
        else:
            print("no file was given")
    elif cmd_line_option_process_file:
        path_of_the_directory = None
        path_of_the_directory = pathlib.Path(sys.argv[2])
        if path_of_the_directory is not None:
            process_file(path_of_the_directory, ".nhf", ".gwy")
        else:
            print("no file was given")
    else:
        print("no option selected")
        print("available options:")
        print("-ask_folder")
        print("-ask_file")
        print("-process_file")

# %%
### Continue to access measurement data, result maps and lists here: ###
# E.g. Plot signal or map, further post-processing and export of data...
# Uncomment block for test
"""
plt.plot(meas_data.ch_nma_deflection.dataset[0:1000])
plt.show()
plt.imshow(res_map.map_adhesion_in_nN)
plt.show()
"""
