""" studio_scripting_demo client.py
Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT
"""

import nanosurf as nsf

studio = nsf.Studio()
if studio.connect():
    print(f"Available sessions: {studio.main.session.list()}")
    print(f"Connected with session = '{studio.session_id}'")
    print(f"Server Ip", studio.server_ip)
    print(f"Server Port", studio.server_port)

    # set a value 
    studio.spm.workflow.imaging.property.points_per_line.value = 200

    # set values with more direct access
    imaging = studio.spm.workflow.imaging
    imaging.property.scan_range_fast_axis.value = 2e-6
    imaging.property.scan_range_slow_axis.value = 2e-6

    # or even direct property shortening
    scan_mode = imaging.property.scan_mode
    print(scan_mode.value)
    scan_mode.value = scan_mode.ValueEnum.Single_Frame

    # call a workflow action
    studio.spm.workflow.imaging.start_imaging()

    # different methods to iterate over enum properties
    print(f"possible scan modes by list: {imaging.property.scan_mode.enum}")
    print("possible scan modes by enum: ")
    for mode in imaging.property.scan_mode.ValueEnum:
        print(mode)

    # converting a property to SciVal
    scan_range_fast_axis = imaging.property.scan_range_fast_axis
    scan_range = nsf.sci_val.SciVal(imaging.property.scan_range_fast_axis)
    print(f"Fast scan range converted to SciVal is {scan_range}")
    print(f"This give the same result: {imaging.property.scan_range_fast_axis.value}")
    print(f"And also this give the same result: {nsf.sci_val.convert.to_string(scan_range_fast_axis.value,scan_range_fast_axis.unit)}")
    print(f"And this give the same value but not so nicely formatted: {scan_range_fast_axis.value}{scan_range_fast_axis.unit}")

    studio.disconnect()
else:
    print(f"Connecting to studio failed: {studio.last_error}")

