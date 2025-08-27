""" studio_scripting_demo client.py
Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT
"""

import nanosurf as nsf

studio = nsf.Studio()
if studio.connect():
    print(f"Connected with session = '{studio.session_id}'")

    # set a value 
    studio.spm.workflow.imaging.property.points_per_line.value = 200

    # set values with more direct access
    imaging = studio.spm.workflow.imaging
    imaging.property.scan_range_fast_axis.value = 2e-6
    imaging.property.scan_range_slow_axis.value = 2e-6

    # or even direct property shortening
    scan_mode = imaging.property.scan_mode
    scan_mode.value = scan_mode.ValueEnum.Single_Frame

    # call a workflow action
    studio.spm.workflow.imaging.start_imaging()

    studio.disconnect()
else:
    print(f"Connecting to studio failed: {studio.last_error}")




