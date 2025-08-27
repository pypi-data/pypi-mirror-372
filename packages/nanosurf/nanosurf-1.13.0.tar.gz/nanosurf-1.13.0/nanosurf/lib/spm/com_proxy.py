"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""


import enum
import time
import psutil
import win32com.client

import nanosurf.lib.spm.lowlevel as ll
import nanosurf.lib.spm.lowlevel.ctrlunits.factory as ctrl_factory

_known_spm_app_names = [ 'MobileS', 'SPM_S', 'Easyscan2', 'C3000', 'Naio', 'USPM', 'CoreAFM', 'CX']

class Spm():
    """Base class for dealing with Nanosurf SPMs."""
    
    class SystemState(enum.IntEnum):
        Uncal = 0
        Idle = 1
        Approach = 2
        Scan = 3
        Spec = 4
        Litho = 5
        MacroCmd = 6

    class SystemEnvironment(enum.IntEnum):
        Air = 0
        Liquid = 1

    class SystemHealthState(enum.IntEnum):
        OK = 0
        NotResponding = 1
        SimulationMode = 2

    class SystemZAxisIdleMode(enum.IntEnum):
        ZControllerActive = 0
        RetractTip = 1
        KeepLastPos = 2
        AbsolutePos = 3

    class SystemXYAxisIdleMode(enum.IntEnum):
        ImageCenter = 0
        KeepLastPos = 1

    class SystemMotorID(enum.IntEnum):
        Approach = 0
        FootA = 1
        FootB = 2
        FootC = 3
        Focus = 4
        PTEX = 5
        PTEY = 6
        BeamDefX = 7
        BeamDefY = 8
        PhotoDetLateral = 9
        PhotoDetNormal = 10
        LensGimbal = 11

    class SystemMotorDirection(enum.IntEnum):
        Positive = 0
        Negative = 1

    class SystemMotorSpeedLevel(enum.IntEnum):
        VerySlow = 0
        Slow = 1
        Normal = 2
        Fast = 3
        VeryFast = 4

    class ScanAxisRangeModes(enum.IntEnum):
        Off = 0
        FullRange = 1
        ReducedRange = 2

    class XYClosedLoopModes(enum.IntEnum):
        OpenLoop = 0
        ClosedLoop = 1

    class ZClosedLoopModes(enum.IntEnum):
        FixDrive = 0
        FixPosition = 1

    class VideoSource(enum.IntEnum):
        SideView = 0
        TopView = 1

    class ThermalTuneAvgType(enum.IntEnum):
        ExpDecay = 0
        PropWeight = 1

    class ThermalTuneNsfFit(enum.IntEnum):
        Damping = 0
        Sigma = 1
        ResFreq = 2
        QualityFactor = 3
        ResPeakAmpAboveNoise = 4
        NumOfParams = 5

    class ThermalTuneSHOFit(enum.IntEnum):
        WhiteNoise = 0
        PinkNoise = 1
        ResFreq = 2
        QualityFactor = 3
        ResPeakAmpAboveNoise = 4
        NumOfParams = 5

    class OperatingMode(enum.IntEnum):
        User = 0
        STM = 1
        StaticAFM = 2
        DynamicAFM = 3
        PhaseContrast = 4
        ForceModulation = 5
        SpreadingResistivity = 6
        ContPhase = 7
        DeltaF = 8
        LateralForce = 9

    class ApproachStatus(enum.IntEnum):
        Standby = 0
        Initializing = 1
        Approaching = 2
        ApproachDone = 3
        ApproachAborted = 4
        MoveToParkPos = 5
        ParkPosReached = 6
        MoveAway = 7
        MoveToward = 8
        SensorFailed = 9
        LimitFailed = 10
        CalibrationFailed = 12
        UserAbort = 13
        MaxOut = 14
        Initdone = 15
        AdjustingTipPos = 16

    class ApproachMotorStatus(enum.IntEnum):
        Fail = ord('6')
        Error = ord('5')
        NC = ord('4')
        MaxOou = ord('3')
        MinIn = ord('2')
        InRange = ord('1')
        NotDefined = ord('0')
        Unknown = -1

    class AFMSensorStatus(enum.IntEnum):
        ToLow = ord('7')
        Fail = ord('4')
        ToHigh = ord('3')
        OK = ord('1')
        NotDefined = -1

    class DataFilter(enum.IntEnum):
        RAW = 0
        MeanFit = 1
        LineFit = 2
        DerivedData = 3
        ParabolaFit = 4
        PolynomialFit = 5

    class CantileverProperty(enum.IntEnum):
        LeverLength = 0
        LeverWidth = 1
        SpringConst = 2
        AirResonanceFrq = 3
        AirQFactor = 4
        LiquidResonanceFrq = 5
        LiquidQFactor = 6

    class CalibrationSignalID(enum.IntEnum):
        XAxis = 0
        YAxis = 1
        ZAxis = 2
        TipCurrent = 3
        TipVoltage = 4
        Ch0_Deflection = 5
        Ch0_Amp = 6
        Ch0_Pase = 7
        Ch0_Excitation = 8
        UserADC0 = 9
        UserADC1 = 10
        UserDAC0 = 11
        UserDAC1 = 12
        UserADC2 = 13

    class ZControllerLoopMode(enum.IntEnum):
        Run = 0
        Freeze = 1
        StopAndClear = 2

    class DataConversion(enum.IntEnum):
        Binary16 = 0
        Physical = 1
        Binary32 = 2

    class DataLineFlagMask(enum.IntEnum):
        DataValid = 1
        CurrentData = 2

    class ChartType(enum.IntEnum):
        LineGraph = 0
        ColorMap = 1
        View3D = 2
        ShadedColorMap = 3
        DualLineGraph = 4
        XYLineGraph = 5

    class WindowStyle(enum.IntEnum):
        Hide = 0
        Normal = 1
        Minimized = 2
        Maximized = 3
        ShowNoActive = 4
        ShowActive = 5

    class ScanLineMode(enum.IntEnum):
        Standard = 0
        ConstHeight = 1

    class LineScanningMode(enum.IntEnum):
        Standard = 0
        DualScan = 1
        Interlaced = 2
        SecondScanOnly = 3

    class ScanMeasureMode(enum.IntEnum):
        Undefined = 0
        Forward = 1
        Backward = 2
        ForwardBackward = 3

    class ScanMode(enum.IntEnum):
        Continuos = 0
        ContUp = 2
        ContDown = 3

    class ScanGroupID(enum.IntEnum):
        Forward = 0
        Backward = 1

    class ScanFrameDir(enum.IntEnum):
        NotScanning = 0
        Up = 1
        Down = 2

    class ScanChannel(enum.IntEnum):
        Deflection_or_ZCtrlIn = 0
        Topography = 1
        
    class SpecChannel(enum.IntEnum):
        Deflection_or_ZCtrlIn = 0
        Topography = 1
        
    class TipSignalMode(enum.IntEnum):
        CurrentSensinput = 0
        VoltageOutput = 1
        DirectFeedthrough = 2

    class LaserPowerMode(enum.IntEnum):
        Unidefined = 0
        LaserDrive = 1
        LaserPower = 2
        DetectorSensitivity = 3

    class ExcitationSource(enum.IntEnum):
        Internal = 0
        External = 1

    class ExcitationMode(enum.IntEnum):
        PiezoElectric = 0
        PhotoThermal = 1

    class User0InputPol(enum.IntEnum):
        Positive = 0
        Negative = 1

    class ScanHeadID(enum.IntEnum):
        NC = 0
        Unknown = 1
        NaioSTM = 2
        NaioAFM = 9
        NaniteAFM = 12
        FlexAFM = 14
        LensAFM = 15
        DriveAFM = 18
        CoreAFM = 19
        DriveNMA = 20
        DriveMount = 21

    class FrqSweepResult(enum.IntEnum):
        PeakNotFound = 0
        PeakFound = 1
        Running = 2

    class LithoMode(enum.IntEnum):
        User = 0
        STM = 1
        StaticAFM = 2
        DynamicAFM = 3

    class LithoPenMode(enum.IntEnum):
        LiftTip = 0
        ChangeOpMode = 1

    class LeverExcitationMode(enum.IntEnum):
        InternalSource = 0
        ExternalSource = 1

    class DeflectionUnitMode(enum.IntEnum):
        Volt = 0
        Meter = 1
        Newton = 2

    class SpecRepetitionMode(enum.IntEnum):
        List = 0
        Position = 1

    class SpecEndMode(enum.IntEnum):
        KeepLastZPos = 0
        Approached = 1

    class SpecModulatedOutput(enum.IntEnum):
        ZAxis = 0
        TipVoltage = 1
        UserOut1 = 2
        UserOut2 = 3

    class SpecModulationMode(enum.IntEnum):
        FixedLength = 0
        StopByValue = 1

    class SpecStopMode(enum.IntEnum):
        IsLessThan = 0
        IsGreaterThan = 1

    class SpecPauseMode(enum.IntEnum):
        KeepLastZPos = 0
        ZControllerActive = 1

    class SpecModuleLevel(enum.IntEnum):
        Standard = 0
        Advanced = 1

    class SpecCurrentModulationPhase(enum.IntEnum):
        Idle = 0
        ForwardModulation = 1
        ForwardPause = 2
        BackwardModulation = 3
        BackwardPause = 4

    class SpecGroupNo(enum.IntEnum):
        Forward = 0
        Backward = 1
        ForwardPause = 2
        BackwardPause = 3

    class StageState(enum.IntEnum):
        IdleUnreferenced = 1
        Idle = 2
        Moving = 3
        BackwardPause = 3

    class CantileverGUID():
        AN2_200 = "{BD61D124-8350-4464-BFE4-1D8A156E4913}"
        GLA_1 = "{9E2BA28D-D843-41bf-8F62-05502B3EDB18}"
        ACL_A = "{ABB75273-9543-431a-B681-C79B533DD9E6}"
        ANSCM = "{40AEA787-942C-4d48-A389-DA81571F009C}"
        SICON_A = "{F7A339A7-E29F-42a9-B7AA-D69C54363B76}"
        XYNCHR = "{DD3DFE39-455E-40a1-801E-5D5B14CE4080}"
        XYCONTR = "{12ADC816-C7B1-48f8-8B9E-5E579151CF50}"
        ContAl_G = "{ED5A15E6-D3B0-4e64-8C50-809335D3E143}"
        Multi75E_G = "{9593403B-A476-49a9-AA1F-9C3AEDAC0178}"
        Multi75M_G = "{03D0715C-A520-4976-A5E2-4FC3078E3821}"
        Multi75Al_G = "{443A2EDC-5C9C-4d60-843F-C6688BEA1DEA}"
        Tap190Al_G = "{041FB80E-A179-4170-B5A4-A4EA1CC0A965}"
        Tap150Al_G = "{E0F31C86-6BB8-496b-AC7E-F55C62EAB635}"
        USC_F1_2_k7_3 = "{19AEEE43-478F-4D16-BDB7-2EE256EAF4A4}"
        USC_F0_3_k0_3 = "{16FAEEB6-A887-46F6-A418-81A9EBBCB6C3}"
        Dyn190Al = "{E9CE0D2D-F59E-4B44-A74F-B78C11575E9F}"
        Stat0_2LAuD =  "{A4A16538-CCD1-4BB1-B048-7B4F0F1B31BD}"
        CONTR  = "{89E92173-96FB-4ff9-94D8-42296D00D980}"
        CONTSCR = "{5A687B3E-A75A-4b22-BD70-40ABB931F00E}"
        CONTSCPt  = "{1E95D12B-1DDB-4ace-B3AF-BE9C0D52D4FC}"
        EFMR = "{986305AC-64B5-462e-B37E-6BD5AE447BE3}"
        LFMR = "{C61FCA2C-6D5D-4105-9FDE-640D263E229F}"
        MFMR = "{9499F49F-920F-47ec-80B6-883F683FF056}"
        NCLR = "{62633FD4-0555-4cee-A8B4-B82F4CEFBB48}"
        PPP_FMR = "{EBA2B75C-AA94-4451-AD36-1388CDABF5E8}"
        pq_SCONT = "{8D28AE10-E1DD-49E0-8CC6-ABD7CEDF57B0}"
        qp_CONT = "{0996E3AC-ABF6-4A22-B320-4BF749288156}"
        qp_fast_CB1 = "{3F3DD96B-F838-45B6-AA8C-B54F66ED9571}"
        qp_fast_CB2 = "{964280C3-70F7-4E22-AA60-734E672D7A02}"
        qp_fast_CB3 = "{CCF4B65D-F3D8-4A40-9108-53468ECBA1B4}"

    class ControllerType(enum.IntEnum):
        Undefined = -1
        Sim =       0
        ST9 =       1
        FLEX =      2
        CX =        3

    class FirmwareType(enum.IntEnum):
        Unknown = -1
        FREERTOS = 0
        LINUX = 1

    _class_id = ""  # class_id  The COM class id string, if equal to SPM.Application: try to connect to any running application.
    # lowlevel = ll.Lowlevel() # makes code recognition in VisualStudio code possible

    def __init__(self, class_id: str, lu_shared_file_path: str=""):
        """Create the COM client to deal with the SPM.

        Parameters
        ----------
        class_id: str
            COM automation name registered. eg 'CX.Application'
        lu_shared_file_path: str  
            Path to interface definition file, if empty, query the application for the path
        """

        # Connect or start application
        self._class_id = class_id
        self.application = None
        self.lowlevel:ll.Lowlevel = None # this is for old style compatibility
        self.lu:ll.Lowlevel = None       # this is for compatibility with Studio
        self.lu_shared_file_path = lu_shared_file_path

        if self._class_id == "SPM.Application":
            if not self._connect_to_running_app():
                print("Could not find a running Nanosurf SPM application.\nPlease start one first.")
                return
        else:
            try:
                self.application = win32com.client.Dispatch(self._class_id)
            except:
                print("Could not start application", self._class_id)
                
        #  If scripting is enabled finish startup and prepare subclasses
        if self.is_scripting_enabled():
            self._wait_for_end_of_startup()
            self._prepare_lowlevel_scripting()
            
    def is_connected(self) -> bool:
        return self.application is not None

    @property
    def is_studio(self) -> bool:
        return False

    @property
    def spm(self) -> 'Spm':
        return self

    def is_scripting_enabled(self) -> bool:
        script_enabled = False
        if self.application is not None:
            script_enabled = self.application.Scan is not None
        return script_enabled

    def is_lowlevel_scripting_enabled(self) -> bool:
        self._prepare_lowlevel_scripting()                
        return self.lowlevel is not None
    
    def get_sw_version(self) -> tuple[int,int,int,int]:
        sw_version:str = self.application.Version
        major, minor, revision, bugfix = sw_version.split(".")
        return (int(major), int(minor), int(revision), int(bugfix))

    def get_controller_type(self) -> ControllerType:
        detected_type = Spm.ControllerType.Undefined
        try:
            test_obj = self.application.CreateTestObj
            detected_type = test_obj.GetControllerMode()
        except:
            known_cx_applications = ["CX.Application", "USPM.Application"]
            known_flex_applications = ["C3000.Application", "CoreAFM.Application"]
            if self._class_id in known_cx_applications:
                detected_type = Spm.ControllerType.CX
            elif self._class_id in known_flex_applications:
                detected_type = Spm.ControllerType.FLEX
            else:
                detected_type = Spm.ControllerType.ST9
        return detected_type

    def get_firmware_type(self) -> FirmwareType:
        detect_firmware_type = Spm.FirmwareType.Unknown
        major, minor, *_ = self.get_sw_version()
        if major < 3 or (major == 3 and minor < 4): 
            if self.get_controller_type() != Spm.ControllerType.ST9:
                detect_firmware_type = Spm.FirmwareType.FREERTOS
        else:
            if self.get_controller_type() == Spm.ControllerType.CX:
                detect_firmware_type = Spm.FirmwareType.LINUX
            else:
                detect_firmware_type = Spm.FirmwareType.FREERTOS
        return detect_firmware_type

    def _prepare_lowlevel_scripting(self):
        if self.is_scripting_enabled():
            if self.lowlevel is None and self.application.SPMCtrlManager is not None:
                self.lowlevel = ll.Lowlevel(self.application.SPMCtrlManager, self.lu_shared_file_path)
                self.lowlevel.ctrlunits = ctrl_factory._CtrlUnitFactory(self)
                self.lu = self.lowlevel

    def _connect_to_running_app(self) -> bool:
        """ try to connect to a running spm application instance """
        self._class_id = ""
        _known_spm_app_names_lowercase = [i.lower() for i in _known_spm_app_names]
        
        for process in psutil.process_iter(['name']):
            procname = str(process.info['name'])
            if procname.endswith('.exe'):
                app_name = procname[:-4]
                if  app_name.lower() in _known_spm_app_names_lowercase:
                    self._class_id = app_name + ".Application"
                    self.application = win32com.client.Dispatch(self._class_id)
                    print(f"Connected to running app: {app_name}")
                    break
        return (self._class_id != "")
        # Should work like this but to whatever reason it gives only a runtime exception:
        # for app_name in _known_spm_app_names:
        #     if self._class_id == "":
        #         try:
        #             self._class_id = app_name + ".Application"
        #             self.application = win32com.client.GetActiveObject(self._class_id)
        #         except:
        #             pass

    def _wait_for_end_of_startup(self) -> bool:
        if self.application.IsStartingUp:
            print("Waiting for controller startup.", end="")
            tick = 0
            while self.application.IsStartingUp and (tick < 30):
                time.sleep(1)
                tick += 1
                print(".", end="")
            print()
            if self.application.IsStartingUp:
                print("Timeout. End of startup not reached.")
        return not self.application.IsStartingUp
    

class SPM(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("SPM.Application", *args, **kwargs)

class USPM(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("USPM.Application", *args, **kwargs)

class CX(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("CX.Application", *args, **kwargs)

class C3000(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("C3000.Application", *args, **kwargs)

class Naio(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("Naio.Application", *args, **kwargs)

class CoreAFM(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("CoreAFM.Application", *args, **kwargs)

class Easyscan2(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("Easyscan2.Application", *args, **kwargs)

class MobileS(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("MobileS.Application", *args, **kwargs)

class SPM_S(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("SPM_S.Application", *args, **kwargs)

