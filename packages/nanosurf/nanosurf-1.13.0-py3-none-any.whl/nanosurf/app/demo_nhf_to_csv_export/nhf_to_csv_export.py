'''
10.07.2025 PMA
11.08.2028 DBR
Copyright Nanosurf AG 2025

General NHF to CSV converter, works for
Spec Points, Grids, Images, WaveMode NMA Data
Can be executed from Visual Studio Code (Run Cell, Ctrl+Enter) -> Requires Jupyter Extension
From CMD-Line: python nhf_to_csv_export.py [-h] [-ask] [-nma] [-dir] [filename] 

positional arguments:
  filename            Full path and filename to an nhf-file     

options:
  -h, --help          show this help message and exit
  -ask, --ask         Show a file dialog to ask for file
  -nma, --export_nma  Export the nma data files if any
  -dir, --dir         Create a directory for exported file

Tested with:
# Python 3.13.5
# Nanosurf Library 1.13.0
# Nanosurf Studio 9.0 (Fluorine) and higher
'''

#%%
import numpy as np
import pathlib
import json
import argparse
from nanosurf.lib.util import nhf_reader   
from nanosurf.lib.util import fileutil

list_of_nma_data_channels  = ['Fast In Deflection (16bit)', 'NMA Deflection', 'NMA Deflection Baseline']
list_of_channels_to_ignore = ['NMA Interaction']
   
class Measurement_Info:
    def __init__(self):
        self.created: str = ""
        self.scan_head_type: str = ""
        self.deflection_sensitivity: float = 0.0
        self.spring_constant: float = 0.0
        self.cycle_repetitions: str = ""
        self.group_type: str = ""
        self.target_file_name_mask: str = ""
        self.target_directory: pathlib.Path = pathlib.Path("")

def export_image_channel(ch:nhf_reader.NHFDataset, m_info:Measurement_Info):
    csv_file_name = f"{m_info.target_file_name_mask}_{ch.parent.name}_{ch.name}.txt"

    print(f"Exporting '{csv_file_name}'...")
    with open(m_info.target_directory / csv_file_name,"w") as f_hdl:
        # --- header
        f_hdl.write("file_name = {}\n".format(ch.parent.parent._file_hdl._filename.name))
        f_hdl.write("file_type = {}\n".format(m_info.group_type))
        f_hdl.write("created = {}\n".format(m_info.created))
        f_hdl.write("scanhead_type = {}\n".format(m_info.scan_head_type))
        f_hdl.write("deflection_sensitivity = {}\n".format(m_info.deflection_sensitivity))
        f_hdl.write("spring_constant = {}\n".format(m_info.spring_constant))
        f_hdl.write("offset_x = {}\n".format(ch.dataset_offset_x))
        f_hdl.write("offset_y = {}\n".format(ch.dataset_offset_y))
        f_hdl.write("size_x = {}\n".format(ch.dataset_range_x))
        f_hdl.write("size_y = {}\n".format(ch.dataset_range_x))
        f_hdl.write("points_x = {}\n".format(ch.dataset_size_x))
        f_hdl.write("points_y = {}\n".format(ch.dataset_size_x))
        f_hdl.write("rotation = {}\n".format(ch.dataset_rotation_z))
        f_hdl.write("number_of_segments = {}\n".format(ch.parent.parent.segment_count()))
        f_hdl.write("number_of_channels = {}\n".format(ch.parent.channel_count()))
        f_hdl.write("segment_name = {}\n".format(ch.parent.name))
        f_hdl.write("channel_name = {}\n".format(ch.name))
        f_hdl.write("channel_unit = {}\n".format(ch.unit))
        f_hdl.write("!\n")
        
        # --- data
        if ch.has_nan_values:
            image_data = ch.get_masked_dataset()
        else:
            image_data = ch.dataset
        np.savetxt(f_hdl, image_data, fmt='%.8e',delimiter=',')

def export_spec_point(measurement:nhf_reader.NHFMeasurement, m_info:Measurement_Info, current_spec:int, num_of_specs:int):

    # create data array of all channels and segments of a measurement
    number_of_points = int(sum(segment.spec_data_points[current_spec] for segment in measurement.segments))
    number_of_channels = measurement.segments[0].channel_count()

    csv_data = np.full((number_of_points, number_of_channels), np.nan)
    csv_offset = 0

    for seg in measurement.segments:
        data_offset = int(seg.spec_offsets[current_spec])
        data_length = int(seg.spec_data_points[current_spec])
        print(f"{data_offset=}, {data_length=}")
        for ch_index in range(seg.channel_count()):
            ch = seg.read_channel(ch_index, as_matrix=False)
            csv_data[csv_offset : (csv_offset + data_length), ch_index] = ch.dataset[data_offset : (data_offset + data_length)]
        csv_offset += data_length

    # start export 
    csv_file_name = f"{m_info.target_file_name_mask}_Spec{current_spec:05d}.txt"

    try:
        seg_configs:list[str] = [json.loads(s.attribute["segment_configuration"]) for s in measurement.segments]
    except Exception:
        seg_configs = []
        
    print(f"Exporting '{csv_file_name}'...")
    with open(m_info.target_directory / csv_file_name,"w") as f_hdl:
        f_hdl.write("file_name = {}\n".format(measurement._file_hdl._filename.name))
        f_hdl.write("file_type = {}\n".format(m_info.group_type))
        f_hdl.write("created = {}\n".format(m_info.created))
        f_hdl.write("scanhead_type = {}\n".format(m_info.scan_head_type))
        f_hdl.write("deflection_sensitivity = {}\n".format(m_info.deflection_sensitivity))
        f_hdl.write("spring_constant = {}\n".format(m_info.spring_constant))
        f_hdl.write("offset_x = {}\n".format(measurement.dataset_offset_x))
        f_hdl.write("offset_y = {}\n".format(measurement.dataset_offset_y))
        f_hdl.write("size_x = {}\n".format(measurement.dataset_range_x))
        f_hdl.write("size_y = {}\n".format(measurement.dataset_range_x))
        f_hdl.write("points_x = {}\n".format(measurement.dataset_size_x))
        f_hdl.write("points_y = {}\n".format(measurement.dataset_size_x))
        f_hdl.write("rotation = {}\n".format(measurement.dataset_rotation_z))
        f_hdl.write("cycle_repetitions = {}\n".format(m_info.cycle_repetitions))
        f_hdl.write("spec_num = {}\n".format(current_spec))
        f_hdl.write("number_of_specs = {}\n".format(num_of_specs))
        f_hdl.write("number_of_segments = {}\n".format(measurement.segment_count()))
        f_hdl.write("number_of_channels = {}\n".format(measurement.segments[0].channel_count()))
        f_hdl.write("segment_names = {}\n".format(measurement.segment_list()))
        for s_index, s_config in enumerate(seg_configs):
            f_hdl.write(f"segment_config_{s_index} = {s_config}\n")
        f_hdl.write("!\n")
        # Write list of channel names with their units
        channel_header = ""
        for ch in measurement.segments[0].channels:
            channel_header += f"{ch.name} ({ch.unit}), "
        f_hdl.write(f"{channel_header.removesuffix(", ")}\n")
        # write data
        np.savetxt(f_hdl, csv_data, fmt='%.8e',delimiter=',')

def export_free_wave_channel(m:nhf_reader.NHFMeasurement, m_info:Measurement_Info):
    
    # search for free wave mode data
    h5_free_wave_dataset = m.find_dataset_by_attribute_value("signal_id","wavemode_free_wave") 
    if h5_free_wave_dataset is None:
        print("Warning: Could not find free wave data")
        return
    
    ch_name = str(h5_free_wave_dataset.attrs["signal_name"])
    ch_free_wave = m.read_channel(ch_name, as_matrix=False)
    
    # start export 
    csv_file_name = f"{m_info.target_file_name_mask}_{ch_free_wave.name}.txt"

    print(f"Exporting '{csv_file_name}'...")
    with open(m_info.target_directory / csv_file_name,"w") as f_hdl:

        f_hdl.write("file_name = {}\n".format(m._file_hdl._filename.name))
        f_hdl.write("file_type = {}\n".format(m_info.group_type))
        f_hdl.write("created = {}\n".format(m_info.created))
        f_hdl.write("scanhead_type = {}\n".format(m_info.scan_head_type))
        f_hdl.write("deflection_sensitivity = {}\n".format(m_info.deflection_sensitivity))
        f_hdl.write("spring_constant = {}\n".format(m_info.spring_constant))
        f_hdl.write("offset_x = {}\n".format(m.dataset_offset_x))
        f_hdl.write("offset_y = {}\n".format(m.dataset_offset_y))
        f_hdl.write("size_x = {}\n".format(m.dataset_range_x))
        f_hdl.write("size_y = {}\n".format(m.dataset_range_x))
        f_hdl.write("points_x = {}\n".format(m.dataset_size_x))
        f_hdl.write("points_y = {}\n".format(m.dataset_size_x))
        f_hdl.write("rotation = {}\n".format(m.dataset_rotation_z))
        f_hdl.write("number_of_segments = {}\n".format(m.segment_count()))
        try:
            time_shift = float(m.attribute['wavemode_free_wave_phase_delay'])
            amp_correction = float(m.attribute['wavemode_free_wave_amplitude_correction'])
        except KeyError:
            time_shift = 0.0
            amp_correction = 1.0
        f_hdl.write("wavemode_time_shift = {}\n".format(time_shift))
        f_hdl.write("wavemode_amplitude_correction = {}\n".format(amp_correction))
        f_hdl.write("!\n")

        # --- data
        if ch_free_wave.has_nan_values:
            ch_data = ch_free_wave.get_masked_dataset()
        else:
            ch_data = ch_free_wave.dataset
        np.savetxt(f_hdl, ch_data, fmt='%.8e',delimiter=',')

def export_nma_data_channel(ch:nhf_reader.NHFDataset, m_info:Measurement_Info):
    csv_file_name = f"{m_info.target_file_name_mask}_{ch.parent.name}_{ch.name}.txt"

    print(f"Exporting '{csv_file_name}'...")
    with open(m_info.target_directory / csv_file_name,"w") as f_hdl:
        # --- header
        f_hdl.write("file_name = {}\n".format(ch.parent.parent._file_hdl._filename.name))
        f_hdl.write("file_type = {}\n".format(m_info.group_type))
        f_hdl.write("created = {}\n".format(m_info.created))
        f_hdl.write("scanhead_type = {}\n".format(m_info.scan_head_type))
        f_hdl.write("deflection_sensitivity = {}\n".format(m_info.deflection_sensitivity))
        f_hdl.write("spring_constant = {}\n".format(m_info.spring_constant))
        f_hdl.write("offset_x = {}\n".format(ch.dataset_offset_x))
        f_hdl.write("offset_y = {}\n".format(ch.dataset_offset_y))
        f_hdl.write("size_x = {}\n".format(ch.dataset_range_x))
        f_hdl.write("size_y = {}\n".format(ch.dataset_range_x))
        f_hdl.write("points_x = {}\n".format(ch.dataset_size_x))
        f_hdl.write("points_y = {}\n".format(ch.dataset_size_x))
        f_hdl.write("rotation = {}\n".format(ch.dataset_rotation_z))
        f_hdl.write("number_of_segments = {}\n".format(ch.parent.parent.segment_count()))
        f_hdl.write("number_of_channels = {}\n".format(ch.parent.channel_count()))
        f_hdl.write("segment_name = {}\n".format(ch.parent.name))
        f_hdl.write("channel_name = {}\n".format(ch.name))
        f_hdl.write("channel_unit = {}\n".format(ch.unit))
        try:
            time_shift = float(ch.parent.parent.attribute['wavemode_free_wave_phase_delay'])
            amp_correction = float(ch.parent.parent.attribute['wavemode_free_wave_amplitude_correction'])
        except KeyError:
            time_shift = 0.0
            amp_correction = 1.0
        f_hdl.write("wavemode_time_shift = {}\n".format(time_shift))
        f_hdl.write("wavemode_amplitude_correction = {}\n".format(amp_correction))
        f_hdl.write("!\n")

        # --- data
        if ch.has_nan_values:
            nma_data = ch.get_masked_dataset()
        else:
            nma_data = ch.dataset
            
        # changing from shape(n,1) to shape(1,n) speeds up writing of np.savetxt() by about factor 4
        # to keep output format of single row per data point the delimiter is '\n' instead of ','.
        np.savetxt(f_hdl, nma_data.reshape(1, -1), fmt='%.8e',delimiter='\n')


def export_image_measurement(m:nhf_reader.NHFMeasurement, m_info:Measurement_Info):
    for s in m.segments:
        for ch in s.channels:
            if ch.name not in (list_of_nma_data_channels + list_of_channels_to_ignore):
                export_image_channel(s.read_channel(ch.name, as_matrix=True), m_info)
    
def export_spec_measurement(measurement:nhf_reader.NHFMeasurement, m_info:Measurement_Info):
    num_spec = measurement.dataset_size_x * measurement.dataset_size_y
    print(f"Number of Spec-Curves: {num_spec}")
    for i in range(num_spec):        
        export_spec_point(measurement, m_info, i, num_spec)
    
def export_nma_measurement(m:nhf_reader.NHFMeasurement, m_info:Measurement_Info):
    export_free_wave_channel(m, m_info)
    for s in m.segments:
        for ch in s.channels:
            if ch.name in list_of_nma_data_channels and ch.name not in list_of_channels_to_ignore:
                export_nma_data_channel(s.read_channel(ch.name, as_matrix=False), m_info)
    
def get_measurement_info(m:nhf_reader.NHFMeasurement, target_directory:pathlib.Path) -> Measurement_Info:
    measurement_info = Measurement_Info()
    try:
        measurement_info.scan_head_type = "DriveAFM"
        measurement_info.created = m.attribute['created'] 
        measurement_info.group_type = m.attribute["group_type"]
        measurement_info.deflection_sensitivity = float(m.attribute['spm_probe_calibration_deflection_sensitivity'])
        measurement_info.spring_constant = float(m.attribute['spm_probe_calibration_spring_constant'])
        measurement_info.cycle_repetitions = str(m.attribute['cycle_repetitions']) if 'cycle_repetitions' in m.attribute else ""
    except KeyError:
        pass
    measurement_info.target_file_name_mask = m._file_hdl._filename.stem
    measurement_info.target_directory = target_directory
    return measurement_info

def export_file(file_path:pathlib.Path | str, target_directory:pathlib.Path, export_nma:bool=False):
    try:
        with nhf_reader.NHFFileReader(file_path) as nhf_file:
            file_version = nhf_file.version()
            if file_version >= (2,0) and file_version < (3,0):

                for m in nhf_file.measurements:
                    m_info = get_measurement_info(m, target_directory)    

                    match m.measurement_type:
                        case nhf_reader.NHFMeasurementType.Spectroscopy:
                            export_spec_measurement(m, m_info)
                        case nhf_reader.NHFMeasurementType.Image:
                            export_image_measurement(m, m_info)
                        case nhf_reader.NHFMeasurementType.WaveModeNMA:
                            export_image_measurement(m, m_info)
                            if not export_nma:
                                print('Exporting NMA may take a while...')
                                export_nma = input('Export NMA Data? (y/n)') == 'y'
                            if export_nma:
                                export_nma_measurement(m, m_info)
                        case _:
                            print(f"Skip measurement '{m.name}'. Don't know how to export ")
            else:
                print(f"nhf-file with version {file_version} is not supported.")                
    except Exception as e:
        print(f"Could not read file: {file_path}.\nReason: {e}")

# Main Function ---------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exports data from Nanosurf nhf-files to text file(s)")
    parser.add_argument("filename", help="Full path and filename of a nhf-file", nargs="?", type=str,default="")
    parser.add_argument("-ask", "--ask", help="Show a file dialog to ask for a file",  action="store_true", default=False)
    parser.add_argument("-nma", "--export_nma", help="Export the nma data files if any",  action="store_true", default=False)
    parser.add_argument("-dir", "--dir", help="Create a directory for exported file", action="store_true", default=False)

    args = parser.parse_args()
    file_path = str(args.filename)
    export_nma = bool(args.export_nma)
    save_into_directory = bool(args.dir)
    ask_for_file = bool(args.ask)

    if ask_for_file:
        file_path = fileutil.ask_open_file(suffix_mask="nhf")
        if file_path is None:
            exit(0)

    source_file = pathlib.Path(file_path)
    if not source_file.is_file():
        print(f"Error: File '{file_path}' does not exists")
        exit(0)

    target_directory = source_file.parent
    if save_into_directory:
        target_directory = source_file.parent / source_file.stem
        if not fileutil.create_folder(target_directory):
            print(f"Error: Could not create target directory: {target_directory}")        
            exit(0)
    
    export_file(file_path, target_directory, export_nma)
