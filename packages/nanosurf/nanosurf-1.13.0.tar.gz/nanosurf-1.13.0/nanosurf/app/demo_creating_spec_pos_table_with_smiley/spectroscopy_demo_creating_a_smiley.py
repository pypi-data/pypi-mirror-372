"""High-level programming interface example

The app demonstrates how to use the spectroscopy position table to define arbitrary spectroscopy patterns
The result of the calculation is shown in the Spectroscopy panel in the main software GUI

Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import math
import nanosurf as nsf

def create_smiley(spm: nsf.Spm, smiley_radius: float, number_of_points_for_head: int):
    """ This function defines spectroscopy coordinates looking like a smiley.

        Parameters
        ----------
        spm_controller: 
            controllers scripting interface object
        smiley_radius: float
            radius of the calculated smiley in [m]
        number_of_points_for_head: int
            defines the resolution or number of spec-points calculated for the circle which defines the head 
    """
    PI = math.pi
    step = 2*math.pi/number_of_points_for_head # degrees

    # get access to spectroscopy functions
    spec = spm.application.Spec
    spec.ClearPositionList()

    # draw head circle
    for i in range(number_of_points_for_head): 
        x = smiley_radius*math.cos(i*step)
        y = smiley_radius*math.sin(i*step)
        spec.AddPosition(x, y, 0)
    
    # draw eyes
    spec.AddPosition((smiley_radius/3), (smiley_radius/3), 0)
    spec.AddPosition((-smiley_radius/3), (smiley_radius/3), 0)

    # draw mouth
    number_of_points_for_mouth = math.trunc(number_of_points_for_head/6.0)
    for i in range(0,number_of_points_for_mouth+1):
        x = 0.75*smiley_radius*math.cos(PI*1.5-i*step)
        y = 0.75*smiley_radius*math.sin(PI*1.5-i*step)+0.1*smiley_radius
        spec.AddPosition(x, y, 0)
    for i in range(1,number_of_points_for_mouth+1):
        x = 0.75*smiley_radius*math.cos(PI*1.5+i*step)
        y = 0.75*smiley_radius*math.sin(PI*1.5+i*step)+0.1*smiley_radius
        spec.AddPosition(x, y, 0)

# Connecting to a running Nanosurf Control software...
spm = nsf.SPM()  
if spm.is_connected():
    if spm.is_scripting_enabled():

        create_smiley(spm, smiley_radius=30.0e-6, number_of_points_for_head=24)    

        # now the spectroscopy can be started to 'plot' the smiley
        # this can by done by the user in the applications GUI or here by
        # spec.Start()
    else:
        print("Sorry scripting is not activated on this controller.")
del spm
print("Done")

