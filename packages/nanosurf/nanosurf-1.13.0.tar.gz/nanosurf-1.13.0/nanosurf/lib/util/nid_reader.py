"""Nanosurf nid-file reader implementation for image, spec and FFT data
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import re
import numpy as np
import time
import pathlib 
import configparser

class ThermalTune():
    def __init__(self) -> None:
        self.q_factor = 0.0
        self.peak_freq = 0.0
        self.peak_freq_unit = ""
        self.peak_amp = 0.0
        self.peak_amp_unit = ""
        self.spring_const = 0.0
        self.spring_const_unit = ""

class ImageData():
    def __init__(self) -> None:
        self.forward : np.ndarray = None
        self.backward : np.ndarray = None
        self.forward_2nd : np.ndarray = None
        self.backward_2nd : np.ndarray = None

class SpecData():
    def __init__(self) -> None:
        self.forward : np.ndarray = None
        self.backward : np.ndarray = None
        self.forward_pause : np.ndarray = None
        self.backward_pause : np.ndarray = None

class SpectrumData():
    def __init__(self) -> None:
        self.fft : np.ndarray = None
        self.fit : np.ndarray = None
        self.sweep : np.ndarray = None
        self.sweep_sho : np.ndarray = None

class NIDData():
    def __init__(self) -> None:
        self.image : ImageData = None
        self.spectroscopy : SpecData = None
        self.spectrum : SpectrumData = None

class NIDDataInfo():
    def __init__(self) -> None:
        self.spec_pos_map : dict[str] = None
        self.image_dim_info : dict[str] = None
        self.image_offset : dict[str] = None

class NIDHeaderInfo():
    def __init__(self) -> None:
        self.sections : configparser.ConfigParser = None
        self.thermal_tune : ThermalTune = None
        self.cantilever : dict[str] = None

class NIDFileReader():
    def __init__(self, filename: pathlib.Path=None, verbose=False):
        self.init_result()
        self._filename = filename
        self._file_id = None
        self._verbose = verbose
        # names of the channels that can be opened.  Can be added to.
        self._data_names = ['Spec forward', 'Spec backward', 'Spec fwd pause', 'Spec bwd pause',
                           'Scan forward', 'Scan backward', '2nd scan forward', '2nd scan backward',
                           'Frequency sweep', 'Frequency sweep SHO', 'Spectrum FFT', 'Spectrum Fit']
        self._data_types = [1, 1, 1, 1, 0, 0, 0, 0, 2, 2, 2, 2]
        self._thermal_tune : ThermalTune = None
        self._header = configparser.ConfigParser()
        self._header.optionxform = lambda option: option # preserve upper/lower case
        if filename:
            self.read()

    def init_result(self):
        self.data : NIDData = None
        self.header : NIDHeaderInfo = None
        self.data_param : NIDDataInfo = None

    def read(self, filename: pathlib.Path=None) -> bool:
        """ Open the nid-file with given path for read access. 
        """
        self.init_result()
        if filename is not None:
            self._filename = filename
        try:
            t = time.time()
            
            self._file_id = open(self._filename, 'rb')
            self.read_header()
            self.read_data()
            self._file_id.close()
            self._file_id = None

            self.compose_result()
    
            if self._verbose:
                print(f"Elapsed Time: {time.time()-t:3.2f} sec\n")
       
            return True
        except Exception as e:
            print(e)
            if self._file_id is not None: 
                self._file_id.close()
            self._file_id = None
            self.init_result()
            return False

    def compose_result(self):
        self.data = NIDData()
        self.data.image = self.image
        self.data.spectroscopy = self.spec
        self.data.spectrum = self.spectrum

        self.header = NIDHeaderInfo()
        self.header.sections = self._header
        self.header.thermal_tune = self._thermal_tune
        self.header.cantilever = self._cantilever

        x = dict(zip(['min', 'range', 'units'],
                    [self.param['Dim0Min'], self.param['Dim0Range'], self.param['Dim0Unit']]))
        y = dict(zip(['min', 'range', 'units'],
                    [self.param['Dim1Min'], self.param['Dim1Range'], self.param['Dim1Unit']]))
        z = dict(zip(['min', 'range', 'units'],
                    [self.param['Dim2Min'], self.param['Dim2Range'], self.param['Dim2Unit']]))

        self.data_param = NIDDataInfo()
        self.data_param.image_dim_info = dict(zip(['X', 'Y', 'Z'],[x, y, z]))
        self.data_param.spec_pos_map = dict(zip(['maps'], [self.spec_map]))
        self.data_param.image_offset = dict(zip(['offset'], [self.image_center]))


    def read_header(self) -> bool:
        """ read in the files content"""
        if self._file_id is not None:
            if self._verbose:
                print("Reading Header")

            data_header_part = self._file_id.read().split(b'#!', maxsplit=1)[0]
            header_str = bytearray(data_header_part).decode(encoding="UTF-8")
            self._header.read_string(header_str)

            self.param : dict[str,str] = {}
            groupNames = []
            dataSet = []

            ds = 'DataSet'
            grCnt = int(self._header[ds]['GroupCount'])
            for gr in range(grCnt):
                groupNames.append(self._header[ds]['Gr' + str(gr) + '-Name'])
                gc = int(self._header[ds]['Gr' + str(gr) + '-Count'])

                for g in range(gc):
                    key = 'Gr' + str(gr) + '-Ch' + str(g)
                    if key in self._header[ds]:
                        dataSet.append(self._header[ds][key])

            terms = ['Frame', 'Points', 'Lines', 'SaveBits',
                    'Dim0Min', 'Dim0Range', 'Dim0Unit',
                    'Dim1Min', 'Dim1Range', 'Dim1Unit',
                    'Dim2Min', 'Dim2Range', 'Dim2Unit',
                    'Dim2Name']

            types = [0, 1, 1, 1,
                    2, 2, 0,
                    2, 2, 0,
                    2, 2, 0,
                    0]

            # 0 = string, 1 = integer, 2 = float
            typ = [lambda x:str(x), lambda x:int(x), lambda x:float(x)]
        
            for term, ty in zip(terms, types):
                val = []
                for d in dataSet:
                    h = self._header[d]
                    if term in h:
                        val.append(typ[ty](h[term]))

                self.param[term] = val

            # for spectroscopy with maps
            data_points = []
            for d in dataSet:
                h = self._header[d]
                line_points = []
                if 'LineDim0Min' in h:
                    for key, value in h.items():
                        if re.match(r'LineDim\d*Points', key):
                            line_points.append(int(value))
                data_points.append(np.array(line_points))
            self.param['LinePoints'] = data_points
            
            self._cantilever : dict[str] = {}
            key = 'DataSet\\Calibration\\Cantilever'
            if key in self._header:
                self._cantilever = self._header[key]

            key = 'DataSet\\Calibration\\Scanhead'
            if key in self._header:
                deflection_input = self._header[key]['In5']
                sensitivity = float(deflection_input.split(',')[4]) / 10.0
                self._cantilever['Sensitivity'] = str(sensitivity)

            self.spec_map : np.ndarray = None  
            key = 'DataSet\\SpecInfos'
            if key in self._header:
                n = int(self._header[key]['SubSectionCount'])
                secNames = [self._header[key]['SubSection' + str(i)] for i in range(n)]
                specMode = self._header[key + '\\' + secNames[0]]['SpecMode']
                count = int(self._header[key + '\\' + secNames[1]]['Count'])
                
                self.spec_map = [self._header[key + '\\' + secNames[1]][specMode[:3] + str(i)].split(';') for i in range(count)]
                self.spec_map = np.array(self.spec_map).astype(float)
                
            self.image_center : list[float] = []
            key = 'DataSet\\Parameters\\Imaging'
            if key in self._header:
                self.image_center, *_ = self._get_values(key, 'ScanOffset')
            
            self._thermal_tune : ThermalTune = None
            key = 'DataSet-Info'
            if key in self._header:
                data_set_info = self._header[key]
                if '-- Thermal Tuning --' in data_set_info:
                    self._thermal_tune = ThermalTune()
                    
                    self._thermal_tune.q_factor = float(data_set_info['Q Factor:'])
                    
                    peak_freq = data_set_info['Frequency:']
                    gr = re.search(r'(\d+\.\d+)(\S*)', peak_freq).groups()
                    self._thermal_tune.peak_freq = gr[0]
                    self._thermal_tune.peak_freq_unit = gr[1]
                    
                    spring_c = data_set_info['Spring Constant:']
                    gr = re.search(r'(\d+\.\d+)\s(\S*)', spring_c).groups()
                    self._thermal_tune.spring_const = gr[0]
                    self._thermal_tune.spring_const_unit = gr[1]
                    
                    peak_amp = data_set_info['Peak Value:']
                    gr = re.search(r'(\d+\.\d+)(\S*)', peak_amp).groups()
                    peak_amp = {'Value': gr[0], 'Unit': gr[1]}
                    self._thermal_tune.peak_amp = gr[0]
                    self._thermal_tune.peak_amp_unit = gr[1]
                

    def read_data(self) -> bool:
        """ read in the files data section"""
        if self._file_id is not None:
            if self._verbose:
                print('Reading Data')
            
            self.required_size = int(sum([a*b*c/8 for a, b, c in zip(self.param['Points'],
                                                                self.param['Lines'],
                                                                self.param['SaveBits'])]))
            
            if self.param['SaveBits'][0] == 16:
                dt = np.int16
            elif self.param['SaveBits'][0] == 32:
                dt = np.int32

            q = float(2**self.param['SaveBits'][0])
            z0 = float(q/2)

            self._file_id.seek(-self.required_size, 2) # two means offset from file end
            data_in = np.fromfile(self._file_id, count=self.required_size, dtype=dt).astype(float)
            data_in = (data_in + z0) / q

            data_in = np.split(data_in, np.cumsum([a * b for a, b in zip(self.param['Points'],
                                                                        self.param['Lines'])]))
            data_in.pop()

            data = []
            # reshape and rescale data
            for datain, pts, lns, zran, zmin in zip(data_in,
                                                    self.param['Points'],
                                                    self.param['Lines'],
                                                    self.param['Dim2Range'],
                                                    self.param['Dim2Min']):

                data.append(datain.reshape((lns, pts)).__mul__(zran).__add__(zmin))

            data_crop = []
            for numP, dSet in zip(self.param['LinePoints'], data):
                if numP.any():
                    temp = []
                    for n, d in zip(numP, dSet):
                        temp.append(d[:n])
                    data_crop.append(temp)
                else:
                    data_crop.append(dSet)
            data = np.array(data_crop, dtype=object)

            # this is the index of the channels that will be output.
            idx = [idx for idx, frame in enumerate(self.param['Frame']) if frame in self._data_names]

            # only take data from approved list in name
            data = data[idx]
            frames = np.array(self.param['Frame'])[idx]
            channel = np.array(self.param['Dim2Name'])[idx]

            out = {}
            for frame, chan, dat in zip(frames, channel, data):
                if frame not in out:
                    out[frame] = {}
                if chan not in out[frame]:
                    out[frame][chan] = {}
                out[frame][chan] = np.array(dat).astype(np.float64)
        
            self.image = ImageData()
            self.spec = SpecData()
            self.spectrum = SpectrumData()

            for name, value in out.items():
                dt = self._data_types[self._data_names.index(name)]
                if dt == 0:
                    if name == 'Scan forward':
                        self.image.forward = value
                    elif name == 'Scan backward':
                        self.image.backward = value
                    elif name == '2nd scan forward':
                        self.image.forward_2nd = value
                    elif name == '2nd scan backward':
                        self.image.backward_2nd = value
                    else:
                        pass
                if dt == 1:
                    if name == 'Spec forward':
                        self.spec.forward = value
                    elif name == 'Spec backward':
                        self.spec.backward = value
                    elif name == 'Spec fwd pause':
                        self.spec.forward_pause = value
                    elif name == 'Spec bwd pause':
                        self.spec.backward_pause = value
                    else:
                        pass
                if dt == 2:
                    if name == 'Spectrum FFT':
                        self.spectrum.fft = value
                    elif name == 'Spectrum Fit':
                        self.spectrum.fit= value
                    elif name == 'Frequency sweep':
                        self.spectrum.sweep = value
                    elif name == 'Frequency sweep SHO':
                        self.spectrum.sweep_sho = value
                    else:
                        pass

    def _from_array(self, key, param) -> float:
        return float(self._header[key][param].split(',')[4])

    def _get_values(self, key, param) -> tuple[float, str]:
        string = self._header[key][param]

        ty, val, unit = re.search(r'(\S)\[(.*)\]\*\[(.*)\]', string).groups()
        if ty == 'D':
            val = float(val)
        if ty == 'B':
            val = bool(val)
        if ty == 'L':
            val = int(val)
        if ty == 'V':
            val = [float(v) for v in val.split(',')]
            unit = [str(u) for u in unit.split(',')]
        return (val, unit)

