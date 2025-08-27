"""High-level programming interface example
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import matplotlib.pyplot as plt
import nanosurf as nsf

print("Connecting to a running Nanosurf Control software...")
spm = nsf.SPM() # Depending on the software version, this could be nanosurf.C3000(), or nanosurf.CoreAFM(), etc.
if spm.is_connected():
    if spm.is_scripting_enabled():

        # make a shortcut to the application object, to make subsequent code shorter:
        application = spm.application
        application.Visible = True

        spec = application.Spec
        spec.ClearPositionList()
        spec.ModuleLevel = spm.SpecModuleLevel.Standard
        spec.ModulatedOutput = spm.SpecModulatedOutput.ZAxis
        spec.ActiveZController = False
        spec.EnableRelative = True
        spec.RepetitionMode = spm.SpecRepetitionMode.Position
        spec.Repetition = 1
        spec.SpecEndMode = spm.SpecEndMode.KeepLastZPos
        spec.StartOffsetMoveSpeed = 10e-6
        spec.StartOffset = 0.0
        spec.XYMoveSpeed = 100e-6

        spec.FwdModDataPoints = 512
        spec.FwdModulationMode = spm.SpecModulationMode.FixedLength
        spec.FwdModulationRange = 500e-9
        spec.FwdModulationTime = 0.5
        spec.FwdPauseMode = spm.SpecPauseMode.KeepLastZPos
        spec.FwdPauseDataPoints = 0

        spec.BwdModDataPoints = 512
        spec.BwdModulationMode = spm.SpecModulationMode.FixedLength
        spec.BwdModulationRange = -500e-9
        spec.BwdModulationTime = 0.5
        spec.BwdPauseMode = spm.SpecPauseMode.KeepLastZPos
        spec.BwdPauseDataPoints = 0

        spec.Start()
        while spec.IsMeasuring:
            pass

        # plot the result of the measurement:
        spec_line_no = 0
        plt.plot(spec.GetLine2(
            spm.SpecGroupNo.Forward, spm.SpecChannel.Deflection_or_ZCtrlIn, spec_line_no, spm.DataFilter.RAW, spm.DataConversion.Physical), 'k')
        plt.plot(spec.GetLine2(
            spm.SpecGroupNo.Backward, spm.SpecChannel.Deflection_or_ZCtrlIn, spec_line_no, spm.DataFilter.RAW, spm.DataConversion.Physical), 'k:')
        plt.show()
    else:
        print("Sorry scripting is not activated on this controller.")
del spm